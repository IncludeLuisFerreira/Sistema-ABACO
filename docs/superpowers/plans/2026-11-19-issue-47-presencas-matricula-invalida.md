# Issue #47 — Presenças não devem ignorar matrícula inválida em silêncio

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `POST /api/v1/presencas` deixa de descartar matrículas fora da turma em silêncio e passa a responder 422 com mensagem clara, sem gravar nada do lote.

**Architecture:** O service valida o batch inteiro antes do loop de persistência e lança `InvalidMatriculasError` com os ids inválidos (sem duplicatas, na ordem do payload). O router traduz a exceção para 422, igual a `notas`. A mensagem exibida ao usuário é montada no router, em português, com plural correto e limite de ids listados.

**Tech Stack:** Python 3.14, FastAPI, SQLAlchemy 2, PostgreSQL 16 (testes em SQLite).

**Spec:** Issue #47 (`gh issue view 47`), achado `BUG-19` da varredura da PR #33 + plano aprovado em conversa.

## Global Constraints

- Sem migration e sem mudança de schema.
- Sem alteração no frontend: `attendance-management.ts` já exibe `err.error.detail`.
- `alembic heads` continua com um único head (`007`).
- Conventional Commits em português, até 72 caracteres na primeira linha.
- Cobertura dos arquivos alterados em 100%.
- Sem `print()` / `console.log` no diff.

## Review Focus

- Batch com mistura de matrícula válida e inválida não pode gravar parcialmente.
- Ids repetidos no payload não podem aparecer repetidos na mensagem.
- Mensagem precisa ler como frase: singular com id, plural com até três ids, plural genérico acima disso.
- Autorização (`verify_cargo` + `enforce_turma_access`) roda antes da validação de matrícula; 403 continua vencendo 422.

---

### Task 1: Service rejeita o batch antes de gravar

**Files:**
- Modify: `backend/app/services/presenca_service.py:14-33`

**Interfaces:**
- Produces: `InvalidMatriculasError(Exception)` com atributo `ids_invalidos: list[int]`; `create_or_update_presencas` levanta a exceção antes de qualquer `add`/`commit`.

- [x] **Step 1: Escrever teste que falha**

```python
def test_raises_para_matricula_fora_da_turma(self, db_session, turma):
    payload = PresencaBatchSchema(
        idTurma=turma.id_turma,
        dataAula=date(2026, 6, 21),
        presencas=[PresencaItemSchema(idMatricula=9999, presente=True)],
    )
    with pytest.raises(InvalidMatriculasError) as exc:
        create_or_update_presencas(db_session, payload)
    assert exc.value.ids_invalidos == [9999]
```

- [x] **Step 2: Rodar e ver falhar**

Run: `cd backend && python -m pytest tests/test_presenca_service.py -q`
Expected: `ImportError: cannot import name 'InvalidMatriculasError'`.

- [x] **Step 3: Implementar**

Calcular `ids_invalidos` com `dict.fromkeys` (dedupe preservando ordem) antes do loop e levantar `InvalidMatriculasError(ids_invalidos)`. Remover o `continue` e o `# FIXME` correspondente.

- [x] **Step 4: Rodar e ver passar**

Run: `cd backend && python -m pytest tests/test_presenca_service.py -q`

### Task 2: Router traduz para 422 com mensagem legível

**Files:**
- Modify: `backend/app/api/v1/presencas.py:1-24`

**Interfaces:**
- Consumes: `InvalidMatriculasError.ids_invalidos`.
- Produces: `HTTPException(422, detail=<frase>)`.

- [x] **Step 1: Escrever teste de contrato**

`test_create_matricula_de_outra_turma_retorna_422` e `test_create_matricula_inexistente_nao_salva_nada` em `TestPresencasEndpoints`, verificando status, frase e ausência de registro salvo.

- [x] **Step 2: Implementar `_matriculas_invalidas_detail`**

| Caso | Mensagem |
|------|----------|
| 1 id | `A matrícula 999999 não pertence à turma informada ou não está ativa.` |
| 2–3 ids | `As matrículas 12, 15 e 18 não pertencem à turma informada ou não estão ativas.` |
| 4+ ids | `Algumas matrículas informadas não pertencem à turma ou não estão ativas.` |

Listar mais de três ids transformaria o alerta global em parede de texto; o professor corrige a seleção na própria tela.

- [x] **Step 3: Cobrir as três variações de mensagem**

`TestMensagemMatriculasInvalidas` fixa a cópia exata das frases.

- [x] **Step 4: Rodar e ver passar**

Run: `cd backend && python -m pytest tests/test_presenca_service.py tests/test_notas_presencas_historico_endpoints.py tests/test_rbac_presencas.py -q`
Expected: `25 passed`.

### Task 3: Verificação final

- [x] `cd backend && python -m pytest -q` → `592 passed, 1 skipped`
- [x] `cd backend && python -m pytest ... --cov-report=term-missing` → `presencas.py` 100%, `presenca_service.py` 100%
- [x] `cd backend && alembic heads` → `007 (head)`
- [x] Frontend não alterado → sem `npm test` / `npm run build`

## Documentação

Nenhum doc de feature documenta o comportamento silencioso: `README.md` descreve apenas "registro em lote", `docs/requirements/PRD.md` mapeia `0/1`, `docs/analise-rotas-admin.md` lista rota e cargo (inalterados), e `docs/reviews/2026-11-11-varredura-bugs.md` não existe no repositório. Nada a corrigir fora deste plano.

## Commits

1. `fix(presencas): rejeita matricula invalida no batch`
2. `docs(agentes): adiciona plano da issue 47`

## Riscos

- Professor com tela desatualizada que envie matrícula de outra turma passa a receber erro em vez de salvamento parcial — comportamento desejado pela issue.
- O alerta global é `sticky` no topo e quebra linha; mensagens longas foram limitadas a três ids para não transformar o aviso em bloco ilegível.
