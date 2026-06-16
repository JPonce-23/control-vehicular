from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class PersonaAutorizada(Base):
    __tablename__ = "persona_autorizada"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido_paterno = Column(String)
    apellido_materno = Column(String)
    cargo = Column(String(150), nullable=False)
    num_licencia = Column(String(25), unique=True, nullable=True)
    rfc = Column(String)
    vigencia_licencia = Column(Date, nullable=True)
    tipo_licencia = Column(String(50), nullable=True)
    estado = Column(String)