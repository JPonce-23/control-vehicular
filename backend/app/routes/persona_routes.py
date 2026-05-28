from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.persona_model import PersonaAutorizada
from app.schemas.persona_schema import PersonaResponse

router = APIRouter(
    prefix="/personas",
    tags=["Personas autorizadas"]
)

@router.get("/", response_model=list[PersonaResponse])
def listar_personas(db: Session = Depends(get_db)):
    return db.query(PersonaAutorizada).all()