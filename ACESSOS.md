# Acessos e Dados de Teste — SGA ABACO

## Logins

| Cargo | Email | Senha |
|-------|-------|-------|
| **Diretora** | admin@abaco.org.br | `ADMIN_SEED_PASSWORD` (padrão `admin123`) |
| **Admin** | admin2@abaco.org.br | `SEED_ADMIN_PASSWORD` (padrão `admin123`) |
| **Professora** | maria@abaco.org.br | `SEED_PROFESSOR_PASSWORD` (padrão `prof12345`) |
| **Professor** | joao@abaco.org.br | `SEED_PROFESSOR_PASSWORD` (padrão `prof12345`) |
| **Professora** | ana@abaco.org.br | `SEED_PROFESSOR_PASSWORD` (padrão `prof12345`) |
| **Professor** | paulo@abaco.org.br | `SEED_PROFESSOR_PASSWORD` (padrão `prof12345`) |

> As senhas vêm do `.env` (veja `.env.example`). Sem `SEED_ADMIN_PASSWORD`/`SEED_PROFESSOR_PASSWORD`,
> `admin2` e os professores não são criados — e sem professor não há turmas, matrículas nem pedidos
> de teste. O primeiro diretor (`admin@abaco.org.br`) depende de `ADMIN_SEED_EMAIL`/`ADMIN_SEED_PASSWORD`.
> O seed é idempotente e pode ser rodado avulso: `docker compose exec backend python -m app.db.seed`.

> Para criar um Administrativo (cargo 3), a Diretora pode cadastrar via `/admin/usuarios`.

---

## Dados populados (seed automático)

### Cursos
| Nome |
|------|
| Informática Básica |
| Corte e Costura |
| Administração |
| Inglês Básico |
| Espanhol |

### Turmas
| # | Curso | Professor | Capacidade | Período | Dias | Avaliações | Alunos |
|---|-------|-----------|-----------|---------|------|------------|--------|
| 1 | Informática Básica | Maria Silva | 20 vagas | 01/06 a 30/09 | Seg/Qua/Sex | Prova 1 + Prova 2 + Trabalho Final | 3 |
| 2 | Informática Básica | Maria Silva | 25 vagas | 01/08 a 15/12 | Ter/Qui | Prova 1 + Prova 2 | 2 |
| 3 | Corte e Costura | João Santos | 15 vagas | 01/05 a 30/08 | Seg/Qua/Sex | Prova Única + Trabalho Prático | 2 |
| 4 | Administração | Ana Costa | 30 vagas | 01/07 a 30/10 | Ter/Qui/Sáb | 4 Provas | 2 |
| 5 | Inglês Básico | João Santos | 18 vagas | 15/06 a 15/12 | Ter/Qui | Listening + Speaking + Written Test | 2 |
| 6 | Espanhol | Paulo Lima | 12 vagas | 01/08 a 30/11 | Seg/Qua | Prova Oral + Prova Escrita | 2 |

### Alunos (12)
Pedro, Carla, Lucas, Juliana, Rafael, Beatriz, Gabriel, Mariana, Fernando, Patrícia, Ricardo, Tatiane

### Pedidos de material (3)
| # | Professor | Status | Itens |
|---|-----------|--------|-------|
| 1 | Maria Silva | Solicitado | Caneta (50), Caderno (30) |
| 2 | João Santos | Aprovado | Lápis (40), Tesoura (15) |
| 3 | Ana Costa | Comprado | Papel sulfite (8 resmas) |

### Matrículas (12)
Distribuídas entre as 6 turmas.

### Estoque
| Item | Disponível | Mínimo | Alerta? |
|------|-----------|--------|---------|
| Caneta esferográfica | 200 un | 50 | Não |
| Caderno universitário | 80 un | 20 | Não |
| **Lápis HB** | **5 un** | 30 | **🔴 Sim** |
| Borracha branca | 60 un | 15 | Não |
| Papel sulfite A4 | 12 resmas | 5 | Não |
| **Tesoura escolar** | **3 un** | 10 | **🔴 Sim** |

---

## Como testar

1. **Diretora**: loga com `admin@abaco.org.br` / senha definida em `ADMIN_SEED_PASSWORD`
   - Vê o dashboard na home com KPIs e gráficos
   - Acessa Turmas → vê os cards agrupados por curso
   - Gerencia alunos, matrículas, usuários
   - Aprova pedidos, vê estoque crítico

2. **Professor**: loga com `maria@abaco.org.br` / senha definida em `SEED_PROFESSOR_PASSWORD`
   - Vê dashboard do professor
   - Acessa "Minhas Turmas" → vê 2 turmas de Informática
   - Registra presenças e notas

3. **Email de recuperação**: ao usar "Esqueci minha senha", o link aparece no log do container:
   ```bash
   docker logs sga_backend | grep ABACO
   ```
