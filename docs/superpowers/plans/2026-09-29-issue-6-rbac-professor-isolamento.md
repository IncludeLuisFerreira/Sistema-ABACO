# Issue 6 — RBAC Professor: Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restringir o perfil Professor (cargo 2) às suas próprias turmas e alunos em todas as rotas por turma/matrícula, retornando 403 para acesso a turma de terceiros, sem alterar o acesso de Diretor (1) e Administrativo (3).

**Architecture:** Um módulo central `app/core/authorization.py` concentra a política de posse de turma, expondo funções puras (`assert_*`), tradutoras HTTP (`enforce_*`) e dependências FastAPI (`require_*`). Os routers consomem essas dependências; `POST /notas` e `POST /presencas` validam o `idTurma` do corpo via `enforce_turma_access`. Listagens globais de turmas e matrículas deixam de aceitar cargo 2.

**Tech Stack:** FastAPI, SQLAlchemy, pytest, pytest-cov, SQLite (testes unitários), JWT.

**Spec:** `docs/superpowers/specs/2026-09-29-issue-6-rbac-professor-isolamento-design.md`
**Branch:** `6-sprint-1-rbac-restringir-acesso-professor-propria-turma-e-alunos`

---

## Pré-requisitos de execução

- Trabalhar a partir da raiz do repositório.
- Os testes de API existentes (`tests/test_api_endpoints.py`) usam o banco real. É preciso ter
  PostgreSQL acessível em `localhost:5432` (container `sga_database`):
  ```bash
  docker start sga_database
  ```
- Todos os comandos de teste são executados dentro de `backend/`. Prefixo de ambiente:
  ```bash
  DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test
  ```

---

## Task 0: Configuração de testes e cobertura

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/pytest.ini`
- Modify: `.gitignore`

- [ ] **Step 1: Adicionar `pytest-cov` às dependências**

Acrescentar ao final de `backend/requirements.txt`:

```
pytest-cov==5.0.0
```

- [ ] **Step 2: Configurar cobertura no pytest**

Substituir todo o conteúdo de `backend/pytest.ini` por:

```ini
[pytest]
testpaths = tests
pythonpath = .
addopts = --cov=app --cov-report=term-missing
```

Nota: o gate `--cov-fail-under=70` é aplicado apenas na verificação final (Task 5),
porque o baseline atual é 69,62% e só deve passar após os novos testes das Tasks 1–4.

- [ ] **Step 3: Ignorar artefatos de ambiente e cobertura**

Acrescentar ao final de `.gitignore`:

```
# Ambientes virtuais e cobertura
.venv/
.coverage
htmlcov/
```

- [ ] **Step 4: Ambiente virtual**

Há um venv já preparado em `/tmp/opencode/venv-abaco` com todas as dependências e
`pytest-cov`, usado nos comandos abaixo. (Alternativamente, criar `backend/.venv` com
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` e ajustar os comandos.)

Run (a partir de `backend/`):

```bash
/tmp/opencode/venv-abaco/bin/python -m pytest --version
```

Expected: versão do pytest exibida sem erro.

- [ ] **Step 5: Rodar a suíte para medir o baseline**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest -q
```

Expected: `102 passed` e `TOTAL ... 70%` (69,62% real; sem gate nesta etapa).

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/pytest.ini .gitignore
git commit -m "test: configurar pytest-cov e meta de cobertura"
```

---

## Task 1: Módulo de autorização por turma

**Files:**
- Create: `backend/app/core/authorization.py`
- Test: `backend/tests/test_authorization.py`

- [ ] **Step 1: Escrever os testes que falham**

Criar `backend/tests/test_authorization.py` com:

```python
import pytest
from fastapi import HTTPException

from app.core.authorization import (
    TurmaAccessDeniedError,
    assert_matricula_access,
    assert_turma_access,
    enforce_matricula_access,
    enforce_turma_access,
    get_user_id,
    is_privileged,
)
from app.models.matricula import Matricula
from app.models.usuario import Usuario
from app.services.matricula_service import MatriculaNotFoundError
from app.services.turma_service import TurmaNotFoundError


def _criar_professor(db_session, email: str) -> Usuario:
    professor = Usuario(nome="Professor Secundário", email=email, senha_hash="x", cargo=2)
    db_session.add(professor)
    db_session.commit()
    db_session.refresh(professor)
    return professor


class TestHelpers:
    def test_is_privileged_diretor_e_admin(self):
        assert is_privileged({"cargo": 1}) is True
        assert is_privileged({"cargo": 3}) is True
        assert is_privileged({"cargo": 2}) is False

    def test_get_user_id_converte_sub(self):
        assert get_user_id({"sub": "7"}) == 7
        assert get_user_id({}) == 0


class TestAssertTurmaAccess:
    def test_diretor_acessa_qualquer_turma(self, db_session, turma):
        assert assert_turma_access(db_session, turma.id_turma, {"sub": "999", "cargo": 1}).id_turma == turma.id_turma

    def test_administrativo_acessa_qualquer_turma(self, db_session, turma):
        assert assert_turma_access(db_session, turma.id_turma, {"sub": "999", "cargo": 3}).id_turma == turma.id_turma

    def test_professor_dono_acessa(self, db_session, turma, usuario_professor):
        user = {"sub": str(usuario_professor.id_usuario), "cargo": 2}
        assert assert_turma_access(db_session, turma.id_turma, user).id_turma == turma.id_turma

    def test_professor_terceiro_recebe_negado(self, db_session, turma):
        outro = _criar_professor(db_session, "terceiro1@abaco.org.br")
        user = {"sub": str(outro.id_usuario), "cargo": 2}
        with pytest.raises(TurmaAccessDeniedError):
            assert_turma_access(db_session, turma.id_turma, user)

    def test_turma_inexistente_recebe_not_found(self, db_session):
        with pytest.raises(TurmaNotFoundError):
            assert_turma_access(db_session, 9999, {"sub": "1", "cargo": 1})


class TestAssertMatriculaAccess:
    def test_professor_dono_acessa(self, db_session, matricula_ativa, usuario_professor):
        user = {"sub": str(usuario_professor.id_usuario), "cargo": 2}
        result = assert_matricula_access(db_session, matricula_ativa.id_matricula, user)
        assert result.id_matricula == matricula_ativa.id_matricula

    def test_professor_terceiro_recebe_negado(self, db_session, matricula_ativa):
        outro = _criar_professor(db_session, "terceiro2@abaco.org.br")
        user = {"sub": str(outro.id_usuario), "cargo": 2}
        with pytest.raises(TurmaAccessDeniedError):
            assert_matricula_access(db_session, matricula_ativa.id_matricula, user)

    def test_matricula_inexistente_recebe_not_found(self, db_session):
        with pytest.raises(MatriculaNotFoundError):
            assert_matricula_access(db_session, 9999, {"sub": "1", "cargo": 1})


class TestEnforceTurmaAccess:
    def test_negado_vira_403(self, db_session, turma):
        outro = _criar_professor(db_session, "terceiro3@abaco.org.br")
        user = {"sub": str(outro.id_usuario), "cargo": 2}
        with pytest.raises(HTTPException) as exc:
            enforce_turma_access(db_session, turma.id_turma, user)
        assert exc.value.status_code == 403

    def test_inexistente_vira_404(self, db_session):
        with pytest.raises(HTTPException) as exc:
            enforce_turma_access(db_session, 9999, {"sub": "1", "cargo": 1})
        assert exc.value.status_code == 404


class TestEnforceMatriculaAccess:
    def test_matricula_inexistente_vira_404(self, db_session):
        with pytest.raises(HTTPException) as exc:
            enforce_matricula_access(db_session, 9999, {"sub": "1", "cargo": 1})
        assert exc.value.status_code == 404

    def test_matricula_de_turma_inexistente_vira_404(self, db_session):
        matricula = Matricula(id_aluno=1, id_turma=9999, status=0)
        db_session.add(matricula)
        db_session.commit()
        db_session.refresh(matricula)
        with pytest.raises(HTTPException) as exc:
            enforce_matricula_access(db_session, matricula.id_matricula, {"sub": "1", "cargo": 1})
        assert exc.value.status_code == 404
```

- [ ] **Step 2: Rodar os testes para ver falhar**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest tests/test_authorization.py -q
```

Expected: FAIL com `ModuleNotFoundError: No module named 'app.core.authorization'`.

- [ ] **Step 3: Implementar o módulo**

Criar `backend/app/core/authorization.py` com:

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.services.matricula_service import MatriculaNotFoundError
from app.services.turma_service import TurmaNotFoundError


ACCESS_DENIED_DETAIL = "Acesso negado. Você não tem permissão para acessar este recurso."


class TurmaAccessDeniedError(Exception):
    pass


def is_privileged(current_user: dict) -> bool:
    return int(current_user.get("cargo", 0) or 0) in (1, 3)


def get_user_id(current_user: dict) -> int:
    return int(current_user.get("sub", 0) or 0)


def assert_turma_access(db: Session, turma_id: int, current_user: dict) -> Turma:
    turma = db.query(Turma).filter(Turma.id_turma == turma_id).first()
    if not turma:
        raise TurmaNotFoundError
    if is_privileged(current_user) or get_user_id(current_user) == turma.id_professor:
        return turma
    raise TurmaAccessDeniedError


def assert_matricula_access(db: Session, matricula_id: int, current_user: dict) -> Matricula:
    matricula = db.query(Matricula).filter(Matricula.id_matricula == matricula_id).first()
    if not matricula:
        raise MatriculaNotFoundError
    assert_turma_access(db, matricula.id_turma, current_user)
    return matricula


def enforce_turma_access(db: Session, turma_id: int, current_user: dict) -> Turma:
    try:
        return assert_turma_access(db, turma_id, current_user)
    except TurmaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada") from exc
    except TurmaAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ACCESS_DENIED_DETAIL) from exc


def enforce_matricula_access(db: Session, matricula_id: int, current_user: dict) -> Matricula:
    try:
        return assert_matricula_access(db, matricula_id, current_user)
    except MatriculaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula não encontrada") from exc
    except TurmaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada") from exc
    except TurmaAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ACCESS_DENIED_DETAIL) from exc


def require_turma_access(
    turma_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Turma:
    return enforce_turma_access(db, turma_id, current_user)


def require_matricula_access(
    matricula_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Matricula:
    return enforce_matricula_access(db, matricula_id, current_user)
```

- [ ] **Step 4: Rodar os testes para ver passar**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest tests/test_authorization.py -q
```

Expected: `14 passed`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/authorization.py backend/tests/test_authorization.py
git commit -m "feat: módulo central de autorização por turma"
```

---

## Task 2: RBAC em turmas e listagens globais

**Files:**
- Modify: `backend/tests/conftest.py`
- Create: `backend/tests/test_rbac_turmas.py`
- Modify: `backend/app/api/v1/turmas.py`
- Modify: `backend/app/api/v1/matriculas.py`

- [ ] **Step 1: Adicionar fixtures compartilhadas ao conftest**

Acrescentar ao final de `backend/tests/conftest.py`:

```python
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
```

- [ ] **Step 2: Escrever os testes de RBAC de turmas e listagens**

Criar `backend/tests/test_rbac_turmas.py` com:

```python
class TestTurmasRbac:
    def test_professor_acessa_propria_turma(
        self, api_client, turma, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get(f"/api/v1/turmas/{turma.id_turma}", headers=headers)
        assert response.status_code == 200
        assert response.json()["idTurma"] == turma.id_turma

    def test_professor_nao_acessa_turma_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.get(f"/api/v1/turmas/{turma.id_turma}", headers=headers)
        assert response.status_code == 403

    def test_turma_inexistente_retorna_404(
        self, api_client, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get("/api/v1/turmas/9999", headers=headers)
        assert response.status_code == 404

    def test_diretor_acessa_turma_de_terceiro(self, api_client, turma, diretor_headers):
        response = api_client.get(f"/api/v1/turmas/{turma.id_turma}", headers=diretor_headers)
        assert response.status_code == 200

    def test_professor_nao_lista_todas_turmas(
        self, api_client, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get("/api/v1/turmas", headers=headers)
        assert response.status_code == 403

    def test_professor_lista_apenas_suas_turmas(
        self, api_client, turma, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get("/api/v1/turmas/me", headers=headers)
        assert response.status_code == 200
        assert [t["idTurma"] for t in response.json()] == [turma.id_turma]


class TestMatriculasListagemRbac:
    def test_professor_nao_lista_todas_matriculas(
        self, api_client, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get("/api/v1/matriculas", headers=headers)
        assert response.status_code == 403
```

- [ ] **Step 3: Rodar os testes para ver falhar**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest tests/test_rbac_turmas.py -q
```

Expected: FAIL nos casos `test_professor_nao_acessa_turma_de_outro`,
`test_professor_nao_lista_todas_turmas` e `test_professor_nao_lista_todas_matriculas`
(retornam 200 em vez de 403).

- [ ] **Step 4: Proteger `GET /turmas/{turma_id}` e fechar a listagem**

Em `backend/app/api/v1/turmas.py`:

1. Atualizar os imports para remover `get_turma_by_id` e adicionar a dependência e o model.
   O bloco de imports de serviços deve ficar:

```python
from app.core.authorization import require_turma_access
from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.models.turma import Turma
from app.schemas.turma_schema import TurmaCreateSchema, TurmaResponseSchema, TurmaUpdateSchema
from app.services.turma_service import (
    CursoNotFoundForTurmaError,
    ProfessorNotFoundForTurmaError,
    TurmaHasDependenciesError,
    TurmaNotFoundError,
    create_turma,
    delete_turma,
    list_turmas,
    list_turmas_by_professor,
    update_turma,
)
```

2. Trocar a rota de listagem para aceitar apenas cargos 1 e 3:

```python
@router.get("")
def read_turmas(_current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    return [TurmaResponseSchema.model_validate(turma) for turma in list_turmas(db)]
```

3. Trocar a rota por ID para usar a dependência de autorização:

```python
@router.get("/{turma_id}")
def read_turma(turma: Turma = Depends(require_turma_access)):
    return TurmaResponseSchema.model_validate(turma)
```

- [ ] **Step 5: Fechar a listagem global de matrículas**

Em `backend/app/api/v1/matriculas.py`, trocar a rota de listagem:

```python
@router.get("")
def read_matriculas(_current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    return [MatriculaResponseSchema.model_validate(m) for m in list_matriculas(db)]
```

- [ ] **Step 6: Rodar os testes para ver passar**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest tests/test_rbac_turmas.py tests/test_api_endpoints.py -q
```

Expected: todos passam.

- [ ] **Step 7: Commit**

```bash
git add backend/tests/conftest.py backend/tests/test_rbac_turmas.py backend/app/api/v1/turmas.py backend/app/api/v1/matriculas.py
git commit -m "feat: isolar turmas do professor e fechar listagens globais"
```

---

## Task 3: RBAC em notas (leitura e lançamento)

**Files:**
- Create: `backend/tests/test_rbac_notas.py`
- Modify: `backend/app/api/v1/notas.py`

- [ ] **Step 1: Escrever os testes que falham**

Criar `backend/tests/test_rbac_notas.py` com:

```python
class TestNotasRbac:
    def test_professor_acessa_notas_da_propria_turma(
        self, api_client, turma, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get(f"/api/v1/notas/turma/{turma.id_turma}", headers=headers)
        assert response.status_code == 200

    def test_professor_nao_acessa_notas_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.get(f"/api/v1/notas/turma/{turma.id_turma}", headers=headers)
        assert response.status_code == 403

    def test_professor_nao_acessa_media_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.get(f"/api/v1/notas/media/turma/{turma.id_turma}", headers=headers)
        assert response.status_code == 403

    def test_professor_acessa_matricula_da_propria_turma(
        self, api_client, matricula_ativa, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get(
            f"/api/v1/notas/matricula/{matricula_ativa.id_matricula}", headers=headers
        )
        assert response.status_code == 200

    def test_professor_nao_acessa_matricula_de_outro(
        self, api_client, matricula_ativa, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.get(
            f"/api/v1/notas/matricula/{matricula_ativa.id_matricula}", headers=headers
        )
        assert response.status_code == 403

    def test_professor_nao_lanca_notas_em_turma_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.post(
            "/api/v1/notas",
            headers=headers,
            json={"idTurma": turma.id_turma, "prova": 1, "notas": []},
        )
        assert response.status_code == 403
```

- [ ] **Step 2: Rodar os testes para ver falhar**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest tests/test_rbac_notas.py -q
```

Expected: FAIL nos casos de terceiro (retornam 200 ou 422 em vez de 403).

- [ ] **Step 3: Aplicar a autorização nas rotas de notas**

Em `backend/app/api/v1/notas.py`:

1. Atualizar os imports (adicionar autorização e os models):

```python
from app.core.authorization import (
    enforce_turma_access,
    require_matricula_access,
    require_turma_access,
)
from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.schemas.nota_schema import MediaTurmaSchema, NotaBatchSchema, NotaResponseSchema
from app.services.nota_service import (
    InvalidMatriculasError,
    calcular_media_por_prova,
    create_or_update_notas,
    list_notas_by_matricula,
    list_notas_by_turma,
)
```

2. Validar o `idTurma` no lançamento (inserir a chamada antes da validação de `prova`):

```python
@router.post("")
def create_notas(
    payload: NotaBatchSchema,
    current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    enforce_turma_access(db, payload.idTurma, current_user)
    # REFACTOR: validação "prova >= 1" pertence ao schema/service, não ao router
    if payload.prova < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="O numero da prova deve ser maior ou igual a 1.")
    try:
        notas = create_or_update_notas(db, payload)
    except InvalidMatriculasError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Algumas matrículas informadas não pertencem à turma")
    result = [NotaResponseSchema.model_validate(n) for n in notas]
    return result
```

3. Proteger a leitura por matrícula:

```python
@router.get("/matricula/{matricula_id}")
def read_notas_by_matricula(
    matricula_id: int,
    _matricula: Matricula = Depends(require_matricula_access),
    db: Session = Depends(get_db),
):
    notas = list_notas_by_matricula(db, matricula_id)
    return [NotaResponseSchema.model_validate(n) for n in notas]
```

4. Proteger a leitura por turma:

```python
@router.get("/turma/{turma_id}")
def read_notas_by_turma(
    turma_id: int,
    prova: int | None = Query(None),
    _turma: Turma = Depends(require_turma_access),
    db: Session = Depends(get_db),
):
    notas = list_notas_by_turma(db, turma_id, prova)
    return [NotaResponseSchema.model_validate(n) for n in notas]
```

5. Proteger a média por turma:

```python
@router.get("/media/turma/{turma_id}")
def read_media_turma(
    turma_id: int,
    _turma: Turma = Depends(require_turma_access),
    db: Session = Depends(get_db),
):
    medias = calcular_media_por_prova(db, turma_id)
    return MediaTurmaSchema(idTurma=turma_id, medias=medias)
```

- [ ] **Step 4: Rodar os testes para ver passar**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest tests/test_rbac_notas.py -q
```

Expected: `6 passed`.

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_rbac_notas.py backend/app/api/v1/notas.py
git commit -m "feat: isolar leitura e lançamento de notas por turma"
```

---

## Task 4: RBAC em presenças (leitura e lançamento)

**Files:**
- Create: `backend/tests/test_rbac_presencas.py`
- Modify: `backend/app/api/v1/presencas.py`

- [ ] **Step 1: Escrever os testes que falham**

Criar `backend/tests/test_rbac_presencas.py` com:

```python
class TestPresencasRbac:
    def test_professor_acessa_presencas_da_propria_turma(
        self, api_client, turma, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get(f"/api/v1/presencas/turma/{turma.id_turma}", headers=headers)
        assert response.status_code == 200

    def test_professor_nao_acessa_presencas_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.get(f"/api/v1/presencas/turma/{turma.id_turma}", headers=headers)
        assert response.status_code == 403

    def test_professor_nao_registra_presenca_em_turma_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.post(
            "/api/v1/presencas",
            headers=headers,
            json={"idTurma": turma.id_turma, "dataAula": "2026-01-01", "presencas": []},
        )
        assert response.status_code == 403
```

- [ ] **Step 2: Rodar os testes para ver falhar**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest tests/test_rbac_presencas.py -q
```

Expected: FAIL nos casos de terceiro.

- [ ] **Step 3: Aplicar a autorização nas rotas de presenças**

Substituir o conteúdo de `backend/app/api/v1/presencas.py` por:

```python
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.authorization import enforce_turma_access, require_turma_access
from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.models.turma import Turma
from app.schemas.presenca_schema import PresencaBatchSchema, PresencaResponseSchema
from app.services.presenca_service import create_or_update_presencas, list_presencas_by_turma

router = APIRouter(prefix="/api/v1/presencas", tags=["presencas"])


@router.post("")
def create_presencas(
    payload: PresencaBatchSchema,
    current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    enforce_turma_access(db, payload.idTurma, current_user)
    presencas = create_or_update_presencas(db, payload)
    return [PresencaResponseSchema.model_validate(p) for p in presencas]


@router.get("/turma/{turma_id}")
def read_presencas_by_turma(
    turma_id: int,
    data_aula: date | None = Query(None, alias="dataAula"),
    _turma: Turma = Depends(require_turma_access),
    db: Session = Depends(get_db),
):
    presencas = list_presencas_by_turma(db, turma_id, data_aula)
    return [PresencaResponseSchema.model_validate(p) for p in presencas]
```

- [ ] **Step 4: Rodar os testes para ver passar**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest tests/test_rbac_presencas.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_rbac_presencas.py backend/app/api/v1/presencas.py
git commit -m "feat: isolar leitura e lançamento de presenças por turma"
```

---

## Task 5: Verificação final de cobertura e regressão

**Files:**
- Nenhuma alteração de código.

- [ ] **Step 1: Rodar a suíte completa com o gate de cobertura**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
```

Expected: todos os testes passam e o relatório termina com `TOTAL ... >= 70%`
sem erro `FAIL Required test coverage of 70% not reached`.

- [ ] **Step 2: Confirmar a cobertura do módulo novo**

Run (a partir de `backend/`):

```bash
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/sga_abacos" SECRET_KEY=test /tmp/opencode/venv-abaco/bin/python -m pytest -q --cov-report=term-missing 2>&1 | grep "app/core/authorization.py"
```

Expected: linha `app/core/authorization.py` com cobertura de 100% (nenhuma coluna "Missing").

- [ ] **Step 3: Verificação manual do fluxo do professor no frontend**

Com o stack no ar (`docker start sga_database sga_backend sga_frontend`):

1. Acessar `http://localhost:3000`, logar como `maria@abaco.org.br` / `prof12345`.
2. Ir em "Minhas Turmas" e abrir os detalhes de uma turma de Maria → deve carregar normalmente.
3. Navegar manualmente para uma turma de outro professor (ex.: `/academico/turmas/3`) → deve exibir
   "Turma não encontrada ou você não tem acesso a ela" (backend respondeu 403).

Nota: o container `sga_backend` roda uma imagem antiga. Para o teste manual refletir este código,
reconstruir com `docker compose build backend && docker restart sga_backend` antes de validar.

- [ ] **Step 4: Registrar evidência no commit final (se houver ajuste)**

Caso algum teste revele regressão, corrigir, rodar novamente os Steps 1 e 2 e commitar com:

```bash
git add -A
git commit -m "test: ajustes finais de cobertura da issue 6"
```

---

## Self-Review

**Cobertura do spec:**
- Enforcement por turma/matrícula → Tasks 1, 2, 3, 4.
- Fechamento das listagens globais → Task 2 (turmas e matrículas).
- Validação de `idTurma` no corpo (notas/presenças) → Tasks 3 e 4.
- 403 para turma de terceiro, 404 para inexistente → Task 1 (unitário) e Tasks 2–4 (integração).
- Cobertura >= 70% e pytest-cov → Task 0 e Task 5.
- Sem mudanças estruturais no frontend → Task 5 (verificação manual).

**Consistência de tipos e nomes:** `assert_turma_access`, `assert_matricula_access`,
`enforce_turma_access`, `enforce_matricula_access`, `require_turma_access`,
`require_matricula_access`, `is_privileged`, `get_user_id` são usados de forma idêntica
entre Tasks 1–4. As fixtures `api_client`, `outro_professor`, `turma_outro_professor`,
`professor_headers_factory` e `diretor_headers` são definidas na Task 2 e consumidas nas
Tasks 3 e 4 sem renomeação.

**Riscos conhecidos:** o baseline de cobertura está exatamente em 70%; como o módulo novo
tem cobertura 100% e as rotas ganham mais casos de teste, o total deve permanecer ou subir.
O container do backend é stale e não é usado para os testes automatizados (que rodam no venv
local); ele só aparece na verificação manual da Task 5.
