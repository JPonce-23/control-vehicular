from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.database import Base

class TokenAcceso(Base):
    __tablename__ = "token_acceso"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario_sistema.id"))
    token = Column(String)
    tipo = Column(String)
    fecha_expiracion = Column(DateTime)
    usado = Column(Boolean)