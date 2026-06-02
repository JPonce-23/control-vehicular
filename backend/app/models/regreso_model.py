from sqlalchemy import Column, Integer, DateTime, Text, Numeric, ForeignKey, String
from app.database import Base
from sqlalchemy import func

class Regreso(Base):
    __tablename__ = "regreso"

    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salida.id"))
    capturado_por = Column(Integer, ForeignKey("usuario_sistema.id"))
    fecha_regreso = Column(DateTime, nullable=False, server_default=func.now())
    km_odometro_regreso = Column(Numeric)
    nivel_gasolina_regreso = Column(String)
    estado_llantas_regreso = Column(String)
    estado_vehiculo_regreso = Column(String)
    finalidad_devolucion = Column(String)
    observaciones = Column(Text)