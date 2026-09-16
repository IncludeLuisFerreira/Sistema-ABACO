# Plano de Melhorias — Área do Professor (Acadêmico)

> **Objetivo**: aprimorar a experiência do professor no `/academico`, garantindo que
> ele só veja dados das **suas turmas** e tenha acesso a pedidos de material.
> Toda navegação e dados são escopados ao professor logado.

---

## Diagnóstico atual

| Página | Status | Problema |
|--------|--------|----------|
| Início | ✅ Funcional | Cards de navegação ok, mas não mostra dados reais |
| Minhas Turmas | ⚠️ Tabela | Precisa de cards visuais com status (como admin) |
| Alunos | ⚠️ Tabela | Precisa de cards com avatar + melhor empty state |
| Presenças | ✅ Funcional | Funciona mas sem indicadores visuais de status |
| Notas | ✅ Funcional | Seletor de prova ok, mas falta feedback visual |
| **Pedidos** | ❌ Não existe | Professor não consegue fazer pedidos de material |

---

## Sprint 1 — Dashboard do Professor com dados reais

**Objetivo**: a home mostrar KPIs reais das turmas do professor + atalhos.

- [ ] 1.1 Carregar dados reais no dashboard (total de turmas, total de alunos)
  - Usar `turmaService.listMine()` e `matriculaService.list()` filtrado
- [ ] 1.2 Cards de KPI com números reais (ex: "3 turmas", "24 alunos")
- [ ] 1.3 Atalhos mantidos (Turmas, Alunos, Presenças, Notas)
- [ ] 1.4 Se o professor não tem turmas: mensagem "Você ainda não possui turmas atribuídas. Solicite à diretoria."

---

## Sprint 2 — Minhas Turmas com cards visuais

**Objetivo**: substituir a tabela por cards com status, progresso e vagas (igual ao admin).

- [ ] 2.1 Reutilizar `TurmaCardComponent` do admin na página de turmas do professor
- [ ] 2.2 Mostrar status colorido (em andamento/futura/encerrada), progresso, vagas
- [ ] 2.3 Empty state contextual:
  - Se `turmas.length === 0`: "Nenhuma turma atribuída a você. Entre em contato com a diretoria."
  - Botão "Solicitar turma" (opcional, link para contato)
- [ ] 2.4 Remover ações de editar/excluir (professor não edita turma)
- [ ] 2.5 Adicionar botão "Ver Alunos" no card que filtra alunos daquela turma

---

## Sprint 3 — Alunos com cards e empty states inteligentes

**Objetivo**: mostrar alunos das turmas do professor com visual moderno e mensagens claras.

- [ ] 3.1 Substituir tabela por grid de cards com avatar (inicial do nome)
- [ ] 3.2 Cada card mostra: nome, telefone, turma que pertence, status da matrícula
- [ ] 3.3 Filtrar por turma (dropdown no topo: "Todas as turmas" ou turma específica)
- [ ] 3.4 Empty states contextuais:
  - "Você não possui turmas atribuídas" (se `turmas.length === 0`)
  - "Suas turmas não possuem alunos matriculados" (se tem turma mas sem matrícula)
  - "Nenhum aluno encontrado para o filtro" (se busca não encontra)

---

## Sprint 4 — Presenças com melhor usabilidade

**Objetivo**: facilitar o registro de presenças com indicadores visuais e contagem.

- [ ] 4.1 Adicionar contador de presenças no topo ("12/15 alunos presentes")
- [ ] 4.2 Botão "Marcar todos como presentes" para agilizar
- [ ] 4.3 Indicador visual de presença salva (badge "Salvo em 21/06")
- [ ] 4.4 Empty states contextuais:
  - "Você não possui turmas atribuídas"
  - "Nenhum aluno matriculado nesta turma"
  - "Selecione uma turma e data para registrar presenças"

---

## Sprint 5 — Notas com feedback por avaliação

**Objetivo**: tornar o lançamento de notas mais claro com indicadores de progresso.

- [ ] 5.1 Barra de progresso: "2/3 avaliações lançadas nesta turma"
- [ ] 5.2 Indicador visual de nota salva (badge verde no campo após salvar)
- [ ] 5.3 Destaque no seletor de prova: avaliação atual com cor diferente
- [ ] 5.4 Empty states contextuais:
  - "Você não possui turmas atribuídas"
  - "Nenhum aluno matriculado nesta turma"
  - "Configure as avaliações da turma para lançar notas"

---

## Sprint 6 — Pedidos e Estoque para Professor

**Objetivo**: professor poder criar pedidos de material e ver estoque.

- [ ] 6.1 Adicionar seção "Logístico" no menu lateral do academico
  - Links: "Novo Pedido", "Meus Pedidos"
- [ ] 6.2 Criar página "Novo Pedido" (`/academico/pedidos/novo`)
  - Reutilizar `PedidoFormComponent` do admin
  - Lista de turmas filtrada (só turmas do professor)
  - Ao criar, `idUsuario` = professor logado
- [ ] 6.3 Criar página "Meus Pedidos" (`/academico/pedidos`)
  - Listar pedidos criados pelo professor (filtro por `idUsuario`)
  - Mostrar status do pedido (Solicitado/Aprovado/Comprado/Entregue)
  - Badge colorido por status
- [ ] 6.4 Adicionar rotas no `academico.routes.ts`:
  - `/academico/pedidos/novo`
  - `/academico/pedidos`
- [ ] 6.5 Backend: garantir que `POST /api/v1/pedidos` aceita professor
  - Atualmente usa `verify_cargo(1, 3)` — precisa incluir cargo 2 ou criar endpoint separado

---

## Resumo

| Sprint | O que muda | Issues |
|--------|-----------|--------|
| 1 | Dashboard com dados reais | 4 |
| 2 | Cards visuais nas turmas | 5 |
| 3 | Cards de alunos + empty states | 4 |
| 4 | Melhorias em presenças | 4 |
| 5 | Feedback visual em notas | 4 |
| 6 | Pedidos e estoque para professor | 5 |
| **Total** | | **26 issues** |
