from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Nota(Base):
    __tablename__ = "nota"

    id_nota: Mapped[int] = mapped_column("idnota", Integer, primary_key=True, index=True)
    nota: Mapped[float | None] = mapped_column(Float, nullable=True)
    prova: Mapped[int | None] = mapped_column(Integer, nullable=True)
    id_matricula: Mapped[int] = mapped_column("idmatricula", Integer, ForeignKey("matricula.idmatricula"), nullable=False)

    matricula = relationship("Matricula", lazy="joined")
