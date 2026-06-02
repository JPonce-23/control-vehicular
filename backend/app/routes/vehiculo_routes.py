from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.vehiculo_model import Vehiculo
from app.schemas.vehiculo_schema import VehiculoResponse, VehiculoCreate

router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehículos"]
)

@router.get("/", response_model=list[VehiculoResponse])
def listar_vehiculos(db: Session = Depends(get_db)):
    return db.query(Vehiculo).all()

@router.post("/", response_model=VehiculoResponse)
def crear_vehiculo(vehiculo: VehiculoCreate, db: Session = Depends(get_db)):
    nuevo_vehiculo = Vehiculo(**vehiculo.model_dump())
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo