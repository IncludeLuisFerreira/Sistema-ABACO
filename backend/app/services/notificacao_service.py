import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.notificacao import Notificacao
from app.models.usuario import Usuario

logger = logging.getLogger(__name__)


class NotificacaoNotFoundError(Exception):
    pass


def list_notificacoes(
    db: Session,
    usuario_id: int,
    apenas_nao_lidas: bool = False,
    limite: int = 50,
    offset: int = 0,
) -> list[Notificacao]:
    query = db.query(Notificacao).filter(Notificacao.id_usuario == usuario_id)
    if apenas_nao_lidas:
        query = query.filter(Notificacao.lida.is_(False))
    return (
        query.order_by(Notificacao.criada_em.desc(), Notificacao.id_notificacao.desc())
        .limit(limite)
        .offset(offset)
        .all()
    )


def contar_nao_lidas(db: Session, usuario_id: int) -> int:
    return (
        db.query(func.count(Notificacao.id_notificacao))
        .filter(Notificacao.id_usuario == usuario_id, Notificacao.lida.is_(False))
        .scalar()
        or 0
    )


def marcar_como_lida(db: Session, usuario_id: int, notificacao_id: int) -> Notificacao:
    notificacao = (
        db.query(Notificacao)
        .filter(
            Notificacao.id_notificacao == notificacao_id,
            Notificacao.id_usuario == usuario_id,
        )
        .first()
    )
    if notificacao is None:
        raise NotificacaoNotFoundError

    if not notificacao.lida:
        notificacao.lida = True
        db.commit()
        db.refresh(notificacao)
    return notificacao


def marcar_todas_como_lidas(db: Session, usuario_id: int) -> int:
    atualizadas = (
        db.query(Notificacao)
        .filter(Notificacao.id_usuario == usuario_id, Notificacao.lida.is_(False))
        .update({Notificacao.lida: True}, synchronize_session=False)
    )
    db.commit()
    return atualizadas


def notificar_usuarios(
    db: Session,
    destinatarios: list[tuple[int, str | None]],
    tipo: str,
    titulo: str,
    mensagem: str,
) -> int:
    """Grava notificações em transação própria, sem propagar falha ao chamador.

    O link é individual por destinatário. Se o mesmo usuário aparecer mais de uma
    vez no lote, prevalece o primeiro link: o inbox registra uma notificação por
    usuário por chamada.
    """
    sessao = Session(bind=db.get_bind())
    try:
        links_por_id: dict[int, str | None] = {}
        for usuario_id, link in destinatarios:
            links_por_id.setdefault(usuario_id, link)
        if not links_por_id:
            return 0

        ids = list(links_por_id)
        existentes = {
            row[0]
            for row in sessao.query(Usuario.id_usuario).filter(Usuario.id_usuario.in_(ids)).all()
        }
        for usuario_id in ids:
            if usuario_id not in existentes:
                logger.warning(
                    "Destinatário %s inexistente; notificação '%s' ignorada", usuario_id, titulo
                )

        novas = [
            Notificacao(
                id_usuario=usuario_id,
                tipo=tipo,
                titulo=titulo,
                mensagem=mensagem,
                link=link,
            )
            for usuario_id, link in links_por_id.items()
            if usuario_id in existentes
        ]
        if not novas:
            return 0

        sessao.add_all(novas)
        sessao.commit()
        return len(novas)
    except Exception as exc:
        sessao.rollback()
        logger.exception("Falha ao gravar notificações '%s': %s", titulo, exc)
        return 0
    finally:
        sessao.close()
