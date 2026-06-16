from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.persona_model import PersonaAutorizada
from app.schemas.persona_schema import (
    PersonaResponse,
    PersonaCreate,
    PersonaUpdate,
    PersonaEstadoUpdate
)
from app.services.auth_service import requerir_rol

router = APIRouter(
    prefix="/personas",
    tags=["Personas autorizadas"]
)


@router.get("/", response_model=list[PersonaResponse])
def listar_personas(
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador", "capturista"]))
):
    return db.query(PersonaAutorizada).all()


@router.post("/", response_model=PersonaResponse)
def crear_persona(
    persona: PersonaCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    if persona.num_licencia:
        licencia_existente = db.query(PersonaAutorizada).filter(
            PersonaAutorizada.num_licencia == persona.num_licencia
        ).first()

        if licencia_existente:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una persona con ese número de licencia"
            )

    if persona.rfc:
        rfc_existente = db.query(PersonaAutorizada).filter(
            PersonaAutorizada.rfc == persona.rfc
        ).first()

        if rfc_existente:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una persona con ese RFC"
            )

    nueva_persona = PersonaAutorizada(**persona.model_dump())

    db.add(nueva_persona)
    db.commit()
    db.refresh(nueva_persona)

    return nueva_persona


@router.put("/{persona_id}", response_model=PersonaResponse)
def actualizar_persona(
    persona_id: int,
    datos: PersonaUpdate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    persona = db.query(PersonaAutorizada).filter(
        PersonaAutorizada.id == persona_id
    ).first()

    if persona is None:
        raise HTTPException(
            status_code=404,
            detail="Persona autorizada no encontrada"
        )

    if datos.num_licencia:
        licencia_existente = db.query(PersonaAutorizada).filter(
            PersonaAutorizada.num_licencia == datos.num_licencia,
            PersonaAutorizada.id != persona_id
        ).first()

        if licencia_existente:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una persona con ese número de licencia"
            )

    if datos.rfc:
        rfc_existente = db.query(PersonaAutorizada).filter(
            PersonaAutorizada.rfc == datos.rfc,
            PersonaAutorizada.id != persona_id
        ).first()

        if rfc_existente:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una persona con ese RFC"
            )

    datos_actualizados = datos.model_dump()

    for campo, valor in datos_actualizados.items():
        setattr(persona, campo, valor)

    db.commit()
    db.refresh(persona)

    return persona


@router.put("/{persona_id}/estado")
def actualizar_estado_persona(
    persona_id: int,
    datos: PersonaEstadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    estados_permitidos = [
        "activo",
        "suspendido"
    ]

    if datos.estado not in estados_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Estado de persona no válido"
        )

    persona = db.query(PersonaAutorizada).filter(
        PersonaAutorizada.id == persona_id
    ).first()

    if persona is None:
        raise HTTPException(
            status_code=404,
            detail="Persona autorizada no encontrada"
        )

    persona.estado = datos.estado

    db.commit()
    db.refresh(persona)

    return {
        "mensaje": "Estado actualizado correctamente",
        "persona_id": persona.id,
        "estado": persona.estado
    }


@router.get("/{persona_id}", response_model=PersonaResponse)
def obtener_persona_por_id(
    persona_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador", "capturista"]))
):
    persona = db.query(PersonaAutorizada).filter(
        PersonaAutorizada.id == persona_id
    ).first()

    if persona is None:
        raise HTTPException(
            status_code=404,
            detail="Persona autorizada no encontrada"
        )

    return persona