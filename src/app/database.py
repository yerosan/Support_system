# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
import os

from config.config import settings

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/chat_app")
# DATABASE_URL = "postgresql://postgres:postsane!4422@localhost:5432/chat_app"

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base: DeclarativeMeta = declarative_base()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
