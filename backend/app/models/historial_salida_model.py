from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from app.database import Base


class HistorialSalida(Base):
    __tablename__ = "historial_salida"

    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salida.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario_sistema.id"), nullable=False)
    accion = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha = Column(DateTime, nullable=False, server_default=func.now())
