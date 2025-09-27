from sqlmodel import Session, create_engine

from .config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


def get_session():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
