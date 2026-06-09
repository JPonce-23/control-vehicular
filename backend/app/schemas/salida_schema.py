from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

class SalidaCreate(BaseModel):
    vehiculo_id: int
    persona_id: int
    capturado_por: int
    fecha_salida: Optional[datetime] = None
    num_oficio: Optional[str] = None
    num_expediente: Optional[str] = None
    cargo_en_viaje: str
    area_en_viaje: str
    tipo_movimiento: str
    forma_movimiento: str
    fecha_fin_provisional: Optional[date] = None
    finalidad_uso: str
    km_odometro_salida: Decimal
    nivel_gasolina_salida: str
    estado_llantas_salida: str
    observaciones: Optional[str] = None
    observaciones_croquis: Optional[str] = None

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
        
class SalidaUpdate(BaseModel):
    num_oficio: Optional[str] = None
    num_expediente: Optional[str] = None
    cargo_en_viaje: Optional[str] = None
    area_en_viaje: Optional[str] = None
    tipo_movimiento: Optional[str] = None
    forma_movimiento: Optional[str] = None
    fecha_fin_provisional: Optional[date] = None
    finalidad_uso: Optional[str] = None
    km_odometro_salida: Optional[Decimal] = None
    nivel_gasolina_salida: Optional[str] = None
    estado_llantas_salida: Optional[str] = None
    observaciones: Optional[str] = None
    observaciones_croquis: Optional[str] = None
    
    
class SalidaCorreccionAdministrativa(BaseModel):
    motivo: str

    km_odometro_salida: Optional[Decimal] = None
    km_odometro_regreso: Optional[Decimal] = None

    nivel_gasolina_salida: Optional[str] = None
    nivel_gasolina_regreso: Optional[str] = None

    estado_llantas_salida: Optional[str] = None
    estado_llantas_regreso: Optional[str] = None

    estado_vehiculo_regreso: Optional[str] = None

    finalidad_uso: Optional[str] = None
    finalidad_devolucion: Optional[str] = None

    observaciones_salida: Optional[str] = None
    observaciones_regreso: Optional[str] = None
    
class CondicionUpdateItem(BaseModel):
    item_condicion_id: int
    estado: str
    observaciones: Optional[str] = None


class CondicionUpdateRequest(BaseModel):
    condiciones: list[CondicionUpdateItem]
    
class InventarioUpdateItem(BaseModel):
    item_id: int
    estado: str
    observaciones: Optional[str] = None


class InventarioUpdateRequest(BaseModel):
    inventario: list[InventarioUpdateItem]