# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "support"

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        orm_mode = True

class MikrotikCreate(BaseModel):
    name: str
    ip: str
    ssh_port: Optional[int] = 22
    ssh_user: str
    credential_type: str = "password"  # or 'key'
    credential: str
    group_ids: Optional[List[int]] = []

class MikrotikOut(BaseModel):
    id: int
    name: str
    ip: str
    ssh_port: int
    ssh_user: str
    class Config:
        orm_mode = True

class ExecRequest(BaseModel):
    targets: List[int]  # mikrotik ids
    command: str
    save_as_favorite: Optional[str] = None
