from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel


class CourseRegistrationStatusEnum(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class CourseRegistrationCreate(SQLModel):
    userId: str
    courseId: str
    status: CourseRegistrationStatusEnum = CourseRegistrationStatusEnum.PENDING


class CourseRegistrationUpdate(SQLModel):
    status: CourseRegistrationStatusEnum | None = None
    updatedAt: datetime | None = None,
    isDestroyed: bool | None = False,


class CourseRegistrationRead(SQLModel):
    id: str
    userId: str
    courseId: str
    status: CourseRegistrationStatusEnum
    registeredAt: datetime
    updatedAt: datetime
    isDestroyed: bool
