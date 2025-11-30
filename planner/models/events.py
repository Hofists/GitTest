from sqlmodel import JSON, SQLModel, Field, Column
from typing import List, Optional

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    image: str
    description: str
    tags: List[str] = Field(sa_column=Column(JSON))
    location: str
    
    class Config:
        arbitrary_types_allowed = True  
        schema_extra = {
            "example": {
                "title": "FastAPI Book Launch",
                "image": "https://linktomyimage.com/image.png",
                "description": "FastAPI app",
                "tags": ["python", "fastapi", "book","launch"],
                "location": "Google Meet"
            }
        }

class EventUpdate(SQLModel):
    title: Optional[str] = None  
    image: Optional[str] = None  
    description: Optional[str] = None  
    tags: Optional[List[str]] = None  
    location: Optional[str] = None  

    class Config:
        schema_extra = {
            "example": {
                "title": "FastAPI Book Launch",
                "image": "https://linktomyimage.com/image.png",
                "description": "FastAPI app",
                "tags": ["python", "fastapi", "book","launch"],
                "location": "Google Meet"
            }
        }
