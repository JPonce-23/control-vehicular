from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.persona_model import PersonaAutorizada
from app.schemas.persona_schema import PersonaResponse, PersonaCreate

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