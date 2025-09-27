
from sqlmodel import SQLModel  # noqa: I001

from ..entities.users import User
from ..entities.courses import Course
from ..entities.tests import Test
from .database import engine
from .seed import seed_courses_and_tests, seed_users


def init_db():
    SQLModel.metadata.create_all(engine, tables=[User.__table__])
    # 그 다음 courses, tests 테이블 생성
    SQLModel.metadata.create_all(
        engine, tables=[Course.__table__, Test.__table__])

    seed_users(engine)
    seed_courses_and_tests(engine)
