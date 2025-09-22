from sqlmodel import SQLModel

class UserSignIn(SQLModel):
    email: str
    password: str

class UserSignInRead(SQLModel):
   accessToken: str
