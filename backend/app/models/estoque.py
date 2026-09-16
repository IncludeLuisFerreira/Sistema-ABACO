from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Estoque(Base):
    __tablename__ = "estoque"

    id_item_estoque: Mapped[int] = mapped_column("iditemestoque", Integer, primary_key=True, index=True)
    nome_item: Mapped[str | None] = mapped_column("nomeitem", String, nullable=True)
    quantidade_disponivel: Mapped[int | None] = mapped_column("quantidadedisponivel", Integer, nullable=True)
    unidade: Mapped[str | None] = mapped_column(String, nullable=True)
    estoque_minimo: Mapped[int | None] = mapped_column("estoqueminimo", Integer, nullable=True)
