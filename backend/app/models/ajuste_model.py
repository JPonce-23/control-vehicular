from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, Text, func

from app.database import Base


class AjusteOdometro(Base):
    __tablename__ = "ajuste_odometro"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculo.id"), nullable=False)
    fecha_ajuste = Column(DateTime, nullable=False, server_default=func.now())
    km_anterior = Column(Numeric(12, 2), nullable=False)
    km_nuevo = Column(Numeric(12, 2), nullable=False)
    motivo = Column(Text, nullable=True)
    realizado_por = Column(Integer, ForeignKey("usuario_sistema.id"), nullable=False)
