from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from ...features.users.schemas import UserCreate, UserRead
from ...shared.database import get_session
from . import service
from .schemas import UserSignIn, UserSignInRead

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

@router.post("/signup", response_model=UserRead)
def sign_up(user_create: UserCreate, session: Session = Depends(get_session)):
    return service.sign_up(user_create=user_create, session=session)

@router.post("/login", response_model=UserSignInRead)
def login(user_signIn: UserSignIn, session: Session = Depends(get_session)):
    return service.sign_in(user_signIn=user_signIn, session=session)

@router.get("/me", response_model=UserRead)
def get_my(access_token: HTTPAuthorizationCredentials = Depends(security)):
    return service.get_my_info(access_token=access_token.credentials)
