import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

def _normalize(url: str) -> str:
    """Render entrega 'postgresql://...'; el driver psycopg3 requiere el prefijo +psycopg."""
    if not url:
        return "sqlite:///./gestion.db"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

DATABASE_URL = _normalize(os.getenv("DATABASE_URL", ""))

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
