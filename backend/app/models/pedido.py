from datetime import date

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Pedido(Base):
    __tablename__ = "pedido"

    id_pedido: Mapped[int] = mapped_column("idpedido", Integer, primary_key=True, index=True)
    id_usuario: Mapped[int] = mapped_column("idusuario", Integer, ForeignKey("usuario.idusuario"), nullable=False)
    id_turma: Mapped[int] = mapped_column("idturma", Integer, ForeignKey("turma.idturma"), nullable=False)
    data_pedido: Mapped[date | None] = mapped_column("datapedido", Date, nullable=True)
    status: Mapped[int | None] = mapped_column(Integer, nullable=True)

    usuario = relationship("Usuario", lazy="joined")
    turma = relationship("Turma", lazy="joined")
    itens = relationship("ItemPedido", lazy="joined", cascade="all, delete-orphan")
