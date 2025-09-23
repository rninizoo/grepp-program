from fastapi import APIRouter, Depends
from sqlmodel import Session

from ...shared.database import get_session
from . import service
from .schemas import UserRead

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[UserRead])
def get_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return service.find_users(session=session, skip=skip, limit=limit)
