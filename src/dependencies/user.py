

from ..features.users.service import UserService


def get_user_service() -> UserService:
    return UserService()
