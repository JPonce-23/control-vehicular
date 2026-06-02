from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.regreso_model import Regreso
from app.schemas.regreso_schema import RegresoResponse, RegresoCreate
from app.models.salida_model import Salida
from app.models.vehiculo_model import Vehiculo

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

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == salida.vehiculo_id).first()

    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    datos_regreso = regreso.model_dump(exclude_none=True)
    nuevo_regreso = Regreso(**datos_regreso)

    vehiculo.estado = "disponible"
    


    db.add(nuevo_regreso)
    db.commit()
    db.refresh(nuevo_regreso)

    return nuevo_regreso