from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.revision_inventario_model import RevisionInventario
from app.schemas.revision_inventario_schema import RevisionInventarioResponse
from app.services.auth_service import obtener_usuario_actual

router = APIRouter(prefix="/revision-inventario", tags=["Revisión Inventario"])


@router.get("/", response_model=list[RevisionInventarioResponse])
def listar_revision_inventario(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
):
    return db.query(RevisionInventario).all()
