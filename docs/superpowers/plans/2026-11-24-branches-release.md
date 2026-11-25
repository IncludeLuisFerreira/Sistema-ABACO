# Papéis de `main`/`develop` e processo de release — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Documentar em `CONTRIBUTING.md` e `AGENTS.md` que `main` é a versão estável em produção, `develop` é o ambiente de desenvolvimento/teste, e que `main` só avança por release SemVer versionada, com hotfix e back-merge obrigatório.

**Architecture:** Duas edições de documentação, sem tocar em código, CI ou schema. `CONTRIBUTING.md` ganha a seção §4 "Modelo de Releases" (processo completo) e tem as seções seguintes renumeradas; `AGENTS.md` ganha regras curtas e imperativas para agentes que apenas apontam para o `CONTRIBUTING.md`.

**Tech Stack:** Markdown. Verificação por `grep`/script de âncoras e por inspeção das referências cruzadas.

**Spec:** `docs/superpowers/specs/2026-11-24-branches-release-design.md`

## Global Constraints

- Não alterar `.github/workflows/`, `scripts/`, `README.md`, código de aplicação, testes ou migrations.
- Sem `CHANGELOG.md` manual; notas de release são geradas pelo GitHub.
- Fonte única de versão: tag anotada `vX.Y.Z`. Não sincronizar `frontend/package.json` nem `/api/health`.
- Processo detalhado vive em `CONTRIBUTING.md`; `AGENTS.md` só tem regra curta + ponteiro (sem duplicar texto).
- Preservar estilo local: `CONTRIBUTING.md` usa `##` numerado com `---` entre seções; `AGENTS.md` usa lista numerada em §4.
- Commits em Conventional Commits, português, imperativo, ≤72 caracteres na primeira linha.
- Não reescrever trechos não relacionados: editar apenas as linhas necessárias.

## Review Focus

1. Renumeração de `CONTRIBUTING.md` quebra o link interno `[Testes](#10-testes)` (linha 267) e as âncoras do índice — ambos devem apontar para os novos números.
2. Contradição entre §3 ("`main` recebe merges apenas da `develop`") e o fluxo de hotfix (que sai da `main`) — o texto de §3 precisa cobrir `release/` **e** `hotfix/`.
3. Exemplos de versão incorretos: patch de `v1.0.1` é `v1.0.2`, não `v1.0.1`; cada exemplo deve ser aritmeticamente válido.
4. Regra para agentes ambígua o bastante para um agente criar tag ou mergear em `main` por conta própria — deve ser proibitiva e explícita.
5. Duplicação de texto entre `AGENTS.md` e `CONTRIBUTING.md` que pode divergir depois — `AGENTS.md` só referencia, não repete o passo a passo.

---

### Task 1: `CONTRIBUTING.md` — seção "Modelo de Releases" e renumeração

**Files:**
- Modify: `CONTRIBUTING.md` (índice linhas 9-23; §3 linhas 105-127; §4 em diante renumerado; link interno na linha 267)

**Interfaces:**
- Produces: seção `## 4. Modelo de Releases` com âncora `#4-modelo-de-releases`; seções antigas 4-12 passam a ser 5-13 (`#5-fluxo-de-trabalho-completo` … `#13-processo-de-code-review`).

- [ ] **Step 1: Renumerar os títulos existentes 4-12 para 5-13**

Em `CONTRIBUTING.md`, alterar apenas o número no início de cada título `## N.`:

| De | Para |
|----|------|
| `## 4. Fluxo de Trabalho Completo` | `## 5. Fluxo de Trabalho Completo` |
| `## 5. Convenção de Branches` | `## 6. Convenção de Branches` |
| `## 6. Convenção de Commits` | `## 7. Convenção de Commits` |
| `## 7. Abrindo uma Issue` | `## 8. Abrindo uma Issue` |
| `## 8. Implementando uma Feature ou Bugfix` | `## 9. Implementando uma Feature ou Bugfix` |
| `## 9. Padrões de Código` | `## 10. Padrões de Código` |
| `## 10. Testes` | `## 11. Testes` |
| `## 11. Abrindo um Pull Request` | `## 12. Abrindo um Pull Request` |
| `## 12. Processo de Code Review` | `## 13. Processo de Code Review` |

Ordem decrescente (12 → 4) para não colidir com números já existentes.

- [ ] **Step 2: Atualizar o link interno de "Testes"**

Na seção "Implementando uma Feature ou Bugfix" (agora §9), trocar:

`Veja a seção [Testes](#10-testes) para detalhes.`

por:

`Veja a seção [Testes](#11-testes) para detalhes.`

- [ ] **Step 3: Atualizar o índice**

Substituir as linhas 11-22 do índice pela lista abaixo (numeração e alvos novos, mais a linha de releases):

```markdown
1. [Pré-requisitos](#1-pré-requisitos)
2. [Configuração do Ambiente](#2-configuração-do-ambiente)
3. [Modelo de Branches](#3-modelo-de-branches)
4. [Modelo de Releases](#4-modelo-de-releases)
5. [Fluxo de Trabalho Completo](#5-fluxo-de-trabalho-completo)
6. [Convenção de Branches](#6-convenção-de-branches)
7. [Convenção de Commits](#7-convenção-de-commits)
8. [Abrindo uma Issue](#8-abrindo-uma-issue)
9. [Implementando uma Feature ou Bugfix](#9-implementando-uma-feature-ou-bugfix)
10. [Padrões de Código](#10-padrões-de-código)
11. [Testes](#11-testes)
12. [Abrindo um Pull Request](#12-abrindo-um-pull-request)
13. [Processo de Code Review](#13-processo-de-code-review)
```

- [ ] **Step 4: Atualizar o diagrama e a tabela de §3 para incluir release e hotfix**

No bloco de código do diagrama de branches, substituir por:

```
main        ← versões estáveis em produção (cada merge recebe tag vX.Y.Z)
  └── develop   ← ambiente de desenvolvimento e teste, integração contínua
        ├── feature/nome    ← seu trabalho acontece aqui (no seu fork)
        ├── fix/nome
        └── docs/nome

release/vX.Y.Z   ← sai da develop, entra na main, vira tag
hotfix/vX.Y.Z    ← sai da main, volta para a develop depois da tag
```

Na linha `- **\`main\`** recebe merges apenas da \`develop\`, quando a versão estiver estável e testada.`, substituir por:

```markdown
- **`main`** é a versão estável em produção. Recebe apenas PRs de `release/vX.Y.Z` (a partir da `develop`) ou de `hotfix/vX.Y.Z` (a partir da própria `main`), conforme a seção [Modelo de Releases](#4-modelo-de-releases).
- **`develop`** é o ambiente de desenvolvimento e teste: tudo é integrado e validado aqui antes de virar release.
```

- [ ] **Step 5: Inserir a seção `## 4. Modelo de Releases` antes de `## 5. Fluxo de Trabalho Completo`**

Conteúdo exato:

````markdown
## 4. Modelo de Releases

`main` é a **versão estável em produção**. Não recebe commits de feature: recebe apenas releases
versionadas, sempre vindas da `develop`. `develop` é o **ambiente de desenvolvimento e teste** —
tudo é integrado e validado nela primeiro.

### Versionamento (SemVer)

Toda release recebe uma tag anotada `vX.Y.Z` na `main`. O número não é escolhido por opinião: ele
sai dos commits acumulados na `develop` desde a última tag.

| O que entrou desde a última tag | Bump | Exemplo |
|---------------------------------|------|---------|
| Apenas `fix` / `perf` | patch | `v1.0.0` → `v1.0.1` |
| Pelo menos um `feat` | minor | `v1.0.1` → `v1.1.0` |
| Breaking change (`!` ou `BREAKING CHANGE`) | major | `v1.1.0` → `v2.0.0` |

`docs`, `style`, `test`, `chore` e `refactor` sem mudança de comportamento **não geram release**
sozinhos. Se não houver `fix`, `perf`, `feat` ou breaking change pendente, não há release.

A tag é a fonte única da versão. Não sincronize `frontend/package.json` nem `/api/health` com ela.

### Abrindo uma release

1. Confirme que a `develop` está verde no CI e que não há PR pendente que deveria entrar na versão.
2. Atualize sua `develop` local a partir da base remota e crie a branch de release:

```bash
git fetch origin
git switch -c release/v1.0.1 origin/develop
git push -u origin release/v1.0.1
```

3. Abra o PR de release para a `main`:

```bash
gh pr create --base main --title "release: v1.0.1" --body "Closes #<issue>"
```

4. O PR de release exige **2 aprovações**, nenhuma do autor. Só quem tem permissão de manutenção no
   repositório aprova release; contribuidores sem essa permissão participam da discussão.
5. Faça merge com **merge commit**, nunca squash — o histórico de releases precisa ficar legível.
6. Na `main`, crie a tag anotada e publique o GitHub Release com notas geradas dos commits:

```bash
git switch main && git pull
git tag -a v1.0.1 -m "release: v1.0.1"
git push origin v1.0.1
gh release create v1.0.1 --generate-notes --title "v1.0.1"
```

7. Faça o back-merge da `main` para a `develop` (PR `main → develop`) para que o ambiente de
   desenvolvimento não fique atrás da produção.

### Hotfix (bug em produção)

Bug na `main` **não** se resolve desfazendo histórico. Se o incidente for grave, o deploy volta
para a tag anterior como contenção; o código se corrige com um novo patch.

1. Crie a branch a partir da `main`:

```bash
git fetch origin
git switch -c hotfix/v1.0.2 origin/main
```

2. Abra o PR `hotfix/v1.0.2 → main` com o mesmo ritual de aprovação do release (2 aprovações).
3. Faça merge, crie a tag `v1.0.2` e publique o GitHub Release.
4. **Back-merge obrigatório** para a `develop` (PR `main → develop`), referenciando o PR da `main`.
   Sem isso a correção volta como bug no próximo release.

### O que é proibido

- Reescrever, mover ou apagar tag já publicada (`git tag -d` seguido de novo push, `--force` em tag).
- Usar `git revert` de uma release para "voltar de versão" — versão publicada é imutável.
- Mergear na `main` fora do fluxo de release ou de hotfix.
- Abrir PR de feature ou fix direto para a `main`.

---
````

- [ ] **Step 6: Verificar âncoras e numeração**

Run:

```bash
grep -n '^## [0-9]' CONTRIBUTING.md
```

Expected: títulos `1` a `13` em ordem, sem número repetido e com `4. Modelo de Releases` presente.

Run:

```bash
grep -o '](#[^)]*)' CONTRIBUTING.md | sort -u
```

Expected: apenas alvos `#1-…` a `#13-…` correspondentes aos títulos; nenhum `#10-testes` restante.

- [ ] **Step 7: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs(contributing): define modelo de releases e papeis das branches"
```

---

### Task 2: `AGENTS.md` — regras de release para agentes

**Files:**
- Modify: `AGENTS.md` (§2 tabela de fonte de verdade; §4 regras inegociáveis; §9 commits)

**Interfaces:**
- Consumes: `CONTRIBUTING.md` §4 `Modelo de Releases` (criada na Task 1) — referenciar por número, sem repetir passos.
- Produces: regras numeradas `2` e `3` em §4; antigas `2`-`14` passam a ser `4`-`16`.

- [ ] **Step 1: Adicionar linha na tabela de §2**

Após a linha `| Processo humano: issue, branch, commit, PR, review | \`CONTRIBUTING.md\` |`, inserir:

```markdown
| Release, hotfix e versionamento (SemVer) | `CONTRIBUTING.md` §4 |
```

- [ ] **Step 2: Inserir as regras 2 e 3 em §4 e renumerar as demais**

Inserir logo após a regra 1 (`Nunca faça push direto em main ou develop...`), em ordem decrescente
a partir de 14 para evitar colisão:

```markdown
2. `main` é produção: só recebe PR de `release/vX.Y.Z` ou de `hotfix/vX.Y.Z`. Nunca merge direto,
   nunca feature ou fix direto para ela. `develop` é o ambiente de desenvolvimento e teste.
3. Versão é SemVer derivado dos commits (`fix`/`perf` → patch, `feat` → minor, breaking → major) e
   registrada em tag anotada `vX.Y.Z` na `main`. Agente não cria tag, não mergeia em `main` e não
   decide número de versão: prepara o PR de release e o texto das notas, e espera confirmação humana.
```

Renumerar as regras antigas: `2`→`4`, `3`→`5`, `4`→`6`, `5`→`7`, `6`→`8`, `7`→`9`, `8`→`10`,
`9`→`11`, `10`→`12`, `11`→`13`, `12`→`14`, `13`→`15`, `14`→`16`. Nenhuma referência a números de
regra existe fora do próprio `AGENTS.md` (verificado), então a renumeração só afeta a lista.

- [ ] **Step 3: Registrar a convenção de título de release em §9**

Na seção "9. Commits — Conventional Commits", após a linha que lista os tipos, inserir:

```markdown
Release e hotfix usam o mesmo padrão: título do PR `release: vX.Y.Z` (ou `hotfix: vX.Y.Z`), e a
tag resultante é `vX.Y.Z`. O tipo dos commits desde a última tag determina o bump — ver
`CONTRIBUTING.md` §4.
```

- [ ] **Step 4: Verificar numeração e ausência de duplicação**

Run:

```bash
grep -nE '^[0-9]+\. ' AGENTS.md | head -30
```

Expected: sequência contínua `1` a `16` em §4, sem número repetido ou faltando.

Run:

```bash
grep -nE 'git tag|gh release|git switch main' AGENTS.md
```

Expected: nenhuma linha com os comandos de release — `AGENTS.md` só aponta para o `CONTRIBUTING.md`.

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md
git commit -m "docs(agentes): proibe agente de criar tag e mergear na main"
```

---

### Task 3: Consistência entre os dois documentos

**Files:**
- Modify: `CONTRIBUTING.md` ou `AGENTS.md` apenas se a verificação encontrar divergência.

- [ ] **Step 1: Conferir referência cruzada**

Run:

```bash
grep -n 'CONTRIBUTING.md.*§4\|Modelo de Releases' AGENTS.md CONTRIBUTING.md
```

Expected: `AGENTS.md` cita `CONTRIBUTING.md` §4 nas duas ocorrências; `CONTRIBUTING.md` contém o
título `## 4. Modelo de Releases`.

- [ ] **Step 2: Conferir que não sobrou afirmação antiga sobre `main`**

Run:

```bash
grep -n 'recebe merges apenas da' CONTRIBUTING.md
```

Expected: nenhuma saída (texto substituído na Task 1, Step 4).

- [ ] **Step 3: Conferir exemplos de versão**

Run:

```bash
grep -n 'v1\.0\|v1\.1\|v2\.0' CONTRIBUTING.md
```

Expected: `v1.0.0 → v1.0.1`, `v1.0.1 → v1.1.0`, `v1.1.0 → v2.0.0` e hotfix usando `v1.0.2` a
partir de `v1.0.1` — nenhum patch repetindo o número da versão anterior.

- [ ] **Step 4: Conferir diff final**

Run:

```bash
git diff --stat HEAD~2
git status --short
```

Expected: apenas `CONTRIBUTING.md` e `AGENTS.md` modificados; nenhuma mudança em código, CI,
`README.md`, `scripts/` ou `frontend/package.json`. Os arquivos não rastreados pré-existentes em
`docs/superpowers/` permanecem intocados.

- [ ] **Step 5: Registrar divergência (somente se houver)**

Se algum passo acima falhar, corrigir o texto em `CONTRIBUTING.md` (processo) ou `AGENTS.md`
(regra) e commitar:

```bash
git commit -m "docs: alinha texto de release entre contributing e agents"
```

Caso contrário, não criar commit vazio.
