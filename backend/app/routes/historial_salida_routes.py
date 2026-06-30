from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, aliased
from typing import Optional
from app.database import get_db
from app.models.historial_salida_model import HistorialSalida
from app.models.salida_model import Salida
from app.models.regreso_model import Regreso
from app.models.vehiculo_model import Vehiculo
from app.schemas.historial_salida_schema import HistorialSalidaResponse, HistorialAuditoriaResponse, HistorialAuditoriaVehiculoResponse
from app.services.auth_service import obtener_usuario_actual
from app.models.usuario_model import UsuarioSistema
from app.models.persona_model import PersonaAutorizada
from app.services.auth_service import requerir_rol

router = APIRouter(
    prefix="/historial-salida",
    tags=["Historial Salida"]
)


@router.get("/auditoria", response_model=list[HistorialAuditoriaResponse])
def listar_auditoria(
    salida_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
    accion: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    query = db.query(
        HistorialSalida,
        UsuarioSistema
    ).outerjoin(
        UsuarioSistema,
        HistorialSalida.usuario_id == UsuarioSistema.id
    )

    if salida_id is not None:
        query = query.filter(HistorialSalida.salida_id == salida_id)

    if usuario_id is not None:
        query = query.filter(HistorialSalida.usuario_id == usuario_id)

    if accion is not None:
        query = query.filter(HistorialSalida.accion == accion)

    registros = query.order_by(HistorialSalida.id.desc()).all()

    respuesta = []

    for historial, usuario in registros:
        respuesta.append({
            "id": historial.id,
            "salida_id": historial.salida_id,
            "usuario_id": historial.usuario_id,
            "usuario_correo": usuario.correo if usuario else None,
            "usuario_nombre": usuario.nombre if usuario and hasattr(usuario, "nombre") else None,
            "accion": historial.accion,
            "descripcion": historial.descripcion,
            "fecha": historial.fecha
        })

    return respuesta


def fecha_a_texto(fecha):
    if fecha is None:
        return None

    return str(fecha)


def obtener_nombre_usuario(usuario):
    if usuario is None:
        return "Usuario no encontrado"

    nombre = getattr(usuario, "nombre", None)
    correo = getattr(usuario, "correo", None)

    if nombre and correo:
        return f"{nombre} - {correo}"

    if correo:
        return correo

    if nombre:
        return nombre

    return f"Usuario {usuario.id}"


def obtener_nombre_persona(persona):
    if persona is None:
        return "Sin persona"

    nombre = getattr(persona, "nombre", None)
    apellido_paterno = getattr(persona, "apellido_paterno", None)
    apellido_materno = getattr(persona, "apellido_materno", None)

    partes = []

    if nombre:
        partes.append(nombre)

    if apellido_paterno:
        partes.append(apellido_paterno)

    if apellido_materno:
        partes.append(apellido_materno)

    if partes:
        return " ".join(partes)

    return "Persona autorizada"


@router.get("/auditoria-vehiculo", response_model=list[HistorialAuditoriaVehiculoResponse])
def listar_auditoria_por_vehiculo(
    vehiculo_id: int,
    accion: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    UsuarioHistorial = aliased(UsuarioSistema)

    # ÚNICA fuente de verdad: historial_salida.
    # Salida/Regreso/PersonaAutorizada solo se usan para enriquecer cada fila.
    historial_query = db.query(
        HistorialSalida,
        Salida,
        UsuarioHistorial
    ).join(
        Salida,
        HistorialSalida.salida_id == Salida.id
    ).outerjoin(
        UsuarioHistorial,
        HistorialSalida.usuario_id == UsuarioHistorial.id
    ).filter(
        Salida.vehiculo_id == vehiculo_id
    )

    if accion is not None:
        historial_query = historial_query.filter(HistorialSalida.accion == accion)

    historial_registros = historial_query.order_by(HistorialSalida.id.desc()).all()

    respuesta = []

    for historial, salida_historial, usuario_historial in historial_registros:
        regreso_historial = db.query(Regreso).filter(
            Regreso.salida_id == salida_historial.id
        ).first()

        persona_historial = db.query(PersonaAutorizada).filter(
            PersonaAutorizada.id == salida_historial.persona_id
        ).first()

        respuesta.append({
            "salida_id": salida_historial.id,
            "vehiculo_id": vehiculo.id,
            "vehiculo": f"{vehiculo.marca} {vehiculo.tipo}",
            "placa": vehiculo.placa,
            "persona": obtener_nombre_persona(persona_historial),
            "fecha_salida": fecha_a_texto(salida_historial.fecha_salida),
            "fecha_regreso": fecha_a_texto(regreso_historial.fecha_regreso) if regreso_historial else None,
            "accion": historial.accion,
            "descripcion": historial.descripcion,
            "fecha_movimiento": fecha_a_texto(historial.fecha),
            "usuario_id": historial.usuario_id,
            "usuario": obtener_nombre_usuario(usuario_historial)
        })

    respuesta.sort(
        key=lambda item: item["fecha_movimiento"] or "",
        reverse=True
    )

    return respuesta



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



