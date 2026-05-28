from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.salida_model import Salida
from app.schemas.salida_schema import SalidaResponse

router = APIRouter(
    prefix="/salidas",
    tags=["Salidas"]
)

@router.get("/", response_model=list[SalidaResponse])
def listar_salidas(db: Session = Depends(get_db)):
    return db.query(Salida).all()