from datetime import datetime

from sqlmodel import SQLModel

from ...entities.tests import TestStatusEnum


class TestCreate(SQLModel):
    title: str
    description: str
    startAt: datetime
    endAt: datetime
    status: TestStatusEnum


class TestUpdate(SQLModel):
    title: str | None
    description: str | None
    examineeCount: int | None
    startAt: datetime  | None
    endAt: datetime | None
    status: TestStatusEnum | None
    isDestroyed: bool | None

class TestRead(SQLModel):
    id: int
    title: str
    description: str
    startAt: datetime
    endAt: datetime
    status: TestStatusEnum
    isDestroyed: bool
    createdAt: datetime
    updatedAt: datetime
    examineeCount: int
    actantId: int
