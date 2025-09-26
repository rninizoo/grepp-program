from typing import Literal

from fastapi import APIRouter, Body, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from ...dependencies.auth import get_auth_service
from ...dependencies.test import get_test_service
from ...features.auth.service import AuthService
from ...features.payments.schemas import PaymentApplyTest, PaymentRead
from ...shared.database import get_session
from ...shared.security import security
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
    return test_service.find_tests(skip=skip, limit=limit, query_opts=query_opts, session=session)


@router.post("", response_model=TestRead)
def create_test(
    test_create: TestCreate = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    session: Session = Depends(get_session),
    test_service: service.TestService = Depends(get_test_service),
):
    current_user = auth_service.get_my_by_token(
        credentials.credentials, session=session)
    return test_service.create_test(test_create=test_create, actant_id=current_user["id"], session=session)


@router.patch("/{test_id}", response_model=TestRead)
def update_test(
    test_id: str,
    test_update: TestUpdate = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    session: Session = Depends(get_session),
    test_service: service.TestService = Depends(get_test_service),
):
    auth_service.get_my_by_token(
        credentials.credentials, session=session)
    return test_service.update_test(
        test_id=test_id, test_update=test_update, session=session
    )


@router.post("/{test_id}/apply", response_model=PaymentRead)
def apply_test(
    test_id: str,
    payment_apply_test: PaymentApplyTest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    session: Session = Depends(get_session),
    test_service: service.TestService = Depends(get_test_service),
):
    current_user = auth_service.get_my_by_token(
        credentials.credentials, session=session)
    return test_service.apply_test(test_id=test_id, payment_apply_test=payment_apply_test, actant_id=current_user['id'], session=session)
