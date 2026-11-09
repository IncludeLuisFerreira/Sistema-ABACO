# AGENTS.md — SGA ABACO

Regras para agentes de IA (OpenCode, Claude Code, Codex, Copilot e similares) neste repositório.
Leia este arquivo inteiro. Ele é curto de propósito: contexto profundo e prompts operacionais
ficam em `docs/agents/` e só são carregados quando a tarefa exige.

## 1. O que é este projeto

SGA ABACO: sistema de gestão acadêmica (alunos, cursos, turmas, matrículas, presenças, notas,
histórico) e logística (estoque e pedidos de material) da Associação ABACO. Aplicação full-stack,
API REST com JWT, containerizada com Docker Compose.

Stack real — não invente versões nem bibliotecas:

| Camada | Tecnologias |
|--------|-------------|
| Backend | Python 3.11, FastAPI 0.136, SQLAlchemy 2.0, Pydantic 2.13, Alembic 1.14, PostgreSQL 16, PyJWT, bcrypt, slowapi, uvicorn |
| Frontend | Angular 21.2 (standalone), TypeScript 5.9 (`strict`), RxJS 7.8, ApexCharts + ng-apexcharts, SCSS, Vitest 4 + jsdom |
| Infra | Docker Compose, Nginx, PostgreSQL 16 |

Não há Tailwind, NgRx, PrimeNG, Material ou biblioteca de UI externa. O `docs/architecture/architecture.md`
menciona Tailwind e deploy em Vercel/Railway: está desatualizado, ignore esses dois pontos.

## 2. Fonte de verdade

| Assunto | Arquivo |
|---------|---------|
| Processo humano: issue, branch, commit, PR, review | `CONTRIBUTING.md` |
| Setup, portas, credenciais de seed, módulos | `README.md` |
| Regras do agente, comandos e limites | `AGENTS.md` (este arquivo) |
| Arquitetura, domínio, papéis, modelo de dados | `docs/agents/CONTEXT.md` |
| Detalhes e armadilhas do backend | `docs/agents/CONTEXT-backend.md` |
| Detalhes e armadilhas do frontend | `docs/agents/CONTEXT-frontend.md` |
| Prompts de execução | `docs/agents/prompts/` |
| Planos e designs anteriores | `docs/superpowers/plans/`, `docs/superpowers/specs/` |

Regra de conflito: `CONTRIBUTING.md` vence em processo; o código existente vence em comportamento;
este arquivo vence em regra para agente. Não duplique conteúdo entre eles.

## 3. Início de sessão — obrigatório

A causa mais comum de retrabalho neste repositório é começar de uma `develop` local desatualizada.
Faça sempre, nesta ordem:

```bash
git status --short                  # se houver mudança não commitada, pare e pergunte
./scripts/agent-preflight.sh --check
```

O preflight resolve a **base remota** sozinho e faz o `fetch` dela. A base é `upstream/develop`
quando você trabalha num fork (o `CONTRIBUTING.md` define `origin` como o fork e `upstream` como o
repositório principal) e `origin/develop` em clone direto. Se o fetch falhar, o preflight aborta com
código não-zero em vez de seguir com referência desatualizada.

Depois:

1. Nunca trabalhe diretamente em `main` ou `develop`.
2. Crie a branch a partir da base remota — nunca da `develop` local:

```bash
BASE=upstream   # ou origin, em clone direto (sem upstream)
git switch -c feature/descricao-curta "$BASE/develop"
# ou, deixando o script resolver:
./scripts/agent-preflight.sh --start feature/descricao-curta
```

3. Se já estiver numa branch de trabalho, verifique se ela está atrasada:

```bash
git log --oneline "HEAD..$BASE/develop"     # commits que faltam na sua branch
```

Se estiver atrasada, faça `git rebase "$BASE/develop"` antes de continuar. Se o rebase gerar conflito
que você não entende, pare e peça ajuda em vez de "resolver" escolhendo um lado.

4. Leia a issue antes de propor código: `gh issue view <N>` (ou o texto colado pelo usuário).

## 4. Regras inegociáveis

1. Nunca faça push direto em `main` ou `develop`. Nunca use `--force` em branch compartilhada.
2. Um PR = uma issue = uma mudança lógica. O corpo do PR deve conter `Closes #N`.
3. Não declare tarefa concluída sem rodar a verificação. Feature nova exige teste novo.
4. Backend: regra de negócio só em `backend/app/services/`. Router não decide regra, não acessa
   model para lógica e não monta resposta manualmente.
5. Resposta de API usa schema Pydantic (`model_validate`). Nunca devolva model SQLAlchemy.
6. Todo endpoint novo ou alterado precisa de autorização explícita: `verify_cargo(...)`,
   `require_turma_access` ou `enforce_turma_access` / `enforce_matricula_access`.
7. Mudou o schema do banco? Crie migration Alembic e garanta `alembic heads` com **um único head**.
   Nunca edite migration já aplicada. Nunca edite `database-schema.sql`.
8. Frontend: chamada HTTP só em `frontend/src/app/core/services/`. Componente não injeta `HttpClient`.
9. Segredo nunca no código. `.env` nunca é commitado. Não imprima token, senha ou chave em log.
10. Não remova `# TODO` / `# FIXME` sem resolver o problema descrito.
11. Não reformate arquivo inteiro: o backend mistura tabs e espaços por arquivo. Preserve o estilo local.
12. Nenhum `print()` ou `console.log` de debug no diff final.
13. Não adicione dependência nova sem justificar e sem aprovação explícita do usuário.
14. Não altere `CONTRIBUTING.md`, `README.md`, CI ou `scripts/` sem pedido explícito.

## 5. Comandos canônicos

Use estes comandos. Não invente variações, flags ou scripts que não existem.

| Objetivo | Comando |
|----------|---------|
| Checar sincronização e ambiente | `./scripts/agent-preflight.sh --check` |
| Criar branch atualizada | `./scripts/agent-preflight.sh --start feature/nome` |
| Subir stack completa | `./rebuild.sh` |
| Subir stack em background | `docker compose up --build -d` |
| Logs do backend | `docker compose logs -f backend` |
| Health check | `curl -s http://localhost:8000/api/health` |
| Backend: todos os testes | `cd backend && python -m pytest -q` |
| Backend: um arquivo | `cd backend && python -m pytest tests/test_turma_service.py -q` |
| Backend: um teste | `cd backend && python -m pytest tests/test_turma_service.py::test_nome -q` |
| Backend: cobertura | `cd backend && python -m pytest -q --cov=app --cov-report=term-missing` |
| Backend: migrar banco | `cd backend && alembic upgrade head` |
| Backend: nova migration | `cd backend && alembic revision --autogenerate -m "descricao"` |
| Backend: conferir heads | `cd backend && alembic heads` |
| Frontend: dependências | `cd frontend && npm ci` |
| Frontend: dev server | `cd frontend && npm start` |
| Frontend: testes (uma vez) | `cd frontend && npm test -- --watch=false` |
| Frontend: cobertura | `cd frontend && npm run test:coverage -- --watch=false` |
| Frontend: build | `cd frontend && npm run build` |
| Formatar frontend | `cd frontend && npx prettier --write <arquivos>` |

Portas: frontend `3000` (Docker) ou `4200` (`ng serve`); backend `8000`; PostgreSQL `5432`.
O backend lê o `.env` da raiz. Em Docker, o host do banco é `database`; fora do Docker, `localhost`.

## 6. Onde cada coisa vai

| Preciso… | Backend | Frontend |
|----------|---------|----------|
| Criar endpoint | `app/api/v1/<recurso>.py` | — |
| Regra de negócio | `app/services/<recurso>_service.py` | — |
| Validar entrada/saída | `app/schemas/<recurso>_schema.py` | `core/models/*.model.ts` |
| Alterar tabela | `app/models/<recurso>.py` + migration | — |
| Chamada HTTP | — | `core/services/<recurso>.service.ts` |
| Página/rota | — | `features/<dominio>/pages/<pagina>/` |
| Componente reutilizável | — | `shared/components/<nome>/` |
| Guard / interceptor | `app/core/authorization.py`, `dependencies.py` | `core/guards/`, `core/interceptors/` |

O `main.py` registra os routers. Endpoint novo só existe depois de importado e incluído lá.

## 7. Carregue o prompt da tarefa

Antes de executar, carregue **apenas** o prompt correspondente e o contexto da stack afetada:

| Tarefa | Prompt | Contexto extra |
|--------|--------|----------------|
| Implementar feature | `docs/agents/prompts/build-feature.md` | `CONTEXT.md` + `CONTEXT-backend.md` e/ou `CONTEXT-frontend.md` |
| Corrigir bug | `docs/agents/prompts/fix-bug.md` | `CONTEXT.md` + stack afetada |
| Revisar PR | `docs/agents/prompts/review-pr.md` | `CONTEXT-backend.md` / `CONTEXT-frontend.md` |
| Antes de abrir PR | `docs/agents/prompts/pre-pr.md` | — |

Atalhos no OpenCode: `/build`, `/fix`, `/review`, `/pre-pr`.

## 8. Orçamento de contexto

O objetivo é acertar na primeira tentativa gastando pouco. Regras:

- Não leia o repositório inteiro. Use `grep -n` e `glob` para localizar; leia só o trecho relevante.
- Leia `CONTEXT.md` sempre; leia `CONTEXT-backend.md` **ou** `CONTEXT-frontend.md`, não ambos sem motivo.
- Rode o teste do módulo afetado durante o desenvolvimento; a suíte completa só no fim.
- Não rode `docker compose up --build` se a mudança pode ser validada com teste unitário.
- Não cole diff ou log gigante na resposta. Resuma e cite `arquivo:linha`.
- Se a tarefa for conceitual ("como funciona X?"), responda com o contexto já carregado e não explore o repo.
- Pare e pergunte quando: requisito ambíguo, mudança de schema destrutiva, necessidade de credencial,
  ou o escopo passar de 8 arquivos fora do módulo da issue.

## 9. Commits — Conventional Commits

Formato obrigatório em todo commit:

```
<tipo>(<escopo opcional>): <descrição no imperativo>
```

| Tipo | Uso |
|------|-----|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `style` | Formatação sem mudança de lógica |
| `refactor` | Refatoração sem mudança de comportamento |
| `test` | Teste novo ou corrigido |
| `chore` | Manutenção, dependências, CI, scripts |

Regras:

- Escopo em minúsculas e curto: `auth`, `turmas`, `email`, `agentes`, `scripts`.
- Descrição em **português**, no **imperativo**, sem ponto final, até **72 caracteres**.
- Um commit por mudança lógica. Não misture feature com refatoração ou formatação.
- Corpo opcional explica **por quê** e impacto; referencie a issue (`Closes #N`) no corpo ou no PR.
- Mudança incompatível: `feat(api)!: ...` e explique o breaking change no corpo.

```bash
git commit -m "feat(turmas): adiciona validação de capacidade"
git commit -m "fix(auth): corrige expiração do token em fuso UTC-3"
git commit -m "docs(agentes): documenta fluxo de review"
```

Proibido: `update`, `ajustes`, `wip`, `fix bug`, `commit`, mensagem vazia de contexto ou mistura de
assuntos no mesmo commit. O push deve conter commits que passariam sozinhos em um review.

## 10. Definição de pronto

- [ ] Teste novo ou atualizado cobrindo o comportamento
- [ ] `cd backend && python -m pytest -q` verde
- [ ] `cd frontend && npm test -- --watch=false` verde (se mexeu no frontend)
- [ ] `cd frontend && npm run build` verde (se mexeu no frontend)
- [ ] `cd backend && alembic heads` com um único head (se mexeu no schema)
- [ ] Sem segredo, token, `.env`, `print()` ou `console.log` no diff
- [ ] Commit no padrão Conventional Commits, em português, até 72 caracteres na primeira linha
- [ ] PR com issue vinculada, o que muda, por quê, como testar e checklist preenchido

## 11. Proibido

- Commitar `.env`, `node_modules`, `dist`, `__pycache__`, `.coverage`, `htmlcov`
- Rodar `git reset --hard`, `git clean -fd` ou `git push --force` sem autorização explícita
- Editar arquivos gerados (`frontend/dist`, `backend/htmlcov`, caches)
- Instalar dependência, trocar versão ou alterar CI por conta própria
- Mascarar falha de teste com `skip`, `xfail` ou removendo asserção
- "Consertar" código não relacionado à issue no mesmo PR
- Inventar endpoints, tabelas, campos ou variáveis de ambiente que não existem no código
