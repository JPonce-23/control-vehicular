from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.persona_model import PersonaAutorizada
from app.schemas.persona_schema import PersonaResponse, PersonaCreate, PersonaEstadoUpdate

router = APIRouter(
    prefix="/personas",
    tags=["Personas autorizadas"]
)

@router.get("/", response_model=list[PersonaResponse])
def listar_personas(db: Session = Depends(get_db)):
    return db.query(PersonaAutorizada).all()

@router.post("/", response_model=PersonaResponse)
def crear_persona(persona: PersonaCreate, db: Session = Depends(get_db)):
    nueva_persona = PersonaAutorizada(**persona.model_dump())
    db.add(nueva_persona)
    db.commit()
    db.refresh(nueva_persona)
    return nueva_persona

@router.put("/{persona_id}/estado")
def actualizar_estado_persona(
    persona_id: int,
    datos: PersonaEstadoUpdate,
    db: Session = Depends(get_db)
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