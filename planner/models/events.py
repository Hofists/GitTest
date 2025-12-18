from beanie import Document
from typing import Optional, List
from pydantic import BaseModel

class Event(Document):
    title: str
    image: str
    description: str
    tags: List[str]
    location: str
    
    class Config:
        schema_extra = {
            "example": {
                "title": "FastAPI noSQL DB",
                "image": "https://linktomyimage.com/image.png",
                "description": "In description pole you may describe your event",
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet"
            }
        }
    class Settings:
        name = "events"
class EventUpdate(BaseModel):
    title: Optional[str]
    image: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    location: Optional[str]
    class Config:
        schema_extra = {
            "example": {
                "title": "FastAPI Book Launch","image":
                "https://linktomyimage.com/image.png",
                "description": "same",
                "tags": ["python", "fastapi", "book","launch"],
                "location": "Google Meet"
            }
        }
