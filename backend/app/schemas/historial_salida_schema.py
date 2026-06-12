from pydantic import BaseModel
from datetime import date
from typing import Optional
from datetime import datetime

class HistorialSalidaResponse(BaseModel):
    id: int
    salida_id: int
    usuario_id: int
    accion: str
    descripcion: Optional[str]
    fecha: datetime

    class Config:
        from_attributes = True
        
        
from pydantic import BaseModel
from typing import Optional
from datetime import date


class HistorialAuditoriaResponse(BaseModel):
    id: int
    salida_id: int
    usuario_id: Optional[int] = None
    usuario_correo: Optional[str] = None
    usuario_nombre: Optional[str] = None
    accion: str
    descripcion: Optional[str] = None
    fecha: date

    class Config:
        from_attributes = True
        
        
        
from pydantic import BaseModel
from typing import Optional


class HistorialAuditoriaVehiculoResponse(BaseModel):
    salida_id: int
    vehiculo_id: int
    vehiculo: Optional[str] = None
    placa: Optional[str] = None
    persona: Optional[str] = None
    fecha_salida: Optional[str] = None
    fecha_regreso: Optional[str] = None
    accion: str
    descripcion: Optional[str] = None
    fecha_movimiento: Optional[str] = None
    usuario_id: Optional[int] = None
    usuario: Optional[str] = None

    class Config:
        from_attributes = True