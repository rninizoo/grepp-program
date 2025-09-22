from fastapi import HTTPException
from sqlmodel import Session, select

from ...entities.users import User
from .schemas import UserCreate


def create_new_user(user_create: UserCreate, session: Session) -> User:
    # 이메일 중복 체크
    existing_user = session.exec(select(User).where(User.email == user_create.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User.from_orm(user_create)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def get_all_users(session: Session, skip: int, limit: int) -> list[User]:
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users
