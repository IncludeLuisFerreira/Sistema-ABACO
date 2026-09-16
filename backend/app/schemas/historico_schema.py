from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class HistoricoNotaInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prova: int | None = None
    nota: float | None = None


class HistoricoPresencaInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data_aula: date | None = Field(None, alias="dataAula")
    presente: bool | None = None


class HistoricoAlunoInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_aluno: int = Field(alias="idAluno")
    nome: str
    data_nascimento: date | None = Field(None, alias="dataNascimento")
    telefone: str | None = None


class HistoricoTurmaInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_turma: int = Field(alias="idTurma")
    nome_curso: str = Field(alias="nomeCurso")
    nome_professor: str | None = Field(None, alias="nomeProfessor")
    data_inicio: date | None = Field(None, alias="dataInicio")
    data_fim: date | None = Field(None, alias="dataFim")
    dias_aula: str | None = Field(None, alias="diasAula")


class HistoricoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_matricula: int = Field(alias="idMatricula")
    data_matricula: date | None = Field(None, alias="dataMatricula")
    status: int | None = None
    aluno: HistoricoAlunoInfo
    turma: HistoricoTurmaInfo
    notas: list[HistoricoNotaInfo] = []
    presencas: list[HistoricoPresencaInfo] = []
    percentual_frequencia: float | None = Field(None, alias="percentualFrequencia")
