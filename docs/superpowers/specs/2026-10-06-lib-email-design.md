# Biblioteca interna de e-mail do backend

## Objetivo

Centralizar todo o envio de e-mail do backend em uma biblioteca interna única, de modo que qualquer
parte do sistema que precise enviar e-mail chame essa biblioteca em vez de reimplementar o envio.
Hoje a lógica de e-mail existe em `backend/app/services/email_service.py` e está duplicada em várias
branches com versões divergentes. Esta mudança consolida a implementação em um pacote com fronteira
clara e uma interface de domínio estável.

## Contexto e motivação

O projeto usa e-mail transacional em duas funcionalidades:

- **Recuperação de senha** — `send_reset_email`, chamada por `backend/app/api/v1/auth.py`.
- **Primeiro acesso / criação de conta** — `send_first_access_email`, chamada por
  `backend/app/api/v1/usuarios.py`.

O arquivo `backend/app/services/email_service.py` evoluiu de formas diferentes em branches
distintas. A branch `feat/email-real-criacao-conta` adicionou envio real via API do Brevo, com
fallback para SMTP. A branch `feature/esqueci-minha-senha-envio-email` reforçou a validação do
token e o tratamento de erro. Nenhuma das duas consolida as demais.

Estado atual verificado: com `SMTP_USER` vazio e sem `BREVO_API_KEY`, nenhuma branch envia e-mail
de verdade. O código cai no fallback de log e registra o link no console (documentado em
`docs/architecture/features/RECUPERACAO_SENHA.md`, seção 8.1). Esta especificação também cria a
base para que o envio real funcione de ponta a ponta quando as credenciais forem configuradas.

## Escopo

### Dentro do escopo

- Criar o pacote interno `backend/app/email/` com interface de domínio.
- Suportar três provedores, selecionados por configuração: Brevo (API REST), SMTP e console (dev).
- Mover para a biblioteca a montagem das mensagens de reset de senha e de primeiro acesso.
- Migrar todos os chamadores para a nova biblioteca.
- Remover `backend/app/services/email_service.py`.
- Adaptar e ampliar os testes de e-mail.
- Adicionar as configurações novas (`BREVO_API_KEY`, `EMAIL_SENDER_NAME`) nos exemplos de ambiente
  e no `docker-compose.yml`.

### Fora do escopo

Os itens abaixo já estão documentados como problemas em `RECUPERACAO_SENHA.md` e não fazem parte
desta mudança:

- Persistência e uso único do token de recuperação (seção 8.3).
- Invalidação de sessões ativas na troca de senha (seção 8.4).
- Rate limit por conta e estado compartilhado do limiter (seção 8.7).
- `JWT_SECRET` obrigatório na subida (seção 8.6).
- Envio assíncrono ou por fila.
- Internacionalização das mensagens.

## Branch de trabalho

A implementação parte de `feature/esqueci-minha-senha-envio-email`, que já contém a validação
reforçada de token e os testes de fluxo de recuperação.

## Arquitetura

A biblioteca é um pacote Python dentro do backend, sem publicação externa. A estrutura é:

```
backend/app/email/
├── __init__.py        # API pública: send_reset_email, send_first_access_email, EmailDeliveryError
├── service.py         # seleção de provedor e núcleo de envio
├── messages.py        # montagem de assunto, corpo e links por domínio
├── exceptions.py      # EmailDeliveryError
└── providers/
    ├── __init__.py
    ├── brevo.py       # envio via API REST do Brevo
    ├── smtp.py        # envio via SMTP
    └── console.py     # fallback de desenvolvimento, registra link mascarado
```

Cada arquivo tem uma responsabilidade única:

- `providers/*` conhecem apenas `to`, `subject` e `body`. Não conhecem token, link nem regra de
  negócio. Toda configuração vem de `app.core.config.get_settings()`.
- `messages.py` monta assunto, corpo e link de cada funcionalidade. Não envia nada.
- `service.py` é o núcleo: escolhe o provedor e delega o envio.
- `exceptions.py` define o erro único de entrega.
- `__init__.py` é a única superfície pública. Chamadores importam daqui.

Os provedores são funções, não classes. Cada um expõe `send(to: str, subject: str, body: str) ->
None`. A seleção é por configuração, não há registry nem injeção de dependência. Para três
provedores fixos, classes e ABC adicionariam estrutura sem benefício.

## Interface pública

`backend/app/email/__init__.py` exporta:

```python
def send_reset_email(to_email: str, reset_token: str) -> None: ...
def send_first_access_email(to_email: str, first_access_token: str) -> None: ...
class EmailDeliveryError(Exception): ...
```

Os chamadores passam apenas e-mail e token. Assunto, corpo e montagem do link ficam dentro da
biblioteca. Nenhum chamador importa de `app.email.providers`, `app.email.service` ou
`app.email.messages` diretamente.

As assinaturas atuais são preservadas, o que torna a migração dos chamadores uma troca de import.

## Fluxo de envio

```
caller: send_reset_email(email, token)
  └─ messages.build_reset_message() -> (subject, body, link, label)
       └─ service._send_email(to, subject, body)
            └─ _select_provider() -> providers.<p>.send(to, subject, body)
```

`_select_provider()` escolhe, nesta ordem:

1. Se `brevo_api_key` está preenchido, usa Brevo.
2. Senão, se `smtp_user` está preenchido, usa SMTP.
3. Senão, usa console.

O fallback de console é o comportamento de desenvolvimento: registra o link com o token mascarado
(somente um prefixo), nunca o token completo. Isso substitui o log atual, que imprime o link
inteiro em texto puro.

## Configuração

Campos a adicionar em `backend/app/core/config.py`:

| Campo | Alias | Default | Uso |
|---|---|---|---|
| `brevo_api_key` | `BREVO_API_KEY`, `SENDINBLUE_API_KEY` | `""` | Habilita o provedor Brevo |
| `email_sender_name` | `EMAIL_SENDER_NAME` | `"SGA ABACO"` | Nome do remetente no Brevo |

Campos existentes reutilizados: `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`,
`smtp_from`, `frontend_url`, `reset_token_expire_minutes`, `first_access_token_expire_minutes`.

As duas variáveis novas também devem constar em `.env.example`, `backend/.env.example` e no bloco
de `environment` do `docker-compose.yml`, seguindo o padrão de repasse já existente para as demais
variáveis de e-mail.

## Tratamento de erro

Contrato da biblioteca:

- Cada provider levanta `EmailDeliveryError` em falha de entrega.
- `EmailDeliveryError` envolve a causa original: status HTTP do Brevo, `SMTPException`, `OSError`,
  timeout de conexão.
- O provedor de console nunca falha.
- A biblioteca não engole erro. `_send_email` e as funções de domínio propagam `EmailDeliveryError`.

Os chamadores decidem o comportamento:

- `api/v1/auth.py` (`forgot_password`): captura `EmailDeliveryError`, registra no log e devolve a
  resposta 200 genérica. Isso corrige a enumeração de contas descrita em `RECUPERACAO_SENHA.md`,
  seção 8.2, em que hoje uma falha de SMTP retorna 500 e distingue e-mail existente de inexistente.
- `api/v1/usuarios.py` (`create_usuarios`): captura `EmailDeliveryError`, registra um aviso e
  continua. A criação de usuário não é bloqueada por falha de e-mail, mantendo o comportamento
  atual.

O tratamento de cada chamador é explícito e coberto por teste.

## Mensagens

Duas mensagens, montadas em `messages.py`:

- Recuperação de senha: link `{frontend_url}/reset-password?token={token}`, assunto
  `SGA ABACO - Recuperação de Senha`, validade `reset_token_expire_minutes`.
- Primeiro acesso: link `{frontend_url}/first-access?token={token}`, assunto
  `SGA ABACO - Conta criada com sucesso`, validade `first_access_token_expire_minutes`.

O texto é o mesmo já existente nas branches atuais. Esta mudança não altera conteúdo, apenas a
localização do código.

## Testes

`backend/tests/test_email_service.py` é adaptado para exercitar a nova superfície. Cobertura
mínima:

- Seleção de provedor: apenas Brevo configurado usa Brevo; sem Brevo mas com `smtp_user` usa SMTP;
  sem nenhum usa console.
- Brevo: sucesso e resposta HTTP de erro produzem, respectivamente, envio e `EmailDeliveryError`
  (mock de `urllib`).
- SMTP: sucesso e `SMTPException` produzem, respectivamente, envio e `EmailDeliveryError` (mock de
  `smtplib`).
- Console: registra o link com token mascarado e não registra o token completo.
- Mensagens: os links de reset e de primeiro acesso são montados com o caminho e o token corretos.
- API: `forgot-password` responde 200 mesmo quando o envio falha; `create_usuarios` cria o usuário
  mesmo quando o envio falha.

Os testes existentes que consolidavam o comportamento de logar o link completo devem ser
substituídos pelos testes de mascaramento.

## Migração

1. Criar o pacote `backend/app/email/`.
2. Substituir os imports em `backend/app/api/v1/auth.py` e `backend/app/api/v1/usuarios.py` para
   `from app.email import ...`.
3. Remover `backend/app/services/email_service.py`.
4. Atualizar `.env.example`, `backend/.env.example` e `docker-compose.yml`.
5. Adaptar os testes.

Não haverá shim de compatibilidade. Como o módulo antigo é removido no mesmo commit, qualquer
import restante falha imediatamente e é corrigido na hora.

## Critérios de sucesso

- Todo envio de e-mail do backend passa pela biblioteca `app.email`.
- Nenhum arquivo fora de `app/email/` contém lógica de SMTP, Brevo ou montagem de mensagem.
- `backend/app/services/email_service.py` não existe mais.
- Com `BREVO_API_KEY` configurada, o envio ocorre pela API do Brevo; com `SMTP_USER` configurada,
  ocorre por SMTP; sem nenhum, o link é registrado com token mascarado.
- `forgot_password` responde 200 mesmo com falha de envio.
- A suíte de testes do backend passa, com a cobertura descrita acima.

## Riscos

- **Regressão na enumeração de contas.** A mudança de 500 para 200 em `forgot_password` altera o
  contrato observável do endpoint. Mitigação: teste de API que afirma o status 200 sob falha.
- **Diferença de comportamento entre branches.** As branches divergem na ordem dos provedores e nos
  assuntos. A biblioteca adota a ordem Brevo → SMTP → console e o assunto de primeiro acesso
  "Conta criada com sucesso". Mitigação: mensagens e ordem fixadas nesta especificação.
- **Credenciais ausentes em produção.** A biblioteca não impede a subida sem provedor. A falha
  visível de configuração continua fora de escopo.
