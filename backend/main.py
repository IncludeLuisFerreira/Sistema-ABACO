import logging
from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.seed_on_startup and not settings.is_production:
        from app.db.seed import run_seed

        db = SessionLocal()
        try:
            counts = run_seed(db)
            logger.info("Seed de dados de teste executado no boot: %s", counts)
        except Exception:
            logger.exception("Seed de dados de teste falhou no boot; startup segue sem seed")
            db.rollback()
        finally:
            db.close()
    yield


app = FastAPI(
    title="SGA ABACO API",
    description="API do Sistema de Gestão Acadêmica da Associação ABACO. "
                "Gerencia alunos, cursos, turmas, matrículas, presenças, notas, "
                "histórico escolar, pedidos de material e estoque.",
    version="1.0.0",
    lifespan=lifespan,
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
        {"name": "usuarios", "description": "Gestão de usuários (restrito à diretoria e administradores)"},
        {"name": "dashboard", "description": "Indicadores e gráficos administrativos"},
        {"name": "estoque", "description": "Gestão de estoque e baixa de itens"},
        {"name": "pedidos", "description": "Pedidos de material — criar, aprovar, comprar, entregar"},
    ],
)

app.state.limiter = limiter
# HACK: usa handler privado (_rate_limit_exceeded_handler) do slowapi, sujeito a quebra
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Tente novamente mais tarde."},
    )


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
    # FIXME: engole Exception e sempre retorna HTTP 200, mesmo com banco fora
    except Exception:
        db_ok = False
    return {"status": "ok", "database": "connected" if db_ok else "disconnected"}


@app.get("/")
def read_root():
    return {"status": "API online e rodando perfeitamente"}
