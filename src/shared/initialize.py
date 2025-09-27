
from sqlmodel import SQLModel

from .database import engine, get_session
from .seed import seed_courses_and_tests, seed_users


def init_db():
    SQLModel.metadata.create_all(engine)

    with next(get_session()) as session:
        seed_users(session)
        seed_courses_and_tests(session)
