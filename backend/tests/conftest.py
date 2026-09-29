import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.estoque import Estoque
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.models.usuario import Usuario


@pytest.fixture
def db_session():
    # TODO: testes só em SQLite; JSONB e with_for_update não são cobertos
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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


from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.db.database import get_db
from main import app


@pytest.fixture
def api_client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def outro_professor(db_session) -> Usuario:
    professor = Usuario(
        nome="Outro Professor",
        email="outro.prof@abaco.org.br",
        senha_hash="$2b$12$6rgU3Nzuu7ZMdPqt7O1kZOkLTZGUQEKd9BsN3Oh/wdZdNvXTfAvha",
        cargo=2,
    )
    db_session.add(professor)
    db_session.commit()
    db_session.refresh(professor)
    return professor


@pytest.fixture
def turma_outro_professor(db_session, curso, outro_professor) -> Turma:
    t = Turma(
        capacidade=10,
        id_curso=curso.id_curso,
        id_professor=outro_professor.id_usuario,
        dias_aula="Ter/Qui",
    )
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


@pytest.fixture
def professor_headers_factory():
    def _make(usuario: Usuario) -> dict:
        token = create_access_token(subject=str(usuario.id_usuario), cargo=2)
        return {"Authorization": f"Bearer {token}"}

    return _make


@pytest.fixture
def diretor_headers() -> dict:
    token = create_access_token(subject="1", cargo=1)
    return {"Authorization": f"Bearer {token}"}
