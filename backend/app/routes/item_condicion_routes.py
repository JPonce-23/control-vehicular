from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.item_condicion_model import ItemCondicion
from app.schemas.item_condicion_schema import ItemCondicionResponse

router = APIRouter(
    prefix="/item-condicion",
    tags=["Item Condición"]
)

@router.get("/", response_model=list[ItemCondicionResponse])
def listar_item_condicion(db: Session = Depends(get_db)):
    return db.query(ItemCondicion).all()