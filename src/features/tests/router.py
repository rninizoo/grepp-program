from fastapi import APIRouter, Body, Depends
from sqlmodel import Session

from ...features.users.schemas import UserRead
from ...shared.database import get_session
from ...shared.security import authenticate_token
from . import service
from .schemas import TestCreate, TestRead, TestUpdate

router = APIRouter(prefix="/tests", tags=["tests"])

@router.get("", response_model=list[TestRead])
def get_tests(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return service.find_tests(session=session, skip=skip, limit=limit)

@router.post("", response_model=TestRead)
def create_test(current_user: UserRead = Depends(authenticate_token), test_create: TestCreate = Body(...), session: Session = Depends(get_session)):
    return service.create_test(test_create=test_create, actant_id=current_user["id"], session=session)

@router.patch("/{test_id}", response_model=TestRead)
def update_test(test_id: int, test_update: TestUpdate = Body(...), current_user: UserRead = Depends(authenticate_token), session: Session = Depends(get_session)):
    return service.update_test(test_id=test_id, test_update=test_update, actant_id=current_user["id"], session=session)


