import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import create_access_token
from app.db.database import Base, get_db
from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.estoque import Estoque
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.models.usuario import Usuario


@pytest.fixture
def db_session():
    # TODO: testes só em SQLite; JSONB e with_for_update não são cobertos
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def usuario(db_session: Session) -> Usuario:
    u = Usuario(
        nome="Teste Usuario",
        email="teste@abaco.org.br",
        senha_hash="$2b$12$6rgU3Nzuu7ZMdPqt7O1kZOkLTZGUQEKd9BsN3Oh/wdZdNvXTfAvha",
        cargo=1,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture
def usuario_professor(db_session: Session) -> Usuario:
    u = Usuario(
        nome="Professor Teste",
        email="prof@abaco.org.br",
        senha_hash="$2b$12$6rgU3Nzuu7ZMdPqt7O1kZOkLTZGUQEKd9BsN3Oh/wdZdNvXTfAvha",
        cargo=2,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture
def aluno(db_session: Session) -> Aluno:
    a = Aluno(nome="Aluno Teste", telefone="11999999999")
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)
    return a


@pytest.fixture
def curso(db_session: Session) -> Curso:
    c = Curso(nome_curso="Curso Teste")
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture
def turma(db_session: Session, curso: Curso, usuario_professor: Usuario) -> Turma:
    t = Turma(
        capacidade=30,
        id_curso=curso.id_curso,
        id_professor=usuario_professor.id_usuario,
        dias_aula="Seg/Qua/Sex",
    )
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


@pytest.fixture
def matricula_ativa(db_session: Session, aluno: Aluno, turma: Turma) -> Matricula:
    m = Matricula(id_aluno=aluno.id_aluno, id_turma=turma.id_turma, status=0)
    db_session.add(m)
    db_session.commit()
    db_session.refresh(m)
    return m


@pytest.fixture
def estoque_item(db_session: Session) -> Estoque:
    item = Estoque(
        nome_item="Teste Item",
        quantidade_disponivel=100,
        unidade="un",
        estoque_minimo=10,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


def _enable_sqlite_foreign_keys(dbapi_connection, _record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _make_isolated_sqlite_engine(db_path) -> object:
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


@pytest.fixture
def api_client(tmp_path):
    """TestClient com banco SQLite isolado (get_db sobrescrito) e limiter desativado."""
    from main import app

    engine = _make_isolated_sqlite_engine(tmp_path / "test_api.db")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    from app.core.limiter import limiter

    previous_enabled = limiter.enabled
    limiter.enabled = False
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        app.dependency_overrides.pop(get_db, None)
        limiter.enabled = previous_enabled
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _headers_for_cargo(cargo: int, subject: str = "1") -> dict:
    token = create_access_token(subject=subject, cargo=cargo)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def director_headers() -> dict:
    return _headers_for_cargo(1)


@pytest.fixture
def professor_headers() -> dict:
    return _headers_for_cargo(2, subject="2")


@pytest.fixture
def admin_headers() -> dict:
    return _headers_for_cargo(3, subject="3")


@pytest.fixture
def guest_headers() -> dict:
    """Token válido, porém sem cargo reconhecido — deve ser tratado como sem privilégios."""
    return _headers_for_cargo(0, subject="9")


def _create_usuario(client, headers, nome: str, email: str, cargo: int) -> dict:
    return client.post(
        "/api/v1/usuarios",
        json={"nome": nome, "email": email, "senha": "senha123", "cargo": cargo},
        headers=headers,
    ).json()


@pytest.fixture
def seeded(api_client, director_headers):
    """Cria um grafo acadêmico mínimo via API e devolve ids e tokens derivados dos ids."""
    client = api_client
    headers = director_headers
    professor = _create_usuario(client, headers, "Professor Teste", "prof@abaco.org.br", 2)
    director = _create_usuario(client, headers, "Diretora Teste", "diretora@abaco.org.br", 1)
    aluno = client.post("/api/v1/alunos", json={"nome": "Aluno Teste"}, headers=headers).json()
    curso = client.post("/api/v1/cursos", json={"nomeCurso": "Curso Teste"}, headers=headers).json()
    turma = client.post(
        "/api/v1/turmas",
        json={
            "capacidade": 2,
            "idCurso": curso["idCurso"],
            "idProfessor": professor["idUsuario"],
            "diasAula": "Seg",
        },
        headers=headers,
    ).json()
    matricula = client.post(
        "/api/v1/matriculas",
        json={"idAluno": aluno["idAluno"], "idTurma": turma["idTurma"]},
        headers=headers,
    ).json()
    estoque = client.post(
        "/api/v1/estoque",
        json={"nomeItem": "Papel A4", "quantidadeDisponivel": 10, "unidade": "cx", "estoqueMinimo": 2},
        headers=headers,
    ).json()
    return {
        "client": client,
        "headers": headers,
        "professor": professor,
        "director": director,
        "aluno": aluno,
        "curso": curso,
        "turma": turma,
        "matricula": matricula,
        "estoque": estoque,
        "professor_headers": _headers_for_cargo(2, str(professor["idUsuario"])),
        "director_headers": _headers_for_cargo(1, str(director["idUsuario"])),
    }
