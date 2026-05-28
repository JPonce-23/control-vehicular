from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.resguardo_model import Resguardo
from app.schemas.resguardo_schema import ResguardoResponse

router = APIRouter(
    prefix="/resguardos",
    tags=["Resguardos"]
)

@router.get("/", response_model=list[ResguardoResponse])
def listar_resguardos(db: Session = Depends(get_db)):
    return db.query(Resguardo).all()