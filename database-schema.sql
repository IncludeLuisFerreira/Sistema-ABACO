CREATE TABLE aluno (
    idaluno SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    telefone TEXT,
    nascimento DATE,
    rua TEXT,
    bairro TEXT,
    numero INTEGER
);

CREATE TABLE curso (
    idcurso SERIAL PRIMARY KEY,
    nomecurso TEXT NOT NULL
);

CREATE TABLE usuario (
    idusuario SERIAL PRIMARY KEY,
    nome TEXT,
    telefone TEXT,
    email TEXT UNIQUE,
    senhahash TEXT,
    cargo INTEGER
);

CREATE TABLE turma (
    idturma SERIAL PRIMARY KEY,
    capacidade INTEGER,
    datainicio DATE,
    datafim DATE,
    idcurso INTEGER REFERENCES curso(idcurso),
    idprofessor INTEGER REFERENCES usuario(idusuario),
    diasaula TEXT
);

CREATE TABLE matricula (
    idmatricula SERIAL PRIMARY KEY,
    idaluno INTEGER REFERENCES aluno(idaluno),
    idturma INTEGER REFERENCES turma(idturma),
    datamatricula DATE,
    status INTEGER
);

CREATE TABLE presenca (
    idpresenca SERIAL PRIMARY KEY,
    idmatricula INTEGER REFERENCES matricula(idmatricula),
    dataaula DATE,
    presente BOOLEAN
);

CREATE TABLE nota (
    idnota SERIAL PRIMARY KEY,
    nota FLOAT,
    prova INTEGER,
    idmatricula INTEGER REFERENCES matricula(idmatricula)
);

CREATE INDEX idx_nota_id_matricula ON nota (idmatricula);
CREATE INDEX idx_nota_matricula_prova ON nota (idmatricula, prova);

CREATE TABLE estoque (
    iditemestoque SERIAL PRIMARY KEY,
    nomeitem TEXT,
    quantidadedisponivel INTEGER,
    unidade TEXT,
    estoqueminimo INTEGER
);

CREATE TABLE movimentacao_estoque (
    idmovimentacao SERIAL PRIMARY KEY,
    iditemestoque INTEGER REFERENCES estoque(iditemestoque),
    quantidade INTEGER NOT NULL,
    tipomovimentacao TEXT NOT NULL,
    justificativa TEXT,
    datamovimentacao TIMESTAMP NOT NULL
);

CREATE TABLE pedido (
    idpedido SERIAL PRIMARY KEY,
    idusuario INTEGER REFERENCES usuario(idusuario),
    idturma INTEGER REFERENCES turma(idturma),
    datapedido DATE,
    status INTEGER
);

CREATE TABLE itempedido (
    iditempedido SERIAL PRIMARY KEY,
    idpedido INTEGER REFERENCES pedido(idpedido),
    iditemestoque INTEGER REFERENCES estoque(iditemestoque),
    nomeitem TEXT,
    quantidade INTEGER,
    precounitario FLOAT
);
