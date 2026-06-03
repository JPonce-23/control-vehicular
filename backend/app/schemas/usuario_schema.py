from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    num_empleado: str
    correo: str
    rol: str
    estado: str
    fecha_alta: datetime
    ultimo_acceso: Optional[datetime]
    
class LoginRequest(BaseModel):
    correo: str
    password: str

    class Config:
        from_attributes = True
        
class UsuarioCreate(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    num_empleado: str
    correo: str
    password: str
    rol: str = "capturista"
    estado: str = "activo"
    
class UsuarioRolUpdate(BaseModel):
    rol: str