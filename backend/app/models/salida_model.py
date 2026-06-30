from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Numeric, ForeignKey, func

from app.database import Base

class Salida(Base):
    __tablename__ = "salida"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculo.id"))
    persona_id = Column(Integer, ForeignKey("persona_autorizada.id"))
    capturado_por = Column(Integer, ForeignKey("usuario_sistema.id"))
    fecha_salida = Column(DateTime, nullable=False, server_default=func.now())
    num_oficio = Column(String)
    num_expediente = Column(String)
    area_en_viaje = Column(String)
    tipo_movimiento = Column(String)
    forma_movimiento = Column(String)
    fecha_fin_provisional = Column(Date)
    fecha_regreso_estimada = Column(Date, nullable=True)
    finalidad_uso = Column(Text)
    km_odometro_salida = Column(Numeric)
    nivel_gasolina_salida = Column(String)
    estado_llantas_salida = Column(String)
    observaciones = Column(Text)
    observaciones_croquis = Column(Text)