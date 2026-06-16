from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.salida_model import Salida
from app.schemas.salida_schema import SalidaResponse, SalidaCreate, SalidaUpdate, SalidaCorreccionAdministrativa, CondicionUpdateRequest, InventarioUpdateRequest
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

@router.get("/", response_model=list[SalidaResponse])
def listar_salidas(db: Session = Depends(get_db)):
    return db.query(Salida).all()

@router.post("/", response_model=SalidaResponse)
def crear_salida(
    salida: SalidaCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador", "capturista"]))
):
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

    if persona.vigencia_licencia is not None and persona.vigencia_licencia < date.today():
        raise HTTPException(
            status_code=400,
            detail="La licencia del conductor está vencida"
    )

    datos_salida = salida.model_dump(exclude_none=True)

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
        descripcion="Se registró una nueva salida",
        fecha=date.today()
    )

    db.add(historial)
    db.commit()
    db.refresh(nueva_salida)

    return nueva_salida


@router.get("/{salida_id}", response_model=SalidaResponse)
def obtener_salida_por_id(
    salida_id: int,
    db: Session = Depends(get_db)
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



@router.get("/activas/", response_model=list[SalidaResponse])
def listar_salidas_activas(
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    salidas = db.query(Salida).outerjoin(
        Regreso, Salida.id == Regreso.salida_id
    ).filter(
        Regreso.id == None
    ).all()

    return salidas



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

    if resguardo_existente and os.path.exists(resguardo_existente.ruta_archivo):
        os.remove(resguardo_existente.ruta_archivo)

    datos_actualizar = datos.model_dump(exclude_unset=True)

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

    if datos.observaciones_salida is not None:
        salida.observaciones = datos.observaciones_salida

    if datos.observaciones_regreso is not None:
        regreso.observaciones = datos.observaciones_regreso

    historial = HistorialSalida(
        salida_id=salida.id,
        usuario_id=usuario_actual.id,
        accion="modificacion",
        descripcion=f"Corrección administrativa: {datos.motivo}",
        fecha=date.today()
    )

    db.add(historial)
    db.commit()

    return {
        "mensaje": "Corrección administrativa aplicada correctamente",
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
        raise HTTPException(
            status_code=404,
            detail="Salida no encontrada"
        )

    regreso = db.query(Regreso).filter(
        Regreso.salida_id == salida.id
    ).first()

    if regreso is None:
        raise HTTPException(
            status_code=400,
            detail="No se puede generar el resguardo sin registrar el regreso"
        )

    resguardo_existente = db.query(Resguardo).filter(
        Resguardo.salida_id == salida.id
    ).first()

    if resguardo_existente and os.path.exists(resguardo_existente.ruta_archivo):
        os.remove(resguardo_existente.ruta_archivo)

    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id == salida.vehiculo_id
    ).first()

    persona = db.query(PersonaAutorizada).filter(
        PersonaAutorizada.id == salida.persona_id
    ).first()

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
        regreso,
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
            "archivo": resguardo_existente.nombre_archivo,
            "ruta": resguardo_existente.ruta_archivo
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
        "archivo": nuevo_resguardo.nombre_archivo,
        "ruta": nuevo_resguardo.ruta_archivo
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

    if not os.path.exists(resguardo.ruta_archivo):
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

    for item in datos.condiciones:
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

    for item in datos.inventario:
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