from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class VehiculoResponse(BaseModel):
    id: int
    num_economico: Optional[str]
    placa: str
    marca: str
    tipo: str
    modelo_anio: int
    cilindros: int
    num_serie: str
    num_motor: Optional[str]
    num_poliza: Optional[str]
    num_inventario: Optional[str]
    color: str
    num_tarjeta_gasolina: Optional[str]
    km_acumulado: Decimal
    estado: str

    class Config:
        from_attributes = True