from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class InformSys(SQLModel, table=True):
    __tablename__ = "inform_sys"
    id: Optional[int] = Field(default=None, primary_key=True)
    source_table: str
    original_id: int
    content: Optional[str] = None
    author_or_user_id: Optional[int] = None
    publication_date: Optional[datetime] = None
    likes_count: Optional[int] = None
    anecdote_id: Optional[int] = None
    value: Optional[float] = None
