from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item_inventario_model import ItemInventario
from app.schemas.item_inventario_schema import ItemInventarioResponse
from app.services.auth_service import obtener_usuario_actual

router = APIRouter(prefix="/item-inventario", tags=["Item Inventario"])


@router.get("/", response_model=list[ItemInventarioResponse])
def listar_item_inventario(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
):
    return db.query(ItemInventario).filter(ItemInventario.activo.is_(True)).all()
