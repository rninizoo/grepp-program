from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from ...entities.course_registration import CourseRegistration, CourseRegistrationStatusEnum
from .schemas import CourseRegistrationRead, CourseRegistrationUpdate


class CourseRegistrationService:

    def create_registration(self, user_id: str,  course_id: str,  payment_id: str, session: Session) -> CourseRegistrationRead:
        existing = session.exec(
            select(CourseRegistration)
            .where(
                CourseRegistration.userId == user_id,
                CourseRegistration.courseId == course_id,
                CourseRegistration.paymentId == payment_id,
                CourseRegistration.isDestroyed.is_(False)
            )
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Already registered")

        registration = CourseRegistration(
            userId=user_id,
            courseId=course_id,
            status=CourseRegistrationStatusEnum.PENDING,
            paymentId=payment_id,
            registeredAt=datetime.now(timezone.utc)
        )
        session.add(registration)
        session.flush()
        session.refresh(registration)
        return CourseRegistrationRead.model_validate(registration)

    def find_registration_by_id(self, registration_id: str,  session: Session, for_update: bool = False) -> CourseRegistrationRead:
        stmt = select(CourseRegistration).where(
            CourseRegistration.id == registration_id,
            CourseRegistration.isDestroyed.is_(False)
        )

        if for_update:
            stmt = stmt.with_for_update()

        registration = session.exec(stmt).first()
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )
        return CourseRegistrationRead.model_validate(registration)

    def find_registration_by_target_id_and_payment_id(self, target_id: str, payment_id: str, session: Session, for_update: bool = False) -> CourseRegistrationRead:
        stmt = select(CourseRegistration).where(
            CourseRegistration.courseId == target_id,
            CourseRegistration.paymentId == payment_id,
            CourseRegistration.isDestroyed.is_(False)
        )

        if for_update:
            stmt = stmt.with_for_update()

        registration = session.exec(stmt).first()
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )
        return CourseRegistration.model_validate(registration)

    def update_registration(self, registration_id: str, registration_update: CourseRegistrationUpdate, session: Session, for_update: bool = False) -> CourseRegistrationRead:
        stmt = select(CourseRegistration).where(
            CourseRegistration.id == registration_id,
            CourseRegistration.isDestroyed.is_(False)
        )

        if for_update:
            stmt = stmt.with_for_update()

        registration = session.exec(stmt).first()
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        update_data = registration_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(registration, key, value)

        registration.updatedAt = datetime.now(timezone.utc)
        session.add(registration)
        session.flush()
        session.refresh(registration)
        return CourseRegistrationRead.model_validate(registration)

    def delete_registration(self, registration_id: str, session: Session, for_update: bool = False) -> None:
        stmt = select(CourseRegistration).where(CourseRegistration.id ==
                                                registration_id, CourseRegistration.isDestroyed.is_(False))

        if for_update:
            stmt = stmt.with_for_update()

        registration = session.exec(stmt).first()
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

        registration.isDestroyed = True
        registration.updatedAt = datetime.now(timezone.utc)
        session.add(registration)
        session.flush()
