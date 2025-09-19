# backend/app/routers/mikrotik.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..deps import get_current_user, require_admin, get_db_dep
from ..crypto import encrypt_text, decrypt_text

router = APIRouter()

@router.post("/", response_model=schemas.MikrotikOut)
def create_mikrotik(payload: schemas.MikrotikCreate, db: Session = Depends(get_db_dep), user = Depends(get_current_user)):
    # only admin allowed to create devices
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="admin role required")
    enc = encrypt_text(payload.credential)
    m = models.Mikrotik(
        name=payload.name, ip=payload.ip, ssh_port=payload.ssh_port,
        ssh_user=payload.ssh_user, credential_type=payload.credential_type,
        credential_encrypted=enc
    )
    db.add(m); db.commit(); db.refresh(m)
    # group association if given
    if payload.group_ids:
        groups = db.query(models.Group).filter(models.Group.id.in_(payload.group_ids)).all()
        m.groups = groups
        db.commit()
    return m

@router.get("/", response_model=list[schemas.MikrotikOut])
def list_mikrotiks(db: Session = Depends(get_db_dep), user = Depends(get_current_user)):
    # support only sees groups they belong to
    if user.role == "admin":
        q = db.query(models.Mikrotik).all()
    else:
        group_ids = [g.id for g in user.groups]
        q = db.query(models.Mikrotik).join(models.mikrotik_group).filter(models.mikrotik_group.c.group_id.in_(group_ids)).all()
    return q

@router.get("/{mikrotik_id}", response_model=schemas.MikrotikOut)
def get_mikrotik(mikrotik_id: int, db: Session = Depends(get_db_dep), user = Depends(get_current_user)):
    m = db.query(models.Mikrotik).filter(models.Mikrotik.id == mikrotik_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Not found")
    # permission check
    if user.role != "admin":
        allowed_ids = [mi.id for g in user.groups for mi in g.mikrotiks]
        if m.id not in allowed_ids:
            raise HTTPException(status_code=403, detail="No access")
    return m

@router.delete("/{mikrotik_id}")
def delete_mikrotik(mikrotik_id: int, db: Session = Depends(get_db_dep), user = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="admin required")
    m = db.query(models.Mikrotik).filter(models.Mikrotik.id == mikrotik_id).first()
    if not m:
        raise HTTPException(status_code=404)
    db.delete(m); db.commit()
    return {"ok": True}
