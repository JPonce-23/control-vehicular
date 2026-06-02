from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.regreso_model import Regreso
from app.schemas.regreso_schema import RegresoResponse, RegresoCreate
from app.models.salida_model import Salida
from app.models.vehiculo_model import Vehiculo
from app.models.historial_salida_model import HistorialSalida

router = APIRouter(
    prefix="/regresos",
    tags=["Regresos"]
)

@router.get("/", response_model=list[RegresoResponse])
def listar_regresos(db: Session = Depends(get_db)):
    return db.query(Regreso).all()

@router.post("/", response_model=RegresoResponse)
def crear_regreso(regreso: RegresoCreate, db: Session = Depends(get_db)):
    salida = db.query(Salida).filter(Salida.id == regreso.salida_id).first()

    if salida is None:
        raise HTTPException(status_code=404, detail="Salida no encontrada")
    
    regreso_existente = db.query(Regreso).filter(
    Regreso.salida_id == regreso.salida_id
    ).first()

    if regreso_existente:
        raise HTTPException(
        status_code=400,
        detail="Esta salida ya tiene un regreso registrado"
    )
        
    if regreso.km_odometro_regreso < salida.km_odometro_salida:
        raise HTTPException(
        status_code=400,
        detail="El kilometraje de regreso no puede ser menor al de salida"
    )

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == salida.vehiculo_id).first()

    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    

    datos_regreso = regreso.model_dump(exclude_none=True)
    nuevo_regreso = Regreso(**datos_regreso)

    vehiculo.estado = "disponible"
    
    vehiculo.km_acumulado = regreso.km_odometro_regreso

    db.add(nuevo_regreso)
    db.flush()

    historial = HistorialSalida(
        salida_id=regreso.salida_id,
        usuario_id=regreso.capturado_por,
        accion="registro_regreso",
        descripcion="Se registró el regreso del vehículo",
        fecha=date.today()
    )

    db.add(historial)
    db.commit()
    db.refresh(nuevo_regreso)

    return nuevo_regreso