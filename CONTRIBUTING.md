# Guia de Contribuição — SGA ABACO

Bem-vindo ao guia de contribuição do **SGA ABACO**. Este documento define o processo obrigatório para todos os membros da equipe ao implementar features, corrigir bugs ou realizar qualquer alteração no repositório.

Leia com atenção antes de abrir sua primeira issue ou Pull Request.

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Configuração do Ambiente](#2-configuração-do-ambiente)
3. [Modelo de Branches](#3-modelo-de-branches)
4. [Fluxo de Trabalho Completo](#4-fluxo-de-trabalho-completo)
5. [Convenção de Branches](#5-convenção-de-branches)
6. [Convenção de Commits](#6-convenção-de-commits)
7. [Abrindo uma Issue](#7-abrindo-uma-issue)
8. [Implementando uma Feature ou Bugfix](#8-implementando-uma-feature-ou-bugfix)
9. [Padrões de Código](#9-padrões-de-código)
10. [Testes](#10-testes)
11. [Abrindo um Pull Request](#11-abrindo-um-pull-request)
12. [Processo de Code Review](#12-processo-de-code-review)

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

Nenhum membro tem permissão de push direto no repositório principal. Todo trabalho começa com um **fork**:

1. Acesse https://github.com/IncludeLuisFerreira/Sistema-ABACO
2. Clique em **Fork** (canto superior direito) para criar uma cópia na sua conta
3. Clone o seu fork localmente:

```bash
git clone https://github.com/SEU-USUARIO/Sistema-ABACO.git
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
main        ← versões estáveis e testadas (releases)
  └── develop   ← integração contínua, sempre a versão mais recente
        └── feature/nome    ← seu trabalho acontece aqui (no seu fork)
        └── fix/nome
        └── docs/nome
```

### Regras das branches protegidas

| Branch | Propósito | Push direto | Merge via PR | Aprovações mínimas |
|--------|-----------|-------------|--------------|-------------------|
| `main` | Versões estáveis | ❌ Proibido | ✅ Obrigatório | 1 (não pode ser o autor) |
| `develop` | Versão mais recente | ❌ Proibido | ✅ Obrigatório | 1 (não pode ser o autor) |

- **`develop`** é a base para todo desenvolvimento. Toda branch de feature/fix deve ser criada a partir dela.
- **`main`** recebe merges apenas da `develop`, quando a versão estiver estável e testada.
- Nenhum membro pode aprovar o próprio Pull Request.

---

## 4. Fluxo de Trabalho Completo

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

## 5. Convenção de Branches

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

## 6. Convenção de Commits

Siga o padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/):

```
<tipo>(<escopo opcional>): <descrição curta no imperativo>
```

**Tipos aceitos:**

| Tipo | Descrição |
|------|-----------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
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

## 7. Abrindo uma Issue

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

## 8. Implementando uma Feature ou Bugfix

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

Toda nova feature **obrigatoriamente** deve vir acompanhada de testes cobrindo o comportamento implementado. PRs sem testes para a nova funcionalidade serão recusados no review. Veja a seção [Testes](#10-testes) para detalhes.

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

## 9. Padrões de Código

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
- Proteja rotas com os guards existentes: `authGuard`, `roleGuard([cargos])`, `directorGuard`, `adminGuard`
- Chamadas HTTP ficam nos services em `core/services/` — nunca no componente diretamente
- Siga o `.prettierrc` existente para formatação

### Geral

- Não commite credenciais, tokens ou chaves no código
- Não commite arquivos `.env`
- Remova `console.log` e `print()` de debug antes de abrir o PR

---

## 10. Testes

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

## 11. Abrindo um Pull Request

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

## 12. Processo de Code Review

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
