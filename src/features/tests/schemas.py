from datetime import date, datetime
from typing import Literal

from sqlmodel import SQLModel

from ...entities.tests import TestStatusEnum


class TestQueryOpts(SQLModel):
    status: str = "AVAILABLE"
    sort: Literal["created", "popular"] = "created"


class TestCreate(SQLModel):
    title: str
    description: str
    startAt: date
    endAt: date
    cost: int
    status: TestStatusEnum


class TestUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    examineeCount: int | None = None
    startAt: date | None = None
    endAt: date | None = None
    status: TestStatusEnum | None = None
    cost: int | None = None
    isDestroyed: bool | None = False


class TestRead(SQLModel):
    id: str
    title: str
    description: str
    startAt: date
    endAt: date
    status: TestStatusEnum
    isDestroyed: bool
    createdAt: datetime
    updatedAt: datetime
    examineeCount: int
    cost: int
    actantId: str
