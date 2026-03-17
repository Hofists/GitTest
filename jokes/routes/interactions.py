from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from database.connection import get_session
from database.dependence import get_current_user
from models.users import User
from models.anecdotes import Anecdote
from models.interactions import Favorite, Rating
from models.inform_sys import InformSys

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
        old_value = existing.value
        existing.value = value
        session.add(existing)
        
        # Обновляем в inform_sys
        inform_entry = session.exec(
            select(InformSys).where(
                InformSys.source_table == "rating",
                InformSys.original_id == existing.id
            )
        ).first()
        if inform_entry:
            inform_entry.value = value
            session.add(inform_entry)
    else:
        new_rating = Rating(user_id=user.id, anecdote_id=anecdote_id, value=value)
        session.add(new_rating)
        session.flush()  # Чтобы получить ID
        
        # Дублируем в inform_sys
        inform_entry = InformSys(
            source_table="rating",
            original_id=new_rating.id,
            author_or_user_id=user.id,
            anecdote_id=anecdote_id,
            value=value
        )
        session.add(inform_entry)
    
    joke = session.get(Anecdote, anecdote_id)
    if joke:
        # Обновляем likes_count в анекдоте
        if existing:
            joke.likes_count = joke.likes_count - old_value + value
        else:
            joke.likes_count += value 
        session.add(joke)
        
        # Обновляем likes_count в inform_sys для анекдота
        inform_anecdote = session.exec(
            select(InformSys).where(
                InformSys.source_table == "anecdote",
                InformSys.original_id == anecdote_id
            )
        ).first()
        if inform_anecdote:
            inform_anecdote.likes_count = joke.likes_count
            session.add(inform_anecdote)
    
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
        # Удаляем только из базовой таблицы
        session.delete(existing)
    else:
        # Добавляем только в базовую таблицу (без дублирования в inform_sys)
        new_favorite = Favorite(user_id=user.id, anecdote_id=anecdote_id)
        session.add(new_favorite)
    
    session.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
