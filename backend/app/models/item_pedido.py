from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ItemPedido(Base):
    __tablename__ = "itempedido"

    id_item_pedido: Mapped[int] = mapped_column("iditempedido", Integer, primary_key=True, index=True)
    id_pedido: Mapped[int] = mapped_column("idpedido", Integer, ForeignKey("pedido.idpedido"), nullable=False)
    id_item_estoque: Mapped[int | None] = mapped_column("iditemestoque", Integer, ForeignKey("estoque.iditemestoque"), nullable=True)
    nome_item: Mapped[str | None] = mapped_column("nomeitem", String, nullable=True)
    quantidade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preco_unitario: Mapped[float | None] = mapped_column("precounitario", Float, nullable=True)

    item_estoque = relationship("Estoque", lazy="joined")
