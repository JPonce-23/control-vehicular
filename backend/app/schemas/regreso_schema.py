from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional

class RegresoCreate(BaseModel):
    salida_id: int
    fecha_regreso: Optional[datetime] = None
    km_odometro_regreso: Decimal
    nivel_gasolina_regreso: str
    saldo_tarjeta_regreso: Decimal
    estado_llantas_regreso: str
    estado_vehiculo_regreso: str
    finalidad_devolucion: str
    observaciones: Optional[str] = None
    

class RegresoResponse(BaseModel):
    id: int
    salida_id: int
    capturado_por: int
    fecha_regreso: datetime
    km_odometro_regreso: Decimal
    nivel_gasolina_regreso: str
    saldo_tarjeta_antes_regreso: Optional[Decimal] = None
    saldo_tarjeta_regreso: Optional[Decimal] = None
    monto_gastado_tarjeta: Optional[Decimal] = None
    estado_llantas_regreso: str
    estado_vehiculo_regreso: str
    finalidad_devolucion: str
    observaciones: Optional[str]

    class Config:
        from_attributes = True