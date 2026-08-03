from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class AjusteCreate(BaseModel):
    vehiculo_id: int
    km_nuevo: Decimal
    motivo: Optional[str] = None


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
