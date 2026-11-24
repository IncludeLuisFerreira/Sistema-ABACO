from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificacaoResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_notificacao: int = Field(alias="idNotificacao")
    tipo: str
    titulo: str
    mensagem: str
    link: str | None = None
    lida: bool
    criada_em: datetime = Field(alias="criadaEm")


class NotificacaoContagemSchema(BaseModel):
    nao_lidas: int = Field(alias="naoLidas")


class MarcarTodasLidasResponseSchema(BaseModel):
    atualizadas: int
