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