import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

load_dotenv()

ENGINE = None

if os.getenv("DISABLE_CHECK_SAME_THREAD").lower() == "true":
    extra_args = {"check_same_thread": False}
    ENGINE = create_engine(os.getenv("USER_DATABASE_URL"), poolclass=StaticPool, connect_args=extra_args)
else:
    ENGINE = create_engine(os.getenv("USER_DATABASE_URL"))

SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


class Base(DeclarativeBase):
    __abstract__ = True


def get_user_db() -> Session:
    Base.metadata.create_all(bind=ENGINE)
    db = SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()
