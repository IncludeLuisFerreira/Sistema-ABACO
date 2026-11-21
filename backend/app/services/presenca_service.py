from datetime import date

from sqlalchemy.orm import Session

from app.models.matricula import Matricula
from app.models.presenca import Presenca
from app.schemas.presenca_schema import PresencaBatchSchema


class TurmaNotFoundForPresencaError(Exception):
    pass


class InvalidMatriculasError(Exception):
    def __init__(self, ids_invalidos: list[int]) -> None:
        self.ids_invalidos = ids_invalidos
        super().__init__(f"Matriculas invalidas na turma: {ids_invalidos}")


def create_or_update_presencas(db: Session, payload: PresencaBatchSchema) -> list[Presenca]:
    matriculas = db.query(Matricula).filter(
        Matricula.id_turma == payload.idTurma,
        Matricula.status == 0,
    ).all()

    matriculas_por_id = {m.id_matricula for m in matriculas}

    ids_invalidos = list(
        dict.fromkeys(
            item.idMatricula for item in payload.presencas
            if item.idMatricula not in matriculas_por_id
        )
    )
    if ids_invalidos:
        raise InvalidMatriculasError(ids_invalidos)

    criadas: list[Presenca] = []

    for item in payload.presencas:
        # REFACTOR: N+1 — consulta Presenca por item do batch
        presenca = db.query(Presenca).filter(
            Presenca.id_matricula == item.idMatricula,
            Presenca.data_aula == payload.dataAula,
        ).first()

        if presenca:
            presenca.presente = item.presente
        else:
            presenca = Presenca(
                id_matricula=item.idMatricula,
                data_aula=payload.dataAula,
                presente=item.presente,
            )
            db.add(presenca)

        criadas.append(presenca)

    db.commit()

    for p in criadas:
        db.refresh(p)

    return criadas


def list_presencas_by_turma(db: Session, turma_id: int, data_aula: date | None = None) -> list[Presenca]:
    query = db.query(Presenca).join(
        Matricula, Presenca.id_matricula == Matricula.id_matricula
    ).filter(
        Matricula.id_turma == turma_id,
    )

    if data_aula is not None:
        query = query.filter(Presenca.data_aula == data_aula)

    return query.order_by(Presenca.data_aula.desc(), Presenca.id_presenca).all()
