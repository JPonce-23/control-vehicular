from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.persona_model import PersonaAutorizada
from app.schemas.persona_schema import PersonaCreate, PersonaEstadoUpdate, PersonaResponse, PersonaUpdate
from app.services.auth_service import requerir_rol

router = APIRouter(prefix="/personas", tags=["Personas autorizadas"])


def _normalizar_texto(valor):
    if valor is None:
        return None
    valor = valor.strip()
    return valor or None


def _normalizar_datos(datos: dict) -> dict:
    for campo in ("nombre", "apellido_paterno", "apellido_materno", "cargo", "num_licencia", "rfc", "tipo_licencia"):
        if campo in datos:
            datos[campo] = _normalizar_texto(datos[campo])
    if datos.get("rfc"):
        datos["rfc"] = datos["rfc"].upper()
    return datos


def _validar_unicos(db: Session, datos: dict, persona_id: int | None = None) -> None:
    for campo, mensaje in (
        ("num_licencia", "Ya existe una persona con ese número de licencia"),
        ("rfc", "Ya existe una persona con ese RFC"),
    ):
        valor = datos.get(campo)
        if not valor:
            continue
        query = db.query(PersonaAutorizada).filter(getattr(PersonaAutorizada, campo) == valor)
        if persona_id is not None:
            query = query.filter(PersonaAutorizada.id != persona_id)
        if query.first():
            raise HTTPException(status_code=409, detail=mensaje)


@router.get("/", response_model=list[PersonaResponse])
def listar_personas(
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador", "capturista"])),
):
    return db.query(PersonaAutorizada).order_by(PersonaAutorizada.id).all()


@router.post("/", response_model=PersonaResponse, status_code=201)
def crear_persona(
    persona: PersonaCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    datos = _normalizar_datos(persona.model_dump())
    datos["estado"] = "activo"
    if not datos.get("nombre") or not datos.get("apellido_paterno") or not datos.get("cargo"):
        raise HTTPException(status_code=400, detail="Nombre, apellido paterno y cargo son obligatorios")
    _validar_unicos(db, datos)

    # Evita duplicados por reenvío accidental del mismo formulario, incluso si no hay RFC/licencia.
    duplicada = db.query(PersonaAutorizada).filter(
        func.lower(PersonaAutorizada.nombre) == datos["nombre"].lower(),
        func.lower(PersonaAutorizada.apellido_paterno) == datos["apellido_paterno"].lower(),
        func.lower(func.coalesce(PersonaAutorizada.apellido_materno, "")) == (datos.get("apellido_materno") or "").lower(),
        func.lower(PersonaAutorizada.cargo) == datos["cargo"].lower(),
    ).first()
    if duplicada:
        raise HTTPException(status_code=409, detail="Esta persona ya se encuentra registrada")

    nueva_persona = PersonaAutorizada(**datos)
    db.add(nueva_persona)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible registrar la persona porque existe un dato duplicado")
    db.refresh(nueva_persona)
    return nueva_persona


@router.put("/{persona_id}", response_model=PersonaResponse)
def actualizar_persona(
    persona_id: int,
    datos: PersonaUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    persona = db.query(PersonaAutorizada).filter(PersonaAutorizada.id == persona_id).first()
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona autorizada no encontrada")

    actualizados = _normalizar_datos(datos.model_dump())
    _validar_unicos(db, actualizados, persona_id)
    for campo, valor in actualizados.items():
        setattr(persona, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible actualizar la persona por un dato duplicado")
    db.refresh(persona)
    return persona


@router.put("/{persona_id}/estado")
def actualizar_estado_persona(
    persona_id: int,
    datos: PersonaEstadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    if datos.estado not in {"activo", "suspendido"}:
        raise HTTPException(status_code=400, detail="Estado de persona no válido")
    persona = db.query(PersonaAutorizada).filter(PersonaAutorizada.id == persona_id).first()
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona autorizada no encontrada")
    persona.estado = datos.estado
    db.commit()
    return {"mensaje": "Estado actualizado correctamente", "persona_id": persona.id, "estado": persona.estado}


@router.get("/{persona_id}", response_model=PersonaResponse)
def obtener_persona_por_id(
    persona_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador", "capturista"])),
):
    persona = db.query(PersonaAutorizada).filter(PersonaAutorizada.id == persona_id).first()
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona autorizada no encontrada")
    return persona
