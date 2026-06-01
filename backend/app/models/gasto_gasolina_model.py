from sqlalchemy import Column, Integer, Numeric, ForeignKey, Text, Date
from app.database import Base

class GastoGasolina(Base):
    __tablename__ = "gasto_gasolina"
    
    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculo.id"))
    salida_id = Column(Integer, ForeignKey("salida.id"))
    presupuesto_id = Column(Integer, ForeignKey("presupuesto_gasolina.id"))
    fecha_gasto = Column(Date)
    litros = Column(Numeric(10, 2))
    monto = Column(Numeric(10, 2))
    nota = Column(Text)

