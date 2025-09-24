from sqlmodel import SQLModel


class BaseModel(SQLModel):
    model_config = {"arbitrary_types_allowed": True}
