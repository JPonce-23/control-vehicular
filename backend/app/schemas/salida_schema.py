from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

class SalidaResponse(BaseModel):
    id: int
    vehiculo_id: int
    persona_id: int
    capturado_por: int
    fecha_salida: datetime
    num_oficio: Optional[str]
    num_expediente: Optional[str]
    cargo_en_viaje: str
    area_en_viaje: str
    tipo_movimiento: str
    forma_movimiento: str
    fecha_fin_provisional: Optional[date]
    finalidad_uso: str
    km_odometro_salida: Decimal
    nivel_gasolina_salida: str
    estado_llantas_salida: str
    observaciones: Optional[str]
    observaciones_croquis: Optional[str]

    class Config:
        from_attributes = True