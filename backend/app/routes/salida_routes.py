from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.salida_model import Salida
from app.schemas.salida_schema import SalidaResponse, SalidaCreate

router = APIRouter(
    prefix="/salidas",
    tags=["Salidas"]
)

@router.get("/", response_model=list[SalidaResponse])
def listar_salidas(db: Session = Depends(get_db)):
    return db.query(Salida).all()

@router.post("/", response_model=SalidaResponse)
def crear_salida(salida: SalidaCreate, db: Session = Depends(get_db)):
    datos_salida = salida.model_dump(exclude_none=True)
    nueva_salida = Salida(**datos_salida)

    db.add(nueva_salida)
    db.commit()
    db.refresh(nueva_salida)

    return nueva_salida