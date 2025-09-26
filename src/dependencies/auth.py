from fastapi import Depends

from ..dependencies.user import get_user_service
from ..features.auth.service import AuthService
from ..features.users.service import UserService


def get_auth_service(user_service: UserService = Depends(get_user_service)) -> AuthService:
    return AuthService(user_service)
