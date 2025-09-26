from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, asc, desc, select

from ...entities.payments import PaymentStatusEnum, PaymentTargetTypeEnum
from ...entities.tests import Test
from ...features.payments.schemas import PaymentApplyTest, PaymentCreate, PaymentRead
from ...features.payments.service import PaymentService
from .schemas import TestCreate, TestQueryOpts, TestRead, TestUpdate


class TestService:
    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service

    def create_test(self, test_create: TestCreate, actant_id: str, session: Session) -> Test:
        # title 중복 체크
        existing_test = session.exec(select(Test).where(
            Test.title == test_create.title, Test.isDestroyed.is_(False))).first()
        if existing_test:
            raise HTTPException(
                status_code=409, detail="Test already registered")

        if test_create.startAt >= test_create.endAt:
            raise HTTPException(
                status_code=400, detail="Cannot create this test on startAt with endAt")

        test = Test(
            title=test_create.title,
            description=test_create.description,
            startAt=test_create.startAt,
            endAt=test_create.endAt,
            status=test_create.status,
            cost=test_create.cost,
            actantId=actant_id,
        )

        session.add(test)
        session.flush()
        session.refresh(test)
        return test

    def find_test_by_id(self, id: str, session: Session, for_update: bool = False) -> Test | None:
        stmt = select(Test).where(Test.id == id, Test.isDestroyed.is_(False))

        if for_update:
            stmt = stmt.with_for_update()  # 여기서 FOR UPDATE 적용

        test = session.exec(stmt).first()
        return test

    def find_tests(self, session: Session, skip: int, limit: int, query_opts: TestQueryOpts) -> list[TestRead]:
        stmt = select(Test).where(Test.isDestroyed.is_(False))

        # status 필터링
        if query_opts.status:
            stmt = stmt.where(Test.status == query_opts.status)

        # 정렬 created | popular
        if query_opts.sort == "created":
            stmt = stmt.order_by(asc(Test.createdAt))
        elif query_opts.sort == "popular":
            stmt = stmt.order_by(desc(Test.examineeCount))

        # offset, limit
        stmt = stmt.offset(skip).limit(limit)

        tests = session.exec(stmt).all()
        return [TestRead.model_validate(test) for test in tests]

    def update_test(self, test_id: str, test_update: TestUpdate, session: Session) -> TestRead:
        stmt = select(Test).where(Test.id == test_id).with_for_update()
        test = session.exec(stmt).one_or_none()

        # 존재여부 체크
        if not test or test.isDestroyed:
            raise HTTPException(status_code=404, detail="Test not found")

        # 존재여부 시작일, 종료일 체크
        if test_update.startAt is not None and test_update.endAt is not None:
            if test_update.startAt >= test_update.endAt:
                raise HTTPException(
                    status_code=400, detail="Cannot update this test on startAt with endAt"
                )

        update_data = test_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(test, key, value)
            test.updatedAt = datetime.now(timezone.utc)
        session.add(test)
        session.flush()
        session.refresh(test)

        return TestRead.model_validate(test)

    def apply_test(self, test_id: str, payment_apply_test: PaymentApplyTest, actant_id: str, session: Session) -> PaymentRead:

        try:
            test = self.find_test_by_id(test_id, session, True)
            if not test or test.isDestroyed:
                raise HTTPException(
                    status_code=404, detail="Test not found")

            # 신청기간이 아니면 에러처리
            if not (test.startAt <= date.today() <= test.endAt):
                raise HTTPException(
                    status_code=400, detail="This test is not open for registration at the current time")

            # 결제금액이 부족할 시 에러처리
            if (test.cost > payment_apply_test.amount):
                raise HTTPException(
                    status_code=400, detail="This test is cannot register by not enough amount")

            existing_payment = self.payment_service.find_payment_by_target_id_and_user_id(
                target_id=test.id,
                target_type=PaymentTargetTypeEnum.TEST,
                user_id=actant_id,
                session=session,
                for_update=True
            )

            if existing_payment and existing_payment.status != PaymentStatusEnum.CANCELLED:
                raise HTTPException(
                    status_code=409, detail="Already payment applied Test")

            # 취소상태가 아닌 결제정보만 신규 결제 생성 가능
            if existing_payment and existing_payment.status != PaymentStatusEnum.CANCELLED:
                raise HTTPException(
                    status_code=409, detail="Already payment applied Test")

            payment_create = PaymentCreate(
                userId=actant_id,
                amount=payment_apply_test.amount,
                status=PaymentStatusEnum.PAID,
                method=payment_apply_test.method,
                targetType=PaymentTargetTypeEnum.TEST,
                targetId=test_id,
                paidAt=datetime.now(timezone.utc),
                title=test.title,
                validFrom=date.today(),
                validTo=test.endAt
            )

            payment = self.payment_service.apply_payment(
                payment_create=payment_create, user_id=actant_id, session=session)

            # 응시인원 증가
            test_update = TestUpdate(examineeCount=test.examineeCount + 1)
            self.update_test(
                test_id=test.id, test_update=test_update, session=session)

            return PaymentRead.model_validate(payment)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def cancel_test(self, test_id: str, actant_id: str, session: Session) -> PaymentRead:

        try:
            test = self.find_test_by_id(test_id, session, True)
            if not test or test.isDestroyed:
                raise HTTPException(
                    status_code=404, detail="Test not found")

            # 응시완료(TestRegistration.Status = true) 상태이면 취소 불가
            if not (test.startAt <= date.today() <= test.endAt):
                raise HTTPException(
                    status_code=400, detail="This test is not open for registration at the current time")

            existing_payment = self.payment_service.find_payment_by_target_id(
                target_id=test.id,
                session=session
            )

            # 결제된 응시만 취소 가능
            if existing_payment and existing_payment.status != PaymentStatusEnum.PAID:
                raise HTTPException(
                    status_code=400, detail="Already payment applied Test")

            payment = self.payment_service.cancel_payment(
                payment_id=existing_payment.id, user_id=actant_id, session=session)

            # 응시인원 감소
            test_update = TestUpdate(examineeCount=test.examineeCount - 1)
            self.update_test(
                test_id=test.id, test_update=test_update, session=session)

            return PaymentRead.model_validate(payment)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def bulk_update_test(self, test_updates: list[tuple[int, TestUpdate]], session: Session):
        try:
            results: list[TestRead] = []
            for test_id, test_update in test_updates:
                updated_test = self.update_test(
                    test_id, test_update, session)
                results.append(updated_test)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
