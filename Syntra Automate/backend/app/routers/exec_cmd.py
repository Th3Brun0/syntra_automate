# backend/app/routers/exec_cmd.py
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_current_user, get_db_dep
from .. import models, schemas
from ..crypto import decrypt_text
import asyncssh
from ..models import ExecLog

router = APIRouter()

# concurrency semaphore
MAX_CONCURRENT_SSH = int(__import__("os").getenv("MAX_CONCURRENT_SSH", "6"))
semaphore = asyncio.Semaphore(MAX_CONCURRENT_SSH)

async def run_ssh_command(host, port, user, secret, credential_type, command, timeout=10):
    try:
        async with semaphore:
            conn_kwargs = {"host": host, "port": port, "username": user, "known_hosts": None}
            if credential_type == "password":
                conn_kwargs["password"] = secret
            else:
                conn_kwargs["client_keys"] = [secret]  # in memory key requires file; handled below
            async with asyncssh.connect(**conn_kwargs) as conn:
                result = await asyncio.wait_for(conn.run(command), timeout=timeout)
                return {"stdout": result.stdout, "stderr": result.stderr, "exit_status": result.exit_status}
    except Exception as e:
        return {"error": str(e)}

@router.post("/run")
async def execute(req: schemas.ExecRequest, db: Session = Depends(get_db_dep), user = Depends(get_current_user)):
    targets = db.query(models.Mikrotik).filter(models.Mikrotik.id.in_(req.targets)).all()
    if not targets:
        raise HTTPException(status_code=404, detail="No targets")
    # permission check for non-admin
    if user.role != "admin":
        allowed_ids = [mi.id for g in user.groups for mi in g.mikrotiks]
        for t in targets:
            if t.id not in allowed_ids:
                raise HTTPException(status_code=403, detail="No access to one or more targets")
    tasks = []
    for t in targets:
        secret = decrypt_text(t.credential_encrypted)
        credential_type = t.credential_type
        # If key and multi-line private key, asyncssh needs a file - create temp file
        if credential_type == "key" and "\n" in secret:
            import tempfile
            tf = tempfile.NamedTemporaryFile(delete=False)
            tf.write(secret.encode()); tf.flush(); tf.close()
            secret_ref = tf.name
        else:
            secret_ref = secret
        tasks.append(run_ssh_command(t.ip, t.ssh_port, t.ssh_user, secret_ref, credential_type, req.command))
    results = await asyncio.gather(*tasks)
    # log per target
    for t, r in zip(targets, results):
        log = ExecLog(user_id=user.id, user_name=user.username, command=req.command, targets=str(t.id), output=str(r), status="ok" if not r.get("error") else "error")
        db.add(log)
    db.commit()
    return {"results": [{ "id": t.id, "ip": t.ip, "result": r} for t, r in zip(targets, results)]}
