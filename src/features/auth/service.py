from sqlmodel import Session

from ...entities.users import User
from ...features.users.schemas import UserCreate, UserRead
from ...shared.security import authenticate, createAccessToken
from ..users.service import createUser, findUserByEmail
from .schemas import UserSignIn, UserSignInRead


def signUp(user_create: UserCreate, session: Session) -> User:
    new_user = createUser(user_create=user_create, session=session)

    return new_user

def signIn(user_signIn: UserSignIn, session: Session) -> UserSignInRead:
      found_user = findUserByEmail(email=user_signIn.email, session=session)
      print(user_signIn, found_user)

      access_token = createAccessToken(data={"sub":found_user.email, "username": found_user.username, "id": found_user.id, "isDestroyed": found_user.isDestroyed })

      return {"accessToken": access_token}

def getMyInfo(access_token: str) -> UserRead:
     token = authenticate(access_token=access_token)
     return {
        "id": token["id"],
        "username": token["username"],
        "email": token["sub"],
        "isDestroyed": token["isDestroyed"]
    }

