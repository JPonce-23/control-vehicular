from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional

class GastoGasolinaResponse(BaseModel):
    id: int
    vehiculo_id: int
    salida_id: int
    presupuesto_id: int
    fecha_gasto: date
    litros: Decimal
    monto: Decimal
    nota: Optional[str]

    class Config:
        from_attributes = True