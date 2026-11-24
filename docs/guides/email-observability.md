# Observabilidade do envio de e-mails

Este guia descreve como acompanhar falhas de envio no fluxo de recuperação de senha
(`POST /api/v1/auth/forgot-password`).

## Comportamento do usuário

A resposta do `forgot-password` continua sendo **200 com a mesma mensagem** para e-mail
cadastrado, não cadastrado e quando o provedor falha com `EmailDeliveryError`. A mensagem genérica
é intencional: evita enumeração de contas. Falhas inesperadas (não previstas como
`EmailDeliveryError`) continuam retornando 500, comportamento legado.

## Log operacional

Cada falha de entrega (`EmailDeliveryError`) gera um log de nível `ERROR` no logger
`app.api.v1.auth`:

```text
password_reset_email_failed error_type=EmailDeliveryError consecutive_failures=1
```

O log não contém e-mail, token nem corpo da mensagem. A recomendação é alertar em qualquer
ocorrência do evento `password_reset_email_failed` (ou a partir de um limiar definido pela
operação).

Falhas inesperadas também são contabilizadas (`last_failure_type=UnexpectedError`) e continuam
gerando `logger.exception`, mas o usuário recebe 500 nesse caminho.

## Health check

```bash
curl http://localhost:8000/api/health/email
```

- **200** com `status=ok` quando não há falha recente e há provedor configurado (ou o ambiente
  não é produção).
- **503** com `status=degraded` quando a última falha ocorreu dentro de
  `EMAIL_HEALTH_FAILURE_WINDOW_MINUTES` (padrão: 15) ou quando `APP_ENV=production` e nenhum
  provedor Brevo/SMTP está configurado.

O health não fica degradado para sempre: uma falha antiga deixa de manter o 503 depois da janela,
mesmo sem novo envio. Para alerta durável, use o log `password_reset_email_failed`.

Exemplo de resposta degradada:

```json
{
  "status": "degraded",
  "provider": "brevo",
  "password_reset": {
    "attempts": 4,
    "failures": 1,
    "consecutive_failures": 1,
    "last_failure_at": "2026-11-22T17:00:00+00:00",
    "last_failure_type": "EmailDeliveryError"
  }
}
```

Campos:

| Campo | Significado |
|---|---|
| `status` | `ok` ou `degraded` |
| `provider` | Provedor selecionado: `brevo`, `smtp` ou `console` |
| `attempts` | Pedidos de recuperação para e-mail cadastrado que chegaram a tentar o envio |
| `failures` | Falhas de envio acumuladas desde o start do processo |
| `consecutive_failures` | Falhas desde o último envio sem exceção; zera no próximo sucesso |
| `last_failure_at` | Data/hora UTC da última falha |
| `last_failure_type` | Classe da exceção (`EmailDeliveryError` ou `UnexpectedError`) |

Os contadores não incluem e-mail, token ou qualquer dado pessoal.

## Limitações

- Os contadores são **em memória e por processo**: reiniciam no restart e não são agregados entre
  workers ou réplicas. Para alerta durável, use o log; para múltiplos processos, consulte cada um
  ou agregue os logs.
- O fallback de console (quando não há Brevo nem SMTP configurado) registra a mensagem e retorna
  sem exceção; para a métrica, ele não conta como falha. Em produção, o health fica `degraded`
  enquanto o provedor for `console`; em desenvolvimento, ele permanece `ok`.
- O health check observa exceções do provedor e a configuração do provedor, não a taxa de entrega
  final na caixa de entrada do destinatário.

## Como validar localmente

```bash
cd backend
python -m pytest tests/test_api_endpoints.py -q
curl -i http://localhost:8000/api/health/email
```
