# Guia de Contribuição — SGA ABACO

Bem-vindo ao guia de contribuição do **SGA ABACO**. Este documento define o processo obrigatório para todos os membros da equipe ao implementar features, corrigir bugs ou realizar qualquer alteração no repositório.

Leia com atenção antes de abrir sua primeira issue ou Pull Request.

---

## Índice

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

---

## 1. Pré-requisitos

Antes de qualquer coisa, certifique-se de ter instalado:

- [Git](https://git-scm.com/)
- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.11+](https://www.python.org/) (para desenvolvimento local do backend)
- [Node.js 20+](https://nodejs.org/) e [Angular CLI](https://angular.dev/tools/cli) (para desenvolvimento local do frontend)

Portas **3000**, **8000** e **5432** devem estar disponíveis na sua máquina.

---

## 2. Configuração do Ambiente

### 2.1 Fork e clone

Nenhum membro tem permissão de push direto na main ou na develop. Todo trabalho começa com uma nova **branch**:

```bash
git clone https://github.com/IncludeLuisFerreira/Sistema-ABACO.git
cd Sistema-ABACO
```

4. Adicione o repositório original como remote `upstream` para manter seu fork atualizado:

```bash
git remote add upstream https://github.com/IncludeLuisFerreira/Sistema-ABACO.git
```

Verifique os remotes configurados:

```bash
git remote -v
# origin    https://github.com/SEU-USUARIO/Sistema-ABACO.git (fetch/push)
# upstream  https://github.com/IncludeLuisFerreira/Sistema-ABACO.git (fetch/push)
```

### 2.2 Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env e defina ao menos JWT_SECRET
```

### 2.3 Suba o ambiente com Docker

```bash
chmod +x rebuild.sh
./rebuild.sh
```

Após o rebuild, acesse:
- Frontend: http://localhost:3000
- API Docs (Swagger): http://localhost:8000/docs

### 2.4 Desenvolvimento local sem Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
ng serve
# Acesse http://localhost:4200
```

> O `proxy.conf.json` já está configurado para redirecionar `/api/` para o backend em `localhost:8000`.

---

## 3. Modelo de Branches

O projeto usa um modelo baseado em **Git Flow simplificado** com duas branches protegidas:

```
main        ← versões estáveis em produção (cada merge recebe tag vX.Y.Z)
  └── develop   ← ambiente de desenvolvimento e teste, integração contínua
        ├── feature/nome    ← seu trabalho acontece aqui (no seu fork)
        ├── fix/nome
        └── docs/nome

release/vX.Y.Z   ← sai da develop, entra na main, vira tag
hotfix/vX.Y.Z    ← sai da main, volta para a develop depois da tag
```

### Regras das branches protegidas

| Branch | Propósito | Push direto | Merge via PR | Aprovações mínimas |
|--------|-----------|-------------|--------------|-------------------|
| `main` | Versões estáveis | ❌ Proibido | ✅ Obrigatório | 2 (nenhuma do autor) |
| `develop` | Versão mais recente | ❌ Proibido | ✅ Obrigatório | 1 (não pode ser o autor) |

- **`develop`** é a base para todo desenvolvimento. Toda branch de feature/fix deve ser criada a partir dela.
- **`main`** é a versão estável em produção. Recebe apenas PRs de `release/vX.Y.Z` (a partir da `develop`) ou de `hotfix/vX.Y.Z` (a partir da própria `main`), conforme a seção [Modelo de Releases](#4-modelo-de-releases).
- **`develop`** é o ambiente de desenvolvimento e teste: tudo é integrado e validado aqui antes de virar release.
- Nenhum membro pode aprovar o próprio Pull Request.

---

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

Os comandos abaixo seguem o modelo de fork das seções [Convenção de Branches](#6-convenção-de-branches) e [Implementando uma Feature ou Bugfix](#9-implementando-uma-feature-ou-bugfix): `origin` é o seu fork e `upstream` é o repositório principal (`IncludeLuisFerreira/Sistema-ABACO`). Em clone direto, troque `upstream` por `origin`.

### Abrindo uma release

1. Confirme que a `develop` está verde no CI e que não há PR pendente que deveria entrar na versão.
2. Atualize sua `develop` local a partir da base remota e crie a branch de release:

```bash
git fetch upstream
git switch -c release/v1.0.1 upstream/develop
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
git switch main
git pull --ff-only upstream main
git tag -a v1.0.1 -m "release: v1.0.1"
git push upstream v1.0.1
gh release create v1.0.1 --generate-notes --title "v1.0.1"
```

7. Faça o back-merge da `main` para a `develop` (PR `main → develop`) para que o ambiente de
   desenvolvimento não fique atrás da produção.

### Hotfix (bug em produção)

Bug na `main` **não** se resolve desfazendo histórico. Se o incidente for grave, o deploy volta
para a tag anterior como contenção; o código se corrige com um novo patch.

1. Crie a branch a partir da `main`:

```bash
git fetch upstream
git switch -c hotfix/v1.0.2 upstream/main
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

## 5. Fluxo de Trabalho Completo

```
1. Abra uma Issue descrevendo o que será feito
2. Sincronize seu fork com o upstream/develop
3. Crie uma branch a partir da develop (no seu fork)
4. Implemente, escreva os testes e faça commits
5. Sincronize novamente com upstream/develop antes de abrir o PR
6. Abra um Pull Request: sua branch → develop do repositório principal
7. Aguarde review de pelo menos 1 membro (que não seja você)
8. Após aprovação, o PR é mergeado na develop
```

---

## 6. Convenção de Branches

Use o padrão `tipo/descricao-curta-em-kebab-case`:

| Tipo | Quando usar | Exemplo |
|------|-------------|---------|
| `feature/` | Nova funcionalidade | `feature/relatorio-frequencia` |
| `fix/` | Correção de bug | `fix/calculo-media-notas` |
| `docs/` | Documentação | `docs/atualiza-readme` |
| `refactor/` | Refatoração sem mudança de comportamento | `refactor/service-matricula` |
| `test/` | Adição ou correção de testes | `test/cobertura-pedido-service` |
| `chore/` | Configuração, dependências, CI | `chore/atualiza-requirements` |

```bash
# Sempre sincronize com o upstream antes de criar a branch
git fetch upstream
git checkout develop
git merge upstream/develop

# Crie a branch a partir da develop atualizada
git checkout -b feature/nome-da-sua-feature
```

---

## 7. Convenção de Commits

Siga o padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/):

```
<tipo>(<escopo opcional>): <descrição curta no imperativo>
```

**Tipos aceitos:**

| Tipo | Descrição |
|------|-----------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `perf` | Melhoria de desempenho sem mudança de comportamento |
| `docs` | Alteração em documentação |
| `style` | Formatação, espaços, ponto e vírgula (sem lógica) |
| `refactor` | Refatoração sem mudança de comportamento |
| `test` | Adição ou correção de testes |
| `chore` | Tarefas de manutenção (deps, configs, CI) |

**Exemplos:**

```bash
git commit -m "feat(pedidos): adiciona filtro por status na listagem"
git commit -m "fix(auth): corrige expiração do token JWT em fuso UTC-3"
git commit -m "docs: adiciona seção de deploy no README"
git commit -m "test(estoque): adiciona testes para dar_baixa com quantidade zero"
git commit -m "refactor(turma-service): extrai validação de capacidade para método privado"
```

**Regras:**
- Mensagem em **português**, no imperativo ("adiciona", "corrige", "remove")
- Máximo de 72 caracteres na primeira linha
- Commits pequenos e focados — um commit por mudança lógica
- Não commite arquivos gerados (`__pycache__`, `node_modules`, `dist`, `.env`)

---

## 8. Abrindo uma Issue

Toda tarefa — feature, bug ou melhoria — deve ter uma issue **antes** de qualquer código ser escrito.

### Bug Report

Use o template `.github/ISSUE_TEMPLATE/bug.md`. Inclua obrigatoriamente:
- Passos para reproduzir
- Comportamento esperado vs. atual
- Qual camada é afetada (Frontend / Backend / Docker)
- Evidências (screenshot, log de erro)

### Feature Request

Use o template `.github/ISSUE_TEMPLATE/feature.md`. Inclua:
- Contexto e motivação
- Descrição do que deve ser feito
- Critérios de aceite (checklist)
- Qual stack é afetado (Angular / FastAPI / Banco / Docker)
- Estimativa de tamanho (S / M / L / XL)

> Atribua a issue a si mesmo quando começar a trabalhar nela para evitar trabalho duplicado.

---

## 9. Implementando uma Feature ou Bugfix

### Passo a passo

**1. Sincronize seu fork com o upstream**
```bash
git fetch upstream
git checkout develop
git merge upstream/develop
git push origin develop  # atualiza seu fork remoto
```

**2. Crie sua branch a partir da develop**
```bash
git checkout -b feature/nome-da-feature
```

**3. Implemente as mudanças**

Siga a arquitetura existente do projeto:

- **Backend (FastAPI):** lógica de negócio em `backend/app/services/`, endpoints em `backend/app/api/v1/`, schemas Pydantic em `backend/app/schemas/`, models SQLAlchemy em `backend/app/models/`.
- **Frontend (Angular):** páginas (smart components) em `frontend/src/app/features/`, componentes reutilizáveis em `frontend/src/app/shared/`, serviços HTTP em `frontend/src/app/core/services/`.
- **Banco de dados:** alterações no schema exigem uma migration Alembic. Nunca edite `database-schema.sql` diretamente.

**4. Crie a migration se alterou o banco**
```bash
cd backend
alembic revision --autogenerate -m "descricao_da_mudanca"
# Revise o arquivo gerado em alembic/versions/ antes de commitar
```

**5. Escreva e execute os testes**

Toda nova feature **obrigatoriamente** deve vir acompanhada de testes cobrindo o comportamento implementado. PRs sem testes para a nova funcionalidade serão recusados no review. Veja a seção [Testes](#11-testes) para detalhes.

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

Todos os testes existentes devem continuar passando.

**6. Faça commits incrementais**
```bash
git add .
git commit -m "feat(modulo): descrição da mudança"
```

**7. Sincronize com o upstream antes de abrir o PR**
```bash
git fetch upstream
git rebase upstream/develop
# Resolva conflitos se houver
git push origin feature/nome-da-feature
```

---

## 10. Padrões de Código

### Backend (Python / FastAPI)

- Use type hints em todas as funções
- Schemas Pydantic para validação de entrada e saída — nunca retorne o model SQLAlchemy diretamente
- Proteja endpoints com `@verify_cargo(...)` conforme o nível de acesso:
  - Cargo 1 = Diretor (acesso total)
  - Cargo 2 = Professor (acesso restrito às suas turmas)
  - Cargo 3 = Admin (acesso acadêmico e logístico)
- Erros de negócio devem lançar `HTTPException` com status code adequado
- Lógica de negócio fica nos services — nunca nos routers

### Frontend (Angular / TypeScript)

- Todos os componentes devem ser `standalone: true`
- Use `Signals` para estado reativo quando possível
- Rotas novas devem usar `loadComponent` ou `loadChildren` (lazy loading)
- Proteja rotas com os guards existentes: `authGuard`, `roleGuard([cargos])`, `adminGuard`
- Chamadas HTTP ficam nos services em `core/services/` — nunca no componente diretamente
- Siga o `.prettierrc` existente para formatação

### Geral

- Não commite credenciais, tokens ou chaves no código
- Não commite arquivos `.env`
- Remova `console.log` e `print()` de debug antes de abrir o PR

---

## 11. Testes

O projeto possui **107 testes automatizados** no backend (pytest) e testes unitários no frontend (Vitest + jsdom).

### Regra para novas features

**Toda nova feature deve incluir testes que cubram o comportamento implementado.** Isso é obrigatório e será verificado no code review. Não basta os testes existentes passarem — a funcionalidade nova precisa ter sua própria cobertura.

- **Backend:** adicione os testes no arquivo `backend/tests/test_<modulo>_service.py` correspondente ao service criado ou alterado. Se o módulo for novo, crie o arquivo seguindo o padrão dos existentes (ex: `test_aluno_service.py`).
- **Frontend:** adicione testes unitários para o service ou componente criado, cobrindo os casos de sucesso e os principais casos de erro.

Exemplos do que testar em uma nova feature:
- Caminho feliz (comportamento esperado com dados válidos)
- Validações de entrada (dados inválidos, campos obrigatórios ausentes)
- Regras de negócio (ex: matrícula em turma lotada, pedido com status inválido)
- Permissões (ex: professor não pode acessar endpoint exclusivo do diretor)

### Rodando os testes

**Backend:**
```bash
cd backend
source venv/bin/activate
pytest                                      # todos os testes
pytest -v                                   # verbose
pytest tests/test_aluno_service.py          # arquivo específico
```

**Frontend:**
```bash
cd frontend
npm test
npm test -- --reporter=verbose
```

### Critério mínimo para o PR

- Todos os 107 testes existentes devem passar
- Testes novos cobrindo a feature implementada devem estar presentes
- Nenhum PR será aprovado sem atender esses dois critérios

---

## 12. Abrindo um Pull Request

Quando sua branch estiver pronta:

1. Acesse https://github.com/IncludeLuisFerreira/Sistema-ABACO
2. Clique em **New pull request**
3. Configure: **base:** `develop` ← **compare:** `SEU-USUARIO:sua-branch`
4. Preencha o template de PR (`.github/pull_request_template.md`):
   - **O que muda?** — resumo de 1-2 frases
   - **Por quê?** — contexto e link para a issue (`Closes #N`)
   - **Como testar?** — passos para o reviewer reproduzir
   - **Screenshots** — obrigatório para mudanças de UI
   - **Checklist** — marque todos os itens antes de pedir review
5. Atribua pelo menos **1 reviewer** que não seja você
6. Adicione as labels adequadas (`feature`, `bug`, `docs`, etc.)

> PRs sem issue vinculada, sem testes passando, sem testes para a nova feature ou com o template incompleto serão fechados sem review.

---

## 13. Processo de Code Review

### Para quem abre o PR

- Responda os comentários do reviewer com clareza
- Faça as correções solicitadas em novos commits (não force-push durante o review)
- Após aprovação, o autor do PR realiza o merge

### Para quem revisa

- Revise em até **48 horas** após ser atribuído
- Verifique: lógica, segurança, padrões de código, testes e performance
- Seja construtivo — aponte o problema e sugira a solução
- Use **"Request changes"** para bloqueios e **"Comment"** para sugestões não-bloqueantes
- **Você não pode aprovar o próprio PR**

### Checklist de aprovação

- [ ] Código segue os padrões do projeto
- [ ] Testes existentes passando (backend e frontend)
- [ ] Testes novos cobrindo a feature ou bugfix implementado
- [ ] Nenhuma credencial ou dado sensível exposto
- [ ] Lógica de negócio nos services (backend) e nos services HTTP (frontend)
- [ ] Rotas protegidas com guards e `@verify_cargo` corretos
- [ ] Migrations Alembic incluídas se o schema foi alterado
- [ ] PR description preenchida com link para a issue

---

## Credenciais de Teste (Seed Automático)

Para testar localmente após o rebuild:

| Perfil | Email | Senha |
|--------|-------|-------|
| Diretor(a) | `admin@abaco.org.br` | `admin123` |
| Administrador(a) | `admin2@abaco.org.br` | `admin123` |
| Professor(a) | `maria@abaco.org.br` | `prof12345` |

---

Dúvidas? Abra uma issue com a label `question` ou fale com o responsável pelo repositório.
