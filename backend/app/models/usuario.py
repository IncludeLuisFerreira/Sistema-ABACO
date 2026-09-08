from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column("idusuario", Integer, primary_key=True, index=True)
    nome: Mapped[str | None] = mapped_column(Text, nullable=True)
    telefone: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True, index=True)
    senha_hash: Mapped[str | None] = mapped_column("senhahash", Text, nullable=True)
    cargo: Mapped[int | None] = mapped_column(Integer, nullable=True)