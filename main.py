# -*- coding: utf-8 -*-
"""
Tablero de Gestión — Corredor Pisco–Ica  (aplicación en UN SOLO archivo)
Backend FastAPI + PostgreSQL + frontend (HTML/gráficos) embebido.
Desplegar en Render con render.yaml. Solo este archivo contiene toda la lógica.
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse
from sqlalchemy import (create_engine, inspect, text, func,
                        Column, Integer, String, Text, DateTime)
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ─────────────────────────────  BASE DE DATOS  ─────────────────────────────
def _normalize(url: str) -> str:
    if not url:
        return "sqlite:///./gestion.db"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

DATABASE_URL = _normalize(os.getenv("DATABASE_URL", ""))
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─────────────────────────────  MODELO  ─────────────────────────────
class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    prioridad = Column(String, default="Media"); sector = Column(String, default="")
    razon = Column(String, default=""); comercial = Column(String, default="")
    ruc = Column(String, default=""); planta = Column(Text, default="")
    residuos = Column(Text, default=""); tipo = Column(String, default="")
    ton_np = Column(String, default=""); ton_pel = Column(String, default="")
    precio_np = Column(String, default=""); precio_pel = Column(String, default="")
    costo_np = Column(String, default=""); costo_pel = Column(String, default="")
    tonelaje = Column(String, default=""); operador = Column(String, default="")
    vencimiento = Column(String, default=""); contacto = Column(String, default="")
    cargo = Column(String, default=""); correo = Column(String, default=""); celular = Column(String, default="")
    etapa = Column(String, default="Prospecto"); ultimo_contacto = Column(String, default="")
    proxima_accion = Column(Text, default=""); fecha_proxima = Column(String, default="")
    responsable = Column(String, default=""); valor = Column(String, default="")
    prob = Column(String, default=""); estado = Column(String, default="Activo"); notas = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, default="")
    def as_dict(self):
        return {c.name: (getattr(self, c.name).isoformat() if isinstance(getattr(self, c.name), datetime)
                          else getattr(self, c.name)) for c in self.__table__.columns}

# ─────────────────────────────  AUTENTICACIÓN  ─────────────────────────────
def require_token(x_app_token: str | None = Header(default=None)):
    expected = os.getenv("APP_TOKEN", "")
    if not expected:
        return
    if x_app_token != expected:
        raise HTTPException(status_code=401, detail="Token inválido")

# ─────────────────────────────  DATOS INICIALES (21 cuentas)  ─────────────────────────────
SEED = [
 ("Alta","Siderurgia","Corporación Aceros Arequipa S.A.","Aceros Arequipa","20370146994","Panamericana Sur Km 241, Paracas – Pisco","Polvo EAF, escoria, refractarios, lodos, aceites, chatarra, EPP","Peligroso / Mixto","Prospecto","Cuenta ancla. Alto tonelaje peligroso."),
 ("Alta","Metalurgia","Minsur S.A.","Funsur","20100136741","Fundición y Refinería de Estaño, Paracas Km 238.5","Escorias, polvos y lodos con metales, refractarios, aceites, EPP","Peligroso / Mixto","Prospecto","Cuenta ancla."),
 ("Alta","Hidrocarburos/Gas","Pluspetrol Camisea S.A.","Pluspetrol","20510889135","Planta de Fraccionamiento Playa Lobería, Pisco","Lodos aceitosos, borras, catalizadores, suelos contaminados, filtros","Peligroso","Prospecto","Verificar entidad operadora (vs. Pluspetrol Perú Corporation 20304177552)."),
 ("Alta","Pesca","Tecnológica de Alimentos S.A.","TASA","20100971772","Km 15 Carretera Pisco–Paracas","Lodos PAMA/PTAR, sanguaza/borras, aceites, envases de reactivos, EPP","Mixto","Prospecto","Volumen recurrente; picos por temporada."),
 ("Alta","Pesca","Pesquera Diamante S.A.","Diamante","20159473148","Km 16.5 Carretera Pisco–Paracas","Lodos, aceites, envases de químicos, mantenimiento, EPP","Mixto","Prospecto",""),
 ("Alta","Pesca","Austral Group S.A.A.","Austral","20338054115","Lotización Santa Elena de Paracas","Lodos, aceites, envases, EPP, congelado y conservas","Mixto","Prospecto","Confirmar RUC (existe homónimo 'Pesquera Austral')."),
 ("Media","Pesca","Pesquera Hayduk S.A.","Hayduk","20136165667","Paracas – Pisco","Lodos PAMA, aceites, envases de reactivos, chatarra, EPP","Mixto","Prospecto",""),
 ("Media","Pesca","Corporación Pesquera Inca S.A.C.","Copeinca (ex CFG Investment)","20512868046","Paracas – Pisco","Lodos, aceites, envases contaminados, EPP","Mixto","Prospecto","Antes CFG Investment S.A.C."),
 ("Media","Pesca","Pesquera Exalmar S.A.A.","Exalmar","20380336384","Litoral Ica / Pisco","Lodos, aceites, envases de químicos, mantenimiento","Mixto","Prospecto",""),
 ("Media","Pesca","Sea Food Trading S.A.","Sea Food Trading","Por verificar en SUNAT","Lotización Santa Elena, Km 16.85 Pisco–Paracas","Residuos de proceso, aceites, envases, EPP","Mixto","Prospecto","Verificar razón social y RUC."),
 ("Media","Agroindustria","Complejo Agroindustrial Beta S.A.","Beta","20297939131","Valle de Ica / Villacurí","Envases de agroquímicos, plásticos de riego, EPP, mermas, aceites","Peligroso / Mixto","Prospecto","Foco en certificación/cumplimiento."),
 ("Media","Agroindustria","Sociedad Agrícola Drokasa S.A.","Agrokasa","20325117835","Ica","Envases de agroquímicos, plásticos, EPP, mermas, aceites","Peligroso / Mixto","Prospecto",""),
 ("Media","Agroindustria","Agrícola Don Ricardo S.A.C.","Don Ricardo","20293718220","San José de los Molinos, Ica","Envases de agroquímicos, plásticos, EPP, mermas, aceites","Peligroso / Mixto","Prospecto",""),
 ("Media","Agroindustria","El Pedregal S.A.","El Pedregal","20336183791","Ica","Envases de agroquímicos, plásticos, EPP, mermas","Peligroso / Mixto","Prospecto","Confirmar sede/planta y RUC en SUNAT."),
 ("Media","Agroindustria","Virú S.A.","Virú","20373860736","Sede La Libertad; campos también en Ica","Envases de químicos, EPP, aceites, mermas, hojalata","Peligroso / Mixto","Prospecto","Sede matriz fuera de Ica; validar planta."),
 ("Media","Agroindustria","Machu Picchu Foods S.A.C.","Machu Picchu Foods","Por verificar en SUNAT","Ica / Chincha","Envases de insumos, aceites, mermas, plásticos","Mixto","Prospecto","Verificar razón social y RUC."),
 ("Media","Agroindustria","Corporación Frutícola de Chincha S.A.C.","Corp. Frutícola de Chincha","Por verificar en SUNAT","Chincha / Ica","Envases de agroquímicos, plásticos, EPP, mermas","Peligroso / Mixto","Prospecto","Verificar razón social y RUC."),
 ("Media","Agroindustria","Procesadora Larán S.A.C. / Agrícola Chapi","Larán / Chapi","Por verificar en SUNAT","Ica","Envases de agroquímicos, plásticos, EPP, mermas","Peligroso / Mixto","Prospecto","Confirmar razón social exacta y RUC."),
 ("Alta","Aliado / EO-RS","Century Ecological Corporation S.A.C.","Ecocentury","20502073401","Lima (Chorrillos) — operador de residuos","Operador de recolección, transporte y comercialización (pel. y no pel.)","Operador","Reunión","Definir rol: EO-RS aliado que deriva a SMA o generador."),
 ("Media","Por definir","VIAMERICA (razón social por verificar)","Viamerica","Por verificar en SUNAT","Por verificar","Por caracterizar (generador u operador)","Por definir","Contactado","Verificar razón social, RUC y actividad."),
 ("Media","Por definir","IQJ del Perú (razón social por verificar)","IQJ del Perú","Por verificar en SUNAT","Por verificar","Por caracterizar (posible industrial/química)","Por definir","Contactado","Verificar razón social, RUC y actividad."),
]

def seed_if_empty():
    db = SessionLocal()
    try:
        if db.query(Account).count() > 0:
            return
        for i, r in enumerate(SEED, start=1):
            prioridad, sector, razon, comercial, ruc, planta, residuos, tipo, etapa, notas = r
            db.add(Account(id=i, prioridad=prioridad, sector=sector, razon=razon, comercial=comercial,
                           ruc=ruc, planta=planta, residuos=residuos, tipo=tipo, etapa=etapa,
                           estado="Activo", notas=notas))
        db.commit()
    finally:
        db.close()

def ensure_columns():
    insp = inspect(engine)
    if "accounts" not in insp.get_table_names():
        return
    existing = {c["name"] for c in insp.get_columns("accounts")}
    with engine.begin() as conn:
        for col in Account.__table__.columns:
            if col.name not in existing:
                ddl = "TIMESTAMP" if isinstance(col.type, DateTime) else "VARCHAR"
                conn.execute(text(f'ALTER TABLE accounts ADD COLUMN "{col.name}" {ddl}'))

# ─────────────────────────────  API  ─────────────────────────────
BASE_FIELDS = {"razon","comercial","ruc","sector","planta","residuos","tipo"}
GEST_FIELDS = {"prioridad","ton_np","ton_pel","precio_np","precio_pel","costo_np","costo_pel",
               "tonelaje","operador","vencimiento","contacto","cargo","correo","celular","etapa",
               "ultimo_contacto","proxima_accion","fecha_proxima","responsable","valor","prob","estado","notas"}
EDITABLE = BASE_FIELDS | GEST_FIELDS

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_columns()
    seed_if_empty()
    yield

app = FastAPI(title="Gestión Pisco-Ica", lifespan=lifespan)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/config")
def config():
    return {"auth_required": bool(os.getenv("APP_TOKEN", ""))}

@app.get("/api/accounts", dependencies=[Depends(require_token)])
def list_accounts(db: Session = Depends(get_db)):
    return [r.as_dict() for r in db.query(Account).order_by(Account.id).all()]

@app.post("/api/accounts", dependencies=[Depends(require_token)])
def create_account(payload: dict, db: Session = Depends(get_db)):
    if not (payload.get("razon") or "").strip():
        raise HTTPException(status_code=400, detail="La razón social es obligatoria")
    next_id = (db.query(func.max(Account.id)).scalar() or 0) + 1
    payload.pop("updated_by", "")
    data = {k: ("" if v is None else str(v)) for k, v in payload.items() if k in EDITABLE}
    data.setdefault("prioridad", "Media"); data.setdefault("etapa", "Prospecto"); data.setdefault("estado", "Activo")
    acc = Account(id=next_id, **data)
    db.add(acc); db.commit(); db.refresh(acc)
    return acc.as_dict()

@app.put("/api/accounts/{account_id}", dependencies=[Depends(require_token)])
def update_account(account_id: int, payload: dict, db: Session = Depends(get_db)):
    acc = db.get(Account, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    updated_by = payload.pop("updated_by", "") or ""
    for k, v in payload.items():
        if k in EDITABLE:
            setattr(acc, k, "" if v is None else str(v))
    if updated_by:
        acc.updated_by = updated_by
    db.commit(); db.refresh(acc)
    return acc.as_dict()

@app.delete("/api/accounts/{account_id}", dependencies=[Depends(require_token)])
def delete_account(account_id: int, db: Session = Depends(get_db)):
    acc = db.get(Account, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    db.delete(acc); db.commit()
    return {"deleted": account_id}

# ─────────────────────────────  FRONTEND (HTML + gráficos embebidos)  ─────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tablero de Gestión — Corredor Pisco–Ica</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{color-scheme:light;--navy:#1F3864;--blue:#2E75B6;--grey:#F2F2F2;--ok:#2E7D32;--warn:#C62828;--amber:#B7791F;
--line:#e3e8ef;--bg:#f6f8fb;--card:#fff;--txt:#1a2333;--mut:#6b7788;--money:#0b7285;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font-family:Arial,Helvetica,sans-serif;font-size:13px}
.wrap{padding:16px 18px 40px}
h1{font-size:19px;margin:0 0 2px;color:var(--navy)}
.sub{color:var(--mut);font-size:12px;margin-bottom:12px}
.tabs{display:flex;gap:4px;margin-bottom:14px;border-bottom:2px solid var(--line);flex-wrap:wrap}
.tab{padding:8px 15px;cursor:pointer;font-weight:700;color:var(--mut);border:none;background:none;font-size:13px;border-bottom:3px solid transparent;margin-bottom:-2px}
.tab.active{color:var(--navy);border-bottom-color:var(--blue)}
.kpis{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;min-width:130px}
.kpi .v{font-size:20px;font-weight:700;color:var(--navy)} .kpi .l{font-size:11px;color:var(--mut);margin-top:3px}
.kpi.money .v{color:var(--money)} .kpi.win .v{color:var(--ok)} .kpi.lose .v{color:var(--warn)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:14px}
.card h2{font-size:13px;margin:0 0 12px;color:var(--navy);text-transform:uppercase;letter-spacing:.4px}
.chartgrid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:820px){.chartgrid{grid-template-columns:1fr}}
.chartbox{position:relative;height:290px}
.pipe{display:flex;overflow-x:auto;padding-bottom:4px}
.stage{flex:1 0 118px;padding:10px 12px 10px 24px;background:var(--grey);margin-right:2px;clip-path:polygon(0 0,calc(100% - 14px) 0,100% 50%,calc(100% - 14px) 100%,0 100%,14px 50%)}
.stage:first-child{padding-left:14px;clip-path:polygon(0 0,calc(100% - 14px) 0,100% 50%,calc(100% - 14px) 100%,0 100%)}
.stage .sn{font-size:11px;color:var(--navy);font-weight:700}.stage .sc{font-size:20px;font-weight:700;color:var(--navy)}.stage .sp{font-size:10px;color:var(--mut)}
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:10px}
select,input,textarea{font-family:inherit;font-size:12px;border:1px solid #cdd6e2;border-radius:6px;padding:4px 6px;background:#fff;color:var(--txt)}
.controls select,.controls input{padding:5px 8px}
.btn{background:var(--navy);color:#fff;border:none;border-radius:6px;padding:6px 12px;font-size:12px;cursor:pointer}
.btn.sec{background:#fff;color:var(--navy);border:1px solid var(--navy)} .btn.add{background:var(--ok)}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:0 0 8px 8px}
.topscroll{overflow-x:auto;overflow-y:hidden;border:1px solid var(--line);border-bottom:none;border-radius:8px 8px 0 0;height:15px;background:#fbfcfe}
.topscroll>div{height:1px}
table.grid{border-collapse:collapse;width:max-content;min-width:100%}
table.grid th,table.grid td{border-bottom:1px solid var(--line);border-right:1px solid var(--line);padding:6px 8px;vertical-align:top;text-align:left}
table.grid th{background:var(--navy);color:#fff;font-size:11px;position:sticky;top:0;white-space:nowrap}
th.grp-cost{background:#0b7285} th.grp-calc{background:#155e75}
table.grid tr:nth-child(even) td{background:#fafcff} td.fix{background:#fff}
.razon{font-weight:700;color:var(--navy)} .muted{color:var(--mut);font-size:11px}
.tbl-in{width:100%;border:none;background:transparent;padding:3px 2px;font-size:12px}
.tbl-in:focus{background:#fffbe6;outline:1px solid var(--blue)}
td input.num{width:70px;text-align:right} td input.dt{width:120px}
td.calc{background:#f0fbfc;text-align:right;white-space:nowrap;font-weight:700;color:var(--money)}
td.calc .pct{display:block;font-weight:400;color:var(--mut);font-size:10px}
.del{color:var(--warn);cursor:pointer;border:none;background:none;font-size:15px;padding:0 4px}
.foot{color:var(--mut);font-size:11px}
.hidden{display:none}
.ptable{width:100%;border-collapse:collapse}
.ptable th,.ptable td{padding:7px 10px;border-bottom:1px solid var(--line);font-size:12px;text-align:right}
.ptable th{background:#eef3f9;color:var(--navy);text-align:right} .ptable td.l,.ptable th.l{text-align:left}
.barwrap{background:#eef2f7;border-radius:5px;width:150px;display:inline-block;vertical-align:middle}
.bar{height:10px;border-radius:5px;background:var(--blue);min-width:2px;display:block}
.modal{position:fixed;inset:0;background:rgba(20,30,50,.5);display:none;align-items:center;justify-content:center;z-index:60}
.modal .box{background:#fff;border-radius:12px;padding:20px 22px;width:520px;max-width:94vw;max-height:90vh;overflow:auto;box-shadow:0 10px 40px rgba(0,0,0,.25)}
.modal h3{margin:0 0 12px;color:var(--navy)} .frow{display:flex;gap:10px;margin-bottom:10px}
.frow label{flex:1;font-size:12px;color:var(--mut)} .frow label input,.frow label select{width:100%;margin-top:3px;padding:6px}
.status{font-size:11px;padding:2px 8px;border-radius:10px}
.status.ok{background:#e2efda;color:var(--ok)} .status.err{background:#fde7e7;color:var(--warn)} .status.sav{background:#e7f0fb;color:var(--blue)}
#gate{position:fixed;inset:0;background:rgba(20,30,50,.55);display:none;align-items:center;justify-content:center;z-index:70}
#gate .box{background:#fff;border-radius:12px;padding:22px 24px;width:340px} #gate input{width:100%;margin-bottom:10px;padding:8px}
</style>
</head>
<body>
<div id="gate"><div class="box">
  <h3>Acceso al tablero</h3>
  <p style="color:var(--mut);font-size:12px">Ingresa el token compartido del equipo (APP_TOKEN en Render).</p>
  <input type="password" id="tokenInput" placeholder="Token de acceso">
  <button class="btn" id="tokenBtn" style="width:100%">Entrar</button>
  <div id="gateErr" style="color:var(--warn);font-size:12px;margin-top:8px"></div>
</div></div>

<div class="modal" id="modal"><div class="box">
  <h3>Nueva cuenta</h3>
  <div class="frow"><label>Razón social *<input id="m_razon"></label><label>Nombre comercial<input id="m_comercial"></label></div>
  <div class="frow"><label>RUC<input id="m_ruc"></label><label>Sector<input id="m_sector" placeholder="Ej: Pesca, Agroindustria…"></label></div>
  <div class="frow"><label>Planta / ubicación<input id="m_planta"></label></div>
  <div class="frow"><label>Residuos principales<input id="m_residuos"></label></div>
  <div class="frow">
    <label>Tipo<select id="m_tipo"><option>Peligroso</option><option>No peligroso</option><option>Mixto</option><option>Operador</option><option>Por definir</option></select></label>
    <label>Prioridad<select id="m_prioridad"><option>Media</option><option>Alta</option><option>Baja</option></select></label>
    <label>Etapa<select id="m_etapa"></select></label>
  </div>
  <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:6px">
    <button class="btn sec" id="m_cancel">Cancelar</button><button class="btn add" id="m_save">Crear cuenta</button>
  </div>
  <div id="m_err" style="color:var(--warn);font-size:12px;margin-top:8px"></div>
</div></div>

<div class="wrap">
  <h1>Tablero de Gestión — Generadores Corredor Pisco–Ica</h1>
  <div class="sub">Plataforma técnico-comercial-financiera. Datos compartidos en vivo (PostgreSQL). <span id="conn" class="status"></span></div>

  <div class="tabs">
    <button class="tab active" data-v="resumen">Resumen</button>
    <button class="tab" data-v="gestion">Gestión y costeo</button>
    <button class="tab" data-v="potencial">Potencial</button>
    <button class="tab" data-v="financiero">Financiero</button>
  </div>

  <div id="v_resumen">
    <div class="kpis" id="rkpis"></div>
    <div class="card">
      <h2>Pipeline lineal por etapa</h2>
      <div class="pipe" id="pipe"></div>
    </div>
    <div class="chartgrid">
      <div class="card"><h2>Valor del pipeline por etapa (S/ mes)</h2><div class="chartbox"><canvas id="chStageVal"></canvas></div></div>
      <div class="card"><h2>Cuentas por etapa</h2><div class="chartbox"><canvas id="chStageCnt"></canvas></div></div>
      <div class="card"><h2>Ingreso potencial por sector (S/ mes)</h2><div class="chartbox"><canvas id="chSector"></canvas></div></div>
      <div class="card"><h2>Conversión por ingreso</h2><div class="chartbox"><canvas id="chConv"></canvas></div></div>
    </div>
  </div>

  <div id="v_gestion" class="hidden">
    <div class="kpis" id="kpis"></div>
    <div class="card">
      <h2>Gestión y costeo (una línea por cuenta)</h2>
      <div class="controls">
        <button class="btn add" id="addBtn">＋ Nueva cuenta</button>
        <input type="text" id="q" placeholder="Buscar cuenta, RUC, planta…" style="min-width:200px">
        <select id="fSector"></select><select id="fPrio"></select><select id="fEtapa"></select>
        <button class="btn sec" id="clear">Limpiar</button>
        <button class="btn" id="csv">Exportar CSV</button>
        <button class="btn sec" id="reload">Recargar</button>
        <input type="text" id="who" placeholder="Tu nombre (auditoría)" style="min-width:150px">
        <span class="foot" id="stamp"></span>
      </div>
      <div class="topscroll" id="topscroll"><div></div></div>
      <div class="tablewrap" id="tblwrap"><table class="grid" id="tbl"></table></div>
    </div>
  </div>

  <div id="v_potencial" class="hidden">
    <div class="kpis" id="pkpis"></div>
    <div class="chartgrid">
      <div class="card"><h2>Embudo de valor (ingreso/mes por etapa)</h2><div class="chartbox"><canvas id="chFunnel"></canvas></div></div>
      <div class="card"><h2>Ponderado por probabilidad (S/ mes)</h2><div class="chartbox"><canvas id="chPond"></canvas></div></div>
    </div>
    <div class="card"><h2>Potencial por etapa</h2><table class="ptable" id="petapa"></table></div>
    <div class="card"><h2>Potencial por sector</h2><table class="ptable" id="psector"></table></div>
    <div class="card"><h2>Resumen de conversión</h2><table class="ptable" id="pconv"></table></div>
  </div>

  <div id="v_financiero" class="hidden">
    <div class="kpis" id="fkpis"></div>
    <div class="chartgrid">
      <div class="card"><h2>Ingreso vs Margen por sector (S/ mes)</h2><div class="chartbox"><canvas id="chSecFin"></canvas></div></div>
      <div class="card"><h2>Mezcla de tonelaje (No peligroso vs Peligroso)</h2><div class="chartbox"><canvas id="chMix"></canvas></div></div>
    </div>
    <div class="card"><h2>Estado de resultados estimado (mensual)</h2><table class="ptable" id="pnl"></table></div>
    <div class="card"><h2>Detalle financiero por sector</h2><table class="ptable" id="fsector"></table></div>
    <div class="card"><h2>Resumen técnico (tonelaje/mes)</h2><table class="ptable" id="ftec"></table></div>
  </div>
</div>

<script>
const STAGES=["Prospecto","Contactado","Reunión","Visita técnica","Propuesta","Negociación","Homologación","Cerrado - ganado","Cerrado - perdido"];
const OPEN_STAGES=["Prospecto","Contactado","Reunión","Visita técnica","Propuesta","Negociación","Homologación"];
const COST_FIELDS=["ton_np","ton_pel","precio_np","precio_pel","costo_np","costo_pel"];
const RECALC=new Set([...COST_FIELDS,"prob","prioridad","etapa","estado","sector"]);
const PALETTE=["#1F3864","#2E75B6","#0b7285","#5B9BD5","#B7791F","#2E7D32","#8E44AD","#C0392B","#16A085","#7F8C8D"];
let TOKEN=localStorage.getItem("app_token")||"", AUTH_REQUIRED=true, state=[], view="resumen";
const charts={};
function headers(){const h={"Content-Type":"application/json"};if(TOKEN)h["X-App-Token"]=TOKEN;return h;}
function setConn(t,cls){const e=document.getElementById('conn');e.textContent=t;e.className="status "+cls;}
const nn=x=>parseFloat(x)||0;
function money(x){return x?('S/ '+Math.round(x).toLocaleString('es-PE')):'—';}
function moneyAx(v){return 'S/ '+Number(v).toLocaleString('es-PE');}
function compute(r){const ing=nn(r.ton_np)*nn(r.precio_np)+nn(r.ton_pel)*nn(r.precio_pel);const cost=nn(r.ton_np)*nn(r.costo_np)+nn(r.ton_pel)*nn(r.costo_pel);const mar=ing-cost;return{ing,cost,mar,marp:ing>0?mar/ing:0};}
function chart(id,cfg){if(charts[id])charts[id].destroy();const el=document.getElementById(id);if(!el)return;charts[id]=new Chart(el,cfg);}
async function api(path,opts={}){
  const r=await fetch(path,Object.assign({headers:headers()},opts));
  if(r.status===401)throw{code:401};
  if(!r.ok){let m="HTTP "+r.status;try{m=(await r.json()).detail||m;}catch(e){}throw new Error(m);}
  return r.status===204?null:r.json();
}
async function boot(){
  try{AUTH_REQUIRED=(await fetch("/api/config").then(r=>r.json())).auth_required;}catch(e){}
  if(AUTH_REQUIRED && !TOKEN){showGate();return;}
  await loadData();
}
function showGate(msg){document.getElementById('gate').style.display='flex';if(msg)document.getElementById('gateErr').textContent=msg;}
document.getElementById('tokenBtn').onclick=async()=>{
  TOKEN=document.getElementById('tokenInput').value.trim();
  try{await api("/api/accounts");localStorage.setItem("app_token",TOKEN);document.getElementById('gate').style.display='none';await loadData();}
  catch(e){document.getElementById('gateErr').textContent="Token inválido, intenta de nuevo.";}
};
async function loadData(){
  try{state=await api("/api/accounts");setConn("Conectado","ok");initFilters();renderAll();}
  catch(e){if(e.code===401){TOKEN="";localStorage.removeItem("app_token");showGate("Sesión expirada, ingresa el token.");}else setConn("Sin conexión","err");}
}
function uniq(a){return[...new Set(a)].filter(Boolean);}
function fillSelect(el,label,vals){el.innerHTML="<option value=''>"+label+"</option>"+vals.map(v=>`<option>${v}</option>`).join("");}
function initFilters(){
  fillSelect(document.getElementById('fSector'),"Todos los sectores",uniq(state.map(r=>r.sector)));
  fillSelect(document.getElementById('fPrio'),"Toda prioridad",["Alta","Media","Baja"]);
  fillSelect(document.getElementById('fEtapa'),"Toda etapa",STAGES);
  fillSelect(document.getElementById('m_etapa'),"",STAGES);document.getElementById('m_etapa').value="Prospecto";
}
function sumArr(arr){let ing=0,cost=0,mar=0,pond=0,tnp=0,tpel=0;arr.forEach(r=>{const c=compute(r);ing+=c.ing;cost+=c.cost;mar+=c.mar;pond+=c.ing*nn(r.prob)/100;tnp+=nn(r.ton_np);tpel+=nn(r.ton_pel);});return{ing,cost,mar,pond,tnp,tpel,n:arr.length};}
function byStage(){return STAGES.map(s=>({s,...sumArr(state.filter(r=>r.etapa===s))}));}
function bySector(){return uniq(state.map(r=>r.sector)).map(s=>({s,...sumArr(state.filter(r=>r.sector===s))})).sort((a,b)=>b.ing-a.ing);}
function filters(){return{q:document.getElementById('q').value.toLowerCase(),sector:document.getElementById('fSector').value,prio:document.getElementById('fPrio').value,etapa:document.getElementById('fEtapa').value};}
function filtered(){const f=filters();return state.filter(r=>{
  if(f.sector&&r.sector!==f.sector)return false;if(f.prio&&r.prioridad!==f.prio)return false;if(f.etapa&&r.etapa!==f.etapa)return false;
  if(f.q){const b=(r.razon+" "+r.comercial+" "+r.ruc+" "+r.planta+" "+r.residuos).toLowerCase();if(!b.includes(f.q))return false;}return true;});}
function renderKpis(){
  const total=state.length,alta=state.filter(r=>r.prioridad==="Alta").length,activas=state.filter(r=>r.estado==="Activo").length;
  const t=sumArr(state);const marp=t.ing>0?Math.round(t.mar/t.ing*100):0;
  const k=[["Cuentas totales",total,""],["Prioridad Alta",alta,""],["Activas",activas,""],
    ["Ingreso mensual",money(t.ing),"money"],["Ingreso anual",money(t.ing*12),"money"],
    ["Margen mensual",money(t.mar)+" ("+marp+"%)","money"],["Ponderado x prob.",money(t.pond),"money"]];
  document.getElementById('kpis').innerHTML=k.map(x=>`<div class="kpi ${x[2]}"><div class="v">${x[1]}</div><div class="l">${x[0]}</div></div>`).join("");
}
function renderPipe(){
  const tot=state.length||1;
  document.getElementById('pipe').innerHTML=STAGES.map(s=>{const c=state.filter(r=>r.etapa===s).length;const pct=Math.round(c/tot*100);
    const bg=s.startsWith("Cerrado - g")?"#e2efda":s.startsWith("Cerrado - p")?"#fde7e7":"";
    return `<div class="stage" style="${bg?'background:'+bg:''}"><div class="sn">${s}</div><div class="sc">${c}</div><div class="sp">${pct}%</div></div>`;}).join("");
}
function inp(r,f,cls,type){type=type||"text";const v=r[f]??"";return `<input class="tbl-in ${cls||''}" data-id="${r.id}" data-f="${f}" type="${type}" value="${String(v).replace(/"/g,'&quot;')}">`;}
function sel(r,f,opts){return `<select class="tbl-in" data-id="${r.id}" data-f="${f}">`+opts.map(o=>`<option ${r[f]===o?'selected':''}>${o}</option>`).join("")+`</select>`;}
function calcCell(r){const c=compute(r);return `<span id="ing-${r.id}">${money(c.ing)}</span>`;}
function marCell(r){const c=compute(r);return `<span id="mar-${r.id}">${money(c.mar)}</span><span class="pct" id="marp-${r.id}">${c.ing>0?Math.round(c.marp*100)+'%':''}</span>`;}
const COLS=[
 ["",r=>`<button class="del" data-del="${r.id}" title="Eliminar">🗑</button>`,"fix"],
 ["N°",r=>`<span class="muted">${r.id}</span>`,"fix"],["Prioridad",r=>sel(r,"prioridad",["Alta","Media","Baja"]),""],
 ["Sector",r=>inp(r,"sector"),""],["Razón social",r=>`<div class="razon">${r.razon||''}</div>`+inp(r,"comercial"),"fix"],
 ["RUC",r=>inp(r,"ruc"),""],["Planta / ubicación",r=>inp(r,"planta"),""],["Tipo",r=>`<span class="muted">${r.tipo||''}</span>`,"fix"],
 ["Ton NP (t/mes)",r=>inp(r,"ton_np","num","number"),"cost"],["Ton Pel (t/mes)",r=>inp(r,"ton_pel","num","number"),"cost"],
 ["Precio NP (S/t)",r=>inp(r,"precio_np","num","number"),"cost"],["Precio Pel (S/t)",r=>inp(r,"precio_pel","num","number"),"cost"],
 ["Costo NP (S/t)",r=>inp(r,"costo_np","num","number"),"cost"],["Costo Pel (S/t)",r=>inp(r,"costo_pel","num","number"),"cost"],
 ["Ingreso/mes",calcCell,"calc"],["Margen/mes",marCell,"calc"],
 ["Operador actual",r=>inp(r,"operador"),""],["Venc. contrato",r=>inp(r,"vencimiento","dt","date"),""],
 ["Contacto operac.",r=>inp(r,"contacto"),""],["Cargo",r=>inp(r,"cargo"),""],["Correo",r=>inp(r,"correo"),""],["Celular",r=>inp(r,"celular"),""],
 ["Etapa",r=>sel(r,"etapa",STAGES),""],["Últ. contacto",r=>inp(r,"ultimo_contacto","dt","date"),""],
 ["Próxima acción",r=>inp(r,"proxima_accion"),""],["Fecha próx.",r=>inp(r,"fecha_proxima","dt","date"),""],
 ["Responsable",r=>inp(r,"responsable"),""],["Prob. %",r=>inp(r,"prob","num","number"),""],
 ["Estado",r=>sel(r,"estado",["Activo","En pausa","Descartado"]),""],["Notas",r=>inp(r,"notas"),""],
];
function thClass(c){return c[2]==="cost"?"grp-cost":c[2]==="calc"?"grp-calc":"";}
function renderTable(){
  const rows=filtered();
  document.getElementById('tbl').innerHTML="<tr>"+COLS.map(c=>`<th class="${thClass(c)}">${c[0]}</th>`).join("")+"</tr>"+
    rows.map(r=>"<tr>"+COLS.map(c=>`<td class="${c[2]==='fix'?'fix':c[2]==='calc'?'calc':''}">${c[1](r)}</td>`).join("")+"</tr>").join("");
  document.querySelectorAll('#tbl .tbl-in').forEach(el=>el.addEventListener('change',e=>save(+e.target.dataset.id,e.target.dataset.f,e.target.value)));
  document.querySelectorAll('#tbl .del').forEach(el=>el.addEventListener('click',e=>delAccount(+e.target.dataset.del)));
  syncTopScroll();
}
function syncTopScroll(){
  const tbl=document.getElementById('tbl'),ts=document.getElementById('topscroll');
  if(tbl&&ts&&ts.firstElementChild)ts.firstElementChild.style.width=tbl.scrollWidth+'px';
}
(function(){
  const ts=document.getElementById('topscroll'),tw=document.getElementById('tblwrap');
  if(ts&&tw){
    let lock=false;
    ts.addEventListener('scroll',()=>{if(lock)return;lock=true;tw.scrollLeft=ts.scrollLeft;lock=false;});
    tw.addEventListener('scroll',()=>{if(lock)return;lock=true;ts.scrollLeft=tw.scrollLeft;lock=false;});
    window.addEventListener('resize',syncTopScroll);
  }
})();
function updateComputed(r){const c=compute(r);
  const a=document.getElementById('ing-'+r.id);if(a)a.textContent=money(c.ing);
  const b=document.getElementById('mar-'+r.id);if(b)b.textContent=money(c.mar);
  const d=document.getElementById('marp-'+r.id);if(d)d.textContent=c.ing>0?Math.round(c.marp*100)+'%':'';}
async function save(id,field,value){
  const row=state.find(x=>x.id===id);row[field]=value;
  if(RECALC.has(field)){updateComputed(row);renderKpis();renderPipe();renderAnalytics();}
  setConn("Guardando…","sav");
  const who=document.getElementById('who').value.trim();
  try{const upd=await api("/api/accounts/"+id,{method:"PUT",body:JSON.stringify({[field]:value,updated_by:who})});
    Object.assign(row,upd);setConn("Guardado","ok");
    document.getElementById('stamp').textContent="Última edición: "+new Date().toLocaleString('es-PE')+(who?(" · "+who):"");}
  catch(e){setConn("Error al guardar","err");}
}
async function delAccount(id){
  const row=state.find(x=>x.id===id);
  if(!confirm("¿Eliminar la cuenta "+(row?row.razon:id)+"? No se puede deshacer."))return;
  try{await api("/api/accounts/"+id,{method:"DELETE"});state=state.filter(x=>x.id!==id);initFilters();renderAll();setConn("Cuenta eliminada","ok");}
  catch(e){setConn("Error al eliminar","err");}
}
document.getElementById('addBtn').onclick=()=>{document.getElementById('modal').style.display='flex';document.getElementById('m_err').textContent='';};
document.getElementById('m_cancel').onclick=()=>{document.getElementById('modal').style.display='none';['m_razon','m_comercial','m_ruc','m_sector','m_planta','m_residuos'].forEach(i=>document.getElementById(i).value='');};
document.getElementById('m_save').onclick=async()=>{
  const razon=document.getElementById('m_razon').value.trim();
  if(!razon){document.getElementById('m_err').textContent="La razón social es obligatoria.";return;}
  const body={razon,comercial:document.getElementById('m_comercial').value.trim(),ruc:document.getElementById('m_ruc').value.trim(),
    sector:document.getElementById('m_sector').value.trim(),planta:document.getElementById('m_planta').value.trim(),
    residuos:document.getElementById('m_residuos').value.trim(),tipo:document.getElementById('m_tipo').value,
    prioridad:document.getElementById('m_prioridad').value,etapa:document.getElementById('m_etapa').value,
    updated_by:document.getElementById('who').value.trim()};
  try{const acc=await api("/api/accounts",{method:"POST",body:JSON.stringify(body)});
    state.push(acc);document.getElementById('m_cancel').click();initFilters();renderAll();setConn("Cuenta creada","ok");}
  catch(e){document.getElementById('m_err').textContent="No se pudo crear: "+e.message;}
};
function renderResumen(){
  const total=state.length,alta=state.filter(r=>r.prioridad==="Alta").length;
  const t=sumArr(state), proc=sumArr(state.filter(r=>r.estado==="Activo"&&OPEN_STAGES.includes(r.etapa)));
  const won=sumArr(state.filter(r=>r.etapa==="Cerrado - ganado"));
  const k=[["Cuentas",total,""],["Prioridad Alta",alta,""],["Ingreso mensual",money(t.ing),"money"],
    ["Ingreso anual",money(t.ing*12),"money"],["En proceso (mes)",money(proc.ing),"money"],
    ["Ponderado x prob.",money(proc.pond),"money"],["Ganado (mes)",money(won.ing),"win"]];
  document.getElementById('rkpis').innerHTML=k.map(x=>`<div class="kpi ${x[2]}"><div class="v">${x[1]}</div><div class="l">${x[0]}</div></div>`).join("");
  const bs=byStage();
  chart('chStageVal',{type:'bar',data:{labels:STAGES,datasets:[{label:'Ingreso/mes',data:bs.map(r=>Math.round(r.ing)),
    backgroundColor:STAGES.map(s=>s.startsWith('Cerrado - g')?'#2E7D32':s.startsWith('Cerrado - p')?'#C0392B':'#2E75B6')}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>moneyAx(c.raw)}}},scales:{x:{ticks:{font:{size:9},maxRotation:60,minRotation:40}},y:{ticks:{callback:moneyAx,font:{size:9}}}}}});
  chart('chStageCnt',{type:'bar',data:{labels:STAGES,datasets:[{label:'Cuentas',data:bs.map(r=>r.n),backgroundColor:'#1F3864'}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{font:{size:9},maxRotation:60,minRotation:40}},y:{ticks:{precision:0,font:{size:9}},beginAtZero:true}}}});
  const secs=bySector();
  chart('chSector',{type:'doughnut',data:{labels:secs.map(s=>s.s||'(sin sector)'),datasets:[{data:secs.map(s=>Math.round(s.ing)),backgroundColor:PALETTE}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{font:{size:10}}},tooltip:{callbacks:{label:c=>c.label+': '+moneyAx(c.raw)}}}}});
  const lost=sumArr(state.filter(r=>r.etapa==="Cerrado - perdido"));
  chart('chConv',{type:'doughnut',data:{labels:['En proceso','Ganado','Perdido'],datasets:[{data:[Math.round(proc.ing),Math.round(won.ing),Math.round(lost.ing)],backgroundColor:['#2E75B6','#2E7D32','#C0392B']}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{font:{size:10}}},tooltip:{callbacks:{label:c=>c.label+': '+moneyAx(c.raw)}}}}});
}
function renderPotencial(){
  const proc=sumArr(state.filter(r=>r.estado==="Activo"&&OPEN_STAGES.includes(r.etapa)));
  const won=sumArr(state.filter(r=>r.etapa==="Cerrado - ganado")), lost=sumArr(state.filter(r=>r.etapa==="Cerrado - perdido"));
  const act=sumArr(state.filter(r=>r.estado==="Activo"));
  const k=[["Potencial activo (mes)",money(act.ing),"money"],["Potencial activo (año)",money(act.ing*12),"money"],
    ["En proceso (mes)",money(proc.ing),"money"],["Ponderado en proceso",money(proc.pond),"money"],
    ["Ganado (mes)",money(won.ing),"win"],["Perdido (mes)",money(lost.ing),"lose"]];
  document.getElementById('pkpis').innerHTML=k.map(x=>`<div class="kpi ${x[2]}"><div class="v">${x[1]}</div><div class="l">${x[0]}</div></div>`).join("");
  const bs=byStage();
  chart('chFunnel',{type:'bar',data:{labels:STAGES,datasets:[{label:'Ingreso/mes',data:bs.map(r=>Math.round(r.ing)),backgroundColor:'#0b7285'}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>moneyAx(c.raw)}}},scales:{x:{ticks:{callback:moneyAx,font:{size:9}}},y:{ticks:{font:{size:9}}}}}});
  chart('chPond',{type:'bar',data:{labels:STAGES,datasets:[{label:'Ponderado',data:bs.map(r=>Math.round(r.pond)),backgroundColor:'#B7791F'}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>moneyAx(c.raw)}}},scales:{x:{ticks:{callback:moneyAx,font:{size:9}}},y:{ticks:{font:{size:9}}}}}});
  const maxIng=Math.max(1,...bs.map(r=>r.ing));
  document.getElementById('petapa').innerHTML="<tr><th class='l'>Etapa</th><th>Cuentas</th><th>Ingreso/mes</th><th>Ingreso/año</th><th>Ponderado</th><th class='l'>Peso</th></tr>"+
    bs.map(r=>`<tr><td class='l'>${r.s}</td><td>${r.n}</td><td>${money(r.ing)}</td><td>${money(r.ing*12)}</td><td>${money(r.pond)}</td><td class='l'><span class='barwrap'><span class='bar' style='width:${Math.round(r.ing/maxIng*150)}px;${r.s.startsWith('Cerrado - g')?'background:var(--ok)':r.s.startsWith('Cerrado - p')?'background:var(--warn)':''}'></span></span></td></tr>`).join("");
  const secs=bySector();
  document.getElementById('psector').innerHTML="<tr><th class='l'>Sector</th><th>Cuentas</th><th>Ingreso/mes</th><th>Ingreso/año</th><th>Ponderado</th></tr>"+
    secs.map(r=>`<tr><td class='l'>${r.s||'(sin sector)'}</td><td>${r.n}</td><td>${money(r.ing)}</td><td>${money(r.ing*12)}</td><td>${money(r.pond)}</td></tr>`).join("");
  const conv=[["En proceso (activas)",proc],["Ganado",won],["Perdido",lost]];
  document.getElementById('pconv').innerHTML="<tr><th class='l'>Estado</th><th>Cuentas</th><th>Ingreso/mes</th><th>Ingreso/año</th></tr>"+
    conv.map(c=>`<tr><td class='l'>${c[0]}</td><td>${c[1].n}</td><td>${money(c[1].ing)}</td><td>${money(c[1].ing*12)}</td></tr>`).join("");
}
function renderFinanciero(){
  const t=sumArr(state);const marp=t.ing>0?Math.round(t.mar/t.ing*100):0;
  const k=[["Ingreso mensual",money(t.ing),"money"],["Costo mensual",money(t.cost),"money"],
    ["Margen bruto (mes)",money(t.mar)+" ("+marp+"%)","money"],["Ingreso anual",money(t.ing*12),"money"],
    ["Margen anual",money(t.mar*12),"money"],["Ponderado x prob.",money(t.pond),"money"]];
  document.getElementById('fkpis').innerHTML=k.map(x=>`<div class="kpi ${x[2]}"><div class="v">${x[1]}</div><div class="l">${x[0]}</div></div>`).join("");
  const secs=bySector();
  chart('chSecFin',{type:'bar',data:{labels:secs.map(s=>s.s||'(sin)'),datasets:[
    {label:'Ingreso/mes',data:secs.map(s=>Math.round(s.ing)),backgroundColor:'#2E75B6'},
    {label:'Margen/mes',data:secs.map(s=>Math.round(s.mar)),backgroundColor:'#2E7D32'}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{font:{size:10}}},tooltip:{callbacks:{label:c=>c.dataset.label+': '+moneyAx(c.raw)}}},scales:{x:{ticks:{font:{size:9},maxRotation:60,minRotation:30}},y:{ticks:{callback:moneyAx,font:{size:9}}}}}});
  const tnp=t.tnp,tpel=t.tpel;
  chart('chMix',{type:'doughnut',data:{labels:['No peligroso','Peligroso'],datasets:[{data:[Math.round(tnp),Math.round(tpel)],backgroundColor:['#5B9BD5','#C0392B']}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{font:{size:10}}},tooltip:{callbacks:{label:c=>c.label+': '+Number(c.raw).toLocaleString('es-PE')+' t/mes'}}}}});
  document.getElementById('pnl').innerHTML=
    "<tr><th class='l'>Concepto</th><th>Mensual</th><th>Anual</th></tr>"+
    `<tr><td class='l'>Ingresos por disposición</td><td>${money(t.ing)}</td><td>${money(t.ing*12)}</td></tr>`+
    `<tr><td class='l'>(-) Costos directos</td><td>${money(t.cost)}</td><td>${money(t.cost*12)}</td></tr>`+
    `<tr><td class='l'><b>Margen bruto</b></td><td><b>${money(t.mar)}</b></td><td><b>${money(t.mar*12)}</b></td></tr>`+
    `<tr><td class='l'>Margen %</td><td>${marp}%</td><td>${marp}%</td></tr>`+
    `<tr><td class='l'>Ingreso ponderado x prob.</td><td>${money(t.pond)}</td><td>${money(t.pond*12)}</td></tr>`;
  document.getElementById('fsector').innerHTML="<tr><th class='l'>Sector</th><th>Cuentas</th><th>Ingreso/mes</th><th>Costo/mes</th><th>Margen/mes</th><th>Margen %</th></tr>"+
    secs.map(r=>{const mp=r.ing>0?Math.round(r.mar/r.ing*100):0;return `<tr><td class='l'>${r.s||'(sin sector)'}</td><td>${r.n}</td><td>${money(r.ing)}</td><td>${money(r.cost)}</td><td>${money(r.mar)}</td><td>${mp}%</td></tr>`;}).join("");
  const ingNP=state.reduce((a,r)=>a+nn(r.ton_np)*nn(r.precio_np),0), ingPel=state.reduce((a,r)=>a+nn(r.ton_pel)*nn(r.precio_pel),0);
  document.getElementById('ftec').innerHTML="<tr><th class='l'>Flujo</th><th>Toneladas/mes</th><th>Ingreso/mes</th><th>Ingreso/año</th></tr>"+
    `<tr><td class='l'>No peligroso</td><td>${tnp.toLocaleString('es-PE')}</td><td>${money(ingNP)}</td><td>${money(ingNP*12)}</td></tr>`+
    `<tr><td class='l'>Peligroso</td><td>${tpel.toLocaleString('es-PE')}</td><td>${money(ingPel)}</td><td>${money(ingPel*12)}</td></tr>`+
    `<tr><td class='l'><b>Total</b></td><td><b>${(tnp+tpel).toLocaleString('es-PE')}</b></td><td><b>${money(ingNP+ingPel)}</b></td><td><b>${money((ingNP+ingPel)*12)}</b></td></tr>`;
}
function renderAnalytics(){ if(view==='resumen')renderResumen(); else if(view==='potencial')renderPotencial(); else if(view==='financiero')renderFinanciero(); }
function renderAll(){renderKpis();renderPipe();renderTable();renderAnalytics();}
function exportCSV(){
  const heads=["N°","Prioridad","Sector","Razón social","Nombre comercial","RUC","Planta/ubicación","Residuos","Tipo","Ton NP (t/mes)","Ton Pel (t/mes)","Precio NP (S/t)","Precio Pel (S/t)","Costo NP (S/t)","Costo Pel (S/t)","Ingreso/mes (S/)","Margen/mes (S/)","Margen %","Operador actual","Venc. contrato","Contacto operaciones","Cargo","Correo","Celular","Etapa","Fecha último contacto","Próxima acción","Fecha próxima acción","Responsable","Prob %","Estado","Notas"];
  const esc=v=>'"'+String(v??"").replace(/"/g,'""')+'"';
  const rows=state.map(r=>{const c=compute(r);return [r.id,r.prioridad,r.sector,r.razon,r.comercial,r.ruc,r.planta,r.residuos,r.tipo,r.ton_np,r.ton_pel,r.precio_np,r.precio_pel,r.costo_np,r.costo_pel,Math.round(c.ing),Math.round(c.mar),(c.ing>0?Math.round(c.marp*100):0),r.operador,r.vencimiento,r.contacto,r.cargo,r.correo,r.celular,r.etapa,r.ultimo_contacto,r.proxima_accion,r.fecha_proxima,r.responsable,r.prob,r.estado,r.notas].map(esc).join(",");});
  const csv=[heads.map(esc).join(",")].concat(rows).join("\r\n");
  const b=new Blob(["﻿"+csv],{type:"text/csv;charset=utf-8"});const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="gestion_costeo_pisco_ica.csv";a.click();
}
function showView(v){
  view=v;
  ["resumen","gestion","potencial","financiero"].forEach(x=>document.getElementById('v_'+x).classList.toggle('hidden',x!==v));
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t.dataset.v===v));
  renderAnalytics();
}
document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>showView(t.dataset.v));
['q','fSector','fPrio','fEtapa'].forEach(id=>document.getElementById(id).addEventListener('input',renderTable));
document.getElementById('clear').onclick=()=>{['q','fSector','fPrio','fEtapa'].forEach(id=>document.getElementById(id).value='');renderTable();};
document.getElementById('csv').onclick=exportCSV;
document.getElementById('reload').onclick=loadData;
document.getElementById('who').value=localStorage.getItem("who")||"";
document.getElementById('who').addEventListener('change',e=>localStorage.setItem("who",e.target.value));
boot();

</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML
