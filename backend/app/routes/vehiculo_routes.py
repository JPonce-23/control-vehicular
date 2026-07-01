from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.vehiculo_model import Vehiculo
from app.schemas.vehiculo_schema import VehiculoResponse, VehiculoCreate
from app.schemas.vehiculo_schema import VehiculoEstadoUpdate, VehiculoUpdate
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


@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
def actualizar_vehiculo(
    vehiculo_id: int,
    datos: VehiculoUpdate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    placa_existente = db.query(Vehiculo).filter(
        Vehiculo.placa == datos.placa,
        Vehiculo.id != vehiculo_id
    ).first()

    if placa_existente:
        raise HTTPException(status_code=400, detail="Ya existe un vehículo con esa placa")

    serie_existente = db.query(Vehiculo).filter(
        Vehiculo.num_serie == datos.num_serie,
        Vehiculo.id != vehiculo_id
    ).first()

    if serie_existente:
        raise HTTPException(status_code=400, detail="Ya existe un vehículo con ese número de serie")

    if datos.num_motor:
        motor_existente = db.query(Vehiculo).filter(
            Vehiculo.num_motor == datos.num_motor,
            Vehiculo.id != vehiculo_id
        ).first()

        if motor_existente:
            raise HTTPException(status_code=400, detail="Ya existe un vehículo con ese número de motor")

    if datos.num_inventario:
        inventario_existente = db.query(Vehiculo).filter(
            Vehiculo.num_inventario == datos.num_inventario,
            Vehiculo.id != vehiculo_id
        ).first()

        if inventario_existente:
            raise HTTPException(status_code=400, detail="Ya existe un vehículo con ese número de inventario")

    if datos.num_tarjeta_gasolina:
        tarjeta_existente = db.query(Vehiculo).filter(
            Vehiculo.num_tarjeta_gasolina == datos.num_tarjeta_gasolina,
            Vehiculo.id != vehiculo_id
        ).first()

        if tarjeta_existente:
            raise HTTPException(status_code=400, detail="Ya existe un vehículo con esa tarjeta de gasolina")

    datos_actualizados = datos.model_dump()

    if datos_actualizados.get("saldo_tarjeta_gasolina") is None:
        datos_actualizados["saldo_tarjeta_gasolina"] = 0

    for campo, valor in datos_actualizados.items():
        setattr(vehiculo, campo, valor)

    db.commit()
    db.refresh(vehiculo)

    return vehiculo

