from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.vehiculo_model import Vehiculo
from app.schemas.vehiculo_schema import VehiculoResponse, VehiculoCreate
from app.schemas.vehiculo_schema import VehiculoEstadoUpdate
from app.services.auth_service import obtener_usuario_actual, requerir_rol

router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehículos"]
)

@router.get("/", response_model=list[VehiculoResponse])
def listar_vehiculos(db: Session = Depends(get_db)):
    return db.query(Vehiculo).all()

@router.post("/", response_model=VehiculoResponse)
def crear_vehiculo(
    vehiculo: VehiculoCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    campos_unicos = {
        "placa": "Ya existe un vehículo registrado con esa placa",
        "num_serie": "Ya existe un vehículo registrado con ese número de serie",
        "num_motor": "Ya existe un vehículo registrado con ese número de motor",
        "num_inventario": "Ya existe un vehículo registrado con ese número de inventario"
    }

    for campo, mensaje in campos_unicos.items():
        valor = getattr(vehiculo, campo, None)

        if valor is not None and str(valor).strip() != "":
            existente = db.query(Vehiculo).filter(
                getattr(Vehiculo, campo) == valor
            ).first()

            if existente:
                raise HTTPException(
                    status_code=400,
                    detail=mensaje
                )

    nuevo_vehiculo = Vehiculo(**vehiculo.model_dump())

    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)

    return nuevo_vehiculo

@router.put("/{vehiculo_id}/estado")
def actualizar_estado_vehiculo(
    vehiculo_id: int,
    datos: VehiculoEstadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
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
    
@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
def obtener_vehiculo_por_id(
    vehiculo_id: int,
    db: Session = Depends(get_db)
):
    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id == vehiculo_id
    ).first()

    if vehiculo is None:
        raise HTTPException(
            status_code=404,
            detail="Vehículo no encontrado"
        )

    return vehiculo


