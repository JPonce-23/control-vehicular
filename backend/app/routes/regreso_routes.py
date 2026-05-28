from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.regreso_model import Regreso
from app.schemas.regreso_schema import RegresoResponse

router = APIRouter(
    prefix="/regresos",
    tags=["Regresos"]
)

@router.get("/", response_model=list[RegresoResponse])
def listar_regresos(db: Session = Depends(get_db)):
    return db.query(Regreso).all()