from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Notificacao(Base):
    __tablename__ = "notificacao"

    id_notificacao: Mapped[int] = mapped_column("idnotificacao", Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(
        "idusuario", Integer, ForeignKey("usuario.idusuario", ondelete="CASCADE"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str | None] = mapped_column(Text, nullable=True)
    lida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    criada_em: Mapped[datetime] = mapped_column(
        "criada_em",
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("idx_notificacao_idusuario_lida", "idusuario", "lida"),
        Index("idx_notificacao_idusuario_criada_em", "idusuario", "criada_em"),
    )
