from typing import Literal

from fastapi import APIRouter, Body, Depends, Query
from sqlmodel import Session

from ...dependencies.test import get_test_service
from ...features.payments.schemas import PaymentRead
from ...features.users.schemas import UserRead
from ...shared.database import get_session
from ...shared.security import authenticate_token
from . import service
from .schemas import TestCreate, TestQueryOpts, TestRead, TestUpdate

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("", response_model=list[TestRead])
def get_tests(
    status: str = Query("AVAILABLE", description="Filter by test status"),
    sort: Literal["created", "popular"] = Query(
        "created", description="Sort by created or popular"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    test_service: service.TestService = Depends(get_test_service),
):
    query_opts = TestQueryOpts(status=status, sort=sort)
    return test_service.find_tests(session=session, skip=skip, limit=limit, query_opts=query_opts)


@router.post("", response_model=TestRead)
def create_test(
    current_user: UserRead = Depends(authenticate_token),
    test_create: TestCreate = Body(...),
    session: Session = Depends(get_session),
    test_service: service.TestService = Depends(get_test_service),
):
    return test_service.create_test(test_create=test_create, actant_id=current_user["id"], session=session)


@router.patch("/{test_id}", response_model=TestRead)
def update_test(
    test_id: int,
    test_update: TestUpdate = Body(...),
    current_user: UserRead = Depends(authenticate_token),
    session: Session = Depends(get_session),
    test_service: service.TestService = Depends(get_test_service),
):
    return test_service.update_test(
        test_id=test_id, test_update=test_update, actant_id=current_user["id"], session=session
    )


@router.post("/{test_id}/apply", response_model=PaymentRead)
def apply_test(
    test_id: int,
    current_user: UserRead = Depends(authenticate_token),
    session: Session = Depends(get_session),
    test_service: service.TestService = Depends(get_test_service),
):
    return test_service.apply_test(test_id=test_id, actant_id=current_user["id"], session=session)
