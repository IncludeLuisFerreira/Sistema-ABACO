# Contexto do backend

Leia junto com `CONTEXT.md` quando a tarefa tocar `backend/`.

## Stack e estrutura

Python 3.11, FastAPI 0.136, SQLAlchemy 2.0, Pydantic 2.13, Alembic 1.14, PostgreSQL 16.
Endpoints são síncronos (`def`, não `async def`) e usam `Session` do SQLAlchemy.

```
backend/
├── main.py                     # cria o app, registra routers, CORS, rate limit, /api/health
├── app/api/v1/<recurso>.py     # routers, prefixo /api/v1/<recurso>
├── app/services/<recurso>_service.py
├── app/schemas/<recurso>_schema.py
├── app/models/<recurso>.py
├── app/core/                   # config, security, dependencies, authorization, limiter
├── app/db/database.py          # engine, SessionLocal, Base, get_db
├── app/email/                  # providers Brevo/SMTP/console + service
├── alembic/                    # migrations
└── tests/                      # pytest
```

## Convenções

- Nomes em `snake_case` para funções, variáveis e módulos. Classes de schema em `PascalCase`
  com sufixo `Schema` (`TurmaCreateSchema`, `TurmaResponseSchema`, `TurmaUpdateSchema`).
- Services expõem funções de módulo (`create_turma`, `list_turmas`), não classes.
- Erros de negócio são classes de exceção no próprio service (`TurmaNotFoundError`). O router
  captura e traduz para `HTTPException` com status e mensagem em português.
- Schema de entrada usa `alias`/`populate_by_name` quando o frontend envia camelCase
  (ex.: `idCurso`). Confira o schema existente antes de criar campo novo.
- Resposta sempre por schema: `TurmaResponseSchema.model_validate(turma)`.
- SQLAlchemy 2.0: `Mapped[T]` + `mapped_column("nome_no_banco", ...)`. O nome do atributo e o nome
  da coluna podem diferir (`id_turma` ↔ `idturma`). Respeite o padrão do model afetado.
- `relationship` usa `lazy="joined"` ou `lazy="selectin"` para evitar N+1 em listagens.
- Indentação: alguns arquivos usam tabs (`core/config.py`, `core/dependencies.py`, `db/database.py`),
  outros usam 4 espaços. Preserve o arquivo que está editando; não converta o arquivo inteiro.
- Type hints obrigatórios em funções de service e schema.

## Receita: novo endpoint

1. Localize o módulo em `app/api/v1/`. Se for recurso novo, crie router com
   `APIRouter(prefix="/api/v1/<recurso>", tags=["<recurso>"])` e registre em `main.py`
   (import + `app.include_router`).
2. Defina schemas de entrada/saída em `app/schemas/<recurso>_schema.py`.
3. Implemente a regra em `app/services/<recurso>_service.py`. O service recebe `db: Session`,
   valida, persiste e lança exceção de domínio.
4. No router: dependência de autorização + `db: Session = Depends(get_db)`; `try/except` das
   exceções de domínio; retorno com `ResponseSchema.model_validate(...)`.
5. Teste em `tests/test_<recurso>_service.py` (regra) e/ou `tests/test_<recurso>s_endpoints.py`
   (contrato HTTP).

## Receita: nova migration

```bash
cd backend
alembic revision --autogenerate -m "descricao_curta"
# revise o arquivo em alembic/versions/ antes de rodar
alembic heads          # precisa retornar exatamente um head
alembic upgrade head
python -m pytest -q
```

Regras:

- Nunca edite migration já aplicada; crie uma nova.
- Nunca apague migration para "limpar" a árvore.
- Se `alembic heads` mostrar mais de um head, o `down_revision` está errado. Corrija a cadeia,
  não crie merge migration sem entender o histórico (`alembic history --verbose`).
- `database-schema.sql` é referência histórica, não fonte de verdade.
- Testes usam SQLite em memória (`tests/conftest.py`): `JSONB`, `with_for_update`, índices
  funcionais e constraints específicas do PostgreSQL **não são exercitados**. Se a mudança depende
  disso, diga no PR que a cobertura é parcial.

## Testes

- Configuração em `backend/pytest.ini`: `testpaths = tests`, `pythonpath = .`,
  cobertura automática de `app`.
- `tests/conftest.py` cria engine SQLite in-memory, habilita foreign keys e fornece fixtures
  (`db_session`, `usuario`, `usuario_professor`, etc.) e `TestClient`.
- Padrão de teste de service: montar entidades com fixtures, chamar a função, assertar retorno e
  exceção. Use `pytest.raises(...)` para caminhos de erro.
- Padrão de teste de endpoint: `TestClient` + token gerado com `create_access_token`; teste também
  401 (sem token), 403 (cargo errado) e 404/400 quando aplicável.
- Um arquivo por módulo, nome `test_<modulo>_service.py` ou `test_<modulo>_endpoints.py`.
- Não use banco real nem dependa de ordem de execução. Não marque teste como `skip` para passar.
- Marca `integration` existe para e-mail real e só roda com `RUN_EMAIL_INTEGRATION=1`.

Comandos:

```bash
cd backend
python -m pytest -q
python -m pytest tests/test_turma_service.py -q
python -m pytest tests/test_turmas_endpoints.py::test_nome -q
```

## Armadilhas frequentes

1. **Lógica no router** — se o router tem `if` de regra de negócio, ela pertence ao service.
2. **Vazamento de model** — retornar `turma` direto expõe campos internos e quebra contrato.
3. **Autorização esquecida** — endpoint novo sem `verify_cargo` fica aberto. Teste 401/403.
4. **IDOR de professor** — receber `turma_id`/`matricula_id` sem `enforce_*_access` permite que um
   professor leia dados de outro. Sempre valide o vínculo.
5. **Transação pela metade** — service que altera duas tabelas precisa de `commit` único e
   `rollback` em erro.
6. **Migration com dois heads** — quebra o `alembic upgrade head` no Docker.
7. **`get_db` fecha sem rollback** — comportamento conhecido; não propague sessão suja.
8. **Mistura de tabs/espaços** — não reformate; siga o arquivo.
9. **Rate limit** — endpoints de auth usam `slowapi`; não remova o limiter ao refatorar.
10. **Seed/credenciais** — não logue `ADMIN_SEED_PASSWORD`, `JWT_SECRET` ou `BREVO_API_KEY`.

## Definição de pronto (backend)

- Regra nova em service, com teste de sucesso e de erro.
- Endpoint com autorização e teste 401/403.
- `python -m pytest -q` verde.
- Se houve schema: migration revisada, `alembic heads` único, teste de migration passando.
- Sem `print()` e sem segredo no diff.
