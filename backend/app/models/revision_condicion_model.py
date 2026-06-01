from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class RevisionCondicion(Base):
    __tablename__ = "revision_condicion"
    
    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salida.id"))
    item_condicion_id = Column(Integer, ForeignKey("item_condicion.id"))
    estado = Column(String)
    observaciones = Column(String)