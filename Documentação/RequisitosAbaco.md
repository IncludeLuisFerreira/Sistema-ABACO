# DOCUMENTO DE REQUISITOS — SGA ABACO

**Sistema de Gestão Acadêmica da Associação ABACO**

---

## 1. Introdução

Este documento descreve os requisitos do sistema SGA ABACO (Sistema de Gestão Acadêmica), desenvolvido para a Associação ABACO — uma ONG que oferece cursos profissionalizantes gratuitos para a comunidade.

O sistema tem como objetivo digitalizar os processos acadêmicos, logísticos e administrativos da organização, eliminando o controle manual que gerava atrasos e dificuldades na gestão.

---

## 2. Descrição Geral do Sistema

O SGA ABACO é uma plataforma web com três módulos principais:

- **Módulo Acadêmico**: gestão de alunos, cursos, turmas, matrículas, notas, presenças e históricos
- **Módulo Logístico**: gestão de pedidos de materiais e controle de estoque
- **Módulo Administrativo**: gestão de usuários, permissões e dashboards gerenciais

### 2.1 Arquitetura

- **Frontend**: Angular 21 (Standalone Components)
- **Backend**: FastAPI (Python 3.14+)
- **Banco de Dados**: PostgreSQL
- **Autenticação**: JWT com bcrypt
- **Containerização**: Docker / Docker Compose

### 2.2 Atores do Sistema

| Ator | Cargo | Descrição |
|------|-------|-----------|
| **Diretor(a)** | cargo = 1 | Acesso total ao sistema, incluindo dashboards, gestão de usuários e aprovação de pedidos |
| **Professor(a)** | cargo = 2 | Acesso ao módulo acadêmico restrito às suas turmas: notas, presenças, pedidos |
| **Admin/Operacional** | cargo = 3 | Acesso a alunos, cursos, turmas, matrículas, estoque e pedidos (exceto dashboards e gestão de usuários) |

---

## 3. Requisitos Funcionais

### 3.1 Módulo de Autenticação

| ID | Requisito | Prioridade | Atores |
|----|-----------|------------|--------|
| RF001 | Realizar login com e-mail e senha | Essencial | Todos |
| RF002 | Recuperar senha (enviar e-mail com token) | Essencial | Todos |
| RF003 | Redefinir senha com token válido | Essencial | Todos |
| RF004 | Rate limiting (5 tentativas/min no login, 3/min no forgot-password) | Importante | Sistema |

### 3.2 Módulo Acadêmico

| ID | Requisito | Prioridade | Atores |
|----|-----------|------------|--------|
| RF005 | Cadastrar aluno | Essencial | Diretor, Admin |
| RF006 | Editar aluno | Essencial | Diretor, Admin |
| RF007 | Excluir aluno (somente sem matrículas vinculadas) | Importante | Diretor, Admin |
| RF008 | Visualizar aluno | Essencial | Diretor, Admin, Professor |
| RF009 | Cadastrar curso | Essencial | Diretor, Admin |
| RF010 | Editar curso | Essencial | Diretor, Admin |
| RF011 | Excluir curso (somente sem turmas vinculadas) | Importante | Diretor, Admin |
| RF012 | Visualizar curso | Essencial | Diretor, Admin, Professor |
| RF013 | Criar turma (com curso, professor, capacidade, datas, dias de aula e avaliações configuráveis) | Essencial | Diretor, Admin |
| RF014 | Editar turma | Essencial | Diretor, Admin |
| RF015 | Excluir turma (somente sem matrículas ou pedidos vinculados) | Importante | Diretor, Admin |
| RF016 | Visualizar turma | Essencial | Diretor, Admin, Professor |
| RF017 | Visualizar minhas turmas (professor vê apenas suas turmas) | Essencial | Professor |
| RF018 | Realizar matrícula de aluno em turma (com validação de lotação e duplicidade) | Essencial | Diretor, Admin |
| RF019 | Editar matrícula | Essencial | Diretor, Admin |
| RF020 | Cancelar/Concluir matrícula via alteração de status | Importante | Diretor, Admin |
| RF021 | Excluir matrícula (somente sem notas ou presenças vinculadas) | Importante | Diretor, Admin |
| RF022 | Visualizar matrícula | Essencial | Diretor, Admin, Professor |
| RF023 | Visualizar minhas matrículas (professor vê apenas matrículas de suas turmas) | Essencial | Professor |
| RF024 | Lançar/editar notas em lote por turma e prova | Essencial | Diretor, Admin, Professor |
| RF025 | Visualizar notas por matrícula | Essencial | Diretor, Admin, Professor |
| RF026 | Visualizar notas por turma (com filtro opcional por prova) | Essencial | Diretor, Admin, Professor |
| RF027 | Calcular e visualizar média por prova de uma turma | Essencial | Diretor, Admin, Professor |
| RF028 | Registrar/editar presenças em lote por turma e data | Essencial | Diretor, Admin, Professor |
| RF029 | Visualizar presenças por turma (com filtro opcional por data) | Essencial | Diretor, Admin, Professor |
| RF030 | Gerar histórico acadêmico completo (dados do aluno, turma, notas por prova, presenças com percentual de frequência) | Essencial | Diretor, Admin |
| RF031 | Exportar histórico acadêmico em PDF | Desejável | Diretor, Admin |

### 3.3 Módulo Logístico

| ID | Requisito | Prioridade | Atores |
|----|-----------|------------|--------|
| RF032 | Cadastrar item no estoque | Essencial | Diretor, Admin |
| RF033 | Editar item do estoque | Essencial | Diretor, Admin |
| RF034 | Excluir item do estoque (somente sem pedidos vinculados) | Importante | Diretor, Admin |
| RF035 | Visualizar estoque | Essencial | Todos |
| RF036 | Pesquisar itens no estoque por nome | Essencial | Todos |
| RF037 | Dar baixa manual no estoque (com quantidade e justificativa) | Essencial | Diretor, Admin |
| RF038 | Visualizar alertas de estoque mínimo | Essencial | Todos |
| RF039 | Criar pedido de materiais (com itens, quantidade e turma destino) | Essencial | Todos |
| RF040 | Visualizar pedidos | Essencial | Todos |
| RF041 | Aprovar pedido (transição: Solicitado -> Aprovado) | Essencial | Diretor |
| RF042 | Confirmar compra de pedido (transição: Aprovado -> Comprado) | Essencial | Diretor |
| RF043 | Entregar pedido (transição: Comprado -> Entregue), adicionando itens ao estoque | Essencial | Diretor |
| RF044 | Atualizar status do pedido | Essencial | Diretor |
| RF045 | Excluir pedido | Importante | Diretor, Admin |
| RF046 | Registrar movimentação de estoque automaticamente (ao aprovar pedido ou dar baixa manual) | Essencial | Sistema |

### 3.4 Módulo Administrativo

| ID | Requisito | Prioridade | Atores |
|----|-----------|------------|--------|
| RF047 | Cadastrar usuário do sistema (nome, e-mail, senha, cargo) | Essencial | Diretor |
| RF048 | Editar usuário | Essencial | Diretor |
| RF049 | Excluir usuário (não pode auto-excluir-se) | Importante | Diretor |
| RF050 | Visualizar usuários | Essencial | Diretor |
| RF051 | Visualizar dashboard com KPIs (total de alunos ativos, turmas vigentes, pedidos pendentes, estoque crítico) | Essencial | Diretor |
| RF052 | Visualizar gráficos acadêmicos (alunos por curso, status das matrículas) | Essencial | Diretor |
| RF053 | Visualizar gráficos logísticos (consumo de itens no mês atual) | Essencial | Diretor |

---

## 4. Requisitos Não Funcionais

| ID | Requisito | Prioridade | Descrição |
|----|-----------|------------|-----------|
| NF001 | Usabilidade | Essencial | Interface intuitiva, responsiva e acessível |
| NF002 | Desempenho | Importante | Resposta da API em até 3 segundos para operações comuns |
| NF003 | Segurança | Essencial | Autenticação JWT, senhas hasheadas com bcrypt, controle de acesso por cargo (RBAC) |
| NF004 | Disponibilidade | Importante | 95% de uptime, deploys via Docker |
| NF005 | Confiabilidade | Essencial | Backup automático do banco de dados |
| NF006 | Rate Limiting | Importante | Limite de requisições em endpoints de autenticação para prevenir brute force |
| NF007 | Auditoria | Importante | Registro de movimentações de estoque com data, tipo e justificativa |

---

## 5. Regras de Negócio

### 5.1 Matrícula

- Um aluno pode ter múltiplas matrículas, porém **não pode ter duas matrículas ativas no mesmo curso** (mesmo que em turmas diferentes)
- Uma turma **não pode exceder sua capacidade** de alunos com matrículas ativas
- Status da matrícula:
  - `0` = Ativa
  - `1` = Concluída
  - `2` = Cancelada
- Não é possível excluir uma matrícula que possua notas ou presenças vinculadas

### 5.2 Turma

- Uma turma pertence a um curso e pode ter um professor responsável
- Uma turma pode ter **avaliações configuráveis** (nome, tipo: prova/trabalho, peso) armazenadas em JSON
- Dias de aula armazenados como texto (ex: "Segunda, Quarta, Sexta")
- A propriedade `vagasOcupadas` é calculada dinamicamente com base nas matrículas ativas
- Não é possível excluir uma turma que possua matrículas ou pedidos vinculados

### 5.3 Nota

- As notas são lançadas **em lote** por turma e número de prova
- Cada aluno pode ter múltiplas provas/avaliações
- Se já existir nota para a mesma matrícula + prova, ela é **atualizada**; senão, é **criada**
- A média por prova é calculada automaticamente agregando todos os alunos da turma

### 5.4 Presença

- As presenças são registradas **em lote** por turma e data
- Se já existir registro para a mesma matrícula + data, ele é **atualizado**; senão, é **criado**
- Presença: `true` = presente, `false` = ausente
- O percentual de frequência é calculado como (total de presenças / total de aulas) * 100

### 5.5 Pedido

- O pedido segue o fluxo de status:
  - `0` = Solicitado
  - `1` = Aprovado
  - `2` = Comprado
  - `3` = Entregue
- **Transições válidas**: 0→1, 1→2, 2→3 (não é possível pular etapas ou retroceder)
- **Ao aprovar** (0→1): o sistema deduz as quantidades do estoque automaticamente
- **Ao comprar** (1→2): o sistema permite ajustar as quantidades compradas
- **Ao entregar** (2→3): o sistema adiciona os itens ao estoque (ou cria novos itens se não existirem)

### 5.6 Estoque

- Cada item possui: nome, quantidade disponível, unidade e estoque mínimo
- O sistema emite **alerta** quando `quantidadeDisponivel <= estoqueMinimo`
- Ao dar baixa manual, é obrigatório informar quantidade e justificativa
- Não é possível dar baixa em quantidade superior ao saldo disponível
- Itens com nomes duplicados (case-insensitive) não são permitidos

### 5.7 Usuário

- Cargos:
  - `1` = Diretor(a) — acesso total
  - `2` = Professor(a) — acesso acadêmico restrito
  - `3` = Admin — acesso operacional (não vê dashboards nem gerencia usuários)
- Não é possível excluir o próprio usuário
- O e-mail deve ser único no sistema

### 5.8 Autenticação

- Senha deve conter pelo menos 8 caracteres, uma letra e um número
- Token JWT expira conforme configuração (padrão: 30 minutos)
- Token de reset de senha expira conforme configuração (padrão: 30 minutos)
- Rate limiting: 5 requisições/minuto no login, 3/minuto no forgot-password

---

## 6. Fluxo de Navegação (Rotas)

### 6.1 Acesso Público
```
/login
/forgot-password
/reset-password
```

### 6.2 Área do Professor (cargo = 2)
```
/academico
/academico/turmas
/academico/turmas/:id
/academico/alunos
/academico/presencas
/academico/notas
/academico/pedidos/novo
/academico/pedidos
```

### 6.3 Área Administrativa (cargos = 1, 3)
```
/admin/home
/admin/alunos
/admin/cursos
/admin/turmas
/admin/matriculas
/admin/presencas
/admin/notas
/admin/notas/aluno/:id
/admin/historico/matricula/:id
/admin/logistico
/admin/logistico/estoque
/admin/logistico/pedidos
/admin/logistico/pedidos/novo
```

### 6.4 Exclusivo Diretor (cargo = 1)
```
/admin/usuarios
/admin/dashboard (redirect para /admin/home com KPIs e gráficos)
```

---

## 7. Critérios de Aceite

O sistema será considerado pronto quando:

- [ ] Matrículas puderem ser realizadas com validação de lotação e duplicidade
- [ ] Presenças puderem ser registradas em lote por turma e data
- [ ] Notas puderem ser lançadas e médias calculadas por turma
- [ ] Pedidos puderem ser criados, aprovados, comprados e entregues
- [ ] Estoque puder ser gerenciado com alertas de estoque mínimo
- [ ] Dashboards com KPIs e gráficos estiverem disponíveis para a Diretoria
- [ ] Histórico acadêmico com notas, presenças e frequência puder ser gerado
- [ ] Autenticação com controle de acesso por cargo (RBAC) estiver funcionando
- [ ] Recuperação de senha por e-mail estiver operacional
