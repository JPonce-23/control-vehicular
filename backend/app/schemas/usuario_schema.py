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

    class Config:
        from_attributes = True