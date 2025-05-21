from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def recreate_tables():
    """Drop and recreate all tables"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def init_db():
    """Initialize the database and create tables"""
    Base.metadata.create_all(bind=engine)