from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario_model import UsuarioSistema
from app.schemas.usuario_schema import UsuarioResponse
from app.services.auth_service import obtener_usuario_actual

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    return db.query(UsuarioSistema).all()