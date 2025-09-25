from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from ...dependencies.auth import get_auth_service
from ...features.users.schemas import UserCreate, UserRead
from ...shared.database import get_session
from ...shared.security import security
from . import service
from .schemas import UserSignIn, UserSignInRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead)
def sign_up(
    user_create: UserCreate,
    session: Session = Depends(get_session),
    auth_service: service.AuthService = Depends(get_auth_service)
):
    return auth_service.sign_up(user_create=user_create, session=session)


@router.post("/login", response_model=UserSignInRead)
def login(
    user_signIn: UserSignIn,
    session: Session = Depends(get_session),
    auth_service: service.AuthService = Depends(get_auth_service)
):
    return auth_service.sign_in(user_signIn=user_signIn, session=session)


@router.get("/me", response_model=UserRead)
def get_my(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
    auth_service: service.AuthService = Depends(get_auth_service)
):
    return auth_service.get_my_by_token(access_token=credentials.credentials, session=session)
