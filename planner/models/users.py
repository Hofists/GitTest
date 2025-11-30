from pydantic import EmailStr
from typing import Optional, List
from models.events import Event
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "fastapi@packt.com",
                "password": "rts1234"
            }
        }

class NewUser(SQLModel):
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "fastapi@packt.com",
                "password": "rts1234"
            }
        }

class UserSignIn(SQLModel):
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "fastapi@packt.com",
                "password": "rts1234"
            }
        }
