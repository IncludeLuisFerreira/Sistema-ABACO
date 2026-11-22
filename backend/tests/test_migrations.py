import importlib.util
from datetime import datetime
from pathlib import Path

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.database import Base
from app.models.estoque import Estoque
from app.models.item_pedido import ItemPedido
from app.models.movimentacao_estoque import MovimentacaoEstoque

BACKEND_DIR = Path(__file__).resolve().parents[1]
MIGRATION_010 = BACKEND_DIR / "alembic" / "versions" / "010_normaliza_nomeitem_estoque.py"


def _script_directory() -> ScriptDirectory:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return ScriptDirectory.from_config(cfg)


def _load_migration_010():
    spec = importlib.util.spec_from_file_location("migration_010", MIGRATION_010)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_single_migration_head() -> None:
    assert _script_directory().get_heads() == ["010"]


def test_migration_chain_is_linear() -> None:
    script = _script_directory()
    expected = [
        "010",
        "009",
        "008",
        "007",
        "006",
        "005",
        "004_add_endereco_to_usuario",
        "b5aaca51a7ff",
        "002",
        "001",
    ]
    chain = []
    rev = script.get_revision("010")
    while rev is not None:
        chain.append(rev.revision)
        down = rev.down_revision
        assert not isinstance(down, (tuple, list)), f"branch em {rev.revision}: {down}"
        rev = script.get_revision(down) if down else None
    assert chain == expected


def test_migration_010_normaliza_e_mescla_duplicatas(tmp_path) -> None:
    db_path = tmp_path / "migracao-010.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        mantido = Estoque(
            nome_item="Papel A4",
            quantidade_disponivel=10,
            unidade="cx",
            estoque_minimo=2,
        )
        duplicata = Estoque(
            nome_item="  Papel   A4  ",
            quantidade_disponivel=5,
            unidade=None,
            estoque_minimo=4,
        )
        session.add_all([mantido, duplicata])
        session.flush()

        session.add(
            MovimentacaoEstoque(
                id_item_estoque=duplicata.id_item_estoque,
                quantidade=-1,
                tipo_movimentacao="baixa_manual",
                justificativa="teste de migration",
                data_movimentacao=datetime.now(),
            )
        )
        session.add(
            ItemPedido(
                id_pedido=1,
                id_item_estoque=duplicata.id_item_estoque,
                nome_item="Papel A4",
                quantidade=1,
            )
        )
        session.commit()
        id_mantido = mantido.id_item_estoque

    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        with Operations.context(context):
            _load_migration_010().upgrade()

    with Session(engine) as session:
        itens = session.query(Estoque).all()
        assert len(itens) == 1
        item = itens[0]
        assert item.nome_item == "Papel A4"
        assert item.quantidade_disponivel == 15
        assert item.estoque_minimo == 4
        assert item.unidade == "cx"

        movimentacao = session.query(MovimentacaoEstoque).one()
        assert movimentacao.id_item_estoque == id_mantido

        item_pedido = session.query(ItemPedido).one()
        assert item_pedido.id_item_estoque == id_mantido

    engine.dispose()


def test_migration_010_conflito_de_unidade_mantem_primeira(tmp_path) -> None:
    db_path = tmp_path / "migracao-010-unidade.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        mantido = Estoque(
            nome_item="Fita adesiva",
            quantidade_disponivel=3,
            unidade="un",
            estoque_minimo=1,
        )
        duplicata = Estoque(
            nome_item="  fita   ADESIVA ",
            quantidade_disponivel=7,
            unidade="cx",
            estoque_minimo=2,
        )
        session.add_all([mantido, duplicata])
        session.commit()

    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        with Operations.context(context):
            _load_migration_010().upgrade()

    with Session(engine) as session:
        itens = session.query(Estoque).all()
        assert len(itens) == 1
        item = itens[0]
        assert item.nome_item == "Fita adesiva"
        assert item.quantidade_disponivel == 10
        assert item.estoque_minimo == 2
        assert item.unidade == "un"

    engine.dispose()
