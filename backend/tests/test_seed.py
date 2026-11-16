import pytest
from sqlalchemy import func

from app.core.config import get_settings
from app.models.curso import Curso
from app.models.estoque import Estoque
from app.models.item_pedido import ItemPedido
from app.models.turma import Turma
from app.models.usuario import Usuario


@pytest.fixture
def seed_passwords(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "seed_admin_password", "senha-admin-teste")
    monkeypatch.setattr(settings, "seed_professor_password", "senha-professor-teste")
    monkeypatch.setattr(settings, "admin_seed_email", "admin@abaco.org.br")
    monkeypatch.setattr(settings, "admin_seed_password", "senha-diretor-teste")
    return settings


def test_run_seed_cria_grafo_completo(db_session, seed_passwords):
    from app.db.seed import run_seed

    counts = run_seed(db_session)

    assert counts["cursos"] == 5
    assert counts["estoque"] == 6
    assert counts["turmas"] == 6
    assert counts["usuarios"] == 6
    assert counts["itens_pedido"] == 5

    estoque_ids = {item.id_item_estoque for item in db_session.query(Estoque).all()}
    itens = db_session.query(ItemPedido).all()
    assert len(itens) == 5
    for item in itens:
        assert item.id_item_estoque in estoque_ids


def test_run_seed_e_idempotente(db_session, seed_passwords):
    from app.db.seed import run_seed

    run_seed(db_session)
    total_usuarios = db_session.query(Usuario).count()
    total_itens = db_session.query(ItemPedido).count()

    second = run_seed(db_session)

    assert all(value == 0 for value in second.values())
    assert db_session.query(Usuario).count() == total_usuarios
    assert db_session.query(ItemPedido).count() == total_itens


def test_run_seed_completa_banco_parcial(db_session, seed_passwords):
    from app.db.seed import run_seed

    db_session.add(
        Usuario(
            nome="Carlos Admin",
            email="admin2@abaco.org.br",
            senha_hash="hash-existente",
            cargo=3,
            primeiro_acesso=False,
        )
    )
    db_session.commit()

    counts = run_seed(db_session)

    assert counts["cursos"] == 5
    assert db_session.query(Usuario).filter(Usuario.email == "admin2@abaco.org.br").count() == 1
    assert db_session.query(Usuario).filter(Usuario.email == "maria@abaco.org.br").count() == 1


def test_run_seed_pula_usuarios_sem_senha(db_session, monkeypatch):
    from app.db.seed import run_seed

    settings = get_settings()
    monkeypatch.setattr(settings, "seed_admin_password", None)
    monkeypatch.setattr(settings, "seed_professor_password", None)
    monkeypatch.setattr(settings, "admin_seed_email", None)
    monkeypatch.setattr(settings, "admin_seed_password", None)

    counts = run_seed(db_session)

    assert counts["cursos"] == 5
    assert counts["estoque"] == 6
    assert counts["usuarios"] == 0
    assert counts["turmas"] == 0
    assert db_session.query(Usuario).count() == 0
    assert db_session.query(Turma).count() == 0


class _SessaoFalsa:
    def __init__(self):
        self.fechada = False
        self.revertida = False

    def rollback(self):
        self.revertida = True

    def close(self):
        self.fechada = True


def _patch_session(monkeypatch):
    import main as main_module

    sessao = _SessaoFalsa()
    monkeypatch.setattr(main_module, "SessionLocal", lambda: sessao)
    return sessao


def test_startup_nao_seeda_com_flag_desligada(monkeypatch):
    from fastapi.testclient import TestClient

    import app.db.seed as seed_module
    from main import app, settings

    chamadas = []
    monkeypatch.setattr(settings, "seed_on_startup", False)
    monkeypatch.setattr(seed_module, "run_seed", lambda db: chamadas.append(db) or {})
    _patch_session(monkeypatch)

    with TestClient(app):
        pass

    assert chamadas == []


def test_startup_nao_seeda_em_producao(monkeypatch):
    from fastapi.testclient import TestClient

    import app.db.seed as seed_module
    from main import app, settings

    chamadas = []
    monkeypatch.setattr(settings, "seed_on_startup", True)
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(seed_module, "run_seed", lambda db: chamadas.append(db) or {})
    _patch_session(monkeypatch)

    with TestClient(app):
        pass

    assert chamadas == []


def test_startup_chama_seed_com_flag_ligada(monkeypatch):
    from fastapi.testclient import TestClient

    import app.db.seed as seed_module
    from main import app, settings

    chamadas = []
    monkeypatch.setattr(settings, "seed_on_startup", True)
    monkeypatch.setattr(settings, "environment", "development")
    monkeypatch.setattr(seed_module, "run_seed", lambda db: chamadas.append(db) or {})
    _patch_session(monkeypatch)

    with TestClient(app):
        pass

    assert len(chamadas) == 1


def test_startup_nao_quebra_quando_seed_falha(monkeypatch):
    from fastapi.testclient import TestClient

    import app.db.seed as seed_module
    from main import app, settings

    def _falha(_db):
        raise RuntimeError("boom")

    monkeypatch.setattr(settings, "seed_on_startup", True)
    monkeypatch.setattr(settings, "environment", "development")
    monkeypatch.setattr(seed_module, "run_seed", _falha)
    sessao = _patch_session(monkeypatch)

    with TestClient(app):
        pass

    assert sessao.fechada is True


def test_run_seed_reaproveita_estoque_com_caixa_diferente(db_session, seed_passwords):
    from app.db.seed import run_seed

    db_session.add(
        Estoque(nome_item="CANETA ESFERográfica", quantidade_disponivel=1, unidade="un", estoque_minimo=0)
    )
    db_session.commit()

    counts = run_seed(db_session)

    assert counts["estoque"] == 5
    assert db_session.query(Estoque).count() == 6
    assert (
        db_session.query(Estoque)
        .filter(func.lower(Estoque.nome_item) == "caneta esferográfica")
        .count()
        == 1
    )


def test_run_seed_nao_duplica_usuario_com_email_em_caixa_diferente(db_session, seed_passwords):
    from app.db.seed import run_seed

    db_session.add(
        Usuario(
            nome="Maria Existente",
            email="Maria@Abaco.org.br",
            senha_hash="hash-existente",
            cargo=2,
            primeiro_acesso=False,
        )
    )
    db_session.commit()

    counts = run_seed(db_session)

    assert counts["usuarios"] == 5
    assert db_session.query(Usuario).filter(func.lower(Usuario.email) == "maria@abaco.org.br").count() == 1


def test_run_seed_respeita_estoque_com_ids_deslocados(db_session, seed_passwords):
    from app.db.seed import run_seed

    for indice in range(3):
        db_session.add(
            Estoque(
                nome_item=f"Item avulso {indice}",
                quantidade_disponivel=1,
                unidade="un",
                estoque_minimo=0,
            )
        )
    db_session.commit()

    run_seed(db_session)

    estoque_por_id = {item.id_item_estoque: item.nome_item.lower() for item in db_session.query(Estoque).all()}
    itens = db_session.query(ItemPedido).all()
    assert len(itens) == 5
    for item in itens:
        assert estoque_por_id[item.id_item_estoque] == item.nome_item.lower()
        assert not estoque_por_id[item.id_item_estoque].startswith("item avulso")

