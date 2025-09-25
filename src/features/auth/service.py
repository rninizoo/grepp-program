from fastapi import HTTPException
from sqlmodel import Session

from ...entities.users import User
from ...features.users.schemas import UserCreate, UserRead
from ...shared.security import authenticate, create_access_token, verify_password
from ..users.service import UserService
from .schemas import UserSignIn, UserSignInRead


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def sign_up(self, user_create: UserCreate, session: Session) -> User:
        # TODO: email 형식 validation
        new_user = self.user_service.create_user(
            user_create=user_create, session=session)

        return new_user

    def sign_in(self, user_signIn: UserSignIn, session: Session) -> UserSignInRead:
        found_user = self.user_service.find_user_by_email(
            email=user_signIn.email, session=session)
        if not found_user:
            raise HTTPException(status_code=404, detail="User Not Registered")

        if not verify_password(user_signIn.password, found_user.password):
            raise HTTPException(status_code=401, detail="Invalid password")

        access_token = create_access_token(
            data={"sub": found_user.email, "username": found_user.username, "id": found_user.id, "isDestroyed": found_user.isDestroyed})

        return {"accessToken": access_token}

    def get_my_by_token(self, access_token: str, session: Session) -> UserRead:
        token = authenticate(access_token=access_token)
        found_user = self.user_service.find_user_by_id(
            token["id"], session=session)

        if not found_user:
            raise HTTPException(status_code=404, detail="User Not Found")

        return {
            "id": token["id"],
            "username": token["username"],
            "email": token["sub"],
            "isDestroyed": token["isDestroyed"]
        }
