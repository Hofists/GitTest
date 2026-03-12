from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database.connection import get_session
from database.dependence import get_current_user
from models.anecdotes import Anecdote
from models.users import User
from models.inform_sys import InformSys  # Добавляем импорт
from services.recommendations import get_recommendations_for_user, get_popular_anecdotes
from datetime import datetime

router = APIRouter(tags=["Content Service"])
templates = Jinja2Templates(directory="templates")

def _format_anecdote(inform: InformSys) -> dict:
    """
    Преобразует объект InformSys с source_table='anecdote' в словарь,
    содержащий поля id, content, likes_count, которые ожидает шаблон.
    """
    return {
        "id": inform.original_id,           # используем original_id как идентификатор анекдота
        "content": inform.content,
        "likes_count": inform.likes_count or 0
    }

@router.get("/")
async def home_page(
    request: Request, 
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    anecdotes = session.exec(select(Anecdote).order_by(Anecdote.id.desc())).all()
    # Рекомендации: для авторизованных — персональные, для гостей — популярные
    recommended = []
    if user:
    # Для авторизованного пользователя получаем персональные рекомендации
        recs = get_recommendations_for_user(session, user.id, limit=5)
        recommended = [_format_anecdote(a) for a in recs]
    else:
        # Для гостя — популярные анекдоты
        recs = get_popular_anecdotes(session, limit=5)
        recommended = [_format_anecdote(a) for a in recs]
        
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "anecdotes": anecdotes,
        "user": user,
        "recommended": recommended
    })

@router.post("/anecdote/new")
async def create_anecdote(
    content: str = Form(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not user:
        return RedirectResponse(url="/user/login", status_code=status.HTTP_303_SEE_OTHER)

    # Создаем анекдот
    new_joke = Anecdote(content=content, author_id=user.id)
    session.add(new_joke)
    session.flush()  # Чтобы получить ID
    
    # Дублируем в inform_sys
    inform_entry = InformSys(
        source_table="anecdote",
        original_id=new_joke.id,
        content=content,
        author_or_user_id=user.id,
        publication_date=new_joke.publication_date,
        likes_count=0
    )
    session.add(inform_entry)
    
    session.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/anecdote/delete/{anecdote_id}")
async def delete_anecdote(
    anecdote_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    joke = session.get(Anecdote, anecdote_id)
    if joke and user and user.id == joke.author_id:
        # Удаляем из inform_sys
        inform_entry = session.exec(
            select(InformSys).where(
                InformSys.source_table == "anecdote",
                InformSys.original_id == anecdote_id
            )
        ).first()
        if inform_entry:
            session.delete(inform_entry)
        
        # Удаляем анекдот
        session.delete(joke)
        session.commit()
        return RedirectResponse(url="/user/profile", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/", status_code=status.HTTP_403_FORBIDDEN)
