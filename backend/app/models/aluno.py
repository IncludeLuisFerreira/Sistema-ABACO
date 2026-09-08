from datetime import date

from sqlalchemy import Integer, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Aluno(Base):
    __tablename__ = "aluno"

    id_aluno: Mapped[int] = mapped_column("idaluno", Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    telefone: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_nascimento: Mapped[date | None] = mapped_column("nascimento", Date, nullable=True)
    rua: Mapped[str | None] = mapped_column(Text, nullable=True)
    bairro: Mapped[str | None] = mapped_column(Text, nullable=True)
    numero: Mapped[int | None] = mapped_column(Integer, nullable=True)

    matriculas = relationship("Matricula", back_populates="aluno", lazy="selectin")
