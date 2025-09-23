from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from ...entities.tests import Test
from .schemas import TestCreate, TestRead, TestUpdate


def create_test(test_create: TestCreate, actant_id: int,session: Session) -> Test:
    # title 중복 체크
    existing_test = session.exec(select(Test).where(Test.title == test_create.title, Test.isDestroyed.is_(False))).first()
    if existing_test:
        raise HTTPException(status_code=409, detail="Test already registered")

    test = Test(
        title=test_create.title,
        description=test_create.description,
        startAt=test_create.startAt,
        endAt=test_create.endAt,
        status=test_create.status,
        actantId=actant_id
    )

    session.add(test)
    session.commit()
    session.refresh(test)
    return test

def find_tests(session: Session, skip: int, limit: int) -> list[TestRead]:
    tests = session.exec(select(Test).where(Test.isDestroyed.is_(False)).offset(skip).limit(limit)).all()
    return [TestRead.model_validate(test) for test in tests]

def update_test(test_id: int, test_update: TestUpdate, actant_id :int, session: Session) -> TestRead:

    stmt = select(Test).where(Test.id == test_id).with_for_update()
    test = session.exec(stmt).one_or_none()

    # 존재여부 체크
    if not test or test.isDestroyed :
        raise HTTPException(status_code=404, detail="Test not found")

    # 존재여부 시작일, 종료일 체크
    if test.startAt > test.endAt:
        raise HTTPException(status_code=400, detail="Cannot update this test on startAt with endAt")

    # 작성자만 변경 가능
    if test.actantId != actant_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this test")


    update_data = test_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(test, key, value)

    test.updatedAt = datetime.now(timezone.utc)
    session.add(test)
    session.commit()
    session.refresh(test)

    return TestRead.model_validate(test)

def bulk_update_test(test_updates: list[tuple[int, TestUpdate]], actant_id: int, session: Session):
    try:
        with session.begin():
            results: list[TestRead] = []
            for test_id, test_update in test_updates:
                updated_test = update_test(test_id, test_update, actant_id, session)
                results.append(updated_test)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
