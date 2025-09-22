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
def createUser(user_create: UserCreate, session: Session = Depends(get_session)):
    return service.signUp(user_create=user_create, session=session)

@router.post("/login", response_model=UserSignInRead)
def getUsers(user_signIn: UserSignIn, session: Session = Depends(get_session)):
    return service.signIn(user_signIn=user_signIn, session=session)

@router.get("/my", response_model=UserRead)
def getMy( access_token: HTTPAuthorizationCredentials = Depends(security)):
    return service.getMyInfo(access_token=access_token.credentials)
