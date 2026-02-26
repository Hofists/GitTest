import uvicorn
from fastapi import FastAPI
from database.connection import create_db_and_tables
from routes.users import user_router
from routes.anecdotes import router as anecdotes_router
from routes.interactions import router as interaction_router

app = FastAPI()

app.include_router(user_router)
app.include_router(anecdotes_router)
app.include_router(interaction_router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
