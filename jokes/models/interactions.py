from sqlmodel import SQLModel, Field
from typing import Optional

class Rating(SQLModel, table=True):
    __tablename__ = "rating"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    anecdote_id: int  
    value: int

class Favorite(SQLModel, table=True):
    __tablename__ = "favorite"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    anecdote_id: int
