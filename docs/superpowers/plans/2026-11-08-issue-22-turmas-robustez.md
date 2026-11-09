# Issue #22 — Turmas: confirmação, testes e robustez — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Tornar obrigatórios e validados os campos de abertura/configuração de turmas, impedir atualizações que apaguem campos obrigatórios ou reduzam capacidade abaixo das vagas ocupadas, e cobrir o módulo com testes.

**Architecture:** Validação de forma/tipo no Pydantic (422); validação de regra de negócio no service (400/409), com exceções específicas mapeadas na API. O model e o banco permanecem nullable para dados legados; nenhuma migration destrutiva.

**Tech Stack:** FastAPI, Pydantic v2, SQLAlchemy, pytest, Angular 21 (Reactive Forms), Vitest.

**Spec:** Issue #22 (GitHub) + decisões aprovadas na conversa.

## Global Constraints

- Não fazer commit nem push sem autorização explícita do usuário.
- Não criar migration destrutiva.
- Não redesenhar a tela de turmas.
- Não alterar o fluxo de matrícula, exceto a leitura de vagas ocupadas na atualização da turma.
- `POST` continua retornando 200.
- Código e mensagens em português, seguindo o estilo existente.

## Review Focus

- Turma legada com campos nulos: `GET` continua funcionando; edição exige preencher os obrigatórios, mas não deve quebrar por causa de data nula legada.
- `diasAula` legado (`"Seg/Qua"`): leitura funciona; novo create/update aceita apenas `0`–`6` separados por vírgula, sem duplicatas.
- Update parcial: campo omitido não pode ser tratado igual a `null` explícito.
- Capacidade igual ao número de vagas ocupadas é válida; apenas menor é conflito.
- `avaliacoes: []` e `avaliacoes: null` são aceitos; item inválido retorna 422.

---

### Task 1: Schema tipado e validações de entrada

**Files:**
- Modify: `backend/app/schemas/turma_schema.py`
- Test: `backend/tests/test_turma_schema.py` (criar)

**Interfaces:**
- Produces:
  - `AvaliacaoSchema` com `nome: str`, `tipo: Literal["prova", "trabalho"]`, `peso: float`
  - `TurmaCreateSchema(idCurso: int, idProfessor: int, capacidade: int, dataInicio: date, dataFim: date, diasAula: str, avaliacoes: list[AvaliacaoSchema] | None = None)`
  - `TurmaUpdateSchema` com os mesmos campos opcionais
  - `TurmaResponseSchema.avaliacoes: list[AvaliacaoSchema] | None`

- [x] **Step 1: Escrever testes de schema**

Casos:
- payload completo válido;
- capacidade `0` e `-1` → `ValidationError`;
- `diasAula` inválido: `""`, `"7"`, `"Seg"`, `"1,"`, `",1"`, `"1,,2"`, `"1, 2"`, `"1,1"` → erro;
- `diasAula` válido: `"0"`, `"0,6"`, `"1,3,5"`;
- `avaliacoes` inválida: `nome=""`, `nome="   "`, `tipo="seminario"`, `peso=0`, `peso=-1` → erro;
- ausência de cada campo obrigatório → erro.

- [x] **Step 2: Rodar e ver falhar**

Run: `cd backend && .venv/bin/python -m pytest tests/test_turma_schema.py -q --no-cov`
Expected: FAIL.

- [x] **Step 3: Implementar schemas**

Usar `Field(gt=0)`, `Literal`, `field_validator("nome")` com `strip` e não vazio, e validador de `diasAula` sem duplicatas.

- [x] **Step 4: Rodar e ver passar**

Run: `cd backend && .venv/bin/python -m pytest tests/test_turma_schema.py -q --no-cov`
Expected: PASS.

---

### Task 2: Regras de criação no service

**Files:**
- Modify: `backend/app/services/turma_service.py`
- Test: `backend/tests/test_turma_service.py`

**Interfaces:**
- Produces:
  - `DatasInvalidasError`
  - `ProfessorCargoInvalidoError`
  - `_validate_datas(data_inicio: date, data_fim: date) -> None`
  - `_resolve_professor` exige `cargo == 2`

- [x] **Step 1: Escrever testes de criação**

Casos:
- criação completa válida;
- `dataFim < dataInicio` → `DatasInvalidasError`;
- professor com `cargo != 2` → `ProfessorCargoInvalidoError`;
- professor inexistente continua → `ProfessorNotFoundForTurmaError`.

- [x] **Step 2: Rodar e ver falhar**

Run: `cd backend && .venv/bin/python -m pytest tests/test_turma_service.py -q --no-cov`
Expected: FAIL.

- [x] **Step 3: Implementar validações no service**

`create_turma` chama `_resolve_curso`, `_resolve_professor` e `_validate_datas` antes de persistir.

- [x] **Step 4: Rodar e ver passar**

Run: `cd backend && .venv/bin/python -m pytest tests/test_turma_service.py -q --no-cov`
Expected: PASS.

---

### Task 3: Robustez da atualização

**Files:**
- Modify: `backend/app/services/turma_service.py`
- Test: `backend/tests/test_turma_service.py`

**Interfaces:**
- Produces:
  - `CampoObrigatorioError(campo: str)`
  - `CapacidadeAbaixoDasVagasError(vagas: int)`

- [x] **Step 1: Escrever testes de update**

Casos:
- `null` explícito em `idCurso`, `idProfessor`, `capacidade`, `dataInicio`, `dataFim`, `diasAula` → `CampoObrigatorioError`;
- omitir campo não falha;
- capacidade abaixo de `vagas_ocupadas` → `CapacidadeAbaixoDasVagasError`;
- capacidade igual às vagas ocupadas → sucesso;
- alterar apenas `dataInicio` para depois da `dataFim` existente → `DatasInvalidasError`;
- turma legada com data nula atualizada em outro campo → sucesso.

- [x] **Step 2: Rodar e ver falhar**

Run: `cd backend && .venv/bin/python -m pytest tests/test_turma_service.py -q --no-cov`
Expected: FAIL.

- [x] **Step 3: Implementar update**

Usar `payload.model_fields_set`; mesclar datas com o estado atual; validar apenas quando ambas existirem; validar capacidade quando enviada.

- [x] **Step 4: Rodar e ver passar**

Run: `cd backend && .venv/bin/python -m pytest tests/test_turma_service.py -q --no-cov`
Expected: PASS.

---

### Task 4: Mapeamento HTTP e regressão de endpoints

**Files:**
- Modify: `backend/app/api/v1/turmas.py`
- Modify: `backend/tests/conftest.py`
- Modify: `backend/tests/test_turmas_endpoints.py`
- Modify: `backend/tests/test_notas_presencas_historico_endpoints.py`

**Interfaces:**
- Consumes: exceções e schemas das Tasks 1–3.
- Produces: 400 para data/professor/campo obrigatório; 409 para capacidade abaixo das vagas.

- [x] **Step 1: Atualizar fixtures e payloads quebrados**

`conftest.turma`: datas, capacidade e `dias_aula="1,3,5"`. `conftest.seeded`: `dataInicio`, `dataFim`, `diasAula="1"`, `idProfessor`. Payloads equivalentes em testes de notas.

- [x] **Step 2: Escrever testes de endpoint**

Casos:
- create completo → 200;
- campos obrigatórios ausentes → 422;
- `capacidade <= 0` → 422;
- `diasAula` inválido → 422;
- `avaliacoes` inválida → 422;
- `dataFim < dataInicio` → 400;
- professor com cargo 1 → 400;
- update com `null` obrigatório → 400;
- update capacidade abaixo das vagas → 409.

- [x] **Step 3: Rodar e ver falhar**

Run: `cd backend && .venv/bin/python -m pytest tests/test_turmas_endpoints.py tests/test_notas_presencas_historico_endpoints.py -q --no-cov`
Expected: FAIL.

- [x] **Step 4: Implementar mapeamento na API**

Adicionar `except` específicos com mensagens claras.

- [x] **Step 5: Rodar e ver passar**

Run: `cd backend && .venv/bin/python -m pytest tests/test_turmas_endpoints.py tests/test_notas_presencas_historico_endpoints.py -q --no-cov`
Expected: PASS.

---

### Task 5: Formulário Angular robusto

**Files:**
- Modify: `frontend/src/app/core/models/turma.model.ts`
- Modify: `frontend/src/app/features/classes/components/class-form/class-form.ts`
- Modify: `frontend/src/app/features/classes/components/class-form/class-form.html`
- Modify: `frontend/src/app/features/classes/pages/classes-management/classes-management.ts`
- Modify: `frontend/src/app/features/classes/pages/classes-management/classes-management.html`
- Test: `frontend/src/app/features/classes/components/class-form/class-form.spec.ts` (criar)

**Interfaces:**
- Produces: `ClassFormSubmit` com `capacidade: number`, `idProfessor: number`, `dataInicio: string`, `dataFim: string`, `diasAula: string`; `@Input() errorMessage: string | null`.

- [x] **Step 1: Escrever testes do formulário**

Casos:
- formulário incompleto não emite `save`;
- `dataFim < dataInicio` não emite;
- nenhum dia selecionado não emite;
- avaliação com `peso <= 0` não emite;
- formulário válido emite payload sem `null` nos obrigatórios.

- [x] **Step 2: Rodar e ver falhar**

Run: `cd frontend && npm test -- --run src/app/features/classes/components/class-form/class-form.spec.ts`
Expected: FAIL.

- [x] **Step 3: Implementar validadores e mensagens**

Validators `required`/`min(1)`; validador de grupo para datas; validador de ao menos um dia; linha de avaliação com `nome` obrigatório, `tipo` e `peso > 0`; exibir `errorMessage` inline.

- [x] **Step 4: Rodar e ver passar**

Run: `cd frontend && npm test -- --run src/app/features/classes/components/class-form/class-form.spec.ts`
Expected: PASS.

---

### Task 6: Verificação final

- [x] **Step 1: Suíte backend**

Run: `cd backend && .venv/bin/python -m pytest tests -q`
Expected: PASS.

- [x] **Step 2: Cobertura do módulo**

Run: `cd backend && .venv/bin/python -m pytest tests --cov=app.services.turma_service --cov=app.schemas.turma_schema --cov=app.api.v1.turmas --cov-report=term-missing`
Expected: cobertura ≥ 70% nos três módulos.

- [x] **Step 3: Frontend**

Run: `cd frontend && npm test -- --run && npm run build`
Expected: PASS.

- [ ] **Step 4: Checklist manual**

Criar turma completa, editar, tentar salvar inválidos e excluir turma sem vínculos.

---

## Auditoria pós-implementação

Correções aplicadas após revisão do escopo:

- [x] Normalizar erro 422 do FastAPI no frontend (`getApiErrorMessage`), evitando `[object Object]`.
- [x] `avaliacoes`: `null`/omitido preserva; lista vazia `[]` limpa.
- [x] Duplicar turma preenche o formulário e limpa apenas as datas.
- [x] Alerta de conflito recalcula quando datas mudam.
- [x] Testes de update para cargo inválido, `diasAula` inválido, capacidade zero e avaliação inválida.
- [ ] Checklist manual.
