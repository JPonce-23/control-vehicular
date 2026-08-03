from sqlalchemy import Column, Date, Integer, String, text

from app.database import Base


class PersonaAutorizada(Base):
    __tablename__ = "persona_autorizada"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=False)
    apellido_materno = Column(String(100), nullable=True)
    cargo = Column(String(150), nullable=False)
    num_licencia = Column(String(25), unique=True, nullable=True)
    rfc = Column(String(13), unique=True, nullable=True)
    vigencia_licencia = Column(Date, nullable=True)
    tipo_licencia = Column(String(50), nullable=True)
    estado = Column(String, nullable=False, default="activo", server_default=text("'activo'"))
