---
name: verificacao-entrega
description: >
  Gate final de verificação antes de commit/PR no SGA ABACO: confere sincronização com a base
  remota, escopo do diff, testes de backend e frontend, cobertura dos arquivos alterados,
  migration com head único, coerência das mensagens exibidas ao usuário, sincronização de
  documentação e higiene do diff. Use antes de commitar, ao abrir PR, ao revisar entrega
  própria ou quando o usuário pedir "verifica se está pronto", "pode commitar?" ou "/pre-pr".
---

# Verificação de entrega — SGA ABACO

Gate antes de commit e PR. Não implementa código nem "conserta" o diff: se algo falhar, reporta
**NÃO APTO** com arquivo:linha e o comando que falhou. Não mascarar falha com `skip`, `xfail` ou
asserção removida.

Regras de projeto que este gate pressupõe: `AGENTS.md` (fonte de verdade), `CONTRIBUTING.md`
(processo), `docs/agents/CONTEXT-backend.md` e `docs/agents/CONTEXT-frontend.md`.

## 1. Base e escopo

```bash
git status --short              # nada fora do escopo, nada gerado, nada de outra issue
./scripts/agent-preflight.sh --check
git log --oneline "HEAD..origin/develop"
git diff --stat origin/develop...HEAD
```

Reprovar se: branch atrasada, arquivo de outra issue no diff, artefato (`node_modules`, `dist`,
`__pycache__`, `.coverage`, `htmlcov`, `.env`), mudança em `CONTRIBUTING.md`, `README.md`, CI ou
`scripts/` sem pedido explícito, ou mais de 8 arquivos fora do módulo da issue.

## 2. Testes e cobertura

```bash
cd backend && python -m pytest -q
cd backend && python -m pytest <testes do módulo> -q \
  --cov=app/<caminho do arquivo alterado> --cov-report=term-missing
```

- Suíte completa verde. Teste novo cobre o comportamento e o caminho de erro.
- Cobertura dos arquivos alterados conferida: linha não coberta é lacuna real ou código morto —
  relatar, não ignorar.
- Mudou frontend:

```bash
cd frontend && npm test -- --watch=false
cd frontend && npm run build
```

## 3. Schema e migrations

```bash
cd backend && alembic heads     # exatamente um head
```

Sem migration nova quando não houve mudança de schema. Migration já aplicada não é editada.
Mudança que depende de recurso só de PostgreSQL (JSONB, constraint, índice funcional) tem
cobertura parcial em SQLite: registrar isso no PR.

## 4. Coerência do que o usuário vê

Toda mensagem nova ou alterada que chega à UI:

1. Traçar o caminho real: exceção de domínio → `HTTPException.detail` → serviço Angular → template.
2. Confirmar que o texto é frase completa, em português, com acentos, plural e pontuação corretos —
   não um dump de exceção, id cru ou mensagem truncada.
3. Conferir como é renderizado: `app.html` (alerta global `sticky`, quebra linha, sem `ellipsis`) e
   o feedback local da página. Lista longa de ids vira parede de texto: limitar.
4. Se a cópia importa, fixar o texto em teste para não regredir.
5. Erro precisa dizer o que fazer; sucesso precisa dizer o que foi salvo.

## 5. Documentação da feature

Comparar o comportamento novo com: `README.md`, `docs/requirements/PRD.md`,
`docs/analise-rotas-admin.md`, `docs/agents/CONTEXT*.md` e docs de feature em
`docs/architecture/features/`. Se algum afirmar comportamento que mudou, atualizar — exceto
`README.md`, que exige pedido explícito. Registrar no PR a conclusão: "nenhum doc desatualizado"
ou o arquivo corrigido.

## 6. Higiene do diff

```bash
git diff origin/develop...HEAD | grep -nE "print\(|console\.log|pdb|breakpoint\("
git diff origin/develop...HEAD | grep -nE "secret|password|token|API_KEY" | head
```

- Sem `print()` / `console.log` / debugger.
- Sem segredo, token, `.env` ou credencial.
- Sem `# TODO` / `# FIXME` removido sem resolver o problema descrito.
- Sem reformatação do arquivo inteiro; tabs/espaços preservados por arquivo.
- Regra de negócio em `services/`, resposta via schema Pydantic, autorização explícita em endpoint
  novo ou alterado.
- Frontend: `HttpClient` só em `core/services/`.

## 7. Commits

Formato `tipo(escopo): descrição`, português, imperativo, até 72 caracteres, um commit por mudança
lógica. Comparar com `git log --oneline -5` do repositório para manter o padrão.

## 8. Evidência para o PR

Reunir saída real, não descrição: comando de teste com o resumo final, `curl` do endpoint com a
resposta e o status, e print da tela quando a mudança for visível na UI. Evidência inventada ou
simulada deve ser rotulada como simulação.

## 9. Saída

Reportar nesta ordem:

1. **APTO** ou **NÃO APTO**
2. Tabela: item, resultado, evidência (comando + resumo)
3. Pendências com `arquivo:linha` e o comando que falhou
4. Sugestão de mensagens de commit para o diff atual
