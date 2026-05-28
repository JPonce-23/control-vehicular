from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional

class AjusteResponse(BaseModel):
    id: int
    vehiculo_id: int
    fecha_ajuste: datetime
    km_anterior: Decimal
    km_nuevo: Decimal
    motivo: Optional[str]
    realizado_por: int

    class Config:
        from_attributes = True