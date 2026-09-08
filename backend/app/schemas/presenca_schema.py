from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PresencaItemSchema(BaseModel):
    idMatricula: int
    presente: bool


class PresencaBatchSchema(BaseModel):
    idTurma: int
    dataAula: date
    presencas: list[PresencaItemSchema]


class PresencaAlunoInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_aluno: int = Field(alias="idAluno")
    nome: str | None = None


class PresencaMatriculaInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_matricula: int = Field(alias="idMatricula")
    aluno: PresencaAlunoInfo | None = None


class PresencaResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_presenca: int = Field(alias="idPresenca")
    id_matricula: int = Field(alias="idMatricula")
    data_aula: date | None = Field(None, alias="dataAula")
    presente: bool | None = None
    matricula: PresencaMatriculaInfo | None = None
