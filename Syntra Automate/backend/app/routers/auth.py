# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas
from ..db import get_db
from ..auth import verify_password, create_access_token, get_password_hash
from ..deps import get_db_dep

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_dep)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # NOTE: should implement lockout/attempt counting in production
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserOut)
def register(u: schemas.UserCreate, db: Session = Depends(get_db_dep)):
    existing = db.query(models.User).filter(models.User.username == u.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = models.User(username=u.username, hashed_password=get_password_hash(u.password), role=u.role)
    db.add(user); db.commit(); db.refresh(user)
    return user
