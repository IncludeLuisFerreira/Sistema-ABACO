from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Curso(Base):
    __tablename__ = "curso"

    id_curso: Mapped[int] = mapped_column("idcurso", Integer, primary_key=True, index=True)
    nome_curso: Mapped[str] = mapped_column("nomecurso", Text, nullable=False)
