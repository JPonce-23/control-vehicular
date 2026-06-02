from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from app.database import Base

class Resguardo(Base):
    __tablename__ = "resguardo"

    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salida.id"))
    fecha_generacion = Column(DateTime, nullable=False, server_default=func.now())
    nombre_archivo = Column(String)
    ruta_archivo = Column(Text)