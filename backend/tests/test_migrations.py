from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _script_directory() -> ScriptDirectory:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return ScriptDirectory.from_config(cfg)


def test_single_migration_head() -> None:
    assert _script_directory().get_heads() == ["006"]


def test_migration_chain_is_linear() -> None:
    script = _script_directory()
    expected = [
        "006",
        "005",
        "004_add_endereco_to_usuario",
        "b5aaca51a7ff",
        "002",
        "001",
    ]
    chain = []
    rev = script.get_revision("006")
    while rev is not None:
        chain.append(rev.revision)
        down = rev.down_revision
        assert not isinstance(down, (tuple, list)), f"branch em {rev.revision}: {down}"
        rev = script.get_revision(down) if down else None
    assert chain == expected
