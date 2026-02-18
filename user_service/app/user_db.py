from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

USER_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@postgres:5432/user_db"

Base = declarative_base()

def get_user_db(database_url: str = USER_DATABASE_URL) -> Session:
    engine = create_engine(database_url)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        return session_local()
    finally:
        session_local().close()
