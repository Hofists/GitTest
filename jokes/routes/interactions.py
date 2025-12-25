from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from database.connection import get_session
from database.dependence import get_current_user
from models.users import User
from models.anecdotes import Anecdote
from models.interactions import Favorite, Rating

router = APIRouter(prefix="/interaction", tags=["Interaction Service"])

@router.post("/rate/{anecdote_id}")
async def rate_anecdote(
    anecdote_id: int,
    value: int = Form(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not user:
        return RedirectResponse(url="/user/login", status_code=status.HTTP_303_SEE_OTHER)

    existing = session.exec(select(Rating).where(Rating.user_id == user.id, Rating.anecdote_id == anecdote_id)).first()
    
    if existing:
        existing.value = value
        session.add(existing)
    else:
        new_rating = Rating(user_id=user.id, anecdote_id=anecdote_id, value=value)
        session.add(new_rating)
    
    joke = session.get(Anecdote, anecdote_id)
    if joke:
        joke.likes_count += value 
        session.add(joke)
    
    session.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/favorite/{anecdote_id}")
async def toggle_favorite(
    anecdote_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not user:
        return RedirectResponse(url="/user/login", status_code=status.HTTP_303_SEE_OTHER)

    existing = session.exec(select(Favorite).where(Favorite.user_id == user.id, Favorite.anecdote_id == anecdote_id)).first()
    if existing:
        session.delete(existing)
    else:
        session.add(Favorite(user_id=user.id, anecdote_id=anecdote_id))
    
    session.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
