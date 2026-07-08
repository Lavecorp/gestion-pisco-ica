import os
from fastapi import Header, HTTPException

def require_token(x_app_token: str | None = Header(default=None)):
    """Valida el token compartido. Si APP_TOKEN no está configurado (dev), permite el acceso."""
    expected = os.getenv("APP_TOKEN", "")
    if not expected:
        return  # modo desarrollo sin token
    if x_app_token != expected:
        raise HTTPException(status_code=401, detail="Token inválido")
