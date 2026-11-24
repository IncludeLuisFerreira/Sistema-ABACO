from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.turma import Turma
from app.schemas.turma_schema import TurmaCreateSchema, TurmaUpdateSchema


class TurmaNotFoundError(Exception):
    pass


class TurmaHasDependenciesError(Exception):
    pass


class CursoNotFoundForTurmaError(Exception):
    pass


class ProfessorNotFoundForTurmaError(Exception):
    pass


class ProfessorCargoInvalidoError(Exception):
    pass


class DatasInvalidasError(Exception):
    pass


class CampoObrigatorioError(Exception):
    def __init__(self, campo: str):
        self.campo = campo
        super().__init__(campo)


class CapacidadeAbaixoDasVagasError(Exception):
    def __init__(self, vagas: int):
        self.vagas = vagas
        super().__init__(vagas)


CAMPOS_OBRIGATORIOS_UPDATE = (
    "idCurso",
    "idProfessor",
    "capacidade",
    "dataInicio",
    "dataFim",
    "diasAula",
)


def _resolve_curso(db: Session, curso_id: int) -> None:
    from app.models.curso import Curso

    curso = db.query(Curso).filter(Curso.id_curso == curso_id).first()
    if not curso:
        raise CursoNotFoundForTurmaError


def _resolve_professor(db: Session, professor_id: int) -> None:
    from app.models.usuario import Usuario

    professor = db.query(Usuario).filter(Usuario.id_usuario == professor_id).first()
    if not professor:
        raise ProfessorNotFoundForTurmaError
    if professor.cargo != 2:
        raise ProfessorCargoInvalidoError


def _validate_datas(data_inicio: date, data_fim: date) -> None:
    if data_fim < data_inicio:
        raise DatasInvalidasError


def _count_vagas_ocupadas(db: Session, turma_id: int) -> int:
    from app.models.matricula import Matricula

    return (
        db.query(Matricula)
        .filter(Matricula.id_turma == turma_id, Matricula.status == 0)
        .count()
    )


def _reject_required_field_clearing(payload: TurmaUpdateSchema) -> None:
    for campo in CAMPOS_OBRIGATORIOS_UPDATE:
        if campo in payload.model_fields_set and getattr(payload, campo) is None:
            raise CampoObrigatorioError(campo)


def create_turma(db: Session, payload: TurmaCreateSchema) -> Turma:
    _resolve_curso(db, payload.idCurso)
    _resolve_professor(db, payload.idProfessor)
    _validate_datas(payload.dataInicio, payload.dataFim)

    turma = Turma(
        capacidade=payload.capacidade,
        data_inicio=payload.dataInicio,
        data_fim=payload.dataFim,
        id_curso=payload.idCurso,
        id_professor=payload.idProfessor,
        dias_aula=payload.diasAula,
        avaliacoes=(
            [avaliacao.model_dump() for avaliacao in payload.avaliacoes]
            if payload.avaliacoes is not None
            else None
        ),
    )
    db.add(turma)
    db.commit()
    db.refresh(turma)
    return turma


def list_turmas(db: Session) -> list[Turma]:
    return db.query(Turma).order_by(Turma.id_turma.desc()).all()


def list_turmas_by_professor(db: Session, professor_id: int) -> list[Turma]:
    return db.query(Turma).filter(Turma.id_professor == professor_id).order_by(Turma.id_turma.desc()).all()


def get_turma_by_id(db: Session, turma_id: int) -> Turma:
    turma = db.query(Turma).filter(Turma.id_turma == turma_id).first()
    if not turma:
        raise TurmaNotFoundError
    return turma


def update_turma(db: Session, turma_id: int, payload: TurmaUpdateSchema) -> Turma:
    turma = get_turma_by_id(db, turma_id)
    _reject_required_field_clearing(payload)

    if payload.idCurso is not None:
        _resolve_curso(db, payload.idCurso)

    if payload.idProfessor is not None:
        _resolve_professor(db, payload.idProfessor)

    if payload.capacidade is not None:
        vagas_ocupadas = _count_vagas_ocupadas(db, turma_id)
        if payload.capacidade < vagas_ocupadas:
            raise CapacidadeAbaixoDasVagasError(vagas_ocupadas)

    data_inicio = payload.dataInicio if payload.dataInicio is not None else turma.data_inicio
    data_fim = payload.dataFim if payload.dataFim is not None else turma.data_fim
    if data_inicio is not None and data_fim is not None:
        _validate_datas(data_inicio, data_fim)

    if payload.idCurso is not None:
        turma.id_curso = payload.idCurso
    if payload.idProfessor is not None:
        turma.id_professor = payload.idProfessor
    if payload.capacidade is not None:
        turma.capacidade = payload.capacidade
    if payload.dataInicio is not None:
        turma.data_inicio = payload.dataInicio
    if payload.dataFim is not None:
        turma.data_fim = payload.dataFim
    if payload.diasAula is not None:
        turma.dias_aula = payload.diasAula
    if payload.avaliacoes is not None:
        turma.avaliacoes = [avaliacao.model_dump() for avaliacao in payload.avaliacoes]

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise TurmaHasDependenciesError from exc

    db.refresh(turma)
    return turma


def delete_turma(db: Session, turma_id: int) -> None:
    turma = get_turma_by_id(db, turma_id)
    db.delete(turma)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise TurmaHasDependenciesError from exc
