from fastapi import FastAPI
from routes.users import user_router
from routes.events import event_router
from database.connection import Settings
import uvicorn
from contextlib import asynccontextmanager

app = FastAPI(
    title="Event Planner API",
    description="A simple event planning application built with FastAPI",
    version="1.0.0"
)

app.include_router(user_router, prefix="/user")
app.include_router(event_router, prefix="/event")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await settings.initialize_database()
    
#@app.on_event("startup")
#async def startup_event():
 #   await Settings.initialize_database()

@app.get("/")
async def root():
    return {
        "message": "Welcome to Event Planner API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
