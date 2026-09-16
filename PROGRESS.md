# PROGRESS.md

> Status: **100% funcional**. Veja `docs/planning/PLANO_FINAL.md` para o plano completo de acabamento.

## Sprint 1 — Infraestrutura ✅
- [x] #9  Docker stack e health check
- [x] #10 Login e fluxo JWT
- [x] #11 Tela de login e role redirect
- [x] #12 CRUD de usuários (diretor)
- [x] #13 Hardening de segurança

## Sprint 2 — Núcleo acadêmico ✅
- [x] #14 Gestão de alunos
- [x] #15 Gestão de cursos
- [x] #16 Gestão de turmas
- [x] #17 Matrículas

## Sprint 3 — Presença, notas e histórico ✅
- [x] #18 Registro de presença
- [x] #19 Lançamento e consulta de notas
- [x] #20 Histórico escolar

## Sprint 4 — Logística e estoque ✅
- [x] #21 Criação e listagem de pedidos
- [x] #22 Aprovação de pedidos
- [x] #23 Estoque e alertas
- [x] #28 Módulo logístico completo

## Sprint 5 — Dashboard e fechamento ✅
- [x] #24 Dashboard administrativo
- [x] #25 Validação final e tratamento de erros
- [x] #26 Testes automatizados
- [x] #27 Documentação atualizada

## Extras implementados
- Alembic migrations (substituindo SQL ad-hoc)
- Rate limiting nos endpoints de auth
- Auto-logout por expiração de token JWT
- Confirm dialog customizado
- NotificationService com success/error + auto-dismiss
- Auto-cadastro de professor + recuperação de senha
- Dashboard do professor
- `.env.example` com todas variáveis
- CORS configurável por ambiente
