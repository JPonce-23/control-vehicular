from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ResguardoResponse(BaseModel):
    id: int
    salida_id: int
    fecha_generacion: datetime
    nombre_archivo: str
    ruta_archivo: Optional[str]

    class Config:
        from_attributes = True