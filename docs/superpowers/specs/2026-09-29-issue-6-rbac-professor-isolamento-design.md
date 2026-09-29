# Issue 6 — RBAC: isolar acesso do perfil Professor à própria turma e alunos

## Objetivo

Garantir que o perfil **Professor** (cargo 2) acesse somente as turmas em que está
vinculado e apenas os alunos nelas matriculados. Diretor (cargo 1) e Administrativo
(cargo 3) mantêm acesso irrestrito. A API deve aplicar os filtros de segurança no
banco com base na identidade autenticada e bloquear com **403** qualquer tentativa de
acesso a turma de outro professor.

Referências: issue #6 `[Sprint 1] [RBAC] Restringir acesso do perfil Professor à
própria turma e alunos`.

## Contexto atual

- Cargos: `1 = Diretor(a)`, `2 = Professor`, `3 = Administrativo`.
- A página "Minhas Turmas" (`/academico/turmas`) já consome `GET /api/v1/turmas/me`,
  que filtra por `Turma.id_professor`. A lista de alunos (`/academico/alunos`) já
  cruza `GET /turmas/me` com `GET /matriculas/me` e filtra no cliente.
- Persistem lacunas de autorização por ID:
  - `GET /api/v1/turmas/{turma_id}` permite cargos 1, 2 e 3 sem checar posse.
  - `GET /api/v1/notas/turma/{turma_id}`, `GET /api/v1/notas/media/turma/{turma_id}`,
    `GET /api/v1/notas/matricula/{matricula_id}` e `GET /api/v1/presencas/turma/{turma_id}`
    permitem cargo 2 sem checar se a turma pertence ao professor.
  - `POST /api/v1/notas` e `POST /api/v1/presencas` recebem `idTurma` no corpo e não
    validam posse — um professor pode lançar notas/presenças em turma de terceiro.
  - Listagens globais `GET /api/v1/turmas` e `GET /api/v1/matriculas` permitem cargo 2
    e expõem dados de todos.

## Escopo

### Dentro do escopo

- Enforcement de posse de turma para cargo 2 nos endpoints por turma e por matrícula.
- Fechamento das listagens globais de turmas e matrículas para cargo 2.
- Validação de `idTurma` nos corpos de `POST /notas` e `POST /presencas`.
- Testes unitários e de integração das novas regras, com cobertura >= 70%.

### Fora do escopo

- Migração do token de `localStorage` para cookie httpOnly.
- Introdução de enumerações formais de cargo no banco.
- Refatorações estruturais amplas (`dependencies.py`, camada de serviços).
- Alterações de UI além do tratamento de erro já existente.

## Regras de autorização

| Cargo | Turma de terceiro (por ID) | Turma inexistente | Listagens globais |
|---|---|---|---|
| 1 — Diretor(a) | permitido | 404 | permitido |
| 2 — Professor | **403** | 404 | bloqueado (usar `/me`) |
| 3 — Administrativo | permitido | 404 | permitido |

- A posse do professor é determinada por `Turma.id_professor == sub` do JWT.
- Recurso aninhado (matrícula, nota por matrícula) resolve a turma dona antes da
  checagem.

## Arquitetura

### Novo módulo `backend/app/core/authorization.py`

Responsável por toda a política de acesso por turma, desacoplado dos routers e
testável de forma isolada.

- `TurmaAccessDeniedError(Exception)` — sinaliza 403.
- `is_privileged(current_user: dict) -> bool` — cargo em `(1, 3)`.
- `get_user_id(current_user: dict) -> int` — `sub` do token, com fallback `0`.
- `assert_turma_access(db, turma_id, current_user) -> Turma`
  - turma inexistente → `TurmaNotFoundError` (404);
  - privilegiado → retorna a turma;
  - cargo 2 e `turma.id_professor == get_user_id(...)` → retorna a turma;
  - caso contrário → `TurmaAccessDeniedError` (403).
- `assert_matricula_access(db, matricula_id, current_user) -> Matricula`
  - matrícula inexistente → `MatriculaNotFoundError` (404);
  - delega a `assert_turma_access` usando `matricula.id_turma`.
- Dependências FastAPI reutilizáveis:
  - `require_turma_access(turma_id, current_user=Depends(get_current_user), db=Depends(get_db)) -> Turma`
  - `require_matricula_access(matricula_id, current_user=Depends(get_current_user), db=Depends(get_db)) -> Matricula`

As dependências autenticam e autorizam numa única passada: `get_current_user`
decodifica o token e `assert_*` aplica a política. Isso evita decodificação
duplicada e mantém a semântica 403/404.

### Mapeamento de erros

`TurmaAccessDeniedError` → HTTP 403 com
`"Acesso negado. Você não tem permissão para acessar este recurso."`.
`TurmaNotFoundError` → HTTP 404 com `"Turma não encontrada"`.
`MatriculaNotFoundError` → HTTP 404 com `"Matrícula não encontrada"`.

Os routers tratam as exceções com `try/except` e `HTTPException`, seguindo o padrão
atual do projeto.

## Alterações por arquivo

### `backend/app/api/v1/turmas.py`

- `GET /turmas` → `verify_cargo(1, 3)` (remove cargo 2).
- `GET /turmas/{turma_id}` → `turma: Turma = Depends(require_turma_access)`; remove
  o `verify_cargo(1, 2, 3)` e o `get_turma_by_id` manual.
- `GET /turmas/me`, `POST`, `PUT`, `DELETE` inalterados.

### `backend/app/api/v1/matriculas.py`

- `GET /matriculas` → `verify_cargo(1, 3)` (remove cargo 2).
- `GET /matriculas/me` e demais rotas inalteradas (professor já não acessa por ID).

### `backend/app/api/v1/notas.py`

- `GET /notas/turma/{turma_id}` → `Depends(require_turma_access)`.
- `GET /notas/media/turma/{turma_id}` → `Depends(require_turma_access)`.
- `GET /notas/matricula/{matricula_id}` → `Depends(require_matricula_access)`.
- `POST /notas` → valida `payload.idTurma` via `assert_turma_access` com o
  `current_user` autenticado (`verify_cargo(1, 2, 3)`).

### `backend/app/api/v1/presencas.py`

- `GET /presencas/turma/{turma_id}` → `Depends(require_turma_access)`.
- `POST /presencas` → valida `payload.idTurma` via `assert_turma_access`.

### Frontend

Sem mudanças estruturais. A página `turma-detail` já trata erro exibindo
"Turma não encontrada ou você não tem acesso a ela", e a lista de alunos já filtra
por `/turmas/me` + `/matriculas/me`. Será validado que o 403 resulta nessa mensagem.

## Fluxo de uma requisição protegida

```
Cliente → GET /api/v1/turmas/{id}
  → require_turma_access
      → get_current_user (decodifica JWT)
      → assert_turma_access
          → carrega Turma (404 se ausente)
          → privilegiado? retorna
          → professor dono? retorna
          → senão 403
  → handler devolve TurmaResponseSchema
```

## Testes e cobertura

- Adicionar `pytest-cov==5.0.0` a `backend/requirements.txt`.
- Atualizar `backend/pytest.ini`:
  `addopts = --cov=app --cov-report=term-missing --cov-fail-under=70`.
- `backend/tests/test_authorization.py` (unitário, SQLite via `db_session`):
  - privilegiado acessa qualquer turma;
  - dono acessa a própria turma;
  - não-dono recebe `TurmaAccessDeniedError`;
  - turma inexistente recebe `TurmaNotFoundError`;
  - `assert_matricula_access` dono/não-dono/inexistente.
- `backend/tests/test_rbac_api.py` (integração):
  - `TestClient` com `app.dependency_overrides[get_db]` usando o `db_session` SQLite;
  - tokens reais gerados por `create_access_token(subject=..., cargo=...)`;
  - casos: professor dono → 200; professor terceiro → 403; turma inexistente → 404;
    diretor → 200; `GET /turmas` e `GET /matriculas` com cargo 2 → 403;
    `POST /notas` e `POST /presencas` em turma de terceiro → 403.
- A meta de cobertura é aferida no backend inteiro, executado no container/ambiente
  com dependências instaladas.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Testes de API existentes usam banco real (FIXME no `conftest`) | Novos testes usam `dependency_overrides[get_db]` com SQLite, sem tocar o banco real |
| Quebra de telas do professor por 403 inesperado | Todos os fluxos do professor já usam `/me`; validar `turma-detail` |
| Cobertura global abaixo de 70% após adicionar `--cov-fail-under` | Medir baseline e complementar testes dos módulos tocados |

## Branch de trabalho

`6-sprint-1-rbac-restringir-acesso-professor-propria-turma-e-alunos`, criada a partir
de `develop`. Spec e implementação ficam isolados nela.
