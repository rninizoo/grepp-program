from datetime import datetime, timezone
from enum import Enum

import ulid
from sqlmodel import Field, Index, SQLModel


class TestRegistrationStatusEnum(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class TestRegistration(SQLModel, table=True):
    __tablename__ = "test_registrations"
    __table_args__ = (
        Index("idx_test_registration_user_test_status",
              "userId", "testId", "status"),
    )

    id: str = Field(default_factory=lambda: str(
        ulid.new()), primary_key=True, index=True)
    userId: str = Field(foreign_key="users.id", nullable=False)
    testId: str = Field(foreign_key="tests.id", nullable=False)
    paymentId: str = Field(foreign_key="payments.id", nullable=False)

    status: TestRegistrationStatusEnum = Field(
        default=TestRegistrationStatusEnum.PENDING, nullable=False)
    registeredAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    isDestroyed: bool = Field(default=False, nullable=False)
