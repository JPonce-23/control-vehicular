from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.salida_model import Salida
from app.schemas.salida_schema import SalidaResponse, SalidaCreate, SalidaUpdate, SalidaCorreccionAdministrativa
from app.models.vehiculo_model import Vehiculo
from app.models.historial_salida_model import HistorialSalida
from app.models.persona_model import PersonaAutorizada
from app.services.auth_service import obtener_usuario_actual, requerir_rol
from app.models.regreso_model import Regreso
from app.models.resguardo_model import Resguardo

router = APIRouter(
    prefix="/salidas",
    tags=["Salidas"]
)

@router.get("/", response_model=list[SalidaResponse])
def listar_salidas(db: Session = Depends(get_db)):
    return db.query(Salida).all()

@router.post("/", response_model=SalidaResponse)
def crear_salida(salida: SalidaCreate, 
db: Session = Depends(get_db), 
usuario_actual = Depends(requerir_rol(["administrador", "capturista"]))
):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == salida.vehiculo_id).first()
    

    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    if vehiculo.estado != "disponible":
        raise HTTPException(
            status_code=400,
            detail="El vehículo no está disponible para salida"
        )
        
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

    datos_salida = salida.model_dump(exclude_none=True)
    nueva_salida = Salida(**datos_salida)

    vehiculo.estado = "en_uso"
    
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

    if persona.vigencia_licencia < date.today():
        raise HTTPException(
        status_code=400,
        detail="La licencia del conductor está vencida"
    )
    
    db.add(nueva_salida)
    db.flush()

    historial = HistorialSalida (
        salida_id=nueva_salida.id,
        usuario_id=salida.capturado_por,
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

    if resguardo_existente:
        raise HTTPException(
            status_code=400,
            detail="No se puede editar una salida que ya tiene resguardo generado"
        )

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