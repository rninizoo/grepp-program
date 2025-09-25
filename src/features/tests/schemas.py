from datetime import datetime
from typing import Literal

from sqlmodel import SQLModel

from ...entities.tests import TestStatusEnum


class TestQueryOpts(SQLModel):
    status: str = "AVAILABLE"
    sort: Literal["created", "popular"] = "created"


class TestCreate(SQLModel):
    title: str
    description: str
    startAt: datetime
    endAt: datetime
    cost: int
    status: TestStatusEnum


class TestUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    examineeCount: int | None = None
    startAt: datetime | None = None
    endAt: datetime | None = None
    status: TestStatusEnum | None = None
    cost: int | None = None
    isDestroyed: bool | None = None


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
    cost: int
    actantId: int
