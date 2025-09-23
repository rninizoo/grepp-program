from fastapi import HTTPException
from sqlmodel import Session, select

from ...entities.users import User
from ...shared.security import hash_password
from .schemas import UserCreate, UserRead


def create_user(user_create: UserCreate, session: Session) -> User:
    # 이메일 중복 체크
    existing_user = session.exec(select(User).where(User.email == user_create.email, User.isDestroyed.is_(False))).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_password = hash_password(user_create.password)

    # pw hashing
    user_data = user_create.model_dump(exclude={"password"})
    db_user = User(**user_data, password=hashed_password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def find_users(session: Session, skip: int, limit: int) -> list[UserRead]:
    users = session.exec(select(User).where(User.isDestroyed.is_(False)).offset(skip).limit(limit)).all()
    return [UserRead.model_validate(user) for user in users]


def find_user_by_email(email: str, session: Session) -> User | None:
    statement = select(User).where(User.email == email, User.isDestroyed.is_(False))
    found_user = session.exec(statement).first()
    if not found_user:
        return None
    return found_user
