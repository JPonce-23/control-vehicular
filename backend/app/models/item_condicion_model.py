from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class ItemCondicion(Base):
    __tablename__ = "item_condicion"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    estado_default = Column(String)
    activo = Column(Boolean)