from sqlalchemy import Column, Integer, DateTime, Text, Numeric, ForeignKey, String, Enum
from app.database import Base
from sqlalchemy import func

class Regreso(Base):
    __tablename__ = "regreso"

    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salida.id"))
    capturado_por = Column(Integer, ForeignKey("usuario_sistema.id"))
    fecha_regreso = Column(DateTime, nullable=False)
    km_odometro_regreso = Column(Numeric)
    nivel_gasolina_regreso = Column(String)
    saldo_tarjeta_antes_regreso = Column(Numeric(10, 2), nullable=True)
    saldo_tarjeta_regreso = Column(Numeric(10, 2), nullable=True)
    monto_gastado_tarjeta = Column(Numeric(10, 2), nullable=True)
    estado_llantas_regreso = Column(String)
    estado_vehiculo_regreso = Column(String)
    finalidad_devolucion = Column(String)
    observaciones = Column(Text)
    