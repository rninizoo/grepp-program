from fastapi import APIRouter, Depends
from sqlmodel import Session

from ...dependencies.user import get_user_service
from ...shared.database import get_session
from .schemas import UserRead
from .service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def get_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
):
    return user_service.find_users(session=session, skip=skip, limit=limit)
