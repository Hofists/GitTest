from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class InformSys(SQLModel, table=True):
    __tablename__ = "inform_sys"
    source_table: str = Field(primary_key=True)
    original_id: int = Field(primary_key=True)
    content: Optional[str] = None
    author_or_user_id: Optional[int] = None
    publication_date: Optional[datetime] = None
    likes_count: Optional[int] = None
    anecdote_id: Optional[int] = None
    value: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
