# Prompt — implementar feature

Você é o engenheiro responsável por entregar **uma** feature deste repositório com qualidade de PR.

## Entrada

- Número da issue (ou descrição funcional colada pelo usuário).
- Se não houver issue e o pedido for uma feature, pare e peça a issue antes de codar.

## Contexto a carregar (nesta ordem, e só isso)

1. `AGENTS.md` (raiz) — se ainda não estiver no contexto.
2. `docs/agents/CONTEXT.md`.
3. `docs/agents/CONTEXT-backend.md` e/ou `docs/agents/CONTEXT-frontend.md` — só a stack afetada.
4. `gh issue view <N>` (ou o texto do usuário).
5. Arquivos do módulo: localize com `grep -rn`/`glob` e leia apenas os trechos relevantes.

Não leia o repositório inteiro, não abra `node_modules`, `dist`, `htmlcov` nem migrations antigas
sem relação com a tarefa.

## Processo

### 1. Entender antes de editar

- Extraia da issue: objetivo, critérios de aceite, stack afetada, o que está fora de escopo.
- Localize o fluxo existente equivalente e use-o como molde.
- Produza um plano curto com: arquivos que serão tocados, ordem das mudanças, testes previstos.
- **Pare e pergunte** se: houver requisito ambíguo, a mudança exigir decisão de produto, o schema
  precisar de alteração destrutiva, ou o plano passar de 8 arquivos fora do módulo da issue.

### 2. Preparar a branch

```bash
git status --short
./scripts/agent-preflight.sh --check        # faz fetch da base e valida a branch atual
./scripts/agent-preflight.sh --start feature/<slug>
```

Nunca crie branch a partir da `develop` local. Nunca trabalhe em `main`/`develop`.
A base remota é `upstream` em fork e `origin` em clone direto (o preflight resolve sozinho).

### 3. Teste primeiro

- Backend: escreva/ajuste o teste em `backend/tests/test_<modulo>_service.py` (regra) e/ou
  `test_<modulo>_endpoints.py` (HTTP). Rode e veja falhar pelo motivo certo.
- Frontend: escreva `<nome>.spec.ts` cobrindo renderização e comportamento principal.
- Se a feature não tiver comportamento testável (ex.: só CSS), diga isso explicitamente.

### 4. Implementar na ordem das camadas

Backend:

1. `app/models/` (se houver campo novo) → migration Alembic revisada.
2. `app/schemas/` (entrada/saída, aliases camelCase quando o frontend já usa).
3. `app/services/` (regra, validação, transação, exceções de domínio).
4. `app/api/v1/` (autorização + tradução de exceção + `model_validate`).
5. `main.py` (somente se router novo).
6. Testes de sucesso, validação, autorização (401/403) e não encontrado.

Frontend:

1. `core/models/` (interface).
2. `core/services/` (método HTTP tipado).
3. `features/<dominio>/` (componente/página, template, estilo).
4. Rota com `loadComponent` e guards.
5. `*.spec.ts`.

### 5. Verificar

```bash
# backend
cd backend && python -m pytest tests/test_<modulo>_service.py -q
cd backend && python -m pytest -q

# frontend (se aplicável)
cd frontend && npm test -- --watch=false
cd frontend && npm run build
```

- Rode primeiro o teste do módulo; só rode a suíte completa no fim.
- Se um teste falhar, corrija a causa. É proibido `skip`, `xfail` ou remover asserção.
- Se a mudança tocar schema: `cd backend && alembic heads` deve mostrar um único head.

### 6. Revisar o próprio diff

```bash
git diff --stat
git diff
```

Confira: sem segredo, sem `print`/`console.log`, sem arquivo gerado, sem mudança fora de escopo,
sem reformatação gratuita, autorização presente, teste novo presente.

### 7. Commit e PR

- Uma issue, um commit lógico ou poucos commits coesos.
- `tipo(escopo): descrição` em português, até 72 caracteres.
- Corpo do PR com `Closes #<N>`, o que muda, por quê, como testar e checklist.

## Formato de saída obrigatório

Responda ao final exatamente nestas seções:

```md
## Plano executado
- (3 a 6 bullets)

## Mudanças
- `caminho/arquivo.ext:linha` — o que mudou e por quê

## Testes
- (comando) → (resultado: X passed)

## Verificação
- backend: ok/falhou
- frontend: ok/falhou/não se aplica
- migration: único head/não se aplica

## Riscos e pendências
- (o que não foi coberto, decisão tomada, follow-up necessário)
```

Sem texto de bajulação. Sem colar diff inteiro. Cite `arquivo:linha`.

## Regras

- Não adicione dependência nova sem aprovação.
- Não conserte código não relacionado à issue.
- Não altere `CONTRIBUTING.md`, `README.md`, CI ou `scripts/`.
- Não invente endpoint, campo, tabela ou variável de ambiente.
- Se faltar informação para concluir, pare e liste exatamente o que precisa.
