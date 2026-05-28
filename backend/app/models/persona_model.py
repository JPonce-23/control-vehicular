from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class PersonaAutorizada(Base):
    __tablename__ = "persona_autorizada"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido_paterno = Column(String)
    apellido_materno = Column(String)
    num_licencia = Column(String)
    rfc = Column(String)
    vigencia_licencia = Column(Date)
    tipo_licencia = Column(String)
    estado = Column(String)