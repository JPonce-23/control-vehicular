from sqlalchemy import Column, Integer, DateTime, Numeric, Text, ForeignKey, func
from app.database import Base

class AjusteOdometro(Base):
    __tablename__ = "ajuste_odometro"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculo.id"))
    fecha_ajuste = Column(DateTime, nullable=False, server_default=func.now())
    km_anterior = Column(Numeric)
    km_nuevo = Column(Numeric)
    motivo = Column(Text)
    realizado_por = Column(Integer, ForeignKey("usuario_sistema.id"))