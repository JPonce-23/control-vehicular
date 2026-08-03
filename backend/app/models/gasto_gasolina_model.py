import enum

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, Text
from sqlalchemy.sql import func

from app.database import Base


class NivelGasolinaEnum(enum.Enum):
    vacio = "vacio"
    cuarto = "cuarto"
    medio = "medio"
    tres_cuartos = "tres_cuartos"
    lleno = "lleno"


class GastoGasolina(Base):
    __tablename__ = "gasto_gasolina"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculo.id"), nullable=False)
    salida_id = Column(Integer, ForeignKey("salida.id"), nullable=False)
    presupuesto_id = Column(Integer, ForeignKey("presupuesto_gasolina.id"), nullable=False)
    fecha_gasto = Column(Date, nullable=False)
    litros = Column(Numeric(10, 2), nullable=True)
    monto = Column(Numeric(12, 2), nullable=False)
    nivel_tanque = Column(Enum(NivelGasolinaEnum, name="nivel_gasolina_salida", create_type=False), nullable=True)
    km_odometro = Column(Numeric(12, 2), nullable=True)
    nota = Column(Text, nullable=True)
    capturado_por = Column(Integer, ForeignKey("usuario_sistema.id"), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)
