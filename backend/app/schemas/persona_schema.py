from pydantic import BaseModel
from datetime import date
from typing import Optional

class PersonaResponse(BaseModel):
    id: int
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    num_licencia: str
    rfc: Optional[str]
    vigencia_licencia: date
    tipo_licencia: str
    estado: str

    class Config:
        from_attributes = True