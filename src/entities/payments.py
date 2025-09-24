from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class PaymentStatusEnum(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class PaymentMethodEnum(str, Enum):
    KAKAOPAY = "KAKAOPAY"
    TOSS = "TOSS"
    BANK = "BANK"
    CARD = "CARD"

class PaymentTargetTypeEnum(str, Enum):
    TEST = "TEST"
    COURSE = "COURSE"

class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: int = Field(default=None, primary_key=True)
    userId: int = Field(foreign_key="user.id", nullable=False)

    amount: int = Field(nullable=False)  # 단위: KRW
    method: PaymentMethodEnum = Field(nullable=True)
    status: PaymentStatusEnum = Field(nullable=False)

    targetType: PaymentTargetTypeEnum = Field(nullable=False)
    targetId: str = Field(nullable=False)
    title: str = Field(nullable=False)

    paidAt: datetime | None = Field(default=None)
    validFrom: datetime = Field(nullable=False)
    validTo: datetime = Field(nullable=False)

    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    isDestroyed: bool = Field(default=False, nullable=False)
