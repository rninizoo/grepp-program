from datetime import date, datetime, timezone
from enum import Enum

import ulid
from sqlmodel import Field, Index, SQLModel


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
    __table_args__ = (
        Index(
            "idx_payment_target_user_type_isdestroyed",
            "targetId", "targetType", "userId", "isDestroyed"
        ),
    )

    id: str = Field(default_factory=lambda: str(
        ulid.new()), primary_key=True, index=True)
    userId: str = Field(foreign_key="users.id", nullable=False)

    amount: int = Field(nullable=False)  # 단위: KRW
    method: PaymentMethodEnum = Field(nullable=True)
    status: PaymentStatusEnum = Field(nullable=False)

    targetType: PaymentTargetTypeEnum = Field(nullable=False)
    targetId: str = Field(nullable=False)
    title: str = Field(nullable=False)

    paidAt: datetime | None = Field(default=None)
    validFrom: date = Field(nullable=False)
    validTo: date = Field(nullable=False)

    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    cancelledAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    isDestroyed: bool = Field(default=False, nullable=False)
