import pytest
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.services.auth_service import (
    EmailNotFoundError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    PasswordsDoNotMatchError,
    authenticate_user,
    build_login_response,
    process_forgot_password,
    process_reset_password,
)


class TestAuthenticateUser:
    def test_valid_credentials(self, db_session: Session, usuario):
        result = authenticate_user(db_session, "teste@abaco.org.br", "senha123")
        assert result.id_usuario == usuario.id_usuario

    def test_invalid_email(self, db_session: Session):
        with pytest.raises(InvalidCredentialsError):
            authenticate_user(db_session, "naoexiste@abaco.org.br", "senha123")

    def test_invalid_password(self, db_session: Session, usuario):
        with pytest.raises(InvalidCredentialsError):
            authenticate_user(db_session, "teste@abaco.org.br", "senha_errada")


class TestBuildLoginResponse:
    def test_returns_token_and_usuario(self, usuario):
        response = build_login_response(usuario)
        assert "access_token" in response
        assert response["token_type"] == "bearer"
        assert response["usuario"]["idUsuario"] == usuario.id_usuario
        assert response["usuario"]["email"] == "teste@abaco.org.br"


class TestProcessForgotPassword:
    def test_generates_token_for_existing_user(self, db_session: Session, usuario):
        token = process_forgot_password(db_session, "teste@abaco.org.br")
        assert token is not None
        assert len(token) > 0

    def test_raises_for_unknown_email(self, db_session: Session):
        with pytest.raises(EmailNotFoundError):
            process_forgot_password(db_session, "naoexiste@abaco.org.br")


class TestProcessResetPassword:
    def test_resets_password_with_valid_token(self, db_session: Session, usuario):
        old_hash = usuario.senha_hash
        token = process_forgot_password(db_session, "teste@abaco.org.br")
        process_reset_password(db_session, token, "novaSenha1", "novaSenha1")
        db_session.refresh(usuario)
        assert usuario.senha_hash != old_hash

    def test_passwords_dont_match(self, db_session: Session, usuario):
        token = process_forgot_password(db_session, "teste@abaco.org.br")
        with pytest.raises(PasswordsDoNotMatchError):
            process_reset_password(db_session, token, "novaSenha1", "diferente")

    def test_invalid_token_raises(self, db_session: Session):
        with pytest.raises(InvalidResetTokenError):
            process_reset_password(db_session, "token_invalido", "novaSenha1", "novaSenha1")
