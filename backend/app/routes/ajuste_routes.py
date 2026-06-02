from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ajuste_model import AjusteOdometro
from app.schemas.ajuste_schema import AjusteResponse, AjusteCreate

router = APIRouter(
    prefix="/ajustes",
    tags=["Ajustes odómetro"]
)

@router.get("/", response_model=list[AjusteResponse])
def listar_ajustes(db: Session = Depends(get_db)):
    return db.query(AjusteOdometro).all()

@router.post("/", response_model=AjusteResponse)
def crear_ajuste(ajuste: AjusteCreate, db: Session = Depends(get_db)):
    datos_ajuste = ajuste.model_dump(exclude_none=True)
    nuevo_ajuste = AjusteOdometro(**datos_ajuste)

    db.add(nuevo_ajuste)
    db.commit()
    db.refresh(nuevo_ajuste)

    return nuevo_ajuste