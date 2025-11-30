from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from database.connection import get_session
from models.users import User, NewUser, UserSignIn

user_router = APIRouter(tags=["User"])

@user_router.post("/signup")
async def sign_new_user(data: NewUser, session: Session = Depends(get_session)) -> dict:
    """Регистрация нового пользователя в БАЗЕ ДАННЫХ"""
    # Проверяем существование пользователя в БД
    statement = select(User).where(User.email == data.email)
    results = session.exec(statement)
    existing_user = results.first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied email exists"
        )
    
    # Создаем нового пользователя в БД
    user = User(email=data.email, password=data.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "message": "User successfully registered!"
    }

@user_router.post("/signin")
async def sign_user_in(user: UserSignIn, session: Session = Depends(get_session)) -> dict:
    """Вход пользователя - проверка в БАЗЕ ДАННЫХ"""
    # Ищем пользователя в БД
    statement = select(User).where(User.email == user.email)
    results = session.exec(statement)
    existing_user = results.first()
    
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )
    
    if existing_user.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong credential passed"
        )
    
    return {
        "message": "User signed in successfully"
    }
