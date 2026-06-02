from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.regreso_model import Regreso
from app.schemas.regreso_schema import RegresoResponse, RegresoCreate

router = APIRouter(
    prefix="/regresos",
    tags=["Regresos"]
)

@router.get("/", response_model=list[RegresoResponse])
def listar_regresos(db: Session = Depends(get_db)):
    return db.query(Regreso).all()

@router.post("/", response_model=RegresoResponse)
def crear_regreso(regreso: RegresoCreate, db: Session = Depends(get_db)):
    datos_regreso = regreso.model_dump(exclude_none=True)
    nuevo_regreso = Regreso(**datos_regreso)

    db.add(nuevo_regreso)
    db.commit()
    db.refresh(nuevo_regreso)

    return nuevo_regreso