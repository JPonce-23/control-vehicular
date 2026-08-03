from sqlalchemy import Boolean, Column, Integer, String, text

from app.database import Base


class ItemCondicion(Base):
    __tablename__ = "item_condicion"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    estado_default = Column(String, nullable=False, default="bueno", server_default=text("'bueno'"))
    activo = Column(Boolean, nullable=False, default=True, server_default=text("true"))
