from fastapi import FastAPI
from sqlmodel import SQLModel

from ..features.users.router import router as user_router
from ..shared.database import engine


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI(on_startup=[create_db_and_tables])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FSD-structured API!"}

app.include_router(user_router)
