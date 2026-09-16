import pytest
from pydantic import ValidationError

from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
)


class TestLoginRequest:
    def test_valid(self):
        s = LoginRequest(email="teste@abaco.org.br", senha="abc123")
        assert s.email == "teste@abaco.org.br"

    def test_empty_email_rejected(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="", senha="abc")

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="nao-email", senha="abc")


class TestForgotPasswordRequest:
    def test_valid(self):
        s = ForgotPasswordRequest(email="teste@abaco.org.br")
        assert s.email == "teste@abaco.org.br"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            ForgotPasswordRequest(email="invalido")


class TestResetPasswordRequest:
    def test_valid(self):
        s = ResetPasswordRequest(token="abc", nova_senha="abc12345", confirmar_senha="abc12345")
        assert s.token == "abc"

    def test_short_password_rejected(self):
        with pytest.raises(ValidationError):
            ResetPasswordRequest(token="x", nova_senha="1234567", confirmar_senha="1234567")

    def test_passwords_dont_match_rejected(self):
        with pytest.raises(ValidationError) as exc:
            ResetPasswordRequest(token="x", nova_senha="abc12345", confirmar_senha="abc54321")
        assert "conferem" in str(exc.value).lower()
