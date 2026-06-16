from pydantic import BaseModel
from datetime import date
from typing import Optional


class PersonaCreate(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    cargo: str
    num_licencia: Optional[str] = None
    rfc: Optional[str] = None
    vigencia_licencia: Optional[date] = None
    tipo_licencia: Optional[str] = None
    estado: str = "activo"


class PersonaUpdate(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    cargo: str
    num_licencia: Optional[str] = None
    rfc: Optional[str] = None
    vigencia_licencia: Optional[date] = None
    tipo_licencia: Optional[str] = None


class PersonaResponse(BaseModel):
    id: int
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    cargo: str
    num_licencia: Optional[str]
    rfc: Optional[str]
    vigencia_licencia: Optional[date]
    tipo_licencia: Optional[str]
    estado: str

    class Config:
        from_attributes = True


class PersonaEstadoUpdate(BaseModel):
    estado: str