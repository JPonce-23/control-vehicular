from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# ─── Presupuesto ────────────────────────────────────────────

class PresupuestoCrear(BaseModel):
    monto_autorizado_total: Decimal
    anio: int
    mes_inicio: int = 1
    mes_fin: int = 12

    @field_validator("monto_autorizado_total")
    @classmethod
    def monto_positivo(cls, v):
        if v <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        return v

    @field_validator("anio")
    @classmethod
    def anio_valido(cls, v):
        if v < 2000 or v > 2100:
            raise ValueError("El año no es válido")
        return v

    @field_validator("mes_fin")
    @classmethod
    def mes_fin_valido(cls, v):
        if v < 1 or v > 12:
            raise ValueError("El mes fin debe estar entre 1 y 12")
        return v

    @field_validator("mes_inicio")
    @classmethod
    def mes_inicio_valido(cls, v):
        if v < 1 or v > 12:
            raise ValueError("El mes inicio debe estar entre 1 y 12")
        return v
    

class PresupuestoRespuesta(BaseModel):
    presupuesto_id: int
    vehiculo_id: int
    anio: int
    mes_inicio: int
    mes_fin: int
    monto_autorizado_total: Decimal
    monto_por_mes: Decimal
    monto_utilizado: Decimal
    monto_restante: Decimal
    porcentaje_restante: float

    model_config = {"from_attributes": True}

# ─── Gasto ──────────────────────────────────────────────────

class GastoCrear(BaseModel):
    salida_id: int
    fecha_gasto: date
    monto: Decimal
    nivel_tanque: Optional[str] = None
    km_odometro: Optional[Decimal] = None
    nota: Optional[str] = None

    @field_validator("monto")
    @classmethod
    def monto_positivo(cls, v):
        if v <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        return v

class GastoRespuesta(BaseModel):
    id: int
    vehiculo_id: int
    salida_id: Optional[int]
    presupuesto_id: int
    fecha_gasto: date
    monto: Decimal
    nivel_tanque: Optional[str]
    km_odometro: Optional[Decimal]
    nota: Optional[str]
    capturado_por: Optional[int]
    fecha_registro: datetime

    model_config = {"from_attributes": True}

# ─── Resumen del mes (panel lateral del mockup) ─────────────

class ResumenMes(BaseModel):
    monto_autorizado_mes: Decimal
    gasto_mes: Decimal
    monto_restante: Decimal
    porcentaje_restante: float

# ─── Reporte mensual para gráficas ──────────────────────────

class ReporteMes(BaseModel):
    mes_numero: int
    mes: str
    monto_autorizado_mes: Decimal
    gasto_mes: Decimal
    monto_restante_mes: Decimal
    gasto_acumulado: Decimal
    monto_restante_total: Decimal

class ReporteCombustible(BaseModel):
    vehiculo_id: int
    anio: int
    reporte: list[ReporteMes]

# ─── Viajes ─────────────────────────────────────────────────

class ViajeRespuesta(BaseModel):
    salida_id: int
    vehiculo_id: int
    persona: str
    fecha_salida: datetime
    fecha_regreso: Optional[datetime]
    km_salida: Optional[Decimal]
    km_regreso: Optional[Decimal]
    kilometros_recorridos: Optional[Decimal]
    finalidad_uso: Optional[str]
    finalidad_devolucion: Optional[str]

    model_config = {"from_attributes": True}