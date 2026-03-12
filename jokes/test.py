from sqlmodel import Session, select
from database.connection import engine
from models.inform_sys import InformSys

with Session(engine) as session:
    ratings = session.exec(select(InformSys).where(InformSys.source_table == "rating")).all()
    print(f"Найдено оценок: {len(ratings)}")
    if ratings:
        print("Пример оценки:", ratings[0])
    else:
        print("Нет данных об оценках! Запустите генератор тестовых данных из практической №5.")
