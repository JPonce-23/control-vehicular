from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.historial_salida_model import HistorialSalida
from app.schemas.historial_salida_schema import HistorialSalidaResponse
from app.services.auth_service import obtener_usuario_actual

router = APIRouter(
    prefix="/historial-salida",
    tags=["Historial Salida"]
)

@router.get("/", response_model=list[HistorialSalidaResponse])
def listar_historial_salida(
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    return db.query(HistorialSalida).all()


@router.get("/{salida_id}", response_model=list[HistorialSalidaResponse])
def obtener_historial_por_salida(
    salida_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    historial = db.query(HistorialSalida).filter(
        HistorialSalida.salida_id == salida_id
    ).order_by(HistorialSalida.fecha.desc()).all()

    if not historial:
        raise HTTPException(
            status_code=404,
            detail="No hay historial registrado para esta salida"
        )

    return historial