from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.database import Base

class PresupuestoGasolina(Base):
    __tablename__ = "presupuesto_gasolina"
    
    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculo.id"))
    monto_autorizado_total = Column(Numeric(10, 2))
    monto_por_mes = Column(Numeric(10, 2))
    monto_utilizado = Column(Numeric(10, 2))
    saldo_acumulado = Column(Numeric(10, 2))
    anio = Column(Integer)

