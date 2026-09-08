from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Presenca(Base):
    __tablename__ = "presenca"

    id_presenca: Mapped[int] = mapped_column("idpresenca", Integer, primary_key=True, index=True)
    id_matricula: Mapped[int] = mapped_column("idmatricula", Integer, ForeignKey("matricula.idmatricula"), nullable=False)
    data_aula: Mapped[date | None] = mapped_column("dataaula", Date, nullable=True)
    presente: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    matricula = relationship("Matricula", lazy="joined")
