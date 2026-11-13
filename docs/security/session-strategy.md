# Estratégia de sessão e revogação

Documento de referência para o endurecimento de autenticação da issue #50
(`BUG-28` da varredura de 2026-11-11).

## Modelo de sessão

- O login (`POST /api/v1/auth/login`) emite um JWT de acesso e o entrega em dois formatos:
  - corpo da resposta (`access_token`), para clientes de API e testes de integração;
  - cookie `abaco_session`, usado pelo frontend Angular.
- O cookie de sessão é `HttpOnly`, `SameSite=Lax` e `Secure` quando `APP_ENV=production`.
  O frontend não lê nem persiste o JWT; ele guarda apenas metadados não sensíveis
  (`abaco_session` no `localStorage`: id do usuário, cargo, papel, expiração e flag de primeiro acesso).
- Requisições do frontend usam `withCredentials`, então o navegador envia o cookie automaticamente.
- O backend aceita `Authorization: Bearer <token>` para clientes programáticos. Nesse caso não há CSRF,
  pois o token não é enviado automaticamente pelo navegador.

## CSRF

- O login também define o cookie `abaco_csrf` (legível por JavaScript).
- Requisições autenticadas por cookie com método `POST`, `PUT`, `PATCH` ou `DELETE` precisam enviar
  o header `X-CSRF-Token` com o mesmo valor do cookie (double-submit).
- Requisições `GET`, `HEAD` e `OPTIONS` não exigem o header.
- O interceptor `session.interceptor.ts` copia o cookie para o header automaticamente.
- O backend valida antes de executar qualquer endpoint que use `verify_cargo` ou `get_current_user`.

## Revogação

- Todo token emitido no login contém `jti`, `iat` e o claim `ver` (versão da sessão do usuário).
- A coluna `usuario.tokenversion` é incrementada em:
  - logout (`POST /api/v1/auth/logout`);
  - troca de senha (`POST /api/v1/auth/change-password`);
  - redefinição de senha (`POST /api/v1/auth/reset-password`);
  - definição de senha no primeiro acesso (`POST /api/v1/auth/first-access`).
- Para tokens com `ver`, o backend confere no banco se o usuário existe, se a versão confere e se o
  cargo atual ainda é o mesmo. Caso contrário responde `401`.
- Logout invalida todas as sessões do usuário (revogação global), não apenas o dispositivo atual.
- Tokens antigos, emitidos antes desta mudança e sem `ver`, continuam válidos até expirar
  (no máximo `ACCESS_TOKEN_EXPIRE_MINUTES`). Após esse período, todo token passa pela checagem.

## Produção

- Com `APP_ENV=production` (ou `ENVIRONMENT=production`), o backend falha no startup se
  `SECRET_KEY`/`JWT_SECRET` estiver ausente, for o default de desenvolvimento ou tiver menos de
  32 caracteres.
- Em produção o cookie de sessão usa `Secure` por padrão. `SESSION_COOKIE_SECURE` permite
  sobrescrever quando o TLS é terminado em um proxy.
- O frontend e a API devem estar no mesmo site (mesmo host ou subdomínios do mesmo site), pois o
  cookie é `SameSite=Lax`. O `docker-compose` já publica a API via proxy Nginx no mesmo host.

## CORS

- Origens permitidas continuam vindo de `CORS_ORIGINS`.
- Métodos permitidos: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`.
- Headers permitidos: `Authorization`, `Content-Type`, `X-CSRF-Token`.
- `allow_credentials=True` exige origens explícitas (não há `*`).

## Cobertura de testes

- `backend/tests/test_session_hardening.py`
  - startup de produção sem segredo forte;
  - CORS restrito;
  - cookie `HttpOnly` + CSRF legível;
  - autenticação por cookie e bloqueio sem `X-CSRF-Token`;
  - logout invalidando o token e incremento de versão invalidando tokens antigos;
  - claims `jti`, `iat` e `ver`.
- `frontend/src/app/core/services/auth.service.spec.ts`
  - login não persiste o JWT;
  - logout revoga no servidor e limpa metadados;
  - expiração e restauração da sessão.
- `frontend/src/app/core/interceptors/session.interceptor.spec.ts`
  - `withCredentials` e envio de `X-CSRF-Token`.

## Limitações conhecidas

- A revogação é global por usuário; não há lista de sessões individuais por dispositivo.
- Tokens legados sem `ver` permanecem válidos até a expiração natural.
- O cookie CSRF exige que o frontend consiga ler cookies do domínio da API; por isso a API deve
  compartilhar o mesmo site do frontend.
