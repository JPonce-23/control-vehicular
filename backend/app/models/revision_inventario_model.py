from sqlalchemy import Column, Enum, ForeignKey, Integer, Text, UniqueConstraint

from app.database import Base


class RevisionInventario(Base):
    __tablename__ = "revision_inventario"

    id = Column(Integer, primary_key=True, index=True)
    salida_id = Column(
        Integer,
        ForeignKey("salida.id", ondelete="CASCADE"),
        nullable=False,
    )
    item_id = Column(Integer, ForeignKey("item_inventario.id"), nullable=False)
    estado = Column(
        Enum("correcto", "na", "vacio", name="estado_revision_inventario"),
        nullable=False,
    )
    observaciones = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("salida_id", "item_id", name="uq_revision_inventario_salida_item"),
    )
