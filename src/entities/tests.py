from datetime import date, datetime, timezone
from enum import Enum

import ulid
from sqlmodel import CheckConstraint, Field

from .base import BaseModel


class TestStatusEnum(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class Test(BaseModel, table=True):
    __tablename__ = "tests"
    __table_args__ = (
        CheckConstraint('"startAt" < "endAt"', name="check_start_before_end"),
        CheckConstraint('"examineeCount" >= 0',
                        name="check_examinee_count_positive"),
    )

    id: str = Field(default_factory=lambda: str(
        ulid.new()), primary_key=True, index=True)
    title: str
    description: str | None = None
    startAt: date = Field(nullable=False)
    endAt: date = Field(nullable=False)
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=True,
    )
    actantId: str = Field(foreign_key="users.id", nullable=False)
    status: TestStatusEnum = Field(nullable=False)
    cost: int = Field(nullable=False)
    examineeCount: int = Field(default=0)
    isDestroyed: bool = Field(default=False, nullable=False)
