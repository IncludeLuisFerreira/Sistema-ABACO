import logging

import pytest
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.email.exceptions import EmailDeliveryError
from app.email.messages import EmailMessage
from app.models.notificacao import Notificacao
from app.models.usuario import Usuario
from app.services import notificacao_dispatcher_service as dispatcher


def _usuario(db: Session, nome: str, email: str | None = None) -> Usuario:
    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash="hash",
        cargo=2,
        primeiro_acesso=False,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _evento(email: EmailMessage | None = None) -> dispatcher.EventoNotificacao:
    return dispatcher.EventoNotificacao(
        tipo="evento_teste",
        titulo="Título do evento",
        mensagem="Mensagem do evento",
        email=email,
    )


def test_deduplica_por_usuario_e_mantem_o_primeiro_link(monkeypatch, db_session: Session):
    primeiro = _usuario(db_session, "Primeiro")
    segundo = _usuario(db_session, "Segundo")
    lotes: list[list[tuple[int, str | None]]] = []

    monkeypatch.setattr(
        dispatcher,
        "notificar_usuarios",
        lambda _db, destinatarios, *_args: lotes.append(list(destinatarios)) or 1,
    )

    quantidade = dispatcher.disparar_evento(
        db_session,
        _evento(),
        [
            dispatcher.DestinatarioNotificacao(primeiro.id_usuario, "/primeiro"),
            dispatcher.DestinatarioNotificacao(primeiro.id_usuario, "/segundo"),
            dispatcher.DestinatarioNotificacao(segundo.id_usuario, "/terceiro"),
        ],
    )

    assert lotes == [
        [
            (primeiro.id_usuario, "/primeiro"),
            (segundo.id_usuario, "/terceiro"),
        ]
    ]
    assert quantidade == 1


def test_grava_inbox_com_link_individual(db_session: Session, usuario, usuario_professor):
    quantidade = dispatcher.disparar_evento(
        db_session,
        _evento(),
        [
            dispatcher.DestinatarioNotificacao(usuario.id_usuario, "/admin/pedidos"),
            dispatcher.DestinatarioNotificacao(usuario_professor.id_usuario, "/academico/pedidos"),
        ],
    )

    assert quantidade == 2
    notificacoes = (
        db_session.query(Notificacao)
        .filter(Notificacao.tipo == "evento_teste")
        .order_by(Notificacao.id_usuario)
        .all()
    )
    assert {item.id_usuario: item.link for item in notificacoes} == {
        usuario.id_usuario: "/admin/pedidos",
        usuario_professor.id_usuario: "/academico/pedidos",
    }
    assert all(item.titulo == "Título do evento" for item in notificacoes)
    assert all(item.mensagem == "Mensagem do evento" for item in notificacoes)


def test_email_e_opcional_por_destinatario(monkeypatch, db_session: Session):
    com_email = _usuario(db_session, "Com Email", "com@abaco.org.br")
    sem_envio = _usuario(db_session, "Sem Envio", "semenvio@abaco.org.br")
    sem_endereco = _usuario(db_session, "Sem Endereco")
    mensagem = EmailMessage("Assunto", "Texto", "<p>Texto</p>")
    enviados: list[tuple[str, EmailMessage]] = []
    monkeypatch.setattr(
        dispatcher, "send_email", lambda to_email, msg: enviados.append((to_email, msg))
    )

    dispatcher.disparar_evento(
        db_session,
        _evento(mensagem),
        [
            dispatcher.DestinatarioNotificacao(
                com_email.id_usuario, "/a", com_email.email, True
            ),
            dispatcher.DestinatarioNotificacao(
                sem_envio.id_usuario, "/b", sem_envio.email, False
            ),
            dispatcher.DestinatarioNotificacao(sem_endereco.id_usuario, "/c", None, True),
        ],
    )

    assert enviados == [("com@abaco.org.br", mensagem)]


def test_destinatario_sem_email_gera_log_e_nao_quebra(monkeypatch, db_session: Session, caplog):
    usuario = _usuario(db_session, "Sem Email")
    monkeypatch.setattr(dispatcher, "send_email", lambda *_args: None)
    mensagem = EmailMessage("Assunto", "Texto", "<p>Texto</p>")

    with caplog.at_level(logging.WARNING):
        dispatcher.disparar_evento(
            db_session,
            _evento(mensagem),
            [dispatcher.DestinatarioNotificacao(usuario.id_usuario, "/a", None, True)],
        )

    assert "sem e-mail cadastrado" in caplog.text


def test_sem_destinatarios_nao_grava_nem_envia(monkeypatch, db_session: Session):
    enviados: list[tuple[str, EmailMessage]] = []
    monkeypatch.setattr(
        dispatcher, "send_email", lambda to_email, msg: enviados.append((to_email, msg))
    )

    quantidade = dispatcher.disparar_evento(
        db_session,
        _evento(EmailMessage("Assunto", "Texto", "<p>Texto</p>")),
        [],
    )

    assert quantidade == 0
    assert enviados == []


def test_falha_do_inbox_e_absorvida_e_nao_impede_email(
    monkeypatch, db_session: Session, caplog
):
    usuario = _usuario(db_session, "Usuario", "usuario@abaco.org.br")
    mensagem = EmailMessage("Assunto", "Texto", "<p>Texto</p>")
    enviados: list[tuple[str, EmailMessage]] = []

    def falha_inbox(*_args, **_kwargs):
        raise RuntimeError("inbox indisponível")

    monkeypatch.setattr(dispatcher, "notificar_usuarios", falha_inbox)
    monkeypatch.setattr(
        dispatcher, "send_email", lambda to_email, msg: enviados.append((to_email, msg))
    )

    with caplog.at_level(logging.ERROR):
        quantidade = dispatcher.disparar_evento(
            db_session,
            _evento(mensagem),
            [
                dispatcher.DestinatarioNotificacao(
                    usuario.id_usuario, "/a", usuario.email, True
                )
            ],
        )

    assert quantidade == 0
    assert enviados == [("usuario@abaco.org.br", mensagem)]
    assert "inbox indisponível" in caplog.text


@pytest.mark.parametrize(
    ("erro", "trecho_log"),
    [
        (EmailDeliveryError("provedor fora do ar"), "Falha ao enviar e-mail"),
        (RuntimeError("erro interno"), "Erro inesperado ao enviar e-mail"),
    ],
)
def test_falha_de_email_e_absorvida(
    monkeypatch, db_session: Session, caplog, erro: Exception, trecho_log: str
):
    usuario = _usuario(db_session, "Usuario", "usuario@abaco.org.br")

    def falha_email(*_args, **_kwargs):
        raise erro

    monkeypatch.setattr(dispatcher, "send_email", falha_email)

    with caplog.at_level(logging.ERROR):
        dispatcher.disparar_evento(
            db_session,
            _evento(EmailMessage("Assunto", "Texto", "<p>Texto</p>")),
            [
                dispatcher.DestinatarioNotificacao(
                    usuario.id_usuario, "/a", usuario.email, True
                )
            ],
        )

    assert trecho_log in caplog.text


def test_background_tasks_agendam_email_sem_enviar_na_hora(
    monkeypatch, db_session: Session
):
    usuario = _usuario(db_session, "Usuario", "usuario@abaco.org.br")
    mensagem = EmailMessage("Assunto", "Texto", "<p>Texto</p>")
    enviados: list[tuple[str, EmailMessage]] = []
    monkeypatch.setattr(
        dispatcher, "send_email", lambda to_email, msg: enviados.append((to_email, msg))
    )
    tasks = BackgroundTasks()

    dispatcher.disparar_evento(
        db_session,
        _evento(mensagem),
        [dispatcher.DestinatarioNotificacao(usuario.id_usuario, "/a", usuario.email, True)],
        tasks,
    )

    assert enviados == []
    assert len(tasks.tasks) == 1
    tarefa = tasks.tasks[0]
    tarefa.func(*tarefa.args, **tarefa.kwargs)
    assert enviados == [("usuario@abaco.org.br", mensagem)]
