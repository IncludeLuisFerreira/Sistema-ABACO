# Issue #44 — Conflito de horário por interseção de dias

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detectar conflito de turma quando os dias de aula têm qualquer interseção e recalcular o aviso automaticamente ao alterar datas ou dias.

**Architecture:** `ClassFormComponent` passa a observar os controles que afetam o contexto com `merge + valueChanges`, mantendo `updateContexto()` como única fonte de cálculo. A comparação de dias vira interseção de conjuntos numéricos.

**Tech Stack:** Angular 21 standalone, TypeScript 5.9, RxJS 7.8, Vitest 4.

**Spec:** Issue #44 (`gh issue view 44`) + plano aprovado em conversa.

## Global Constraints

- Sem backend, migration ou alteração de documentação de feature.
- Preservar estilo local e não reformatar arquivos inteiros.
- Cobertura ≥ 70% para `class-form.ts`.
- Conventional Commits em português, até 72 caracteres na primeira linha.

## Review Focus

- `"1,3"` × `"1,3,5"` precisa gerar aviso.
- `"1,3"` × `"2,4"` não pode gerar falso positivo.
- Alterar dias ou datas deve recalcular sem chamada manual a `updateContexto()`.
- `patchForm()` não pode quebrar o cálculo inicial nem criar assinatura duplicada.
- Edição da própria turma continua ignorada no conflito.

---

### Task 1: Testes de interseção e reatividade

**Files:**
- Test: `frontend/src/app/features/classes/components/class-form/class-form.spec.ts`

- [ ] **Step 1: Escrever testes que falham**

Adicionar testes para:
- dias parcialmente coincidentes (`"1,3,5"` contra `"1,3"`) → `conflitoLabel` contém `"já tem"`;
- dias sem interseção (`"2,4"` contra `"1,3"`) → `conflitoLabel` nulo;
- alterar dias de `"1,3"` para `"2,4"` sem chamar `updateContexto()` → aviso some;
- alterar datas sem chamar `updateContexto()` → aviso aparece/some.

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd frontend && npm test -- --watch=false`
Expected: FAIL nos cenários de interseção parcial e recálculo automático.

### Task 2: Implementação no componente

**Files:**
- Modify: `frontend/src/app/features/classes/components/class-form/class-form.ts`
- Modify: `frontend/src/app/features/classes/components/class-form/class-form.html`

**Interfaces:**
- Produces: `parseDiasAula(value: string | null | undefined): Set<number>` e `diasAulaSobrepoem(a, b): boolean` no módulo do componente.

- [ ] **Step 1: Implementar helpers**

`parseDiasAula` separa por vírgula, converte para número e mantém inteiros de 0 a 6. `diasAulaSobrepoem` retorna verdadeiro quando há ao menos um dia em comum.

- [ ] **Step 2: Trocar a comparação**

No filtro de conflitos, substituir `t.diasAula === diasAulaStr` por `diasAulaSobrepoem(t.diasAula, diasAulaStr)`.

- [ ] **Step 3: Reagir a mudanças**

No construtor, assinar com `merge(...)` os `valueChanges` de `idCurso`, `idProfessor`, `dataInicio`, `dataFim` e `diasAula`, usando `takeUntilDestroyed(this.destroyRef)`, chamando `updateContexto()`.

Remover `(change)="updateContexto()"` de datas/checkbox, `(change)="onCursoChange()"`/`onProfessorChange()` dos selects e os métodos que ficarem sem uso.

- [ ] **Step 4: Rodar e ver passar**

Run: `cd frontend && npm test -- --watch=false`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/features/classes/components/class-form/
git commit -m "fix(turmas): detecta conflito por intersecao de dias"
```

### Task 3: Verificação final

- [ ] **Step 1: Suíte e build**

```bash
cd frontend && npm test -- --watch=false
cd frontend && npm run build
```

- [ ] **Step 2: Cobertura do arquivo alterado**

Tentar override do `coverageInclude` para `class-form.ts`; se o builder Angular não aceitar, rodar o Vitest/coverage disponível e reportar a limitação com o resultado obtido.

Expected: `class-form.ts` ≥ 70%.
