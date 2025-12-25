from fastapi import Request, Depends
from sqlmodel import Session
from database.connection import get_session
from models.users import User

def get_current_user(request: Request, session: Session = Depends(get_session)) -> User | None:
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    return session.get(User, int(user_id))
