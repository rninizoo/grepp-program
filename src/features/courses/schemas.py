from datetime import date, datetime
from typing import Literal

from sqlmodel import SQLModel

from ...entities.courses import CourseStatusEnum


class CourseQueryOpts(SQLModel):
    status: str = "AVAILABLE"
    sort: Literal["created", "popular"] = "created"


class CourseCreate(SQLModel):
    title: str
    description: str
    startAt: date
    endAt: date
    status: CourseStatusEnum
    cost: int


class CourseUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    studentCount: int | None = None
    startAt: date | None = None
    endAt: date | None = None
    status: CourseStatusEnum | None = None
    cost: int | None = None
    isDestroyed: bool | None = False


class CourseRead(SQLModel):
    id: str
    title: str
    description: str
    startAt: datetime
    endAt: datetime
    status: CourseStatusEnum
    createdAt: datetime
    updatedAt: datetime
    cost: int
    studentCount: int
    actantId: str
    isDestroyed: bool
