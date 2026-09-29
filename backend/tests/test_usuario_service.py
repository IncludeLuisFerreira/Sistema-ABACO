import pytest
from sqlalchemy.orm import Session

from app.schemas.usuario_schema import UsuarioCreateSchema, UsuarioUpdateSchema
from app.services.usuario_service import (
    UsuarioEmailAlreadyExistsError,
    UsuarioNotFoundError,
    create_usuario,
    delete_usuario,
    get_usuario_by_id,
    list_usuarios,
    update_usuario,
)


class TestCreateUsuario:
    def test_creates_with_first_access_enabled(self, db_session: Session):
        payload = UsuarioCreateSchema(
            nome="Novo Usuario",
            email="novo.usuario@abaco.org.br",
            senha="senha123",
            cargo=2,
        )
        result = create_usuario(db_session, payload)
        assert result.id_usuario is not None
        assert result.primeiro_acesso is True

    def test_duplicate_email_raises(self, db_session: Session, usuario):
        payload = UsuarioCreateSchema(
            nome="Duplicado",
            email=usuario.email,
            senha="senha123",
            cargo=1,
        )
        with pytest.raises(UsuarioEmailAlreadyExistsError):
            create_usuario(db_session, payload)


class TestListUsuarios:
    def test_lists_all(self, db_session: Session, usuario):
        results = list_usuarios(db_session)
        assert any(u.email == usuario.email for u in results)


class TestGetUsuarioById:
    def test_finds_existing(self, db_session: Session, usuario):
        result = get_usuario_by_id(db_session, usuario.id_usuario)
        assert result.email == usuario.email

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(UsuarioNotFoundError):
            get_usuario_by_id(db_session, 9999)


class TestUpdateUsuario:
    def test_updates_fields(self, db_session: Session, usuario):
        payload = UsuarioUpdateSchema(nome="Atualizado", telefone="11900000000", cargo=3)
        result = update_usuario(db_session, usuario.id_usuario, payload)
        assert result.nome == "Atualizado"
        assert result.cargo == 3

    def test_raises_for_nonexistent(self, db_session: Session):
        payload = UsuarioUpdateSchema(nome="Qualquer", cargo=1)
        with pytest.raises(UsuarioNotFoundError):
            update_usuario(db_session, 9999, payload)


class TestDeleteUsuario:
    def test_deletes_existing(self, db_session: Session, usuario):
        delete_usuario(db_session, usuario.id_usuario)
        with pytest.raises(UsuarioNotFoundError):
            get_usuario_by_id(db_session, usuario.id_usuario)

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(UsuarioNotFoundError):
            delete_usuario(db_session, 9999)
