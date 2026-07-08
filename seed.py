# Datos base verificados en fuentes públicas (validar razón social y RUC en SUNAT).
# Campos de gestión (contacto, tonelaje, etapa, etc.) se completan desde el tablero.
from db import SessionLocal
from models import Account

SEED = [
 ("Alta","Siderurgia","Corporación Aceros Arequipa S.A.","Aceros Arequipa","20370146994",
  "Panamericana Sur Km 241, Paracas – Pisco","Polvo EAF, escoria, refractarios, lodos, aceites, chatarra, EPP","Peligroso / Mixto",
  "Prospecto","Cuenta ancla. Alto tonelaje peligroso."),
 ("Alta","Metalurgia","Minsur S.A.","Funsur","20100136741",
  "Fundición y Refinería de Estaño, Paracas Km 238.5","Escorias, polvos y lodos con metales, refractarios, aceites, EPP","Peligroso / Mixto",
  "Prospecto","Cuenta ancla."),
 ("Alta","Hidrocarburos/Gas","Pluspetrol Camisea S.A.","Pluspetrol","20510889135",
  "Planta de Fraccionamiento Playa Lobería, Pisco","Lodos aceitosos, borras, catalizadores, suelos contaminados, filtros","Peligroso",
  "Prospecto","Verificar entidad operadora (vs. Pluspetrol Perú Corporation 20304177552)."),
 ("Alta","Pesca","Tecnológica de Alimentos S.A.","TASA","20100971772",
  "Km 15 Carretera Pisco–Paracas","Lodos PAMA/PTAR, sanguaza/borras, aceites, envases de reactivos, EPP","Mixto",
  "Prospecto","Volumen recurrente; picos por temporada."),
 ("Alta","Pesca","Pesquera Diamante S.A.","Diamante","20159473148",
  "Km 16.5 Carretera Pisco–Paracas","Lodos, aceites, envases de químicos, mantenimiento, EPP","Mixto",
  "Prospecto",""),
 ("Alta","Pesca","Austral Group S.A.A.","Austral","20338054115",
  "Lotización Santa Elena de Paracas","Lodos, aceites, envases, EPP, congelado y conservas","Mixto",
  "Prospecto","Confirmar RUC (existe homónimo 'Pesquera Austral')."),
 ("Media","Pesca","Pesquera Hayduk S.A.","Hayduk","20136165667",
  "Paracas – Pisco","Lodos PAMA, aceites, envases de reactivos, chatarra, EPP","Mixto",
  "Prospecto",""),
 ("Media","Pesca","Corporación Pesquera Inca S.A.C.","Copeinca (ex CFG Investment)","20512868046",
  "Paracas – Pisco","Lodos, aceites, envases contaminados, EPP","Mixto",
  "Prospecto","Antes CFG Investment S.A.C."),
 ("Media","Pesca","Pesquera Exalmar S.A.A.","Exalmar","20380336384",
  "Litoral Ica / Pisco","Lodos, aceites, envases de químicos, mantenimiento","Mixto",
  "Prospecto",""),
 ("Media","Pesca","Sea Food Trading S.A.","Sea Food Trading","Por verificar en SUNAT",
  "Lotización Santa Elena, Km 16.85 Pisco–Paracas","Residuos de proceso, aceites, envases, EPP","Mixto",
  "Prospecto","Verificar razón social y RUC."),
 ("Media","Agroindustria","Complejo Agroindustrial Beta S.A.","Beta","20297939131",
  "Valle de Ica / Villacurí","Envases de agroquímicos, plásticos de riego, EPP, mermas, aceites","Peligroso / Mixto",
  "Prospecto","Foco en certificación/cumplimiento."),
 ("Media","Agroindustria","Sociedad Agrícola Drokasa S.A.","Agrokasa","20325117835",
  "Ica","Envases de agroquímicos, plásticos, EPP, mermas, aceites","Peligroso / Mixto",
  "Prospecto",""),
 ("Media","Agroindustria","Agrícola Don Ricardo S.A.C.","Don Ricardo","20293718220",
  "San José de los Molinos, Ica","Envases de agroquímicos, plásticos, EPP, mermas, aceites","Peligroso / Mixto",
  "Prospecto",""),
 ("Media","Agroindustria","El Pedregal S.A.","El Pedregal","20336183791",
  "Ica","Envases de agroquímicos, plásticos, EPP, mermas","Peligroso / Mixto",
  "Prospecto","Confirmar sede/planta y RUC en SUNAT."),
 ("Media","Agroindustria","Virú S.A.","Virú","20373860736",
  "Sede La Libertad; campos también en Ica","Envases de químicos, EPP, aceites, mermas, hojalata","Peligroso / Mixto",
  "Prospecto","Sede matriz fuera de Ica; validar planta."),
 ("Media","Agroindustria","Machu Picchu Foods S.A.C.","Machu Picchu Foods","Por verificar en SUNAT",
  "Ica / Chincha","Envases de insumos, aceites, mermas, plásticos","Mixto",
  "Prospecto","Verificar razón social y RUC."),
 ("Media","Agroindustria","Corporación Frutícola de Chincha S.A.C.","Corp. Frutícola de Chincha","Por verificar en SUNAT",
  "Chincha / Ica","Envases de agroquímicos, plásticos, EPP, mermas","Peligroso / Mixto",
  "Prospecto","Verificar razón social y RUC."),
 ("Media","Agroindustria","Procesadora Larán S.A.C. / Agrícola Chapi","Larán / Chapi","Por verificar en SUNAT",
  "Ica","Envases de agroquímicos, plásticos, EPP, mermas","Peligroso / Mixto",
  "Prospecto","Confirmar razón social exacta y RUC."),
 ("Alta","Aliado / EO-RS","Century Ecological Corporation S.A.C.","Ecocentury","20502073401",
  "Lima (Chorrillos) — operador de residuos","Operador de recolección, transporte y comercialización (pel. y no pel.)","Operador",
  "Reunión","Definir rol: EO-RS aliado que deriva a SMA o generador."),
 ("Media","Por definir","VIAMERICA (razón social por verificar)","Viamerica","Por verificar en SUNAT",
  "Por verificar","Por caracterizar (generador u operador)","Por definir",
  "Contactado","Verificar razón social, RUC y actividad."),
 ("Media","Por definir","IQJ del Perú (razón social por verificar)","IQJ del Perú","Por verificar en SUNAT",
  "Por verificar","Por caracterizar (posible industrial/química)","Por definir",
  "Contactado","Verificar razón social, RUC y actividad."),
]

def seed_if_empty():
    db = SessionLocal()
    try:
        if db.query(Account).count() > 0:
            return 0
        for i, row in enumerate(SEED, start=1):
            prioridad, sector, razon, comercial, ruc, planta, residuos, tipo, etapa, notas = row
            db.add(Account(id=i, prioridad=prioridad, sector=sector, razon=razon,
                           comercial=comercial, ruc=ruc, planta=planta, residuos=residuos,
                           tipo=tipo, etapa=etapa, estado="Activo", notas=notas))
        db.commit()
        return len(SEED)
    finally:
        db.close()
