from pydantic import BaseModel

class ItemInventarioResponse(BaseModel):
    id: int
    nombre: str
    categoria: str
    estado_default: str
    activo: bool

    class Config:
        from_attributes = True