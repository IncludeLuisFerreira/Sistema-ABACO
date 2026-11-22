from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _validar_status(value: object) -> object:
    if value is None or (isinstance(value, int) and not isinstance(value, bool)):
        return value
    raise ValueError("Status deve ser 0, 1 ou 2")


MatriculaStatus = Annotated[Literal[0, 1, 2], BeforeValidator(_validar_status)]


class MatriculaCreateSchema(BaseModel):
    idAluno: int
    idTurma: int
    dataMatricula: date | None = None
    status: MatriculaStatus = 0


class MatriculaUpdateSchema(BaseModel):
    idAluno: int | None = None
    idTurma: int | None = None
    dataMatricula: date | None = None
    status: MatriculaStatus | None = None


class MatriculaAlunoInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_aluno: int = Field(alias="idAluno")
    nome: str | None = None


class MatriculaCursoInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_curso: int = Field(alias="idCurso")
    nome_curso: str = Field(alias="nomeCurso")


class MatriculaTurmaInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_turma: int = Field(alias="idTurma")
    capacidade: int | None = None
    curso: MatriculaCursoInfo | None = None


class MatriculaResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_matricula: int = Field(alias="idMatricula")
    id_aluno: int | None = Field(None, alias="idAluno")
    id_turma: int | None = Field(None, alias="idTurma")
    data_matricula: date | None = Field(None, alias="dataMatricula")
    status: int | None = None
    aluno: MatriculaAlunoInfo | None = None
    turma: MatriculaTurmaInfo | None = None
