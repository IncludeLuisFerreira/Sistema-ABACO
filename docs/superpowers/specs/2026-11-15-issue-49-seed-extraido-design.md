# Issue #49 — Extrair seed do `main.py` e remover credenciais hardcoded

## Intenção

Hoje o seed de dados fictícios vive dentro de `backend/main.py` e roda no `startup`. Ele quebra o
boot em banco parcialmente populado, depende da sequence de `estoque` para acertar `id_item_estoque`
e carrega senhas conhecidas no código-fonte. O objetivo é ter um seed idempotente, granular,
executável fora do `main.py` e sem credenciais literais no código.

## Objetivos

- Seed em módulo próprio, com `run_seed(session)` puro e CLI (`python -m app.db.seed`).
- Idempotência granular por chave natural (nome do curso, e-mail, nome do item de estoque).
- `ItemPedido` referencia `Estoque` pelo objeto após `flush`, nunca por ID fixo.
- Credenciais de usuários de teste vindas de variáveis de ambiente.
- Seed automático no boot apenas com `SEED_ON_STARTUP=true` (default `false`).
- Startup não falha em banco parcialmente populado.

## Não-objetivos

- Não mexe em Alembic, migrations, schema ou `database-schema.sql`.
- Não muda o fluxo de login, RBAC, nem os endpoints.
- Não altera o seed de produção real (não existe; produção não deve rodar seed).

## Anti-objetivos / falhas

- Recriar dados fictícios em produção por padrão.
- Logar senha, `JWT_SECRET` ou `BREVO_API_KEY`.
- Deixar o seed "tudo-ou-nada" (abortar se existir qualquer registro).

## Restrições

- Python 3.11, SQLAlchemy 2.0, Pydantic 2.13 (`BaseSettings` já usado em `app/core/config.py`).
- Testes rodam em SQLite in-memory via fixture `db_session` em `backend/tests/conftest.py`.
- `AGENTS.md` §4: sem `print`, sem segredo no código, um PR = uma issue.
- Limite de escopo: até 8 arquivos.

## Abordagens consideradas

**A — Módulo `backend/app/db/seed.py` + CLI (`python -m app.db.seed`)** — escolhida.
Reaproveita `SessionLocal`/`Base`, é importável pelo pytest atual e pelo startup. Um arquivo novo
concentra a lógica; o `main.py` fica só com o gatilho condicionado pela flag.

**B — Script avulso `backend/scripts/seed.py`** — descartada.
Mesma lógica fora do pacote `app`, com import path pior dentro do container e sem cobertura natural
pelo `db_session`. Ganho zero.

**C — Manter no startup e só corrigir IDs e senhas** — descartada.
Menor diff, mas viola o critério de aceite "executável fora do `main.py`" e preserva o acoplamento
que causou o bug.

## Decisões

- **D1 — Automação no boot:** flag `SEED_ON_STARTUP` (default `false`). `docker-compose.yml` passa
  `${SEED_ON_STARTUP:-true}` para manter a experiência de dev; produção define `false` e não roda
  seed. CLI explícito ignora a flag e sempre executa.
- **D2 — Senhas de dev:** saem do código para `SEED_ADMIN_PASSWORD` e `SEED_PROFESSOR_PASSWORD`.
  Valores de dev (`admin123`, `prof12345`) ficam apenas em `.env.example` e na documentação, nunca
  em `.py`. Sem a variável, os usuários de teste correspondentes são pulados com `warning` (sem
  logar valor).
- **D3 — Idempotência:** granular. Cada entidade é buscada pela chave natural antes de inserir;
  só o que falta é criado. `run_seed` retorna contagem por entidade.
- **D4 — Bootstrap do diretor:** mantém `ADMIN_SEED_EMAIL`/`ADMIN_SEED_PASSWORD` como estão, agora
  dentro do módulo de seed; o `startup` do `main.py` não cria mais usuário.
- **D5 — `on_event` deprecado:** o startup migra para `lifespan` no mesmo diff (o `# REFACTOR` em
  `main.py:79` aponta para isso e o bloco é o mesmo).

## Desenho

`backend/app/db/seed.py`:

- Dataset declarativo no topo (cursos, usuários, alunos, turmas, matrículas, pedidos, estoque,
  itens de pedido referenciando o estoque **pelo nome**).
- `run_seed(db: Session) -> dict[str, int]` — idempotente, granular, usa `flush` antes de referenciar
  chaves geradas. Nada de `id_item_estoque` literal.
- `seed_enabled() -> bool` — lê `settings.seed_on_startup`.
- `main()` — CLI: abre sessão própria, roda `run_seed`, imprime o resumo, fecha. `python -m app.db.seed`.

`backend/app/core/config.py`: três campos novos — `seed_on_startup` (`SEED_ON_STARTUP`, default
`false`), `seed_admin_password` (`SEED_ADMIN_PASSWORD`, default `None`), `seed_professor_password`
(`SEED_PROFESSOR_PASSWORD`, default `None`).

`backend/main.py`: remove `_seed_test_data` e o startup; adiciona `lifespan` que chama
`run_seed` somente se `settings.seed_on_startup`. `main.py` fica com ~150 linhas.

`backend/tests/test_seed.py` (novo), com a fixture `db_session`:

1. banco vazio + senhas definidas → cria o grafo e todo `ItemPedido.id_item_estoque` aponta para
   um `Estoque` existente;
2. duas execuções seguidas → a segunda não cria nada e não levanta `IntegrityError`;
3. banco parcialmente populado (usuário de seed já existe, cursos vazios) → completa sem erro;
4. sem `SEED_ADMIN_PASSWORD`/`SEED_PROFESSOR_PASSWORD` → usuários de teste pulados, resto criado.

`.env.example`, `docker-compose.yml`, `README.md` (tabela de credenciais) e `ACESSOS.md`: passam a
apontar as senhas de dev para as variáveis, sem mudar valores.

## Verificação

- `cd backend && python -m pytest tests/test_seed.py -q`
- `cd backend && python -m pytest -q`
- `cd backend && alembic heads` → um único head (`007`, inalterado)
- Smoke: `docker compose up --build -d` em volume limpo e em volume já populado; `curl /api/health`.

## Fora do plano

- Rotação das senhas de dev, política de senha para seed, seed em produção.
- Qualquer refatoração do `health_check` (`main.py:252`) ou de `get_db` (`app/db/database.py`).
