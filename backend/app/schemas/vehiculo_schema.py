from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

class VehiculoCreate(BaseModel):
    num_economico: Optional[str] = None
    placa: str
    marca: str
    tipo: str
    modelo_anio: int
    cilindros: int
    num_serie: str
    num_motor: Optional[str] = None
    num_poliza: Optional[str] = None
    num_inventario: Optional[str] = None
    color: str
    num_tarjeta_gasolina: Optional[str] = None
    km_acumulado: Decimal = 0
    estado: str = "disponible"

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
    
class VehiculoEstadoUpdate(BaseModel):
    estado: str

    class Config:
        from_attributes = True
        
        
class VehiculoUpdate(BaseModel):
    placa: str
    marca: str
    tipo: str
    modelo_anio: int
    cilindros: int
    num_serie: str
    num_motor: Optional[str] = None
    num_poliza: Optional[str] = None
    num_inventario: Optional[str] = None
    color: str
    num_tarjeta_gasolina: Optional[str] = None
    km_acumulado: Decimal