# DIAGRAMA DE CASO DE USO — SGA ABACO

**Descrição textual dos casos de uso para elaboração do diagrama UML**

---

## 1. Atores do Sistema

| Ator | Descrição |
|------|-----------|
| **Diretor(a)** | Usuário com cargo = 1. Acesso total ao sistema. Pode gerenciar usuários, visualizar dashboards, aprovar/comprar/entregar pedidos e executar todas as operações acadêmicas e logísticas. |
| **Professor(a)** | Usuário com cargo = 2. Acesso restrito ao módulo acadêmico. Visualiza apenas suas próprias turmas e matrículas. Pode lançar notas, registrar presenças e criar pedidos de materiais. |
| **Admin** | Usuário com cargo = 3. Acesso operacional. Gerencia alunos, cursos, turmas, matrículas, estoque e pedidos. Não acessa dashboards nem gerencia usuários. |
| **Visitante** | Usuário não autenticado. Pode apenas realizar login ou recuperar senha. |

---

## 2. Casos de Uso por Módulo

### 2.1 Módulo de Autenticação

| Caso de Uso | Ator Primário | Descrição | Fluxo |
|-------------|---------------|-----------|-------|
| **UC01 - Realizar Login** | Visitante | O usuário informa e-mail e senha para acessar o sistema | 1. Informa e-mail e senha<br>2. Sistema valida credenciais<br>3. Sistema retorna token JWT<br>4. Redireciona conforme o cargo |
| **UC02 - Recuperar Senha** | Visitante | O usuário solicita redefinição de senha | 1. Informa e-mail<br>2. Sistema gera token de reset<br>3. Sistema envia e-mail com link<br>4. Usuário acessa link e redefine a senha |
| **UC03 - Redefinir Senha** | Visitante | O usuário redefine a senha usando token válido | 1. Informa token, nova senha e confirmação<br>2. Sistema valida token<br>3. Sistema atualiza a senha |

### 2.2 Módulo Acadêmico — Gerenciamento de Alunos

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC04 - Cadastrar Aluno** | Diretor, Admin | Incluir novo aluno com nome, telefone, data de nascimento, endereço |
| **UC05 - Editar Aluno** | Diretor, Admin | Alterar dados cadastrais de um aluno existente |
| **UC06 - Excluir Aluno** | Diretor, Admin | Remover aluno (somente se não tiver matrículas vinculadas) |
| **UC07 - Visualizar Aluno** | Diretor, Admin, Professor | Consultar dados de um aluno específico |
| **UC08 - Listar Alunos** | Diretor, Admin, Professor | Visualizar relação de todos os alunos cadastrados |

### 2.3 Módulo Acadêmico — Gerenciamento de Cursos

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC09 - Cadastrar Curso** | Diretor, Admin | Incluir novo curso com nome |
| **UC10 - Editar Curso** | Diretor, Admin | Alterar nome do curso |
| **UC11 - Excluir Curso** | Diretor, Admin | Remover curso (somente se não tiver turmas vinculadas) |
| **UC12 - Visualizar Curso** | Diretor, Admin, Professor | Consultar dados de um curso |
| **UC13 - Listar Cursos** | Diretor, Admin, Professor | Visualizar todos os cursos cadastrados |

### 2.4 Módulo Acadêmico — Gerenciamento de Turmas

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC14 - Criar Turma** | Diretor, Admin | Criar turma informando curso, professor, capacidade, datas, dias de aula e avaliações |
| **UC15 - Editar Turma** | Diretor, Admin | Alterar dados da turma |
| **UC16 - Excluir Turma** | Diretor, Admin | Remover turma (somente sem matrículas ou pedidos vinculados) |
| **UC17 - Visualizar Turma** | Diretor, Admin, Professor | Consultar dados da turma com curso e professor |
| **UC18 - Listar Turmas** | Diretor, Admin, Professor | Visualizar todas as turmas |
| **UC19 - Listar Minhas Turmas** | Professor | Visualizar apenas as turmas onde o professor logado é responsável |

### 2.5 Módulo Acadêmico — Gerenciamento de Matrículas

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC20 - Realizar Matrícula** | Diretor, Admin | Matricular aluno em turma (valida lotação e duplicidade no curso) |
| **UC21 - Editar Matrícula** | Diretor, Admin | Alterar dados da matrícula (aluno, turma, status) |
| **UC22 - Excluir Matrícula** | Diretor, Admin | Remover matrícula (somente sem notas ou presenças vinculadas) |
| **UC23 - Visualizar Matrícula** | Diretor, Admin, Professor | Consultar dados da matrícula |
| **UC24 - Listar Matrículas** | Diretor, Admin, Professor | Visualizar todas as matrículas |
| **UC25 - Listar Minhas Matrículas** | Professor | Visualizar matrículas apenas das suas turmas |

### 2.6 Módulo Acadêmico — Notas

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC26 - Lançar Notas** | Diretor, Admin, Professor | Lançar ou editar notas em lote por turma e número de prova |
| **UC27 - Visualizar Notas por Turma** | Diretor, Admin, Professor | Consultar notas de todos os alunos de uma turma (com filtro opcional por prova) |
| **UC28 - Visualizar Notas por Matrícula** | Diretor, Admin, Professor | Consultar notas de um aluno específico |
| **UC29 - Visualizar Média por Prova** | Diretor, Admin, Professor | Calcular e exibir a média da turma em cada prova |

### 2.7 Módulo Acadêmico — Presenças

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC30 - Registrar Presenças** | Diretor, Admin, Professor | Registrar ou editar presenças em lote por turma e data |
| **UC31 - Visualizar Presenças por Turma** | Diretor, Admin, Professor | Consultar presenças de uma turma (com filtro opcional por data) |

### 2.8 Módulo Acadêmico — Histórico

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC32 - Gerar Histórico Escolar** | Diretor, Admin | Visualizar histórico completo: dados do aluno, turma, curso, professor, notas por prova, presenças por data e percentual de frequência |
| **UC33 - Exportar Histórico em PDF** | Diretor, Admin | Gerar arquivo PDF do histórico escolar |

### 2.9 Módulo Logístico — Estoque

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC34 - Cadastrar Item no Estoque** | Diretor, Admin | Adicionar novo item (nome, quantidade, unidade, estoque mínimo) |
| **UC35 - Editar Item do Estoque** | Diretor, Admin | Alterar dados do item |
| **UC36 - Excluir Item do Estoque** | Diretor, Admin | Remover item (somente sem pedidos vinculados) |
| **UC37 - Listar Estoque** | Diretor, Admin, Professor | Visualizar todos os itens do estoque |
| **UC38 - Pesquisar Item no Estoque** | Diretor, Admin, Professor | Buscar itens por nome |
| **UC39 - Dar Baixa no Estoque** | Diretor, Admin | Registrar saída manual de item (quantidade + justificativa) |
| **UC40 - Visualizar Alertas de Estoque** | Diretor, Admin, Professor | Listar itens com quantidade abaixo do estoque mínimo |

### 2.10 Módulo Logístico — Pedidos

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC41 - Criar Pedido de Materiais** | Diretor, Admin, Professor | Solicitar materiais informando turma e itens (nome, quantidade, item de estoque opcional) |
| **UC42 - Listar Pedidos** | Diretor, Admin, Professor | Visualizar todos os pedidos |
| **UC43 - Visualizar Pedido** | Diretor, Admin, Professor | Consultar detalhes de um pedido |
| **UC44 - Aprovar Pedido** | Diretor | Aprovar pedido solicitado (deduz itens do estoque) |
| **UC45 - Comprar Pedido** | Diretor | Confirmar compra do pedido aprovado (ajustar quantidades) |
| **UC46 - Entregar Pedido** | Diretor | Entregar pedido comprado (adicionar itens ao estoque) |
| **UC47 - Atualizar Status do Pedido** | Diretor | Alterar status do pedido (0→1 ou 1→2) |
| **UC48 - Excluir Pedido** | Diretor, Admin | Remover pedido |

### 2.11 Módulo Administrativo — Usuários

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC49 - Cadastrar Usuário** | Diretor | Criar novo usuário (nome, e-mail, senha, cargo) |
| **UC50 - Editar Usuário** | Diretor | Alterar dados do usuário |
| **UC51 - Excluir Usuário** | Diretor | Remover usuário (não pode auto-excluir-se) |
| **UC52 - Listar Usuários** | Diretor | Visualizar todos os usuários do sistema |

### 2.12 Módulo Administrativo — Dashboard

| Caso de Uso | Ator Primário | Descrição |
|-------------|---------------|-----------|
| **UC53 - Visualizar KPIs** | Diretor | Exibir indicadores: total de alunos, turmas vigentes, pedidos pendentes, estoque crítico |
| **UC54 - Visualizar Gráficos Acadêmicos** | Diretor | Exibir gráficos de alunos por curso e status das matrículas |
| **UC55 - Visualizar Gráficos Logísticos** | Diretor | Exibir gráfico de consumo de itens no mês atual |

---

## 3. Relacionamentos entre Casos de Uso

### 3.1 Include (Inclusão obrigatória)

| Caso de Uso | Include | Descrição |
|-------------|---------|-----------|
| UC02 - Recuperar Senha | → UC03 - Redefinir Senha | O fluxo de recuperação inclui a redefinição da senha |
| UC32 - Gerar Histórico | → UC27, UC31 | O histórico inclui visualização de notas e presenças |

### 3.2 Extend (Extensão opcional)

| Caso de Uso | Extend | Condição |
|-------------|--------|----------|
| UC32 - Gerar Histórico | ← UC33 - Exportar PDF | Se o usuário desejar exportar |
| UC37 - Listar Estoque | ← UC38 - Pesquisar Item | Se o usuário desejar filtrar |

---

## 4. Matriz Atores vs Casos de Uso

Legenda: ● = Executa diretamente | ○ = Visualiza apenas

| Caso de Uso | Diretor | Admin | Professor | Visitante |
|-------------|---------|-------|-----------|-----------|
| UC01 - Realizar Login | | | | ● |
| UC02 - Recuperar Senha | | | | ● |
| UC03 - Redefinir Senha | | | | ● |
| UC04 a UC08 - Alunos | ● | ● | ○ | |
| UC09 a UC13 - Cursos | ● | ● | ○ | |
| UC14 a UC18 - Turmas | ● | ● | ○ | |
| UC19 - Minhas Turmas | | | ● | |
| UC20 a UC24 - Matrículas | ● | ● | ○ | |
| UC25 - Minhas Matrículas | | | ● | |
| UC26 a UC29 - Notas | ● | ● | ● | |
| UC30 a UC31 - Presenças | ● | ● | ● | |
| UC32 - Histórico | ● | ● | | |
| UC33 - Exportar PDF | ● | ● | | |
| UC34 a UC40 - Estoque | ● | ● | ○ | |
| UC41 a UC43 - Pedidos (criar/ver) | ● | ● | ● | |
| UC44 a UC48 - Pedidos (aprovar/comprar/entregar) | ● | | | |
| UC49 a UC52 - Usuários | ● | | | |
| UC53 a UC55 - Dashboard | ● | | | |
