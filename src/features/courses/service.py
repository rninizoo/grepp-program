from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, asc, desc, select

from ...entities.courses import Course
from ...entities.payments import PaymentStatusEnum, PaymentTargetTypeEnum
from ...features.payments.schemas import PaymentApplyCourse, PaymentCreate, PaymentRead, PaymentUpdate
from ...features.payments.service import PaymentService
from .schemas import CourseCreate, CourseQueryOpts, CourseRead, CourseUpdate


class CourseService:
    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service

    def create_course(self, course_create:   CourseCreate, actant_id: int, session: Session) -> Course:
        # title 중복 체크
        existing_course = session.exec(select(Course).where(
            Course.title == course_create.title, Course.isDestroyed.is_(False))).first()
        if existing_course:
            raise HTTPException(
                status_code=409, detail="Course already registered")

        if course_create.startAt >= course_create.endAt:
            raise HTTPException(
                status_code=400, detail="Cannot create this course on startAt with endAt")

        course = Course(
            title=course_create.title,
            description=course_create.description,
            startAt=course_create.startAt,
            endAt=course_create.endAt,
            status=course_create.status,
            cost=course_create.cost,
            actantId=actant_id,
        )

        session.add(course)
        session.flush()
        session.refresh(course)
        return course

    def find_courses(self, session: Session, skip: int, limit: int, query_opts: CourseQueryOpts) -> list[CourseRead]:
        stmt = select(Course).where(Course.isDestroyed.is_(False))

        # status 필터링
        if query_opts.status:
            stmt = stmt.where(Course.status == query_opts.status)

        # 정렬 created | popular
        if query_opts.sort == "created":
            stmt = stmt.order_by(asc(Course.createdAt))
        elif query_opts.sort == "popular":
            stmt = stmt.order_by(desc(Course.studentCount))

        # offset, limit
        stmt = stmt.offset(skip).limit(limit)

        courses = session.exec(stmt).all()
        return [CourseRead.model_validate(course) for course in courses]

    def find_course_by_id(self, id: int, session: Session) -> Course | None:
        statement = select(Course).where(
            Course.id == id, Course.isDestroyed.is_(False))
        found_course = session.exec(statement).first()
        if not found_course:
            return None
        return found_course

    def update_course(self, course_id: int, course_update: CourseUpdate, session: Session) -> CourseRead:

        stmt = select(Course).where(Course.id == course_id).with_for_update()
        course = session.exec(stmt).one_or_none()

       # 존재여부 체크
        if not course or course.isDestroyed:
            raise HTTPException(status_code=404, detail="Course not found")

        # 존재여부 시작일, 종료일 체크
        if course_update.startAt is not None and course_update.endAt is not None:
            if course_update.startAt >= course_update.endAt:
                raise HTTPException(
                    status_code=400, detail="Cannot update this course on startAt with endAt"
                )

        update_data = course_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(course, key, value)

        course.updatedAt = datetime.now(timezone.utc)
        session.add(course)
        session.flush()
        session.refresh(course)

        return CourseRead.model_validate(course)

    def apply_course(self, course_id: int, payment_apply_course: PaymentApplyCourse, actant_id: int, session: Session) -> PaymentRead:

        try:
            course = self.find_course_by_id(course_id, session)
            if not course or course.isDestroyed:
                raise HTTPException(
                    status_code=404, detail="Course not found")

            # 신청기간이 아니면 에러처리
            if not (course.startAt <= date.today() <= course.endAt):
                raise HTTPException(
                    status_code=400, detail="This course is not open for registration at the current time")

            # 결제금액이 부족할 시 에러처리
            if (course.cost > payment_apply_course.amount):
                raise HTTPException(
                    status_code=400, detail="This course is cannot register by not enough amount")

            existing_payment = self.payment_service.find_payment_by_target_id_and_user_id(
                target_id=course.id,
                target_type=PaymentTargetTypeEnum.COURSE,
                user_id=actant_id,
                session=session
            )

            if existing_payment and existing_payment.status != PaymentStatusEnum.CANCELLED:
                raise HTTPException(
                    status_code=409, detail="Already payment applied Course")

            # 취소상태가 아닌 결제정보만 신규 결제 생성 가능
            if existing_payment and existing_payment.status != PaymentStatusEnum.CANCELLED:
                raise HTTPException(
                    status_code=409, detail="Already payment applied Course")

            payment_create = PaymentCreate(
                userId=actant_id,
                amount=payment_apply_course.amount,
                status=PaymentStatusEnum.PAID,
                method=payment_apply_course.method,
                targetType=PaymentTargetTypeEnum.COURSE,
                targetId=course_id,
                paidAt=datetime.now(timezone.utc),
                title=course.title,
                validFrom=date.today(),
                validTo=course.endAt
            )

            payment = self.payment_service.create_payment(
                payment_create=payment_create, user_id=actant_id, session=session)

            # 응시인원 증가
            course_update = CourseUpdate(
                studentCount=course.studentCount + 1)
            self.update_course(
                course_id=course.id, course_update=course_update, session=session)

            return PaymentRead.model_validate(payment)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def cancel_course(self, course_id: int, actant_id: int, session: Session) -> PaymentRead:

        try:
            course = self.find_course_by_id(course_id, session)
            if not course or course.isDestroyed:
                raise HTTPException(
                    status_code=404, detail="Course not found")

            # 응시완료(CourseRegistration.Status = true) 상태이면 취소 불가
            if not (course.startAt <= date.today() <= course.endAt):
                raise HTTPException(
                    status_code=400, detail="This course is not open for registration at the current time")

            existing_payment = self.payment_service.find_payment_by_target_id(
                target_id=course.id,
                session=session
            )

            # 결제된 응시만 취소 가능
            if existing_payment and existing_payment.status != PaymentStatusEnum.PAID:
                raise HTTPException(
                    status_code=400, detail="Already payment applied Course")

            payment_update = PaymentUpdate(
                status=PaymentStatusEnum.CANCELLED,
                method=None,
                paidAt=None,
                cancelledAt=datetime(timezone.utc)
            )

            payment = self.payment_service.update_payment(
                payment_id=existing_payment.id, payment_update=payment_update, user_id=actant_id, session=session)

            # 응시인원 감소
            course_update = CourseUpdate(
                studentCount=course.studentCount - 1)
            self.update_course(
                course_id=course.id, course_update=course_update, session=session)

            return PaymentRead.model_validate(payment)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def bulk_update_course(self, course_updates: list[tuple[int, CourseUpdate]], actant_id: int, session: Session):
        try:
            results: list[CourseRead] = []
            for course_id, course_update in course_updates:
                updated_course = self.update_course(
                    course_id, course_update, session)
                results.append(updated_course)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
