# Varredura de bugs — 2026-11-11

> **Documento de triagem.** Este arquivo não altera comportamento do sistema. Cada seção
> (`BUG-xx`) foi escrita para virar **uma issue independente**. Use o checklist do fim do
> documento ao abrir as issues.
>
> Base analisada: `develop` em `dac3087` (2026-11-11).

## Resumo

| ID | Severidade | Título | Camada |
|----|------------|--------|--------|
| BUG-01 | Alta | Edição de matrícula em turma lotada/duplicada retorna 500 | Backend |
| BUG-02 | Alta | Professor cria pedido em turma de outro professor | Backend |
| BUG-03 | Alta | Professor lê pedidos de todos os usuários | Backend |
| BUG-04 | Alta | Quantidade negativa em pedido aumenta o estoque | Backend |
| BUG-05 | Alta | Fluxo compra/entrega permite inflar estoque e nunca dá baixa líquida | Backend |
| BUG-06 | Alta | Pedido com item de estoque inexistente retorna 500 | Backend |
| BUG-07 | Alta | Login e recuperação de senha diferenciam maiúsculas/minúsculas no e-mail | Backend |
| BUG-08 | Alta | Tokens de reset e primeiro acesso são reutilizáveis | Backend |
| BUG-09 | Média | Token de usuário excluído continua válido | Backend |
| BUG-10 | Média | Validações de domínio ausentes (estoque negativo, nota fora de 0–10, senha fraca) | Backend |
| BUG-11 | Média | Health check responde 200 mesmo com banco indisponível | Infra/Backend |
| BUG-12 | Média | Gráfico de consumo de estoque exibe valores negativos | Backend/Frontend |
| BUG-13 | Média | Admin não consegue comprar/entregar pedidos pela interface | Frontend |
| BUG-14 | Média | Botão “Excluir” de pedido aparece para professor e sempre falha | Frontend |
| BUG-15 | Média | Formulário de pedido aceita item sem estoque e quantidade vazia/zero | Frontend |
| BUG-16 | Média | Listas de notas/presenças podem ficar vazias por condição de corrida | Frontend |
| BUG-17 | Média | Detecção de conflito de horário do professor compara dias por igualdade de string | Frontend |
| BUG-18 | Média | Tela de estoque fica em “carregando” para sempre em falha de rede | Frontend |
| BUG-19 | Baixa | Presenças ignoram matrícula inválida em silêncio | Backend |
| BUG-20 | Baixa | Aba “Lista de Compras” inclui pedidos já entregues | Frontend |
| BUG-21 | Baixa | `create_aluno`/`create_curso` sem tratamento de `IntegrityError` | Backend |
| BUG-22 | Baixa | `update_estoque` não normaliza o nome do item | Backend |
| BUG-23 | Baixa | Qualquer `IntegrityError` em `create_estoque` vira “item já existe” | Backend |
| BUG-24 | Baixa | Falha de envio no “esqueci a senha” é silenciosa para o usuário | Backend |
| BUG-25 | Baixa | Erro 422 do login não é exibido corretamente | Frontend |
| BUG-26 | Baixa | Cargo inválido é convertido silenciosamente para Admin | Frontend |
| BUG-27 | Baixa | Seed embutido no `main.py` depende de IDs fixos e credenciais hardcoded | Backend/Infra |
| BUG-28 | Média | Endurecimento de autenticação (segredo default, JWT em localStorage) | Backend/Frontend |

## Escopo e método

- Leitura de routers, services, schemas, models, e-mail e migrations do backend; guards,
  interceptors, services, rotas e telas principais do frontend.
- Suíte do backend executada: **533 passed, 1 skipped**, cobertura **95%**.
- Hipóteses confirmadas com `TestClient` + SQLite isolado (sem tocar no banco real):
  BUG-01, BUG-02, BUG-03, BUG-04, BUG-06 e BUG-07.
- Itens já sinalizados no código com `TODO`/`FIXME` foram mantidos quando representam
  risco real; o texto abaixo registra o impacto, não apenas o marcador.

---

## BUG-01 — Edição de matrícula em turma lotada/duplicada retorna 500

**Severidade:** Alta
**Componente:** `backend/app/api/v1/matriculas.py`, `backend/app/services/matricula_service.py`

**Evidência**
- `backend/app/services/matricula_service.py:136-142` chama `_check_matricula_duplicada` e
  `_check_turma_lotada` em `update_matricula`.
- `backend/app/api/v1/matriculas.py:64-76` só captura `MatriculaNotFoundError`,
  `AlunoNotFoundForMatriculaError`, `TurmaNotFoundForMatriculaError` e
  `MatriculaHasDependenciesError` — **não captura** `TurmaLotadaError` nem
  `MatriculaDuplicadaError`.

**Impacto**
- Qualquer edição de matrícula em turma cheia resulta em **500**. O frontend
  (`frontend/src/app/features/enrollments/pages/enrollments-management/enrollments-management.ts:130-135`)
  sempre envia `idTurma`, então o caminho é atingido até para alterar apenas o `status`.
- A checagem de lotação não exclui a própria matrícula e roda mesmo quando a turma não mudou.

**Reprodução**
1. Turma com `capacidade = 1` e uma matrícula ativa.
2. `PUT /api/v1/matriculas/{id}` com `{idAluno, idTurma, dataMatricula, status}`.
3. Resultado observado: `TurmaLotadaError` não tratado (500). O mesmo ocorre com
   `MatriculaDuplicadaError`.

**Correção sugerida**
- Mapear as duas exceções no router (`400` para lotação, `409` para duplicidade) **ou**
  tratá-las no service como erro de domínio único.
- Em `update_matricula`, só checar lotação quando `idTurma` realmente mudar e excluir a
  própria matrícula da contagem.
- Testes de regressão: editar status de matrícula em turma cheia; mover para turma cheia;
  editar gerando duplicidade ativa.

---

## BUG-02 — Professor cria pedido em turma de outro professor

**Severidade:** Alta
**Componente:** `backend/app/services/pedido_service.py`, `backend/app/api/v1/pedidos.py`

**Evidência**
- `backend/app/services/pedido_service.py:54-55`: `create_pedido` chama apenas
  `_resolve_turma` (verifica existência).
- `backend/app/api/v1/pedidos.py:41-48`: endpoint não chama `enforce_turma_access`.

**Impacto**
- Um professor pode criar pedidos de material vinculados a turmas de terceiros,
  distorcendo relatórios e o fluxo de aprovação.

**Reprodução**
- Professor A autenticado envia `POST /api/v1/pedidos` com `idTurma` do professor B.
- Resultado observado: **200** e pedido criado.

**Correção sugerida**
- No router, usar `enforce_turma_access(db, payload.idTurma, current_user)` antes de criar.
- Teste de regressão: professor tentando criar em turma alheia recebe 403.

---

## BUG-03 — Professor lê pedidos de todos os usuários

**Severidade:** Alta
**Componente:** `backend/app/api/v1/pedidos.py`, `backend/app/services/pedido_service.py`

**Evidência**
- `backend/app/api/v1/pedidos.py:27-29` (`GET /pedidos`) e `:32-38` (`GET /pedidos/{id}`)
  permitem cargo 2 sem filtrar por solicitante.
- `backend/app/services/pedido_service.py:81-82` retorna a tabela inteira.

**Impacto**
- Vazamento de dados entre professores (materiais, turmas e nomes de solicitantes).
- Combinado com BUG-14, o professor vê ações que não pode executar.

**Correção sugerida**
- Para cargo 2, filtrar por `Pedido.id_usuario == current_user.sub` (ou por turmas do
  professor, conforme regra de produto).
- `GET /pedidos/{id}` deve aplicar a mesma regra.
- Testes de regressão para listagem e detalhe.

---

## BUG-04 — Quantidade negativa em pedido aumenta o estoque

**Severidade:** Alta
**Componente:** `backend/app/schemas/pedido_schema.py`, `backend/app/services/pedido_service.py`

**Evidência**
- `backend/app/schemas/pedido_schema.py:6-10`: `quantidade: int | None = None` sem `gt=0`.
- `backend/app/services/pedido_service.py:172-193`: `if not item.quantidade: continue`
  deixa passar negativos e faz `saldo - (-50)`.

**Impacto**
- Pedido com quantidade negativa aprovado **aumenta** o estoque.
- Quantidade `null` é aceita e o item é ignorado silenciosamente na aprovação.

**Reprodução**
- Estoque com 100 unidades; pedido com `quantidade: -50`; aprovação.
- Resultado observado: estoque **150**.

**Correção sugerida**
- `quantidade: int = Field(gt=0)` no schema (e `idItemEstoque` obrigatório quando o item
  vier do estoque).
- Defesa adicional no service (rejeitar `<= 0`).
- Teste de regressão: aprovação rejeita quantidade negativa/zero/nula.

---

## BUG-05 — Fluxo compra/entrega permite inflar estoque e nunca dá baixa líquida

**Severidade:** Alta
**Componente:** `backend/app/services/pedido_service.py`

**Evidência**
- `backend/app/services/pedido_service.py:166` (`_aprovar_pedido`) deduz o estoque.
- `:196-203` (`comprar_pedido`) altera a quantidade do item **sem ajustar o estoque**.
- `:259-276` (`entregar_pedido`) **soma** a quantidade atual ao estoque e ainda casa o item
  por `nome_item` (não por `id_item_estoque`), criando item novo com `unidade=None` quando
  não encontra o nome.

**Impacto**
- Cenário: aprovar 1 unidade (−1), comprar alterando para 1000, entregar (+1000) → saldo
  líquido **+999**.
- No caminho feliz, aprovar (−X) e entregar (+X) resulta em **estoque líquido zero**,
  contrariando a expectativa de baixa de material.
- Entregas não geram `MovimentacaoEstoque`, então a auditoria fica incompleta.

**Correção sugerida**
- Definir a regra: baixa na entrega **ou** baixa na aprovação (não ambas).
- Ajustar o saldo pela variação de quantidade ao comprar, ou bloquear alteração de
  quantidade após aprovação.
- Usar `id_item_estoque` como chave e criar `MovimentacaoEstoque` de saída na entrega.
- Teste de regressão: saldo final após o ciclo completo; compra com quantidade divergente.

---

## BUG-06 — Pedido com item de estoque inexistente retorna 500

**Severidade:** Alta
**Componente:** `backend/app/services/pedido_service.py`

**Evidência**
- `backend/app/services/pedido_service.py:54-78`: valida apenas a turma; não valida
  `idItemEstoque` e não trata `IntegrityError` no `commit`.

**Impacto**
- FK inválida em `itempedido` gera exceção não tratada → 500 com mensagem genérica.

**Reprodução**
- `POST /api/v1/pedidos` com `idItemEstoque: 9999` → `IntegrityError` (FK).

**Correção sugerida**
- Validar os itens contra o estoque e devolver `400` com detalhe.
- Envolver o `commit` em `try/except IntegrityError` com `rollback`.
- Teste de regressão.

---

## BUG-07 — Login e recuperação de senha diferenciam maiúsculas/minúsculas no e-mail

**Severidade:** Alta
**Componente:** `backend/app/services/auth_service.py`

**Evidência**
- `backend/app/services/auth_service.py:40` e `:72` comparam `Usuario.email == email`.
- `EmailStr` valida o formato, mas não normaliza a caixa.

**Impacto**
- Usuário cadastrado como `nome@abaco.org.br` não consegue entrar como
  `Nome@Abaco.org.BR` (401).
- No “esqueci a senha”, a resposta é o 200 genérico e **nenhum e-mail é enviado**.

**Reprodução**
- Login com e-mail em caixa mista → 401 (confirmado).

**Correção sugerida**
- Normalizar (`strip().lower()`) em `LoginRequest`, `ForgotPasswordRequest` e na consulta
  (`func.lower(Usuario.email) == email.lower()`).
- Teste de regressão para login e recuperação com caixa mista e espaços.

---

## BUG-08 — Tokens de reset e primeiro acesso são reutilizáveis

**Severidade:** Alta
**Componente:** `backend/app/core/security.py`, `backend/app/services/auth_service.py`

**Evidência**
- `backend/app/core/security.py:33-37` e `:66-72`: JWT sem `jti` e sem estado no servidor.
- `backend/app/services/auth_service.py:97-120`: redefinem a senha sem invalidar o token.

**Impacto**
- O mesmo link de reset (30 min) ou de primeiro acesso (24 h) pode ser usado várias vezes,
  inclusive depois de já ter sido consumido (ex.: link vazado em log/histórico).
- `process_reset_password` não zera `primeiro_acesso`, então o usuário que reseta a senha
  continua sendo forçado a “alterar senha” no próximo login.

**Correção sugerida**
- Persistir hash/`jti` de uso único (tabela de tokens) ou incluir versão da senha no token.
- Zerar `primeiro_acesso` no reset.
- Teste de regressão: segundo uso do mesmo token falha.

---

## BUG-09 — Token de usuário excluído continua válido

**Severidade:** Média
**Componente:** `backend/app/core/dependencies.py`

**Evidência**
- `backend/app/core/dependencies.py:55-57`: `get_current_user` decodifica o JWT e não
  consulta o banco (já marcado como `TODO` no código).

**Impacto**
- Usuário excluído (ou com cargo alterado) mantém acesso até a expiração do token.

**Correção sugerida**
- Consultar o usuário no banco em `get_current_user`/`verify_cargo` e comparar o cargo
  atual, ou manter uma lista de revogação.
- Teste de regressão: token de usuário removido retorna 401.

---

## BUG-10 — Validações de domínio ausentes

**Severidade:** Média
**Componente:** `backend/app/schemas/estoque_schema.py`, `nota_schema.py`, `usuario_schema.py`, `matricula_schema.py`

**Evidência**
- `estoque_schema.py:4-16`: `quantidadeDisponivel` e `estoqueMinimo` aceitam negativos.
- `nota_schema.py:6-15`: `nota` sem faixa 0–10 (a UI tem `min/max`, mas não bloqueia o
  envio; o backend aceita qualquer valor).
- `usuario_schema.py:9-10`: senha do cadastro com `min_length=1`, enquanto o reset exige
  8+ com letra e número (`auth_schema.py:18-28`).
- `matricula_schema.py:6-17`: `status` aceita qualquer inteiro.

**Impacto**
- Dados inválidos entram no banco e contaminam médias, alertas e relatórios.

**Correção sugerida**
- `Field(ge=0)` para quantidades; `Field(ge=0, le=10)` para nota; regex de senha no
  cadastro; `Literal[0,1,2]` (ou enum) para status de matrícula.
- Testes unitários de schema.

---

## BUG-11 — Health check responde 200 mesmo com banco indisponível

**Severidade:** Média
**Componente:** `backend/main.py`, `docker-compose.yml`

**Evidência**
- `backend/main.py:246-256` engole a exceção e devolve sempre `{"status": "ok", ...}`.
- `docker-compose.yml:56` valida apenas `r.status == 200` e o byte `ok`.

**Impacto**
- O backend é marcado *healthy* com o banco fora; o frontend sobe e acumula erros.
- Orquestradores que dependem do health check não reiniciam o serviço.

**Correção sugerida**
- Retornar `503` quando `database == "disconnected"` (ou separar `/health/live` e
  `/health/ready`).
- Ajustar o health check do Compose.
- Teste de regressão.

---

## BUG-12 — Gráfico de consumo de estoque exibe valores negativos

**Severidade:** Média
**Componente:** `backend/app/services/dashboard_service.py`, `frontend/.../dashboard/pages/home/home.ts`

**Evidência**
- `backend/app/services/dashboard_service.py:99-117` soma `MovimentacaoEstoque.quantidade`,
  que é negativa para `baixa_manual` e `pedido_aprovado`.
- `frontend/src/app/features/dashboard/pages/home/home.ts:206-209` plota direto.

**Impacto**
- O gráfico “Consumo de Estoque (Mês Atual)” aparece com barras negativas.
- A ordem (`ORDER BY SUM(...) DESC`) também fica invertida.

**Correção sugerida**
- Retornar `abs(sum)` (ou `-sum`) como consumo e ordenar por esse valor.
- Teste de regressão com movimentações negativas.

---

## BUG-13 — Admin não consegue comprar/entregar pedidos pela interface

**Severidade:** Média
**Componente:** `frontend/src/app/features/logistico/components/pedido-table`

**Evidência**
- `pedido-table.ts:67-69`: `isDirector()` retorna `cargo === 1`.
- `pedido-table.html:66` e `:76`: botões “Comprar”/“Entregar” exigem `isDirector()`.
- Backend permite cargo 3: `backend/app/api/v1/pedidos.py:70` e `:102`.

**Impacto**
- O Admin vê a esteira de pedidos, mas não consegue avançá-la, apesar de o backend
  autorizar. Inconsistência entre UI e RBAC documentado.

**Correção sugerida**
- Criar `canManagePedidos()` para cargos 1 e 3 e usar em comprar/entregar; manter
  “Aprovar” exclusivo do cargo 1.
- Teste de componente.

---

## BUG-14 — Botão “Excluir” de pedido aparece para professor e sempre falha

**Severidade:** Média
**Componente:** `frontend/src/app/features/logistico/components/pedido-table/pedido-table.html`

**Evidência**
- `pedido-table.html:85-92`: botão “Excluir” sem verificação de cargo.
- Backend exige cargo 1/3: `backend/app/api/v1/pedidos.py:115`.

**Impacto**
- Professor recebe 403 ao clicar; ação também aparece em pedidos de terceiros.

**Correção sugerida**
- Exibir somente para cargos 1 e 3 e, se a regra for “dono do pedido”, também validar
  `idUsuario`.
- Teste de componente.

---

## BUG-15 — Formulário de pedido aceita item sem estoque e quantidade vazia/zero

**Severidade:** Média
**Componente:** `frontend/src/app/features/logistico/components/pedido-form/pedido-form.ts`

**Evidência**
- `pedido-form.ts:142-146`: `quantidade` e `idItemEstoque` sem validadores.
- `pedido-form.ts:44-49` e `:127-131`: item pode ser texto livre, com `idItemEstoque: null`.

**Impacto**
- Pedidos com itens “fantasma”, quantidade nula/zero ou negativa; na aprovação os itens
  são ignorados (BUG-04) e na entrega podem criar itens de estoque indevidos (BUG-05).

**Correção sugerida**
- `Validators.required`, `Validators.min(1)` para quantidade; exigir seleção no dropdown
  (`idItemEstoque`) ou tratar explicitamente “item não cadastrado”.
- Teste de componente.

---

## BUG-16 — Listas de notas/presenças podem ficar vazias por condição de corrida

**Severidade:** Média
**Componente:** `frontend/.../grades/pages/grades-management`, `.../attendance/pages/attendance-management`

**Evidência**
- `grades-management.ts:48-60` dispara `loadMatriculas()` e `loadNotas()` em paralelo;
  `buildStudentList()` (`:166-186`) usa `this.matriculas`, que pode estar vazio.
- `loadMatriculas()` (`:131-141`) apenas atualiza o array, sem reconstruir a lista.
- `attendance-management.ts:95-106` (`onTurmaChange`) e `:200-258` seguem o mesmo padrão.

**Impacto**
- Selecionar a turma logo após abrir a tela pode mostrar “Nenhum aluno matriculado” sem
  que o usuário tenha feito nada errado; só recarregar resolve.

**Correção sugerida**
- Encadear as chamadas (`switchMap`/`forkJoin`) ou reconstruir a lista quando as
  matrículas chegarem.
- Teste de componente com respostas fora de ordem.

---

## BUG-17 — Detecção de conflito de horário compara dias por igualdade de string

**Severidade:** Média
**Componente:** `frontend/src/app/features/classes/components/class-form/class-form.ts`

**Evidência**
- `class-form.ts:181-193`: conflito só é detectado quando `t.diasAula === diasAulaStr`.
- `updateContexto` só é chamado em `onCursoChange`/`onProfessorChange` (`:145-151`), não
  quando datas/dias mudam.

**Impacto**
- Turmas com dias parcialmente coincidentes (“1,3” × “1,3,5”) passam sem aviso, e o aviso
  fica desatualizado após editar datas/dias.

**Correção sugerida**
- Comparar conjuntos de dias (interseção não vazia) e recalcular em `valueChanges` de
  datas/dias.
- Teste de componente.

---

## BUG-18 — Tela de estoque fica em “carregando” para sempre em falha de rede

**Severidade:** Média
**Componente:** `frontend/src/app/core/services/estoque.service.ts`, `.../estoque-management`

**Evidência**
- `estoque.service.ts:18-23`: `loadAll()` faz `subscribe` interno sem `error`.
- `estoque-management.ts:240-243`: `loadEstoque()` seta `loadingList = true` e só zera
  quando o `BehaviorSubject` emite.

**Impacto**
- Em erro de rede/500 a tela fica permanentemente carregando, sem feedback.

**Correção sugerida**
- Tratar `error` no `subscribe` interno (notificação + reset de estado) ou expor
  `loadAll(): Observable`.
- Teste de serviço.

---

## BUG-19 — Presenças ignoram matrícula inválida em silêncio

**Severidade:** Baixa
**Componente:** `backend/app/services/presenca_service.py`

**Evidência**
- `backend/app/services/presenca_service.py:24-27`: `continue` quando a matrícula não
  pertence à turma.
- `nota_service.py:36-40` lança erro equivalente.

**Impacto**
- Salvamento parcial sem aviso; o professor acredita que todos foram registrados.

**Correção sugerida**
- Lançar erro de validação (422) como em notas, ou devolver a lista de ignorados.
- Teste de regressão.

---

## BUG-20 — Aba “Lista de Compras” inclui pedidos já entregues

**Severidade:** Baixa
**Componente:** `frontend/src/app/features/logistico/pages/pedido-list/pedido-list.ts`

**Evidência**
- `pedido-list.ts:46-48`: filtra `status >= 1`, incluindo `3` (entregue).

**Impacto**
- Lista de compras cresce indefinidamente e mostra itens já entregues.

**Correção sugerida**
- Filtrar `status === 1` (aprovado) e, se necessário, uma aba separada para histórico.

---

## BUG-21 — `create_aluno`/`create_curso` sem tratamento de `IntegrityError`

**Severidade:** Baixa
**Componente:** `backend/app/services/aluno_service.py`, `curso_service.py`

**Evidência**
- `aluno_service.py:26-27` e `curso_service.py:20-21`: `commit` sem `try/except`.

**Impacto**
- Falhas de integridade viram 500 em vez de resposta de domínio; sessão não recebe
  `rollback` explícito.

**Correção sugerida**
- Padronizar com `update`/`delete` (try/except + rollback + exceção de domínio).

---

## BUG-22 — `update_estoque` não normaliza o nome do item

**Severidade:** Baixa
**Componente:** `backend/app/services/estoque_service.py`

**Evidência**
- `estoque_service.py:90-91`: `estoque.nome_item = payload.nomeItem` sem `strip()`.
- O índice único é `lower(nomeitem)` (`models/estoque.py:9-11`), que não remove espaços.

**Impacto**
- `"Papel"` e `"Papel "` coexistem; a checagem de duplicidade de `create` usa `strip()` e
  não prevê o caso do update.

**Correção sugerida**
- `strip()` (e talvez colapsar espaços) no update; normalizar também na busca.

---

## BUG-23 — Qualquer `IntegrityError` em `create_estoque` vira “item já existe”

**Severidade:** Baixa
**Componente:** `backend/app/services/estoque_service.py`

**Evidência**
- `estoque_service.py:59-65`: `except IntegrityError` mapeia sempre para
  `EstoqueAlreadyExistsError`.

**Impacto**
- Outros erros de integridade são mascarados como 409, dificultando diagnóstico.

**Correção sugerida**
- Reutilizar `_is_unique_violation` (já existe em `:33-39`) e relançar os demais casos.

---

## BUG-24 — Falha de envio no “esqueci a senha” é silenciosa

**Severidade:** Baixa
**Componente:** `backend/app/api/v1/auth.py`

**Evidência**
- `auth.py:66-71`: `EmailDeliveryError` só gera log; a resposta continua sendo sucesso.

**Impacto**
- Usuário é informado de que o e-mail foi enviado, mas nada chega, sem canal de suporte
  nem indicação de falha.

**Correção sugerida**
- Manter mensagem genérica (anti-enumeração), mas registrar métrica/alerta operacional e
  documentar o comportamento; opcionalmente expor health de e-mail.

---

## BUG-25 — Erro 422 do login não é exibido corretamente

**Severidade:** Baixa
**Componente:** `frontend/src/app/core/services/auth.service.ts`, `.../login/login.ts`

**Evidência**
- `auth.service.ts:123-126`: `error?.error?.detail` pode ser um array (422 do FastAPI) e é
  atribuído diretamente a `message`.
- `login.ts:64-67` exibe `err.message` como string.

**Impacto**
- Mensagens como `[object Object]` ou vazias em erros de validação.

**Correção sugerida**
- Usar o utilitário existente `getApiErrorMessage` (`core/utils/api-error.ts`).

---

## BUG-26 — Cargo inválido é convertido silenciosamente para Admin

**Severidade:** Baixa
**Componente:** `frontend/.../users/pages/users-management/users-management.ts`

**Evidência**
- `users-management.ts:229-235`: `normalizeCargo` retorna `3` para qualquer valor fora de
  1/2/3.

**Impacto**
- Um payload inesperado pode rebaixar/atribuir Admin sem aviso.

**Correção sugerida**
- Bloquear o envio e exibir erro quando o cargo for inválido.

---

## BUG-27 — Seed embutido depende de IDs fixos e credenciais hardcoded

**Severidade:** Baixa
**Componente:** `backend/main.py`

**Evidência**
- `backend/main.py:199-225`: `ItemPedido` referencia `id_item_estoque` fixos 1–6 antes de
  inserir o estoque.
- `backend/main.py:136-144`: senhas `admin123`/`prof12345` no código.
- `backend/main.py:81-112`: seed só roda se `ADMIN_SEED_*` estiver definido; se `Curso`
  estiver vazio mas houver usuários, o seed tenta recriar e-mails únicos → falha de startup.

**Impacto**
- Banco novo funciona por coincidência de sequence; ambientes parcialmente populados
  podem quebrar o startup. Credenciais conhecidas em código.

**Correção sugerida**
- Extrair seed para script/CLI idempotente, buscar IDs após `flush`, usar variáveis de
  ambiente e validar pré-condições.

---

## BUG-28 — Endurecimento de autenticação

**Severidade:** Média
**Componente:** `backend/app/core/config.py`, `backend/main.py`, `frontend/.../auth.service.ts`

**Evidência**
- `config.py:19-23`: `SECRET_KEY` com default `development_secret_change_me`.
- `frontend/.../auth.service.ts:113-114`: JWT em `localStorage`.
- `backend/main.py:61-68`: `allow_methods=["*"]`/`allow_headers=["*"]` com credenciais.
- `security.py:28`: JWT sem `jti`/`iat` (sem revogação/logout real).

**Impacto**
- Se `SECRET_KEY` não for definida em produção, tokens podem ser forjados; XSS permite
  roubo de sessão; não há revogação.

**Correção sugerida**
- Falhar o startup sem `SECRET_KEY` em produção; cookie `HttpOnly` + CSRF; permitir apenas
  métodos/headers necessários; adicionar `jti`/revogação.

---

## Checklist para abrir as issues

Para cada `BUG-xx`:

- [ ] Título no formato `[BUG-xx] <descrição curta>`
- [ ] Corpo copiando a seção correspondente (evidência, impacto, reprodução, correção)
- [ ] Labels sugeridas: `bug`, `backend` **ou** `frontend`, `prioridade:alta|media|baixa`,
      e `seguranca` quando aplicável (BUG-02, 03, 07, 08, 09, 28)
- [ ] Vincular este documento no corpo da issue
- [ ] Definir critério de aceite = teste de regressão descrito na seção

**Ordem sugerida:** BUG-01 a BUG-08 (correções com impacto funcional/segurança), depois
BUG-10, 11, 13–18, e por fim os itens de robustez (19–28).

> Observação: a suíte do backend está verde porque os caminhos acima não têm cobertura.
> Toda issue deve incluir o teste que reproduz a falha **antes** da correção.
