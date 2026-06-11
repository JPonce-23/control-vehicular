from sqlalchemy import Column, Integer, Numeric, UniqueConstraint, ForeignKey
from app.database import Base

class PresupuestoGasolina(Base):
    __tablename__ = "presupuesto_gasolina"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculo.id"), nullable=False)
    monto_autorizado_total = Column(Numeric(10, 2), nullable=False)
    monto_por_mes = Column(Numeric(10, 2), nullable=False)
    monto_utilizado = Column(Numeric(10, 2), nullable=False, default=0)
    saldo_acumulado = Column(Numeric(10, 2), nullable=False, default=0)
    anio = Column(Integer, nullable=False)
    mes_inicio = Column(Integer, nullable=False, default=1)
    mes_fin = Column(Integer, nullable=False, default=12)

    __table_args__ = (
        UniqueConstraint("vehiculo_id", "anio", name="presupuesto_gasolina_vehiculo_anio_unique"),
    )