from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel


class TestRegistrationStatusEnum(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class TestRegistrationCreate(SQLModel):
    userId: str
    testId: str
    status: TestRegistrationStatusEnum = TestRegistrationStatusEnum.PENDING


class TestRegistrationUpdate(SQLModel):
    status: TestRegistrationStatusEnum | None = None
    updatedAt: datetime | None = None,
    isDestroyed: bool | None = False,


class TestRegistrationRead(SQLModel):
    id: str
    userId: str
    testId: str
    status: TestRegistrationStatusEnum
    registeredAt: datetime
    updatedAt: datetime
    isDestroyed: bool
