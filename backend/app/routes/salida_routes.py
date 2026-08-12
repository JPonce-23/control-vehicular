from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.database import get_db
from typing import Optional
from sqlalchemy import or_, func
from app.models.salida_model import Salida
from app.schemas.salida_schema import SalidaResponse, SalidaCreate, SalidaUpdate, SalidaCorreccionAdministrativa, SalidaCancelacion, CondicionUpdateRequest, InventarioUpdateRequest
from app.models.vehiculo_model import Vehiculo
from app.models.historial_salida_model import HistorialSalida
from app.models.persona_model import PersonaAutorizada
from app.services.auth_service import obtener_usuario_actual, requerir_rol
from app.models.regreso_model import Regreso
from app.models.resguardo_model import Resguardo
from app.models.revision_condicion_model import RevisionCondicion
from app.models.item_condicion_model import ItemCondicion
from app.models.revision_inventario_model import RevisionInventario
from app.models.item_inventario_model import ItemInventario
from app.services.resguardo_service import generar_resguardo_word
from fastapi.responses import FileResponse
import os

router = APIRouter(
    prefix="/salidas",
    tags=["Salidas"]
)

NIVELES = {"vacio", "cuarto", "medio", "tres_cuartos", "lleno"}
TIPOS_MOVIMIENTO = {"asignacion", "devolucion"}
ESTADOS_REGRESO = {"bueno", "dañado", "mantenimiento"}
FINALIDADES_DEVOLUCION = {"disponible", "reparacion", "sustitucion"}


def _validar_valor(valor, permitidos: set[str], nombre: str) -> None:
    if valor is not None and valor not in permitidos:
        raise HTTPException(status_code=400, detail=f"{nombre} no válido")


@router.get("/buscar-correccion")
def buscar_salidas_para_correccion(
    placa: Optional[str] = None,
    persona: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    query = db.query(
        Salida,
        Vehiculo,
        PersonaAutorizada,
        Regreso
    ).join(
        Vehiculo,
        Salida.vehiculo_id == Vehiculo.id
    ).join(
        PersonaAutorizada,
        Salida.persona_id == PersonaAutorizada.id
    ).join(
        Regreso,
        Regreso.salida_id == Salida.id
    )

    if placa:
        query = query.filter(
            Vehiculo.placa.ilike(f"%{placa}%")
        )

    if persona:
        texto_persona = f"%{persona}%"

        query = query.filter(
            or_(
                PersonaAutorizada.nombre.ilike(texto_persona),
                PersonaAutorizada.apellido_paterno.ilike(texto_persona),
                PersonaAutorizada.apellido_materno.ilike(texto_persona),
                func.concat(
                    PersonaAutorizada.nombre,
                    " ",
                    PersonaAutorizada.apellido_paterno,
                    " ",
                    func.coalesce(PersonaAutorizada.apellido_materno, "")
                ).ilike(texto_persona)
            )
        )

    resultados = query.order_by(Salida.fecha_salida.desc()).all()

    respuesta = []

    for salida, vehiculo, persona_autorizada, regreso in resultados:
        nombre_persona = " ".join(
            parte for parte in [
                persona_autorizada.nombre,
                persona_autorizada.apellido_paterno,
                persona_autorizada.apellido_materno
            ] if parte
        )

        respuesta.append({
            "salida_id": salida.id,
            "vehiculo_id": vehiculo.id,
            "vehiculo": f"{vehiculo.marca} {vehiculo.tipo}",
            "placa": vehiculo.placa,
            "persona_id": persona_autorizada.id,
            "persona": nombre_persona,
            "cargo": persona_autorizada.cargo,
            "fecha_salida": salida.fecha_salida,
            "fecha_regreso": regreso.fecha_regreso,
            "finalidad_uso": salida.finalidad_uso,
            "km_odometro_salida": salida.km_odometro_salida,
            "km_odometro_regreso": regreso.km_odometro_regreso
        })

    return respuesta


@router.get("/", response_model=list[SalidaResponse])
def listar_salidas(
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    return db.query(Salida).order_by(Salida.fecha_salida.desc()).all()

@router.post("/", response_model=SalidaResponse, status_code=201)
def crear_salida(
    salida: SalidaCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador", "capturista"]))
):
    _validar_valor(salida.tipo_movimiento, TIPOS_MOVIMIENTO, "Tipo de movimiento")
    _validar_valor(salida.nivel_gasolina_salida, NIVELES, "Nivel de gasolina")
    _validar_valor(salida.estado_llantas_salida, NIVELES - {"vacio"}, "Nivel de llantas")
    if not salida.finalidad_uso.strip():
        raise HTTPException(status_code=400, detail="La finalidad de uso es obligatoria")
    fecha_base = (salida.fecha_salida or datetime.now()).date()
    if salida.fecha_regreso_estimada and salida.fecha_regreso_estimada < fecha_base:
        raise HTTPException(status_code=400, detail="La fecha estimada de regreso no puede ser anterior a la salida")

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == salida.vehiculo_id).first()

    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    if vehiculo.estado == "en_uso":
        raise HTTPException(
            status_code=400,
            detail="El vehículo ya se encuentra en uso"
        )

    if vehiculo.estado == "mantenimiento":
        raise HTTPException(
            status_code=400,
            detail="El vehículo se encuentra en mantenimiento"
        )

    if vehiculo.estado == "fuera_de_servicio":
        raise HTTPException(
            status_code=400,
            detail="El vehículo está fuera de servicio"
        )

    if vehiculo.estado != "disponible":
        raise HTTPException(
            status_code=400,
            detail="El vehículo no está disponible para salida"
        )

    if salida.km_odometro_salida < vehiculo.km_acumulado:
        raise HTTPException(
            status_code=400,
            detail="El kilometraje de salida no puede ser menor al kilometraje actual del vehículo"
        )

    persona = db.query(PersonaAutorizada).filter(
        PersonaAutorizada.id == salida.persona_id
    ).first()

    if persona is None:
        raise HTTPException(status_code=404, detail="Persona autorizada no encontrada")

    if persona.estado != "activo":
        raise HTTPException(
            status_code=400,
            detail="La persona autorizada no está activa"
        )
        
    persona_en_viaje = (db.query(Salida).join(Regreso, Salida.id == Regreso.salida_id, isouter=True)
        .filter(Salida.persona_id == persona.id, Salida.estado == "activa", Regreso.id == None).first())
    
    if persona_en_viaje is not None:
        raise HTTPException(
            status_code=400,
            detail="La persona seleccionada tiene un viaje en curso"
        )

    if persona.vigencia_licencia is not None and persona.vigencia_licencia < date.today():
        raise HTTPException(
            status_code=400,
            detail="La licencia del conductor está vencida"
    )

    if salida.monto_agregado_tarjeta < 0:
        raise HTTPException(status_code=400, detail="El monto agregado a la tarjeta no puede ser negativo")

    # La regla de negocio actual establece que todos los resguardos son provisionales.
    datos_salida = salida.model_dump(exclude_none=True)
    datos_salida["forma_movimiento"] = "provisional"
    if "fecha_fin_provisional" not in datos_salida and salida.fecha_regreso_estimada:
        datos_salida["fecha_fin_provisional"] = salida.fecha_regreso_estimada

    nueva_salida = Salida(
        **datos_salida,
        capturado_por=usuario_actual.id
    )

    vehiculo.estado = "en_uso"

    db.add(nueva_salida)
    db.flush()

    historial = HistorialSalida(
        salida_id=nueva_salida.id,
        usuario_id=usuario_actual.id,
        accion="registro_salida",
        descripcion="Se registró la salida del vehículo",
        fecha=datetime.now()
    )


    saldo_actual = vehiculo.saldo_tarjeta_gasolina or 0
    monto_agregado = salida.monto_agregado_tarjeta or 0

    saldo_salida = saldo_actual + monto_agregado

    nueva_salida.monto_agregado_tarjeta = monto_agregado
    nueva_salida.saldo_tarjeta_salida = saldo_salida

    vehiculo.saldo_tarjeta_gasolina = saldo_salida



    db.add(historial)
    db.commit()
    db.refresh(nueva_salida)

    return nueva_salida


@router.get("/activas", response_model=list[SalidaResponse], include_in_schema=False)
@router.get("/activas/", response_model=list[SalidaResponse])
def listar_salidas_activas(
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    salidas = db.query(Salida).outerjoin(
        Regreso, Salida.id == Regreso.salida_id
    ).filter(
        Salida.estado == "activa",
        Regreso.id == None
    ).all()

    return salidas

@router.get("/activas-para-cancelacion")
def listar_salidas_activas_para_cancelacion(
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    resultados = (
        db.query(Salida, Vehiculo, PersonaAutorizada)
        .join(Vehiculo, Salida.vehiculo_id == Vehiculo.id)
        .join(PersonaAutorizada, Salida.persona_id == PersonaAutorizada.id)
        .outerjoin(Regreso, Salida.id == Regreso.salida_id)
        .filter(
            Salida.estado == "activa",
            Regreso.id == None
        )
        .order_by(Salida.fecha_salida.desc())
        .all()
    )
    
    respuesta = []
    for salida, vehiculo, persona in resultados:
        nombre_persona = " ".join(
            parte for parte in [
                persona.nombre,
                persona.apellido_paterno,
                persona.apellido_materno
            ] if parte
        )
        
        respuesta.append({
            "salida_id": salida.id,
            "vehiculo_id": vehiculo.id,
            "placa": vehiculo.placa,
            "vehiculo": f"{vehiculo.marca} {vehiculo.tipo}",
            "persona": nombre_persona,
            "fecha_salida": salida.fecha_salida,
        })
        
    return respuesta



@router.get("/{salida_id}", response_model=SalidaResponse)
def obtener_salida_por_id(
    salida_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    salida = db.query(Salida).filter(
        Salida.id == salida_id
    ).first()

    if salida is None:
        raise HTTPException(
            status_code=404,
            detail="Salida no encontrada"
        )

    return salida



@router.put("/{salida_id}", response_model=SalidaResponse)
def actualizar_salida(
    salida_id: int,
    datos: SalidaUpdate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    salida = db.query(Salida).filter(Salida.id == salida_id).first()

    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")

    regreso_existente = db.query(Regreso).filter(
        Regreso.salida_id == salida_id
    ).first()

    if regreso_existente:
        raise HTTPException(
            status_code=400,
            detail="No se puede editar una salida que ya tiene regreso registrado"
        )

    resguardo_existente = db.query(Resguardo).filter(
        Resguardo.salida_id == salida_id
    ).first()

    datos_actualizar = datos.model_dump(exclude_unset=True)
    _validar_valor(datos_actualizar.get("tipo_movimiento"), TIPOS_MOVIMIENTO, "Tipo de movimiento")
    _validar_valor(datos_actualizar.get("nivel_gasolina_salida"), NIVELES, "Nivel de gasolina")
    _validar_valor(datos_actualizar.get("estado_llantas_salida"), NIVELES - {"vacio"}, "Nivel de llantas")
    if "finalidad_uso" in datos_actualizar and not (datos_actualizar["finalidad_uso"] or "").strip():
        raise HTTPException(status_code=400, detail="La finalidad de uso no puede quedar vacía")
    # La forma de movimiento se conserva provisional incluso en ediciones.
    if "forma_movimiento" in datos_actualizar:
        datos_actualizar["forma_movimiento"] = "provisional"

    for campo, valor in datos_actualizar.items():
        setattr(salida, campo, valor)

    db.commit()
    db.refresh(salida)

    return salida



@router.patch("/{salida_id}/correccion-administrativa")
def corregir_salida_administrativa(
    salida_id: int,
    datos: SalidaCorreccionAdministrativa,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    salida = db.query(Salida).filter(Salida.id == salida_id).first()

    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")

    if not datos.motivo or datos.motivo.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="El motivo de la corrección es obligatorio"
        )
    _validar_valor(datos.nivel_gasolina_salida, NIVELES, "Nivel de gasolina de salida")
    _validar_valor(datos.nivel_gasolina_regreso, NIVELES, "Nivel de gasolina de regreso")
    _validar_valor(datos.estado_llantas_salida, NIVELES - {"vacio"}, "Nivel de llantas de salida")
    _validar_valor(datos.estado_llantas_regreso, NIVELES - {"vacio"}, "Nivel de llantas de regreso")
    _validar_valor(datos.estado_vehiculo_regreso, ESTADOS_REGRESO, "Estado del vehículo al regreso")
    _validar_valor(datos.finalidad_devolucion, FINALIDADES_DEVOLUCION, "Finalidad de devolución")

    regreso = db.query(Regreso).filter(Regreso.salida_id == salida_id).first()

    if regreso is None:
        raise HTTPException(
            status_code=400,
            detail="La corrección administrativa requiere que exista un regreso registrado"
        )

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == salida.vehiculo_id).first()

    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    if datos.km_odometro_salida is not None:
        salida.km_odometro_salida = datos.km_odometro_salida

    if datos.km_odometro_regreso is not None:
        regreso.km_odometro_regreso = datos.km_odometro_regreso
        vehiculo.km_acumulado = datos.km_odometro_regreso

    if regreso.km_odometro_regreso < salida.km_odometro_salida:
        raise HTTPException(
            status_code=400,
            detail="El kilometraje de regreso no puede ser menor al kilometraje de salida"
        )

    if datos.nivel_gasolina_salida is not None:
        salida.nivel_gasolina_salida = datos.nivel_gasolina_salida

    if datos.nivel_gasolina_regreso is not None:
        regreso.nivel_gasolina_regreso = datos.nivel_gasolina_regreso

    if datos.estado_llantas_salida is not None:
        salida.estado_llantas_salida = datos.estado_llantas_salida

    if datos.estado_llantas_regreso is not None:
        regreso.estado_llantas_regreso = datos.estado_llantas_regreso

    if datos.estado_vehiculo_regreso is not None:
        regreso.estado_vehiculo_regreso = datos.estado_vehiculo_regreso

    if datos.finalidad_uso is not None:
        salida.finalidad_uso = datos.finalidad_uso

    if datos.finalidad_devolucion is not None:
        regreso.finalidad_devolucion = datos.finalidad_devolucion

    # Mantener sincronizado el estado operativo del vehículo cuando se corrige el regreso.
    if regreso.estado_vehiculo_regreso == "dañado" or regreso.finalidad_devolucion == "sustitucion":
        vehiculo.estado = "fuera_de_servicio"
    elif regreso.estado_vehiculo_regreso == "mantenimiento" or regreso.finalidad_devolucion == "reparacion":
        vehiculo.estado = "mantenimiento"
    else:
        vehiculo.estado = "disponible"

    if datos.observaciones_salida is not None:
        salida.observaciones = datos.observaciones_salida

    if datos.observaciones_regreso is not None:
        regreso.observaciones = datos.observaciones_regreso

    historial = HistorialSalida(
        salida_id=salida.id,
        usuario_id=usuario_actual.id,
        accion="modificacion",
        descripcion=f"Corrección administrativa: {datos.motivo}",
        fecha=datetime.now()
    )

    db.add(historial)
    db.commit()

    return {
        "mensaje": "Corrección administrativa aplicada correctamente",
        "salida_id": salida.id,
        "motivo": datos.motivo
    }
    
    
@router.patch("/{salida_id}/cancelacion")
def cancelar_salida(
    salida_id: int,
    datos: SalidaCancelacion,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    salida = db.query(Salida).filter(Salida.id == salida_id).first()
    
    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")
    
    if salida.estado == "cancelada":
        raise HTTPException(status_code=400, detail="La salida ya se encuentra cancelada")
    
    regreso = db.query(Regreso).filter(Regreso.salida_id == salida_id).first()
    
    if regreso is not None:
        raise HTTPException(status_code=400, detail="No se puede cancelar una salida que ya tiene regreso registrado")
    
    salida.estado = "cancelada"
    
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == salida.vehiculo_id).first()
    
    if vehiculo is not None and vehiculo.estado == "en_uso":
        otra_salida_activa = (
        db.query(Salida)
        .filter(
                Salida.vehiculo_id == vehiculo.id, 
                Salida.estado == "activa", 
                Salida.id != salida.id
            )
            .outerjoin(Regreso, Salida.id == Regreso.salida_id)
            .filter(Regreso.id == None)
            .first()
        )
        
        if otra_salida_activa is None:
            vehiculo.estado = "disponible"
            
    historial = HistorialSalida(
        salida_id=salida.id,
        usuario_id=usuario_actual.id,
        accion="cancelacion_salida",
        descripcion=f"Se canceló la salida: {datos.motivo}",
        fecha=datetime.now()
    )
    
    db.add(historial)
    db.commit()
    
    return {
        "mensaje": "Salida cancelada correctamente",
        "salida_id": salida.id,
        "motivo": datos.motivo
    }

    
    
@router.get("/{salida_id}/resguardo-preview")
def preview_resguardo(
    salida_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    salida = db.query(Salida).filter(Salida.id == salida_id).first()

    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == salida.vehiculo_id).first()
    persona = db.query(PersonaAutorizada).filter(PersonaAutorizada.id == salida.persona_id).first()
    regreso = db.query(Regreso).filter(Regreso.salida_id == salida.id).first()

    condiciones = db.query(RevisionCondicion, ItemCondicion).join(
        ItemCondicion,
        RevisionCondicion.item_condicion_id == ItemCondicion.id
    ).filter(
        RevisionCondicion.salida_id == salida.id
    ).all()

    inventario = db.query(RevisionInventario, ItemInventario).join(
        ItemInventario,
        RevisionInventario.item_id == ItemInventario.id
    ).filter(
        RevisionInventario.salida_id == salida.id
    ).all()

    return {
        "salida": salida,
        "regreso": regreso,
        "vehiculo": vehiculo,
        "persona": persona,
        "condiciones": [
            {
                "item": item.nombre,
                "estado": revision.estado,
                "observaciones": revision.observaciones
            }
            for revision, item in condiciones
        ],
        "inventario": [
            {
                "item": item.nombre,
                "categoria": item.categoria,
                "estado": revision.estado,
                "observaciones": revision.observaciones
            }
            for revision, item in inventario
        ]
    }
    
    
    
    
@router.post("/{salida_id}/resguardo")

def generar_resguardo(
    salida_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    salida = db.query(Salida).filter(Salida.id == salida_id).first()
    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")

    resguardo_existente = db.query(Resguardo).filter(
        Resguardo.salida_id == salida.id
    ).first()

    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id == salida.vehiculo_id
    ).first()

    persona = db.query(PersonaAutorizada).filter(
        PersonaAutorizada.id == salida.persona_id
    ).first()

    if vehiculo is None or persona is None:
        raise HTTPException(
            status_code=409,
            detail="La salida tiene referencias incompletas de vehículo o persona",
        )

    condiciones = db.query(
        RevisionCondicion,
        ItemCondicion
    ).join(
        ItemCondicion,
        RevisionCondicion.item_condicion_id == ItemCondicion.id
    ).filter(
        RevisionCondicion.salida_id == salida.id
    ).all()   

    inventario = db.query(
        RevisionInventario,
        ItemInventario
    ).join(
        ItemInventario,
        RevisionInventario.item_id == ItemInventario.id
    ).filter(
        RevisionInventario.salida_id == salida.id
    ).all()

    nombre_archivo, ruta_archivo = generar_resguardo_word(
        salida,
        vehiculo,
        persona,
        condiciones,
        inventario
    )

    if resguardo_existente:
        resguardo_existente.nombre_archivo = nombre_archivo
        resguardo_existente.ruta_archivo = ruta_archivo

        historial_resguardo = HistorialSalida(
            salida_id=salida.id,
            usuario_id=usuario_actual.id,
            accion="generacion_resguardo",
            descripcion=f"Se regeneró el resguardo: {nombre_archivo}",
            fecha=datetime.now()
        )

        db.add(historial_resguardo)
        db.commit()
        db.refresh(resguardo_existente)

        return {
            "mensaje": "Resguardo regenerado correctamente",
            "resguardo_id": resguardo_existente.id,
            "archivo": resguardo_existente.nombre_archivo
        }

    nuevo_resguardo = Resguardo(
        salida_id=salida.id,
        nombre_archivo=nombre_archivo,
        ruta_archivo=ruta_archivo
    )

    historial_resguardo = HistorialSalida(
        salida_id=salida.id,
        usuario_id=usuario_actual.id,
        accion="generacion_resguardo",
        descripcion=f"Se generó el resguardo: {nombre_archivo}",
        fecha=datetime.now()
    )

    db.add(nuevo_resguardo)
    db.add(historial_resguardo)
    db.commit()
    db.refresh(nuevo_resguardo)

    return {
        "mensaje": "Resguardo generado correctamente",
        "resguardo_id": nuevo_resguardo.id,
        "archivo": nuevo_resguardo.nombre_archivo
    }
    
    
    

    
    
    
@router.get("/{salida_id}/resguardo")
def descargar_resguardo(
    salida_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    resguardo = db.query(Resguardo).filter(
        Resguardo.salida_id == salida_id
    ).first()

    if resguardo is None:
        raise HTTPException(
            status_code=404,
            detail="No existe resguardo generado para esta salida"
        )

    if not resguardo.ruta_archivo or not os.path.exists(resguardo.ruta_archivo):
        raise HTTPException(
            status_code=404,
            detail="El archivo del resguardo no existe en el servidor"
        )

    return FileResponse(
        path=resguardo.ruta_archivo,
        filename=resguardo.nombre_archivo,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    
    
    
@router.get("/{salida_id}/condicion")
def obtener_condicion_salida(
    salida_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    salida = db.query(Salida).filter(Salida.id == salida_id).first()

    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")

    items = db.query(ItemCondicion).filter(
        ItemCondicion.activo == True
    ).order_by(ItemCondicion.id).all()

    revisiones = db.query(RevisionCondicion).filter(
        RevisionCondicion.salida_id == salida_id
    ).all()

    revisiones_por_item = {
        revision.item_condicion_id: revision
        for revision in revisiones
    }

    return [
        {
            "revision_id": revisiones_por_item[item.id].id if item.id in revisiones_por_item else None,
            "item_condicion_id": item.id,
            "nombre": item.nombre,
            "estado": revisiones_por_item[item.id].estado if item.id in revisiones_por_item else item.estado_default,
            "observaciones": revisiones_por_item[item.id].observaciones if item.id in revisiones_por_item else None
        }
        for item in items
    ]
    
    
    
@router.put("/{salida_id}/condicion")
def actualizar_condicion_salida(
    salida_id: int,
    datos: CondicionUpdateRequest,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    salida = db.query(Salida).filter(Salida.id == salida_id).first()

    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")

    estados_permitidos = ["bueno", "regular", "malo"]

    ids_validos = {fila.id for fila in db.query(ItemCondicion.id).all()}
    for item in datos.condiciones:
        if item.item_condicion_id not in ids_validos:
            raise HTTPException(status_code=400, detail="El elemento de condición no existe")
        if item.estado not in estados_permitidos:
            raise HTTPException(
                status_code=400,
                detail=f"Estado no válido para condición: {item.estado}"
            )

        revision = db.query(RevisionCondicion).filter(
            RevisionCondicion.salida_id == salida_id,
            RevisionCondicion.item_condicion_id == item.item_condicion_id
        ).first()

        if revision is None:
            revision = RevisionCondicion(
                salida_id=salida_id,
                item_condicion_id=item.item_condicion_id,
                estado=item.estado,
                observaciones=item.observaciones
            )
            db.add(revision)
        else:
            revision.estado = item.estado
            revision.observaciones = item.observaciones

    db.commit()

    return {
        "mensaje": "Condiciones actualizadas correctamente",
        "salida_id": salida_id
    }
    
    
    
@router.get("/{salida_id}/inventario")
def obtener_inventario_salida(
    salida_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    salida = db.query(Salida).filter(Salida.id == salida_id).first()

    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")

    items = db.query(ItemInventario).filter(
        ItemInventario.activo == True
    ).order_by(ItemInventario.id).all()

    revisiones = db.query(RevisionInventario).filter(
        RevisionInventario.salida_id == salida_id
    ).all()

    revisiones_por_item = {
        revision.item_id: revision
        for revision in revisiones
    }

    return [
        {
            "revision_id": revisiones_por_item[item.id].id if item.id in revisiones_por_item else None,
            "item_id": item.id,
            "nombre": item.nombre,
            "categoria": item.categoria,
            "estado": revisiones_por_item[item.id].estado if item.id in revisiones_por_item else item.estado_default,
            "observaciones": revisiones_por_item[item.id].observaciones if item.id in revisiones_por_item else None
        }
        for item in items
    ]
    
    
    
@router.put("/{salida_id}/inventario")
def actualizar_inventario_salida(
    salida_id: int,
    datos: InventarioUpdateRequest,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    salida = db.query(Salida).filter(Salida.id == salida_id).first()

    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")

    estados_permitidos = ["correcto", "na", "vacio"]  

    ids_validos = {fila.id for fila in db.query(ItemInventario.id).all()}
    for item in datos.inventario:
        if item.item_id not in ids_validos:
            raise HTTPException(status_code=400, detail="El elemento de inventario no existe")
        estado_normalizado = item.estado.lower().strip()

        if estado_normalizado not in estados_permitidos:
            raise HTTPException(
                status_code=400,
                detail=f"Estado no válido para inventario: {item.estado}"
            )

        revision = db.query(RevisionInventario).filter(
            RevisionInventario.salida_id == salida_id,
            RevisionInventario.item_id == item.item_id
        ).first()

        if revision is None:
            revision = RevisionInventario(
                salida_id=salida_id,
                item_id=item.item_id,
                estado=estado_normalizado,
                observaciones=item.observaciones
            )
            db.add(revision)
        else:
            revision.estado = estado_normalizado
            revision.observaciones = item.observaciones

    db.commit()

    return {
        "mensaje": "Inventario actualizado correctamente",
        "salida_id": salida_id
    }