from fastapi import APIRouter, Path, HTTPException, status
todo_router = APIRouter()
from model import Todo, TodoItem, TodoItems
todo_list = []
@todo_router.post("/todo", status_code=201)
async def add_todo(todo: Todo) -> dict:
    todo_list.append(todo)
    return {"message": "Todo added successfully"}
@todo_router.get("/todo", response_model=TodoItems, status_code=201)
async def retrieve_todos() -> dict:
    return {"todos": todo_list}
@todo_router.get("/todo/{todo_id}", status_code=201)
async def get_single_todo(todo_id: int = Path
(..., title="The ID of the todo to retrieve.")) -> dict:
    for todo in todo_list:
        if todo.id == todo_id:
            return {
                "todo": todo
                }
    raise HTTPException( status_code=status.HTTP_404_NOT_FOUND,detail="Todo с таким ID не найден.",)
@todo_router.put("/todo/{todo_id}", status_code=201)
async def update_todo(todo_data: TodoItem, todo_id: int = Path
(..., title="The ID of the todo to be updated")) -> dict:
    for todo in todo_list:
        if todo.id == todo_id:
            todo.item = todo_data.item
            return {"message": "Todo обновлен успешно."}
    raise HTTPException( status_code=status.HTTP_404_NOT_FOUND,detail="Todo с таким ID не найден.",)
@todo_router.delete("/todo/{todo_id}", status_code=201)
async def delete_single_todo(todo_id: int) -> dict:
    for index in range(len(todo_list)):
        todo = todo_list[index]
        if todo.id == todo_id:
            todo_list.pop(index)
            return {"message": "Todo удален успешно."}
    raise HTTPException( status_code=status.HTTP_404_NOT_FOUND,detail="Todo с таким ID не найден.",)
@todo_router.delete("/todo", status_code=201)
async def delete_all_todo() -> dict:
    todo_list.clear()
    return {"message": "Все Todo удалены :)."}
