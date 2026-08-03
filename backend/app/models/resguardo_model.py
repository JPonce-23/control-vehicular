from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from app.database import Base


class Resguardo(Base):
    __tablename__ = "resguardo"

    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salida.id"), nullable=False, unique=True)
    fecha_generacion = Column(DateTime, nullable=False, server_default=func.now())
    nombre_archivo = Column(String(150), nullable=False)
    ruta_archivo = Column(Text, nullable=False)
