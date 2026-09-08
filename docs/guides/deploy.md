# Guia de Deploy — SGA ABACO

## Pré-requisitos

- Docker 24+ e Docker Compose v2
- Git
- Domínio configurado (para produção)

---

## 1. Deploy rápido (desenvolvimento)

```bash
git clone https://github.com/LucaS4nt0s/ABACO_Sistema.git
cd ABACO_Sistema
cp .env.example .env
docker compose up --build
```

Acessos:
- **Aplicação**: http://localhost:3000
- **API/Swagger**: http://localhost:8000/docs

---

## 2. Deploy em produção

### 2.1 Configurar `.env`

```bash
cp .env.example .env
```

Edite `.env` com valores reais:

```ini
# Database
POSTGRES_DB=sga_abacos
POSTGRES_USER=abaco_prod
POSTGRES_PASSWORD=<SENHA_FORTE>
DATABASE_URL=postgresql+psycopg2://abaco_prod:<SENHA_FORTE>@database:5432/sga_abacos

# JWT — use um segredo forte (ex: openssl rand -hex 32)
JWT_SECRET=<SEGREDO_JWT_64_CHARS>
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Admin seed — criado automaticamente no primeiro boot
ADMIN_SEED_EMAIL=admin@abaco.org.br
ADMIN_SEED_PASSWORD=<SENHA_ADMIN>

# SMTP — configure para enviar emails de recuperação
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=<SENHA_APP_GMAIL>
SMTP_FROM=noreply@abaco.org.br

# Frontend URL (domínio da aplicação)
FRONTEND_URL=https://sga.abaco.org.br

# CORS — origens permitidas (separadas por vírgula)
CORS_ORIGINS=https://sga.abaco.org.br,https://api.abaco.org.br

# Rate limiting
RATE_LIMIT_AUTH=5/minute
RATE_LIMIT_DEFAULT=60/minute

# Backend
PORT=8000
```

### 2.2 Subir a aplicação

```bash
docker compose up --build -d
```

### 2.3 Verificar saúde

```bash
curl http://localhost:8000/api/health
# {"status":"ok","database":"connected"}
```

---

## 3. Com Nginx reverse proxy

Exemplo de configuração para domínio próprio:

```nginx
server {
    listen 443 ssl;
    server_name sga.abaco.org.br;

    ssl_certificate     /etc/letsencrypt/live/sga.abaco.org.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sga.abaco.org.br/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 4. Backup do banco

```bash
# Backup
docker exec sga_database pg_dump -U postgres sga_abacos > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i sga_database psql -U postgres sga_abacos < backup_20260621.sql
```

---

## 5. Atualização

```bash
git pull origin dev
docker compose up --build -d
```

As migrations Alembic rodam automaticamente no startup do backend.

---

## 6. Troubleshooting

| Problema | Solução |
|----------|---------|
| Banco não sobe | Verifique se `database-schema.sql` existe (não é uma pasta vazia) |
| Backend não conecta ao banco | Confirme `DATABASE_URL` no `.env` |
| Emails não chegam | Sem SMTP configurado, links aparecem no log do container: `docker logs sga_backend` |
| CORS bloqueado | Adicione o domínio em `CORS_ORIGINS` no `.env` |
| Rate limit atingido | Aumente `RATE_LIMIT_AUTH` no `.env` |

---

## Portas

| Serviço | Porta |
|---------|-------|
| Frontend (Nginx) | 3000 |
| Backend (FastAPI) | 8000 |
| PostgreSQL | 5432 |
