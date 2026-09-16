PRD — Backend de Autenticação (Login) - SGA Associação ABACO
1. Contexto e Objetivo
Este documento detalha os requisitos, arquitetura e critérios de segurança para o desenvolvimento da API de Autenticação (Login) do Sistema de Gestão Acadêmica (SGA). O backend será desenvolvido em Python com FastAPI e se comunicará com o banco de dados PostgreSQL e o frontend em Angular.

O objetivo deste módulo é validar as credenciais do usuário, garantir a proteção contra ataques cibernéticos e fornecer um token de acesso seguro (JWT) contendo o nível de permissão (cargo) para que o Angular gerencie o roteamento e a exibição de componentes.

2. Especificações do Endpoint
Rota: POST /api/v1/auth/login

Descrição: Autentica um usuário existente e retorna um token de sessão.

Content-Type: application/json ou application/x-www-form-urlencoded (Padrão OAuth2 do FastAPI).

2.1. Request (Payload) Esperado
O Angular deverá enviar as credenciais validadas no client-side:

JSON
{
  "email": "diretora@abaco.org.br",
  "senha": "senha_em_texto_plano"
}
2.2. Response Esperado (Sucesso - HTTP 200 OK)
O backend retornará o token JWT e os dados básicos para o state da aplicação Angular:

JSON
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "idUsuario": 1,
    "nome": "Maria Diretora",
    "email": "diretora@abaco.org.br",
    "cargo": 1
  }
}
3. Arquitetura e Mapeamento de Dados
A autenticação consumirá a tabela usuario definida no banco de dados:

Tabela Alvo: usuario

Campos Utilizados:

email (TEXT UNIQUE): Chave de busca do usuário.

senhaHash (TEXT): Onde a senha criptografada está armazenada para comparação.

cargo (INTEGER): Define a Role do usuário (Ex: 1 = Diretora, 2 = Professor, 3 = Admin), que deve ser embutida no Token JWT.

4. Requisitos de Segurança e Validação (Critico)
Como este é um projeto profissional, a rota de login deve ser blindada contra as vulnerabilidades mais comuns (OWASP Top 10).

4.1. Prevenção contra SQL Injection (Injeção de SQL)
Diretriz: É estritamente proibido concatenar strings (ex: f"SELECT * FROM usuario WHERE email = '{email}'") para fazer buscas no banco.

Implementação: O acesso ao banco deve ser feito exclusivamente através do SQLAlchemy (ORM). O SQLAlchemy utiliza Prepared Statements e parametrização de consultas nativamente, neutralizando qualquer tentativa de injeção de SQL vinda do input do Angular.

4.2. Criptografia de Senhas (Hashing)
Diretriz: A senha em texto plano recebida do frontend jamais pode ser salva ou comparada diretamente.

Implementação: Utilizar a biblioteca Passlib com Bcrypt (passlib[bcrypt]). O fluxo deve ser:

Buscar o usuário pelo e-mail no banco.

Utilizar a função bcrypt.verify(senha_recebida, usuario.senhaHash) para validar matematicamente se as senhas batem.

4.3. Autenticação Stateless com JWT (JSON Web Tokens)
Diretriz: O servidor não deve guardar estado de sessão na memória.

Implementação: Utilizar a biblioteca PyJWT.

O token deve ser assinado utilizando o algoritmo HS256 com uma chave secreta (SECRET_KEY) forte, armazenada exclusivamente no arquivo .env.

Payload do Token: Deve conter o sub (email ou ID do usuário), cargo e o exp (Data de Expiração).

Expiração: O token deve ter uma validade curta (ex: 2 horas). Após isso, o Angular forçará um novo login.

4.4. Sanitização e Validação de Entradas
Implementação: Utilizar o Pydantic (schemas/auth_schema.py) para tipar rigorosamente a requisição. O FastAPI rejeitará automaticamente qualquer requisição que não contenha um e-mail válido ou que envie tipos de dados inesperados, antes mesmo de bater na regra de negócio.

4.5. Mitigação de Força Bruta (Rate Limiting e Delay)
Implementação: Mensagens de erro devem ser genéricas para não vazar a existência de um e-mail no banco. (Ex: Retornar "E-mail ou senha incorretos" tanto se o e-mail não existir, quanto se a senha estiver errada).

5. Critérios de Aceite (Definition of Done)
Para que a Issue de "Backend - API de Login" seja considerada concluída, as seguintes verificações devem passar:

[ ] Modelagem: O schema do Pydantic para a requisição exige que o campo de e-mail seja válido (EmailStr).

[ ] Segurança ORM: A consulta ao e-mail no PostgreSQL é feita usando os métodos do SQLAlchemy (session.query(Usuario).filter(...)), garantindo imunidade a SQL Injection.

[ ] Hashing: A verificação de senha utiliza Bcrypt (Passlib) comparando com a coluna senhaHash.

[ ] Geração de Token: Um token JWT válido é retornado no sucesso, contendo o ID do usuário e o cargo no payload.

[ ] Tratamento de Erros: Caso o e-mail não exista ou a senha não bata, a API retorna código HTTP 401 Unauthorized com a mensagem genérica "E-mail ou senha incorretos".

[ ] Variáveis de Ambiente: A chave secreta do JWT (SECRET_KEY) e o tempo de expiração estão isolados no arquivo .env e são lidos via pydantic-settings.

[ ] Teste de Integração: O endpoint responde corretamente ao client do Angular ou a um teste via Postman/Swagger.

6. Stack Afetado
[ ] Frontend

[x] Backend (FastAPI / Python)

[x] Banco de Dados (PostgreSQL)

[ ] Docker/Infra

7. Estimativa de Esforço
M (Média complexidade devido à configuração inicial do JWT, Passlib e SQLAlchemy).