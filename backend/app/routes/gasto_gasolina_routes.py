from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.gasto_gasolina_model import GastoGasolina
from app.schemas.gasto_gasolina_schema import GastoGasolinaResponse

router = APIRouter(
    prefix="/gasto-gasolina",
    tags=["Gasto Gasolina"]
)

@router.get("/", response_model=list[GastoGasolinaResponse])
def listar_gasto_gasolina(db: Session = Depends(get_db)):
    return db.query(GastoGasolina).all()