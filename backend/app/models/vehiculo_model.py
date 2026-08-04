from sqlalchemy import Column, Integer, Numeric, String

from app.database import Base


class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id = Column(Integer, primary_key=True, index=True)
    num_economico = Column(String(50), unique=True, nullable=True)
    placa = Column(String(20), unique=True, nullable=False)
    marca = Column(String(50), nullable=False)
    tipo = Column(String(50), nullable=False)
    modelo_anio = Column(Integer, nullable=False)
    cilindros = Column(Integer, nullable=False)
    num_serie = Column(String(50), unique=True, nullable=False)
    num_motor = Column(String(150), nullable=True)
    num_poliza = Column(String(50), nullable=True)
    num_inventario = Column(String(50), unique=True, nullable=True)
    color = Column(String(30), nullable=False)
    num_tarjeta_gasolina = Column(String(50), nullable=True)
    saldo_tarjeta_gasolina = Column(Numeric(12, 2), nullable=False, default=0)
    km_acumulado = Column(Integer, nullable=False, default=0)
    estado = Column(String, nullable=False, default="disponible")
