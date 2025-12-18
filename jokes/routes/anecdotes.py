from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from database.connection import get_session
from models.anecdotes import Anecdote

anecdote_router = APIRouter(tags=["Anecdotes"])

@anecdote_router.post("/new", response_model=Anecdote)
async def create_anecdote(anecdote: Anecdote, session: Session = Depends(get_session)):
    session.add(anecdote)
    session.commit()
    session.refresh(anecdote)
    return anecdote

@anecdote_router.get("/", response_model=List[Anecdote])
async def get_all_anecdotes(session: Session = Depends(get_session)):
    statement = select(Anecdote)
    results = session.exec(statement).all()
    return results
