from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class RevisionInventario(Base):
    __tablename__ = "revision_inventario"
    
    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salida.id"))
    item_id = Column(Integer, ForeignKey("item_inventario.id"))
    estado = Column(String)
    observaciones = Column(String)