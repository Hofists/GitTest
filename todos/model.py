from pydantic import BaseModel
from typing import List, Optional
from fastapi import Form
class Todo(BaseModel):
    id: Optional[int] = None
    item: str
    @classmethod
    def as_form(cls, item: str = Form(...)):
        return cls(id=None, item=item)
class TodoItem(BaseModel):
    item:str
    class Config:
        schema_extra = {
            "example": {
                "item": "Read the next chapter of the book FRR"}}
class TodoItems(BaseModel):
    todos: list[TodoItem]
    class Config:
        schema_extra = {
            "example": {
                "todos": [
                    {
                        "item": "Example1"
                    },
                    {
                        "item": "Example2"
                    }
                ]
            }
        }
