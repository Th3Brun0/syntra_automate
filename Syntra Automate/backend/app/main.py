# backend/app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db, engine
from .routers import auth, mikrotik, exec_cmd, admin
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Syntra API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()
    # Create tables if not present
    from .models import Base
    Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(mikrotik.router, prefix="/mikrotiks", tags=["mikrotiks"])
app.include_router(exec_cmd.router, prefix="/exec", tags=["exec"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
