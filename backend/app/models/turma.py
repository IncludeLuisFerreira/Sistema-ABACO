from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Turma(Base):
    __tablename__ = "turma"

    id_turma: Mapped[int] = mapped_column("idturma", Integer, primary_key=True, index=True)
    capacidade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_inicio: Mapped[date | None] = mapped_column("datainicio", Date, nullable=True)
    data_fim: Mapped[date | None] = mapped_column("datafim", Date, nullable=True)
    id_curso: Mapped[int] = mapped_column("idcurso", Integer, ForeignKey("curso.idcurso"), nullable=False)
    id_professor: Mapped[int | None] = mapped_column("idprofessor", Integer, ForeignKey("usuario.idusuario"), nullable=True)
    dias_aula: Mapped[str | None] = mapped_column("diasaula", String, nullable=True)
    avaliacoes: Mapped[list | None] = mapped_column(JSON, nullable=True)

    curso = relationship("Curso", lazy="joined")
    professor = relationship("Usuario", lazy="joined")
    matriculas = relationship("Matricula", back_populates="turma", lazy="selectin")

    @property
    def vagas_ocupadas(self) -> int:
        return sum(1 for m in self.matriculas if m.status == 0)
