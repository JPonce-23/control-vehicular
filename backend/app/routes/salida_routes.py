from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.salida_model import Salida
from app.schemas.salida_schema import SalidaResponse, SalidaCreate
from app.models.vehiculo_model import Vehiculo
from app.models.historial_salida_model import HistorialSalida
from app.models.persona_model import PersonaAutorizada
from app.services.auth_service import obtener_usuario_actual, requerir_rol

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