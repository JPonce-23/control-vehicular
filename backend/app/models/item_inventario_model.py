from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class ItemInventario(Base):
    __tablename__ = "item_inventario"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    categoria = Column(String)
    estado_default = Column(String)
    activo = Column(Boolean)