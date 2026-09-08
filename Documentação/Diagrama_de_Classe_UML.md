# UML CLASS DIAGRAM — SGA ABACO

**5-Layer Architecture:** Model, Schema, Controller, Service, View + Core Infrastructure

Based on actual code at `backend/app/` (Python/FastAPI) and `frontend/src/app/` (Angular).

**Legend:**
- `-` private | `#` protected | `+` public
- `?` = nullable/optional
- `PK` = Primary Key | `FK` = Foreign Key
- `alias` = JSON serialization name (camelCase)

---

## LAYER 1 — MODEL (SQLAlchemy Entities)

### Package: `backend/app/models/`

---

### Aluno
Table: `aluno`
```
+------------------------------------------------------------+
| <<Entity>> Aluno                                           |
+------------------------------------------------------------+
| - id_aluno: int (PK, column: idaluno)                      |
| - nome: str (NOT NULL)                                     |
| - telefone: str ?                                           |
| - data_nascimento: date ? (column: nascimento)             |
| - rua: str ?                                                |
| - bairro: str ?                                             |
| - numero: int ?                                             |
+------------------------------------------------------------+
| + get_id_aluno() : int                                      |
| + get_nome() : str                                          |
| + get_telefone() : str?                                     |
| + get_data_nascimento() : date?                             |
| + get_rua() : str?                                          |
| + get_bairro() : str?                                       |
| + get_numero() : int?                                       |
+------------------------------------------------------------+
| Relationships: Aluno 1 --- * Matricula                     |
+------------------------------------------------------------+
```

### Curso
Table: `curso`
```
+------------------------------------------------------------+
| <<Entity>> Curso                                           |
+------------------------------------------------------------+
| - id_curso: int (PK, column: idcurso)                      |
| - nome_curso: str (NOT NULL, column: nomecurso)            |
+------------------------------------------------------------+
| + get_id_curso() : int                                      |
| + get_nome_curso() : str                                    |
+------------------------------------------------------------+
```

### Turma
Table: `turma`
```
+------------------------------------------------------------+
| <<Entity>> Turma                                           |
+------------------------------------------------------------+
| - id_turma: int (PK, column: idturma)                      |
| - capacidade: int ?                                         |
| - data_inicio: date ? (column: datainicio)                 |
| - data_fim: date ? (column: datafim)                       |
| - id_curso: int (FK -> curso)                              |
| - id_professor: int ? (FK -> usuario)                      |
| - dias_aula: str ? (column: diasaula)                      |
| - avaliacoes: list ? (JSONB)                               |
| + vagas_ocupadas: int (readonly, computed)                 |
+------------------------------------------------------------+
| + get_id_turma() : int                                      |
| + get_capacidade() : int?                                   |
| + get_data_inicio() : date?                                 |
| + get_data_fim() : date?                                    |
| + get_id_curso() : int                                      |
| + get_id_professor() : int?                                 |
| + get_dias_aula() : str?                                    |
| + get_avaliacoes() : list?                                  |
| + get_vagas_ocupadas() : int                                |
+------------------------------------------------------------+
| Relationships: Curso 1 --- * Turma ; Usuario 0..1 --- * Turma ; Turma 1 --- * Matricula ; Turma 1 --- * Pedido |
+------------------------------------------------------------+
```

### Matricula
Table: `matricula`
```
+------------------------------------------------------------+
| <<Entity>> Matricula                                       |
+------------------------------------------------------------+
| - id_matricula: int (PK, column: idmatricula)              |
| - id_aluno: int (FK -> aluno)                              |
| - id_turma: int (FK -> turma)                              |
| - data_matricula: date ? (column: datamatricula)           |
| - status: int ?                                             |
+------------------------------------------------------------+
| + get_id_matricula() : int                                  |
| + get_id_aluno() : int                                      |
| + get_id_turma() : int                                      |
| + get_data_matricula() : date?                              |
| + get_status() : int?                                       |
+------------------------------------------------------------+
| Relationships: Aluno 1 --- * Matricula ; Turma 1 --- * Matricula ; Matricula 1 --- * Nota ; Matricula 1 --- * Presenca |
+------------------------------------------------------------+
```

### Nota
Table: `nota`
```
+------------------------------------------------------------+
| <<Entity>> Nota                                            |
+------------------------------------------------------------+
| - id_nota: int (PK, column: idnota)                        |
| - nota: float ?                                             |
| - prova: int ?                                              |
| - id_matricula: int (FK -> matricula)                      |
+------------------------------------------------------------+
| + get_id_nota() : int                                       |
| + get_nota() : float?                                       |
| + get_prova() : int?                                        |
| + get_id_matricula() : int                                  |
+------------------------------------------------------------+
| Relationships: Matricula 1 --- * Nota                      |
+------------------------------------------------------------+
```

### Presenca
Table: `presenca`
```
+------------------------------------------------------------+
| <<Entity>> Presenca                                        |
+------------------------------------------------------------+
| - id_presenca: int (PK, column: idpresenca)                |
| - id_matricula: int (FK -> matricula)                      |
| - data_aula: date ? (column: dataaula)                     |
| - presente: bool ?                                          |
+------------------------------------------------------------+
| + get_id_presenca() : int                                   |
| + get_id_matricula() : int                                  |
| + get_data_aula() : date?                                   |
| + get_presente() : bool?                                    |
+------------------------------------------------------------+
| Relationships: Matricula 1 --- * Presenca                  |
+------------------------------------------------------------+
```

### Usuario
Table: `usuario`
```
+------------------------------------------------------------+
| <<Entity>> Usuario                                         |
+------------------------------------------------------------+
| - id_usuario: int (PK, column: idusuario)                  |
| - nome: str ?                                               |
| - telefone: str ?                                           |
| - email: str ? (UNIQUE)                                     |
| - senha_hash: str ? (column: senhahash)                    |
| - cargo: int ? (1=Diretor, 2=Professor, 3=Admin)          |
+------------------------------------------------------------+
| + get_id_usuario() : int                                    |
| + get_nome() : str?                                         |
| + get_telefone() : str?                                     |
| + get_email() : str?                                        |
| + get_senha_hash() : str?                                   |
| + get_cargo() : int?                                        |
+------------------------------------------------------------+
| Relationships: Usuario 0..1 --- * Turma (professor) ; Usuario 1 --- * Pedido (solicitante) |
+------------------------------------------------------------+
```

### Pedido
Table: `pedido`
```
+------------------------------------------------------------+
| <<Entity>> Pedido                                          |
+------------------------------------------------------------+
| - id_pedido: int (PK, column: idpedido)                    |
| - id_usuario: int (FK -> usuario)                          |
| - id_turma: int (FK -> turma)                              |
| - data_pedido: date ? (column: datapedido)                 |
| - status: int ? (0=Solicitado, 1=Aprovado,                |
|              2=Comprado, 3=Entregue)                       |
+------------------------------------------------------------+
| + get_id_pedido() : int                                     |
| + get_id_usuario() : int                                    |
| + get_id_turma() : int                                      |
| + get_data_pedido() : date?                                 |
| + get_status() : int?                                       |
+------------------------------------------------------------+
| Relationships: Usuario 1 --- * Pedido ; Turma 1 --- * Pedido ; Pedido 1 --- * ItemPedido |
+------------------------------------------------------------+
```

### ItemPedido
Table: `itempedido`
```
+------------------------------------------------------------+
| <<Entity>> ItemPedido                                      |
+------------------------------------------------------------+
| - id_item_pedido: int (PK, column: iditempedido)           |
| - id_pedido: int (FK -> pedido)                            |
| - id_item_estoque: int ? (FK -> estoque)                   |
| - nome_item: str ? (column: nomeitem)                      |
| - quantidade: int ?                                         |
| - preco_unitario: float ? (column: precounitario)          |
+------------------------------------------------------------+
| + get_id_item_pedido() : int                                |
| + get_id_pedido() : int                                     |
| + get_id_item_estoque() : int?                              |
| + get_nome_item() : str?                                    |
| + get_quantidade() : int?                                   |
| + get_preco_unitario() : float?                             |
+------------------------------------------------------------+
| Relationships: Pedido 1 --- * ItemPedido ; Estoque 0..1 --- * ItemPedido |
+------------------------------------------------------------+
```

### Estoque
Table: `estoque`
```
+------------------------------------------------------------+
| <<Entity>> Estoque                                         |
+------------------------------------------------------------+
| - id_item_estoque: int (PK, column: iditemestoque)         |
| - nome_item: str ? (column: nomeitem)                      |
| - quantidade_disponivel: int ? (column: quantidadedisponivel)|
| - unidade: str ?                                            |
| - estoque_minimo: int ? (column: estoqueminimo)            |
+------------------------------------------------------------+
| + get_id_item_estoque() : int                               |
| + get_nome_item() : str?                                    |
| + get_quantidade_disponivel() : int?                        |
| + get_unidade() : str?                                      |
| + get_estoque_minimo() : int?                               |
+------------------------------------------------------------+
| Relationships: Estoque 1 --- * ItemPedido ; Estoque 1 --- * MovimentacaoEstoque |
+------------------------------------------------------------+
```

### MovimentacaoEstoque
Table: `movimentacao_estoque`
```
+------------------------------------------------------------+
| <<Entity>> MovimentacaoEstoque                             |
+------------------------------------------------------------+
| - id_movimentacao: int (PK, column: idmovimentacao)        |
| - id_item_estoque: int (FK -> estoque)                     |
| - quantidade: int                                           |
| - tipo_movimentacao: str (column: tipomovimentacao)        |
| - justificativa: str ?                                      |
| - data_movimentacao: datetime (column: datamovimentacao)   |
+------------------------------------------------------------+
| + get_id_movimentacao() : int                               |
| + get_id_item_estoque() : int                               |
| + get_quantidade() : int                                    |
| + get_tipo_movimentacao() : str                             |
| + get_justificativa() : str?                                |
| + get_data_movimentacao() : datetime                        |
+------------------------------------------------------------+
| Relationships: Estoque 1 --- * MovimentacaoEstoque         |
+------------------------------------------------------------+
```

---

## LAYER 2 — SCHEMA (Pydantic DTOs)

### Package: `backend/app/schemas/`

All Response schemas use `from_attributes=True` and alias generators for camelCase JSON.

Key Response schemas:

| Entity | Response Schema | Composition |
|--------|----------------|-------------|
| Aluno | `AlunoResponseSchema` | `idAluno`, `nome`, `telefone?`, `dataNascimento?`, `rua?`, `bairro?`, `numero?` |
| Curso | `CursoResponseSchema` | `idCurso`, `nomeCurso` |
| Turma | `TurmaResponseSchema` | `idTurma`, `capacidade?`, `dataInicio?`, `dataFim?`, `idCurso`, `idProfessor?`, `diasAula?`, `vagasOcupadas?`, `avaliacoes?`, `curso: TurmaCursoInfo?`, `professor: TurmaProfessorInfo?` |
| Matricula | `MatriculaResponseSchema` | `idMatricula`, `idAluno?`, `idTurma?`, `dataMatricula?`, `status?`, `aluno: MatriculaAlunoInfo?`, `turma: MatriculaTurmaInfo?` |
| Nota | `NotaResponseSchema` | `idNota`, `idMatricula`, `nota?`, `prova?`, `matricula: NotaMatriculaInfo?` |
| Presenca | `PresencaResponseSchema` | `idPresenca`, `idMatricula`, `dataAula?`, `presente?`, `matricula: PresencaMatriculaInfo?` |
| Usuario | `UsuarioResponseSchema` | `idUsuario`, `nome?`, `telefone?`, `email?`, `cargo?` |
| Pedido | `PedidoResponseSchema` | `idPedido`, `idUsuario`, `idTurma`, `dataPedido?`, `status?`, `usuario: UsuarioPedidoInfo?`, `turma: TurmaPedidoInfo?`, `itens: list[ItemPedidoResponseSchema]?` |
| Estoque | `EstoqueResponseSchema` | `idItemEstoque`, `nomeItem?`, `quantidadeDisponivel?`, `unidade?`, `estoqueMinimo?` |
| Auth | `TokenResponse` | `access_token`, `token_type`, `usuario: UsuarioResponse` |
| Dashboard | `KpisResponse` | `total_alunos_ativos`, `total_turmas_vigentes`, `total_pedidos_pendentes`, `total_estoque_critico` |
| Historico | `HistoricoResponse` | `idMatricula`, `dataMatricula?`, `status?`, `aluno: HistoricoAlunoInfo`, `turma: HistoricoTurmaInfo`, `notas`, `presencas`, `percentualFrequencia?` |

---

## LAYER 3 — CONTROLLER (FastAPI Routers)

### Package: `backend/app/api/v1/`

### AuthRouter (`auth.py`) — prefix: `/api/v1/auth`
| Endpoint | Function | Rate Limit |
|----------|----------|------------|
| POST /api/v1/auth/login | `login(payload, request, db)` | 5/min |
| POST /api/v1/auth/forgot-password | `forgot_password(payload, request, db)` | 3/min |
| POST /api/v1/auth/reset-password | `reset_password(payload, request, db)` | 5/min |

### AlunoRouter (`alunos.py`) — prefix: `/api/v1/alunos` — cargo: 1, 3
| Method | Path | Function |
|--------|------|----------|
| GET | /api/v1/alunos | `read_alunos(current_user, db)` |
| GET | /api/v1/alunos/{aluno_id} | `read_aluno(aluno_id, current_user, db)` |
| POST | /api/v1/alunos | `create_alunos(payload, current_user, db)` |
| PUT | /api/v1/alunos/{aluno_id} | `update_alunos(aluno_id, payload, current_user, db)` |
| DELETE | /api/v1/alunos/{aluno_id} | `delete_alunos(aluno_id, current_user, db)` |

### CursoRouter (`cursos.py`) — prefix: `/api/v1/cursos` — cargo: 1, 3
| Method | Path | Function |
|--------|------|----------|
| GET | /api/v1/cursos | `read_cursos(current_user, db)` |
| GET | /api/v1/cursos/{curso_id} | `read_curso(curso_id, current_user, db)` |
| POST | /api/v1/cursos | `create_cursos(payload, current_user, db)` |
| PUT | /api/v1/cursos/{curso_id} | `update_cursos(curso_id, payload, current_user, db)` |
| DELETE | /api/v1/cursos/{curso_id} | `delete_cursos(curso_id, current_user, db)` |

### TurmaRouter (`turmas.py`) — prefix: `/api/v1/turmas` — cargo: 1, 2, 3
| Method | Path | Function |
|--------|------|----------|
| GET | /api/v1/turmas | `read_turmas(current_user, db)` |
| GET | /api/v1/turmas/me | `read_minhas_turmas(current_user, db)` (cargo 1,2) |
| GET | /api/v1/turmas/{turma_id} | `read_turma(turma_id, current_user, db)` |
| POST | /api/v1/turmas | `create_turmas(payload, current_user, db)` |
| PUT | /api/v1/turmas/{turma_id} | `update_turmas(turma_id, payload, current_user, db)` |
| DELETE | /api/v1/turmas/{turma_id} | `delete_turmas(turma_id, current_user, db)` |

### MatriculaRouter (`matriculas.py`) — prefix: `/api/v1/matriculas` — cargo: 1, 2, 3
| Method | Path | Function |
|--------|------|----------|
| GET | /api/v1/matriculas | `read_matriculas(current_user, db)` |
| GET | /api/v1/matriculas/me | `read_matriculas_by_professor(current_user, db)` |
| GET | /api/v1/matriculas/{matricula_id} | `read_matricula(matricula_id, current_user, db)` |
| POST | /api/v1/matriculas | `create_matriculas(payload, current_user, db)` |
| PUT | /api/v1/matriculas/{matricula_id} | `update_matriculas(matricula_id, payload, current_user, db)` |
| DELETE | /api/v1/matriculas/{matricula_id} | `delete_matriculas(matricula_id, current_user, db)` |

### NotaRouter (`notas.py`) — prefix: `/api/v1/notas` — cargo: 1, 2, 3
| Method | Path | Function |
|--------|------|----------|
| POST | /api/v1/notas | `create_notas(payload, current_user, db)` |
| GET | /api/v1/notas/matricula/{matricula_id} | `read_notas_by_matricula(matricula_id, current_user, db)` |
| GET | /api/v1/notas/turma/{turma_id} | `read_notas_by_turma(turma_id, prova?, current_user, db)` |
| GET | /api/v1/notas/media/turma/{turma_id} | `read_media_turma(turma_id, current_user, db)` |

### PresencaRouter (`presencas.py`) — prefix: `/api/v1/presencas` — cargo: 1, 2, 3
| Method | Path | Function |
|--------|------|----------|
| POST | /api/v1/presencas | `create_presencas(payload, current_user, db)` |
| GET | /api/v1/presencas/turma/{turma_id} | `read_presencas_by_turma(turma_id, dataAula?, current_user, db)` |

### UsuarioRouter (`usuarios.py`) — prefix: `/api/v1/usuarios` — cargo: 1
| Method | Path | Function |
|--------|------|----------|
| GET | /api/v1/usuarios | `read_usuarios(current_user, db)` |
| GET | /api/v1/usuarios/{usuario_id} | `read_usuario(usuario_id, current_user, db)` |
| POST | /api/v1/usuarios | `create_usuarios(payload, current_user, db)` |
| PUT | /api/v1/usuarios/{usuario_id} | `update_usuarios(usuario_id, payload, current_user, db)` |
| DELETE | /api/v1/usuarios/{usuario_id} | `delete_usuarios(usuario_id, current_user, db)` |

### PedidoRouter (`pedidos.py`) — prefix: `/api/v1/pedidos` — cargo: 1, 2, 3
| Method | Path | Function | Cargo |
|--------|------|----------|-------|
| GET | /api/v1/pedidos | `read_pedidos(current_user, db)` | 1,2,3 |
| GET | /api/v1/pedidos/{pedido_id} | `read_pedido(pedido_id, current_user, db)` | 1,2,3 |
| POST | /api/v1/pedidos | `create_pedidos(payload, current_user, db)` | 1,2,3 |
| PUT | /api/v1/pedidos/{pedido_id}/aprovar | `aprovar_pedido_endpoint(pedido_id, current_user, db)` | 1 |
| PUT | /api/v1/pedidos/{pedido_id}/comprar | `comprar_pedido_endpoint(pedido_id, payload, current_user, db)` | 1 |
| PUT | /api/v1/pedidos/{pedido_id} | `update_pedidos(pedido_id, payload, current_user, db)` | 1 |
| PUT | /api/v1/pedidos/{pedido_id}/entregar | `entregar_pedido_endpoint(pedido_id, current_user, db)` | 1 |
| DELETE | /api/v1/pedidos/{pedido_id} | `delete_pedidos(pedido_id, current_user, db)` | 1,2,3 |

### EstoqueRouter (`estoque.py`) — prefix: `/api/v1/estoque` — cargo: 1, 2, 3
| Method | Path | Function |
|--------|------|----------|
| GET | /api/v1/estoque | `read_estoque(current_user, db)` |
| GET | /api/v1/estoque/search | `search_estoque(q, current_user, db)` |
| GET | /api/v1/estoque/alertas | `read_alertas_estoque(current_user, db)` |
| GET | /api/v1/estoque/{estoque_id} | `read_estoque_item(estoque_id, current_user, db)` |
| POST | /api/v1/estoque | `create_estoque_item(payload, current_user, db)` |
| PUT | /api/v1/estoque/{estoque_id} | `update_estoque_item(estoque_id, payload, current_user, db)` |
| DELETE | /api/v1/estoque/{estoque_id} | `delete_estoque_item(estoque_id, current_user, db)` |
| PUT | /api/v1/estoque/{estoque_id}/baixa | `baixa_estoque_item(estoque_id, payload, current_user, db)` |

### DashboardRouter (`dashboard.py`) — prefix: `/api/v1/dashboard` — cargo: 1
| Method | Path | Function |
|--------|------|----------|
| GET | /api/v1/dashboard/kpis | `read_kpis(current_user, db)` |
| GET | /api/v1/dashboard/charts/academico | `read_charts_academico(current_user, db)` |
| GET | /api/v1/dashboard/charts/logistica | `read_charts_logistica(current_user, db)` |

### HistoricoRouter (`historico.py`) — prefix: `/api/v1/historico` — cargo: 1, 3
| Method | Path | Function |
|--------|------|----------|
| GET | /api/v1/historico/matricula/{matricula_id} | `read_historico_by_matricula(matricula_id, current_user, db)` |

---

## LAYER 4 — SERVICE (DAO / Business Logic)

### Package: `backend/app/services/`

### AuthService (`auth_service.py`)
| Function | Returns | Exceptions |
|----------|---------|------------|
| `authenticate_user(db, email, senha)` | `Usuario` | `InvalidCredentialsError` |
| `build_login_response(usuario)` | `dict` | - |
| `process_forgot_password(db, email)` | `str` (token) | `EmailNotFoundError` |
| `process_reset_password(db, token, nova_senha, confirmar_senha)` | `void` | `PasswordsDoNotMatchError`, `InvalidResetTokenError` |

### AlunoService (`aluno_service.py`)
| Function | Returns | Exceptions |
|----------|---------|------------|
| `create_aluno(db, payload: AlunoCreateSchema)` | `Aluno` | - |
| `list_alunos(db)` | `list[Aluno]` | - |
| `get_aluno_by_id(db, aluno_id)` | `Aluno` | `AlunoNotFoundError` |
| `update_aluno(db, aluno_id, payload: AlunoUpdateSchema)` | `Aluno` | `AlunoNotFoundError`, `AlunoHasDependenciesError` |
| `delete_aluno(db, aluno_id)` | `void` | `AlunoNotFoundError`, `AlunoHasDependenciesError` |

### CursoService (`curso_service.py`)
| Function | Returns | Exceptions |
|----------|---------|------------|
| `create_curso(db, payload)` | `Curso` | - |
| `list_cursos(db)` | `list[Curso]` | - |
| `get_curso_by_id(db, curso_id)` | `Curso` | `CursoNotFoundError` |
| `update_curso(db, curso_id, payload)` | `Curso` | `CursoNotFoundError`, `CursoHasDependenciesError` |
| `delete_curso(db, curso_id)` | `void` | `CursoNotFoundError`, `CursoHasDependenciesError` |

### TurmaService (`turma_service.py`)
| Function | Returns | Exceptions |
|----------|---------|------------|
| `create_turma(db, payload: TurmaCreateSchema)` | `Turma` | `CursoNotFoundForTurmaError`, `ProfessorNotFoundForTurmaError` |
| `list_turmas(db)` | `list[Turma]` | - |
| `list_turmas_by_professor(db, professor_id)` | `list[Turma]` | - |
| `get_turma_by_id(db, turma_id)` | `Turma` | `TurmaNotFoundError` |
| `update_turma(db, turma_id, payload: TurmaUpdateSchema)` | `Turma` | `TurmaNotFoundError`, `TurmaHasDependenciesError` |
| `delete_turma(db, turma_id)` | `void` | `TurmaNotFoundError`, `TurmaHasDependenciesError` |

### MatriculaService (`matricula_service.py`)
| Function | Returns | Exceptions |
|----------|---------|------------|
| `create_matricula(db, payload: MatriculaCreateSchema)` | `Matricula` | `AlunoNotFoundForMatriculaError`, `TurmaNotFoundForMatriculaError`, `TurmaLotadaError`, `MatriculaDuplicadaError` |
| `list_matriculas(db)` | `list[Matricula]` | - |
| `list_matriculas_by_professor(db, professor_id)` | `list[Matricula]` | - |
| `get_matricula_by_id(db, matricula_id)` | `Matricula` | `MatriculaNotFoundError` |
| `update_matricula(db, matricula_id, payload)` | `Matricula` | `MatriculaNotFoundError`, `TurmaLotadaError`, `MatriculaDuplicadaError` |
| `delete_matricula(db, matricula_id)` | `void` | `MatriculaNotFoundError`, `MatriculaHasDependenciesError` |

### NotaService (`nota_service.py`)
| Function | Returns | Exceptions |
|----------|---------|------------|
| `create_or_update_notas(db, payload: NotaBatchSchema)` | `list[Nota]` | `InvalidMatriculasError` |
| `list_notas_by_matricula(db, matricula_id)` | `list[Nota]` | - |
| `list_notas_by_turma(db, turma_id, prova?)` | `list[Nota]` | - |
| `calcular_media_por_prova(db, turma_id)` | `list[MediaProvaSchema]` | - |

### PresencaService (`presenca_service.py`)
| Function | Returns |
|----------|---------|
| `create_or_update_presencas(db, payload: PresencaBatchSchema)` | `list[Presenca]` |
| `list_presencas_by_turma(db, turma_id, data_aula?)` | `list[Presenca]` |

### UsuarioService (`usuario_service.py`)
| Function | Returns | Exceptions |
|----------|---------|------------|
| `create_usuario(db, payload: UsuarioCreateSchema)` | `Usuario` | `UsuarioEmailAlreadyExistsError` |
| `list_usuarios(db)` | `list[Usuario]` | - |
| `get_usuario_by_id(db, usuario_id)` | `Usuario` | `UsuarioNotFoundError` |
| `update_usuario(db, usuario_id, payload)` | `Usuario` | `UsuarioNotFoundError` |
| `delete_usuario(db, usuario_id)` | `void` | `UsuarioNotFoundError`, `UsuarioHasDependenciesError` |

### PedidoService (`pedido_service.py`)
| Function | Returns | Exceptions |
|----------|---------|------------|
| `create_pedido(db, payload: PedidoCreateSchema, usuario_id)` | `Pedido` | `TurmaNotFoundForPedidoError` |
| `list_pedidos(db)` | `list[Pedido]` | - |
| `get_pedido_by_id(db, pedido_id)` | `Pedido` | `PedidoNotFoundError` |
| `aprovar_pedido(db, pedido_id)` | `Pedido` | `PedidoNotFoundError`, `PedidoInvalidTransitionError` |
| `comprar_pedido(db, pedido_id, payload: PedidoCompraSchema)` | `Pedido` | `PedidoNotFoundError`, `PedidoInvalidTransitionError` |
| `update_pedido_status(db, pedido_id, payload)` | `Pedido` | `PedidoNotFoundError` |
| `entregar_pedido(db, pedido_id)` | `Pedido` | `PedidoNotFoundError`, `PedidoInvalidTransitionError`, `PedidoCannotBeDeliveredError` |
| `delete_pedido(db, pedido_id)` | `void` | `PedidoNotFoundError`, `PedidoHasDependenciesError` |

### EstoqueService (`estoque_service.py`)
| Function | Returns | Exceptions |
|----------|---------|------------|
| `create_estoque(db, payload: EstoqueCreateSchema)` | `Estoque` | `EstoqueAlreadyExistsError` |
| `list_estoque(db)` | `list[Estoque]` | - |
| `search_estoque_by_name(db, term)` | `list[Estoque]` | - |
| `get_estoque_by_id(db, estoque_id)` | `Estoque` | `EstoqueNotFoundError` |
| `update_estoque(db, estoque_id, payload)` | `Estoque` | `EstoqueNotFoundError` |
| `delete_estoque(db, estoque_id)` | `void` | `EstoqueNotFoundError`, `EstoqueHasDependenciesError` |
| `dar_baixa(db, estoque_id, quantidade, justificativa)` | `Estoque` | `EstoqueNotFoundError`, `EstoqueSaldoInsuficienteError`, `EstoqueBaixaJustificativaError` |
| `get_alertas(db)` | `list[Estoque]` | - |
| `deduzir_por_pedido(db, pedido)` | `void` | `EstoqueNotFoundError`, `EstoqueSaldoInsuficienteError` |

### DashboardService (`dashboard_service.py`)
| Function | Returns |
|----------|---------|
| `get_kpis(db)` | `dict` |
| `get_chart_academico(db)` | `dict` |
| `get_chart_logistica(db)` | `dict` |

### HistoricoService (`historico_service.py`)
| Function | Returns | Exceptions |
|----------|---------|------------|
| `get_historico_by_matricula(db, matricula_id)` | `dict` | `MatriculaNotFoundError` |

### EmailService (`email_service.py`)
| Function | Returns |
|----------|---------|
| `send_reset_email(to_email, reset_token)` | `void` |

---

## LAYER 5 — CORE (Infrastructure)

### Package: `backend/app/core/` + `backend/app/db/`

### Settings (`core/config.py`)
+ `app_name: str` = "SGA ABACO API"
+ `database_url: str` (env: DATABASE_URL)
+ `secret_key: str` (env: SECRET_KEY/JWT_SECRET)
+ `jwt_algorithm: str` = "HS256"
+ `access_token_expire_minutes: int` = 120
+ `reset_token_expire_minutes: int` = 15
+ `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`, `smtp_from`
+ `frontend_url: str`
+ `cors_origins: str`
+ `rate_limit_auth: str` = "5/minute"
+ `rate_limit_default: str` = "60/minute"
+ `get_cors_origin_list() -> list[str]`

### SecurityUtils (`core/security.py`)
+ `verify_password(plain_password, password_hash) -> bool`
+ `hash_password(password) -> str`
+ `create_access_token(subject, cargo, expires_delta?) -> str`
+ `create_reset_token(email, expires_delta?) -> str`
+ `decode_reset_token(token) -> dict`

### AuthDependencies (`core/dependencies.py`)
+ `get_current_user(authorization?) -> dict`
+ `verify_cargo(*allowed_cargos) -> callable`
+ `verify_director_role()` (cargo=1)

### Database (`db/database.py`)
+ `engine: Engine`
+ `SessionLocal: sessionmaker`
+ `Base: declarative_base`
+ `get_db() -> Generator[Session]`

---

## LAYER 6 — VIEW (Angular Frontend)

### Package: `frontend/src/app/`

### Pages / Components

| Component | Route | Module |
|-----------|-------|--------|
| `LoginPage` | `/login` | Auth |
| `ForgotPasswordPage` | `/forgot-password` | Auth |
| `ResetPasswordPage` | `/reset-password` | Auth |
| `AdminHome` | `/admin/home` | Dashboard |
| `StudentsManagementComponent` | `/admin/alunos` | Students |
| `CoursesManagementComponent` | `/admin/cursos` | Courses |
| `ClassesManagementComponent` | `/admin/turmas` | Classes |
| `EnrollmentsManagementComponent` | `/admin/matriculas` | Enrollments |
| `GradesManagementComponent` | `/admin/notas` | Grades |
| `AttendanceManagementComponent` | `/admin/presencas` | Attendance |
| `EstoqueManagementComponent` | `/admin/logistico/estoque` | Logistico |
| `PedidoListComponent` | `/admin/logistico/pedidos` | Logistico |
| `PedidoFormPageComponent` | `/admin/logistico/pedidos/novo` | Logistico |
| `UsersManagementComponent` | `/admin/usuarios` | Users |
| `TranscriptViewComponent` | `/admin/historico/matricula/:id` | Transcript |
| `AcademicoHome` | `/academico` | Academico |
| `TurmaDetailPage` | `/academico/turmas/:id` | Academico |
| `AccessDenied` | `/acesso-negado` | Errors |
| `NotFound` | `/**` | Errors |

### Angular Services (`core/services/`)

| Service | API Prefix | Methods |
|---------|-----------|---------|
| `AlunoService` | `/api/v1/alunos` | `list()`, `create(payload)`, `update(id, payload)`, `delete(id)` |
| `AuthService` | `/api/v1/auth` | `login(email, password)`, `forgotPassword(email)`, `resetPassword(token, novaSenha, confirm)`, `logout()`, `isAuthenticated()`, `hasRole(roles)` |
| `CursoService` | `/api/v1/cursos` | `list()`, `create(payload)`, `update(id, payload)`, `delete(id)` |
| `TurmaService` | `/api/v1/turmas` | `list()`, `listMine()`, `getById(id)`, `create(payload)`, `update(id, payload)`, `delete(id)` |
| `MatriculaService` | `/api/v1/matriculas` | `list()`, `listMine()`, `create(payload)`, `update(id, payload)`, `delete(id)` |
| `NotaService` | `/api/v1/notas` | `listByTurma(id, prova?)`, `listByMatricula(id)`, `create(payload)`, `getMediaTurma(id)` |
| `PresencaService` | `/api/v1/presencas` | `listByTurma(id, dataAula?)`, `create(payload)` |
| `UsuarioService` | `/api/v1/usuarios` | `list()`, `create(payload)`, `update(id, payload)`, `delete(id)` |
| `PedidoService` | `/api/v1/pedidos` | `list()`, `create(payload)`, `aprovar(id)`, `comprar(id, payload)`, `entregar(id)`, `delete(id)` |
| `EstoqueService` | `/api/v1/estoque` | `list()`, `search(q)`, `create(payload)`, `update(id, payload)`, `delete(id)`, `baixa(id, payload)`, `getAlertas()` |
| `DashboardService` | `/api/v1/dashboard` | `getKpis()`, `getChartAcademico()`, `getChartLogistica()` |
| `HistoricoService` | `/api/v1/historico` | `getByMatricula(id)` |
| `NotificationService` | (in-app) | `error(message)`, `success(message)`, `clear()` |
| `DialogService` | (in-app) | `confirm(options)` |

### Guards & Interceptors

- `AuthGuard` (`core/guards/auth.guard.ts`) — checks JWT validity
- `RoleGuard` (`core/guards/role.guard.ts`) — checks cargo against allowed list
- `TokenInterceptor` (`core/interceptors/token.interceptor.ts`) — attaches Bearer token to requests
- `ErrorInterceptor` (`core/interceptors/error.interceptor.ts`) — handles 401/403/409 errors

---

## ARCHITECTURE OVERVIEW

```
[VIEW - Angular Components]  ──HTTP──>  [CONTROLLER - FastAPI Routers]
                                              |
                                         [SCHEMA - Pydantic DTOs]
                                              |
                                         [SERVICE - Business Logic]
                                              |
                                         [MODEL - SQLAlchemy ORM]
                                              |
                                         [PostgreSQL Database]
```

**Data Flow:**
1. View sends HTTP request → Controller
2. Controller validates via Schema (Pydantic)
3. Controller calls Service function
4. Service applies business rules, raises typed Exceptions
5. Service queries via Model (ORM) → Database
6. Response serialized via Schema → returned to View
