import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from db import Base, engine, get_db
import models
from auth import require_token
from seed import seed_if_empty

BASE_DIR = Path(__file__).resolve().parent

# Campos que el equipo puede editar desde el tablero
EDITABLE = {"prioridad", "tonelaje", "operador", "vencimiento", "contacto", "cargo",
            "correo", "celular", "etapa", "ultimo_contacto", "proxima_accion",
            "fecha_proxima", "responsable", "valor", "prob", "estado", "notas"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_if_empty()
    yield

app = FastAPI(title="Gestión Pisco–Ica", lifespan=lifespan)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/config")
def config():
    """Indica si el servidor exige token (para que el tablero pida la clave)."""
    return {"auth_required": bool(os.getenv("APP_TOKEN", ""))}

@app.get("/api/accounts", dependencies=[Depends(require_token)])
def list_accounts(db: Session = Depends(get_db)):
    rows = db.query(models.Account).order_by(models.Account.id).all()
    return [r.as_dict() for r in rows]

@app.put("/api/accounts/{account_id}", dependencies=[Depends(require_token)])
def update_account(account_id: int, payload: dict, db: Session = Depends(get_db)):
    acc = db.get(models.Account, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    updated_by = payload.pop("updated_by", "") or ""
    for k, v in payload.items():
        if k in EDITABLE:
            setattr(acc, k, "" if v is None else str(v))
    if updated_by:
        acc.updated_by = updated_by
    db.commit()
    db.refresh(acc)
    return acc.as_dict()

@app.get("/")
def index():
    return FileResponse(BASE_DIR / "index.html")
