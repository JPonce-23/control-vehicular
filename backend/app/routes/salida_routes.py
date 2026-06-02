from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.salida_model import Salida
from app.schemas.salida_schema import SalidaResponse, SalidaCreate
from app.models.vehiculo_model import Vehiculo

router = APIRouter(
    prefix="/salidas",
    tags=["Salidas"]
)

@router.get("/", response_model=list[SalidaResponse])
def listar_salidas(db: Session = Depends(get_db)):
    return db.query(Salida).all()

@router.post("/", response_model=SalidaResponse)
def crear_salida(salida: SalidaCreate, db: Session = Depends(get_db)):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == salida.vehiculo_id).first()

    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    if vehiculo.estado != "disponible":
        raise HTTPException(
            status_code=400,
            detail="El vehículo no está disponible para salida"
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

    db.add(nueva_salida)
    db.commit()
    db.refresh(nueva_salida)

    return nueva_salida