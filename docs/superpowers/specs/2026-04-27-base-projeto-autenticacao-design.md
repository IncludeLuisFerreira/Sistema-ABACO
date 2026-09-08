# Base do projeto + autenticação

## Problema

O PRD descreve um sistema acadêmico e administrativo maior, mas a primeira entrega precisa começar por uma base pequena e validável: ambiente local padronizado, estrutura monorepo e autenticação JWT com controle por papel.

## Objetivo desta spec

Entregar o esqueleto do projeto e o fluxo mínimo de acesso:

- `backend` em Node.js + Express + TypeScript
- `frontend` em Next.js + TypeScript + TailwindCSS
- PostgreSQL via Docker
- login JWT
- proteção de rotas por papel
- interface inicial de login

Usuários serão cadastrados manualmente no banco nesta fase.

## Escopo

### Dentro do escopo

- Estrutura monorepo com `backend/` e `frontend/`
- `docker-compose.yml` com banco, backend e frontend
- backend com camadas separadas: routes, controllers, services, repositories, middlewares
- frontend com página de login e área protegida simples
- autenticação com JWT
- autorização por papel
- papéis: `diretora`, `administrativo`, `professor`
- uso do esquema inicial do banco já documentado no projeto, com a tabela de usuários como fonte de verdade para autenticação

### Fora do escopo

- CRUD de usuários
- CRUD de alunos, cursos, turmas e matrículas
- dashboards completos
- recuperação de senha
- cadastro público de conta
- refresh token

## Abordagens avaliadas

### 1. Base vertical mínima

Implementar Docker, backend, frontend e login protegido antes de qualquer módulo acadêmico.

**Vantagem:** valida arquitetura, autenticação e integração cedo.  
**Desvantagem:** ainda não entrega processos acadêmicos.

### 2. Backend primeiro

Criar toda a API de autenticação e deixar o frontend para depois.

**Vantagem:** menos fricção inicial.  
**Desvantagem:** atrasa validação da experiência real de uso.

### 3. Infraestrutura primeiro

Focar apenas em Docker, banco e estrutura de pastas.

**Vantagem:** estabiliza ambiente.  
**Desvantagem:** pouco valor funcional.

**Decisão:** abordagem 1.

## Design

### Backend

O backend expõe uma API REST em `/api`. A primeira funcionalidade será `POST /api/auth/login`, que recebe `email` e `senha`, valida o usuário na tabela de usuários e devolve um JWT contendo `id`, `nome` e `cargo`.

O middleware de autenticação valida o token e anexa o usuário autenticado à requisição. O middleware de autorização valida se o cargo do usuário é permitido para a rota.

### Frontend

O frontend terá uma página de login em português com campos de e-mail e senha. Após login bem-sucedido, o token será armazenado de forma compatível com a arquitetura escolhida e o usuário será redirecionado para uma área protegida simples.

### Banco de dados

A autenticação usará a tabela de usuários existente no esquema do projeto. Nesta fase, o banco não terá CRUD administrativo de usuários; os registros serão inseridos manualmente para permitir validação do fluxo.

O campo `cargo` será tratado como código de papel no banco e mapeado no backend para os papéis de produto:

- `0` = `diretora`
- `1` = `administrativo`
- `2` = `professor`

As senhas cadastradas manualmente devem ser gravadas como hash compatível com bcrypt.

### Docker

O `docker-compose.yml` deve subir:

- PostgreSQL
- backend
- frontend

O sistema deve subir com um único comando e apontar o backend para o banco pelo nome do serviço do compose.

## Fluxo principal

1. O usuário acessa a tela de login.
2. O frontend envia `email` e `senha` para o backend.
3. O backend valida o usuário e a senha.
4. O backend emite JWT.
5. O frontend usa o token para acessar a área protegida.
6. Rotas protegidas usam middleware de autenticação e autorização.

## Regras

- Senhas nunca são retornadas pela API.
- Tokens e credenciais são validados antes de qualquer regra de negócio.
- Controllers não acessam banco diretamente.
- Services não dependem de `req`/`res`.
- Queries SQL devem ser parametrizadas.

## Estratégia de testes

### Backend

- autenticação com credenciais válidas
- rejeição de credenciais inválidas
- middleware bloqueando acesso sem token
- middleware bloqueando acesso com papel não autorizado

### Frontend

- login exibe erro quando a autenticação falha
- login redireciona após sucesso
- rota protegida não renderiza para usuário desautenticado

### Integração

- login ponta a ponta com banco real via Docker

## Critérios de pronto

- ambiente sobe com Docker
- login funciona com usuário manualmente cadastrado
- rota protegida exige JWT
- autorização por papel funciona
- a base está pronta para iniciar o módulo acadêmico com TDD
