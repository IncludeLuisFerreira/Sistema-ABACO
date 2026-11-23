from sqlalchemy.exc import IntegrityError


class _ErroOriginal:
    def __init__(self, mensagem: str, pgcode: str | None = None):
        self._mensagem = mensagem
        self.pgcode = pgcode

    def __str__(self) -> str:
        return self._mensagem


def _forcar_falha_no_commit(db_session, monkeypatch, erro_original: _ErroOriginal) -> None:
    def commit_que_falha():
        raise IntegrityError("INSERT", {}, erro_original)

    monkeypatch.setattr(db_session, "commit", commit_que_falha)


class TestIntegridadeAlunos:
    def test_violacao_unica_retorna_409(self, api_client, director_headers, db_session, monkeypatch):
        _forcar_falha_no_commit(
            db_session,
            monkeypatch,
            _ErroOriginal("duplicate key value violates unique constraint", pgcode="23505"),
        )

        response = api_client.post("/api/v1/alunos", json={"nome": "Aluno Novo"}, headers=director_headers)

        assert response.status_code == 409
        assert response.json()["detail"] == "Já existe um aluno com esses dados"

    def test_integridade_generica_retorna_422(self, api_client, director_headers, db_session, monkeypatch):
        _forcar_falha_no_commit(
            db_session,
            monkeypatch,
            _ErroOriginal("NOT NULL constraint failed: aluno.nome"),
        )

        response = api_client.post("/api/v1/alunos", json={"nome": "Aluno Novo"}, headers=director_headers)

        assert response.status_code == 422
        assert response.json()["detail"] == "Não foi possível salvar o aluno: dados inconsistentes"


class TestIntegridadeCursos:
    def test_violacao_unica_retorna_409(self, api_client, director_headers, db_session, monkeypatch):
        _forcar_falha_no_commit(
            db_session,
            monkeypatch,
            _ErroOriginal("UNIQUE constraint failed: curso.nomecurso"),
        )

        response = api_client.post("/api/v1/cursos", json={"nomeCurso": "Curso Novo"}, headers=director_headers)

        assert response.status_code == 409
        assert response.json()["detail"] == "Já existe um curso com esses dados"

    def test_integridade_generica_retorna_422(self, api_client, director_headers, db_session, monkeypatch):
        _forcar_falha_no_commit(
            db_session,
            monkeypatch,
            _ErroOriginal("NOT NULL constraint failed: curso.nomecurso"),
        )

        response = api_client.post("/api/v1/cursos", json={"nomeCurso": "Curso Novo"}, headers=director_headers)

        assert response.status_code == 422
        assert response.json()["detail"] == "Não foi possível salvar o curso: dados inconsistentes"
