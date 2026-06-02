from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.vehiculo_model import Vehiculo
from app.schemas.vehiculo_schema import VehiculoResponse, VehiculoCreate
from app.schemas.vehiculo_schema import VehiculoEstadoUpdate

router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehículos"]
)

@router.get("/", response_model=list[VehiculoResponse])
def listar_vehiculos(db: Session = Depends(get_db)):
    return db.query(Vehiculo).all()

@router.post("/", response_model=VehiculoResponse)
def crear_vehiculo(vehiculo: VehiculoCreate, db: Session = Depends(get_db)):
    nuevo_vehiculo = Vehiculo(**vehiculo.model_dump())
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo

@router.put("/{vehiculo_id}/estado")
def actualizar_estado_vehiculo(
    vehiculo_id: int,
    datos: VehiculoEstadoUpdate,
    db: Session = Depends(get_db)
):
    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id == vehiculo_id
    ).first()

    if vehiculo is None:
        raise HTTPException(
            status_code=404,
            detail="Vehiculo no encontrado"
        )

    estados_permitidos = [
        "disponible",
        "en_uso",
        "mantenimiento",
        "fuera_de_servicio"
    ]

    if datos.estado not in estados_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Estado de vehículo no válido"
        )

    vehiculo.estado = datos.estado

    db.commit()
    db.refresh(vehiculo)

    return {
        "mensaje": "Estado actualizado correctamente",
        "vehiculo_id": vehiculo.id,
        "estado": vehiculo.estado
    }