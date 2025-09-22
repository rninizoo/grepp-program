from fastapi import HTTPException
from sqlmodel import Session, select

from ...entities.users import User
from ...shared.security import hashPassword
from .schemas import UserCreate, UserRead


def createUser(user_create: UserCreate, session: Session) -> User:
    # 이메일 중복 체크
    existing_user = session.exec(select(User).where(User.email == user_create.email, User.isDestroyed.is_(False))).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_password = hashPassword(user_create.password)

    # pw hashing
    user_data = user_create.model_dump(exclude={"password"})
    db_user = User(**user_data, password=hashed_password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def findUsers(session: Session, skip: int, limit: int) -> list[UserRead]:
    users = session.exec(select(User).where(User.isDestroyed.is_(False)).offset(skip).limit(limit)).all()
    return [UserRead.model_validate(user) for user in users]


def findUserByEmail(email: str, session: Session) -> User | None:
    statement = select(User).where(User.email == email, User.isDestroyed.is_(False))
    user_from_db = session.exec(statement).first()
    if not user_from_db:
        return None
    return UserRead.model_validate(user_from_db)
