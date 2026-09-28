import pytest
from sqlalchemy.orm import Session

from app.core.security import create_first_access_token, hash_password
from app.services.auth_service import (
    EmailNotFoundError,
    InvalidCredentialsError,
    InvalidCurrentPasswordError,
    InvalidFirstAccessTokenError,
    InvalidResetTokenError,
    PasswordsDoNotMatchError,
    authenticate_user,
    build_login_response,
    change_password,
    process_first_access_password,
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
        assert response["usuario"]["primeiro_acesso"] is False

    def test_first_access_flag_is_propagated(self, usuario_primeiro_acesso):
        response = build_login_response(usuario_primeiro_acesso)
        assert response["usuario"]["primeiro_acesso"] is True


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


class TestProcessFirstAccessPassword:
    def test_sets_password_and_clears_flag(self, db_session: Session, usuario_primeiro_acesso):
        token = create_first_access_token(email=usuario_primeiro_acesso.email)
        process_first_access_password(db_session, token, "novaSenha1", "novaSenha1")
        db_session.refresh(usuario_primeiro_acesso)
        assert usuario_primeiro_acesso.primeiro_acesso is False

    def test_password_is_updated(self, db_session: Session, usuario_primeiro_acesso):
        old_hash = usuario_primeiro_acesso.senha_hash
        token = create_first_access_token(email=usuario_primeiro_acesso.email)
        process_first_access_password(db_session, token, "novaSenha1", "novaSenha1")
        db_session.refresh(usuario_primeiro_acesso)
        assert usuario_primeiro_acesso.senha_hash != old_hash

    def test_passwords_dont_match(self, db_session: Session, usuario_primeiro_acesso):
        token = create_first_access_token(email=usuario_primeiro_acesso.email)
        with pytest.raises(PasswordsDoNotMatchError):
            process_first_access_password(db_session, token, "novaSenha1", "diferente")

    def test_invalid_token_raises(self, db_session: Session):
        with pytest.raises(InvalidFirstAccessTokenError):
            process_first_access_password(db_session, "token_invalido", "novaSenha1", "novaSenha1")

    def test_reset_token_is_rejected(self, db_session: Session, usuario_primeiro_acesso):
        reset_token = process_forgot_password(db_session, usuario_primeiro_acesso.email)
        with pytest.raises(InvalidFirstAccessTokenError):
            process_first_access_password(db_session, reset_token, "novaSenha1", "novaSenha1")

    def test_unknown_email_raises(self, db_session: Session):
        token = create_first_access_token(email="naoexiste@abaco.org.br")
        with pytest.raises(InvalidFirstAccessTokenError):
            process_first_access_password(db_session, token, "novaSenha1", "novaSenha1")


class TestChangePassword:
    def test_changes_password_and_clears_flag(self, db_session: Session, usuario):
        result = change_password(db_session, usuario.id_usuario, "senha123", "novaSenha1", "novaSenha1")
        db_session.refresh(usuario)
        assert result.primeiro_acesso is False
        assert usuario.primeiro_acesso is False

    def test_wrong_current_password_raises(self, db_session: Session, usuario):
        with pytest.raises(InvalidCurrentPasswordError):
            change_password(db_session, usuario.id_usuario, "errada", "novaSenha1", "novaSenha1")

    def test_passwords_dont_match(self, db_session: Session, usuario):
        with pytest.raises(PasswordsDoNotMatchError):
            change_password(db_session, usuario.id_usuario, "senha123", "novaSenha1", "diferente")

    def test_unknown_user_raises(self, db_session: Session):
        with pytest.raises(InvalidCurrentPasswordError):
            change_password(db_session, 9999, "senha123", "novaSenha1", "novaSenha1")

    def test_first_access_user_can_change_password(self, db_session: Session, usuario_primeiro_acesso):
        result = change_password(db_session, usuario_primeiro_acesso.id_usuario, "senha123", "novaSenha1", "novaSenha1")
        assert result.primeiro_acesso is False
