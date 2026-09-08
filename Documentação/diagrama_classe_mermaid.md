```mermaid
classDiagram

    %% ============================================================
    %% MODELS - backend/app/models/
    %% ============================================================

    namespace aluno {
        class Aluno {
            <<Entity>> tabela: aluno
            -id_aluno: int (PK)
            -nome: str (NOT NULL)
            -telefone: str?
            -data_nascimento: date?
            -rua: str?
            -bairro: str?
            -numero: int?
            +get_id_aluno() int
            +get_nome() str
            +get_telefone() str?
            +get_data_nascimento() date?
            +get_rua() str?
            +get_bairro() str?
            +get_numero() int?
        }
    }

    namespace curso {
        class Curso { <<Entity>> -id_curso: int (PK) ; -nome_curso: str ; +get_id_curso() int ; +get_nome_curso() str }
    }

    namespace turma {
        class Turma {
            <<Entity>>
            -id_turma: int (PK) ; -capacidade: int?
            -data_inicio: date? ; -data_fim: date?
            -id_curso: int (FK) ; -id_professor: int? (FK)
            -dias_aula: str? ; -avaliacoes: list? (JSONB)
            +vagas_ocupadas: int (readonly)
            +get_id_turma() int ; +get_capacidade() int?
            +get_data_inicio() date? ; +get_data_fim() date?
            +get_id_curso() int ; +get_id_professor() int?
            +get_dias_aula() str? ; +get_avaliacoes() list?
            +get_vagas_ocupadas() int
        }
    }

    namespace matricula {
        class Matricula { <<Entity>> -id_matricula: int (PK) ; -id_aluno: int (FK) ; -id_turma: int (FK) ; -data_matricula: date? ; -status: int? ; +get_id_matricula() int ; +get_id_aluno() int ; +get_id_turma() int ; +get_data_matricula() date? ; +get_status() int? }
    }

    namespace nota {
        class Nota { <<Entity>> -id_nota: int (PK) ; -nota: float? ; -prova: int? ; -id_matricula: int (FK) ; +get_id_nota() int ; +get_nota() float? ; +get_prova() int? ; +get_id_matricula() int }
    }

    namespace presenca {
        class Presenca { <<Entity>> -id_presenca: int (PK) ; -id_matricula: int (FK) ; -data_aula: date? ; -presente: bool? ; +get_id_presenca() int ; +get_id_matricula() int ; +get_data_aula() date? ; +get_presente() bool? }
    }

    namespace usuario {
        class Usuario { <<Entity>> -id_usuario: int (PK) ; -nome: str? ; -telefone: str? ; -email: str? (UNIQUE) ; -senha_hash: str? ; -cargo: int? ; +get_id_usuario() int ; +get_nome() str? ; +get_telefone() str? ; +get_email() str? ; +get_senha_hash() str? ; +get_cargo() int? }
    }

    namespace pedido {
        class Pedido { <<Entity>> -id_pedido: int (PK) ; -id_usuario: int (FK) ; -id_turma: int (FK) ; -data_pedido: date? ; -status: int? ; +get_id_pedido() int ; +get_id_usuario() int ; +get_id_turma() int ; +get_data_pedido() date? ; +get_status() int? }
    }

    namespace item_pedido {
        class ItemPedido { <<Entity>> -id_item_pedido: int (PK) ; -id_pedido: int (FK) ; -id_item_estoque: int? (FK) ; -nome_item: str? ; -quantidade: int? ; -preco_unitario: float? ; +get_id_item_pedido() int ; +get_id_pedido() int ; +get_id_item_estoque() int? ; +get_nome_item() str? ; +get_quantidade() int? ; +get_preco_unitario() float? }
    }

    namespace estoque {
        class Estoque { <<Entity>> -id_item_estoque: int (PK) ; -nome_item: str? ; -quantidade_disponivel: int? ; -unidade: str? ; -estoque_minimo: int? ; +get_id_item_estoque() int ; +get_nome_item() str? ; +get_quantidade_disponivel() int? ; +get_unidade() str? ; +get_estoque_minimo() int? }
    }

    namespace movimentacao_estoque {
        class MovimentacaoEstoque { <<Entity>> -id_movimentacao: int (PK) ; -id_item_estoque: int (FK) ; -quantidade: int ; -tipo_movimentacao: str ; -justificativa: str? ; -data_movimentacao: datetime ; +get_id_movimentacao() int ; +get_id_item_estoque() int ; +get_quantidade() int ; +get_tipo_movimentacao() str ; +get_justificativa() str? ; +get_data_movimentacao() datetime }
    }

    Aluno "1" --> "*" Matricula
    Curso "1" --> "*" Turma
    Turma "1" --> "*" Matricula
    Turma "*" --> "0..1" Usuario : professor
    Turma "1" --> "*" Pedido
    Matricula "1" --> "*" Nota
    Matricula "1" --> "*" Presenca
    Usuario "1" --> "*" Pedido : solicitante
    Pedido "1" --> "*" ItemPedido
    ItemPedido "*" --> "0..1" Estoque
    Estoque "1" --> "*" MovimentacaoEstoque


    %% ============================================================
    %% SCHEMAS - backend/app/schemas/
    %% ============================================================

    namespace aluno_schema {
        class AlunoCreateSchema { <<DTO>> +nome: str ; +telefone: str? ; +dataNascimento: date? ; +rua: str? ; +bairro: str? ; +numero: int? }
        class AlunoUpdateSchema { <<DTO>> +nome: str? ; +telefone: str? ; +dataNascimento: date? ; +rua: str? ; +bairro: str? ; +numero: int? }
        class AlunoResponseSchema { <<DTO>> +id_aluno (alias idAluno): int ; +nome: str ; +telefone: str? ; +data_nascimento (alias dataNascimento): date? ; +rua: str? ; +bairro: str? ; +numero: int? }
    }

    namespace auth_schema {
        class LoginRequest { <<DTO>> +email: EmailStr ; +senha: str }
        class TokenResponse { <<DTO>> +access_token: str ; +token_type: str = "bearer" ; +usuario: UsuarioResponse }
        class MessageResponse { <<DTO>> +message: str }
    }

    namespace curso_schema {
        class CursoCreateSchema { <<DTO>> +nomeCurso: str }
        class CursoResponseSchema { <<DTO>> +id_curso (alias idCurso): int ; +nome_curso (alias nomeCurso): str }
    }

    namespace dashboard_schema {
        class KpisResponse { <<DTO>> +total_alunos_ativos: int ; +total_turmas_vigentes: int ; +total_pedidos_pendentes: int ; +total_estoque_critico: int }
        class ChartAcademicoResponse { <<DTO>> +alunos_por_curso: list ; +status_matriculas: list }
        class ChartLogisticaResponse { <<DTO>> +consumo_mes_atual: list }
    }

    namespace estoque_schema {
        class EstoqueCreateSchema { <<DTO>> +nomeItem: str ; +quantidadeDisponivel: int? ; +unidade: str? ; +estoqueMinimo: int? }
        class EstoqueResponseSchema { <<DTO>> +id_item_estoque (alias idItemEstoque): int ; +nome_item (alias nomeItem): str? ; +quantidade_disponivel (alias quantidadeDisponivel): int? ; +unidade: str? ; +estoque_minimo (alias estoqueMinimo): int? }
        class EstoqueBaixaSchema { <<DTO>> +quantidade: int ; +justificativa: str }
    }

    namespace historico_schema {
        class HistoricoResponse { <<DTO>> +id_matricula (alias idMatricula): int ; +data_matricula (alias dataMatricula): date? ; +status: int? ; +aluno: HistoricoAlunoInfo ; +turma: HistoricoTurmaInfo ; +notas: list ; +presencas: list ; +percentual_frequencia (alias percentualFrequencia): float? }
    }

    namespace matricula_schema {
        class MatriculaCreateSchema { <<DTO>> +idAluno: int ; +idTurma: int ; +dataMatricula: date? ; +status: int? }
        class MatriculaResponseSchema { <<DTO>> +id_matricula (alias idMatricula): int ; +id_aluno (alias idAluno): int? ; +id_turma (alias idTurma): int? ; +data_matricula (alias dataMatricula): date? ; +status: int? ; +aluno: MatriculaAlunoInfo? ; +turma: MatriculaTurmaInfo? }
    }

    namespace nota_schema {
        class NotaBatchSchema { <<DTO>> +idTurma: int ; +prova: int ; +notas: list }
        class NotaResponseSchema { <<DTO>> +id_nota (alias idNota): int ; +id_matricula (alias idMatricula): int ; +nota: float? ; +prova: int? ; +matricula: NotaMatriculaInfo? }
        class MediaTurmaSchema { <<DTO>> +id_turma (alias idTurma): int ; +medias: list }
    }

    namespace pedido_schema {
        class PedidoCreateSchema { <<DTO>> +idTurma: int ; +dataPedido: date? ; +itens: list }
        class PedidoUpdateSchema { <<DTO>> +status: int }
        class PedidoCompraSchema { <<DTO>> +itens: list }
        class PedidoResponseSchema { <<DTO>> +id_pedido (alias idPedido): int ; +id_usuario (alias idUsuario): int ; +id_turma (alias idTurma): int ; +data_pedido (alias dataPedido): date? ; +status: int? ; +usuario: UsuarioPedidoInfo? ; +turma: TurmaPedidoInfo? ; +itens: list? }
    }

    namespace presenca_schema {
        class PresencaBatchSchema { <<DTO>> +idTurma: int ; +dataAula: date ; +presencas: list }
        class PresencaResponseSchema { <<DTO>> +id_presenca (alias idPresenca): int ; +id_matricula (alias idMatricula): int ; +data_aula (alias dataAula): date? ; +presente: bool? ; +matricula: PresencaMatriculaInfo? }
    }

    namespace turma_schema {
        class TurmaCreateSchema { <<DTO>> +capacidade: int? ; +dataInicio: date? ; +dataFim: date? ; +idCurso: int ; +idProfessor: int? ; +diasAula: str? ; +avaliacoes: list? }
        class TurmaResponseSchema { <<DTO>> +id_turma (alias idTurma): int ; +capacidade: int? ; +data_inicio (alias dataInicio): date? ; +data_fim (alias dataFim): date? ; +id_curso (alias idCurso): int ; +id_professor (alias idProfessor): int? ; +dias_aula (alias diasAula): str? ; +vagas_ocupadas (alias vagasOcupadas): int? ; +avaliacoes: list? ; +curso: TurmaCursoInfo? ; +professor: TurmaProfessorInfo? }
    }

    namespace usuario_schema {
        class UsuarioCreateSchema { <<DTO>> +nome: str ; +email: EmailStr ; +senha: str ; +cargo: int ; +telefone: str? }
        class UsuarioResponseSchema { <<DTO>> +id_usuario (alias idUsuario): int ; +nome: str? ; +telefone: str? ; +email: EmailStr? ; +cargo: int? }
    }


    %% ============================================================
    %% API / V1 - backend/app/api/v1/
    %% ============================================================

    namespace auth {
        class AuthRouter { <<Controller>> +login(payload, request, db) TokenResponse ; +forgot_password(payload, request, db) MessageResponse ; +reset_password(payload, request, db) MessageResponse }
    }

    namespace alunos {
        class AlunoRouter { <<Controller>> +read_alunos(current_user, db) list ; +read_aluno(aluno_id, current_user, db) AlunoResponseSchema ; +create_alunos(payload, current_user, db) AlunoResponseSchema ; +update_alunos(aluno_id, payload, current_user, db) AlunoResponseSchema ; +delete_alunos(aluno_id, current_user, db) dict }
    }

    namespace cursos {
        class CursoRouter { <<Controller>> +read_cursos(current_user, db) list ; +read_curso(curso_id, current_user, db) CursoResponseSchema ; +create_cursos(payload, current_user, db) CursoResponseSchema ; +update_cursos(curso_id, payload, current_user, db) CursoResponseSchema ; +delete_cursos(curso_id, current_user, db) dict }
    }

    namespace turmas {
        class TurmaRouter { <<Controller>> +read_turmas(current_user, db) list ; +read_minhas_turmas(current_user, db) list ; +read_turma(turma_id, current_user, db) TurmaResponseSchema ; +create_turmas(payload, current_user, db) TurmaResponseSchema ; +update_turmas(turma_id, payload, current_user, db) TurmaResponseSchema ; +delete_turmas(turma_id, current_user, db) dict }
    }

    namespace matriculas {
        class MatriculaRouter { <<Controller>> +read_matriculas(current_user, db) list ; +read_matriculas_by_professor(current_user, db) list ; +read_matricula(matricula_id, current_user, db) MatriculaResponseSchema ; +create_matriculas(payload, current_user, db) MatriculaResponseSchema ; +update_matriculas(matricula_id, payload, current_user, db) MatriculaResponseSchema ; +delete_matriculas(matricula_id, current_user, db) dict }
    }

    namespace notas {
        class NotaRouter { <<Controller>> +create_notas(payload, current_user, db) list ; +read_notas_by_matricula(matricula_id, current_user, db) list ; +read_notas_by_turma(turma_id, prova?, current_user, db) list ; +read_media_turma(turma_id, current_user, db) MediaTurmaSchema }
    }

    namespace presencas {
        class PresencaRouter { <<Controller>> +create_presencas(payload, current_user, db) list ; +read_presencas_by_turma(turma_id, dataAula?, current_user, db) list }
    }

    namespace usuarios {
        class UsuarioRouter { <<Controller>> +read_usuarios(current_user, db) list ; +read_usuario(usuario_id, current_user, db) UsuarioResponseSchema ; +create_usuarios(payload, current_user, db) UsuarioResponseSchema ; +update_usuarios(usuario_id, payload, current_user, db) UsuarioResponseSchema ; +delete_usuarios(usuario_id, current_user, db) dict }
    }

    namespace pedidos {
        class PedidoRouter { <<Controller>> +read_pedidos(current_user, db) list ; +read_pedido(pedido_id, current_user, db) PedidoResponseSchema ; +create_pedidos(payload, current_user, db) PedidoResponseSchema ; +aprovar_pedido_endpoint(pedido_id, current_user, db) PedidoResponseSchema ; +comprar_pedido_endpoint(pedido_id, payload, current_user, db) PedidoResponseSchema ; +update_pedidos(pedido_id, payload, current_user, db) PedidoResponseSchema ; +entregar_pedido_endpoint(pedido_id, current_user, db) PedidoResponseSchema ; +delete_pedidos(pedido_id, current_user, db) dict }
    }

    namespace estoque_api {
        class EstoqueRouter { <<Controller>> +read_estoque(current_user, db) list ; +search_estoque(q, current_user, db) list ; +read_alertas_estoque(current_user, db) list ; +read_estoque_item(estoque_id, current_user, db) EstoqueResponseSchema ; +create_estoque_item(payload, current_user, db) EstoqueResponseSchema ; +update_estoque_item(estoque_id, payload, current_user, db) EstoqueResponseSchema ; +delete_estoque_item(estoque_id, current_user, db) dict ; +baixa_estoque_item(estoque_id, payload, current_user, db) EstoqueResponseSchema }
    }

    namespace dashboard {
        class DashboardRouter { <<Controller>> +read_kpis(current_user, db) KpisResponse ; +read_charts_academico(current_user, db) ChartAcademicoResponse ; +read_charts_logistica(current_user, db) ChartLogisticaResponse }
    }

    namespace historico {
        class HistoricoRouter { <<Controller>> +read_historico_by_matricula(matricula_id, current_user, db) HistoricoResponse }
    }


    %% ============================================================
    %% CORE - backend/app/core/
    %% ============================================================

    namespace config {
        class Settings { <<Configuration>> +app_name: str ; +database_url: str ; +secret_key: str ; +jwt_algorithm: str ; +access_token_expire_minutes: int ; +reset_token_expire_minutes: int ; +frontend_url: str ; +get_cors_origin_list() list }
    }

    namespace security {
        class SecurityUtils { <<Utility>> +verify_password(plain, hash) bool ; +hash_password(password) str ; +create_access_token(subject, cargo, expires?) str ; +create_reset_token(email, expires?) str ; +decode_reset_token(token) dict }
    }

    namespace dependencies {
        class AuthDependencies { <<Utility>> +get_current_user(authorization?) dict ; +verify_cargo(*cargos) callable ; +verify_director_role() dict }
    }

    namespace limiter {
        class RateLimiter { <<Infrastructure>> +limiter: Limiter }
    }


    %% ============================================================
    %% DB - backend/app/db/
    %% ============================================================

    namespace database {
        class Database { <<Infrastructure>> +engine: Engine ; +SessionLocal: sessionmaker ; +Base: declarative_base ; +get_db() Generator~Session~ }
    }


    %% ============================================================
    %% SERVICES - backend/app/services/
    %% ============================================================

    namespace auth_service {
        class AuthService { <<Service>> +authenticate_user(db, email, senha) Usuario ; +build_login_response(usuario) dict ; +process_forgot_password(db, email) str ; +process_reset_password(db, token, nova_senha, confirmar_senha) void }
    }

    namespace aluno_service {
        class AlunoService { <<Service>> +create_aluno(db, payload) Aluno ; +list_alunos(db) list ; +get_aluno_by_id(db, aluno_id) Aluno ; +update_aluno(db, aluno_id, payload) Aluno ; +delete_aluno(db, aluno_id) void }
    }

    namespace curso_service {
        class CursoService { <<Service>> +create_curso(db, payload) Curso ; +list_cursos(db) list ; +get_curso_by_id(db, curso_id) Curso ; +update_curso(db, curso_id, payload) Curso ; +delete_curso(db, curso_id) void }
    }

    namespace turma_service {
        class TurmaService { <<Service>> +create_turma(db, payload) Turma ; +list_turmas(db) list ; +list_turmas_by_professor(db, professor_id) list ; +get_turma_by_id(db, turma_id) Turma ; +update_turma(db, turma_id, payload) Turma ; +delete_turma(db, turma_id) void }
    }

    namespace matricula_service {
        class MatriculaService { <<Service>> +create_matricula(db, payload) Matricula ; +list_matriculas(db) list ; +list_matriculas_by_professor(db, professor_id) list ; +get_matricula_by_id(db, matricula_id) Matricula ; +update_matricula(db, matricula_id, payload) Matricula ; +delete_matricula(db, matricula_id) void }
    }

    namespace nota_service {
        class NotaService { <<Service>> +create_or_update_notas(db, payload) list ; +list_notas_by_matricula(db, matricula_id) list ; +list_notas_by_turma(db, turma_id, prova?) list ; +calcular_media_por_prova(db, turma_id) list }
    }

    namespace presenca_service {
        class PresencaService { <<Service>> +create_or_update_presencas(db, payload) list ; +list_presencas_by_turma(db, turma_id, data_aula?) list }
    }

    namespace usuario_service {
        class UsuarioService { <<Service>> +create_usuario(db, payload) Usuario ; +list_usuarios(db) list ; +get_usuario_by_id(db, usuario_id) Usuario ; +update_usuario(db, usuario_id, payload) Usuario ; +delete_usuario(db, usuario_id) void }
    }

    namespace pedido_service {
        class PedidoService { <<Service>> +create_pedido(db, payload, usuario_id) Pedido ; +list_pedidos(db) list ; +get_pedido_by_id(db, pedido_id) Pedido ; +aprovar_pedido(db, pedido_id) Pedido ; +comprar_pedido(db, pedido_id, payload) Pedido ; +update_pedido_status(db, pedido_id, payload) Pedido ; +entregar_pedido(db, pedido_id) Pedido ; +delete_pedido(db, pedido_id) void }
    }

    namespace estoque_service {
        class EstoqueService { <<Service>> +create_estoque(db, payload) Estoque ; +list_estoque(db) list ; +search_estoque_by_name(db, term) list ; +get_estoque_by_id(db, estoque_id) Estoque ; +update_estoque(db, estoque_id, payload) Estoque ; +delete_estoque(db, estoque_id) void ; +dar_baixa(db, estoque_id, qtd, just) Estoque ; +get_alertas(db) list ; +deduzir_por_pedido(db, pedido) void }
    }

    namespace dashboard_service {
        class DashboardService { <<Service>> +get_kpis(db) dict ; +get_chart_academico(db) dict ; +get_chart_logistica(db) dict }
    }

    namespace historico_service {
        class HistoricoService { <<Service>> +get_historico_by_matricula(db, matricula_id) dict }
    }

    namespace email_service {
        class EmailService { <<Service>> +send_reset_email(to_email, reset_token) void }
    }


    %% ============================================================
    %% CROSS-LAYER DEPENDENCIES
    %% ============================================================

    AuthRouter ..> AuthService
    AuthRouter ..> EmailService
    AuthRouter ..> AuthDependencies
    AuthRouter ..> RateLimiter
    AlunoRouter ..> AlunoService
    AlunoRouter ..> AuthDependencies
    CursoRouter ..> CursoService
    CursoRouter ..> AuthDependencies
    TurmaRouter ..> TurmaService
    TurmaRouter ..> AuthDependencies
    MatriculaRouter ..> MatriculaService
    MatriculaRouter ..> AuthDependencies
    NotaRouter ..> NotaService
    NotaRouter ..> AuthDependencies
    PresencaRouter ..> PresencaService
    PresencaRouter ..> AuthDependencies
    UsuarioRouter ..> UsuarioService
    UsuarioRouter ..> AuthDependencies
    PedidoRouter ..> PedidoService
    PedidoRouter ..> AuthDependencies
    EstoqueRouter ..> EstoqueService
    EstoqueRouter ..> AuthDependencies
    DashboardRouter ..> DashboardService
    DashboardRouter ..> AuthDependencies
    HistoricoRouter ..> HistoricoService
    HistoricoRouter ..> AuthDependencies

    AuthService ..> Usuario
    AuthService ..> Database
    AuthService ..> SecurityUtils
    AlunoService ..> Aluno
    AlunoService ..> Database
    CursoService ..> Curso
    CursoService ..> Database
    TurmaService ..> Turma
    TurmaService ..> Curso
    TurmaService ..> Usuario
    TurmaService ..> Database
    MatriculaService ..> Aluno
    MatriculaService ..> Turma
    MatriculaService ..> Database
    NotaService ..> Nota
    NotaService ..> Matricula
    NotaService ..> Database
    PresencaService ..> Presenca
    PresencaService ..> Matricula
    PresencaService ..> Database
    UsuarioService ..> Usuario
    UsuarioService ..> Database
    PedidoService ..> Pedido
    PedidoService ..> ItemPedido
    PedidoService ..> Database
    EstoqueService ..> Estoque
    EstoqueService ..> MovimentacaoEstoque
    EstoqueService ..> Database
    DashboardService ..> Turma
    DashboardService ..> Pedido
    DashboardService ..> Estoque
    DashboardService ..> Matricula
    DashboardService ..> Database
    HistoricoService ..> Matricula
    HistoricoService ..> Aluno
    HistoricoService ..> Turma
    HistoricoService ..> Nota
    HistoricoService ..> Presenca
    HistoricoService ..> Database
    EmailService ..> Settings

    AuthDependencies ..> SecurityUtils
    AuthDependencies ..> Settings
    Database ..> Settings
```
