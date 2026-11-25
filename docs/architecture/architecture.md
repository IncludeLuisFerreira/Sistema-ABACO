# Arquitetura do Sistema

Visão de alto nível. Regras de domínio, papéis e modelo de dados ficam em `docs/agents/CONTEXT.md`;
este documento descreve apenas a arquitetura e a infraestrutura reais do repositório.

## Frontend

- Framework: Angular 21.2, componentes standalone.
- Linguagem: TypeScript 5.9 em modo `strict`.
- Estilo: SCSS por componente. Não há Tailwind, NgRx, PrimeNG, Material nem biblioteca externa de UI.
- Gráficos: ApexCharts + ng-apexcharts.
- Testes: Vitest 4 + jsdom.

Responsabilidades:

- interface administrativa (diretor e administrador)
- interface de professor
- dashboards e gráficos

Organização: páginas em `features/<dominio>/pages/`, componentes reutilizáveis em
`shared/components/`, modelos em `core/models/` e toda chamada HTTP em `core/services/`.
Os componentes não injetam `HttpClient` diretamente.

---

## Backend

- Runtime: Python 3.11.
- Framework: FastAPI 0.136.
- ORM: SQLAlchemy 2.0, com migrações Alembic.
- Validação: Pydantic 2.13.
- Servidor: uvicorn.
- Testes: pytest.

Responsabilidades:

- API REST sob `/api/v1`
- autenticação e autorização
- regras de negócio

Fluxo em camadas:

```
HTTP → app/api/v1/<recurso>.py (router)
     → app/services/<recurso>_service.py (regra de negócio e transação)
     → app/models/<recurso>.py (SQLAlchemy)
     → PostgreSQL
```

Routers não concentram regra de negócio e as respostas usam schemas Pydantic.

---

## Banco de Dados

- Banco: PostgreSQL 16, no container `database`.
- Schema gerenciado exclusivamente por migrações Alembic (`backend/alembic/`).
- `database-schema.sql` é referência, não fonte de alteração.
- No Docker, o backend acessa o banco pelo host `database`; fora do Docker, por `localhost`.
- Conexão configurada por `DATABASE_URL` no `.env` da raiz.

---

## Autenticação

- JWT assinado com HS256 (`JWT_SECRET`), entregue também em cookie de sessão `HttpOnly`.
- Escritas autenticadas por cookie exigem o header `X-CSRF-Token` (double-submit).
- Logout e troca de senha revogam tokens por versão (`usuario.tokenversion`).
- Detalhes em `docs/security/session-strategy.md`.

Papéis (cargo no token):

- `1` — diretor(a)
- `2` — professor(a)
- `3` — administrador(a)

Autorização por recurso: `verify_cargo(...)`, `require_turma_access` e `enforce_turma_access` /
`enforce_matricula_access` em `backend/app/core/`.

---

## Deploy

O deploy é feito com Docker Compose, não em plataformas gerenciadas:

| Serviço | Container | Porta no host |
|---------|-----------|---------------|
| Frontend (build Angular + Nginx) | `sga_frontend` | `3000` |
| Backend (FastAPI/uvicorn) | `sga_backend` | `8000` |
| Banco (PostgreSQL 16) | `sga_database` | `5432` |

- O Nginx do frontend serve o SPA e encaminha `/api/` para `http://backend:8000/api/`.
- O backend executa `alembic upgrade head` antes de iniciar o uvicorn.
- Saúde: `GET /api/health` e `GET /api/health/ready` (verificam o banco).
- Para produção com domínio próprio, o `docs/guides/deploy.md` traz o exemplo de Nginx TLS como
  reverse proxy na frente do Compose.

Não há deploy em Vercel, Railway, Render ou Supabase; a infraestrutura é o `docker-compose.yml`.

---

## Docker

O sistema é totalmente containerizado. Para desenvolvimento:

```bash
docker compose up --build
```

Serviços incluídos:

- PostgreSQL (`database`)
- backend FastAPI (`backend`)
- frontend Angular servido por Nginx (`frontend`)

Variáveis de ambiente vêm do `.env` na raiz (modelo em `.env.example`).
