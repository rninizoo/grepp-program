from fastapi import APIRouter, Depends
from sqlmodel import Session

from ...shared.database import get_session
from . import service
from .schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead)
def create_user(user_create: UserCreate, session: Session = Depends(get_session)):
    return service.create_new_user(user_create=user_create, session=session)

@router.get("/", response_model=list[UserRead])
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return service.get_all_users(session=session, skip=skip, limit=limit)
