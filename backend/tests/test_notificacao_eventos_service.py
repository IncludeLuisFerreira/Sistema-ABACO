import pytest
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app import email as email_pkg
from app.email import messages as email_messages
from app.models.estoque import Estoque
from app.models.notificacao import Notificacao
from app.models.usuario import Usuario
from app.schemas.estoque_schema import EstoqueCreateSchema, EstoqueUpdateSchema
from app.schemas.pedido_schema import (
    ItemPedidoCreateSchema,
    PedidoCompraSchema,
    PedidoCreateSchema,
    PedidoUpdateSchema,
)
from app.services import estoque_service, notificacao_eventos_service as eventos, pedido_service
from app.services.estoque_service import create_estoque, dar_baixa, update_estoque
from app.services.pedido_service import (
    aprovar_pedido,
    comprar_pedido,
    create_pedido,
    entregar_pedido,
    update_pedido_status,
)


def _usuario(db: Session, nome: str, cargo: int, email: str | None = None, sem_email: bool = False) -> Usuario:
    usuario = Usuario(
        nome=nome,
        email=None if sem_email else (email or f"{nome.lower().replace(' ', '.')}@abaco.org.br"),
        senha_hash="hash",
        cargo=cargo,
        primeiro_acesso=False,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _notificacoes(db: Session, usuario_id: int, tipo: str | None = None) -> list[Notificacao]:
    query = db.query(Notificacao).filter(Notificacao.id_usuario == usuario_id)
    if tipo is not None:
        query = query.filter(Notificacao.tipo == tipo)
    return query.all()


def _criar_pedido(db: Session, turma, usuario, estoque_item=None, quantidade: int = 5):
    if estoque_item is None:
        estoque_item = Estoque(
            nome_item="Caneta",
            quantidade_disponivel=100,
            unidade="un",
            estoque_minimo=0,
        )
        db.add(estoque_item)
        db.commit()
        db.refresh(estoque_item)

    payload = PedidoCreateSchema(
        idTurma=turma.id_turma,
        itens=[
            ItemPedidoCreateSchema(
                nomeItem=estoque_item.nome_item,
                quantidade=quantidade,
                idItemEstoque=estoque_item.id_item_estoque,
            )
        ],
    )
    return create_pedido(db, payload, usuario.id_usuario)


@pytest.fixture
def sem_email_estoque(monkeypatch):
    """Impede o envio real durante os testes de notificação de estoque."""
    chamadas: list[tuple[str, list]] = []

    def falso_envio(to_email: str, itens: list) -> None:
        chamadas.append((to_email, list(itens)))

    monkeypatch.setattr(eventos, "send_estoque_baixo_email", falso_envio)
    return chamadas


@pytest.fixture
def destinatarios_estoque(db_session: Session):
    return (
        _usuario(db_session, "Diretora Padrao", 1),
        _usuario(db_session, "Admin Padrao", 3),
    )


class TestPedidoCriado:
    def test_notifica_diretores_com_link_admin_e_exclui_criador(
        self, db_session: Session, turma, usuario, usuario_professor
    ):
        outro_diretor = _usuario(db_session, "Diretora Extra", 1)

        pedido = _criar_pedido(db_session, turma, usuario_professor)

        notificacoes = db_session.query(Notificacao).filter(Notificacao.tipo == "pedido_criado").all()
        assert {item.id_usuario for item in notificacoes} == {usuario.id_usuario, outro_diretor.id_usuario}
        assert all(item.link == "/admin/logistico/pedidos" for item in notificacoes)
        assert all(str(pedido.id_pedido) in item.mensagem for item in notificacoes)
        assert all("Professor Teste" in item.mensagem for item in notificacoes)
        assert all(str(turma.id_turma) in item.mensagem for item in notificacoes)
        assert all(item.id_usuario != usuario_professor.id_usuario for item in notificacoes)

    def test_criado_por_diretor_usa_link_admin_e_nao_notifica_o_proprio_criador(
        self, db_session: Session, turma, usuario
    ):
        outro_diretor = _usuario(db_session, "Diretora Extra", 1)

        _criar_pedido(db_session, turma, usuario)

        notificacoes = _notificacoes(db_session, outro_diretor.id_usuario, "pedido_criado")
        assert len(notificacoes) == 1
        assert notificacoes[0].link == "/admin/logistico/pedidos"
        assert _notificacoes(db_session, usuario.id_usuario, "pedido_criado") == []

    def test_criado_por_admin_usa_link_admin(self, db_session: Session, turma):
        admin = _usuario(db_session, "Admin Criador", 3)
        diretor = _usuario(db_session, "Diretora Extra", 1)

        _criar_pedido(db_session, turma, admin)

        notificacoes = _notificacoes(db_session, diretor.id_usuario, "pedido_criado")
        assert len(notificacoes) == 1
        assert notificacoes[0].link == "/admin/logistico/pedidos"


class TestPedidoAprovado:
    def test_notifica_solicitante_e_admins_mantendo_um_unico_email(
        self, db_session: Session, turma, usuario_professor, estoque_item, monkeypatch
    ):
        admin = _usuario(db_session, "Admin Aprovacao", 3)
        pedido = _criar_pedido(db_session, turma, usuario_professor, estoque_item, 5)
        emails: list[tuple] = []
        monkeypatch.setattr(
            pedido_service,
            "send_pedido_aprovado_email",
            lambda *args: emails.append(args),
        )

        aprovar_pedido(db_session, pedido.id_pedido)

        assert len(emails) == 1
        assert emails[0][0] == usuario_professor.email
        solicitante = _notificacoes(db_session, usuario_professor.id_usuario, "pedido_aprovado")
        administrador = _notificacoes(db_session, admin.id_usuario, "pedido_aprovado")
        assert len(solicitante) == 1
        assert solicitante[0].link == "/academico/pedidos"
        assert len(administrador) == 1
        assert administrador[0].link == "/admin/logistico/pedidos"

    def test_update_status_aprovado_notifica_e_nao_duplica_email(
        self, db_session: Session, turma, usuario_professor, estoque_item, monkeypatch
    ):
        _usuario(db_session, "Admin Aprovacao", 3)
        pedido = _criar_pedido(db_session, turma, usuario_professor, estoque_item, 5)
        emails: list[tuple] = []
        monkeypatch.setattr(
            pedido_service,
            "send_pedido_aprovado_email",
            lambda *args: emails.append(args),
        )

        update_pedido_status(db_session, pedido.id_pedido, PedidoUpdateSchema(status=1))

        assert len(emails) == 1
        assert len(_notificacoes(db_session, usuario_professor.id_usuario, "pedido_aprovado")) == 1

    def test_solicitante_admin_recebe_uma_unica_notificacao(
        self, db_session: Session, turma, estoque_item, monkeypatch
    ):
        admin = _usuario(db_session, "Admin Solicitante", 3)
        monkeypatch.setattr(
            pedido_service, "send_pedido_aprovado_email", lambda *args: None
        )
        pedido = _criar_pedido(db_session, turma, admin, estoque_item, 5)

        aprovar_pedido(db_session, pedido.id_pedido)

        notificacoes = _notificacoes(db_session, admin.id_usuario, "pedido_aprovado")
        assert len(notificacoes) == 1
        assert notificacoes[0].link == "/admin/logistico/pedidos"

    def test_transicoes_invalidas_nao_notificam_nem_enviam_email(
        self, db_session: Session, turma, usuario_professor, estoque_item, monkeypatch
    ):
        pedido = _criar_pedido(db_session, turma, usuario_professor, estoque_item, 1)
        emails: list[tuple] = []
        monkeypatch.setattr(
            pedido_service,
            "send_pedido_aprovado_email",
            lambda *args: emails.append(args),
        )

        with pytest.raises(pedido_service.PedidoInvalidTransitionError):
            comprar_pedido(db_session, pedido.id_pedido, PedidoCompraSchema(itens=[]))
        aprovar_pedido(db_session, pedido.id_pedido)
        with pytest.raises(pedido_service.PedidoInvalidTransitionError):
            aprovar_pedido(db_session, pedido.id_pedido)

        assert len(emails) == 1
        assert len(_notificacoes(db_session, usuario_professor.id_usuario, "pedido_aprovado")) == 1
        assert _notificacoes(db_session, usuario_professor.id_usuario, "pedido_comprado") == []


class TestPedidoCompradoEEntregue:
    def test_comprar_pelos_dois_caminhos_notifica_solicitante(
        self, db_session: Session, turma, usuario_professor, estoque_item, monkeypatch
    ):
        monkeypatch.setattr(
            pedido_service, "send_pedido_aprovado_email", lambda *args: None
        )
        primeiro = _criar_pedido(db_session, turma, usuario_professor, estoque_item, 1)
        segundo = _criar_pedido(db_session, turma, usuario_professor, estoque_item, 1)
        aprovar_pedido(db_session, primeiro.id_pedido)
        aprovar_pedido(db_session, segundo.id_pedido)

        comprar_pedido(db_session, primeiro.id_pedido, PedidoCompraSchema(itens=[]))
        update_pedido_status(db_session, segundo.id_pedido, PedidoUpdateSchema(status=2))

        notificacoes = _notificacoes(db_session, usuario_professor.id_usuario, "pedido_comprado")
        assert len(notificacoes) == 2
        assert all(item.link == "/academico/pedidos" for item in notificacoes)
        assert any(str(primeiro.id_pedido) in item.mensagem for item in notificacoes)
        assert any(str(segundo.id_pedido) in item.mensagem for item in notificacoes)

    def test_entregar_notifica_solicitante_e_nao_gera_alerta_de_estoque(
        self, db_session: Session, turma, usuario_professor, estoque_item, monkeypatch, sem_email_estoque
    ):
        monkeypatch.setattr(
            pedido_service, "send_pedido_aprovado_email", lambda *args: None
        )
        estoque_item.quantidade_disponivel = 5
        estoque_item.estoque_minimo = 10
        db_session.commit()
        pedido = _criar_pedido(db_session, turma, usuario_professor, estoque_item, 1)
        aprovar_pedido(db_session, pedido.id_pedido)
        comprar_pedido(db_session, pedido.id_pedido, PedidoCompraSchema(itens=[]))

        entregar_pedido(db_session, pedido.id_pedido)

        notificacoes = _notificacoes(db_session, usuario_professor.id_usuario, "pedido_entregue")
        assert len(notificacoes) == 1
        assert notificacoes[0].link == "/academico/pedidos"
        assert db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").count() == 0
        assert sem_email_estoque == []


class TestEstoqueBaixo:
    def test_dar_baixa_cruza_minimo_consolida_in_app_e_email(
        self, db_session: Session, estoque_item, sem_email_estoque, usuario_professor
    ):
        diretor = _usuario(db_session, "Diretora Estoque", 1)
        admin = _usuario(db_session, "Admin Estoque", 3)
        _usuario(db_session, "Sem Email", 1, sem_email=True)

        dar_baixa(db_session, estoque_item.id_item_estoque, 95, "Consumo")

        for usuario_id in (diretor.id_usuario, admin.id_usuario):
            notificacoes = _notificacoes(db_session, usuario_id, "estoque_baixo")
            assert len(notificacoes) == 1
            assert notificacoes[0].link == "/admin/logistico/estoque"
            assert "1 item" in notificacoes[0].titulo
            assert len(notificacoes[0].mensagem) <= 500
            assert "Teste Item" in notificacoes[0].mensagem
        assert len(sem_email_estoque) == 2
        assert {email for email, _itens in sem_email_estoque} == {diretor.email, admin.email}
        assert all("Teste Item" in " ".join(item.nome for item in itens) for _email, itens in sem_email_estoque)
        assert _notificacoes(db_session, usuario_professor.id_usuario, "estoque_baixo") == []

    def test_sem_queda_abaixo_do_minimo_nao_alerta(
        self, db_session: Session, estoque_item, sem_email_estoque
    ):
        dar_baixa(db_session, estoque_item.id_item_estoque, 90, "Consumo")

        assert db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").count() == 0
        assert sem_email_estoque == []

    def test_item_ja_baixo_que_cai_mais_nao_repete_alerta(
        self, db_session: Session, estoque_item, sem_email_estoque
    ):
        estoque_item.quantidade_disponivel = 5
        db_session.commit()

        dar_baixa(db_session, estoque_item.id_item_estoque, 2, "Consumo")

        assert db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").count() == 0
        assert sem_email_estoque == []

    def test_nova_queda_apos_reposicao_gera_novo_alerta(
        self, db_session: Session, estoque_item, sem_email_estoque, destinatarios_estoque
    ):
        dar_baixa(db_session, estoque_item.id_item_estoque, 95, "Consumo")
        update_estoque(
            db_session,
            estoque_item.id_item_estoque,
            EstoqueUpdateSchema(quantidadeDisponivel=50),
        )
        assert db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").count() == 2

        dar_baixa(db_session, estoque_item.id_item_estoque, 45, "Consumo")

        assert db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").count() == 4
        assert len(sem_email_estoque) == 4

    def test_minimo_nulo_nunca_alerta(
        self, db_session: Session, estoque_item, sem_email_estoque
    ):
        update_estoque(db_session, estoque_item.id_item_estoque, EstoqueUpdateSchema(estoqueMinimo=None))
        db_session.refresh(estoque_item)

        dar_baixa(db_session, estoque_item.id_item_estoque, 100, "Consumo total")

        assert db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").count() == 0
        assert sem_email_estoque == []

    def test_update_estoque_quantidade_e_minimo_geram_alerta(
        self, db_session: Session, estoque_item, sem_email_estoque, destinatarios_estoque
    ):
        update_estoque(
            db_session,
            estoque_item.id_item_estoque,
            EstoqueUpdateSchema(quantidadeDisponivel=5),
        )
        assert db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").count() == 2

        update_estoque(
            db_session,
            estoque_item.id_item_estoque,
            EstoqueUpdateSchema(quantidadeDisponivel=50),
        )
        update_estoque(
            db_session,
            estoque_item.id_item_estoque,
            EstoqueUpdateSchema(estoqueMinimo=60),
        )
        assert db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").count() == 4

    def test_create_estoque_ja_abaixo_do_minimo_alerta(
        self, db_session: Session, sem_email_estoque, destinatarios_estoque
    ):
        criado = create_estoque(
            db_session,
            EstoqueCreateSchema(
                nomeItem="Novo Item",
                quantidadeDisponivel=2,
                unidade="cx",
                estoqueMinimo=5,
            ),
        )

        notificacoes = db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").all()
        assert len(notificacoes) == 2
        assert "Novo Item" in notificacoes[0].mensagem
        assert criado.quantidade_disponivel == 2
        assert len(sem_email_estoque) == 2

    def test_aprovacao_com_varios_itens_gera_um_email_consolidado(
        self, db_session: Session, turma, usuario_professor, estoque_item, monkeypatch, sem_email_estoque, destinatarios_estoque
    ):
        monkeypatch.setattr(
            pedido_service, "send_pedido_aprovado_email", lambda *args: None
        )
        outro_item = create_estoque(
            db_session,
            EstoqueCreateSchema(
                nomeItem="Segundo Item", quantidadeDisponivel=20, unidade="un", estoqueMinimo=10
            ),
        )
        estoque_item.quantidade_disponivel = 12
        db_session.commit()
        payload = PedidoCreateSchema(
            idTurma=turma.id_turma,
            itens=[
                ItemPedidoCreateSchema(
                    nomeItem=estoque_item.nome_item,
                    quantidade=10,
                    idItemEstoque=estoque_item.id_item_estoque,
                ),
                ItemPedidoCreateSchema(
                    nomeItem=outro_item.nome_item,
                    quantidade=15,
                    idItemEstoque=outro_item.id_item_estoque,
                ),
            ],
        )
        pedido = create_pedido(db_session, payload, usuario_professor.id_usuario)

        aprovar_pedido(db_session, pedido.id_pedido)

        assert len(sem_email_estoque) == 2
        assert all({item.nome for item in itens} == {"Teste Item", "Segundo Item"} for _email, itens in sem_email_estoque)
        notificacao = db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").first()
        assert "2 itens" in notificacao.titulo

    def test_aprovacao_com_duas_linhas_do_mesmo_item_alerta_uma_vez(
        self,
        db_session: Session,
        turma,
        usuario_professor,
        estoque_item,
        monkeypatch,
        sem_email_estoque,
        destinatarios_estoque,
    ):
        monkeypatch.setattr(
            pedido_service, "send_pedido_aprovado_email", lambda *args: None
        )
        estoque_item.quantidade_disponivel = 10
        estoque_item.estoque_minimo = 5
        db_session.commit()

        payload = PedidoCreateSchema(
            idTurma=turma.id_turma,
            itens=[
                ItemPedidoCreateSchema(
                    nomeItem=estoque_item.nome_item,
                    quantidade=6,
                    idItemEstoque=estoque_item.id_item_estoque,
                ),
                ItemPedidoCreateSchema(
                    nomeItem=estoque_item.nome_item,
                    quantidade=4,
                    idItemEstoque=estoque_item.id_item_estoque,
                ),
            ],
        )
        pedido = create_pedido(db_session, payload, usuario_professor.id_usuario)

        aprovar_pedido(db_session, pedido.id_pedido)

        notificacoes = (
            db_session.query(Notificacao)
            .filter(Notificacao.tipo == "estoque_baixo")
            .all()
        )
        assert len(notificacoes) == 2
        assert all(notificacao.mensagem.count("Teste Item") == 1 for notificacao in notificacoes)
        assert len(sem_email_estoque) == 2

    def test_mensagem_in_app_lista_ate_cinco_itens_e_trunca(
        self, db_session: Session, sem_email_estoque, destinatarios_estoque
    ):
        itens = [
            eventos.ItemEstoqueBaixo(nome=f"Item {indice}", saldo=1, minimo=5, unidade="un")
            for indice in range(7)
        ]

        eventos.notificar_estoque_baixo(db_session, itens)

        notificacao = db_session.query(Notificacao).filter(Notificacao.tipo == "estoque_baixo").first()
        assert len(notificacao.mensagem) <= 500
        assert "e 2 outros itens" in notificacao.mensagem
        assert "Item 4" in notificacao.mensagem
        assert "Item 5" not in notificacao.mensagem

    def test_sem_destinatario_com_email_apenas_loga_e_nao_quebra(
        self, db_session: Session, estoque_item, monkeypatch, caplog
    ):
        monkeypatch.setattr(
            eventos,
            "_usuarios_por_cargo",
            lambda *args, **kwargs: [],
        )

        dar_baixa(db_session, estoque_item.id_item_estoque, 95, "Consumo")

        db_session.refresh(estoque_item)
        assert estoque_item.quantidade_disponivel == 5
        assert "Nenhum destinatário" in caplog.text

    def test_falha_de_email_nao_reverte_baixa(
        self, db_session: Session, estoque_item, monkeypatch, caplog, destinatarios_estoque
    ):
        def falha(_email: str, _itens: list) -> None:
            raise email_pkg.EmailDeliveryError("provedor fora do ar")

        monkeypatch.setattr(eventos, "send_estoque_baixo_email", falha)

        resultado = dar_baixa(db_session, estoque_item.id_item_estoque, 95, "Consumo")

        assert resultado.quantidade_disponivel == 5
        assert "Falha ao enviar e-mail de estoque baixo" in caplog.text

    def test_falha_de_notificacao_in_app_nao_reverte_baixa(
        self, db_session: Session, estoque_item, monkeypatch, caplog, destinatarios_estoque
    ):
        def falha(*_args, **_kwargs) -> int:
            raise RuntimeError("inbox indisponível")

        monkeypatch.setattr(eventos, "notificar_usuarios", falha)

        resultado = dar_baixa(db_session, estoque_item.id_item_estoque, 95, "Consumo")

        db_session.refresh(resultado)
        assert resultado.quantidade_disponivel == 5
        assert "inbox indisponível" in caplog.text

    def test_background_tasks_sao_usadas_quando_disponiveis(
        self, db_session: Session, estoque_item, monkeypatch, destinatarios_estoque
    ):
        chamadas: list[tuple[str, list]] = []
        monkeypatch.setattr(
            eventos,
            "send_estoque_baixo_email",
            lambda email, itens: chamadas.append((email, list(itens))),
        )
        tasks = BackgroundTasks()

        dar_baixa(db_session, estoque_item.id_item_estoque, 95, "Consumo", tasks)

        assert chamadas == []
        assert len(tasks.tasks) == 2
        for tarefa in tasks.tasks:
            tarefa.func(*tarefa.args, **tarefa.kwargs)
        assert len(chamadas) == 2
        assert all(itens[0].saldo == 5 for _email, itens in chamadas)


class TestMensagemEmailEstoqueBaixo:
    def test_mensagem_tem_itens_saldo_minimo_e_unidade(self):
        itens = [
            eventos.ItemEstoqueBaixo(nome="Papel A4", saldo=2, minimo=5, unidade="cx"),
            eventos.ItemEstoqueBaixo(nome="Caneta", saldo=0, minimo=3, unidade="un"),
        ]

        subject, body = email_messages.build_estoque_baixo_message(itens)

        assert "2 itens" in subject
        assert "Papel A4" in body
        assert "Caneta" in body
        assert "2" in body and "5" in body and "cx" in body
        assert "0" in body and "3" in body and "un" in body

    def test_service_envia_pelo_provedor_configurado(self, monkeypatch):
        from app.email import service as email_service
        from types import SimpleNamespace

        settings = SimpleNamespace(
            brevo_api_key="",
            smtp_user="",
            email_sender_name="SGA ABACO",
            smtp_host="localhost",
            smtp_port=587,
            smtp_from="noreply@abaco.org.br",
        )
        enviados: dict = {}
        monkeypatch.setattr(email_service, "get_settings", lambda: settings)
        monkeypatch.setattr(
            email_service,
            "console",
            SimpleNamespace(send=lambda to, subject, body: enviados.update(to=to, subject=subject, body=body)),
        )

        email_pkg.send_estoque_baixo_email(
            "diretor@abaco.org.br",
            [eventos.ItemEstoqueBaixo(nome="Papel A4", saldo=2, minimo=5, unidade="cx")],
        )

        assert enviados["to"] == "diretor@abaco.org.br"
        assert "Estoque baixo" in enviados["subject"]
        assert "Papel A4" in enviados["body"]
