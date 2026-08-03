from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text

from app.database import Base


class TokenAcceso(Base):
    __tablename__ = "token_acceso"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuario_sistema.id", ondelete="CASCADE"),
        nullable=False,
    )
    token = Column(String(128), nullable=False, unique=True)
    tipo = Column(String, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    usado = Column(Boolean, nullable=False, default=False, server_default=text("false"))
