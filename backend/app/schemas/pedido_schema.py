from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ItemPedidoCreateSchema(BaseModel):
    nomeItem: str
    quantidade: int | None = None
    idItemEstoque: int | None = None
    precoUnitario: float | None = None


class PedidoCreateSchema(BaseModel):
    idTurma: int
    dataPedido: date | None = None
    itens: list[ItemPedidoCreateSchema]


class ItemPedidoCompraSchema(BaseModel):
    idItemPedido: int
    quantidade: int


class PedidoCompraSchema(BaseModel):
    itens: list[ItemPedidoCompraSchema]


class PedidoUpdateSchema(BaseModel):
    status: int


# TODO: PedidoEntregaSchema vazio e não utilizado (código morto)
class PedidoEntregaSchema(BaseModel):
    pass


class EstoqueItemInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_item_estoque: int = Field(alias="idItemEstoque")
    nome_item: str | None = Field(None, alias="nomeItem")
    unidade: str | None = None


class ItemPedidoResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_item_pedido: int = Field(alias="idItemPedido")
    id_pedido: int = Field(alias="idPedido")
    id_item_estoque: int | None = Field(None, alias="idItemEstoque")
    nome_item: str | None = Field(None, alias="nomeItem")
    quantidade: int | None = None
    preco_unitario: float | None = Field(None, alias="precoUnitario")
    item_estoque: EstoqueItemInfo | None = None


class UsuarioPedidoInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_usuario: int = Field(alias="idUsuario")
    nome: str | None = None


class TurmaPedidoInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_turma: int = Field(alias="idTurma")
    capacidade: int | None = None
    nome_curso: str | None = Field(None, alias="nomeCurso")

    @model_validator(mode="before")
    @classmethod
    def populate_nome_curso(cls, data):
        if isinstance(data, dict):
            return data
        turma = data
        if hasattr(turma, "curso") and turma.curso:
            turma.nome_curso = turma.curso.nome_curso
        return turma


class PedidoResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_pedido: int = Field(alias="idPedido")
    id_usuario: int = Field(alias="idUsuario")
    id_turma: int = Field(alias="idTurma")
    data_pedido: date | None = Field(None, alias="dataPedido")
    status: int | None = None
    usuario: UsuarioPedidoInfo | None = None
    turma: TurmaPedidoInfo | None = None
    itens: list[ItemPedidoResponseSchema] | None = None
