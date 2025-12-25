from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database.connection import get_session
from database.dependence import get_current_user
from models.anecdotes import Anecdote
from models.users import User

router = APIRouter(tags=["Content Service"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def home_page(
    request: Request, 
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    anecdotes = session.exec(select(Anecdote).order_by(Anecdote.id.desc())).all()
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "anecdotes": anecdotes,
        "user": user
    })

@router.post("/anecdote/new")
async def create_anecdote(
    content: str = Form(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not user:
        return RedirectResponse(url="/user/login", status_code=status.HTTP_303_SEE_OTHER)

    new_joke = Anecdote(content=content, author_id=user.id)
    session.add(new_joke)
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
        session.delete(joke)
        session.commit()
        return RedirectResponse(url="/user/profile", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/", status_code=status.HTTP_403_FORBIDDEN)
