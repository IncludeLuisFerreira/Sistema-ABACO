import jwt
import pytest

from app.core.security import (
    create_access_token,
    create_first_access_token,
    decode_first_access_token,
)


class TestCreateAccessToken:
    def test_includes_primeiro_acesso_flag(self):
        token = create_access_token(subject="1", cargo=2, primeiro_acesso=True)
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["primeiro_acesso"] is True
        assert payload["sub"] == "1"
        assert payload["cargo"] == 2

    def test_defaults_primeiro_acesso_to_false(self):
        token = create_access_token(subject="1", cargo=1)
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["primeiro_acesso"] is False


class TestFirstAccessToken:
    def test_roundtrip(self):
        token = create_first_access_token(email="novo@abaco.org.br")
        payload = decode_first_access_token(token)
        assert payload["sub"] == "novo@abaco.org.br"
        assert payload["type"] == "first_access"

    def test_rejects_other_token_type(self):
        from app.core.security import create_reset_token

        reset_token = create_reset_token(email="novo@abaco.org.br")
        with pytest.raises(jwt.PyJWTError):
            decode_first_access_token(reset_token)

    def test_rejects_garbage(self):
        with pytest.raises(jwt.PyJWTError):
            decode_first_access_token("nao-e-um-token")
