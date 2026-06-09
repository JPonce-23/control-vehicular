from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.resguardo_model import Resguardo
from app.schemas.resguardo_schema import ResguardoResponse, ResguardoCreate


router = APIRouter(
    prefix="/resguardos",
    tags=["Resguardos"]
)
"""
@router.get("/", response_model=list[ResguardoResponse])
def listar_resguardos(db: Session = Depends(get_db)):
    return db.query(Resguardo).all()

@router.post("/", response_model=ResguardoResponse)
def crear_resguardo(resguardo: ResguardoCreate, db: Session = Depends(get_db)):
    datos_resguardo = resguardo.model_dump(exclude_none=True)
    nuevo_resguardo = Resguardo(**datos_resguardo)

    db.add(nuevo_resguardo)
    db.commit()
    db.refresh(nuevo_resguardo)

    return nuevo_resguardo

"""