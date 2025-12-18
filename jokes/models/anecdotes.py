from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Anecdote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id") # Связь с пользователем
    content: str
    publication_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="published") # published, deleted

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "content": "Заходит улитка в бар...",
                "status": "published"
            }
        }
