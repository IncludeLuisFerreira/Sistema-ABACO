from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.validators import normalize_nome_item


def _strip_nome_item(value: str) -> str:
    nome = normalize_nome_item(value)
    if not nome:
        raise ValueError("Nome do item é obrigatório")
    return nome


class EstoqueCreateSchema(BaseModel):
    nomeItem: str = Field(min_length=1)
    quantidadeDisponivel: int | None = Field(default=None, ge=0, strict=True)
    unidade: str | None = None
    estoqueMinimo: int | None = Field(default=None, ge=0, strict=True)

    @field_validator("nomeItem")
    @classmethod
    def validar_nome_item(cls, value: str) -> str:
        return _strip_nome_item(value)


class EstoqueUpdateSchema(BaseModel):
    nomeItem: str | None = Field(default=None, min_length=1)
    quantidadeDisponivel: int | None = Field(default=None, ge=0, strict=True)
    unidade: str | None = None
    estoqueMinimo: int | None = Field(default=None, ge=0, strict=True)

    @field_validator("nomeItem")
    @classmethod
    def validar_nome_item(cls, value: str | None) -> str | None:
        return None if value is None else _strip_nome_item(value)


class EstoqueResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_item_estoque: int = Field(alias="idItemEstoque")
    nome_item: str | None = Field(None, alias="nomeItem")
    quantidade_disponivel: int | None = Field(None, alias="quantidadeDisponivel")
    unidade: str | None = None
    estoque_minimo: int | None = Field(None, alias="estoqueMinimo")


class EstoqueBaixaSchema(BaseModel):
    quantidade: int = Field(..., gt=0, strict=True, description="Quantidade a ser deduzida do estoque")
    justificativa: str = Field(..., min_length=1, description="Justificativa para a baixa")


class EstoqueAlertaResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_item_estoque: int = Field(alias="idItemEstoque")
    nome_item: str | None = Field(None, alias="nomeItem")
    quantidade_disponivel: int | None = Field(None, alias="quantidadeDisponivel")
    unidade: str | None = None
    estoque_minimo: int | None = Field(None, alias="estoqueMinimo")
