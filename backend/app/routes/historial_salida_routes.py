from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.historial_salida_model import HistorialSalida
from app.schemas.historial_salida_schema import HistorialSalidaResponse

router = APIRouter(
    prefix="/historial-salida",
    tags=["Historial Salida"]
)

@router.get("/", response_model=list[HistorialSalidaResponse])
def listar_historial_salida(db: Session = Depends(get_db)):
    return db.query(HistorialSalida).all()