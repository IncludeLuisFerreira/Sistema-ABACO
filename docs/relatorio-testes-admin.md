# Relatório de Testes Automatizados - Regras de Autorização Admin

**Data:** 27/09/2026
**Papel:** QA Senior Specialist
**Escopo:** Mapeamento, automação e validação de cobertura das regras de autorização administrativa no Backend (FastAPI / pytest) e Frontend (Angular / Vitest).

---

## 1. Lista de Testes Criados e Executados

### Backend (FastAPI / pytest)

| Nome do Teste | Tipo | Endpoint / Módulo Coberto | Resultado |
|---|---|---|---|
| `test_verify_cargo_success_for_allowed_cargo` | Unitário | `app.core.dependencies.verify_cargo` | Passando |
| `test_verify_cargo_forbidden_for_disallowed_cargo` | Unitário | `app.core.dependencies.verify_cargo` | Passando |
| `test_verify_cargo_unauthorized_when_no_token` | Unitário | `app.core.dependencies.verify_cargo` | Passando |
| `test_verify_cargo_unauthorized_when_expired_token` | Unitário | `app.core.dependencies.verify_cargo` | Passando |
| `test_verify_cargo_unauthorized_when_invalid_token` | Unitário | `app.core.dependencies.verify_cargo` | Passando |
| `test_verify_director_role_success` | Unitário | `app.core.dependencies.verify_director_role` | Passando |
| `test_verify_director_role_forbidden_for_professor` | Unitário | `app.core.dependencies.verify_director_role` | Passando |
| `test_read_usuarios_admin_allowed` | Integração | `GET /api/v1/usuarios` | Passando |
| `test_read_usuarios_common_user_forbidden` | Integração | `GET /api/v1/usuarios` | Passando |
| `test_read_usuarios_anonymous_unauthorized` | Integração | `GET /api/v1/usuarios` | Passando |
| `test_read_usuarios_expired_token_unauthorized` | Integração | `GET /api/v1/usuarios` | Passando |
| `test_read_usuarios_invalid_token_unauthorized` | Integração | `GET /api/v1/usuarios` | Passando |
| `test_read_usuario_by_id_common_user_forbidden` | Integração | `GET /api/v1/usuarios/{id}` | Passando |
| `test_create_usuario_common_user_forbidden` | Integração | `POST /api/v1/usuarios` | Passando |
| `test_update_usuario_common_user_forbidden` | Integração | `PUT /api/v1/usuarios/{id}` | Passando |
| `test_delete_usuario_common_user_forbidden` | Integração | `DELETE /api/v1/usuarios/{id}` | Passando |
| `test_dashboard_kpis_admin_allowed` | Integração | `GET /api/v1/dashboard/kpis` | Passando |
| `test_dashboard_kpis_common_user_forbidden` | Integração | `GET /api/v1/dashboard/kpis` | Passando |
| `test_dashboard_kpis_anonymous_unauthorized` | Integração | `GET /api/v1/dashboard/kpis` | Passando |
| `test_dashboard_charts_academico_common_user_forbidden` | Integração | `GET /api/v1/dashboard/charts/academico` | Passando |
| `test_dashboard_charts_logistica_common_user_forbidden` | Integração | `GET /api/v1/dashboard/charts/logistica` | Passando |
| `test_aprovar_pedido_common_user_forbidden` | Integração | `PUT /api/v1/pedidos/{id}/aprovar` | Passando |
| `test_comprar_pedido_common_user_forbidden` | Integração | `PUT /api/v1/pedidos/{id}/comprar` | Passando |
| `test_update_pedido_common_user_forbidden` | Integração | `PUT /api/v1/pedidos/{id}` | Passando |
| `test_entregar_pedido_common_user_forbidden` | Integração | `PUT /api/v1/pedidos/{id}/entregar` | Passando |
| `test_aprovar_pedido_admin_allowed` | Integração | `PUT /api/v1/pedidos/{id}/aprovar` | Passando |
| `test_create_aluno_professor_forbidden` | Integração | `POST /api/v1/alunos` | Passando |
| `test_create_curso_professor_forbidden` | Integração | `POST /api/v1/cursos` | Passando |
| `test_create_turma_professor_forbidden` | Integração | `POST /api/v1/turmas` | Passando |
| `test_create_matricula_professor_forbidden` | Integração | `POST /api/v1/matriculas` | Passando |
| `test_create_estoque_professor_forbidden` | Integração | `POST /api/v1/estoque` | Passando |

---

### Frontend (Angular / Vitest)

| Nome do Teste | Tipo | Rota / Guard / Serviço Coberto | Resultado |
|---|---|---|---|
| `allows access when user cargo is in allowedCargos` | Unitário | `roleGuard` | Passando |
| `redirects to /acesso-negado when user cargo is not in allowedCargos` | Unitário | `roleGuard` | Passando |
| `redirects to /login when no token is present` | Unitário | `roleGuard` | Passando |
| `redirects to /login and clears token when token is expired` | Unitário | `roleGuard` | Passando |
| `allows access for Director (cargo 1)` | Unitário | `directorGuard` | Passando |
| `redirects Admin (cargo 3) to /acesso-negado because directorGuard strictly requires cargo 1` | Unitário | `directorGuard` | Passando |
| `redirects Professor (cargo 2) to /acesso-negado` | Unitário | `directorGuard` | Passando |
| `redirects when no token is present to /login` | Unitário | `directorGuard` | Passando |
| `allows access for Director (cargo 1)` | Unitário | `adminGuard` | Passando |
| `allows access for Admin (cargo 3)` | Unitário | `adminGuard` | Passando |
| `redirects Professor (cargo 2) to /acesso-negado` | Unitário | `adminGuard` | Passando |
| `redirects unauthenticated user to /login` | Unitário | `adminGuard` | Passando |
| `allows access for valid authenticated user` | Unitário | `authGuard` | Passando |
| `redirects to /login when no token exists` | Unitário | `authGuard` | Passando |
| `redirects to /login and clears token when token is expired` | Unitário | `authGuard` | Passando |
| `mapCargoToRole maps cargo 1 to DIRECTOR, 2 to TEACHER, 3 to ADMIN` | Unitário | `AuthService.mapCargoToRole` | Passando |
| `mapCargoToRole defaults to ADMIN for unknown cargo (fail-open security risk finding)` | Unitário | `AuthService.mapCargoToRole` | Passando |
| `decodePayload correctly decodes base64 JWT payload` | Unitário | `AuthService.decodePayload` | Passando |
| `decodePayload returns empty object for malformed token` | Unitário | `AuthService.decodePayload` | Passando |
| `isTokenExpired checks token exp claim against current time` | Unitário | `AuthService.isTokenExpired` | Passando |
| `getStoredToken and clearStoredToken interact with localStorage` | Unitário | `AuthService.getStoredToken` | Passando |
| `login stores token and updates authState signal` | Unitário | `AuthService.login` | Passando |
| `logout clears state and token in localStorage` | Unitário | `AuthService.logout` | Passando |
| `isAuthenticated returns true for valid unexpired token and false when empty/expired` | Unitário | `AuthService.isAuthenticated` | Passando |
| `root admin route contains authGuard` | Unitário | Configuração de `ADMIN_ROUTES` | Passando |
| `route "usuarios" requires directorGuard (cargo 1)` | Unitário | Configuração de `ADMIN_ROUTES` | Passando |
| `route "dashboard" requires directorGuard (cargo 1)` | Unitário | Configuração de `ADMIN_ROUTES` | Passando |
| `routes "alunos", "cursos", "turmas", "matriculas", "logistico" require adminGuard` | Unitário | Configuração de `ADMIN_ROUTES` | Passando |

---

## 2. Cobertura de Código Alcançada vs. Meta (>= 70%)

### Módulos do Backend (FastAPI)

| Módulo | Linhas Cobertas (%) | Status vs Meta (70%) |
|---|---|---|
| `app.core.dependencies` | **94%** | Superada |
| `app.core.security` | **89%** | Superada |
| `app.core.config` | **100%** | Superada |
| `app.core.limiter` | **100%** | Superada |
| `app.api.v1.dashboard` | **88%** | Superada |
| **Média Módulos Core Autorização Backend** | **94.5%** | **Superada** |

### Módulos do Frontend (Angular)

| Módulo / Arquivo | Linhas Cobertas (%) | Status vs Meta (70%) |
|---|---|---|
| `src/app/core/guards/auth.guard.ts` | **100%** | Superada |
| `src/app/core/guards/role.guard.ts` | **100%** | Superada |
| `src/app/core/services/auth.service.ts` | **71.6%** | Superada |
| **Média Módulos Guards & Auth Frontend** | **90.5%** | **Superada** |

---

## 3. Achados de Segurança e Gaps Detectados durante os Testes

Durante a criação da suíte de testes de autorização, foram identificadas as seguintes vulnerabilidades e inconformidades no código de produção:

1. **Comportamento Fail-Open em `mapCargoToRole` (Frontend - `auth.service.ts`):**
   Se o payload do token JWT contiver um cargo `null` ou um valor numérico não mapeado (ex.: cargo 99), a função `mapCargoToRole` retorna `'ADMIN'` como padrão em vez de negar o acesso.
2. **Inconsistência de Cabeçalho de Autenticação (Backend - `dependencies.py`):**
   A função `_extract_token` lança HTTP 401 sem o cabeçalho `WWW-Authenticate: Bearer` quando a requisição não contém o header `Authorization`.
3. **Autenticação sem Validação de Estado do Usuário no Banco (Backend - `dependencies.py`):**
   A dependência `get_current_user` valida apenas a assinatura e expiração do JWT, sem verificar se o usuário foi desativado ou removido do banco de dados.
4. **Ausência de Mecanismo de Revogação de Token / Blacklist (Backend - `security.py`):**
   Os tokens JWT emitidos não possuem o claim `jti` (JWT ID), impedindo que tokens sejam revogados antes de sua expiração natural.

---

## 4. Resumo Final

- **Suíte de Testes do Backend:** 31 novos testes de autorização implementados e executados via pytest, cobrindo dependências e endpoints restritos.
- **Suíte de Testes do Frontend:** 28 testes de guards, serviços e rotas configurados e executados via Vitest, validando `roleGuard`, `directorGuard`, `adminGuard` e `authGuard`.
- **Meta de Cobertura Superada:** Atingida cobertura de **94.5%** no core de autorização do Backend e **90.5%** nos guards/auth do Frontend (meta de 70%).
- **Isolamento de Testes:** Fixtures fake JWT e override do banco para SQLite em memória garantem execução sem dependência do ambiente externo ou banco real.
- **Integridade do Código Mantida:** Nenhuma alteração foi realizada no código de produção da aplicação, e todos os achados de segurança foram documentados.
