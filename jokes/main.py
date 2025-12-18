import uvicorn
from fastapi import FastAPI
from database.connection import conn
from routes.users import user_router
from routes.anecdotes import anecdote_router
# from routes.interactions import interaction_router

app = FastAPI()

# Регистрация роутеров
app.include_router(user_router, prefix="/user")
app.include_router(anecdote_router, prefix="/anecdote")

# Создание БД при старте
@app.on_event("startup")
def on_startup():
    conn()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
