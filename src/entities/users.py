from datetime import datetime, timezone

import ulid
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(
        ulid.new()), primary_key=True, index=True)
    username: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    password: str = Field(nullable=False)
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updatedAt: datetime = Field(
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=True,

    )
    isDestroyed: bool = Field(default=False, nullable=False)
