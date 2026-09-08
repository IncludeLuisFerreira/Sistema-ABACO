from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacao_estoque"

    id_movimentacao: Mapped[int] = mapped_column("idmovimentacao", Integer, primary_key=True, index=True)
    id_item_estoque: Mapped[int] = mapped_column("iditemestoque", Integer, ForeignKey("estoque.iditemestoque"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_movimentacao: Mapped[str] = mapped_column("tipomovimentacao", String, nullable=False)
    justificativa: Mapped[str | None] = mapped_column(String, nullable=True)
    data_movimentacao: Mapped[datetime] = mapped_column("datamovimentacao", DateTime, nullable=False)
