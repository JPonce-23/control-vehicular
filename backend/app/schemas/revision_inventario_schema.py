from pydantic import BaseModel
from typing import Optional

class RevisionInventarioResponse(BaseModel):
    id: int
    salida_id: int
    item_id: int
    estado: str
    observaciones: Optional[str]

    class Config:
        from_attributes = True