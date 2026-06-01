from pydantic import BaseModel
from datetime import datetime

class TokenAccesoResponse(BaseModel):
    id: int
    usuario_id: int
    token: str
    tipo: str
    fecha_expiracion: datetime
    usado: bool

    class Config:
        from_attributes = True