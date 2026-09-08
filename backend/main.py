import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app.api.v1.alunos import router as alunos_router
from app.api.v1.auth import router as auth_router
from app.api.v1.cursos import router as cursos_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.estoque import router as estoque_router
from app.api.v1.historico import router as historico_router
from app.api.v1.matriculas import router as matriculas_router
from app.api.v1.notas import router as notas_router
from app.api.v1.pedidos import router as pedidos_router
from app.api.v1.presencas import router as presencas_router
from app.api.v1.turmas import router as turmas_router
from app.api.v1.usuarios import router as usuarios_router
from app.core.config import get_settings
from app.core.limiter import limiter
from app.db.database import SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="SGA ABACO API",
    description="API do Sistema de Gestão Acadêmica da Associação ABACO. "
                "Gerencia alunos, cursos, turmas, matrículas, presenças, notas, "
                "histórico escolar, pedidos de material e estoque.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "auth", "description": "Autenticação — login e recuperação de senha"},
        {"name": "alunos", "description": "Cadastro e gestão de alunos"},
        {"name": "cursos", "description": "Cadastro e gestão de cursos"},
        {"name": "turmas", "description": "Cadastro e gestão de turmas"},
        {"name": "matriculas", "description": "Matrícula de alunos em turmas"},
        {"name": "presencas", "description": "Registro e consulta de presenças"},
        {"name": "notas", "description": "Lançamento e consulta de notas e médias"},
        {"name": "historico", "description": "Geração de histórico escolar"},
        {"name": "usuarios", "description": "Gestão de usuários (restrito à diretoria)"},
        {"name": "dashboard", "description": "Indicadores e gráficos administrativos"},
        {"name": "estoque", "description": "Gestão de estoque e baixa de itens"},
        {"name": "pedidos", "description": "Pedidos de material — criar, aprovar, comprar, entregar"},
    ],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Tente novamente mais tarde."},
    )


@app.on_event("startup")
def seed_admin_user():
    if not settings.admin_seed_email or not settings.admin_seed_password:
        return

    from app.core.security import hash_password
    from app.models.curso import Curso
    from app.models.usuario import Usuario

    db = SessionLocal()
    try:
        existing = db.query(Usuario).filter(Usuario.email == settings.admin_seed_email).first()
        if not existing:
            admin = Usuario(
                nome="Administrador",
                email=settings.admin_seed_email,
                senha_hash=hash_password(settings.admin_seed_password),
                cargo=1,
            )
            db.add(admin)
            db.commit()
            logger.info("Admin user seeded: %s", settings.admin_seed_email)

        if db.query(Curso).count() > 0:
            return

        logger.info("Empty database detected, seeding test data...")
        _seed_test_data(db, hash_password)
    finally:
        db.close()


def _seed_test_data(db, hash_password_func):
    from app.models.aluno import Aluno
    from app.models.curso import Curso
    from app.models.estoque import Estoque
    from app.models.item_pedido import ItemPedido
    from app.models.matricula import Matricula
    from app.models.pedido import Pedido
    from app.models.turma import Turma
    from app.models.usuario import Usuario
    from datetime import date

    cursos = [
        Curso(nome_curso="Informática Básica"),
        Curso(nome_curso="Corte e Costura"),
        Curso(nome_curso="Administração"),
        Curso(nome_curso="Inglês Básico"),
        Curso(nome_curso="Espanhol"),
    ]
    db.add_all(cursos)
    db.flush()

    admin_user = Usuario(nome="Carlos Admin", email="admin2@abaco.org.br", senha_hash=hash_password_func("admin123"), cargo=3, telefone="11999990000")
    db.add(admin_user)
    db.flush()

    prof1 = Usuario(nome="Maria Silva", email="maria@abaco.org.br", senha_hash=hash_password_func("prof12345"), cargo=2, telefone="11988887777")
    prof2 = Usuario(nome="João Santos", email="joao@abaco.org.br", senha_hash=hash_password_func("prof12345"), cargo=2, telefone="11977776666")
    prof3 = Usuario(nome="Ana Costa", email="ana@abaco.org.br", senha_hash=hash_password_func("prof12345"), cargo=2, telefone="11966665555")
    prof4 = Usuario(nome="Paulo Lima", email="paulo@abaco.org.br", senha_hash=hash_password_func("prof12345"), cargo=2, telefone="11955554444")
    db.add_all([prof1, prof2, prof3, prof4])
    db.flush()

    alunos = [
        Aluno(nome="Pedro Alves", telefone="11911112222", data_nascimento=date(2000, 3, 15)),
        Aluno(nome="Carla Mendes", telefone="11922223333", data_nascimento=date(1998, 7, 22)),
        Aluno(nome="Lucas Oliveira", telefone="11933334444", data_nascimento=date(2002, 11, 8)),
        Aluno(nome="Juliana Freitas", telefone="11944445555", data_nascimento=date(1999, 1, 30)),
        Aluno(nome="Rafael Souza", telefone="11955556666", data_nascimento=date(2001, 5, 12)),
        Aluno(nome="Beatriz Lima", telefone="11966667777", data_nascimento=date(2000, 9, 3)),
        Aluno(nome="Gabriel Torres", telefone="11977778888", data_nascimento=date(2003, 4, 18)),
        Aluno(nome="Mariana Rocha", telefone="11988889999", data_nascimento=date(1997, 12, 25)),
        Aluno(nome="Fernando Dias", telefone="11912344321", data_nascimento=date(1999, 8, 10)),
        Aluno(nome="Patrícia Neves", telefone="11923455432", data_nascimento=date(2001, 2, 14)),
        Aluno(nome="Ricardo Moura", telefone="11934566543", data_nascimento=date(2000, 6, 30)),
        Aluno(nome="Tatiane Borges", telefone="11945677654", data_nascimento=date(2002, 10, 5)),
    ]
    db.add_all(alunos)
    db.flush()

    turmas = [
        Turma(id_curso=cursos[0].id_curso, id_professor=prof1.id_usuario, capacidade=20, data_inicio=date(2026, 6, 1), data_fim=date(2026, 9, 30), dias_aula="1,3,5",
              avaliacoes=[{"nome": "Prova 1", "tipo": "prova", "peso": 10}, {"nome": "Prova 2", "tipo": "prova", "peso": 10}, {"nome": "Trabalho Final", "tipo": "trabalho", "peso": 10}]),
        Turma(id_curso=cursos[0].id_curso, id_professor=prof1.id_usuario, capacidade=25, data_inicio=date(2026, 8, 1), data_fim=date(2026, 12, 15), dias_aula="2,4",
              avaliacoes=[{"nome": "Prova 1", "tipo": "prova", "peso": 10}, {"nome": "Prova 2", "tipo": "prova", "peso": 10}]),
        Turma(id_curso=cursos[1].id_curso, id_professor=prof2.id_usuario, capacidade=15, data_inicio=date(2026, 5, 1), data_fim=date(2026, 8, 30), dias_aula="1,3,5",
              avaliacoes=[{"nome": "Prova Única", "tipo": "prova", "peso": 10}, {"nome": "Trabalho Prático", "tipo": "trabalho", "peso": 10}]),
        Turma(id_curso=cursos[2].id_curso, id_professor=prof3.id_usuario, capacidade=30, data_inicio=date(2026, 7, 1), data_fim=date(2026, 10, 30), dias_aula="2,4,6",
              avaliacoes=[{"nome": "Prova 1", "tipo": "prova", "peso": 10}, {"nome": "Prova 2", "tipo": "prova", "peso": 10}, {"nome": "Prova 3", "tipo": "prova", "peso": 10}, {"nome": "Prova 4", "tipo": "prova", "peso": 10}]),
        Turma(id_curso=cursos[3].id_curso, id_professor=prof2.id_usuario, capacidade=18, data_inicio=date(2026, 6, 15), data_fim=date(2026, 12, 15), dias_aula="2,4",
              avaliacoes=[{"nome": "Listening", "tipo": "prova", "peso": 5}, {"nome": "Speaking", "tipo": "trabalho", "peso": 5}, {"nome": "Written Test", "tipo": "prova", "peso": 10}]),
        Turma(id_curso=cursos[4].id_curso, id_professor=prof4.id_usuario, capacidade=12, data_inicio=date(2026, 8, 1), data_fim=date(2026, 11, 30), dias_aula="1,3",
              avaliacoes=[{"nome": "Prova Oral", "tipo": "trabalho", "peso": 10}, {"nome": "Prova Escrita", "tipo": "prova", "peso": 10}]),
    ]
    db.add_all(turmas)
    db.flush()

    matriculas = [
        Matricula(id_aluno=alunos[0].id_aluno, id_turma=turmas[0].id_turma, data_matricula=date(2026, 5, 20), status=0),
        Matricula(id_aluno=alunos[1].id_aluno, id_turma=turmas[0].id_turma, data_matricula=date(2026, 5, 21), status=0),
        Matricula(id_aluno=alunos[2].id_aluno, id_turma=turmas[0].id_turma, data_matricula=date(2026, 5, 22), status=0),
        Matricula(id_aluno=alunos[3].id_aluno, id_turma=turmas[1].id_turma, data_matricula=date(2026, 7, 20), status=0),
        Matricula(id_aluno=alunos[4].id_aluno, id_turma=turmas[1].id_turma, data_matricula=date(2026, 7, 21), status=0),
        Matricula(id_aluno=alunos[5].id_aluno, id_turma=turmas[2].id_turma, data_matricula=date(2026, 4, 15), status=0),
        Matricula(id_aluno=alunos[6].id_aluno, id_turma=turmas[2].id_turma, data_matricula=date(2026, 4, 16), status=0),
        Matricula(id_aluno=alunos[7].id_aluno, id_turma=turmas[2].id_turma, data_matricula=date(2026, 4, 17), status=0),
        Matricula(id_aluno=alunos[8].id_aluno, id_turma=turmas[3].id_turma, data_matricula=date(2026, 6, 25), status=0),
        Matricula(id_aluno=alunos[9].id_aluno, id_turma=turmas[3].id_turma, data_matricula=date(2026, 6, 26), status=0),
        Matricula(id_aluno=alunos[10].id_aluno, id_turma=turmas[4].id_turma, data_matricula=date(2026, 6, 10), status=0),
        Matricula(id_aluno=alunos[11].id_aluno, id_turma=turmas[4].id_turma, data_matricula=date(2026, 6, 12), status=0),
    ]
    db.add_all(matriculas)
    db.flush()

    pedidos = [
        Pedido(id_usuario=prof1.id_usuario, id_turma=turmas[0].id_turma, data_pedido=date(2026, 6, 10), status=0),
        Pedido(id_usuario=prof2.id_usuario, id_turma=turmas[2].id_turma, data_pedido=date(2026, 5, 20), status=1),
        Pedido(id_usuario=prof3.id_usuario, id_turma=turmas[3].id_turma, data_pedido=date(2026, 7, 5), status=2),
    ]
    db.add_all(pedidos)
    db.flush()

    itens_pedido = [
        ItemPedido(id_pedido=pedidos[0].id_pedido, nome_item="Caneta esferográfica", quantidade=50, id_item_estoque=1),
        ItemPedido(id_pedido=pedidos[0].id_pedido, nome_item="Caderno universitário", quantidade=30, id_item_estoque=2),
        ItemPedido(id_pedido=pedidos[1].id_pedido, nome_item="Lápis HB", quantidade=40, id_item_estoque=3),
        ItemPedido(id_pedido=pedidos[1].id_pedido, nome_item="Tesoura escolar", quantidade=15, id_item_estoque=6),
        ItemPedido(id_pedido=pedidos[2].id_pedido, nome_item="Papel sulfite A4 (resma)", quantidade=8, id_item_estoque=5),
    ]
    db.add_all(itens_pedido)

    estoque = [
        Estoque(nome_item="Caneta esferográfica", quantidade_disponivel=200, unidade="un", estoque_minimo=50),
        Estoque(nome_item="Caderno universitário", quantidade_disponivel=80, unidade="un", estoque_minimo=20),
        Estoque(nome_item="Lápis HB", quantidade_disponivel=5, unidade="un", estoque_minimo=30),
        Estoque(nome_item="Borracha branca", quantidade_disponivel=60, unidade="un", estoque_minimo=15),
        Estoque(nome_item="Papel sulfite A4 (resma)", quantidade_disponivel=12, unidade="resma", estoque_minimo=5),
        Estoque(nome_item="Tesoura escolar", quantidade_disponivel=3, unidade="un", estoque_minimo=10),
    ]
    db.add_all(estoque)

    db.commit()
    logger.info("Test data seeded: %d cursos, %d professores, %d alunos, %d turmas, %d matrículas, %d itens estoque",
                len(cursos), 3, len(alunos), len(turmas), len(matriculas), len(estoque))


app.include_router(alunos_router)
app.include_router(auth_router)
app.include_router(cursos_router)
app.include_router(dashboard_router)
app.include_router(estoque_router)
app.include_router(historico_router)
app.include_router(matriculas_router)
app.include_router(notas_router)
app.include_router(pedidos_router)
app.include_router(presencas_router)
app.include_router(turmas_router)
app.include_router(usuarios_router)


@app.get("/api/health")
def health_check():
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok", "database": "connected" if db_ok else "disconnected"}


@app.get("/")
def read_root():
    return {"status": "API online e rodando perfeitamente"}
