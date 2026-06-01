from pydantic import BaseModel
from typing import Optional

class RevisionCondicionResponse(BaseModel):
    id: int
    salida_id: int
    item_condicion_id: int
    estado: str
    observaciones: Optional[str]

    class Config:
        from_attributes = True