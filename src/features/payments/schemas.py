from datetime import date, datetime
from typing import Literal

from fastapi import Query
from sqlmodel import SQLModel

from ...entities.payments import PaymentMethodEnum, PaymentStatusEnum, PaymentTargetTypeEnum


class PaymentQueryOpts(SQLModel):
    status: PaymentStatusEnum | None = Query(default=None)
    date_from: date | None = Query(default=None, alias="from")
    date_to: date | None = Query(default=None, alias="to")
    sort: Literal["created", "amount"] | None = Query(default="created")


class PaymentCreate(SQLModel):
    userId: int
    amount: int
    method: PaymentMethodEnum | None = None
    status: PaymentStatusEnum
    targetType: PaymentTargetTypeEnum
    targetId: int
    title: str
    paidAt: datetime | None = None
    validFrom: date
    validTo: date


class PaymentRead(SQLModel):
    id: int
    userId: int
    amount: int
    method: PaymentMethodEnum | None = None
    status: PaymentStatusEnum  # noqa: F821
    targetType: PaymentTargetTypeEnum
    targetId: int
    title: str
    paidAt: datetime | None = None
    validFrom: date
    validTo: date
    createdAt: datetime
    updatedAt: datetime
    isDestroyed: bool


class PaymentUpdate(SQLModel):
    amount: int | None = None
    method: PaymentMethodEnum | None = None
    status: PaymentStatusEnum | None = None
    targetType: PaymentTargetTypeEnum | None = None
    targetId: int | None = None
    title: str | None = None
    paidAt: datetime | None = None
    cancelledAt: datetime | None = None
    validFrom: date | None = None
    validTo: date | None = None
    isDestroyed: bool | None = None


class PaymentApplyTest(SQLModel):
    amount: int
    method: PaymentMethodEnum
