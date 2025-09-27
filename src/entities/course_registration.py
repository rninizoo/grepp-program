from datetime import datetime, timezone
from enum import Enum

import ulid
from sqlmodel import Field, Index, SQLModel


class CourseRegistrationStatusEnum(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class CourseRegistration(SQLModel, table=True):
    __tablename__ = "course_registrations"
    __table_args__ = (
        Index("idx_course_registration_user_course_status",
              "userId", "courseId", "status"),
    )

    id: str = Field(default_factory=lambda: str(
        ulid.new()), primary_key=True, index=True)
    userId: str = Field(foreign_key="users.id", nullable=False)
    courseId: str = Field(foreign_key="courses.id", nullable=False)
    paymentId: str = Field(foreign_key="payments.id", nullable=False)

    status: CourseRegistrationStatusEnum = Field(
        default=CourseRegistrationStatusEnum.PENDING, nullable=False)
    registeredAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    isDestroyed: bool = Field(default=False, nullable=False)
