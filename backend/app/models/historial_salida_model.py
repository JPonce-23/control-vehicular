from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from app.database import Base

class HistorialSalida(Base):
    __tablename__ = "historial_salida"
    
    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salida.id"))
    usuario_id = Column(Integer, ForeignKey("usuario_sistema.id"))
    accion = Column(Text)
    descripcion = Column(Text)
    fecha = Column(DateTime)

