# PRD — Sistema de Gestão Acadêmica (SGA) Associação ABACO

## 1. Contexto

A Associação ABACO é uma ONG que oferece cursos profissionalizantes gratuitos para a comunidade. Atualmente os processos administrativos são realizados manualmente, gerando atrasos e dificuldades na gestão das turmas.

Este sistema tem como objetivo digitalizar os processos acadêmicos e administrativos.

O sistema deverá estar funcional até Julho de 2026.

---

## 2. Objetivos

O sistema deverá permitir:

- gerenciamento de alunos
- gerenciamento de cursos
- criação de turmas
- matrícula de alunos
- registro de presença
- lançamento de notas
- geração de histórico escolar
- gestão de pedidos de materiais
- controle de estoque
- dashboards administrativos

---

## 3. Usuários do Sistema

### Diretora

Permissões:

- visualizar dashboards
- aprovar pedidos
- gerenciar permissões

### Equipe Administrativa

Permissões:

- cadastrar alunos
- realizar matrículas
- consultar relatórios

### Professor

Permissões:

- registrar presença
- lançar notas
- requisitar materiais

---

## 4. Módulos

### Módulo Acadêmico

- cadastrar alunos
- cadastrar cursos
- criar turmas
- realizar matrículas
- registrar presença
- lançar notas
- gerar histórico

### Módulo Logístico

- requisitar materiais
- aprovar pedidos
- dar baixa no estoque
- alertas de estoque

### Módulo Administrativo

- gerenciar usuários
- gerenciar permissões

---

## 5. Regras de Negócio

### Matrícula

- cada aluno pode ter várias matrículas
- cada matrícula pertence a uma turma

Status matrícula:

0 = ativa  
1 = concluída  
2 = cancelada

### Presença

0 = ausente  
1 = presente

### Pedidos

0 = solicitado  
1 = aprovado  
2 = entregue

---

## 6. Critérios de Aceite

O sistema será considerado pronto quando:

- matrículas funcionarem
- presença puder ser registrada
- notas puderem ser lançadas
- pedidos puderem ser aprovados
- dashboards puderem ser gerados

## 7. Critérios de execução

A forma de trabalho deve adotar as seguintes medidas:

- Divida em pequenas tarefas
- Anote a cada etapa de desenvolvimento (Concluido, em andamento, a iniciar)
- Utilizar sub agentes para a realização das tarefas
- É Necessário a realização de testes para a validação de cada etapa
- Anote as etapas de andamento dos testes
