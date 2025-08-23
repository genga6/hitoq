import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import HTTPException

from src.config.env_config import SECRET_KEY
from src.config.logging_config import get_logger

logger = get_logger(__name__)

# Token expiration settings (Twitter-aligned)
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # 2 hours
REFRESH_TOKEN_EXPIRE_DAYS = 180  # 6 months
CSRF_TOKEN_EXPIRE_HOURS = 24

# リフレッシュトークンのブラックリスト（本番環境ではRedisなどを使用）
blacklisted_tokens = set()


class TokenService:
    @staticmethod
    def create_access_token(user_id: str) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": user_id, "type": "access", "exp": expire}
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": now,
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def create_csrf_token() -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(hours=CSRF_TOKEN_EXPIRE_HOURS)
        payload = {
            "csrf": secrets.token_urlsafe(32),
            "exp": expire,
            "iat": now,
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str, token_type: str = "access"):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            if token_type == "csrf":
                return "csrf" in payload

            if payload.get("type") != token_type:
                raise HTTPException(status_code=401, detail="Invalid token type")

            if token_type == "refresh" and token in blacklisted_tokens:
                raise HTTPException(status_code=401, detail="Token has been revoked")

            return payload
        except jwt.ExpiredSignatureError as e:
            if token_type == "csrf":
                return False
            raise HTTPException(status_code=401, detail="Token expired") from e
        except jwt.InvalidTokenError as e:
            if token_type == "csrf":
                return False
            raise HTTPException(status_code=401, detail="Invalid token") from e

    @staticmethod
    def verify_csrf_token(token: str) -> bool:
        return TokenService.verify_token(token, "csrf")

    @staticmethod
    def blacklist_refresh_token(token: str) -> None:
        blacklisted_tokens.add(token)

    @staticmethod
    def get_user_id_from_token(token: str, token_type: str = "access") -> Optional[str]:
        try:
            payload = TokenService.verify_token(token, token_type)
            if isinstance(payload, dict):
                return payload.get("sub")
            return None
        except HTTPException:
            return None
