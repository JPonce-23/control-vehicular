from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id = Column(Integer, primary_key=True, index=True)
    num_economico = Column(String)
    placa = Column(String)
    marca = Column(String)
    tipo = Column(String)
    modelo_anio = Column(Integer)
    cilindros = Column(Integer)
    num_serie = Column(String)
    num_motor = Column(String)
    num_poliza = Column(String)
    num_inventario = Column(String)
    color = Column(String)
    num_tarjeta_gasolina = Column(String)
    km_acumulado = Column(Numeric)
    estado = Column(String)