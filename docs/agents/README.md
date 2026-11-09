# Contextos e prompts para agentes

Este diretório guarda o conhecimento que os agentes carregam **sob demanda**. O `AGENTS.md` da raiz
é o contrato curto; aqui fica o detalhe.

## Ordem de carregamento

1. `AGENTS.md` (raiz) — sempre.
2. `docs/agents/CONTEXT.md` — sempre que a tarefa envolver código deste repositório.
3. `docs/agents/CONTEXT-backend.md` **ou** `CONTEXT-frontend.md` — só a stack afetada.
4. `docs/agents/prompts/<tarefa>.md` — exatamente um prompt por tarefa.
5. Arquivos do módulo afetado — localizados com `grep`/`glob`, nunca o repositório inteiro.

Não carregue os dois contextos de stack "por garantia". Isso dobra o custo sem melhorar a resposta.

## Arquivos

| Arquivo | Quando usar | Conteúdo |
|---------|-------------|----------|
| `CONTEXT.md` | Sempre | Produto, papéis, módulos, modelo de dados, autenticação, regras de negócio |
| `CONTEXT-backend.md` | Tarefa em `backend/` | Camadas, convenções, receitas, armadilhas, testes |
| `CONTEXT-frontend.md` | Tarefa em `frontend/` | Estrutura Angular, padrões, receitas, armadilhas, testes |
| `prompts/build-feature.md` | Nova funcionalidade | Fluxo completo: issue → branch → teste → código → verificação |
| `prompts/fix-bug.md` | Bug | Reprodução → causa raiz → correção mínima → regressão |
| `prompts/review-pr.md` | Revisão de PR | Checklist por severidade e formato de saída fixo |
| `prompts/pre-pr.md` | Antes de abrir PR | Gate final com comandos e critérios bloqueantes |

## Como usar por ferramenta

- **OpenCode:** `/build <issue>`, `/fix <descrição>`, `/review <PR>`, `/pre-pr`
  (definidos em `.opencode/commands/`).
- **Claude Code / Cursor:** referencie o arquivo no pedido, por exemplo
  `@docs/agents/prompts/review-pr.md revise o PR #42`.
- **Codex / Copilot:** eles leem `AGENTS.md` automaticamente; inclua no prompt
  "siga `docs/agents/prompts/<tarefa>.md`".

## Regra de manutenção

- Mudou comando, porta, versão ou convenção? Atualize `AGENTS.md` e o contexto correspondente no
  mesmo PR. Contexto desatualizado é pior que ausência de contexto.
- Não copie regra de processo do `CONTRIBUTING.md` para cá. Cite o arquivo.
- Prompt deve continuar abaixo de ~150 linhas. Se passar, quebre em etapas e referencie.
