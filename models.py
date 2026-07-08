from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from db import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)          # N°
    # --- datos base (verificados) ---
    prioridad = Column(String, default="Media")
    sector = Column(String, default="")
    razon = Column(String, default="")
    comercial = Column(String, default="")
    ruc = Column(String, default="")
    planta = Column(Text, default="")
    residuos = Column(Text, default="")
    tipo = Column(String, default="")
    # --- gestión (editable) ---
    tonelaje = Column(String, default="")
    operador = Column(String, default="")
    vencimiento = Column(String, default="")
    contacto = Column(String, default="")
    cargo = Column(String, default="")
    correo = Column(String, default="")
    celular = Column(String, default="")
    etapa = Column(String, default="Prospecto")
    ultimo_contacto = Column(String, default="")
    proxima_accion = Column(Text, default="")
    fecha_proxima = Column(String, default="")
    responsable = Column(String, default="")
    valor = Column(String, default="")
    prob = Column(String, default="")
    estado = Column(String, default="Activo")
    notas = Column(Text, default="")
    # --- auditoría ---
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, default="")

    def as_dict(self):
        return {c.name: (getattr(self, c.name).isoformat() if isinstance(getattr(self, c.name), datetime)
                          else getattr(self, c.name)) for c in self.__table__.columns}
