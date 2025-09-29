from datetime import datetime, time, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from ...entities.courses import Course
from ...entities.payments import Payment, PaymentStatusEnum, PaymentTargetTypeEnum
from ...entities.tests import Test
from ...features.course_registration.schemas import CourseRegistrationStatusEnum, CourseRegistrationUpdate
from ...features.course_registration.service import CourseRegistrationService
from ...features.test_registration.schemas import TestRegistrationStatusEnum, TestRegistrationUpdate
from ...features.test_registration.service import TestRegistrationService
from .schemas import PaymentCreate, PaymentQueryOpts, PaymentRead, PaymentUpdate


class PaymentService:
    REGISTRATION_MAP = {
        PaymentTargetTypeEnum.TEST: {
            "service_attr": "test_registration_service",
            "update_schema": TestRegistrationUpdate,
            "status_enum": TestRegistrationStatusEnum,
        },
        PaymentTargetTypeEnum.COURSE: {
            "service_attr": "course_registration_service",
            "update_schema": CourseRegistrationUpdate,
            "status_enum": CourseRegistrationStatusEnum,
        },
    }

    def __init__(self, test_registration_service: TestRegistrationService, course_registration_service: CourseRegistrationService):
        self.test_registration_service = test_registration_service
        self.course_registration_service = course_registration_service

    def create_payment(self, payment_create: PaymentCreate, user_id: str, session: Session) -> Payment:
        # validFrom, validTo 검사
        if payment_create.validFrom >= payment_create.validTo:
            raise HTTPException(
                status_code=400, detail="Invalid validFrom/validTo range")

        existing_payment = session.exec(
            select(Payment).where(
                Payment.userId == user_id,
                Payment.targetType == payment_create.targetType,
                Payment.targetId == payment_create.targetId,
                Payment.status != PaymentStatusEnum.CANCELLED,
                Payment.isDestroyed.is_(False)
            )
        ).first()

        if existing_payment:
            raise HTTPException(
                status_code=409, detail="Payment request already exists")

        payment = Payment(
            userId=user_id,
            amount=payment_create.amount,
            method=payment_create.method,
            status=payment_create.status,
            targetType=payment_create.targetType,
            targetId=payment_create.targetId,
            title=payment_create.title,
            paidAt=payment_create.paidAt,
            validFrom=payment_create.validFrom,
            validTo=payment_create.validTo,
        )

        session.add(payment)
        session.flush()
        session.refresh(payment)

        return payment

    def apply_payment(self, payment_create: PaymentCreate, user_id: str, session: Session) -> Payment:
        # validFrom, validTo 검사
        if payment_create.validFrom >= payment_create.validTo:
            raise HTTPException(
                status_code=400, detail="Invalid validFrom/validTo range")

        existing_payment = session.exec(
            select(Payment).where(
                Payment.userId == user_id,
                Payment.targetType == payment_create.targetType,
                Payment.targetId == payment_create.targetId,
                Payment.status != PaymentStatusEnum.CANCELLED,
                Payment.isDestroyed.is_(False)
            )
        ).first()

        if existing_payment:
            raise HTTPException(
                status_code=409, detail="Payment request already exists")

        payment = Payment(
            userId=user_id,
            amount=payment_create.amount,
            method=payment_create.method,
            status=payment_create.status,
            targetType=payment_create.targetType,
            targetId=payment_create.targetId,
            title=payment_create.title,
            paidAt=payment_create.paidAt,
            validFrom=payment_create.validFrom,
            validTo=payment_create.validTo,
        )

        session.add(payment)
        session.flush()
        session.refresh(payment)

        if payment_create.targetType == PaymentTargetTypeEnum.TEST:
            self.test_registration_service.create_registration(
                user_id=payment_create.userId, test_id=payment_create.targetId, payment_id=payment.id, session=session)
        elif payment_create.targetType == PaymentTargetTypeEnum.COURSE:
            self.course_registration_service.create_registration(
                user_id=payment_create.userId, course_id=payment_create.targetId, payment_id=payment.id, session=session)
        else:
            raise HTTPException(status_code=400, detail="Invalid target type")

        return payment

    def cancel_payment(self, payment_id: str, user_id: str, session: Session) -> Payment:

        payment = session.exec(
            select(Payment)
            .where(Payment.id == payment_id, Payment.userId == user_id, Payment.isDestroyed.is_(False))
            .with_for_update()
        ).first()

        if not payment:
            raise HTTPException(
                status_code=404, detail="Payment not found")
        if payment.status != PaymentStatusEnum.PAID:
            if payment.status == PaymentStatusEnum.CANCELLED:
                raise HTTPException(
                    status_code=400, detail="Payment Cancelled Already.")
            if payment.status == PaymentStatusEnum.PENDING:
                raise HTTPException(
                    status_code=400, detail="Payment Not Paid")

        payment.status = PaymentStatusEnum.CANCELLED
        payment.cancelledAt = datetime.now(timezone.utc)
        payment.updatedAt = datetime.now(timezone.utc)

        session.add(payment)

        config = self.REGISTRATION_MAP[payment.targetType]
        registration_service = getattr(self, config["service_attr"])
        update_schema = config["update_schema"]
        status_enum = config["status_enum"]

        registration = registration_service.find_registration_by_target_id_and_payment_id(
            target_id=payment.targetId, payment_id=payment.id, session=session, for_update=True
        )

        if registration.status == status_enum.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel a completed {payment.targetType.lower()} registration"
            )

        registration_update = update_schema(
            isDestroyed=True, updatedAt=datetime.now(timezone.utc))
        registration_service.update_registration(registration_id=registration.id,
                                                 registration_update=registration_update, session=session)

        # Course / Test 인원 감소
        if payment.targetType == PaymentTargetTypeEnum.COURSE:
            course = session.exec(
                select(Course).where(Course.id ==
                                     payment.targetId).with_for_update()
            ).first()
            if course:
                course.studentCount = max(0, course.studentCount - 1)
                course.updatedAt = datetime.now(timezone.utc)
                session.add(course)

        elif payment.targetType == PaymentTargetTypeEnum.TEST:
            test = session.exec(
                select(Test).where(
                    Test.id == payment.targetId).with_for_update()
            ).first()
            if test:
                test.examineeCount = max(0, test.examineeCount - 1)
                test.updatedAt = datetime.now(timezone.utc)
                session.add(test)

        session.flush()
        session.refresh(payment)

        return payment

    def find_payments(
        self,
        session: Session,
        skip: int,
        limit: int,
        query_opts: PaymentQueryOpts,
    ) -> list[PaymentRead]:
        stmt = select(Payment).where(Payment.isDestroyed.is_(False))

        # status 필터링
        if query_opts.status:
            stmt = stmt.where(Payment.status == query_opts.status)

        # 기간 검색
        if query_opts.date_from:
            dt_from = datetime.combine(query_opts.date_from, time.min)
            stmt = stmt.where(Payment.paidAt >= dt_from)
        if query_opts.date_to:
            dt_to = datetime.combine(query_opts.date_to, time.max)
            stmt = stmt.where(Payment.paidAt <= dt_to)

        # offset, limit
        stmt = stmt.offset(skip).limit(limit)

        payments = session.exec(stmt).all()
        return [PaymentRead.model_validate(payment) for payment in payments]

    def find_payment_by_id(self, id: str, session: Session) -> Payment | None:
        statement = select(Payment).where(
            Payment.id == id, Payment.isDestroyed.is_(False))
        found_payment = session.exec(statement).first()
        if not found_payment:
            return None
        return found_payment

    def find_payment_by_target_id_and_user_id(self, target_id: str, target_type: PaymentTargetTypeEnum, user_id: str, session: Session, for_update: bool = False) -> Payment | None:

        stmt = select(Payment).where(
            Payment.targetId == target_id,
            Payment.targetType == target_type,
            Payment.userId == user_id,
            Payment.isDestroyed.is_(False)
        )

        if for_update:
            stmt = stmt.with_for_update()

        found_payment = session.exec(stmt).first()

        if not found_payment:
            return None
        return found_payment

    def update_payment(self, payment_id: str, payment_update: PaymentUpdate, user_id: str, session: Session) -> PaymentRead:
        stmt = select(Payment).where(
            Payment.id == payment_id).with_for_update()
        payment = session.exec(stmt).one_or_none()

        # 존재 여부 체크
        if not payment or payment.isDestroyed:
            raise HTTPException(status_code=404, detail="Payment not found")

        # 본인 결제만 수정 가능
        if payment.userId != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this payment")

        update_data = payment_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(payment, key, value)

        # validFrom / validTo 유효성 재검사
        if payment_update.validFrom and payment_update.validTo and payment_update.validFrom >= payment_update.validTo:
            raise HTTPException(
                status_code=400, detail="Invalid validFrom/validTo range")

        payment.updatedAt = datetime.now(timezone.utc)
        session.add(payment)
        session.flush()
        session.refresh(payment)

        return PaymentRead.model_validate(payment)
