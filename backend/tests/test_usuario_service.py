import pytest
from pydantic import ValidationError
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
    def test_creates_successfully_with_all_required_fields(self, db_session: Session):
        payload = UsuarioCreateSchema(
            nome="Novo Usuario",
            email="novo@abaco.org.br",
            senha="senha123",
            cargo=3,
            telefone="11999999999",
            endereco="Rua das Flores, 123 - Centro",
        )
        result = create_usuario(db_session, payload)
        assert result.nome == "Novo Usuario"
        assert result.email == "novo@abaco.org.br"
        assert result.telefone == "11999999999"
        assert result.endereco == "Rua das Flores, 123 - Centro"
        assert result.cargo == 3
        assert result.id_usuario is not None

    def test_raises_validation_error_when_telefone_or_endereco_empty(self):
        with pytest.raises(ValidationError):
            UsuarioCreateSchema(
                nome="Incompleto",
                email="incompleto@abaco.org.br",
                senha="senha123",
                cargo=2,
                telefone="",
                endereco="Rua Teste, 10",
            )

        with pytest.raises(ValidationError):
            UsuarioCreateSchema(
                nome="Incompleto",
                email="incompleto@abaco.org.br",
                senha="senha123",
                cargo=2,
                telefone="11999999999",
                endereco="",
            )

    def test_raises_when_email_already_exists(self, db_session: Session, usuario):
        payload = UsuarioCreateSchema(
            nome="Outro Usuario",
            email=usuario.email,
            senha="senha123",
            cargo=2,
            telefone="11977778888",
            endereco="Rua Exemplo, 45",
        )
        with pytest.raises(UsuarioEmailAlreadyExistsError):
            create_usuario(db_session, payload)


class TestUpdateUsuario:
    def test_updates_endereco_and_other_fields(self, db_session: Session, usuario):
        payload = UsuarioUpdateSchema(
            nome="Usuario Atualizado",
            telefone="11888888888",
            cargo=1,
            endereco="Av. Principal, 456 - Bairro Alto",
        )
        result = update_usuario(db_session, usuario.id_usuario, payload)
        assert result.nome == "Usuario Atualizado"
        assert result.telefone == "11888888888"
        assert result.endereco == "Av. Principal, 456 - Bairro Alto"

    def test_raises_validation_error_for_empty_fields(self):
        with pytest.raises(ValidationError):
            UsuarioUpdateSchema(
                nome="Atualizado",
                telefone="",
                cargo=1,
                endereco="Av. Brasil, 100",
            )

        with pytest.raises(ValidationError):
            UsuarioUpdateSchema(
                nome="Atualizado",
                telefone="11988887777",
                cargo=1,
                endereco="",
            )

    def test_raises_for_nonexistent(self, db_session: Session):
        payload = UsuarioUpdateSchema(
            nome="Inexistente",
            telefone="11999999999",
            cargo=1,
            endereco="Rua Teste, 1",
        )
        with pytest.raises(UsuarioNotFoundError):
            update_usuario(db_session, 99999, payload)


class TestGetAndListUsuario:
    def test_get_usuario_by_id(self, db_session: Session, usuario):
        found = get_usuario_by_id(db_session, usuario.id_usuario)
        assert found.id_usuario == usuario.id_usuario

    def test_list_usuarios(self, db_session: Session, usuario):
        usuarios = list_usuarios(db_session)
        assert len(usuarios) >= 1
        assert any(u.email == usuario.email for u in usuarios)


class TestDeleteUsuario:
    def test_deletes_successfully(self, db_session: Session):
        payload = UsuarioCreateSchema(
            nome="Para Deletar",
            email="delete@abaco.org.br",
            senha="senha123",
            cargo=3,
            telefone="11999991111",
            endereco="Rua B, 20",
        )
        created = create_usuario(db_session, payload)
        delete_usuario(db_session, created.id_usuario)

        with pytest.raises(UsuarioNotFoundError):
            get_usuario_by_id(db_session, created.id_usuario)
