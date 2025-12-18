from sqlmodel import SQLModel, Session, create_engine

# Имя файла базы данных (SQLite для простоты, как в примере)
database_file = "jokes.db"
database_connection_string = f"sqlite:///{database_file}"

# check_same_thread=False нужен только для SQLite
connect_args = {"check_same_thread": False}

engine_url = create_engine(database_connection_string, echo=True, connect_args=connect_args)

def conn():
    """Создает таблицы в БД при запуске"""
    SQLModel.metadata.create_all(engine_url)

def get_session():
    """Генератор сессий для Dependency Injection в маршрутах"""
    with Session(engine_url) as session:
        yield session
