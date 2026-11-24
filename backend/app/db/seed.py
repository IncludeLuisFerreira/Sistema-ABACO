"""Seed idempotente de dados de teste.

Execute sob demanda com ``python -m app.db.seed``. No boot, o app só roda o seed
quando ``SEED_ON_STARTUP`` está ativo (ver ``main.lifespan``).
"""

import logging
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.estoque import Estoque
from app.models.item_pedido import ItemPedido
from app.models.matricula import Matricula
from app.models.pedido import Pedido
from app.models.turma import Turma
from app.models.usuario import Usuario

logger = logging.getLogger(__name__)

CURSOS = (
    "Informática Básica",
    "Corte e Costura",
    "Administração",
    "Inglês Básico",
    "Espanhol",
)

# (nome, email, cargo, telefone, chave da senha em Settings)
USUARIOS = (
    ("Carlos Admin", "admin2@abaco.org.br", 3, "11999990000", "seed_admin_password"),
    ("Maria Silva", "maria@abaco.org.br", 2, "11988887777", "seed_professor_password"),
    ("João Santos", "joao@abaco.org.br", 2, "11977776666", "seed_professor_password"),
    ("Ana Costa", "ana@abaco.org.br", 2, "11966665555", "seed_professor_password"),
    ("Paulo Lima", "paulo@abaco.org.br", 2, "11955554444", "seed_professor_password"),
)

ALUNOS = (
    ("Pedro Alves", "11911112222", date(2000, 3, 15)),
    ("Carla Mendes", "11922223333", date(1998, 7, 22)),
    ("Lucas Oliveira", "11933334444", date(2002, 11, 8)),
    ("Juliana Freitas", "11944445555", date(1999, 1, 30)),
    ("Rafael Souza", "11955556666", date(2001, 5, 12)),
    ("Beatriz Lima", "11966667777", date(2000, 9, 3)),
    ("Gabriel Torres", "11977778888", date(2003, 4, 18)),
    ("Mariana Rocha", "11988889999", date(1997, 12, 25)),
    ("Fernando Dias", "11912344321", date(1999, 8, 10)),
    ("Patrícia Neves", "11923455432", date(2001, 2, 14)),
    ("Ricardo Moura", "11934566543", date(2000, 6, 30)),
    ("Tatiane Borges", "11945677654", date(2002, 10, 5)),
)

ESTOQUE = (
    ("Caneta esferográfica", 200, "un", 50),
    ("Caderno universitário", 80, "un", 20),
    ("Lápis HB", 5, "un", 30),
    ("Borracha branca", 60, "un", 15),
    ("Papel sulfite A4 (resma)", 12, "resma", 5),
    ("Tesoura escolar", 3, "un", 10),
)

# (curso, professor, capacidade, inicio, fim, dias de aula, avaliações)
TURMAS = (
    ("Informática Básica", "maria@abaco.org.br", 20, date(2026, 6, 1), date(2026, 9, 30), "1,3,5",
     [{"nome": "Prova 1", "tipo": "prova", "peso": 10},
      {"nome": "Prova 2", "tipo": "prova", "peso": 10},
      {"nome": "Trabalho Final", "tipo": "trabalho", "peso": 10}]),
    ("Informática Básica", "maria@abaco.org.br", 25, date(2026, 8, 1), date(2026, 12, 15), "2,4",
     [{"nome": "Prova 1", "tipo": "prova", "peso": 10},
      {"nome": "Prova 2", "tipo": "prova", "peso": 10}]),
    ("Corte e Costura", "joao@abaco.org.br", 15, date(2026, 5, 1), date(2026, 8, 30), "1,3,5",
     [{"nome": "Prova Única", "tipo": "prova", "peso": 10},
      {"nome": "Trabalho Prático", "tipo": "trabalho", "peso": 10}]),
    ("Administração", "ana@abaco.org.br", 30, date(2026, 7, 1), date(2026, 10, 30), "2,4,6",
     [{"nome": "Prova 1", "tipo": "prova", "peso": 10},
      {"nome": "Prova 2", "tipo": "prova", "peso": 10},
      {"nome": "Prova 3", "tipo": "prova", "peso": 10},
      {"nome": "Prova 4", "tipo": "prova", "peso": 10}]),
    ("Inglês Básico", "joao@abaco.org.br", 18, date(2026, 6, 15), date(2026, 12, 15), "2,4",
     [{"nome": "Listening", "tipo": "prova", "peso": 5},
      {"nome": "Speaking", "tipo": "trabalho", "peso": 5},
      {"nome": "Written Test", "tipo": "prova", "peso": 10}]),
    ("Espanhol", "paulo@abaco.org.br", 12, date(2026, 8, 1), date(2026, 11, 30), "1,3",
     [{"nome": "Prova Oral", "tipo": "trabalho", "peso": 10},
      {"nome": "Prova Escrita", "tipo": "prova", "peso": 10}]),
)

# (índice do aluno em ALUNOS, índice da turma em TURMAS, data da matrícula)
MATRICULAS = (
    (0, 0, date(2026, 5, 20)),
    (1, 0, date(2026, 5, 21)),
    (2, 0, date(2026, 5, 22)),
    (3, 1, date(2026, 7, 20)),
    (4, 1, date(2026, 7, 21)),
    (5, 2, date(2026, 4, 15)),
    (6, 2, date(2026, 4, 16)),
    (7, 2, date(2026, 4, 17)),
    (8, 3, date(2026, 6, 25)),
    (9, 3, date(2026, 6, 26)),
    (10, 4, date(2026, 6, 10)),
    (11, 4, date(2026, 6, 12)),
)

# (email do solicitante, índice da turma em TURMAS, data do pedido, status)
PEDIDOS = (
    ("maria@abaco.org.br", 0, date(2026, 6, 10), 0),
    ("joao@abaco.org.br", 2, date(2026, 5, 20), 1),
    ("ana@abaco.org.br", 3, date(2026, 7, 5), 2),
)

# (índice do pedido em PEDIDOS, nome do item, quantidade, nome do item no estoque)
ITENS_PEDIDO = (
    (0, "Caneta esferográfica", 50, "Caneta esferográfica"),
    (0, "Caderno universitário", 30, "Caderno universitário"),
    (1, "Lápis HB", 40, "Lápis HB"),
    (1, "Tesoura escolar", 15, "Tesoura escolar"),
    (2, "Papel sulfite A4 (resma)", 8, "Papel sulfite A4 (resma)"),
)

COUNT_KEYS = (
    "cursos",
    "usuarios",
    "alunos",
    "estoque",
    "turmas",
    "matriculas",
    "pedidos",
    "itens_pedido",
)


def _senha_do_usuario(settings, campo: str) -> str | None:
    senha = getattr(settings, campo, None)
    return senha if senha else None


def _get_or_create_curso(db: Session, nome: str) -> tuple[Curso, bool]:
    curso = (
        db.query(Curso)
        .filter(func.lower(Curso.nome_curso) == nome.lower())
        .first()
    )
    if curso is not None:
        return curso, False
    curso = Curso(nome_curso=nome)
    db.add(curso)
    db.flush()
    return curso, True


def _buscar_usuario(db: Session, email: str) -> Usuario | None:
    return (
        db.query(Usuario)
        .filter(func.lower(Usuario.email) == email.lower())
        .first()
    )


def _get_or_create_usuario(
    db: Session,
    nome: str,
    email: str,
    cargo: int,
    senha: str,
    telefone: str | None = None,
) -> tuple[Usuario, bool]:
    usuario = _buscar_usuario(db, email)
    if usuario is not None:
        return usuario, False
    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=hash_password(senha),
        cargo=cargo,
        telefone=telefone,
        primeiro_acesso=False,
    )
    db.add(usuario)
    db.flush()
    return usuario, True


def _get_or_create_aluno(db: Session, nome: str, telefone: str, nascimento: date) -> tuple[Aluno, bool]:
    aluno = db.query(Aluno).filter(Aluno.nome == nome).first()
    if aluno is not None:
        return aluno, False
    aluno = Aluno(nome=nome, telefone=telefone, data_nascimento=nascimento)
    db.add(aluno)
    db.flush()
    return aluno, True


def _get_or_create_estoque(
    db: Session,
    nome: str,
    quantidade: int,
    unidade: str,
    minimo: int,
) -> tuple[Estoque, bool]:
    item = (
        db.query(Estoque)
        .filter(func.lower(Estoque.nome_item) == nome.lower())
        .first()
    )
    if item is not None:
        return item, False
    item = Estoque(
        nome_item=nome,
        quantidade_disponivel=quantidade,
        unidade=unidade,
        estoque_minimo=minimo,
    )
    db.add(item)
    db.flush()
    return item, True


def _get_or_create_turma(
    db: Session,
    curso: Curso,
    professor: Usuario,
    capacidade: int,
    inicio: date,
    fim: date,
    dias_aula: str,
    avaliacoes: list[dict],
) -> tuple[Turma, bool]:
    turma = (
        db.query(Turma)
        .filter(
            Turma.id_curso == curso.id_curso,
            Turma.id_professor == professor.id_usuario,
            Turma.data_inicio == inicio,
        )
        .first()
    )
    if turma is not None:
        return turma, False
    turma = Turma(
        id_curso=curso.id_curso,
        id_professor=professor.id_usuario,
        capacidade=capacidade,
        data_inicio=inicio,
        data_fim=fim,
        dias_aula=dias_aula,
        avaliacoes=avaliacoes,
    )
    db.add(turma)
    db.flush()
    return turma, True


def _get_or_create_matricula(
    db: Session,
    aluno: Aluno,
    turma: Turma,
    data_matricula: date,
) -> tuple[Matricula, bool]:
    matricula = (
        db.query(Matricula)
        .filter(Matricula.id_aluno == aluno.id_aluno, Matricula.id_turma == turma.id_turma)
        .first()
    )
    if matricula is not None:
        return matricula, False
    matricula = Matricula(
        id_aluno=aluno.id_aluno,
        id_turma=turma.id_turma,
        data_matricula=data_matricula,
        status=0,
    )
    db.add(matricula)
    db.flush()
    return matricula, True


def _get_or_create_pedido(
    db: Session,
    solicitante: Usuario,
    turma: Turma,
    data_pedido: date,
    status: int,
) -> tuple[Pedido, bool]:
    pedido = (
        db.query(Pedido)
        .filter(
            Pedido.id_usuario == solicitante.id_usuario,
            Pedido.id_turma == turma.id_turma,
            Pedido.data_pedido == data_pedido,
            Pedido.status == status,
        )
        .first()
    )
    if pedido is not None:
        return pedido, False
    pedido = Pedido(
        id_usuario=solicitante.id_usuario,
        id_turma=turma.id_turma,
        data_pedido=data_pedido,
        status=status,
    )
    db.add(pedido)
    db.flush()
    return pedido, True


def _get_or_create_item_pedido(
    db: Session,
    pedido: Pedido,
    estoque: Estoque,
    nome_item: str,
    quantidade: int,
) -> tuple[ItemPedido, bool]:
    item = (
        db.query(ItemPedido)
        .filter(ItemPedido.id_pedido == pedido.id_pedido, ItemPedido.nome_item == nome_item)
        .first()
    )
    if item is not None:
        return item, False
    item = ItemPedido(
        id_pedido=pedido.id_pedido,
        id_item_estoque=estoque.id_item_estoque,
        nome_item=nome_item,
        quantidade=quantidade,
    )
    db.add(item)
    db.flush()
    return item, True


def _run_seed(db: Session, counts: dict[str, int], settings) -> None:
    cursos: dict[str, Curso] = {}
    for nome in CURSOS:
        curso, criado = _get_or_create_curso(db, nome)
        cursos[nome] = curso
        counts["cursos"] += int(criado)

    usuarios: dict[str, Usuario] = {}
    if settings.admin_seed_email:
        diretor = _buscar_usuario(db, settings.admin_seed_email)
        if diretor is not None:
            usuarios[settings.admin_seed_email] = diretor
        elif settings.admin_seed_password:
            diretor, criado = _get_or_create_usuario(
                db,
                nome="Administrador",
                email=settings.admin_seed_email,
                cargo=1,
                senha=settings.admin_seed_password,
            )
            usuarios[settings.admin_seed_email] = diretor
            counts["usuarios"] += int(criado)
        else:
            logger.warning(
                "ADMIN_SEED_PASSWORD ausente; diretor %s nao encontrado no banco e nao sera criado",
                settings.admin_seed_email,
            )
    else:
        logger.warning("ADMIN_SEED_EMAIL ausente; diretor inicial nao sera criado")

    senhas_ausentes: set[str] = set()
    for nome, email, cargo, telefone, campo_senha in USUARIOS:
        usuario = _buscar_usuario(db, email)
        if usuario is not None:
            usuarios[email] = usuario
            continue

        senha = _senha_do_usuario(settings, campo_senha)
        if senha is None:
            senhas_ausentes.add(campo_senha)
            continue
        usuario, criado = _get_or_create_usuario(db, nome, email, cargo, senha, telefone)
        usuarios[email] = usuario
        counts["usuarios"] += int(criado)

    for campo in sorted(senhas_ausentes):
        logger.warning(
            "%s ausente; usuarios de teste ainda nao cadastrados serao pulados",
            campo.upper(),
        )

    alunos: list[Aluno] = []
    for nome, telefone, nascimento in ALUNOS:
        aluno, criado = _get_or_create_aluno(db, nome, telefone, nascimento)
        alunos.append(aluno)
        counts["alunos"] += int(criado)

    estoque_por_nome: dict[str, Estoque] = {}
    for nome, quantidade, unidade, minimo in ESTOQUE:
        item, criado = _get_or_create_estoque(db, nome, quantidade, unidade, minimo)
        estoque_por_nome[nome.lower()] = item
        counts["estoque"] += int(criado)

    turmas: list[Turma | None] = []
    for curso_nome, professor_email, capacidade, inicio, fim, dias_aula, avaliacoes in TURMAS:
        professor = usuarios.get(professor_email)
        if professor is None:
            logger.warning("Professor %s ausente; turma de %s sera pulada", professor_email, curso_nome)
            turmas.append(None)
            continue
        turma, criado = _get_or_create_turma(
            db,
            cursos[curso_nome],
            professor,
            capacidade,
            inicio,
            fim,
            dias_aula,
            avaliacoes,
        )
        turmas.append(turma)
        counts["turmas"] += int(criado)

    for aluno_idx, turma_idx, data_matricula in MATRICULAS:
        turma = turmas[turma_idx]
        if turma is None:
            continue
        _, criado = _get_or_create_matricula(db, alunos[aluno_idx], turma, data_matricula)
        counts["matriculas"] += int(criado)

    pedidos: list[Pedido | None] = []
    for solicitante_email, turma_idx, data_pedido, status in PEDIDOS:
        solicitante = usuarios.get(solicitante_email)
        turma = turmas[turma_idx]
        if solicitante is None or turma is None:
            logger.warning("Pedido de %s sera pulado: solicitante ou turma ausente", solicitante_email)
            pedidos.append(None)
            continue
        pedido, criado = _get_or_create_pedido(db, solicitante, turma, data_pedido, status)
        pedidos.append(pedido)
        counts["pedidos"] += int(criado)

    for pedido_idx, nome_item, quantidade, estoque_nome in ITENS_PEDIDO:
        pedido = pedidos[pedido_idx]
        estoque = estoque_por_nome.get(estoque_nome.lower())
        if pedido is None or estoque is None:
            logger.warning("Item de pedido %s sera pulado: pedido ou estoque ausente", nome_item)
            continue
        _, criado = _get_or_create_item_pedido(db, pedido, estoque, nome_item, quantidade)
        counts["itens_pedido"] += int(criado)


def run_seed(db: Session) -> dict[str, int]:
    """Cria os dados de teste que ainda não existem e devolve a contagem por entidade.

    A sessão recebida é usada como unidade de trabalho: em erro, a transação é
    revertida e a exceção propagada para o chamador.
    """
    counts = {chave: 0 for chave in COUNT_KEYS}
    try:
        _run_seed(db, counts, get_settings())
        db.commit()
    except Exception:
        db.rollback()
        raise
    return counts


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    db = SessionLocal()
    try:
        counts = run_seed(db)
    finally:
        db.close()
    logger.info("Seed executado: %s", counts)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
