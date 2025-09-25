from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi.params import Depends
from sqlmodel import Session, asc, desc, select

from ...entities.courses import Course
from .schemas import CourseCreate, CourseQueryOpts, CourseRead, CourseUpdate


class CourseService:
    def __init__(self):
        pass

    def create_course(self, course_create:   CourseCreate, actant_id: int, session: Session) -> Course:
        # title 중복 체크
        existing_course = session.exec(select(Course).where(
            Course.title == course_create.title, Course.isDestroyed.is_(False))).first()
        if existing_course:
            raise HTTPException(
                status_code=409, detail="Course already registered")

        if course_create.startAt >= course_create.endAt:
            raise HTTPException(
                status_code=400, detail="Cannot create this test on startAt with endAt")

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

    def find_courses(self, session: Session, skip: int, limit: int, query_opts: CourseQueryOpts = Depends()) -> list[CourseRead]:
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

    def update_course(self, course_id: int, course_update: CourseUpdate, actant_id: int, session: Session) -> CourseRead:

        stmt = select(Course).where(Course.id == course_id).with_for_update()
        course = session.exec(stmt).one_or_none()

        # 존재여부 체크
        if not course or course.isDestroyed:
            raise HTTPException(status_code=404, detail="Course not found")

        # 존재여부 시작일, 종료일 체크
        if course_update.startAt >= course_update.endAt:
            raise HTTPException(
                status_code=400, detail="Cannot update this course on startAt with endAt")

        # 작성자만 변경 가능
        if course.actantId != actant_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this course")

        update_data = course_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(course, key, value)

        course.updatedAt = datetime.now(timezone.utc)
        session.add(course)
        session.flush()
        session.refresh(course)

        return CourseRead.model_validate(course)

    def bulk_update_course(self, course_updates: list[tuple[int, CourseUpdate]], actant_id: int, session: Session):
        try:
            with session.begin():
                results: list[CourseRead] = []
                for course_id, course_update in course_updates:
                    updated_course = self.update_course(
                        course_id, course_update, actant_id, session)
                    results.append(updated_course)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
