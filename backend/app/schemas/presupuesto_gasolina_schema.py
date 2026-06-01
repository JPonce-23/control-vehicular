from pydantic import BaseModel
from decimal import Decimal

class PresupuestoGasolinaResponse(BaseModel):
    id: int
    vehiculo_id: int
    monto_autorizado_total: Decimal
    monto_por_mes: Decimal
    monto_utilizado: Decimal
    saldo_acumulado: Decimal
    anio: int

    class Config:
        from_attributes = True