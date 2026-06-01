from pydantic import BaseModel

class ItemCondicionResponse(BaseModel):
    id: int
    nombre: str
    estado_default: str
    activo: bool

    class Config:
        from_attributes = True