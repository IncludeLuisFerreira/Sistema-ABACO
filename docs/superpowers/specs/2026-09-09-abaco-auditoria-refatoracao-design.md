# Auditoria de refatoração e modernização do sistema ABACO

## Objetivo

Este documento tem como propósito mapear o estado atual do sistema ABACO, identificar o que já está em bom estado e classificar os pontos que devem ser mantidos, refatorados ou reescritos para entregar uma solução mais segura, escalável, padronizada e fácil de evoluir.

A análise cobre os principais pilares do projeto: banco de dados, backend, frontend, autenticação, segurança e infraestrutura.

## Escopo 

### Dentro do escopo
- arquitetura geral do backend em FastAPI
- estrutura do frontend em Angular
- schema e relacionamentos do banco PostgreSQL
- autenticação e autorização por cargo
- segurança de endpoints, token e sessão
- organização do código e padrões de manutenção
- deploy e ambiente local com Docker

### Fora do escopo
- desenvolvimento de novos módulos de negócio a partir de zero
- migração de todos os fluxos do sistema em uma única etapa
- reescrita completa da solução com priorização por risco

## Resumo executivo

O projeto ABACO já demonstra uma boa base tecnológica: FastAPI, Angular, PostgreSQL e Docker estão bem alinhados ao que o cliente precisa. A arquitetura atual é funcional, com tendência de monólito modular e boa separação entre frontend e backend. O principal problema não é ausência de tecnologia, e sim a ausência de governança de domínio, padronização de modelos, separação clara de responsabilidades e rigor em segurança e qualidade.

A maior parte do esforço de modernização deve estar em:

1. padronizar o banco e os modelos de domínio;
2. organizar a camada de backend por módulos e serviços bem definidos;
3. reduzir duplicação e acoplamento no frontend;
4. reforçar a autenticação e autorização com política explícita e centralizada;
5. preparar a infraestrutura para operação, auditoria e manutenção em produção.

## 1. Visão geral do módulo

### 1.1 Backend

O backend foi montado em FastAPI com múltiplos routers em `/api/v1`, serviços por domínio e modelos SQLAlchemy. O projeto já segue uma estrutura de monólito funcional, com clara separação entre API, regras e persistência. Isso é positivo, porque permite evolução incremental sem necessariamente introduzir complexidade gerencial extra.

Impacto no sistema: o backend é o coração do fluxo operacional do sistema acadêmico, sendo responsável por autorização, regras de negócio e integração com banco de dados.

### 1.2 Frontend

O frontend em Angular 21 já está em uma arquitetura de componentes e serviços organizada por módulos e recursos. Há serviços de autenticação, guardas e páginas por domínio funcional. Isso ajuda no crescimento do sistema, mas há sinais de acoplamento entre UI e regras de negócio, além de duplicação em fluxos repetidos.

Impacto no sistema: a qualidade da UX e da manutenção do frontend impacta diretamente a produtividade da operação, dos professores e da direção.

### 1.3 Banco de dados

O schema do projeto está funcional e cobre os principais domínios acadêmicos e logísticos. No entanto, apresenta vários sinais de design legado: nomes inconsistentes, uso de inteiros como enums, pouca normalização de entidades e ausência de auditoria e restrições de integridade mais robustas.

Impacto no sistema: o banco é a base dos dados e pode virar gargalo operacional se a schema não for melhorada antes de escalar.

### 1.4 Segurança e infraestrutura

Existem boas práticas implementadas, como JWT, rate limiting em autenticação e uso de Docker Compose. Contudo, a segurança ainda precisa ficar mais explícita e centralizada, com validação de permissões, auditoria, políticas de senha, proteção contra enumeração e padronização de tratamento de erro.

Impacto no sistema: a aplicação precisa operar em ambiente real com confiança e baixo risco de exposição de dados ou abuso de endpoints.

## 2. Tabela de triagem (Manter vs. Refatorar)

| Arquivo / Componente | Ação | Nível de Prioridade | Motivo resumido |
|---|---|---:|---|
| `backend/app/core/security.py` | Refatorar | Alta | JWT funcional, mas sem política centralizada de sessão e autorização mais explícita |
| `backend/app/core/dependencies.py` | Refatorar | Alta | Dependências de autenticação/DB precisam ser mais estruturadas e desacopladas |
| `backend/app/api/v1/*.py` | Refatorar | Alta | Rotas com lógica de negócio pouco isolada e baixa padronização |
| `backend/app/services/*.py` | Refatorar | Alta | Regras de negócio espalhadas; duplicação e acoplamento entre módulos |
| `backend/app/models/*.py` | Refatorar | Crítica | Nomes, constraints e relacionamentos ainda refletem modelo legado |
| `database-schema.sql` | Reescrever | Crítica | Schema com pouca normalização, enums em inteiro e ausência de auditoria |
| `backend/app/schemas/*.py` | Refatorar | Média | Validação útil, mas precisa de consistência e contratos mais fortes |
| `frontend/src/app/core/services/*.ts` | Refatorar | Alta | Serviços de domínio e autenticação precisam de contratos e estados mais previsíveis |
| `frontend/src/app/features/*` | Refatorar | Média | Muitas páginas e componentes por domínio, com tendência de acoplamento e repetições |
| `frontend/src/app/core/guards/*` | Manter + Refatorar | Média | Guarda funcional, mas precisa de padronização de roles e mensagens de erro |
| `docker-compose.yml` | Manter | Média | Base correta para desenvolvimento local, mas precisa de hardening para produção |
| `README.md` e documentação | Manter | Baixa | Documentação útil, mas precisa de visão de arquitetura e rascunho de operação |
| `backend/requirements.txt` | Manter | Média | Pilha adequada, mas evoluir para controle mais rígido de vulnerabilidades |

## 3. O que deve ser refatorado

### 3.1 Banco de dados e models

#### Problema atual

O arquivo `database-schema.sql` mostra uma estrutura funcional, porém fortemente inspirada em um modelo de dados legado. Há:

- nomes de entidades em português e inconsistentes (`idaluno`, `idcurso`, `status`) sem padronização de convenção;
- uso de `INTEGER` para representar papéis e status, em vez de enumeração explícita ou tabela de domínio;
- pouco controle de integridade sem regras de unicidade, validações e restrições mais fortes;
- ausência de campos de auditoria e histórico (`created_at`, `updated_at`, `created_by`, etc.);
- pouca ou nenhuma análise de índices em consultas frequentemente filtradas;
- risco de inconsistência entre schema e modelos ORM.

#### Padrão de mercado

Isso viola princípios clássicos de modelagem: normalização, consistência de domínio e separação de responsabilidades. Também contraria boas práticas modernas de DDD-lite e clean database design, onde entidades, estados e regras de negócio são modeladas de forma explícita.

#### Solução proposta

Reescrever o schema em camadas:

1. usar um modelo de domínio com `id` gerado por PK natural ou surrogate explícito;
2. definir enumeração para cargo, status de matrícula, status de pedido, presença, etc.;
3. criar tabelas de relacionamento e auditoria explícitas;
4. adicionar índices para chaves de filtro e junções frequentes;
5. garantir constraints e triggers quando necessário para integridade de negócio.

Exemplo moderno de modelagem:

```sql
CREATE TYPE cargo_usuario AS ENUM ('diretor', 'administrador', 'professor');
CREATE TYPE status_matricula AS ENUM ('ativa', 'concluida', 'cancelada');
CREATE TYPE status_pedido AS ENUM ('solicitado', 'aprovado', 'comprado', 'entregue', 'cancelado');

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    cargo cargo_usuario NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE matriculas (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id),
    turma_id INTEGER NOT NULL REFERENCES turmas(id),
    status status_matricula NOT NULL,
    data_matricula DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3.2 Backend: API e regra de negócio

#### Problema atual

Os arquivos em `backend/app/api/v1/*.py` seguem o padrão REST esperado, mas ainda há sinais de acoplamento e pouca padronização de contratos. Em geral:

- rotas se tornam endpoints de ação e não contratos de domínio;
- regras de negócio aparecem em camadas diferentes sem fronteiras claras;
- validações e mensagens de erro são heterogêneas entre módulos;
- serviços podem depender de detalhes de sessão ou http de forma direta;
- o padrão de resposta pode variar entre endpoints.

#### Padrão de mercado

Isso viola a separação de responsabilidades e compromete a escalabilidade do sistema. O código fica mais difícil de testar, evoluir e validar. Também aumenta a chance de regressões quando a regra de negócio cresce.

#### Solução proposta

Adotar uma estrutura por domínio com fronteiras fortes:

- `api/`: transporte HTTP apenas
- `application/` ou `services/`: casos de uso
- `domain/`: entidades e regras do negócio
- `repositories/`: persistência
- `schemas/`: contratos de entrada e saída

Exemplo:

```python
# api/v1/alunos.py
@router.get("/alunos/{aluno_id}", response_model=AlunoDetalheResponse)
def get_aluno(aluno_id: int, db: Session = Depends(get_db)) -> AlunoDetalheResponse:
    return aluno_service.get_detail(db=db, aluno_id=aluno_id)
```

```python
# services/aluno_service.py
class AlunoService:
    def get_detail(self, db: Session, aluno_id: int) -> AlunoDetalheResponse:
        aluno = self.repository.get_by_id(db, aluno_id)
        if aluno is None:
            raise NotFoundError("Aluno não encontrado")
        return AlunoDetalheResponse.model_validate(aluno)
```

A principal mudança é manter a API sem regra de negócio e separar o domínio do transporte.

### 3.3 Frontend: serviços e componentes

#### Problema atual

O frontend em Angular está organizado por domínio, o que é bom, porém há sinais de crescimento sem padronização ou contract-first. Padrões observados:

- serviços de domínio com responsabilidades sobrepostas;
- lógicas de autenticação e tokens espalhadas em serviços e guardas;
- componentes complexos com excesso de responsabilidade;
- botões de ação e diálogos reutilizados sem um padrão centralizado;
- repetição de código em gerenciamento de listas e formulários.

#### Padrão de mercado

Isso viola o princípio de responsabilidade única e o conceito de UI modular de mercado, em que cada componente tem um objetivo claro, comunica por contratos e evita duplicação.

#### Solução proposta

1. centralizar modelos de domínio em `core/models` e `features/*/models`;
2. separar `service`, `state`, `use-case` e `presentation` em estruturas mais claras;
3. criar `shared` para componentes comuns e regras de UX auditáveis;
4. padronizar `signals` e cachês de dados;
5. reduzir lógica de negócio dentro do template e mover para o service.

Exemplo:

```ts
@Injectable({ providedIn: 'root' })
export class AutenticacaoFacade {
  readonly authState = signal<AuthState>({ token: null, role: null, userId: null });

  login(email: string, senha: string) {
    return this.authService.login(email, senha).pipe(
      tap((response) => this.authState.set({ ... }))
    );
  }
}
```

### 3.4 Segurança e autenticação

#### Problema atual

O fluxo de autenticação mostra uma base positiva, principalmente com JWT, rate limit em autenticação e hash de senha com bcrypt. Porém, ainda há riscos de:

- permissões por cargo baseadas em inteiros não explícitos;
- dificuldade de centralizar políticas de autorização;
- ausência de auditoria de login e eventos sensíveis;
- ausência de política clara para expiração/renovação de sessão;
- uso de token em `localStorage`, que é vulnerável a XSS;
- reflexão de erros e informações internas em algumas respostas.

#### Padrão de mercado

O padrão seguro atual em aplicações web é aplicar autenticação forte, controle fino de autorização, logs de segurança e armazenamento de token em área segura e com mecanismos de expiração, refresh e revogação.

#### Solução proposta

- trocar `localStorage` por cookies httpOnly e secure quando possível;
- criar `role guard` centralizado e forte, com controlo do contexto de usuário;
- definir `isAllowed` e `requireRole` de forma explícita;
- registrar logs de login, falha de autenticação e ações sensíveis;
- padronizar códigos HTTP e mensagens públicas;
- bloquear enumeração de usuários nas rotas de recuperação de senha.

### 3.5 Infraestrutura

#### Problema atual

O ambiente com Docker Compose está bem estruturado para desenvolvimento local, mas ainda é insuficiente para produção. O projeto parece assumir um ambiente doméstico ou de laboratório mais do que um ambiente de operação corporativa.

#### Padrão de mercado

Ambientes de produção precisam de:

- variáveis de ambiente segregadas por ambiente;
- health checks reais;
- volumes persistentes e backups;
- observabilidade mínima (logs, métricas, traces);
- rede isolada e regras de segurança;
- rollback e deploy automatizado.

#### Solução proposta

- separar `docker-compose.yml` em ambientes `dev` e `prod`;
- adicionar parâmetros de segurança e secrets;
- configurar `healthcheck` e `depends_on` seguros;
- usar `postgres` com volumes persistentes e backup planejado;
- centralizar `.env` e `.env.example` com separação por contexto.

## 4. O que pode ser mantido

### 4.1 Stack tecnológica

Os principais componentes atuais são sólidos:

- FastAPI é uma escolha moderna, performática e adequada para uma API de gestão acadêmica;
- PostgreSQL é uma base correta para o tipo de operação e volume previsto;
- Angular 21 é uma escolha moderna para SPA e gestão de módulos;
- Docker Compose é uma boa base para ambiente local e onboarding de equipe.

### 4.2 Estrutura modular atual

O projeto já apresenta uma boa organização por módulos e perfil funcional. Isso reduz o risco da arquitetura global virar algo desordenado. O problema não é a estrutura, e sim a governança e a consistência dentro dela.

### 4.3 Autenticação e autorização iniciais

A base de JWT + bcrypt + rate limit em autenticação é um bom ponto de partida. A manutenção deve ocorrer por refinamento, não por remoção.

### 4.4 Documentação de negócio e arquitetura

Há documentação funcional e de requisitos em vários níveis do projeto. Isso ajuda a preservar contexto e facilita a análise da arquitetura. O principal é transformar essa documentação em um padrão de referência para futuras mudanças.

## 5. Check-list de segurança e UX

### 5.1 Ameaças identificadas

- autenticação baseada em JWT sem política explícita de refresh e revogação;
- token em `localStorage` em frontend;
- `cargo` e `status` representados por inteiro sem enum;
- risco de ataque por enumeração em recuperação de senha;
- falhas de validação de dados em payloads sensíveis;
- ausência de logs e auditoria por ação crítica;
- exposição de mensagens internas em respostas HTTP;
- falta de proteção de endpoints de alta sensibilidade com autorização mais granular.

### 5.2 Melhorias diretas de UX

- interface de login com feedback claro e mensagens amigáveis;
- padronizar navegação por perfil com menus explícitos;
- reduzir cliques em operações recorrentes (presença, notas, pedidos);
- validar formulários em tempo real com mensagens de erro objetivas;
- usar filtros, listas e dashboards com feedback visual de status;
- melhorar a consistência visual entre módulos acadêmicos, administrativos e logísticos;
- evitar páginas sobrecarregadas com excesso de dados em uma única tela;
- organizar ações por contexto e papel do usuário.

## 6. Priorização recomendada

### Prioridade Crítica
- reescrever o schema principal do banco;
- refatorar módulos de autenticação e autorização;
- centralizar validações e tratamento de erros da API;
- definir contratos de resposta e de regra de negócio.

### Prioridade Alta
- reorganizar backend por domínio;
- unificar padrões de serviços e repositories no frontend;
- aplicar padronização de componentes e estado;
- melhorar observabilidade e logs seguros.

### Prioridade Média
- reorganizar tokens e sessões;
- criar políticas de dados e auditoria;
- ajustar UX para fluxos repetitivos e de alto volume.

### Prioridade Baixa
- documentação de manutenção e operação;
- revisão de visual design e micro-interações;
- otimização de performance de templates e caches.

## 7. Decisão de arquitetura recomendada

A recomendação para o cliente não é “recomeçar do zero”, e sim evoluir o sistema existente para um monólito modular bem organizado, com regras de domínio explícitas e contratos claros. Esse modelo preserva a funcionalidade atual, reduz risco de quebra e oferece uma base mais saudável para as próximas fases de crescimento.

Em termos práticos, o que deve ser priorizado é:

1. padronização do domínio de dados;
2. separação clara de API, serviços e persistência;
3. autenticação forte e centralizada;
4. frontend com organização por módulos e componentes reutilizáveis;
5. infraestrutura com observabilidade e segurança para produção.

## Conclusão

O ABACO já está em uma etapa madura de desenvolvimento funcional. O maior salto de qualidade não vem de trocar tudo por tecnologia nova, e sim de aplicar disciplina de arquitetura, modelagem e governança. Em outras palavras, o sistema precisa deixar de ser “funcionalmente bom” e passar a ser “estruturalmente confiável”.

A refatoração deve ser incremental, com prioridade em risco, segurança e clareza de domínio. Essa abordagem permite preservar o valor já entregue e preparar a solução para uma nova etapa de operação real, manutenção e expansão.
