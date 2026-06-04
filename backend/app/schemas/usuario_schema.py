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
    
class UsuarioRolUpdate(BaseModel):
    rol: str
    
class UsuarioEstadoUpdate(BaseModel):
    estado: str
    
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    num_empleado: Optional[str] = None
    correo: Optional[str] = None
    
    
class RecuperarPasswordRequest(BaseModel):
    correo: str

class ResetPasswordRequest(BaseModel):
    correo: str
    token: str
    nueva_password: str
    
class CambiarPasswordRequest(BaseModel):
    password_actual: str
    nueva_password: str
    
    