# Design — Papéis de `main`/`develop` e processo de release

Data: 2026-11-24
Status: aprovado

## Intenção

Deixar explícito nos documentos que agentes e contribuidores leem (`AGENTS.md`,
`CONTRIBUTING.md`) que `main` é a versão estável em produção e `develop` é o ambiente de
desenvolvimento e teste, e que `main` só avança por release versionada. Hoje os dois arquivos
dizem apenas "`main` = estável", sem nenhuma regra de versão, tag ou hotfix. O objetivo é dar ao
projeto um histórico rastreável e um processo que pareça profissional para quem chega de fora.

## Objetivos

- Definir SemVer como padrão de versão (`X.Y.Z`) e a relação commit → tipo de bump.
- Definir o ritual de release: PR de release `develop → main`, tag anotada, GitHub Release.
- Definir o caminho de hotfix (produção quebrada) e o back-merge obrigatório para `develop`.
- Deixar claro que rollback de deploy não é rewind de git.
- Registrar as regras no `AGENTS.md` para que agentes não criem tag, não façam merge em `main`
  e não decidam número de versão por conta própria.

## Não-objetivos

- Não alterar o CI (`.github/workflows/`) nesta entrega.
- Não criar workflow automatizado de tag/release.
- Não adicionar `CHANGELOG.md` manual.
- Não sincronizar `frontend/package.json` nem expor versão em `/api/health`.
- Não alterar código de aplicação, testes ou migrations.

## Anti-objetivos (o que tornaria isso um fracasso)

- Regra escrita que ninguém consegue seguir porque falta permissão ou pessoa disponível.
- Duas fontes de verdade sobre versão (tag + arquivo que ninguém atualiza).
- Doc que repete o mesmo texto nos dois arquivos e depois divergem.

## Restrições

- `AGENTS.md` §1 define orçamento de contexto e §2 define quem manda em caso de conflito:
  `CONTRIBUTING.md` vence em processo, `AGENTS.md` vence em regra para agente. O texto novo deve
  respeitar essa divisão: processo detalhado em `CONTRIBUTING.md`, regra curta e imperativa em
  `AGENTS.md`.
- `AGENTS.md` §4.14 proíbe alterar `CONTRIBUTING.md` sem pedido explícito — este pedido cobre
  `CONTRIBUTING.md` e `AGENTS.md`.
- CI já roda em `develop` e `main`; nada precisa mudar para o processo funcionar.
- Existe uma única tag hoje: `v1.0.0`.

## Abordagens consideradas

| Abordagem | O que é | Trade-off |
|-----------|---------|-----------|
| **A — Release PR + SemVer derivado dos commits** (escolhida) | Número de versão é consequência dos commits mergeados na `develop`; release é um PR para `main` com 2 aprovações; tag anotada + GitHub Release com notas automáticas | Exige disciplina de Conventional Commits (já obrigatória) e cerimônia a cada release |
| B — Release manager rotativo | Uma pessoa decide o número e assina; 1 aprovação | Simples de escrever, mas o número vira julgamento humano e o processo depende de disponibilidade de uma pessoa |
| C — Tag a cada merge na `main`, número manual | Menos cerimônia | É praticamente o estado atual; não resolve rastreabilidade nem o aspecto profissional |

Escolha do usuário: **A**.

## Decisões

1. **SemVer `X.Y.Z`.** Bump derivado dos commits desde a última tag: só `fix`/`perf` → patch;
   algum `feat` → minor; breaking (`!` ou `BREAKING CHANGE`) → major. `docs`, `style`, `test`,
   `chore`, `refactor` sem mudança de comportamento não geram release por si sós.
2. **Ritual de release:** branch `release/vX.Y.Z` sai de `develop`; PR para `main` com título
   `release: vX.Y.Z`; 2 aprovações, nenhuma do autor; merge (sem squash, para preservar histórico);
   tag anotada `vX.Y.Z` na `main`; GitHub Release com notas geradas dos commits; back-merge da
   `main` para `develop`.
3. **Aprovações:** `develop` mantém 1 aprovação; PR de release para `main` exige 2. Só quem tem
   permissão de manutenção no repositório aprova release; contribuidor comum abre o PR e participa
   da discussão.
4. **Notas de release** geradas automaticamente pelo GitHub a partir dos commits. Sem
   `CHANGELOG.md` manual.
5. **Fonte única de versão:** a tag anotada. `frontend/package.json` e `/api/health` não são
   sincronizados nesta fase.
6. **Hotfix:** `hotfix/vX.Y.Z` sai da `main`, PR para `main` com o mesmo ritual de aprovação,
   tag patch, e back-merge obrigatório para `develop` (PR imediato, referenciando o PR da `main`).
7. **Rollback:** produzir incidente não autoriza reescrever histórico. Deploy volta para a tag
   anterior; a correção entra como novo patch. Reescrever tag publicada é proibido.
8. **Agentes:** não criam tag, não fazem merge em `main`, não decidem número de versão. Podem
   preparar o PR de release e o texto, sempre com confirmação humana.
9. **Escopo da entrega:** apenas `CONTRIBUTING.md` e `AGENTS.md`. Sem mudança de CI.

## O que fica para quem implementa

- Escolher a seção exata em `CONTRIBUTING.md` (provável seção nova "Modelo de Releases" após
  "Modelo de Branches", com entrada no índice) e o bloco equivalente em `AGENTS.md` (§4 e §9).
- Manter os dois textos sem duplicação: `CONTRIBUTING.md` descreve o fluxo; `AGENTS.md` descreve a
  proibição/obrigação para agentes e aponta para o `CONTRIBUTING.md`.
- Garantir consistência com o que já existe (`git switch -c`, base remota `origin/develop`, regra
  de 72 caracteres, Conventional Commits em português).
