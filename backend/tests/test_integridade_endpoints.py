from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def _commit_falha():
    raise IntegrityError("INSERT", {}, Exception("violacao de integridade"))


def test_post_alunos_integrity_error_retorna_409(
    api_client, director_headers, db_session: Session, monkeypatch
) -> None:
    monkeypatch.setattr(db_session, "commit", _commit_falha)

    resposta = api_client.post(
        "/api/v1/alunos", json={"nome": "Aluno Duplicado"}, headers=director_headers
    )

    assert resposta.status_code == 409


def test_post_cursos_integrity_error_retorna_409(
    api_client, director_headers, db_session: Session, monkeypatch
) -> None:
    monkeypatch.setattr(db_session, "commit", _commit_falha)

    resposta = api_client.post(
        "/api/v1/cursos", json={"nomeCurso": "Curso Duplicado"}, headers=director_headers
    )

    assert resposta.status_code == 409
