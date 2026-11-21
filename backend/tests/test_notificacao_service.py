import logging
from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session

from app.models.notificacao import Notificacao
from app.models.usuario import Usuario
from app.services import notificacao_service


def _usuario(db: Session, email: str) -> Usuario:
    usuario = Usuario(
        nome=email.split("@")[0],
        email=email,
        senha_hash="hash",
        cargo=1,
        primeiro_acesso=False,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _notificacao(
    db: Session,
    usuario_id: int,
    titulo: str,
    *,
    criada_em: datetime,
    lida: bool = False,
    link: str | None = None,
) -> Notificacao:
    notificacao = Notificacao(
        id_usuario=usuario_id,
        tipo="pedido",
        titulo=titulo,
        mensagem="Mensagem de teste",
        link=link,
        lida=lida,
        criada_em=criada_em,
    )
    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)
    return notificacao


class TestListagem:
    def test_lista_apenas_do_usuario_e_mais_recente_primeiro(self, db_session: Session):
        usuario = _usuario(db_session, "dono@abaco.org.br")
        outro = _usuario(db_session, "outro@abaco.org.br")
        antiga = _notificacao(db_session, usuario.id_usuario, "Antiga", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc))
        recente = _notificacao(db_session, usuario.id_usuario, "Recente", criada_em=datetime(2026, 3, 1, tzinfo=timezone.utc))
        _notificacao(db_session, outro.id_usuario, "De outro", criada_em=datetime(2026, 4, 1, tzinfo=timezone.utc))

        resultado = notificacao_service.list_notificacoes(db_session, usuario.id_usuario)

        assert [item.id_notificacao for item in resultado] == [recente.id_notificacao, antiga.id_notificacao]

    def test_filtro_apenas_nao_lidas(self, db_session: Session):
        usuario = _usuario(db_session, "dono@abaco.org.br")
        lida = _notificacao(db_session, usuario.id_usuario, "Lida", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc), lida=True)
        nao_lida = _notificacao(db_session, usuario.id_usuario, "Não lida", criada_em=datetime(2026, 2, 1, tzinfo=timezone.utc))

        resultado = notificacao_service.list_notificacoes(db_session, usuario.id_usuario, apenas_nao_lidas=True)

        assert [item.id_notificacao for item in resultado] == [nao_lida.id_notificacao]
        assert lida.id_notificacao not in [item.id_notificacao for item in resultado]

    def test_paginacao_por_limite_e_offset(self, db_session: Session):
        usuario = _usuario(db_session, "dono@abaco.org.br")
        primeira = _notificacao(db_session, usuario.id_usuario, "Primeira", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc))
        segunda = _notificacao(db_session, usuario.id_usuario, "Segunda", criada_em=datetime(2026, 2, 1, tzinfo=timezone.utc))
        terceira = _notificacao(db_session, usuario.id_usuario, "Terceira", criada_em=datetime(2026, 3, 1, tzinfo=timezone.utc))

        resultado = notificacao_service.list_notificacoes(db_session, usuario.id_usuario, limite=2, offset=1)

        assert [item.id_notificacao for item in resultado] == [segunda.id_notificacao, primeira.id_notificacao]
        assert terceira.id_notificacao not in [item.id_notificacao for item in resultado]


class TestContagem:
    def test_contagem_ignora_lidas_e_outros_usuarios(self, db_session: Session):
        usuario = _usuario(db_session, "dono@abaco.org.br")
        outro = _usuario(db_session, "outro@abaco.org.br")
        _notificacao(db_session, usuario.id_usuario, "Lida", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc), lida=True)
        _notificacao(db_session, usuario.id_usuario, "Não lida 1", criada_em=datetime(2026, 2, 1, tzinfo=timezone.utc))
        _notificacao(db_session, usuario.id_usuario, "Não lida 2", criada_em=datetime(2026, 3, 1, tzinfo=timezone.utc))
        _notificacao(db_session, outro.id_usuario, "De outro", criada_em=datetime(2026, 4, 1, tzinfo=timezone.utc))

        assert notificacao_service.contar_nao_lidas(db_session, usuario.id_usuario) == 2


class TestMarcacao:
    def test_marcar_como_lida_e_idempotente(self, db_session: Session):
        usuario = _usuario(db_session, "dono@abaco.org.br")
        notificacao = _notificacao(db_session, usuario.id_usuario, "Aviso", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc))

        primeira = notificacao_service.marcar_como_lida(db_session, usuario.id_usuario, notificacao.id_notificacao)
        segunda = notificacao_service.marcar_como_lida(db_session, usuario.id_usuario, notificacao.id_notificacao)

        assert primeira.lida is True
        assert segunda.lida is True

    def test_marcar_de_outro_usuario_levanta_erro(self, db_session: Session):
        usuario = _usuario(db_session, "dono@abaco.org.br")
        outro = _usuario(db_session, "outro@abaco.org.br")
        notificacao = _notificacao(db_session, outro.id_usuario, "De outro", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc))

        with pytest.raises(notificacao_service.NotificacaoNotFoundError):
            notificacao_service.marcar_como_lida(db_session, usuario.id_usuario, notificacao.id_notificacao)

    def test_marcar_todas_devolve_quantidade_atualizada(self, db_session: Session):
        usuario = _usuario(db_session, "dono@abaco.org.br")
        outro = _usuario(db_session, "outro@abaco.org.br")
        _notificacao(db_session, usuario.id_usuario, "Lida", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc), lida=True)
        _notificacao(db_session, usuario.id_usuario, "Não lida", criada_em=datetime(2026, 2, 1, tzinfo=timezone.utc))
        _notificacao(db_session, outro.id_usuario, "De outro", criada_em=datetime(2026, 3, 1, tzinfo=timezone.utc))

        primeira = notificacao_service.marcar_todas_como_lidas(db_session, usuario.id_usuario)
        segunda = notificacao_service.marcar_todas_como_lidas(db_session, usuario.id_usuario)

        assert primeira == 1
        assert segunda == 0
        assert notificacao_service.contar_nao_lidas(db_session, usuario.id_usuario) == 0
        assert notificacao_service.contar_nao_lidas(db_session, outro.id_usuario) == 1


class TestNotificarUsuarios:
    def test_grava_link_por_destinatario_deduplica_e_ignora_inexistente(
        self, db_session: Session, caplog
    ):
        primeiro = _usuario(db_session, "um@abaco.org.br")
        segundo = _usuario(db_session, "dois@abaco.org.br")
        destinatarios = [
            (primeiro.id_usuario, "/pedidos/1"),
            (primeiro.id_usuario, "/pedidos/2"),
            (segundo.id_usuario, None),
            (999999, "/pedidos/3"),
        ]

        with caplog.at_level(logging.WARNING):
            quantidade = notificacao_service.notificar_usuarios(
                db_session, destinatarios, "pedido_aprovado", "Pedido aprovado", "Seu pedido foi aprovado"
            )

        gravadas = db_session.query(Notificacao).order_by(Notificacao.id_notificacao).all()
        assert quantidade == 2
        assert [(item.id_usuario, item.link) for item in gravadas] == [
            (primeiro.id_usuario, "/pedidos/1"),
            (segundo.id_usuario, None),
        ]
        assert all(item.tipo == "pedido_aprovado" for item in gravadas)
        assert "999999" in caplog.text

    def test_mesmo_usuario_com_dois_links_mantem_o_primeiro(self, db_session: Session):
        usuario = _usuario(db_session, "um@abaco.org.br")

        quantidade = notificacao_service.notificar_usuarios(
            db_session,
            [
                (usuario.id_usuario, "/pedidos/1"),
                (usuario.id_usuario, "/pedidos/2"),
            ],
            "pedido_aprovado",
            "Pedido aprovado",
            "Seu pedido foi aprovado",
        )

        gravadas = db_session.query(Notificacao).all()
        assert quantidade == 1
        assert [(item.id_usuario, item.link) for item in gravadas] == [
            (usuario.id_usuario, "/pedidos/1")
        ]

    def test_transacao_propria_nao_commita_nem_reverte_pendencia_do_chamador(
        self, db_session: Session, monkeypatch
    ):
        usuario = _usuario(db_session, "dono@abaco.org.br")
        nome_original = usuario.nome
        usuario.nome = "Nome pendente do chamador"
        chamadas_commit = []
        chamadas_rollback = []
        commit_original = db_session.commit
        rollback_original = db_session.rollback

        def commit_registrado():
            chamadas_commit.append(True)
            return commit_original()

        def rollback_registrado():
            chamadas_rollback.append(True)
            return rollback_original()

        monkeypatch.setattr(db_session, "commit", commit_registrado)
        monkeypatch.setattr(db_session, "rollback", rollback_registrado)

        quantidade = notificacao_service.notificar_usuarios(
            db_session,
            [(usuario.id_usuario, "/pedidos/9")],
            "pedido_aprovado",
            "Pedido aprovado",
            "Aviso",
        )

        assert quantidade == 1
        assert chamadas_commit == []
        assert chamadas_rollback == []
        assert usuario in db_session.dirty
        assert usuario.nome == "Nome pendente do chamador"

        with Session(bind=db_session.get_bind()) as consulta:
            assert consulta.get(Usuario, usuario.id_usuario).nome == nome_original
            assert consulta.query(Notificacao).count() == 1

    def test_sem_destinatarios_validos_nao_grava_nada(self, db_session: Session, caplog):
        with caplog.at_level(logging.WARNING):
            vazia = notificacao_service.notificar_usuarios(
                db_session, [], "estoque_baixo", "Estoque baixo", "Repor item"
            )
            inexistente = notificacao_service.notificar_usuarios(
                db_session, [(999999, None)], "estoque_baixo", "Estoque baixo", "Repor item"
            )

        assert vazia == 0
        assert inexistente == 0
        assert db_session.query(Notificacao).count() == 0
        assert "999999" in caplog.text

    def test_falha_de_gravacao_e_absorvida_com_log(self, db_session: Session, monkeypatch, caplog):
        usuario = _usuario(db_session, "dono@abaco.org.br")
        commits = []
        rollbacks = []
        commit_original = Session.commit
        rollback_original = Session.rollback

        def commit_com_falha(session: Session):
            commits.append(session)
            raise RuntimeError("falha simulada de gravação")

        def rollback_registrado(session: Session):
            rollbacks.append(session)
            return rollback_original(session)

        monkeypatch.setattr(Session, "commit", commit_com_falha)
        monkeypatch.setattr(Session, "rollback", rollback_registrado)

        with caplog.at_level(logging.ERROR):
            quantidade = notificacao_service.notificar_usuarios(
                db_session, [(usuario.id_usuario, None)], "estoque_baixo", "Estoque baixo", "Repor item"
            )

        assert quantidade == 0
        assert commits and all(sessao is not db_session for sessao in commits)
        assert rollbacks and all(sessao is not db_session for sessao in rollbacks)
        assert "falha simulada" in caplog.text
        with Session(bind=db_session.get_bind()) as consulta:
            assert consulta.query(Notificacao).count() == 0
