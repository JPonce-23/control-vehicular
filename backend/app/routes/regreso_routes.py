from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.historial_salida_model import HistorialSalida
from app.models.regreso_model import Regreso
from app.models.salida_model import Salida
from app.models.vehiculo_model import Vehiculo
from app.schemas.regreso_schema import RegresoCreate, RegresoResponse
from app.services.auth_service import obtener_usuario_actual, requerir_rol

router = APIRouter(prefix="/regresos", tags=["Regresos"])

NIVELES = {"vacio", "cuarto", "medio", "tres_cuartos", "lleno"}
NIVELES_LLANTAS = NIVELES - {"vacio"}
ESTADOS_VEHICULO = {"bueno", "dañado", "mantenimiento"}
FINALIDADES = {"disponible", "reparacion", "sustitucion"}


def _validar_catalogo(valor: str, permitidos: set[str], nombre: str) -> None:
    if valor not in permitidos:
        raise HTTPException(status_code=400, detail=f"{nombre} no válido")


@router.get("/", response_model=list[RegresoResponse])
def listar_regresos(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
):
    return db.query(Regreso).order_by(Regreso.fecha_regreso.desc()).all()


@router.post("/", response_model=RegresoResponse, status_code=201)
def crear_regreso(
    regreso: RegresoCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador", "capturista"])),
):
    _validar_catalogo(regreso.nivel_gasolina_regreso, NIVELES, "Nivel de gasolina")
    _validar_catalogo(regreso.estado_llantas_regreso, NIVELES_LLANTAS, "Nivel de llantas")
    _validar_catalogo(regreso.estado_vehiculo_regreso, ESTADOS_VEHICULO, "Estado del vehículo")
    _validar_catalogo(regreso.finalidad_devolucion, FINALIDADES, "Finalidad de devolución")

    salida = db.query(Salida).filter(Salida.id == regreso.salida_id).first()
    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")
    if db.query(Regreso).filter(Regreso.salida_id == regreso.salida_id).first():
        raise HTTPException(status_code=409, detail="Esta salida ya tiene un regreso registrado")
    if regreso.km_odometro_regreso < salida.km_odometro_salida:
        raise HTTPException(status_code=400, detail="El kilometraje de regreso no puede ser menor al de salida")

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == salida.vehiculo_id).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    fecha_regreso = regreso.fecha_regreso or datetime.now()
    if salida.fecha_salida and fecha_regreso.date() < salida.fecha_salida.date():
        raise HTTPException(status_code=400, detail="La fecha de regreso no puede ser anterior a la salida")

    datos_regreso = regreso.model_dump(exclude_none=True)
    datos_regreso["fecha_regreso"] = fecha_regreso
    nuevo_regreso = Regreso(**datos_regreso, capturado_por=usuario_actual.id)

    # El estado operativo se deriva del estado/finalidad reportados, no se fuerza siempre a disponible.
    if regreso.estado_vehiculo_regreso == "dañado" or regreso.finalidad_devolucion == "sustitucion":
        vehiculo.estado = "fuera_de_servicio"
    elif regreso.estado_vehiculo_regreso == "mantenimiento" or regreso.finalidad_devolucion == "reparacion":
        vehiculo.estado = "mantenimiento"
    else:
        vehiculo.estado = "disponible"
    vehiculo.km_acumulado = regreso.km_odometro_regreso

    saldo_antes = salida.saldo_tarjeta_salida or 0
    nuevo_regreso.saldo_tarjeta_antes_regreso = saldo_antes
    if regreso.saldo_tarjeta_regreso is not None:
        if regreso.saldo_tarjeta_regreso < 0:
            raise HTTPException(status_code=400, detail="El saldo final no puede ser negativo")
        if regreso.saldo_tarjeta_regreso > saldo_antes:
            raise HTTPException(
                status_code=400,
                detail="El saldo final no puede ser mayor al saldo con el que salió el vehículo",
            )
        nuevo_regreso.monto_gastado_tarjeta = saldo_antes - regreso.saldo_tarjeta_regreso
        vehiculo.saldo_tarjeta_gasolina = regreso.saldo_tarjeta_regreso

    db.add(nuevo_regreso)
    db.flush()
    db.add(
        HistorialSalida(
            salida_id=regreso.salida_id,
            usuario_id=usuario_actual.id,
            accion="registro_regreso",
            descripcion=f"Se registró el regreso; vehículo quedó {vehiculo.estado}",
            fecha=datetime.now(),
        )
    )
    db.commit()
    db.refresh(nuevo_regreso)
    return nuevo_regreso


@router.get("/salida/{salida_id}", response_model=RegresoResponse)
def obtener_regreso_por_salida(
    salida_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
):
    regreso = db.query(Regreso).filter(Regreso.salida_id == salida_id).first()
    if regreso is None:
        raise HTTPException(status_code=404, detail="Regreso no encontrado para esta salida")
    return regreso
