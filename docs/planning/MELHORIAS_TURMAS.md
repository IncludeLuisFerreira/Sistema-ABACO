# Plano de Melhorias — Gestão de Turmas

> **Objetivo**: transformar a listagem de turmas numa visão gerencial clara com cards por status,
> agrupamento por curso, filtro por semestre, e formulário de criação com feedback contextual.
> A home da Diretora/Admin também será unificada com o dashboard.

---

## Sprint A — ✅ (PR #59) Cards visuais por status ✅ (PR #59)

**Objetivo**: substituir a tabela `class-list` por cards coloridos que mostram status de relance.

- [x] A.1 Criar componente `TurmaCardComponent` standalone
  - Exibe: nome do curso (destaque), nome do professor, datas início/fim formatadas, dias de aula, vagas (X/Y)
  - Badge colorido no topo: 🔴 Em andamento / 🟡 Futura / ⚫ Encerrada
  - Barra de progresso horizontal (% do período decorrido entre início e fim)
  - Botões: `[Ver Alunos]` `[Editar]`
- [x] A.2 Criar função utilitária `getStatusTurma(inicio, fim): 'em_andamento' | 'futura' | 'encerrada'`
  - Compara `new Date()` com as datas
  - Futura se `hoje < inicio`, Encerrada se `hoje > fim`, Em andamento caso contrário
- [x] A.3 Criar função utilitária `getProgressoTurma(inicio, fim): number` (0 a 100)
  - `((hoje - inicio) / (fim - inicio)) * 100`, cap entre 0 e 100
- [x] A.4 Adicionar campo `vagasOcupadas` na resposta do backend
  - Modificar `GET /api/v1/turmas` para incluir `COUNT(matricula WHERE status=0)`
  - Adicionar ao `TurmaResponseSchema`: `vagasOcupadas: int | None`
  - Adicionar ao model frontend `Turma`: `vagasOcupadas: number | null`
- [x] A.5 Substituir `<app-class-list>` no template por `<app-turma-card *ngFor>`
  - Cards em grid CSS: `grid-template-columns: repeat(auto-fill, minmax(340px, 1fr))`
- [x] A.6 Ordenação dos cards: em andamento → futuras → encerradas → sem data
- [x] A.7 Manter funcionalidades existentes: busca, paginação, CRUD
- [x] A.8 Responsividade: 1 coluna no mobile, 2 no tablet, 3+ no desktop

---

## Sprint B — ✅ (PR #60) Agrupamento por curso (expansível)

**Objetivo**: agrupar turmas pelo nome do curso, colapsado por padrão, expande no clique.

- [x] B.1 Criar lógica `agruparPorCurso(turmas): Map<string, Turma[]>`
  - Chave: `curso.nomeCurso ?? 'Sem curso'`
  - Valor: array de turmas daquele curso
- [x] B.2 Criar componente `TurmaGrupoComponent`
  - Cabeçalho clicável: "Informática Básica (3 turmas)" com ícone ▶/▼
  - Expande/recolhe com animação CSS (max-height + overflow hidden + transition)
  - Conteúdo: grid de `TurmaCardComponent` internos
- [x] B.3 Estado expandido/recolhido persiste localmente (Set<string> de cursos expandidos)
- [x] B.4 Botões "Expandir todos" / "Recolher todos" no topo da listagem
- [x] B.5 Tour sem turmas: badge "0 turmas" em cinza (opcional, não expande)

---

## Sprint C — ✅ (PR #61) Filtro por semestre

**Objetivo**: navegar entre semestres com padrão no semestre atual.

- [x] C.1 Criar função `getSemestre(date: Date): string`
  - Jan–Jun → `ano.1` (ex: 2026-03-15 → "2026.1")
  - Jul–Dez → `ano.2` (ex: 2026-08-01 → "2026.2")
- [x] C.2 Criar seletor de semestre no topo da página (pills horizontais)
  - Gera lista: últimos 4 semestres + próximos 2 a partir das turmas existentes
  - Exibe: `2026.1 (3 turmas)` `2026.2 (5 turmas)` `2025.2 (2 turmas)` `Todos`
  - Selecionado por padrão: semestre atual (baseado em `new Date()`)
- [x] C.3 Filtro aplicado sobre `dataInicio` da turma
  - Turma pertence ao semestre se `getSemestre(dataInicio) === semestreSelecionado`
  - Opção "Todos" desabilita o filtro
- [x] C.4 Combinar filtro de semestre com busca textual e agrupamento
- [x] C.5 Botão "Semestre atual" para voltar rápido ao padrão

---

## Sprint D — ✅ (PR #62) Formulário de criação com contexto

**Objetivo**: dar feedback visual ao criar turma sobre curso e professor.

- [x] D.1 Ao selecionar curso: badge informativo abaixo do select
  - "Já existem 2 turmas de Informática Básica em 2026.1"
  - Backend: usar `turmaService.list()` e filtrar no frontend, ou novo endpoint leve
- [x] D.2 Ao selecionar professor: badge informativo
  - "Este professor já tem 3 turmas neste semestre"
- [x] D.3 Alerta de conflito de horário (aviso amarelo, não bloqueia)
  - Mesmo professor + sobreposição de datas + mesmos dias de aula
  - Verificação no frontend ao selecionar datas/dias
- [x] D.4 Campo "Dias de aula" com checkboxes visuais
  - Checkboxes: ☑ Seg ☑ Ter ☐ Qua ☑ Qui ☐ Sex ☐ Sáb
  - Gera string "Seg/Ter/Qui" automaticamente
  - Mantém compatibilidade com o backend (campo texto)
- [x] D.5 Botão "Duplicar turma" no card
  - Abre formulário de criação preenchido com dados da turma selecionada
  - Limpa o campo de datas (para preencher novo período)

---

## Sprint E — ✅ (PR #63) Home unificada (Dashboard + Ações)

**Objetivo**: Diretora/Admin logam e já veem KPIs + atalhos + pendências.

- [x] E.1 Fundir `/admin/home` com `/admin/dashboard` na página home
  - Diretora (cargo 1): KPIs + gráficos + ações rápidas + pendências
  - Admin (cargo 3): KPIs simplificados + cards de navegação (sem gráficos de diretor)
  - Rota `/admin/dashboard` redireciona para `/admin/home`
- [x] E.2 Seção "Ações rápidas" com botões grandes
  - [+ Nova Turma] [+ Nova Matrícula] [+ Novo Aluno] [+ Novo Pedido]
- [x] E.3 Seção "Pendências" (visível para Diretora e Admin)
  - Card "Pedidos aguardando aprovação: N" → link para `/admin/logistico/pedidos`
  - Card "Estoque crítico: N itens" → link para `/admin/logistico/estoque`
- [x] E.4 KPIs clicáveis: cada card de KPI é um link para a página correspondente
- [x] E.5 Loading state unificado (1 spinner para todos os dados simultâneos)
- [x] E.6 Remover link "Dashboard" do menu lateral (agora é a home)

---

## Resumo

| Sprint | O que muda | Issues | Esforço |
|--------|-----------|--------|---------|
| A | Tabela → cards coloridos | 8 | 4-5h |
| B | Agrupamento expansível por curso | 5 | 2-3h |
| C | Filtro por semestre | 5 | 2h |
| D | Formulário com contexto | 5 | 3h |
| E | Home unificada (Dashboard + Ações) | 6 | 3-4h |
| **Total** | | **29 issues** | **14-17h** |
