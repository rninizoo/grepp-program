from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi.params import Depends
from sqlmodel import Session, asc, desc, select

from ...entities.payments import Payment, PaymentStatusEnum
from .schemas import PaymentCreate, PaymentQueryOpts, PaymentRead, PaymentUpdate


class PaymentService:
    def __init__(self):
        pass

    def create_payment(self, payment_create: PaymentCreate, user_id: int, session: Session) -> Payment:
        # validFrom, validTo 검사
        if payment_create.validFrom >= payment_create.validTo:
            raise HTTPException(
                status_code=400, detail="Invalid validFrom/validTo range")

        existing_payment = session.exec(
            select(Payment).where(
                Payment.userId == user_id,
                Payment.targetType == payment_create.targetType,
                Payment.targetId == payment_create.targetId,
                Payment.status != PaymentStatusEnum.CANCELLED,
                Payment.isDestroyed.is_(False)
            )
        ).first()

        if existing_payment:
            raise HTTPException(
                status_code=409, detail="Payment request already exists")

        payment = Payment(
            userId=user_id,
            amount=payment_create.amount,
            method=payment_create.method,
            status=payment_create.status,
            targetType=payment_create.targetType,
            targetId=payment_create.targetId,
            title=payment_create.title,
            validFrom=payment_create.validFrom,
            validTo=payment_create.validTo,
        )

        session.add(payment)
        session.flush()
        session.refresh(payment)
        return payment

    def find_payments(
        self,
        session: Session,
        skip: int,
        limit: int,
        query_opts: PaymentQueryOpts = Depends(),
    ) -> list[PaymentRead]:
        stmt = select(Payment).where(Payment.isDestroyed.is_(False))

        # status 필터링
        if query_opts.status:
            stmt = stmt.where(Payment.status == query_opts.status)

        # 기간 검색
        if query_opts.date_from:
            stmt = stmt.where(Payment.paidAt >= query_opts.date_from)
        if query_opts.date_to:
            stmt = stmt.where(Payment.paidAt <= query_opts.date_to)

        # 정렬: created | amount
        if query_opts.sort == "created":
            stmt = stmt.order_by(asc(Payment.createdAt))
        elif query_opts.sort == "amount":
            stmt = stmt.order_by(desc(Payment.amount))

        # offset, limit
        stmt = stmt.offset(skip).limit(limit)

        payments = session.exec(stmt).all()
        return [PaymentRead.model_validate(payment) for payment in payments]

    def find_payment_by_id(self, id: int, session: Session) -> Payment | None:
        statement = select(Payment).where(
            Payment.id == id, Payment.isDestroyed.is_(False))
        found_payment = session.exec(statement).first()
        if not found_payment:
            return None
        return found_payment

    def find_payment_by_target_id(self, target_id: int, session: Session) -> Payment | None:
        statement = select(Payment).where(
            Payment.targetId == target_id, Payment.isDestroyed.is_(False))
        found_payment = session.exec(statement).first()
        if not found_payment:
            return None
        return found_payment

    def update_payment(self, payment_id: int, payment_update: PaymentUpdate, user_id: int, session: Session) -> PaymentRead:
        stmt = select(Payment).where(
            Payment.id == payment_id).with_for_update()
        payment = session.exec(stmt).one_or_none()

        # 존재 여부 체크
        if not payment or payment.isDestroyed:
            raise HTTPException(status_code=404, detail="Payment not found")

        # 본인 결제만 수정 가능
        if payment.userId != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this payment")

        update_data = payment_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(payment, key, value)

        # validFrom / validTo 유효성 재검사
        if payment_update.validFrom and payment_update.validTo and payment_update.validFrom >= payment_update.validTo:
            raise HTTPException(
                status_code=400, detail="Invalid validFrom/validTo range")

        payment.updatedAt = datetime.now(timezone.utc)
        session.add(payment)
        session.flush()
        session.refresh(payment)

        return PaymentRead.model_validate(payment)

    def bulk_update_payment(self, payment_updates: list[tuple[int, PaymentUpdate]], user_id: int, session: Session):
        try:
            with session.begin():
                results: list[PaymentRead] = []
                for payment_id, payment_update in payment_updates:
                    updated_payment = self.update_payment(
                        payment_id, payment_update, user_id, session)
                    results.append(updated_payment)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
