from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from src.config.env_config import SECRET_KEY
from src.service.token_service import TokenService


class TestTokenService:
    def test_create_access_token(self):
        user_id = "test_user_123"
        token = TokenService.create_access_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_refresh_token(self):
        user_id = "test_user_456"
        token = TokenService.create_refresh_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_csrf_token(self):
        token = TokenService.create_csrf_token()

        assert isinstance(token, str)
        assert len(token) > 0

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert "csrf" in payload
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_access_token_valid(self):
        user_id = "test_user_789"
        token = TokenService.create_access_token(user_id)

        payload = TokenService.verify_token(token, "access")
        assert payload["sub"] == user_id
        assert payload["type"] == "access"

    def test_verify_refresh_token_valid(self):
        user_id = "test_user_101"
        token = TokenService.create_refresh_token(user_id)

        payload = TokenService.verify_token(token, "refresh")
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"

    def test_verify_csrf_token_valid(self):
        token = TokenService.create_csrf_token()

        result = TokenService.verify_csrf_token(token)
        assert result is True

    def test_verify_csrf_token_invalid(self):
        invalid_token = "invalid_token"

        result = TokenService.verify_csrf_token(invalid_token)
        assert result is False

    def test_verify_token_expired(self):
        now = datetime.now(timezone.utc)
        past_time = now - timedelta(minutes=30)
        payload = {
            "sub": "test_user",
            "type": "access",
            "exp": past_time,
        }
        expired_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        with pytest.raises(HTTPException) as exc_info:
            TokenService.verify_token(expired_token, "access")
        assert exc_info.value.status_code == 401
        assert "Token expired" in str(exc_info.value.detail)

    def test_verify_token_invalid_type(self):
        user_id = "test_user_112"
        access_token = TokenService.create_access_token(user_id)

        with pytest.raises(HTTPException) as exc_info:
            TokenService.verify_token(access_token, "refresh")
        assert exc_info.value.status_code == 401
        assert "Invalid token type" in str(exc_info.value.detail)

    def test_verify_token_malformed(self):
        malformed_token = "not.a.valid.jwt.token"

        with pytest.raises(HTTPException) as exc_info:
            TokenService.verify_token(malformed_token, "access")
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)

    def test_blacklist_refresh_token(self):
        user_id = "test_user_blacklist"
        token = TokenService.create_refresh_token(user_id)

        payload = TokenService.verify_token(token, "refresh")
        assert payload["sub"] == user_id

        TokenService.blacklist_refresh_token(token)

        with pytest.raises(HTTPException) as exc_info:
            TokenService.verify_token(token, "refresh")
        assert exc_info.value.status_code == 401
        assert "Token has been revoked" in str(exc_info.value.detail)

    def test_get_user_id_from_token_valid(self):
        user_id = "test_user_get_id"
        token = TokenService.create_access_token(user_id)

        extracted_user_id = TokenService.get_user_id_from_token(token, "access")
        assert extracted_user_id == user_id

    def test_get_user_id_from_token_invalid(self):
        invalid_token = "invalid_token"

        extracted_user_id = TokenService.get_user_id_from_token(invalid_token, "access")
        assert extracted_user_id is None

    def test_csrf_token_different_each_time(self):
        token1 = TokenService.create_csrf_token()
        token2 = TokenService.create_csrf_token()

        assert token1 != token2

        assert TokenService.verify_csrf_token(token1) is True
        assert TokenService.verify_csrf_token(token2) is True
