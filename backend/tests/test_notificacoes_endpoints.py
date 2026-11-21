from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.notificacao import Notificacao
from app.models.usuario import Usuario


@pytest.fixture
def usuario_headers(db_session: Session, usuario: Usuario) -> dict:
    token = create_access_token(subject=str(usuario.id_usuario), cargo=usuario.cargo)
    return {"Authorization": f"Bearer {token}"}


def _notificacao(
    db: Session,
    usuario_id: int,
    titulo: str,
    *,
    criada_em: datetime,
    lida: bool = False,
) -> Notificacao:
    notificacao = Notificacao(
        id_usuario=usuario_id,
        tipo="estoque_baixo",
        titulo=titulo,
        mensagem="Mensagem de teste",
        link=f"/estoque/{titulo}",
        lida=lida,
        criada_em=criada_em,
    )
    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)
    return notificacao


class TestListagem:
    def test_lista_apenas_notificacoes_do_usuario_e_mais_recentes_primeiro(
        self, api_client, db_session, usuario, usuario_headers
    ):
        outro = Usuario(nome="Outro", email="outro@abaco.org.br", cargo=1, primeiro_acesso=False)
        db_session.add(outro)
        db_session.commit()
        db_session.refresh(outro)
        antiga = _notificacao(db_session, usuario.id_usuario, "Antiga", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc))
        recente = _notificacao(db_session, usuario.id_usuario, "Recente", criada_em=datetime(2026, 3, 1, tzinfo=timezone.utc))
        _notificacao(db_session, outro.id_usuario, "De outro", criada_em=datetime(2026, 4, 1, tzinfo=timezone.utc))

        response = api_client.get("/api/v1/notificacoes", headers=usuario_headers)

        assert response.status_code == 200
        dados = response.json()
        assert [item["idNotificacao"] for item in dados] == [recente.id_notificacao, antiga.id_notificacao]
        assert all("criadaEm" in item for item in dados)
        assert all("criada_em" not in item for item in dados)

    def test_filtro_apenas_nao_lidas(self, api_client, db_session, usuario, usuario_headers):
        lida = _notificacao(db_session, usuario.id_usuario, "Lida", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc), lida=True)
        nao_lida = _notificacao(db_session, usuario.id_usuario, "Não lida", criada_em=datetime(2026, 2, 1, tzinfo=timezone.utc))

        response = api_client.get("/api/v1/notificacoes?apenas_nao_lidas=true", headers=usuario_headers)

        assert response.status_code == 200
        assert [item["idNotificacao"] for item in response.json()] == [nao_lida.id_notificacao]
        assert lida.id_notificacao not in [item["idNotificacao"] for item in response.json()]

    def test_paginacao(self, api_client, db_session, usuario, usuario_headers):
        primeira = _notificacao(db_session, usuario.id_usuario, "Primeira", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc))
        segunda = _notificacao(db_session, usuario.id_usuario, "Segunda", criada_em=datetime(2026, 2, 1, tzinfo=timezone.utc))
        terceira = _notificacao(db_session, usuario.id_usuario, "Terceira", criada_em=datetime(2026, 3, 1, tzinfo=timezone.utc))

        response = api_client.get("/api/v1/notificacoes?limite=2&offset=1", headers=usuario_headers)

        assert response.status_code == 200
        assert [item["idNotificacao"] for item in response.json()] == [segunda.id_notificacao, primeira.id_notificacao]
        assert terceira.id_notificacao not in [item["idNotificacao"] for item in response.json()]

    def test_limite_acima_de_50_e_rejeitado(self, api_client, usuario_headers):
        assert api_client.get("/api/v1/notificacoes?limite=51", headers=usuario_headers).status_code == 422


class TestContagem:
    def test_contagem_do_usuario_autenticado(self, api_client, db_session, usuario, usuario_headers):
        outro = Usuario(nome="Outro", email="outro@abaco.org.br", cargo=1, primeiro_acesso=False)
        db_session.add(outro)
        db_session.commit()
        db_session.refresh(outro)
        _notificacao(db_session, usuario.id_usuario, "Lida", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc), lida=True)
        _notificacao(db_session, usuario.id_usuario, "Não lida", criada_em=datetime(2026, 2, 1, tzinfo=timezone.utc))
        _notificacao(db_session, outro.id_usuario, "De outro", criada_em=datetime(2026, 3, 1, tzinfo=timezone.utc))

        response = api_client.get("/api/v1/notificacoes/contagem", headers=usuario_headers)

        assert response.status_code == 200
        assert response.json() == {"naoLidas": 1}


class TestMarcacao:
    def test_marcar_uma_e_idempotente(self, api_client, db_session, usuario, usuario_headers):
        notificacao = _notificacao(db_session, usuario.id_usuario, "Aviso", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc))
        url = f"/api/v1/notificacoes/{notificacao.id_notificacao}/lida"

        primeira = api_client.patch(url, headers=usuario_headers)
        segunda = api_client.patch(url, headers=usuario_headers)

        assert primeira.status_code == 200
        assert segunda.status_code == 200
        assert primeira.json()["lida"] is True
        db_session.refresh(notificacao)
        assert notificacao.lida is True

    def test_marcar_todas_devolve_quantidade_atualizada(self, api_client, db_session, usuario, usuario_headers):
        _notificacao(db_session, usuario.id_usuario, "Não lida 1", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc))
        _notificacao(db_session, usuario.id_usuario, "Não lida 2", criada_em=datetime(2026, 2, 1, tzinfo=timezone.utc))

        response = api_client.post("/api/v1/notificacoes/marcar-todas-lidas", headers=usuario_headers)

        assert response.status_code == 200
        assert response.json() == {"atualizadas": 2}
        assert api_client.get("/api/v1/notificacoes/contagem", headers=usuario_headers).json() == {"naoLidas": 0}

    def test_notificacao_de_terceiro_retorna_404(self, api_client, db_session, usuario, usuario_headers):
        outro = Usuario(nome="Outro", email="outro@abaco.org.br", cargo=1, primeiro_acesso=False)
        db_session.add(outro)
        db_session.commit()
        db_session.refresh(outro)
        notificacao = _notificacao(db_session, outro.id_usuario, "De outro", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc))

        response = api_client.patch(
            f"/api/v1/notificacoes/{notificacao.id_notificacao}/lida", headers=usuario_headers
        )

        assert response.status_code == 404


class TestAutorizacao:
    @pytest.mark.parametrize(
        "metodo,caminho",
        [
            ("get", "/api/v1/notificacoes"),
            ("get", "/api/v1/notificacoes/contagem"),
            ("patch", "/api/v1/notificacoes/1/lida"),
            ("post", "/api/v1/notificacoes/marcar-todas-lidas"),
        ],
    )
    def test_sem_token_retorna_401(self, api_client, metodo, caminho):
        response = getattr(api_client, metodo)(caminho)
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "metodo,caminho",
        [
            ("get", "/api/v1/notificacoes"),
            ("get", "/api/v1/notificacoes/contagem"),
            ("patch", "/api/v1/notificacoes/1/lida"),
            ("post", "/api/v1/notificacoes/marcar-todas-lidas"),
        ],
    )
    def test_cargo_invalido_retorna_403(self, api_client, guest_headers, metodo, caminho):
        response = getattr(api_client, metodo)(caminho, headers=guest_headers)
        assert response.status_code == 403


class TestCsrf:
    def test_patch_e_post_por_cookie_exigem_csrf(self, seeded, db_session):
        client = seeded["client"]
        professor_id = seeded["professor"]["idUsuario"]
        notificacao = _notificacao(db_session, professor_id, "Aviso", criada_em=datetime(2026, 1, 1, tzinfo=timezone.utc))
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "prof@abaco.org.br", "senha": "senha123"},
        )
        assert login.status_code == 200
        csrf_token = login.cookies.get("abaco_csrf")

        url = f"/api/v1/notificacoes/{notificacao.id_notificacao}/lida"
        assert client.patch(url).status_code == 403
        assert client.patch(url, headers={"X-CSRF-Token": csrf_token}).status_code == 200

        assert client.post("/api/v1/notificacoes/marcar-todas-lidas").status_code == 403
        assert client.post(
            "/api/v1/notificacoes/marcar-todas-lidas",
            headers={"X-CSRF-Token": csrf_token},
        ).status_code == 200
