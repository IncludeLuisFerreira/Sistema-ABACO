# Prompt — gate antes do PR

Você é o último filtro antes de abrir o Pull Request. Não implemente nada nesta etapa: verifique e
reporte. Qualquer item bloqueante reprovado impede o PR.

## Entrada

- Branch atual (ou nome da branch).
- Issue vinculada.

## Contexto a carregar

1. `AGENTS.md`.
2. `docs/agents/CONTEXT.md` — só para conferir se a mudança respeita o domínio.
3. O diff: `git diff "$BASE/develop"...HEAD --stat` e `git diff "$BASE/develop"...HEAD`
   (`BASE=upstream` em fork, `BASE=origin` em clone direto).

Não leia arquivos que não aparecem no diff, exceto para confirmar um contrato.

## Checklist de execução

Rode na ordem. Pare no primeiro bloqueante e reporte; não continue "para economizar tempo".

### 1. Sincronização

```bash
BASE=upstream   # ou origin, em clone direto (sem upstream)
git fetch "$BASE" --prune
git status --short
git log --oneline "HEAD..$BASE/develop"
```

- [ ] Working tree limpa (ou mudanças intencionais e commitadas)
- [ ] Branch não está atrasada em relação a `$BASE/develop` (se estiver, `git rebase "$BASE/develop"`)
- [ ] Branch não é `main` nem `develop`
- [ ] Nome da branch segue `feature|fix|docs|refactor|test|chore/<slug>`

### 2. Escopo

```bash
git diff "$BASE/develop"...HEAD --stat
```

- [ ] Só arquivos do módulo da issue
- [ ] Sem arquivo gerado (`dist`, `htmlcov`, `__pycache__`, `.coverage`, `node_modules`)
- [ ] Sem `.env`, segredo, token ou chave
- [ ] Sem dependência nova não aprovada
- [ ] Sem reformatação de arquivo inteiro

### 3. Testes

```bash
cd backend && python -m pytest -q
```

- [ ] Suíte backend verde
- [ ] Teste novo cobre o comportamento (sucesso + erro principal)
- [ ] Teste de autorização (401/403) quando o endpoint mudou
- [ ] Nenhum `skip`/`xfail` novo

```bash
cd frontend && npm test -- --watch=false
cd frontend && npm run build
```

- [ ] Suíte frontend verde (se mexeu no frontend)
- [ ] Build de produção verde (se mexeu no frontend)
- [ ] Rotas novas com guard
- [ ] Sem `console.log`

### 4. Schema e migrations

```bash
cd backend && alembic heads
```

- [ ] Um único head
- [ ] Migration nova revisada (não autogerada às cegas)
- [ ] `down_revision` aponta para o head anterior correto
- [ ] Nenhuma migration aplicada foi editada
- [ ] `database-schema.sql` não foi alterado

### 5. Código

- [ ] Regra de negócio em `app/services/`
- [ ] Endpoint com autorização explícita
- [ ] Resposta por schema Pydantic
- [ ] HTTP do frontend em `core/services/`
- [ ] Erros de API tratados com `getApiErrorMessage`
- [ ] Sem `TODO`/`FIXME` removido indevidamente
- [ ] Comentários e nomes coerentes com o módulo

### 6. Commits e descrição

```bash
git log "$BASE/develop"..HEAD --oneline
```

- [ ] Commits no padrão `tipo(escopo): descrição`
- [ ] Mensagens em português, imperativo, ≤72 caracteres na primeira linha
- [ ] Sem commit de merge desnecessário
- [ ] `Closes #<N>` presente no corpo do PR
- [ ] Descrição preenche: o que muda, por quê, como testar, screenshots (se UI), checklist

## Formato de saída obrigatório

```md
## Resultado
APTO | NÃO APTO — (motivo em 1 frase)

## Evidências
| Verificação | Comando | Resultado |
|-------------|---------|-----------|
| Backend | `python -m pytest -q` | 107 passed |
| Frontend | `npm test -- --watch=false` | 24 passed |
| Build | `npm run build` | ok |
| Migration | `alembic heads` | 1 head |

## Bloqueios
- (lista objetiva; vazio se apto)

## Não bloqueantes
- (lista curta)

## Próximo comando
- `git push -u origin <branch>` e abrir PR para `develop` (somente se APTO)
```

## Regras

- Não abra PR se houver bloqueio. Não "deixe para o reviewer".
- Não rode `git push --force`, `reset --hard` ou `clean -fd`.
- Não altere código nesta etapa; se precisar corrigir, volte ao prompt de build/fix.
- Se um comando não se aplica (ex.: frontend intocado), marque `não se aplica` em vez de omitir.
