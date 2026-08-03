from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.revision_condicion_model import RevisionCondicion
from app.schemas.revision_condicion_schema import RevisionCondicionResponse
from app.services.auth_service import obtener_usuario_actual

router = APIRouter(prefix="/revision-condicion", tags=["Revisión Condición"])


@router.get("/", response_model=list[RevisionCondicionResponse])
def listar_revision_condicion(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
):
    return db.query(RevisionCondicion).all()
