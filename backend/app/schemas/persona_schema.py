from pydantic import BaseModel
from datetime import date
from typing import Optional

class PersonaCreate(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    num_licencia: str
    rfc: Optional[str] = None
    vigencia_licencia: date
    tipo_licencia: str
    estado: str = "activo"

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

class PersonaEstadoUpdate(BaseModel):
    estado: str

    class Config:
        from_attributes = True