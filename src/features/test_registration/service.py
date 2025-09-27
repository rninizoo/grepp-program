from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from ...entities.test_registration import TestRegistration, TestRegistrationStatusEnum
from .schemas import TestRegistrationRead, TestRegistrationUpdate


class TestRegistrationService:

    def create_registration(self, user_id: str,  test_id: str,  payment_id: str, session: Session) -> TestRegistrationRead:
        existing = session.exec(
            select(TestRegistration)
            .where(
                TestRegistration.userId == user_id,
                TestRegistration.testId == test_id,
                TestRegistration.paymentId == payment_id,
                TestRegistration.isDestroyed.is_(False)
            )
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Already registered")

        registration = TestRegistration(
            userId=user_id,
            testId=test_id,
            paymentId=payment_id,
            status=TestRegistrationStatusEnum.PENDING,
            registeredAt=datetime.now(timezone.utc)
        )
        session.add(registration)
        session.flush()
        session.refresh(registration)
        return TestRegistrationRead.model_validate(registration)

    def find_registration_by_id(self, registration_id: str,  session: Session, for_update: bool = False) -> TestRegistrationRead:
        stmt = select(TestRegistration).where(
            TestRegistration.id == registration_id,
            TestRegistration.isDestroyed.is_(False)
        )

        if for_update:
            stmt = stmt.with_for_update()

        registration = session.exec(stmt).first()
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )
        return TestRegistrationRead.model_validate(registration)

    def find_registration_by_target_id_and_payment_id(self, target_id: str, payment_id: str, session: Session, for_update: bool = False) -> TestRegistrationRead:
        stmt = select(TestRegistration).where(
            TestRegistration.testId == target_id,
            TestRegistration.paymentId == payment_id,
            TestRegistration.isDestroyed.is_(False)
        )

        if for_update:
            stmt = stmt.with_for_update()

        registration = session.exec(stmt).first()
        if not registration:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )
        return TestRegistrationRead.model_validate(registration)

    def update_registration(self,  registration_id: str,   registration_update: TestRegistrationUpdate, session: Session, for_update: bool = False) -> TestRegistrationRead:
        stmt = select(TestRegistration).where(
            TestRegistration.id == registration_id,
            TestRegistration.isDestroyed.is_(False)
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
        return TestRegistrationRead.model_validate(registration)

    def delete_registration(self, registration_id: str, session: Session, for_update: bool = False) -> None:
        stmt = select(TestRegistration).where(
            TestRegistration.id == registration_id,
            TestRegistration.isDestroyed.is_(False)
        )

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
