# backend/app/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://syntra:syntradb@localhost/syntra_db")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # placeholder: create DB externally in install script; engine will connect
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
