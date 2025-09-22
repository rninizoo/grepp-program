from typing import Optional

from sqlmodel import SQLModel


# 사용자 생성을 위한 입력 스키마
class UserCreate(SQLModel):
    username: str
    email: str
    full_name: Optional[str] = None

# 사용자 조회를 위한 출력 스키마
class UserRead(SQLModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
