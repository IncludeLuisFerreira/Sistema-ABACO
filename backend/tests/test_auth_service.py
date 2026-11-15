from datetime import timedelta

import pytest
from sqlalchemy.orm import Session

from app.core.security import create_first_access_token, create_reset_token, hash_password
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
    def test_reset_token_cannot_be_reused(self, db_session, usuario):
        token = process_forgot_password(db_session, usuario.email)
        process_reset_password(db_session, token, "novaSenha1", "novaSenha1")

        with pytest.raises(InvalidResetTokenError):
            process_reset_password(db_session, token, "outraSenha2", "outraSenha2")

        authenticate_user(db_session, usuario.email, "novaSenha1")

    def test_reset_clears_first_access_flag(self, db_session, usuario_primeiro_acesso):
        token = process_forgot_password(db_session, usuario_primeiro_acesso.email)
        process_reset_password(db_session, token, "novaSenha1", "novaSenha1")

        db_session.refresh(usuario_primeiro_acesso)
        assert usuario_primeiro_acesso.primeiro_acesso is False

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

    def test_expired_token_does_not_change_password(self, db_session: Session, usuario):
        old_hash = usuario.senha_hash
        token = create_reset_token(email=usuario.email, password_hash=usuario.senha_hash, expires_delta=timedelta(minutes=-1))

        with pytest.raises(InvalidResetTokenError):
            process_reset_password(db_session, token, "novaSenha1", "novaSenha1")

        db_session.refresh(usuario)
        assert usuario.senha_hash == old_hash

    def test_first_access_token_is_not_accepted_for_password_reset(self, db_session: Session, usuario):
        token = create_first_access_token(email=usuario.email, password_hash=usuario.senha_hash)

        with pytest.raises(InvalidResetTokenError):
            process_reset_password(db_session, token, "novaSenha1", "novaSenha1")

    def test_reset_token_has_thirty_minute_default_expiration(self, usuario):
        from app.core.config import Settings
        from app.core.security import decode_reset_token

        assert Settings.model_fields["reset_token_expire_minutes"].default == 30
        token = create_reset_token(email=usuario.email, password_hash=usuario.senha_hash)
        assert decode_reset_token(token)["type"] == "password_reset"


class TestProcessFirstAccessPassword:
    def test_first_access_token_cannot_be_reused(self, db_session, usuario_primeiro_acesso):
        token = create_first_access_token(email=usuario_primeiro_acesso.email, password_hash=usuario_primeiro_acesso.senha_hash)
        process_first_access_password(db_session, token, "novaSenha1", "novaSenha1")

        with pytest.raises(InvalidFirstAccessTokenError):
            process_first_access_password(db_session, token, "outraSenha2", "outraSenha2")

        authenticate_user(db_session, usuario_primeiro_acesso.email, "novaSenha1")

    def test_sets_password_and_clears_flag(self, db_session: Session, usuario_primeiro_acesso):
        token = create_first_access_token(email=usuario_primeiro_acesso.email, password_hash=usuario_primeiro_acesso.senha_hash)
        process_first_access_password(db_session, token, "novaSenha1", "novaSenha1")
        db_session.refresh(usuario_primeiro_acesso)
        assert usuario_primeiro_acesso.primeiro_acesso is False

    def test_password_is_updated(self, db_session: Session, usuario_primeiro_acesso):
        old_hash = usuario_primeiro_acesso.senha_hash
        token = create_first_access_token(email=usuario_primeiro_acesso.email, password_hash=usuario_primeiro_acesso.senha_hash)
        process_first_access_password(db_session, token, "novaSenha1", "novaSenha1")
        db_session.refresh(usuario_primeiro_acesso)
        assert usuario_primeiro_acesso.senha_hash != old_hash

    def test_passwords_dont_match(self, db_session: Session, usuario_primeiro_acesso):
        token = create_first_access_token(email=usuario_primeiro_acesso.email, password_hash=usuario_primeiro_acesso.senha_hash)
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
        token = create_first_access_token(email="naoexiste@abaco.org.br", password_hash=None)
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


@pytest.mark.parametrize("token_kind", ["reset", "first_access"])
@pytest.mark.parametrize("password_change", ["reset", "first_access", "change_password"])
def test_password_changes_invalidate_all_previous_links(db_session, usuario_primeiro_acesso, token_kind, password_change):
    usuario = usuario_primeiro_acesso
    reset_token = process_forgot_password(db_session, usuario.email)
    first_token = create_first_access_token(email=usuario.email, password_hash=usuario.senha_hash)
    if password_change == "reset":
        process_reset_password(db_session, reset_token, "novaSenha1", "novaSenha1")
    elif password_change == "first_access":
        process_first_access_password(db_session, first_token, "novaSenha1", "novaSenha1")
    else:
        change_password(db_session, usuario.id_usuario, "senha123", "novaSenha1", "novaSenha1")

    process = process_reset_password if token_kind == "reset" else process_first_access_password
    error = InvalidResetTokenError if token_kind == "reset" else InvalidFirstAccessTokenError
    with pytest.raises(error):
        process(db_session, reset_token if token_kind == "reset" else first_token, "outraSenha2", "outraSenha2")

    authenticate_user(db_session, usuario.email, "novaSenha1")


@pytest.mark.parametrize("version", [None, "versao-incorreta", "versão-inválida"])
@pytest.mark.parametrize("token_kind", ["reset", "first_access"])
def test_password_links_reject_missing_or_wrong_version(db_session, usuario_primeiro_acesso, version, token_kind):
    import jwt
    from app.core.config import get_settings

    usuario = usuario_primeiro_acesso
    create = create_reset_token if token_kind == "reset" else create_first_access_token
    token = create(email=usuario.email, password_hash=usuario.senha_hash)
    settings = get_settings()
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    if version is None:
        payload.pop("password_version")
    else:
        payload["password_version"] = version
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    process = process_reset_password if token_kind == "reset" else process_first_access_password
    error = InvalidResetTokenError if token_kind == "reset" else InvalidFirstAccessTokenError
    with pytest.raises(error):
        process(db_session, token, "novaSenha1", "novaSenha1")

    authenticate_user(db_session, usuario.email, "senha123")
    assert usuario.primeiro_acesso is True


@pytest.mark.parametrize("token_kind", ["reset", "first_access"])
def test_password_link_cannot_overwrite_a_concurrent_password_change(db_session, usuario_primeiro_acesso, monkeypatch, token_kind):
    import app.services.auth_service as service
    from app.models.usuario import Usuario

    usuario = usuario_primeiro_acesso
    create = create_reset_token if token_kind == "reset" else create_first_access_token
    token = create(email=usuario.email, password_hash=usuario.senha_hash)
    usuario_id = usuario.id_usuario

    def hash_after_another_request_changes_password(password):
        with Session(db_session.bind) as other_session:
            other_session.query(Usuario).filter(Usuario.id_usuario == usuario_id).update({
                Usuario.senha_hash: hash_password("concorrente1"), Usuario.primeiro_acesso: False,
            })
            other_session.commit()
        return hash_password(password)

    monkeypatch.setattr(service, "hash_password", hash_after_another_request_changes_password)
    process = process_reset_password if token_kind == "reset" else process_first_access_password
    error = InvalidResetTokenError if token_kind == "reset" else InvalidFirstAccessTokenError
    with pytest.raises(error):
        process(db_session, token, "novaSenha1", "novaSenha1")

    authenticate_user(db_session, usuario.email, "concorrente1")
