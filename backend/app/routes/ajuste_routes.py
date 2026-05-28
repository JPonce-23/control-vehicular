from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ajuste_model import AjusteOdometro
from app.schemas.ajuste_schema import AjusteResponse

router = APIRouter(
    prefix="/ajustes",
    tags=["Ajustes odómetro"]
)

@router.get("/", response_model=list[AjusteResponse])
def listar_ajustes(db: Session = Depends(get_db)):
    return db.query(AjusteOdometro).all()