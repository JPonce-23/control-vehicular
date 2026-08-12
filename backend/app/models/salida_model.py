from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func

from app.database import Base


class Salida(Base):
    __tablename__ = "salida"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculo.id"), nullable=False)
    persona_id = Column(Integer, ForeignKey("persona_autorizada.id"), nullable=False)
    capturado_por = Column(Integer, ForeignKey("usuario_sistema.id"), nullable=False)
    fecha_salida = Column(DateTime, nullable=False, server_default=func.now())
    num_oficio = Column(String(100), nullable=True)
    num_expediente = Column(String(100), nullable=True)
    area_en_viaje = Column(String(100), nullable=True)
    cargo_en_viaje = Column(String(150), nullable=True)
    tipo_movimiento = Column(String, nullable=False)
    forma_movimiento = Column(String, nullable=False, default="provisional")
    fecha_fin_provisional = Column(Date, nullable=True)
    fecha_regreso_estimada = Column(Date, nullable=True)
    finalidad_uso = Column(Text, nullable=False)
    km_odometro_salida = Column(Numeric(12, 2), nullable=False)
    nivel_gasolina_salida = Column(String, nullable=False)
    estado_llantas_salida = Column(String, nullable=False)
    observaciones = Column(Text, nullable=True)
    observaciones_croquis = Column(Text, nullable=True)
    monto_agregado_tarjeta = Column(Numeric(12, 2), nullable=False, default=0)
    saldo_tarjeta_salida = Column(Numeric(12, 2), nullable=False, default=0)
    estado = Column(String, nullable=False, default="activa", server_default="'activa'")
