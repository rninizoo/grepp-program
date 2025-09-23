from datetime import datetime
from typing import Literal

from sqlmodel import SQLModel

from ...entities.courses import CourseStatusEnum


class CourseQueryOpts(SQLModel):
    status: str = "AVAILABLE"
    sort: Literal["created", "popular"] = "created"

class CourseCreate(SQLModel):
    title: str
    description: str
    startAt: datetime
    endAt: datetime
    status: CourseStatusEnum


class CourseUpdate(SQLModel):
    title: str | None
    description: str | None
    studentCount: int | None
    startAt: datetime  | None
    endAt: datetime | None
    status: CourseStatusEnum | None
    isDestroyed: bool | None

class CourseRead(SQLModel):
    id: int
    title: str
    description: str
    startAt: datetime
    endAt: datetime
    status: CourseStatusEnum
    isDestroyed: bool
    createdAt: datetime
    updatedAt: datetime
    studentCount: int
    actantId: int
