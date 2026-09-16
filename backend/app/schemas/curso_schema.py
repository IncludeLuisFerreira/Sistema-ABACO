from pydantic import BaseModel, ConfigDict, Field


class CursoCreateSchema(BaseModel):
    nomeCurso: str = Field(min_length=1)


class CursoUpdateSchema(BaseModel):
    nomeCurso: str = Field(min_length=1)


class CursoResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_curso: int = Field(alias="idCurso")
    nome_curso: str = Field(alias="nomeCurso")
