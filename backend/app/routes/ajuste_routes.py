from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ajuste_model import AjusteOdometro
from app.models.vehiculo_model import Vehiculo
from app.schemas.ajuste_schema import AjusteCreate, AjusteResponse
from app.services.auth_service import requerir_rol

router = APIRouter(prefix="/ajustes", tags=["Ajustes odómetro"])


@router.get("/", response_model=list[AjusteResponse])
def listar_ajustes(
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    return db.query(AjusteOdometro).order_by(AjusteOdometro.fecha_ajuste.desc()).all()


@router.post("/", response_model=AjusteResponse, status_code=201)
def crear_ajuste(
    ajuste: AjusteCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == ajuste.vehiculo_id).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    if ajuste.km_nuevo < 0:
        raise HTTPException(status_code=400, detail="El kilometraje no puede ser negativo")

    nuevo_ajuste = AjusteOdometro(
        vehiculo_id=vehiculo.id,
        km_anterior=vehiculo.km_acumulado or 0,
        km_nuevo=ajuste.km_nuevo,
        motivo=ajuste.motivo,
        realizado_por=usuario_actual.id,
    )
    vehiculo.km_acumulado = ajuste.km_nuevo
    db.add(nuevo_ajuste)
    db.commit()
    db.refresh(nuevo_ajuste)
    return nuevo_ajuste
