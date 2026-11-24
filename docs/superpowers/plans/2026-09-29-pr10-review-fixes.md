# Plan: Correções da review da PR #10 (RBAC admin)

Fonte: comentário de review de `celsohd21` na PR #10.
Base: branch `7-sprint-1-rbac-isolar-permissões-e-acesso-exclusivo-às-tarefas-de-administrador` (início em `ba42b9c`).
Worktree: `/home/includeluisferreira/Documentos/projetos/reais/ABACO_Sistema/.worktrees/pr10-fixes`.

## Global Constraints

- Trabalhar sempre dentro do worktree acima. Nunca tocar a branch `chore/reorganizacao-diretorios`.
- Estilo backend: indentação com TAB, mensagens em português, respostas com schema Pydantic.
- Comando backend (a partir de `<worktree>/backend`):
  `/home/includeluisferreira/Documentos/projetos/reais/ABACO_Sistema/.venv/bin/python -m pytest -q`
  Baseline: 279 passed.
- Comando frontend (a partir de `<worktree>/frontend`): `npx ng test --watch=false`.
  Baseline: 85 passed / 13 files.
- Não adicionar dependências novas. Não fazer refactor fora do escopo. Seguir padrões existentes.
- Não fazer push. Rebase/merge apenas local até o humano aprovar push.
- Ruling (anti-escalação, aprovado pelo humano): Admin (cargo 3) NÃO pode atribuir, editar nem excluir usuário de cargo 1 (Diretoria) e NÃO pode alterar o próprio cargo. Diretoria (cargo 1) mantém acesso irrestrito.
- Ruling (conflito PR #11): rebase da PR #10 sobre o topo da branch da PR #11 (`origin/6-sprint-1-rbac-restringir-acesso-professor-propria-turma-e-alunos`, `90c8c19`), preservando os dois lados.

## Task 1: Rebase sobre a PR #11 e resolução dos conflitos

Objetivo: rebasear a branch atual sobre `origin/6-sprint-1-rbac-restringir-acesso-professor-propria-turma-e-alunos` resolvendo os conflitos, sem perder nenhuma correção da PR #10 nem da PR #11.

Passos:
1. Confirmar: `git log --oneline -1` = `ba42b9c`, `git status` limpo.
2. Rodar `git rebase origin/6-sprint-1-rbac-restringir-acesso-professor-propria-turma-e-alunos`.
3. Resolver cada conflito:
   - `.gitignore`: manter a união das duas adições (`.pytest_cache/`, `.coverage`, `htmlcov/`, `.venv/`, `venv/`), sem linhas duplicadas. Manter `# .worktrees/` comentado.
   - `backend/app/api/v1/matriculas.py`: preservar os DOIS intentos — (a) a correção de segurança da PR #10 que exige cargo válido em `GET /me` (`verify_cargo(1, 2, 3)`), e (b) a lógica da PR #11 que restringe Professor (cargo 2) às suas turmas via service. O resultado não pode reintroduzir o bypass de token com cargo inválido.
   - `backend/tests/conftest.py`: preservar os DOIS intentos — engine SQLite com `StaticPool`/`check_same_thread=False` e as fixtures novas da PR #11 (`api_client`, `outro_professor`, `professor_headers_factory`, `diretor_headers`), E o listener de PRAGMA `foreign_keys=ON` da PR #10.
4. Ao terminar o rebase, rodar a suíte backend completa e a suíte frontend completa. Ambas devem passar (backend >= 279; frontend >= 85). Se o rebase trouxer testes novos da PR #11, o total sobe.
5. Se algum conflito for semanticamente ambíguo e não der para preservar os dois intentos, PARAR e reportar BLOCKED com os trechos exatos.
6. Não fazer push nem force-push.

Commit: o rebase reescreve os commits existentes; nenhum commit novo é necessário, exceto se a resolução exigir. Se exigir, seguir o padrão de commit do repositório.

## Task 2: Concorrência no estoque — devolver 409 em duplicidade

Problema: `backend/app/services/estoque_service.py` em `create_estoque` faz a checagem de duplicidade e depois `db.commit()` sem tratar violação de unicidade. Sob concorrência, o commit estoura `IntegrityError` e vira 500 em vez de 409.

Passos (TDD):
1. Escrever primeiro um teste que falha: forçar o caminho em que a linha já existe no banco no momento do commit (ex.: inserir direto via `db.add`/`commit` ou monkeypatch que contorne a checagem prévia) e afirmar que a API retorna 409, não 500. Localizar o teste no arquivo de estoque existente (`backend/tests/test_estoque_endpoints.py`).
2. Rodar o teste e registrar a saída de falha (RED).
3. Alterar `create_estoque` para envolver o `db.commit()` em `try/except IntegrityError`, fazendo `db.rollback()` e relançando `EstoqueAlreadyExistsError` (que a rota já mapeia para 409). Remover o FIXME referente a essa corrida.
4. Rodar o teste (GREEN) e a suíte de estoque inteira.
5. Confirmar que a rota `POST /api/v1/estoque` continua devolvendo 409 no caso comum (item duplicado) e não muda o contrato.

## Task 3: Guarda anti-escalação em usuários

Regra aprovada: Admin (cargo 3) não pode atribuir/editar/excluir usuário de cargo 1 (Diretoria) e não pode alterar o próprio cargo. Diretoria (cargo 1) irrestrita.

Passos (TDD):
1. Escrever testes que falham em `backend/tests/test_usuarios_endpoints.py`, cobrindo com token de Admin (cargo 3):
   - criar usuário com `cargo=1` deve retornar 403;
   - editar (`PUT`) usuário existente de cargo 1 deve retornar 403;
   - excluir (`DELETE`) usuário de cargo 1 deve retornar 403;
   - tentar mudar o próprio `cargo` (PUT no próprio id com cargo diferente) deve retornar 403.
   E com token de Diretoria (cargo 1): as mesmas operações continuam permitidas (positivos).
2. Registrar RED.
3. Implementar a verificação no lugar mais adequado seguindo o padrão existente. O cargo do requisitante está no payload de `verify_cargo` (ex.: `_current_user.get("cargo")`) e o id em `sub`. Manter o padrão de erro 403 já usado no módulo. Expor mensagens em português.
4. Rodar os testes (GREEN) e a suíte de usuários completa; garantir que os fluxos válidos de Admin (criar/editar cargos 2 e 3) seguem funcionando.

## Task 4: Documentação — remover `verify_director_role` e registrar confiança no JWT

Passos:
1. Remover a referência ao método removido `verify_director_role()` nos arquivos:
   - `Documentação/Diagrama_de_Classe_UML.md` (linha ~552)
   - `Documentação/diagrama_classe_mermaid.md` (linha ~230)
   - `Documentação/diagrama_classe_mermaid.mmd` (linha ~400)
   - `Documentação/diagrama_classe_plantuml.puml` (linha ~245)
   - `Documentação/diagrama_classe_plantuml_parte2.puml` (linha ~90)
   Ajustar de forma que a classe `AuthDependencies` continue coerente (ex.: manter apenas `get_current_user` e `verify_cargo`).
2. Em `docs/analise-rotas-admin.md`, adicionar uma seção curta registrando que `verify_cargo` confia apenas nas claims do JWT (cargo e sub) sem consultar o banco; portanto mudanças de cargo não revogam o token até expirar. Apontar `backend/app/core/dependencies.py`.
3. Não alterar mais nada na documentação.

## Task 5: Padronizar rótulo de cargo ADMIN no access-denied

Passos:
1. Em `frontend/src/app/features/errors/pages/access-denied/access-denied.ts` (linha ~23), trocar o rótulo do papel `ADMIN` de `'Administrativo'` para `'Admin'`.
2. Atualizar o spec correspondente `frontend/src/app/features/errors/pages/access-denied/access-denied.spec.ts` (linha ~33) para esperar `'Admin'`.
3. Rodar `npx ng test --watch=false` e garantir verde.
