from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AvaliacaoSchema(BaseModel):
    nome: str = Field(min_length=1)
    tipo: Literal["prova", "trabalho"]
    peso: float = Field(gt=0)

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("nome da avaliação não pode ser vazio")
        return value


class AvaliacaoResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    nome: Any = None
    tipo: Any = None
    peso: Any = None

    @field_validator("tipo", mode="before")
    @classmethod
    def normaliza_tipo_legado(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        stripped = value.strip()
        lowered = stripped.lower()
        if lowered in {"prova", "trabalho"}:
            return lowered
        return stripped


def _validate_dias_aula(value: str) -> str:
    dias = value.split(",")
    if any(dia not in {"0", "1", "2", "3", "4", "5", "6"} for dia in dias):
        raise ValueError("diasAula deve conter apenas dias de 0 a 6 separados por vírgula")
    if len(set(dias)) != len(dias):
        raise ValueError("diasAula não pode conter dias duplicados")
    return value


class TurmaCreateSchema(BaseModel):
    capacidade: int = Field(gt=0)
    dataInicio: date
    dataFim: date
    idCurso: int
    idProfessor: int
    diasAula: str
    avaliacoes: list[AvaliacaoSchema] | None = None

    @field_validator("diasAula")
    @classmethod
    def validate_dias_aula(cls, value: str) -> str:
        return _validate_dias_aula(value)


class TurmaUpdateSchema(BaseModel):
    capacidade: int | None = Field(None, gt=0)
    dataInicio: date | None = None
    dataFim: date | None = None
    idCurso: int | None = None
    idProfessor: int | None = None
    diasAula: str | None = None
    avaliacoes: list[AvaliacaoSchema] | None = None

    @field_validator("diasAula")
    @classmethod
    def validate_dias_aula(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validate_dias_aula(value)


class TurmaCursoInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_curso: int = Field(alias="idCurso")
    nome_curso: str = Field(alias="nomeCurso")


class TurmaProfessorInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_usuario: int = Field(alias="idUsuario")
    nome: str | None = None


class TurmaResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_turma: int = Field(alias="idTurma")
    capacidade: int | None = None
    data_inicio: date | None = Field(None, alias="dataInicio")
    data_fim: date | None = Field(None, alias="dataFim")
    id_curso: int = Field(alias="idCurso")
    id_professor: int | None = Field(None, alias="idProfessor")
    dias_aula: str | None = Field(None, alias="diasAula")
    vagas_ocupadas: int | None = Field(None, alias="vagasOcupadas")
    avaliacoes: Any = None
    curso: TurmaCursoInfo | None = None
    professor: TurmaProfessorInfo | None = None

    @field_validator("avaliacoes", mode="before")
    @classmethod
    def normaliza_avaliacoes_legadas(cls, value: Any) -> Any:
        if value is None:
            return None
        if not isinstance(value, list):
            return value
        return [
            AvaliacaoResponseSchema.model_validate(item) if isinstance(item, dict) else item
            for item in value
        ]
