from sqlmodel import SQLModel, Session, create_engine
from models.users import User
from models.anecdotes import Anecdote
from models.interactions import Rating, Favorite
from models.inform_sys import InformSys

database_file = "jokes.db"
database_connection_string = f"sqlite:///{database_file}"
connect_args = {"check_same_thread": False}

engine = create_engine(database_connection_string, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
