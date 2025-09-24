from datetime import datetime, timezone
from enum import Enum

from sqlmodel import CheckConstraint, Field

from .base import BaseModel


class TestStatusEnum(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"

class Test(BaseModel, table=True):
    __tablename__ = "tests"
    __table_args__ = (
        CheckConstraint('"startAt" < "endAt"', name="check_start_before_end"),
        CheckConstraint('"examineeCount" >= 0', name="check_examinee_count_positive"),
    )

    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    startAt: datetime = Field(nullable=False)
    endAt: datetime = Field(nullable=False)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    actantId: int = Field(foreign_key="user.id", nullable=False)
    status: TestStatusEnum = Field(nullable=False)
    cost: int = Field(nullable=False)
    examineeCount: int = Field(default=0)
    isDestroyed: bool = Field(default=False, nullable=False)
