from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func

from app.database import Base


class Regreso(Base):
    __tablename__ = "regreso"

    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salida.id"), nullable=False, unique=True)
    capturado_por = Column(Integer, ForeignKey("usuario_sistema.id"), nullable=False)
    fecha_regreso = Column(DateTime, nullable=False, server_default=func.now())
    km_odometro_regreso = Column(Numeric(10, 2), nullable=False)
    nivel_gasolina_regreso = Column(String, nullable=False)
    saldo_tarjeta_antes_regreso = Column(Numeric(10, 2), nullable=True)
    saldo_tarjeta_regreso = Column(Numeric(10, 2), nullable=True)
    monto_gastado_tarjeta = Column(Numeric(10, 2), nullable=True)
    estado_llantas_regreso = Column(String, nullable=False)
    estado_vehiculo_regreso = Column(String, nullable=False)
    finalidad_devolucion = Column(String, nullable=False)
    observaciones = Column(Text, nullable=True)
