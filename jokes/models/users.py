from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    password: str
    is_deleted: bool = Field(default=False)

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword",
                "is_deleted": False
            }
        }

# Модель для входа (не таблица БД)
class UserSignIn(SQLModel):
    email: EmailStr
    password: str
