# Auditoria de Rotas e Permissões do Perfil Administrador

> **Nota de contexto (baseline).** Este documento é o **baseline da auditoria realizada ANTES das correções da PR #10** (RBAC admin, branch `7-sprint-1-rbac-isolar-permissões-e-acesso-exclusivo-às-tarefas-de-administrador`). Várias afirmações factuais abaixo descrevem o estado do código naquele momento e **não refletem o estado atual** já corrigido. Em especial: `dashboard.py` e `usuarios.py` passaram a usar `verify_cargo(1, 3)`; a rota frontend `/admin/usuarios` passou a usar `adminGuard`; o guard `directorGuard` foi removido; e a guarda anti-escalação em usuários foi implementada. As tabelas de rotas/guards, a matriz de negação e a seção de recomendações foram anotadas onde o código atual diverge. Ver PR #10 e `docs/superpowers/plans/2026-09-29-pr10-review-fixes.md`.

## Sumário Executivo

Esta auditoria traz uma análise minuciosa de segurança do módulo de autorização e controle de acesso no Sistema de Gestão Acadêmica da Associação ABACO, abrangendo o backend em **FastAPI** e o frontend em **Angular**.

O objetivo primário da análise é avaliar o cumprimento do requisito de **exclusividade do perfil Administrador** em acessar tarefas de gestão do sistema, garantindo a segregação de funções e prevenindo privilege escalation ou bypasses de autorização.

**Principais Descobertas:**
1. **Confusão e Ambiguidade de Papéis entre Cargo 1 (Diretor/Diretoria) e Cargo 3 (Admin):** O sistema utiliza o enum/inteiro `cargo` (1 = Diretoria/Diretor, 2 = Professor, 3 = Admin). Na época desta auditoria, diversos endpoints de gestão administrativa (gestão de usuários `/api/v1/usuarios` e dashboards `/api/v1/dashboard`) exigiam exclusivamente `cargo = 1` (`verify_cargo(1)`), bloqueando o Administrador (`cargo = 3`). A rota `/admin/usuarios` no frontend usava `directorGuard`, exigindo Cargo 1. **Estado atual (pós-PR #10):** `dashboard.py` e `usuarios.py` usam `verify_cargo(1, 3)`, `/admin/usuarios` usa `adminGuard` e o guard `directorGuard` foi removido, de modo que o Admin já acessa gestão de usuários e indicadores, respeitando a guarda anti-escalação de cargo.
2. **Falha de Mapeamento Fail-Open no Frontend (`auth.service.ts:68`):** A função `mapCargoToRole()` possui um fallback inseguro no qual qualquer cargo não reconhecido (ou `null`) retorna o perfil `'ADMIN'`. Se um usuário sem cargo definido autenticar, o frontend concede permissões de Administrador nas verificações locais.
3. **Inconsistência de Regra de Negócio nos Pedidos de Material:** No backend, as ações de aprovação, compra e alteração de pedidos de material (`PUT /api/v1/pedidos/{id}/aprovar`, `/comprar`, etc.) exigem unicamente Cargo 1, enquanto a exclusão permite Cargo 1 e Cargo 3.
4. **Endpoint com Autorização Fraca no Backend (`GET /api/v1/matriculas/me`):** Este endpoint utiliza apenas `Depends(get_current_user)` sem validação de cargo no decorator. Embora haja uma filtragem interna para `cargo == 2`, qualquer usuário autenticado (incluindo Cargo 3) consegue chamá-lo sem passar pela dependência `verify_cargo`.
5. **Déficit Severo na Cobertura de Testes de Autorização:** A cobertura geral do backend é de ~70%, contudo, os testes existentes em `backend/tests/test_api_endpoints.py` validam a negação de acesso (403) para apenas 2 rotas (`/dashboard` e `/usuarios`), deixando sem testes de negação 100% dos endpoints de alunos, cursos, turmas, matrículas, estoque, pedidos, notas e presenças. No frontend, os testes de guards limitam-se a stubs básicos sem cobrir o roteamento real.

---

## Metodologia

A análise foi realizada através de inspeção estática de código, auditoria de dependências de autorização e execução da suíte de testes automatizados com medição de cobertura.

**Arquivos e Padrões Inspecionados:**
* **Backend (FastAPI):**
  * Configuração e dependências de segurança: `backend/app/core/dependencies.py` (`verify_cargo`, `get_current_user`, `decode_access_token`) e `backend/app/core/security.py`.
  * Routers de API (v1): `backend/app/api/v1/` (`alunos.py`, `auth.py`, `cursos.py`, `dashboard.py`, `estoque.py`, `historico.py`, `matriculas.py`, `notas.py`, `pedidos.py`, `presencas.py`, `turmas.py`, `usuarios.py`).
  * Modelos de dados e schemas: `backend/app/models/usuario.py` e `backend/app/schemas/usuario_schema.py`.
* **Frontend (Angular):**
  * Configuração de rotas: `frontend/src/app/app.routes.ts`, `frontend/src/app/features/admin/admin.routes.ts`, `frontend/src/app/features/academico/academico.routes.ts`.
  * Guards de rotas: `frontend/src/app/core/guards/auth.guard.ts`, `frontend/src/app/core/guards/role.guard.ts` (no baseline: `adminGuard`, `directorGuard`, `roleGuard`; `directorGuard` foi removido na PR #10).
  * Serviços de autenticação e sessão: `frontend/src/app/core/services/auth.service.ts` (`mapCargoToRole`, `decodePayload`, `getRoleFromToken`).
* **Suíte de Testes:**
  * Testes backend em `backend/tests/` executados com `pytest --cov=backend/app`.
  * Testes frontend spec em `frontend/src/app/**/*.spec.ts`.

---

## Mapa de Endpoints Administrativos (Backend)

| Método HTTP | Path | Dependência de Auth | Role Exigida (Cargo) | Valida 403? | Arquivo:linha |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Nenhuma (Público) | N/A | Não | `backend/app/api/v1/auth.py:33` |
| `POST` | `/api/v1/auth/forgot-password` | Nenhuma (Público) | N/A | Não | `backend/app/api/v1/auth.py:51` |
| `POST` | `/api/v1/auth/reset-password` | Nenhuma (Público) | N/A | Não | `backend/app/api/v1/auth.py:70` |
| `GET` | `/api/v1/alunos` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/alunos.py:23` |
| `GET` | `/api/v1/alunos/{aluno_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/alunos.py:28` |
| `POST` | `/api/v1/alunos` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/alunos.py:37` |
| `PUT` | `/api/v1/alunos/{aluno_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/alunos.py:43` |
| `DELETE` | `/api/v1/alunos/{aluno_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/alunos.py:54` |
| `GET` | `/api/v1/cursos` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/cursos.py:21` |
| `GET` | `/api/v1/cursos/{curso_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/cursos.py:26` |
| `POST` | `/api/v1/cursos` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/cursos.py:35` |
| `PUT` | `/api/v1/cursos/{curso_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/cursos.py:41` |
| `DELETE` | `/api/v1/cursos/{curso_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/cursos.py:52` |
| `GET` | `/api/v1/dashboard/kpis` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/dashboard.py:21` |
| `GET` | `/api/v1/dashboard/charts/academico` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/dashboard.py:29` |
| `GET` | `/api/v1/dashboard/charts/logistica` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/dashboard.py:37` |
| `GET` | `/api/v1/estoque` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/estoque.py:31` |
| `GET` | `/api/v1/estoque/search` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/estoque.py:36` |
| `GET` | `/api/v1/estoque/alertas` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/estoque.py:41` |
| `GET` | `/api/v1/estoque/{estoque_id}` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/estoque.py:46` |
| `POST` | `/api/v1/estoque` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/estoque.py:55` |
| `PUT` | `/api/v1/estoque/{estoque_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/estoque.py:61` |
| `DELETE` | `/api/v1/estoque/{estoque_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/estoque.py:72` |
| `PUT` | `/api/v1/estoque/{estoque_id}/baixa` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/estoque.py:84` |
| `GET` | `/api/v1/historico/matricula/{matricula_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/historico.py:16` |
| `GET` | `/api/v1/matriculas` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/matriculas.py:26` |
| `GET` | `/api/v1/matriculas/me` | `Depends(get_current_user)` | Qualquer Usuário Autenticado | Não | `backend/app/api/v1/matriculas.py:31` |
| `GET` | `/api/v1/matriculas/{matricula_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/matriculas.py:41` |
| `POST` | `/api/v1/matriculas` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/matriculas.py:50` |
| `PUT` | `/api/v1/matriculas/{matricula_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/matriculas.py:65` |
| `DELETE` | `/api/v1/matriculas/{matricula_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/matriculas.py:80` |
| `POST` | `/api/v1/notas` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/notas.py:21` |
| `GET` | `/api/v1/notas/matricula/{matricula_id}` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/notas.py:38` |
| `GET` | `/api/v1/notas/turma/{turma_id}` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/notas.py:49` |
| `GET` | `/api/v1/notas/media/turma/{turma_id}` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/notas.py:59` |
| `GET` | `/api/v1/pedidos` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/pedidos.py:27` |
| `GET` | `/api/v1/pedidos/{pedido_id}` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/pedidos.py:32` |
| `POST` | `/api/v1/pedidos` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/pedidos.py:41` |
| `PUT` | `/api/v1/pedidos/{pedido_id}/aprovar` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/pedidos.py:51` |
| `PUT` | `/api/v1/pedidos/{pedido_id}/comprar` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/pedidos.py:64` |
| `PUT` | `/api/v1/pedidos/{pedido_id}` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/pedidos.py:77` |
| `PUT` | `/api/v1/pedidos/{pedido_id}/entregar` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/pedidos.py:90` |
| `DELETE` | `/api/v1/pedidos/{pedido_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/pedidos.py:103` |
| `POST` | `/api/v1/presencas` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/presencas.py:17` |
| `GET` | `/api/v1/presencas/turma/{turma_id}` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/presencas.py:28` |
| `GET` | `/api/v1/turmas` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/turmas.py:24` |
| `GET` | `/api/v1/turmas/me` | `Depends(verify_cargo(1, 2))` | Diretoria (1), Prof (2) | Sim (403) | `backend/app/api/v1/turmas.py:29` |
| `GET` | `/api/v1/turmas/{turma_id}` | `Depends(verify_cargo(1, 2, 3))` | Diretoria (1), Prof (2), Admin (3) | Sim (403) | `backend/app/api/v1/turmas.py:35` |
| `POST` | `/api/v1/turmas` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/turmas.py:44` |
| `PUT` | `/api/v1/turmas/{turma_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/turmas.py:55` |
| `DELETE` | `/api/v1/turmas/{turma_id}` | `Depends(verify_cargo(1, 3))` | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/turmas.py:70` |
| `GET` | `/api/v1/usuarios` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/usuarios.py:51` |
| `GET` | `/api/v1/usuarios/{usuario_id}` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/usuarios.py:56` |
| `POST` | `/api/v1/usuarios` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/usuarios.py:65` |
| `PUT` | `/api/v1/usuarios/{usuario_id}` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/usuarios.py:75` |
| `DELETE` | `/api/v1/usuarios/{usuario_id}` | `Depends(verify_cargo(1, 3))` *(atual; baseline `verify_cargo(1)`)* | Diretoria (1), Admin (3) | Sim (403) | `backend/app/api/v1/usuarios.py:98` |

---

## Mapa de Rotas Administrativas (Frontend)

| Rota | Componente | Guard | Role Exigida | Lazy? | Arquivo:linha |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/login` | `Login` | Nenhum | Público | Sim | `frontend/src/app/app.routes.ts:6` |
| `/forgot-password` | `ForgotPassword` | Nenhum | Público | Sim | `frontend/src/app/app.routes.ts:10` |
| `/reset-password` | `ResetPassword` | Nenhum | Público | Sim | `frontend/src/app/app.routes.ts:14` |
| `/acesso-negado` | `AccessDenied` | Nenhum | Público | Sim | `frontend/src/app/app.routes.ts:18` |
| `/academico` | `AcademicoLayoutComponent` | `authGuard`, `roleGuard([2])` | TEACHER (Cargo 2) | Sim | `frontend/src/app/app.routes.ts:22` |
| `/admin` | `AdminLayoutComponent` | `authGuard` | Autenticado | Sim | `frontend/src/app/app.routes.ts:26` |
| `/admin/home` | `AdminHome` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:12` |
| `/admin/dashboard` | Redireciona para `/admin/home` | `adminGuard` *(atual; baseline `directorGuard`)* | DIRECTOR (1), ADMIN (3) | N/A | `frontend/src/app/features/admin/admin.routes.ts:18` |
| `/admin/usuarios` | `UsersManagementComponent` | `adminGuard` *(atual; baseline `directorGuard`)* | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:24` |
| `/admin/alunos` | `StudentsManagementComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:30` |
| `/admin/cursos` | `CoursesManagementComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:36` |
| `/admin/turmas` | `ClassesManagementComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:42` |
| `/admin/matriculas` | `EnrollmentsManagementComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:48` |
| `/admin/matriculas/:id/notas` | `StudentGradesComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:54` |
| `/admin/historico/matricula/:id` | `TranscriptViewComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:60` |
| `/admin/presencas` | `AttendanceManagementComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:66` |
| `/admin/notas` | `GradesManagementComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:72` |
| `/admin/notas/aluno/:id` | `StudentGradesComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:78` |
| `/admin/logistico` | `LogisticoHome` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:84` |
| `/admin/logistico/estoque` | `EstoqueManagementComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:90` |
| `/admin/logistico/pedidos` | `PedidoListComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:96` |
| `/admin/logistico/pedidos/novo` | `PedidoFormPageComponent` | `adminGuard` | DIRECTOR (1), ADMIN (3) | Sim | `frontend/src/app/features/admin/admin.routes.ts:102` |

---

## Matriz de Rastreabilidade

| Rota Frontend | Guard Frontend | Endpoints Backend Consumidos | Dependência Auth Backend | Inconsistências / Detalhes |
| :--- | :--- | :--- | :--- | :--- |
| `/admin/home` | `adminGuard` (1, 3) | `GET /api/v1/dashboard/kpis`, `GET /api/v1/dashboard/charts/academico`, `GET /api/v1/dashboard/charts/logistica` | `verify_cargo(1, 3)` *(atual; baseline `verify_cargo(1)`)* | Consistente (Cargo 1 e 3 possuem acesso). *(Baseline apontava inconsistência crítica.)* |
| `/admin/usuarios` | `adminGuard` (1, 3) *(atual; baseline `directorGuard`)* | `GET /api/v1/usuarios`, `POST /api/v1/usuarios`, `PUT /api/v1/usuarios/{id}`, `DELETE /api/v1/usuarios/{id}` | `verify_cargo(1, 3)` *(atual; baseline `verify_cargo(1)`)* | Consistente, com guarda anti-escalação: Admin não gerencia usuários de cargo 1 nem altera o próprio cargo. *(Baseline apontava inconsistência de requisito.)* |
| `/admin/alunos` | `adminGuard` (1, 3) | `GET /api/v1/alunos`, `POST /api/v1/alunos`, `PUT /api/v1/alunos/{id}`, `DELETE /api/v1/alunos/{id}` | `verify_cargo(1, 3)` | Consistente (Cargo 1 e 3 possuem acesso). |
| `/admin/cursos` | `adminGuard` (1, 3) | `GET /api/v1/cursos`, `POST /api/v1/cursos`, `PUT /api/v1/cursos/{id}`, `DELETE /api/v1/cursos/{id}` | `verify_cargo(1, 3)` | Consistente (Cargo 1 e 3 possuem acesso). |
| `/admin/turmas` | `adminGuard` (1, 3) | `GET /api/v1/turmas`, `POST /api/v1/turmas`, `PUT /api/v1/turmas/{id}`, `DELETE /api/v1/turmas/{id}`, `GET /api/v1/usuarios` | `verify_cargo(1, 2, 3)` (leitura), `verify_cargo(1, 3)` (CUD), `verify_cargo(1, 3)` (usuarios, atual) | Consistente. *(Baseline: `/usuarios` usava `verify_cargo(1)`, causando 403 ao Admin.)* |
| `/admin/matriculas` | `adminGuard` (1, 3) | `GET /api/v1/matriculas`, `POST /api/v1/matriculas`, `PUT /api/v1/matriculas/{id}`, `DELETE /api/v1/matriculas/{id}` | `verify_cargo(1, 2, 3)` (leitura), `verify_cargo(1, 3)` (CUD) | Consistente. |
| `/admin/presencas` | `adminGuard` (1, 3) | `GET /api/v1/presencas/turma/{id}`, `POST /api/v1/presencas` | `verify_cargo(1, 2, 3)` | Consistente. |
| `/admin/notas` | `adminGuard` (1, 3) | `GET /api/v1/notas/turma/{id}`, `POST /api/v1/notas`, `GET /api/v1/notas/media/turma/{id}` | `verify_cargo(1, 2, 3)` | Consistente. |
| `/admin/logistico/estoque` | `adminGuard` (1, 3) | `GET /api/v1/estoque`, `POST /api/v1/estoque`, `PUT /api/v1/estoque/{id}`, `DELETE /api/v1/estoque/{id}`, `PUT /api/v1/estoque/{id}/baixa` | `verify_cargo(1, 2, 3)` (leitura), `verify_cargo(1, 3)` (CUD/baixa) | Consistente. |
| `/admin/logistico/pedidos` | `adminGuard` (1, 3) | `GET /api/v1/pedidos`, `PUT /api/v1/pedidos/{id}/aprovar`, `comprar`, `entregar`, `DELETE /api/v1/pedidos/{id}` | `verify_cargo(1, 2, 3)` (GET), `verify_cargo(1, 3)` (aprovar/comprar/entregar/DELETE, atual) | Consistente (Cargo 1 e 3). *(Baseline: ciclo de vida usava `verify_cargo(1)`, causando 403 ao Admin.)* |

---

## Gaps de Segurança

1. **Fallback Fail-Open no Mapeamento de Papéis do Client (`frontend/src/app/core/services/auth.service.ts:68`)**
   * *Descrição:* Em `mapCargoToRole(cargo: number | null)`, caso `cargo` não seja 1, 2 ou 3, a função retorna `'ADMIN'`.
   * *Risco:* Alta. Usuários sem cargo definido ou com valores corrompidos recebem o perfil `'ADMIN'` no client, podendo visualizar menus e layouts administrativos.
   * *Estado atual:* **Resolvido na PR #10.** `mapCargoToRole` adota fail-closed e retorna `'GUEST'` para cargo desconhecido/nulo.

2. **Incompatibilidade do Dashboard para Administradores (`backend/app/api/v1/dashboard.py:21,29,37` vs `frontend/src/app/features/admin/admin.routes.ts:12`)**
   * *Descrição:* A rota `/admin/home` renderiza os gráficos do dashboard consumidos da API `/api/v1/dashboard/*`. No entanto, no backend, esses endpoints exigem `verify_cargo(1)` (Cargo 1 apenas).
   * *Risco:* Média/Alta. Quando um Admin (Cargo 3) acessa a tela inicial `/admin/home`, o Angular permite o acesso via `adminGuard`, mas todas as chamadas HTTP para os gráficos falham com HTTP 403.
   * *Estado atual:* **Resolvido na PR #10.** Endpoints usam `verify_cargo(1, 3)`.

3. **Bloqueio do Administrador na Gestão de Usuários (`backend/app/api/v1/usuarios.py:22,27,36,45,56` & `frontend/src/app/features/admin/admin.routes.ts:24`)**
   * *Descrição:* Os endpoints de CRUD de usuários exigem estritamente Cargo 1 (Diretoria). No frontend, a rota `/admin/usuarios` exige `directorGuard`.
   * *Risco:* Alta (Desconformidade com Critérios de Aceite). O Administrador (Cargo 3) não tem acesso às tarefas de gestão de usuários do sistema.
   * *Estado atual:* **Resolvido na PR #10.** Endpoints usam `verify_cargo(1, 3)` e `/admin/usuarios` usa `adminGuard`, com guarda anti-escalação de cargo.

4. **Dependência Quebrada em Turmas para o Perfil Admin (`frontend/src/app/features/classes/pages/classes-management/classes-management.ts:280`)**
   * *Descrição:* A tela de gestão de turmas (`/admin/turmas`) precisa carregar a lista de professores para preencher o select no formulário. Para isso, chama `UsuarioService.getUsuarios()`, que consome `GET /api/v1/usuarios`. Como `/usuarios` exige Cargo 1, o Admin (Cargo 3) recebe HTTP 403 ao abrir a tela de turmas, impedindo o cadastro/edição de turmas por Administradores.
   * *Risco:* Alta. Funcionalidade de gestão de turmas quebrada para o perfil Admin.
   * *Estado atual:* **Resolvido na PR #10.** `GET /api/v1/usuarios` usa `verify_cargo(1, 3)`.

5. **Ações do Ciclo de Vida de Pedidos Bloqueadas para Admin (`backend/app/api/v1/pedidos.py:51,64,77,90`)**
   * *Descrição:* Os endpoints para aprovar, comprar e entregar pedidos exigem `verify_cargo(1)`. Um usuário Admin (Cargo 3) pode acessar a tela `/admin/logistico/pedidos`, mas não consegue executar ações na esteira de suprimentos.
   * *Risco:* Média. Inconsistência entre permissões de gestão logística e atribuições do Admin.
   * *Estado atual:* **Resolvido na PR #10.** Ciclo de vida usa `verify_cargo(1, 3)`.

6. **Endpoint `/api/v1/matriculas/me` Sem Guard de Cargo no Decorator (`backend/app/api/v1/matriculas.py:31`)**
   * *Descrição:* O decorator `@router.get("/me")` utiliza `Depends(get_current_user)` em vez de `verify_cargo(...)`. Embora o corpo da função filtre se `cargo != 2`, a falta de checagem padronizada no decorator descumpre a padronização de segurança e dificulta auditorias automatizadas.
   * *Risco:* Baixa.
   * *Estado atual:* **Resolvido na PR #10.** O decorator usa `verify_cargo(1, 2, 3)`.

---

## Matriz de Negação de Acesso

Esta matriz descreve o comportamento esperado e a localização da regra de validação para cada perfil ao tentar acessar rotas/endpoints administrativos.

| Rota / Endpoint | Perfil Admin (Cargo 3) | Perfil Diretoria (Cargo 1) | Perfil Professor (Cargo 2) | Anônimo (Sem Token) | Localização da Validação |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Frontend `/admin/home` | Permitido (200) | Permitido (200) | Negado (Redirect `/acesso-negado`) | Negado (Redirect `/login`) | `frontend/src/app/features/admin/admin.routes.ts:12` & `role.guard.ts:27` |
| Frontend `/admin/usuarios` | **Permitido (200)** *(atual; baseline Negado)* | Permitido (200) | Negado (Redirect `/acesso-negado`) | Negado (Redirect `/login`) | `frontend/src/app/features/admin/admin.routes.ts:24` & `role.guard.ts:32` (`adminGuard`) |
| Backend `GET /api/v1/dashboard/*` | **Permitido (200)** *(atual; baseline Negado)* | Permitido (200) | Negado (403 Forbidden) | Negado (401 Unauthorized) | `backend/app/api/v1/dashboard.py:21` & `dependencies.py:66` |
| Backend `GET/POST /api/v1/usuarios` | **Permitido (200)** *(atual; baseline Negado)* | Permitido (200) | Negado (403 Forbidden) | Negado (401 Unauthorized) | `backend/app/api/v1/usuarios.py:51` & `dependencies.py:66` |
| Backend `GET/POST /api/v1/alunos` | Permitido (200) | Permitido (200) | Negado (403 Forbidden) | Negado (401 Unauthorized) | `backend/app/api/v1/alunos.py:23` & `dependencies.py:66` |
| Backend `GET/POST /api/v1/cursos` | Permitido (200) | Permitido (200) | Negado (403 Forbidden) | Negado (401 Unauthorized) | `backend/app/api/v1/cursos.py:21` & `dependencies.py:66` |
| Backend `GET/POST /api/v1/turmas` | Permitido (200) | Permitido (200) | Negado (403 em POST; GET permitido) | Negado (401 Unauthorized) | `backend/app/api/v1/turmas.py:24,44` & `dependencies.py:66` |
| Backend `PUT /api/v1/pedidos/{id}/aprovar` | **Permitido (200)** *(atual; baseline Negado)* | Permitido (200) | Negado (403 Forbidden) | Negado (401 Unauthorized) | `backend/app/api/v1/pedidos.py:51` & `dependencies.py:66` |

---

## Cobertura de Testes

### Situação Atual e Estimativa

* **Cobertura Total do Backend:** **70%** (medida via `pytest --cov=backend/app backend/tests`).
* **Cobertura de Endpoints/Rotas de API (`backend/app/api/v1/`):**
  * `alunos.py`: 46%
  * `auth.py`: 51%
  * `cursos.py`: 44%
  * `dashboard.py`: 88%
  * `estoque.py`: 41%
  * `historico.py`: 60%
  * `matriculas.py`: 32%
  * `notas.py`: 52%
  * `pedidos.py`: 29%
  * `presencas.py`: 75%
  * `turmas.py`: 37%
  * `usuarios.py`: 38%
  * **Média ponderada dos routers de API:** **45%**

### Lacunas Identificadas para Atingir >= 70% nas Regras Administrativas

1. **Inexistência de Testes de Negação de Acesso (403) para Módulos Críticos:**
   * O arquivo `backend/tests/test_api_endpoints.py` possui apenas 2 cenários de verificação de papel: `test_dashboard_requires_director` e `test_usuarios_requires_director`.
   * Não existem testes de integração enviando requisições com token de Professor (Cargo 2) para tentar acessar/modificar endpoints de Alunos, Cursos, Turmas, Matrículas, Estoque, Pedidos ou Histórico.

2. **Falta de Testes de Permissão para o Perfil Admin (Cargo 3):**
   * A fixture `auth_headers` em `backend/tests/conftest.py:17` gera por padrão um token com `cargo = 1` (Diretoria). Praticamente todos os testes felizes de API executam como Cargo 1. Não há testes dedicados validando se requisições com `cargo = 3` (Admin) são aceitas nos endpoints administrativos ou rejeitadas onde deveriam.

3. **Ausência de Testes Integrados de Guard no Frontend Angular:**
   * Os arquivos `admin.guard.spec.ts` e `role.guard.spec.ts` contêm apenas instancianções básicas. Não há testes automatizados que simulem navegação pelo `RouterTestingModule` / `provideRouter` para garantir o redirecionamento correto para `/acesso-negado` ou `/login`.

---

## Recomendações e Próximos Passos

> **Status: implementado na PR #10.** As recomendações abaixo foram a base das correções já aplicadas. Estão mantidas como registro histórico da auditoria.

Para adequar o sistema aos critérios de aceite e garantir a segregação segura de funções, recomendam-se as seguintes ações concretas nas tarefas subsequentes:

1. **Unificação e Ajuste de Roles no Backend (`verify_cargo`):**
   * Permitir `cargo = 3` (Admin) nos endpoints de `dashboard.py` (`verify_cargo(1, 3)`), `usuarios.py` (`verify_cargo(1, 3)`) e na esteira de aprovação/compra de pedidos em `pedidos.py` (`verify_cargo(1, 3)`), alinhando a API ao conceito de que o Admin é gestor pleno do sistema. **[Implementado na PR #10.]**
   * Criar um endpoint dedicado para listagem resumida de professores em `usuarios.py` (ex.: `GET /api/v1/usuarios/professores` com `verify_cargo(1, 2, 3)`), resolvendo o bloqueio HTTP 403 na tela de cadastro de turmas. **[Não implementado: resolvido ao permitir Admin em `GET /api/v1/usuarios` existente.]**

2. **Correção de Segurança no Frontend (`auth.service.ts` e `admin.routes.ts`):**
   * Alterar `mapCargoToRole()` em `frontend/src/app/core/services/auth.service.ts:68` para que cargos nulos ou desconhecidos resultem em negação de acesso (ex.: lançar erro ou mapear para perfil sem privilégios), adotando a abordagem **fail-closed**. **[Implementado na PR #10: retorna `'GUEST'`.]**
   * Atualizar `admin.routes.ts` trocando `directorGuard` por `adminGuard` nas rotas `/admin/usuarios` e `/admin/dashboard`. **[Implementado na PR #10.]**

3. **Expansão da Suíte de Testes para Cobertura >= 70% nas Regras Administrativas:**
   * Criar fixture `admin_headers` (`cargo = 3`) e `professor_headers` (`cargo = 2`) em `conftest.py`. **[Implementado na PR #10.]**
   * Implementar suíte parametrizada em `test_api_endpoints.py` testando matriz completa de permissões (Cargo 1, Cargo 2, Cargo 3 e Anônimo) contra todos os verbos e endpoints de `/alunos`, `/cursos`, `/turmas`, `/matriculas`, `/estoque`, `/pedidos`, `/usuarios` e `/dashboard`. **[Parcialmente implementado na PR #10.]**

---

## Nota sobre Revogação de Cargo e Confiança no JWT

A dependência `verify_cargo` em `backend/app/core/dependencies.py` confia exclusivamente nas claims do JWT. O cargo é lido da claim `cargo` e o identificador do usuário da claim `sub`. Não há consulta ao banco de dados durante a validação.

Consequência: uma mudança de cargo no banco de dados não revoga nem atualiza um token já emitido. O usuário mantém o cargo antigo até o token expirar e um novo token ser emitido no próximo login.

Referência: `backend/app/core/dependencies.py` (`get_current_user`, `verify_cargo`, `decode_access_token`).

---

## Resumo dos 5 Principais Riscos Encontrados

> **Status (pós-PR #10).** Este resumo é o registro do baseline da auditoria. O risco 1 (fail-open no client) foi corrigido; os riscos 2, 3 e 4 foram resolvidos; o risco 5 foi amplamente endereçado pela nova suíte de testes de autorização. Ver nota de contexto no topo.

1. **Bypass por Mapeamento Fail-Open no Client (`auth.service.ts:68`):** Cargos inválidos ou nulos são mapeados por padrão como `'ADMIN'`, concedendo acesso a telas restritas no frontend.
2. **Administrador Bloqueado em Tarefas de Gestão no Backend (`usuarios.py`, `dashboard.py`, `pedidos.py`):** O perfil Admin (Cargo 3) recebe HTTP 403 ao tentar gerenciar usuários, visualizar dashboards e aprovar pedidos.
3. **Quebra Funcional na Tela de Turmas para Admin (`classes-management.ts:280`):** Ao cadastrar/editar turmas, a busca de professores falha com 403 Forbidden para Admin, inviabilizando a gestão.
4. **Endpoint com Controle Flutuante (`matriculas.py:31`):** Rota `/api/v1/matriculas/me` não utiliza o decorator padrão `verify_cargo`, fragilizando a política de controle de acesso centralizada.
5. **Déficit Crítico de Testes de Permissão (403):** 100% dos módulos acadêmicos e logísticos carecem de testes de negação de acesso, tornando regressões em regras de autorização indetectáveis.
