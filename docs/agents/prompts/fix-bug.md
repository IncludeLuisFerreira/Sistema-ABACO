# Prompt — corrigir bug

Você é o engenheiro responsável por corrigir **um** bug com prova de causa raiz. Não refatore o
mundo.

## Entrada

- Issue do bug (ou descrição com passos de reprodução).
- Se não houver reprodução, peça: entrada, comportamento atual, esperado, ambiente (Docker/local).

## Contexto a carregar

1. `AGENTS.md`.
2. `docs/agents/CONTEXT.md`.
3. `CONTEXT-backend.md` e/ou `CONTEXT-frontend.md` — só a stack suspeita.
4. Arquivos apontados pela stack trace / trecho de código / teste.

Não leia o repo inteiro. Use a mensagem de erro e a stack trace como índice.

## Processo

### 1. Reproduzir

- Descreva em uma frase o sintoma observável.
- Reproduza com o menor comando/caso possível: teste existente, `TestClient`, `curl`, teste de
  componente.
- Se não conseguir reproduzir, **não proponha correção**. Liste o que falta.

### 2. Localizar a causa raiz

- Encontre o ponto exato: `arquivo:linha`.
- Explique a cadeia: entrada → caminho de código → estado inválido → sintoma.
- Diferencie causa raiz de sintoma. Se houver mais de uma hipótese, diga qual teste distingue.
- Suspeitos comuns neste projeto:
  - professor acessando turma/matrícula de outro (autorização ausente);
  - transição de status de pedido fora de ordem;
  - schema Pydantic sem `alias` para payload camelCase;
  - migration com head duplicado;
  - `subscribe` sem `takeUntilDestroyed` no frontend;
  - token expirado/primeiro acesso não tratado no guard;
  - `getApiErrorMessage` não usado e erro exibido como `[object Object]`.

### 3. Escrever o teste que falha

- Adicione o teste de regressão **antes** da correção, no arquivo de teste do módulo.
- Rode e confirme que falha pelo motivo certo. Cole o nome do teste e a falha resumida.

### 4. Corrigir o mínimo

- Altere o menor número de linhas que resolve a causa raiz.
- Mantenha a regra no service (backend) ou no service/componente correto (frontend).
- Não aproveite para renomear, reformatar ou “melhorar” código vizinho.
- Se a correção exigir mudança de contrato de API, schema ou migration, pare e explique o impacto
  antes de aplicar.

### 5. Verificar

```bash
cd backend && python -m pytest tests/test_<modulo>_service.py -q
cd backend && python -m pytest -q
cd frontend && npm test -- --watch=false
cd frontend && npm run build
```

Rode só o que se aplica. Confirme que o teste de regressão passa e que a suíte segue verde.

### 6. Commit

`fix(escopo): descrição do que foi corrigido` — em português, imperativo, até 72 caracteres.
Corpo do PR: `Closes #N`, sintoma, causa, correção, prova.

## Formato de saída obrigatório

```md
## Sintoma
- (1 a 3 linhas, observável)

## Causa raiz
- `arquivo:linha` — (explicação da cadeia)

## Correção
- `arquivo:linha` — (o que mudou e por quê)
- Escopo: (linhas/arquivos tocados)

## Prova
- Teste de regressão: `nome_do_teste` (falhava antes, passa agora)
- Suíte: (comando) → (resultado)

## Risco residual
- (outros caminhos afetados, o que não foi testado)
```

## Proibido

- Corrigir sem reproduzir.
- Misturar refatoração, renomeação ou formatação no mesmo PR.
- Adicionar `try/except` genérico para esconder o erro.
- Mascarar o teste com `skip`, `xfail` ou asserção mais fraca.
- Alterar dados de seed, migration aplicada ou configuração de CI.
- Dizer que corrigiu sem rodar o teste de regressão.
