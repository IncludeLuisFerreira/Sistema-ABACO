# Issue #46 — IntegrityError e normalização no estoque

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tratar violações de integridade como erros de domínio em aluno/curso, normalizar nomes do estoque e limpar nomes antigos via migration.

**Architecture:** Serviços continuam donos da regra; routers apenas traduzem exceções de domínio para HTTP 409. A normalização de nome do estoque vira um helper único no service. A migration 008 normaliza, mescla duplicatas e reponta FKs antes de remover as linhas redundantes.

**Tech Stack:** Python 3.14, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16 (testes em SQLite).

**Spec:** Issue #46 (`gh issue view 46`) + plano aprovado em conversa.

## Global Constraints

- Não alterar `database-schema.sql`.
- Migration nova: `008`, `down_revision = "007"`, um único head.
- Conventional Commits em português, até 72 caracteres na primeira linha.
- Cobertura mínima de 70% nos arquivos alterados.
- Sem `print()` / `console.log` no diff.

## Review Focus

- Duplicatas antigas com espaços internos colidem ao normalizar; migration deve mesclar antes de renomear.
- FKs `movimentacao_estoque` e `itempedido` precisam ser repontadas antes de excluir duplicatas.
- `IntegrityError` que não é violação única não pode virar 409 em `create_estoque`.
- Nome com espaços no update não pode criar duplicata.
- Busca com espaços deve encontrar o item normalizado.

---

### Task 1: `create_aluno` retorna erro de domínio

**Files:**
- Modify: `backend/app/services/aluno_service.py:12-29`
- Modify: `backend/app/api/v1/alunos.py:37-39`
- Test: `backend/tests/test_aluno_service.py`

**Interfaces:**
- Produces: `AlunoIntegrityError(Exception)`; `create_aluno` levanta essa exceção após `rollback`.

- [ ] **Step 1: Escrever teste que falha**

```python
def test_integrity_error_vira_erro_de_dominio(self, db_session, monkeypatch):
    from sqlalchemy.exc import IntegrityError

    from app.services.aluno_service import AlunoIntegrityError

    def commit_falha():
        raise IntegrityError("INSERT", {}, Exception("violacao de integridade"))

    monkeypatch.setattr(db_session, "commit", commit_falha)

    with pytest.raises(AlunoIntegrityError):
        create_aluno(db_session, AlunoCreateSchema(nome="Aluno Duplicado"))
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd backend && python -m pytest tests/test_aluno_service.py::TestCreateAluno::test_integrity_error_vira_erro_de_dominio -q`
Expected: FAIL com `ImportError`/`AttributeError` de `AlunoIntegrityError`.

- [ ] **Step 3: Implementar**

Adicionar `class AlunoIntegrityError(Exception)` e envolver o `commit()` de `create_aluno` em `try/except IntegrityError`, com `rollback()` e `raise AlunoIntegrityError from exc`.

No router, adicionar `except AlunoIntegrityError` no POST retornando `409` com `detail="Não foi possível criar o aluno"`.

- [ ] **Step 4: Rodar e ver passar**

Run: `cd backend && python -m pytest tests/test_aluno_service.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/aluno_service.py backend/app/api/v1/alunos.py backend/tests/test_aluno_service.py
git commit -m "fix(alunos): trata IntegrityError ao criar aluno"
```

---

### Task 2: `create_curso` retorna erro de domínio

**Files:**
- Modify: `backend/app/services/curso_service.py:8-23`
- Modify: `backend/app/api/v1/cursos.py:35-37`
- Test: `backend/tests/test_curso_service.py`

**Interfaces:**
- Produces: `CursoIntegrityError(Exception)`; `create_curso` levanta essa exceção após `rollback`.

- [ ] **Step 1: Escrever teste que falha**

```python
def test_integrity_error_vira_erro_de_dominio(self, db_session, monkeypatch):
    from sqlalchemy.exc import IntegrityError

    from app.services.curso_service import CursoIntegrityError

    def commit_falha():
        raise IntegrityError("INSERT", {}, Exception("violacao de integridade"))

    monkeypatch.setattr(db_session, "commit", commit_falha)

    with pytest.raises(CursoIntegrityError):
        create_curso(db_session, CursoCreateSchema(nomeCurso="Curso Duplicado"))
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd backend && python -m pytest tests/test_curso_service.py::TestCreateCurso::test_integrity_error_vira_erro_de_dominio -q`
Expected: FAIL com `ImportError`/`AttributeError` de `CursoIntegrityError`.

- [ ] **Step 3: Implementar**

Adicionar `class CursoIntegrityError(Exception)` e envolver o `commit()` de `create_curso` em `try/except IntegrityError`, com `rollback()` e `raise CursoIntegrityError from exc`.

No router, adicionar `except CursoIntegrityError` no POST retornando `409` com `detail="Não foi possível criar o curso"`.

- [ ] **Step 4: Rodar e ver passar**

Run: `cd backend && python -m pytest tests/test_curso_service.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/curso_service.py backend/app/api/v1/cursos.py backend/tests/test_curso_service.py
git commit -m "fix(cursos): trata IntegrityError ao criar curso"
```

---

### Task 3: Normalização e violação única no estoque

**Files:**
- Modify: `backend/app/services/estoque_service.py:33-106`
- Test: `backend/tests/test_estoque_service.py`
- Test: `backend/tests/test_estoque_endpoints.py`

**Interfaces:**
- Produces: `_normalizar_nome_item(value: str) -> str` — `" ".join(value.split())`.
- Produces: `create_estoque` só converte violação única em `EstoqueAlreadyExistsError`; demais `IntegrityError` são relançados após `rollback`.

- [ ] **Step 1: Escrever testes que falham**

Adicionar em `test_estoque_service.py`:

```python
def test_create_normaliza_espacos(self, db_session):
    item = create_estoque(db_session, EstoqueCreateSchema(nomeItem="  Papel   A4  "))
    assert item.nome_item == "Papel A4"


def test_create_duplicado_com_espacos_levanta_erro(self, db_session):
    db_session.add(Estoque(nome_item="Papel A4", quantidade_disponivel=1))
    db_session.commit()

    with pytest.raises(EstoqueAlreadyExistsError):
        create_estoque(db_session, EstoqueCreateSchema(nomeItem="  papel   a4  "))


def test_create_relanca_integrity_error_nao_unico(self, db_session, monkeypatch):
    def commit_falha():
        raise IntegrityError("INSERT", {}, Exception("NOT NULL constraint failed: estoque.nomeitem"))

    monkeypatch.setattr(db_session, "commit", commit_falha)

    with pytest.raises(IntegrityError):
        create_estoque(db_session, EstoqueCreateSchema(nomeItem="Sem nome"))


def test_update_normaliza_nome(self, db_session, estoque_item):
    result = update_estoque(
        db_session,
        estoque_item.id_item_estoque,
        EstoqueUpdateSchema(nomeItem="  Papel   A4 Premium  "),
    )
    assert result.nome_item == "Papel A4 Premium"


def test_update_duplicado_com_espacos_levanta_erro(self, db_session, estoque_item):
    db_session.add(Estoque(nome_item="Caneta", quantidade_disponivel=1))
    db_session.commit()

    with pytest.raises(EstoqueAlreadyExistsError):
        update_estoque(
            db_session,
            estoque_item.id_item_estoque,
            EstoqueUpdateSchema(nomeItem="  caneta  "),
        )


def test_search_normaliza_termo(self, db_session, estoque_item):
    results = search_estoque_by_name(db_session, "  papel   a4  ")
    assert any(item.id_item_estoque == estoque_item.id_item_estoque for item in results)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd backend && python -m pytest tests/test_estoque_service.py -q`
Expected: FAIL nos testes novos (nome com espaços, duplicata e busca).

- [ ] **Step 3: Implementar**

Em `estoque_service.py`, criar `_normalizar_nome_item` e usá-lo em `create_estoque` (busca e gravação), `update_estoque` (gravação e mensagem) e `search_estoque_by_name` (termo).

Em `create_estoque`, trocar o `except IntegrityError` para:

```python
except IntegrityError as exc:
    db.rollback()
    if _is_unique_violation(exc):
        raise EstoqueAlreadyExistsError(...) from exc
    raise
```

- [ ] **Step 4: Rodar e ver passar**

Run: `cd backend && python -m pytest tests/test_estoque_service.py tests/test_estoque_endpoints.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/estoque_service.py backend/tests/test_estoque_service.py backend/tests/test_estoque_endpoints.py
git commit -m "fix(estoque): normaliza nome e distingue violacao unica"
```

---

### Task 4: Migration 008 — limpeza dos nomes antigos

**Files:**
- Create: `backend/alembic/versions/008_normaliza_nomeitem_estoque.py`
- Modify: `backend/tests/test_migrations.py`
- Test: `backend/tests/test_migrations.py`

**Interfaces:**
- Produces: migration `008`, `down_revision = "007"`; normaliza, mescla duplicatas por `lower(nomeitem)` e reponta FKs.

- [ ] **Step 1: Atualizar teste de cabeçalho e escrever teste de limpeza**

Em `test_migrations.py`, trocar o head esperado para `["008"]` e incluir `"008"` no início da cadeia.

Adicionar teste que cria schema SQLite via `Base.metadata.create_all`, insere:

```python
Estoque(nome_item="Papel A4", quantidade_disponivel=10, unidade="cx", estoque_minimo=2)
Estoque(nome_item="  Papel   A4  ", quantidade_disponivel=5, unidade="cx", estoque_minimo=4)
MovimentacaoEstoque(id_item_estoque=<id da segunda>, quantidade=-1, tipo_movimentacao="baixa_manual", justificativa="teste")
ItemPedido(id_pedido=<pedido>, id_item_estoque=<id da segunda>, nome_item="Papel A4", quantidade=1)
```

Executar `command.stamp(cfg, "007")` e `command.upgrade(cfg, "008")` apontando `DATABASE_URL` para o SQLite temporário. Assertar: uma única linha, `nomeitem == "Papel A4"`, `quantidadedisponivel == 15`, `estoqueminimo == 4`, FKs apontando para o id remanescente.

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd backend && python -m pytest tests/test_migrations.py -q`
Expected: FAIL porque a revisão `008` não existe.

- [ ] **Step 3: Implementar migration**

Criar `008_normaliza_nomeitem_estoque.py`. No `upgrade()`:

1. Ler todas as linhas de `estoque` ordenadas por `iditemestoque`.
2. Agrupar por `" ".join(nomeitem.split()).lower()`.
3. Para cada grupo, manter a primeira linha; somar `quantidadedisponivel` não nulos, pegar maior `estoqueminimo` não nulo e primeira `unidade` não nula.
4. Repontar `movimentacao_estoque.iditemestoque` e `itempedido.iditemestoque` das duplicatas para o id mantido.
5. Excluir duplicatas.
6. Atualizar a linha mantida com o nome normalizado e valores agregados.

`downgrade()` é no-op: limpeza de dados não é reversível.

- [ ] **Step 4: Rodar e ver passar**

Run: `cd backend && python -m pytest tests/test_migrations.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/alembic/versions/008_normaliza_nomeitem_estoque.py backend/tests/test_migrations.py
git commit -m "fix(estoque): limpa nomes antigos via migration"
```

---

### Task 5: Verificação final

- [ ] **Step 1: Suíte backend**

Run: `cd backend && python -m pytest -q`
Expected: PASS.

- [ ] **Step 2: Cobertura dos arquivos alterados**

Run:

```bash
cd backend && python -m pytest \
  tests/test_aluno_service.py tests/test_curso_service.py \
  tests/test_estoque_service.py tests/test_estoque_endpoints.py \
  tests/test_migrations.py \
  --cov=app.services.aluno_service \
  --cov=app.services.curso_service \
  --cov=app.services.estoque_service \
  --cov=app.api.v1.alunos --cov=app.api.v1.cursos --cov=app.api.v1.estoque \
  --cov=alembic.versions.008_normaliza_nomeitem_estoque \
  --cov-report=term-missing
```

Expected: cada arquivo alterado com cobertura ≥ 70%.

- [ ] **Step 3: Head único**

Run: `cd backend && alembic heads`
Expected: `008 (head)`.
