# Contexto do projeto — SGA ABACO

Carregue este arquivo com `AGENTS.md`. Ele descreve o domínio e a arquitetura em nível suficiente
para planejar mudanças sem ler o repositório inteiro.

## Produto

Sistema de gestão acadêmica e logística da Associação ABACO (ONG com cursos profissionalizantes
gratuitos). Substitui processos manuais de cadastro, matrícula, presença, notas, histórico escolar,
estoque e pedidos de material.

- Frontend: SPA Angular em `frontend/`, servida por Nginx na porta `3000` (Docker).
- Backend: API REST FastAPI em `backend/`, porta `8000`, docs em `/docs`.
- Banco: PostgreSQL 16, schema gerenciado por Alembic.
- Autenticação: JWT em `Authorization: Bearer <token>`.

## Papéis (cargo)

| Cargo | Papel | Escopo |
|-------|-------|--------|
| `1` | Diretor(a) | Acesso total, inclusive aprovar pedidos e gerenciar usuários |
| `2` | Professor(a) | Apenas as próprias turmas: presenças, notas, alunos, pedidos |
| `3` | Administrador(a) | Acadêmico e logística, exceto aprovação de pedidos |

O cargo vai no payload do JWT (`cargo`) e é checado por `verify_cargo(...)` em
`backend/app/core/dependencies.py`.

## Módulos da API

Todos sob `/api/v1`, registrados em `backend/main.py`:

`auth`, `alunos`, `cursos`, `turmas`, `matriculas`, `presencas`, `notas`, `historico`,
`usuarios`, `dashboard`, `estoque`, `pedidos`.

Health check: `GET /api/health` (verifica conexão com o banco).

## Modelo de dados

Tabelas e campos-chave (nomes de coluna no banco são sem prefixo, ex.: `id_turma` ↔ `idturma`):

| Tabela | Campos relevantes |
|--------|-------------------|
| `usuario` | `id_usuario`, `nome`, `email` (único), `senha_hash`, `cargo`, `primeiro_acesso`, `telefone` |
| `aluno` | `id_aluno`, `nome`, contato/endereço |
| `curso` | `id_curso`, `nome_curso` |
| `turma` | `id_turma`, `id_curso`, `id_professor`, `capacidade`, `data_inicio`, `data_fim`, `dias_aula`, `avaliacoes` (JSON) |
| `matricula` | `id_matricula`, `id_aluno`, `id_turma`, `data_matricula`, `status` |
| `presenca` | `id_presenca`, `id_matricula`, `data_aula`, `presente` (bool) |
| `nota` | `id_nota`, `id_matricula`, `prova`, `nota` |
| `estoque` | `id_item_estoque`, `nome_item`, `quantidade_disponivel`, `unidade`, `estoque_minimo` |
| `pedido` | `id_pedido`, `id_usuario`, `id_turma`, `data_pedido`, `status` |
| `item_pedido` | `id_item_pedido`, `id_pedido`, `id_item_estoque`, `nome_item`, `quantidade`, `preco_unitario` |
| `movimentacao_estoque` | entrada/saída de item, quantidade, data |

Enums numéricos (não invente novos valores sem migration e regra explícita):

- `matricula.status`: `0` = ativa. `Turma.vagas_ocupadas` conta matrículas com `status == 0`.
- `pedido.status`: `0` = solicitado, `1` = aprovado, `2` = comprado, `3` = entregue.
  Transições são sequenciais; pular etapa lança `PedidoInvalidTransitionError`.
- `usuario.cargo`: `1` diretor, `2` professor, `3` administrador.

## Fluxo em camadas (backend)

```
HTTP → app/api/v1/<recurso>.py (router)
     → app/services/<recurso>_service.py (regra de negócio, transação)
     → app/models/<recurso>.py (SQLAlchemy)
     → PostgreSQL
```

- Router: valida autenticação/autorização, converte exceções de domínio em `HTTPException`, valida
  payload com schema Pydantic e serializa a resposta com `XxxResponseSchema.model_validate(obj)`.
- Service: recebe `Session`, aplica regra, faz `commit`/`rollback`, lança exceções de domínio
  (`TurmaNotFoundError`, `CapacidadeAbaixoDasVagasError`, etc.).
- Model: SQLAlchemy 2.0 com `Mapped`/`mapped_column`. `Base` está em `app/db/database.py`.

## Autenticação e autorização

- `POST /api/v1/auth/login` retorna access token e define os cookies `abaco_session` (HttpOnly) e
  `abaco_csrf` (double-submit). Payload do JWT: `sub` (id do usuário), `cargo`,
  `primeiro_acesso`, `iat`, `jti`, `ver`, `exp`. Algoritmo HS256, segredo em `JWT_SECRET`/`SECRET_KEY`.
  Detalhes em `docs/security/session-strategy.md`.
- O frontend usa o cookie de sessão; não persiste o JWT no `localStorage`. Requisições de escrita
  autenticadas por cookie exigem o header `X-CSRF-Token`.
- `POST /api/v1/auth/logout` incrementa `usuario.tokenversion` e revoga os tokens emitidos. Troca,
  redefinição e primeiro acesso de senha também incrementam a versão.
- Token expira em 120 min por padrão (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- Reset de senha usa token com `type=password_reset` (30 min). Primeiro acesso usa token com
  validade maior (1440 min) e obriga troca de senha.
- `primeiro_acesso=true` bloqueia rotas de negócio até a troca de senha.
- Autorização por recurso:
  - `verify_cargo(1, 3)` — cargos permitidos.
  - `require_turma_access` — dependência que carrega a turma e valida acesso.
  - `enforce_turma_access` / `enforce_matricula_access` — versões imperativas que lançam `HTTPException`.
- Professor só acessa turma da qual é `id_professor`. Diretor e administrador acessam todas.
  Esse é o controle mais sensível do sistema: qualquer endpoint novo que receba `turma_id` ou
  `matricula_id` precisa passar por essas funções.

## Regras de negócio críticas

- Turma não pode ter `capacidade` menor que o número de vagas já ocupadas.
- Datas da turma: `data_fim >= data_inicio`.
- Professor vinculado à turma precisa ter `cargo == 2`.
- Curso e professor referenciados precisam existir.
- Turma com matrículas dependentes não pode ser excluída.
- Pedido: criar como `0` (solicitado), aprovar `0 → 1`, comprar `1 → 2`, entregar `2 → 3`.
  Aprovar/entregar afeta estoque conforme o service; não duplique essa lógica.
- Estoque: nome de item é único case-insensitive (índice funcional no banco).

## Infra e ambiente

- `docker-compose.yml` sobe `database` (PostgreSQL), `backend` e `frontend` (Nginx).
- Backend dentro do Docker executa `alembic upgrade head` antes de iniciar o uvicorn.
- Variáveis em `.env` na raiz (modelo em `.env.example`). Principais: `DATABASE_URL`, `JWT_SECRET`,
  `ADMIN_SEED_EMAIL`, `ADMIN_SEED_PASSWORD`, `SMTP_*`, `BREVO_API_KEY`, `FRONTEND_URL`,
  `CORS_ORIGINS`, `RATE_LIMIT_*`.
- Seed cria usuários de teste quando `ADMIN_SEED_*` está definido. Credenciais no `CONTRIBUTING.md`.
- E-mail transacional: prioridade Brevo → SMTP → console (dev).

## Dívidas técnicas conhecidas (não "conserte" sem issue)

Há `# FIXME` e `# TODO` intencionais em pontos de segurança e transação (segredo default,
fechamento de sessão sem rollback, JWT sem revogação, cobertura só em SQLite). Não os remova nem
os corrija de passagem: eles exigem issue própria e decisão de produto.

## Documentos relacionados

- `README.md` — visão funcional por perfil e stack.
- `CONTRIBUTING.md` — processo de issue, branch, commit, PR e review.
- `docs/architecture/features/` — designs de features específicas.
- `docs/superpowers/specs/` e `plans/` — decisões e planos já aprovados.
