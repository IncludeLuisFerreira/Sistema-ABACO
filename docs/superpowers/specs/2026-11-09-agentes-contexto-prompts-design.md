# Design — contextos e prompts para agentes

Data: 2026-11-09
Status: aprovado informalmente pelo usuário na mesma sessão ("pode implementar a b")

## Intenção

Padronizar como agentes de IA da equipe trabalham neste repositório. O problema relatado tem duas
partes: (1) trabalho começando de `develop` desatualizada; (2) falta de contexto especialista para
que agentes de modelos diferentes produzam mudanças corretas, com review e build confiáveis, sem
gastar tokens explorando o repositório.

## Objetivos

- Uma fonte curta e sempre carregada de regras (`AGENTS.md`).
- Contexto técnico especialista por stack, carregado sob demanda.
- Prompts operacionais detalhados para build, fix, review e gate de PR.
- Verificação automatizada de sincronização com a base remota (`upstream/develop` em fork,
  `origin/develop` em clone direto).
- Reduzir idas e voltas e custo de contexto.

## Não objetivos

- Substituir `CONTRIBUTING.md` (processo humano continua sendo a fonte de verdade).
- Criar pipeline de CI novo ou hooks obrigatórios.
- Documentar cada arquivo do repositório.
- Alterar código de produto.

## Abordagens consideradas

1. **Monolito em `AGENTS.md`** — tudo em um arquivo. Simples, mas paga o custo de todos os prompts
   em toda sessão e dificulta manutenção. Rejeitada.
2. **Divulgação progressiva** — `AGENTS.md` curto + `docs/agents/` + prompts sob demanda.
   Escolhida.
3. **Progressiva + enforcement total** — hooks de pre-commit e checagens obrigatórias. Mais robusta,
   porém com atrito e escopo maior. Parcialmente adotada: só o script de preflight.

## Desenho escolhido

```
AGENTS.md                          # contrato curto, sempre carregado
docs/agents/
├── README.md                      # roteamento e regra de manutenção
├── CONTEXT.md                     # produto, papéis, modelo, auth, regras
├── CONTEXT-backend.md             # camadas, receitas, armadilhas, testes
├── CONTEXT-frontend.md            # Angular, receitas, armadilhas, testes
└── prompts/
    ├── build-feature.md
    ├── fix-bug.md
    ├── review-pr.md
    └── pre-pr.md
scripts/agent-preflight.sh         # --check e --start
.opencode/commands/*.md            # atalhos /build /fix /review /pre-pr
```

### Regras centrais em `AGENTS.md`

- Início de sessão obrigatório: `git status`, `git fetch`, preflight; branch sempre da base remota
  (`upstream/develop` em fork, `origin/develop` em clone direto).
- Fronteiras de arquitetura: regra em service, resposta por schema, HTTP em service do frontend,
  autorização explícita, migration com head único.
- Comandos canônicos, definição de pronto, proibições e orçamento de contexto.
- Conflito de fontes resolvido por precedência explícita.

### Estratégia de tokens

- `AGENTS.md` ~150 linhas; contexto de stack carregado isoladamente (nunca os dois).
- Prompts definem o que ler, o que **não** ler e quando parar.
- Formato de saída fixo em todos os prompts reduz resposta livre e retrabalho.
- Review opera no diff, não no repositório; testes por módulo durante, suíte completa no fim.

### Preflight

- Base remota: `upstream` se o remote existir (fork), senão `origin` (clone direto).
- `--check`: faz `fetch` da base, valida repositório, branch, working tree, atraso vs a base, `.env`.
  Retorna código 1 em bloqueio. Se o `fetch` falhar, aborta com código não-zero.
- `--start <tipo/nome>`: valida nome, faz `fetch` da base, exige árvore limpa e cria a branch sem
  tracking a partir da base. Se o `fetch` falhar, nada é criado nem alterado.
- Nunca faz `pull` automático na branch atual nem `reset`.

## Decisões

- Idioma: português, consistente com o repositório.
- Sem duplicar `CONTRIBUTING.md`; citações em vez de cópia.
- Correção registrada: `docs/architecture/architecture.md` está desatualizado quanto a Tailwind e
  deploy; o `AGENTS.md` aponta isso explicitamente.
- Nenhuma dependência nova.
- Commands do OpenCode usam `.opencode/commands/` (formato V2 documentado).

## Verificação

- `bash -n scripts/agent-preflight.sh` e `bash scripts/test_agent_preflight.sh` (cobre fetch
  malsucedido e fork atrasado com upstream atualizado).
- Links/referências entre documentos conferidos.
- Nenhum arquivo de produto alterado.

## O que fica para o autor

- Commitar os arquivos e abrir PR para `develop` (não feito sem pedido explícito).
- Opcional: adicionar hook de pre-commit depois de validar o atrito com a equipe.
