from pydantic import BaseModel
class Todo(BaseModel):
    id: int
    item: str
    class Config:
        Schema_extra = {
            "example": {
                "id": 1,
                "item": "example FRR"}}
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
