---
description: Executa o gate final antes do PR seguindo docs/agents/prompts/pre-pr.md
---

Siga `docs/agents/prompts/pre-pr.md`.

Verifique sincronização com a base remota (`upstream/develop` em fork, `origin/develop` em clone
direto), escopo do diff, testes de backend e frontend, build, migrations, segredos e mensagem de
commit. Não implemente código nesta etapa. Reporte APTO ou NÃO APTO.
