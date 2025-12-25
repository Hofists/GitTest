from fastapi import APIRouter, Depends, Request, Form, status, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database.connection import get_session
from database.dependence import get_current_user
from models.users import User
from models.anecdotes import Anecdote
from models.interactions import Favorite

user_router = APIRouter(prefix="/user", tags = ["User Service"])
templates = Jinja2Templates(directory="templates")

@user_router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@user_router.post("/register")
async def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    username: str = Form(...),
    session: Session = Depends(get_session)
):
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        error_msg = "Неуспешная регистрация: пользователь с таким email уже существует"
        return templates.TemplateResponse("register.html", {"request": request, "error": error_msg})

    new_user = User(email=email, password=password, username=username)
    session.add(new_user)
    session.commit()
    
    return RedirectResponse(url="/user/login", status_code=status.HTTP_303_SEE_OTHER)


@user_router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@user_router.post("/login")
async def login_user(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.email == email)).first()
    
    if not user or user.password != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный email или пароль"})

    redirect = RedirectResponse(url="/user/profile", status_code=status.HTTP_303_SEE_OTHER)
    redirect.set_cookie(key="user_id", value=str(user.id))
    return redirect


@user_router.get("/profile")
async def profile_page(
    request: Request, 
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not user:
        return RedirectResponse(url="/user/login")

    my_anecdotes = session.exec(select(Anecdote).where(Anecdote.author_id == user.id)).all()
    
    fav_links = session.exec(select(Favorite).where(Favorite.user_id == user.id)).all()
    fav_anecdote_ids = [f.anecdote_id for f in fav_links]
    
    favorites = []
    if fav_anecdote_ids:
        favorites = session.exec(select(Anecdote).where(Anecdote.id.in_(fav_anecdote_ids))).all()

    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "user": user,
        "my_anecdotes": my_anecdotes,
        "favorites": favorites
    })

@user_router.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("user_id")
    return response

@user_router.post("/delete")
async def delete_profile(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if user:
        session.delete(user)
        session.commit()
    
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("user_id")
    return response
