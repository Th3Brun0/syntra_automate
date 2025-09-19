# backend/app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import require_admin, get_db_dep
from .. import models, schemas
from ..auth import get_password_hash

router = APIRouter()

@router.post("/groups")
def create_group(name: str, description: str = "", db: Session = Depends(get_db_dep), admin = Depends(require_admin)):
    g = models.Group(name=name, description=description)
    db.add(g); db.commit(); db.refresh(g)
    return {"id": g.id, "name": g.name}

@router.post("/users")
def create_user(username: str, password: str, role: str = "support", db: Session = Depends(get_db_dep), admin = Depends(require_admin)):
    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="exists")
    u = models.User(username=username, hashed_password=get_password_hash(password), role=role)
    db.add(u); db.commit(); db.refresh(u)
    return {"id": u.id, "username": u.username}
