# Tablero de Gestión — Corredor Pisco–Ica (versión plana)

Pipeline comercial compartido en vivo. Backend **FastAPI + PostgreSQL**, frontend HTML.
Todos los archivos están en la **raíz** (sin carpetas) para que subir a GitHub sea directo.

## Despliegue en Render (≈5 min)

1. Sube TODOS estos archivos a un repositorio de GitHub (todos al mismo nivel, sin carpetas):
   `main.py`, `db.py`, `models.py`, `seed.py`, `auth.py`, `index.html`,
   `render.yaml`, `requirements.txt`, `README.md`.
2. En Render: **New + → Blueprint** → conecta el repositorio.
3. Render lee `render.yaml` y crea el servicio web + la base PostgreSQL + `APP_TOKEN`. Clic en **Apply**.
4. Cuando el servicio esté **Live**, abre su URL pública.
5. Copia el token: servicio → pestaña **Environment** → valor de `APP_TOKEN`.
6. Ábrelo en el tablero, ingresa el token y compártelo con tu equipo.

La base se **siembra sola** con las 21 cuentas la primera vez (solo si está vacía).
Editar cuentas nunca borra datos.

## Local (opcional)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# http://localhost:8000  (sin APP_TOKEN no pide clave; usa SQLite local)
```

## Archivos

- `main.py` — API FastAPI + sirve el tablero
- `db.py` — conexión (Postgres en Render, SQLite en local)
- `models.py` — modelo de datos (25 campos + auditoría)
- `auth.py` — token compartido
- `seed.py` — carga inicial de 21 cuentas
- `index.html` — tablero

*Datos base verificados en fuentes públicas a jul-2026. Validar razón social y RUC en SUNAT.*
