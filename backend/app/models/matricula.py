from datetime import date

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Matricula(Base):
    __tablename__ = "matricula"

    id_matricula: Mapped[int] = mapped_column("idmatricula", Integer, primary_key=True, index=True)
    id_aluno: Mapped[int] = mapped_column("idaluno", Integer, ForeignKey("aluno.idaluno"), nullable=False)
    id_turma: Mapped[int] = mapped_column("idturma", Integer, ForeignKey("turma.idturma"), nullable=False)
    data_matricula: Mapped[date | None] = mapped_column("datamatricula", Date, nullable=True)
    status: Mapped[int | None] = mapped_column(Integer, nullable=True)

    aluno = relationship("Aluno", back_populates="matriculas", lazy="joined")
    turma = relationship("Turma", back_populates="matriculas", lazy="joined")
