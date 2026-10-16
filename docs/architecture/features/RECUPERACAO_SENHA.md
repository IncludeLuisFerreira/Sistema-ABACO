# Recuperação de Senha — Documentação Técnica

**Projeto:** SGA ABACO
**Escopo:** Funcionalidade "Esqueci minha senha" (recuperação de senha por e-mail)
**Data da análise:** 29/09/2026
**Base analisada:** commit `0b53759` — `feat(auth): primeiro acesso por e-mail e troca obrigatória de senha (#12)`
**Versão analisada:** 0a53759 com container `sga_backend` em execução

---

## 1. Visão Geral

A recuperação de senha é composta por dois endpoints REST no backend FastAPI e duas páginas
standalone no frontend Angular. O usuário informa o e-mail, o sistema envia um link por SMTP, e
o link leva a uma página onde a nova senha é definida.

O fluxo é **stateless**: o link de recuperação carrega um JWT assinado com o e-mail do usuário.
Nada é persistido no banco de dados em nenhum momento do processo. Não existe tabela de tokens,
nem registro de uso, nem revogação.

```
Login ──> forgot-password ──> [e-mail] ──> reset-password ──> Login
           (formulário)         (link JWT)     (nova senha)
```

### Estado atual verificado

O fluxo **está quebrado em produção e desenvolvimento**. Nenhum e-mail é enviado. Os detalhes
estão na seção 8.1, com o procedimento de reprodução.

---

## 2. Arquivos Envolvidos

### Backend

| Arquivo | Papel |
|---|---|
| `backend/app/api/v1/auth.py` | Rotas HTTP, rate limit e tradução de exceções |
| `backend/app/schemas/auth_schema.py` | Validação de entrada com Pydantic |
| `backend/app/services/auth_service.py` | Regras de negócio (busca, geração, troca) |
| `backend/app/services/email_service.py` | Montagem e envio do e-mail via SMTP |
| `backend/app/core/security.py` | Geração e decodificação dos tokens JWT |
| `backend/app/core/config.py` | Configuração por variável de ambiente |
| `backend/app/core/limiter.py` | Instância do rate limiter |
| `backend/app/models/usuario.py` | Modelo da tabela `usuario` |
| `backend/main.py` | Registro dos routers na aplicação |

### Frontend

| Arquivo | Papel |
|---|---|
| `frontend/src/app/app.routes.ts` | Rotas Angular `forgot-password` e `reset-password` |
| `frontend/src/app/features/auth/pages/login/login.html` | Link "Esqueci minha senha?" |
| `frontend/src/app/features/auth/pages/forgot-password/forgot-password.ts` | Componente do formulário de e-mail |
| `frontend/src/app/features/auth/pages/forgot-password/forgot-password.html` | Template do formulário |
| `frontend/src/app/features/auth/pages/forgot-password/forgot-password.scss` | Estilos da página |
| `frontend/src/app/features/auth/pages/reset-password/reset-password.ts` | Componente de definição de senha |
| `frontend/src/app/features/auth/pages/reset-password/reset-password.html` | Template da nova senha |
| `frontend/src/app/features/auth/pages/reset-password/reset-password.scss` | Estilos da página |
| `frontend/src/app/core/services/auth.service.ts` | Cliente HTTP e sessão |

### Testes

| Arquivo | Cobertura |
|---|---|
| `backend/tests/test_auth_service.py` | Regras de negócio |
| `backend/tests/test_auth_schema.py` | Validação de entrada |
| `backend/tests/test_email_service.py` | Envio de e-mail |
| `backend/tests/test_security.py` | Tokens |
| `frontend/src/app/core/services/auth.service.spec.ts` | Cliente HTTP |

---

## 3. Endpoints

### 3.1 `POST /api/v1/auth/forgot-password`

Solicita o envio do link de recuperação.

**Rate limit:** 3 requisições por minuto, por endereço IP.

**Request:**

```json
{
  "email": "usuario@abaco.org.br"
}
```

**Response 200:**

```json
{
  "message": "Se o e-mail estiver cadastrado, um link de recuperação será enviado"
}
```

A mesma mensagem é devolvida exista o e-mail ou não. A intenção é impedir enumeração de contas.

**Response 500:**

```json
{
  "detail": "Erro ao enviar e-mail de recuperação. Tente novamente mais tarde."
}
```

Ocorre quando o e-mail existe mas o envio SMTP falha. Ver seção 8.2 — este status vaza
informação.

**Implementação:** `backend/app/api/v1/auth.py:55-71`

### 3.2 `POST /api/v1/auth/reset-password`

Define a nova senha.

**Rate limit:** 5 requisições por minuto, por endereço IP.

**Request:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "nova_senha": "NovaSenha1",
  "confirmar_senha": "NovaSenha1"
}
```

**Response 200:**

```json
{
  "message": "Senha redefinida com sucesso. Você já pode fazer login com a nova senha."
}
```

**Responses de erro:**

| Status | `detail` | Causa |
|---|---|---|
| 400 | `Token inválido ou expirado` | Token malformado, expirado, de outro tipo, ou usuário inexistente |
| 422 | `As senhas não conferem` | Divergência entre os dois campos |
| 422 | *(body do Pydantic)* | Senha abaixo de 8 caracteres ou sem letra e número |

**Implementação:** `backend/app/api/v1/auth.py:74-92`

### 3.3 Endpoints relacionados

| Endpoint | Rate limit | Observação |
|---|---|---|
| `POST /api/v1/auth/login` | 5/min | 5/min está hardcoded, ignora `RATE_LIMIT_AUTH` |
| `POST /api/v1/auth/first-access` | 5/min | Fluxo irmão, mesmo padrão de token e e-mail |
| `POST /api/v1/auth/change-password` | 5/min | Exige `Authorization: Bearer` e senha atual |

---

## 4. Fluxo Detalhado

### Etapa 1 — Solicitação

O usuário está em `/login` e clica em "Esqueci minha senha?"
(`frontend/src/app/features/auth/pages/login/login.html:55`).

O router navega para `/forgot-password`
(`frontend/src/app/app.routes.ts:10-13`).

O componente `ForgotPassword` monta um formulário com um único campo `email`, validado por
`Validators.required` e `Validators.email`
(`frontend/src/app/features/auth/pages/forgot-password/forgot-password.ts:24-27`).

Ao submeter, o componente desabilita o formulário, chama `AuthService.forgotPassword(email)` e
trata o retorno. Sucesso exibe a mensagem do servidor. Erro exibe o `detail` e dispara uma
animação de tremor no cartão
(`forgot-password.ts:29-58`).

A chamada HTTP é feita em
`frontend/src/app/core/services/auth.service.ts:130-137`.

O backend valida o formato do e-mail com `EmailStr`
(`backend/app/schemas/auth_schema.py:14-15`), aplica o rate limit e chama
`process_forgot_password`.

### Etapa 2 — Geração e envio do token

`process_forgot_password` (`backend/app/services/auth_service.py:71-77`):

1. Busca o usuário por e-mail com `.first()`
2. Se não existir, levanta `EmailNotFoundError`
3. Se existir, gera o token e o devolve

O token é criado em `create_reset_token`
(`backend/app/core/security.py:31-35`):

```python
payload = {"sub": email, "type": "password_reset", "exp": expire}
```

| Claim | Valor | Uso |
|---|---|---|
| `sub` | e-mail do usuário | Identifica quem vai ter a senha trocada |
| `type` | `password_reset` | Impede que o token sirva para outro fluxo |
| `exp` | 15 minutos no futuro | Limita a janela de uso |

Assinado com `HS256` usando `SECRET_KEY`. **O token carrega apenas o e-mail.** Não há
`id_usuario`, `jti`, `iat`, nem versão da senha.

De volta ao router: se o e-mail não existir, devolve 200 com a mensagem genérica e encerra. Se
existe, chama `send_reset_email`.

`send_reset_email` (`backend/app/services/email_service.py:39-65`):

1. Monta o link `{FRONTEND_URL}/reset-password?token={token}`
2. Se `SMTP_USER` estiver vazio, **registra o link no log e retorna sem enviar**
3. Caso contrário, envia por SMTP

O envio usa `MIMEMultipart` com corpo `text/plain`. Para porta 465 usa `SMTP_SSL`; para outras,
`SMTP` com `starttls()`. A autenticação só é tentada se usuário e senha estiverem preenchidos.

### Etapa 3 — Definição da nova senha

O usuário recebe o e-mail com assunto "SGA ABACO - Recuperação de Senha" e clica no link. Isso
abre `/reset-password?token=...`, resolvido em
`frontend/src/app/app.routes.ts:14-17`.

`ResetPassword.ngOnInit` lê o token da query string
(`frontend/src/app/features/auth/pages/reset-password/reset-password.ts:32-37`). Sem token,
define o erro "Token de recuperação não encontrado" e o template renderiza um bloco
alternativo em vez do formulário
(`reset-password.html:22-24`), bloqueando a interação.

Com token, o formulário pede a senha duas vezes. Os validadores do cliente exigem mínimo de 8
caracteres e o padrão letra-mais-número, aplicado apenas à `nova_senha`
(`reset-password.ts:27-28`). A igualdade entre os campos é verificada no `onSubmit`
(`reset-password.ts:46-49`).

A chamada HTTP é feita em
`frontend/src/app/core/services/auth.service.ts:139-146`.

### Etapa 4 — Troca no banco

O router valida a igualdade das senhas novamente
(`backend/app/api/v1/auth.py:78-82`) e chama `process_reset_password`.

`process_reset_password` (`backend/app/services/auth_service.py:80-98`):

1. Valida igualdade das senhas
2. Decodifica o token com `decode_reset_token`
3. Confirma que `type == "password_reset"`
4. Extrai o e-mail do claim `sub`
5. Busca o usuário por esse e-mail
6. Gera novo hash com bcrypt e grava em `usuario.senha_hash`
7. Faz `db.commit()`

**Nada mais é alterado.** O token não é invalidado. Nenhuma sessão é encerrada. Nenhum registro
é criado.

**Importante:** o campo `primeiro_acesso` **não** é alterado por este fluxo. Ele só é limpo por
`first-access` e `change-password`. Um usuário que nunca definiu senha e usa a recuperação de
senha continua com `primeiro_acesso = true` e será forçado a trocar a senha novamente após o
login.

No frontend, o sucesso exibe "Senha redefinida com sucesso! Redirecionando para o login..." e
após 2,5 segundos navega para `/login`
(`reset-password.ts:60-62`).

---

## 5. Validações e Regras

### 5.1 Regra de senha

**Definição:** `SENHA_PATTERN` em `backend/app/schemas/auth_schema.py:6`

```python
SENHA_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")
```

Exige ao menos uma letra e ao menos um dígito. O comprimento mínimo de 8 é definido
separadamente em `PasswordPairRequest` (`auth_schema.py:18-19`).

**Onde é validada — quatro camadas:**

| Camada | Arquivo | O que faz |
|---|---|---|
| Cliente | `reset-password.ts:27-28` | `minLength(8)` e `pattern` na `nova_senha` |
| Schema | `auth_schema.py:22-28` | `model_validator` confere igualdade e padrão |
| Router | `auth.py:78-82` | Recompara igualdade, retorna 422 |
| Serviço | `auth_service.py:81-82` | Recompara igualdade, levanta exceção |

A igualdade é checada quatro vezes. O router tem um comentário
`# REFACTOR: checagem de senhas duplicada (schema + service + router)` em
`auth.py:77` reconhecendo a redundância.

### 5.2 Regras não implementadas

Nenhuma das siguientes existe no fluxo de recuperação:

- Comparação com a senha atual
- Bloqueio de senhas comuns ou de dicionário
- Verificação contra e-mail ou nome do usuário
- Histórico que impeça reutilização
- Comprimento máximo
- Notificação ao titular quando a senha é alterada
- Registro de auditoria

### 5.3 Hash

`hash_password` (`backend/app/core/security.py:17-18`) usa `bcrypt.hashpw` com
`bcrypt.gensalt()` — salt aleatório por senha, custo padrão da biblioteca.

---

## 6. Configuração

### 6.1 Variáveis de ambiente

Definidas em `backend/app/core/config.py` e passadas ao container por `docker-compose.yml:31-46`.

| Variável | Default | Uso |
|---|---|---|
| `JWT_SECRET` | `development_secret_change_me` | Assina e valida todos os tokens |
| `RESET_TOKEN_EXPIRE_MINUTES` | `30` | Validade do link de recuperação |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | Validade da sessão |
| `SMTP_HOST` | `localhost` | Servidor SMTP |
| `SMTP_PORT` | `587` | Porta SMTP (465 ativa SSL) |
| `SMTP_USER` | vazio | **Ausência desativa todo o envio** |
| `SMTP_PASSWORD` | vazio | Senha SMTP |
| `SMTP_FROM` | `noreply@abaco.org.br` | Remetente |
| `FRONTEND_URL` | `http://localhost:3000` | Prefixo do link no e-mail |
| `RATE_LIMIT_AUTH` | `5/minute` | **Ignorado no código**, ver 8.7 |

### 6.2 Estado atual verificado

Leitura do arquivo `.env` na raiz e verificação dentro do container `sga_backend`:

| Variável | Valor atual | Avaliação |
|---|---|---|
| `JWT_SECRET` | preenchido, 64 caracteres | Correto |
| `RESET_TOKEN_EXPIRE_MINUTES` | `15` no container inspecionado | Defina `30` ao recriar o container para aplicar o prazo atualizado |
| `SMTP_HOST` | `localhost` | Inválido em container — ver 8.1 |
| `SMTP_PORT` | `587` | Inválido em container — ver 8.1 |
| `SMTP_USER` | **vazio** | Desativa o envio |
| `SMTP_PASSWORD` | **vazio** | — |
| `FRONTEND_URL` | `http://localhost:3000` | Aceitável em dev, inválido em produção |

A configuração de infraestrutura está pronta: o `docker-compose.yml` repassa corretamente as
quatro variáveis SMTP. O que falta é um provedor real configurado.

---

## 7. Testes Existentes

### 7.1 Backend

**`backend/tests/test_auth_service.py`**

| Teste | Linha | Cobre |
|---|---|---|
| `test_generates_token_for_existing_user` | 50 | Token gerado para e-mail existente |
| `test_raises_for_unknown_email` | 55 | `EmailNotFoundError` para e-mail inexistente |
| `test_resets_password_with_valid_token` | 61 | Hash muda após reset |
| `test_passwords_dont_match` | 68 | Divergência levanta exceção |
| `test_invalid_token_raises` | 73 | Token inválido levanta exceção |

**`backend/tests/test_email_service.py`**

| Teste | Linha | Cobre |
|---|---|---|
| `test_logs_link_when_smtp_not_configured` | 99 | Comportamento de fallback para log |

O teste de fallback **consolida o comportamento problemático**: ele assegura que o token
continue sendo escrito no log. Se a funcionalidade for corrigida, este teste precisa mudar.

**`backend/tests/test_auth_schema.py`** — validação de `ForgotPasswordRequest` e
`ResetPasswordRequest` (linhas 27 e 37).

**`backend/tests/test_security.py:33`** — garante que token de reset é rejeitado pelo
decodificador de acesso.

### 7.2 Frontend

**`frontend/src/app/core/services/auth.service.spec.ts`**

| Teste | Linha | Cobre |
|---|---|---|
| `forgotPassword sends email` | 48 | Corpo da requisição |
| `resetPassword sends token and new password` | 56 | Corpo da requisição |

### 7.3 Lacunas de cobertura

Nenhum teste cobre:

- **Comportamento HTTP dos dois endpoints.** `test_api_endpoints.py` cobre apenas `/login`.
  `test_auth_first_access_api.py` cobre os endpoints de primeiro acesso e troca de senha, mas
  não os de recuperação.
- **O status 500 do SMTP** e seu efeito sobre a enumeração de contas.
- **A mensagem anti-enumeração** — nenhum teste assegura que e-mail existente e inexistente
  produzam respostas indistinguíveis.
- **O rate limit** dos endpoints de recuperação.
- **Reuso de token** — não há teste que verifique se um token continua válido após o uso.
- **Persistência de sessão após reset** — não há teste que verifique se sessões antigas sobrevivem.
- **Os componentes `ForgotPassword` e `ResetPassword`.** Não existem arquivos `.spec.ts` para
  as duas páginas, apesar de haver specs para `login` e para os guards.

---

## 8. Problemas Identificados

Ordenados por severidade.

### 8.1 Crítico — Nenhum e-mail é enviado

**Arquivos:** `backend/app/services/email_service.py:44-47`, `.env`, `docker-compose.yml:40-44`

Quando `SMTP_USER` está vazio, `send_reset_email` registra o link no log e retorna normalmente.
O endpoint responde 200 com a mensagem genérica de sucesso. O usuário fica esperando um e-mail
que nunca chega, sem nenhuma indicação de que algo deu errado.

Configuração verificada no container `sga_backend`:

```
SMTP_HOST=[localhost]
SMTP_PORT=[587]
SMTP_USER=[]
SMTP_PASSWORD=[]
```

Não existe serviço SMTP no `docker-compose.yml` — os serviços são `database`, `backend` e
`frontend`. Nenhuma porta SMTP está escutando.

**Reprodução:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@abaco.org.br"}'
```

Resposta:

```json
{"message":"Se o e-mail estiver cadastrado, um link de recuperação será enviado"}
```

Log do container:

```
INFO:app.services.email_service:SMTP não configurado. Link de recuperação para
admin@abaco.org.br: http://localhost:3000/reset-password?token=eyJhbGciOiJIUzI1NiIs...
```

O token aparece em texto puro. Quem tem acesso aos logs consegue completar o fluxo, dentro da
janela de 15 minutos.

**Este mesmo defeito afeta o fluxo de primeiro acesso.**
`send_first_access_email` (`email_service.py:73-76`) tem a mesma condição, com FIXMEs próprios
em `email_service.py:45` e `email_service.py:74`.

**Observação sobre a porta 631.** Existe um processo escutando na porta 631 do host, que é CUPS
e não SMTP. O `SMTP_HOST=localhost` padrão, somado à ausência de `SMTP_USER`, faz com que o
caminho de envio nunca seja exercitado.

### 8.2 Crítico — O status HTTP 500 permite enumerar contas

**Arquivo:** `backend/app/api/v1/auth.py:60-69`

O tratamento de exceções é assimétrico:

```python
try:
    token = process_forgot_password(db, payload.email)
except EmailNotFoundError:
    return {"message": "Se o e-mail estiver cadastrado, ..."}   # 200

try:
    send_reset_email(payload.email, token)
except Exception:
    raise HTTPException(status_code=500, ...)                    # 500
```

E-mail inexistente retorna 200. E-mail existente com SMTP quebrado retorna 500. A resposta
distingue os dois casos de forma inequívoca.

Basta um servidor SMTP configurado e com credencial errada, expirada ou indisponível para que a
base inteira de usuários possa ser enumerada por um terceiro que observe apenas os códigos de
status.

O `except Exception` também descarta a causa raiz. `_send_via_smtp` faz log do erro em
`email_service.py:35` e re-lança, mas o router converte tudo em 500 sem registrar contexto. Não
é possível distinguir falha de DNS, de TLS ou de autenticação pela resposta.

### 8.3 Crítico — O token não é invalidado após o uso

**Arquivos:** `backend/app/core/security.py:31-35`, `backend/app/services/auth_service.py:80-98`

O token é um JWT sem registro no banco. Não há `jti`, nem tabela de tokens usados, nem lista de
revogação. `process_reset_password` apenas sobrescreve `senha_hash`.

Consequência: o link permanece válido por 15 minutos **mesmo depois de a senha já ter sido
trocada**. Se o link vazar depois do uso — por histórico de navegador, log de proxy, print, ou
encaminhamento do e-mail — ele ainda permite trocar a senha novamente.

O token também pode ser reutilizado indefinidamente dentro da janela, e não há verificação de
uso único.

### 8.4 Crítico — A troca de senha não encerra sessões ativas

**Arquivo:** `backend/app/core/dependencies.py:46-48`

```python
def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    # TODO: confia só no token; não consulta o banco
    return decode_access_token(_extract_token(authorization))
```

A autenticação confia apenas no JWT e nunca consulta o banco. Se a conta estava comprometida e o
atacante já possui um token de acesso, **trocar a senha não expulsa o atacante**. O token dele
continua válido por até 120 minutos, o valor de `ACCESS_TOKEN_EXPIRE_MINUTES`.

Não existe claims de versão de senha no token de acesso, nem comparação com um valor no banco
que indicasse que a credencial mudou.

### 8.5 Alto — O token trafega na URL

**Arquivos:** `backend/app/services/email_service.py:42`, `frontend/.../reset-password.ts:33`

O link é montado com o token em query string:

```python
reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
```

O token é exposto em:

- Histórico do navegador
- Logs de acesso do servidor web e do frontend
- Header `Referer`, se a página carregar qualquer recurso externo
- Logs de proxy e CDN
- Prints e encaminhamentos do e-mail

Para mitigar o problema, o token deveria ser um código curto de uso único, entregue fora de banda, e
trocado por uma sessão pelo backend. Não deve estar na URL.

### 8.6 Alto — `SECRET_KEY` tem default utilizável

**Arquivo:** `backend/app/core/config.py:19-23`

```python
secret_key: str = Field(
    default="development_secret_change_me",
    validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET"),
)
```

O código já carrega `# FIXME: SECRET_KEY default insegura permite forjar tokens JWT se não
definida`.

Neste ambiente não há impacto: o `.env` define `JWT_SECRET` com 64 caracteres. Mas qualquer
implantação que esqueça a variável permite forjar um token `password_reset` para qualquer
e-mail e assumir a conta. Como o token carrega apenas o e-mail, não existe segundo fator.

O risco se agrava com `RESET_TOKEN_EXPIRE_MINUTES`: um valor alto amplia a janela.

### 8.7 Alto — Rate limit por IP, in-memory e por conta inexistente

**Arquivos:** `backend/app/core/limiter.py:1-5`, `backend/app/api/v1/auth.py:56,75`

```python
limiter = Limiter(key_func=get_remote_address)
```

Três problemas combinados:

**Por IP, não por conta.** O limite protege a origem da requisição, não a conta alvo. Um
atacante distribuído em vários endereços não tem restrição alguma sobre uma conta específica e
pode disparar pedidos de envio indefinidamente, sem limite de cota por e-mail.

**Colisão em rede compartilhada.** Usuários atrás do mesmo endereço de saída — escritório, VPN,
carrier NAT — compartilham a mesma cota. Com 3 por minuto no `forgot-password`, uma organização
com dezenas de pessoas no mesmo gateway se bloqueia coletivamente. O rate limit vira negação de
serviço contra usuários legítimos.

**In-memory.** O `Limiter` do slowapi armazena o estado em memória do processo. Com múltiplos
workers do uvicorn ou múltiplos réplicas, a cota efetiva é multiplicada pelo número de processos.
O próprio `TODO` em `limiter.py:4` registra isso. O `docker-compose.yml` usa um worker único,
o que mascara o problema hoje.

### 8.8 Alto — Canal de tempo na resposta anti-enumeração

**Arquivo:** `backend/app/api/v1/auth.py:57-71`

Com SMTP funcional, a mensagem é idêntica nos dois casos, mas o caminho do e-mail existente faz
uma ida à rede antes de responder, enquanto o inexistente retorna imediatamente. A diferença de
latência é suficiente para distinguir os casos por medição.

Somado a 8.2, a proteção anti-enumeração tem dois canais de escape.

### 8.9 Médio — Política de senha insuficiente

**Arquivos:** `backend/app/schemas/auth_schema.py:6,18-28`, `backend/app/services/auth_service.py:97`

A regra aceita senhas triviais. `abcdefg1`, `1111111a` e `joaosilva2` passam todas.

Não há bloqueio de senha comum, verificação contra dados do usuário, histórico que impeça
reutilização, nem comprimento máximo. `process_reset_password` grava o hash diretamente, sem
comparar com a senha anterior e sem verificar o estado da conta.

### 8.10 Médio — Sem notificação e sem auditoria

Não existe aviso de "sua senha foi alterada" enviado ao titular, nem entrada de auditoria. O
sistema não registra quem solicitou o reset, de qual IP, em que horário, nem quem aplicou a nova
senha. Numa investigação de incidente não há rastro do caminho.

O e-mail enviado contém a frase "Se você não solicitou esta recuperação, ignore este e-mail",
mas essa é a única pista, e ela está no lado do usuário, não do servidor.

### 8.11 Médio — Nenhum teste de API para os dois endpoints

`test_api_endpoints.py` cobre apenas `/login` e endpoints protegidos. Os endpoints de recuperação
não têm teste HTTP.

A regressão de maior probabilidade neste código é alguém mexer no tratamento de erro do SMTP e
abrir a enumeração de contas descrita em 8.2, sem que nenhum teste falhe. O teste que existe
para o serviço e o schema não exercita a camada onde o problema está.

### 8.12 Baixo — `primeiro_acesso` não é limpo no reset

**Arquivos:** `backend/app/services/auth_service.py:97`, `backend/app/models/usuario.py:16-18`

O campo só é alterado por `process_first_access_password` e por `change_password`. O fluxo de
recuperação não mexe nele.

Um usuário sem senha definida que use a recuperação continua com `primeiro_acesso = true` e é
forçado a trocar a senha de novo após o login, sem contexto — ele acabou de definir uma senha.

### 8.13 Baixo — `FRONTEND_URL` padrão é localhost

**Arquivo:** `backend/app/core/config.py:33`

O default `http://localhost:3000` produz links inúteis se a variável não for sobrescrita em
produção. Não há validação de ambiente que exija um valor absoluto de produção.

---

## 9. Sugestões de Melhorias

### Prioridade 1 — Corrigir o envio de e-mail

Sem isso a funcionalidade não existe. Sem isso o restante é teórico.

1. **Configurar SMTP real.** Preencher `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER` e `SMTP_PASSWORD`
   no `.env` de produção, apontando para um provedor transacional. Adicionar serviço de captura
   de e-mail no `docker-compose.yml` para desenvolvimento — Mailpit ou MailHog —, com a
   diferença de que a configuração local tenha `SMTP_USER` preenchido para exercitar o caminho
   real.
2. **Falhar de forma visível quando SMTP não está configurado.** Substituir o `logger.info`
   silencioso por um aviso de inicialização e, em ambiente não-local, tratar a ausência de SMTP
   como erro de configuração na subida da aplicação. O endpoint pode continuar devolvendo a
   mensagem genérica, mas a aplicação não deveria subir silenciosamente sem e-mail.
3. **Remover o token do log.** Substituir o `logger.info` que imprime o link completo por uma
   mensagem que indique apenas o e-mail e o token mascarado, ou nada. A atualização de
   `test_email_service.py:99` acompanha essa mudança.

### Prioridade 2 — Fechar a enumeração de contas

4. **Tratar falha de SMTP sem diferenciar o caso.** No `auth.py:63-69`, o envio de e-mail deve
   ocorrer fora do caminho de resposta, ou o erro deve ser registrado e mascarado sob o mesmo 200
   genérico. A opção mais limpa é enfileirar o envio e responder sempre 200, o que também resolve
   o item 8.8.
5. **Normalizar o tempo de resposta.** Se o envio permanecer síncrono, introduzir um atraso
   fixo antes de responder no caso de e-mail inexistente, para igualar a latência.
6. **Adicionar teste de API que cubra a paridade.** Requisitar e-mail existente e inexistente e
   afirmar que status, corpo e tempo são indistinguíveis. Este teste é o que impede a regressão.

### Prioridade 3 — Corrigir o modelo de token

7. **Persistir o token de recuperação.** Criar tabela com hash do token, `id_usuario`,
   `expira_em`, `usado_em` e `ip_origem`. Marcar como consumido na primeira uso, em transação
   única com a troca da senha. Isso resolve 8.3 e habilita revogação e auditoria.
8. **Mover o token para fora da URL.** O link deve conter um código curto e opaco, ou nenhum
   identificador. O código é enviado em um campo POST e trocado por uma sessão de uso único.
   Resolve 8.5.
9. **Invalidar sessões ativas na troca de senha.** Adicionar claim de versão de senha no token de
   acesso e comparar com o valor no banco em `get_current_user`. Isso exige que a autenticação
   passe a consultar o banco, o que também corrige o `TODO` em `dependencies.py:47` — usuário
   excluído hoje continua autenticado. Resolve 8.4.
10. **Exigir `JWT_SECRET` na subida.** Remover o default de `development_secret_change_me` e
    falhar no startup se a variável não estiver definida em ambiente não-local. Resolve 8.6.

### Prioridade 4 — Rate limit adequado

11. **Aplicar limite por conta além do limite por IP.** Chavear por e-mail normalizado no
    `forgot-password`, com limite mais alto e janela maior que o limite por IP. Os dois se
    complementam: o por IP protege a infraestrutura, o por conta protege a vítima.
12. **Mover o estado do limiter para armazenamento compartilhado** quando houver mais de um
    processo. Resolver o `TODO` em `limiter.py:4`.
13. **Aplicar `RATE_LIMIT_AUTH` no código.** Hoje o valor é lido do ambiente e ignorado, com
    `# HACK` em `auth.py:37`.

### Prioridade 5 — Política de senha

14. **Usar o `PasswordPairRequest` com validação em camada única.** Remover as três
    verificações duplicadas de igualdade, resolvendo o `REFACTOR` em `auth.py:77`.
15. **Ampliar a regra de senha.** Comprimento mínimo de 12, verificação contra lista de senhas
    comuns, e rejeição quando a senha contiver o e-mail ou o nome do usuário.
16. **Impedir reutilização** da senha anterior imediata.

### Prioridade 6 — Auditoria e feedback

17. **Enviar notificação de segurança** ao titular quando a senha for alterada, informando data,
    origem aproximada e instrução para contatar o suporte se não reconhecer.
18. **Criar registro de auditoria** para pedido de reset e aplicação de senha, com usuário, IP,
    horário e resultado.
19. **Limpar `primeiro_acesso` no fluxo de recuperação**, resolvendo 8.12.

### Prioridade 7 — Cobertura de teste

20. **Testes de API dos dois endpoints.** Cobrir: resposta genérica para e-mail existente e
    inexistente, comportamento sob falha de SMTP, validação de token expirado, token já usado,
    rate limit e rejeição de token de outro tipo.
21. **Teste de integração do fluxo completo**, do POST de solicitação até o login com a senha nova,
    com SMTP capturado.
22. **Specs dos componentes `ForgotPassword` e `ResetPassword`**, seguindo o padrão já usado em
    `login.spec.ts`.

---

## 10. Referências Rápidas

### Comandos úteis

```bash
# Testes do backend
cd backend && pytest tests/test_auth_service.py tests/test_email_service.py -v

# Reproduzir o problema de e-mail
curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@abaco.org.br"}'

# Ver o token vazando
docker logs sga_backend --since 5m 2>&1 | grep "SMTP não configurado"

# Estado do SMTP no container
docker exec sga_backend sh -c 'echo "[$SMTP_HOST]:[$SMTP_PORT] user=[$SMTP_USER]"'
```

### Termos de código relevantes

| Termo | Local | Significado |
|---|---|---|
| `process_forgot_password` | `auth_service.py:71` | Gera o token |
| `process_reset_password` | `auth_service.py:80` | Aplica a nova senha |
| `create_reset_token` | `security.py:31` | Assina o JWT de recuperação |
| `decode_reset_token` | `security.py:38` | Valida assinatura e `type` |
| `send_reset_email` | `email_service.py:39` | Monta e envia o e-mail |
| `senha_hash` | `usuario.py:14` | Onde o bcrypt é gravado |
| `primeiro_acesso` | `usuario.py:16` | Flag de troca obrigatória |

### Commits relacionados

```
0b53759  feat(auth): primeiro acesso por e-mail e troca obrigatória de senha (#12)
3a66427  chore: setup inicial do projeto
```

A funcionalidade de recuperação foi introduzida no commit `0b53759`.
