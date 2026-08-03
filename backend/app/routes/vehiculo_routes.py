from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.vehiculo_model import Vehiculo
from app.schemas.vehiculo_schema import VehiculoCreate, VehiculoEstadoUpdate, VehiculoResponse, VehiculoUpdate
from app.services.auth_service import requerir_rol

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])

CAMPOS_UNICOS = {
    "num_economico": "Ya existe un vehículo con ese número económico",
    "placa": "Ya existe un vehículo registrado con esa placa",
    "num_serie": "Ya existe un vehículo registrado con ese número de serie",
    "num_motor": "Ya existe un vehículo registrado con ese número de motor",
    "num_inventario": "Ya existe un vehículo registrado con ese número de inventario",
    "num_tarjeta_gasolina": "Ya existe un vehículo con esa tarjeta de gasolina",
}


def _normalizar(datos: dict) -> dict:
    for campo, valor in list(datos.items()):
        if isinstance(valor, str):
            valor = valor.strip()
            datos[campo] = valor or None
    for campo in ("placa", "num_serie", "num_motor", "num_inventario"):
        if datos.get(campo):
            datos[campo] = datos[campo].upper()
    return datos


def _validar_unicos(db: Session, datos: dict, vehiculo_id: int | None = None) -> None:
    for campo, mensaje in CAMPOS_UNICOS.items():
        valor = datos.get(campo)
        if not valor:
            continue
        query = db.query(Vehiculo).filter(getattr(Vehiculo, campo) == valor)
        if vehiculo_id is not None:
            query = query.filter(Vehiculo.id != vehiculo_id)
        if query.first():
            raise HTTPException(status_code=409, detail=mensaje)


@router.get("/", response_model=list[VehiculoResponse])
def listar_vehiculos(
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador", "capturista"])),
):
    return db.query(Vehiculo).order_by(Vehiculo.id).all()


@router.post("/", response_model=VehiculoResponse, status_code=201)
def crear_vehiculo(
    vehiculo: VehiculoCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    datos = _normalizar(vehiculo.model_dump())
    datos["estado"] = "disponible"
    _validar_unicos(db, datos)
    nuevo_vehiculo = Vehiculo(**datos)
    db.add(nuevo_vehiculo)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible registrar el vehículo por un dato duplicado")
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo


@router.put("/{vehiculo_id}/estado")
def actualizar_estado_vehiculo(
    vehiculo_id: int,
    datos: VehiculoEstadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    if datos.estado not in {"disponible", "en_uso", "mantenimiento", "fuera_de_servicio"}:
        raise HTTPException(status_code=400, detail="Estado de vehículo no válido")
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    if vehiculo.estado == "en_uso" and datos.estado != "en_uso":
        raise HTTPException(status_code=400, detail="No se puede cambiar manualmente el estado de un vehículo con una salida activa")
    vehiculo.estado = datos.estado
    db.commit()
    return {"mensaje": "Estado actualizado correctamente", "vehiculo_id": vehiculo.id, "estado": vehiculo.estado}


@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
def obtener_vehiculo_por_id(
    vehiculo_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador", "capturista"])),
):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo


@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
def actualizar_vehiculo(
    vehiculo_id: int,
    datos: VehiculoUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    actualizados = _normalizar(datos.model_dump())
    _validar_unicos(db, actualizados, vehiculo_id)
    for campo, valor in actualizados.items():
        setattr(vehiculo, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible actualizar el vehículo por un dato duplicado")
    db.refresh(vehiculo)
    return vehiculo
