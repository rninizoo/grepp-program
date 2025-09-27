from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel

from ..features.auth.router import router as auth_router
from ..features.courses.router import router as course_router
from ..features.payments.router import router as payment_router
from ..features.tests.router import router as test_router
from ..features.users.router import router as user_router
from ..shared.database import engine


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI(on_startup=[create_db_and_tables])


@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(test_router)
app.include_router(course_router)
app.include_router(payment_router)
