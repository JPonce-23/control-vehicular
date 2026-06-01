from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.presupuesto_gasolina_model import PresupuestoGasolina
from app.schemas.presupuesto_gasolina_schema import PresupuestoGasolinaResponse

router = APIRouter(
    prefix="/presupuesto-gasolina",
    tags=["Presupuesto Gasolina"]
)

@router.get("/", response_model=list[PresupuestoGasolinaResponse])
def listar_presupuestos(db: Session = Depends(get_db)):
    return db.query(PresupuestoGasolina).all()