from sqlalchemy import Column, Enum, ForeignKey, Integer, Text, UniqueConstraint

from app.database import Base


class RevisionCondicion(Base):
    __tablename__ = "revision_condicion"

    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(
        Integer,
        ForeignKey("salida.id", ondelete="CASCADE"),
        nullable=False,
    )
    item_condicion_id = Column(Integer, ForeignKey("item_condicion.id"), nullable=False)
    estado = Column(
        Enum("bueno", "regular", "malo", name="estado_condicion"),
        nullable=False,
    )
    observaciones = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "salida_id",
            "item_condicion_id",
            name="uq_revision_condicion_salida_item",
        ),
    )
