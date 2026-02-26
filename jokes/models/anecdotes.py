from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Anecdote(SQLModel, table=True):
    __tablename__ = "anecdote"
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    author_id: int 
    publication_date: datetime = Field(default_factory=datetime.utcnow)
    likes_count: int = Field(default=0)
