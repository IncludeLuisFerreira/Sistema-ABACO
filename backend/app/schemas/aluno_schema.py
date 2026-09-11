from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AlunoCreateSchema(BaseModel):
    nome: str = Field(min_length=1)
    telefone: str | None = None
    dataNascimento: date | None = None
    rua: str | None = None
    bairro: str | None = None
    numero: int | None = None


# REFACTOR: AlunoUpdateSchema é idêntico a AlunoCreateSchema; usar herança/base
class AlunoUpdateSchema(BaseModel):
    nome: str = Field(min_length=1)
    telefone: str | None = None
    dataNascimento: date | None = None
    rua: str | None = None
    bairro: str | None = None
    numero: int | None = None


class AlunoResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_aluno: int = Field(alias="idAluno")
    nome: str
    telefone: str | None = None
    data_nascimento: date | None = Field(None, alias="dataNascimento")
    rua: str | None = None
    bairro: str | None = None
    numero: int | None = None
