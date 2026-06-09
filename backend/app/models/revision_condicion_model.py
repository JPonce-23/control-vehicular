from sqlalchemy import Column, Integer, Text, ForeignKey, Enum
from app.database import Base

class RevisionCondicion(Base):
    __tablename__ = "revision_condicion"

    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(Integer, ForeignKey("salida.id"))
    item_condicion_id = Column(Integer, ForeignKey("item_condicion.id"))
    estado = Column(
        Enum("bueno", "regular", "malo", name="estado_condicion"),
        nullable=False
    )
    observaciones = Column(Text)