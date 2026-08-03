from sqlalchemy import Boolean, Column, Integer, String, text

from app.database import Base


class ItemInventario(Base):
    __tablename__ = "item_inventario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    categoria = Column(String, nullable=False)
    estado_default = Column(String, nullable=False)
    activo = Column(Boolean, nullable=False, default=True, server_default=text("true"))
