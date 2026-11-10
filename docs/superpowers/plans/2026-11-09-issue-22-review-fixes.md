# Issue #22 — Correções do code review do PR #25

**Goal:** Resolver os pontos do review do PR #25 sem reabrir o escopo da issue #22.

**Spec:** Comentários de review do PR #25 (celsohd21 e SamuelBarbosaF) + critérios da issue #22.

## Global Constraints

- Manter validação estrita em `TurmaCreateSchema` e `TurmaUpdateSchema`.
- Leitura de turmas com `avaliacoes` legadas nunca pode retornar 500 nem descartar dados silenciosamente.
- Nenhuma migration destrutiva.
- Não redesenhar a tela de turmas.
- Não alterar fluxo de matrícula.
- Não alterar CI, `scripts/` ou `docs/qa/` (arquivos não rastreados do usuário).
- Não adicionar dependências.
- Não fazer push durante as tasks; push só no final, após review.
- Código e mensagens em português, seguindo o estilo existente.

## Fora de escopo (rulings)

- Gate de cobertura no CI: exige aprovação explícita para alterar CI; follow-up separado.
- Constantes de domínio (`cargo == 2`, `status == 0`): refatoração transversal em 6 arquivos; follow-up separado.
- Roteiro visual/script: permanecem fora do PR; evidência será registrada em comentário do PR.

---

### Task 1: Compatibilidade de leitura para avaliações legadas

**Files:**
- Modify: `backend/app/schemas/turma_schema.py`
- Modify: `backend/tests/test_turma_schema.py`
- Modify: `backend/tests/test_turmas_endpoints.py`

**Interfaces:**
- Produces: `AvaliacaoResponseSchema` (leitura tolerante) usado por `TurmaResponseSchema.avaliacoes`.
- `AvaliacaoSchema` existente permanece estrito para create/update.

**Regra de leitura:**
- `nome`, `tipo` e `peso` aceitam ausência/`null`.
- `tipo` string conhecido em qualquer caixa (`Prova`, `TRABALHO`) é normalizado para `prova`/`trabalho`.
- `tipo` desconhecido (`seminario`) é preservado como veio.
- Chaves extras de registros legados são preservadas (`extra="allow"`).
- Nada é descartado silenciosamente.

- [x] **Step 1: Escrever testes de schema (falhar primeiro)**
  - resposta com `{"nome": "Legada", "tipo": "Prova", "peso": null}` valida e normaliza `tipo` para `prova`;
  - resposta com `{"nome": "Legada", "tipo": "seminario", "peso": 10}` valida e preserva `seminario`;
  - resposta com item sem `nome`/`tipo`/`peso` valida;
  - chave extra (`observacao`) permanece em `model_dump()`.

- [x] **Step 2: Implementar o schema de leitura**

- [x] **Step 3: Escrever testes de endpoint (falhar primeiro)**
  - gravar turma legada direto via `db_session` com `avaliacoes=[{"nome": "Legada", "tipo": "seminario", "peso": 10, "observacao": "antiga"}]`;
  - `GET /api/v1/turmas` → 200 e preserva `tipo`/chave extra;
  - `GET /api/v1/turmas/{id}` → 200;
  - `PUT /api/v1/turmas/{id}` com `{"capacidade": 25}` → 200, resposta 200 e banco com capacidade 25.

- [x] **Step 4: Rodar e ver passar**
  - `cd backend && .venv/bin/python -m pytest tests/test_turma_schema.py tests/test_turmas_endpoints.py -q`
  - `cd backend && .venv/bin/python -m pytest tests -q`

---

### Task 2: Testes do fluxo de erro no frontend

**Files:**
- Create: `frontend/src/app/features/classes/pages/classes-management/classes-management.spec.ts`

**Casos:**
- create com HTTP 422 (`detail` string) → `formError` recebe a mensagem, toast de erro, `saving=false`, painel continua aberto;
- update com HTTP 409 (capacidade abaixo das vagas) → `formError` recebe a mensagem do backend;
- usar `TurmaService`, `CursoService`, `UsuarioService` e `DialogService` mockados; `NotificationService` real com spy.
- Não testar template/visual.

- [x] **Step 1: Escrever os testes (falhar primeiro)**
- [x] **Step 2: Ajustar apenas o necessário para passar (sem alterar comportamento de produção, salvo defeito real)**
- [x] **Step 3: Rodar**
  - `cd frontend && npm test -- --run src/app/features/classes/pages/classes-management/classes-management.spec.ts`
  - `cd frontend && npm test -- --run`

---

### Task 3: Alinhar regra visual do peso

**Files:**
- Modify: `frontend/src/app/features/classes/components/class-form/class-form.html`
- Modify: `frontend/src/app/features/classes/components/class-form/class-form.spec.ts`

**Regra:** backend e validator Angular aceitam peso `> 0`. O HTML deve refletir isso.

- [x] **Step 1: Ajustar input para `min="0.01" step="0.01"`, remover `max="100"`**
- [x] **Step 2: Adicionar teste de componente aceitando peso fracionário positivo (`0.5`)**
- [x] **Step 3: Rodar o spec do formulário**

---

### Task 4: Verificação manual/API

- [x] **Step 1: Rebuild da stack** (`docker compose up -d --build`) sem apagar volume.
- [x] **Step 2: Rodar `bash scripts/verify_issue_22.sh`** e registrar saída no relatório/ledger.
- [x] **Step 3: Registrar evidência para comentário do PR.**

---

## Verificação final

- [x] `cd backend && .venv/bin/python -m pytest tests -q`
- [x] `cd frontend && npm test -- --run`
- [x] `cd frontend && npm run build`
- [ ] Review final do diff completo (base `8ed1aad`).
- [ ] Rebase em `origin/develop` e push da branch do PR.

---

## Resultado da verificação

Verificação final em 2026-11-09:

- Backend: `491 passed, 1 skipped` (`482 passed, 1 skipped` antes dos testes desta onda).
- Frontend: `18 arquivos / 120 testes` (`18 arquivos / 112 testes` antes dos testes desta onda).
- Build: `npm run build` concluído com sucesso.
- API: `scripts/verify_issue_22.sh` → `PASS=23 FAIL=0` (execução da onda anterior).
- PostgreSQL real com linha legada: `GET /api/v1/turmas` e `GET /api/v1/turmas/{id}` → 200; `PUT` de capacidade → 200; chaves extras preservadas.
- Correções desta onda: formatos legados de `avaliacoes` nunca retornam 500; formulário tolera `nome` escalar e itens não-objeto; edição preserva avaliações legadas via `avaliacoesChanged`; `diasAula` nulo não vira domingo.
