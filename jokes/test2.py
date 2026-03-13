from sqlmodel import Session, select
from database.connection import engine
from models.inform_sys import InformSys

user_id = 1  # замените на реальный ID пользователя из cookies или из таблицы user
with Session(engine) as session:
    user_ratings = session.exec(
        select(InformSys).where(
            InformSys.source_table == "rating",
            InformSys.author_or_user_id == user_id
        )
    ).all()
    print(f"У пользователя {user_id} оценок: {len(user_ratings)}")
    if user_ratings:
        print("Пример:", user_ratings[0])
    else:
        print("Оценок нет — алгоритм вернёт популярное.")