import base64
import hashlib
import os
import secrets

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from src.config.env_config import SECRET_KEY, TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET
from src.config.logging_config import get_logger
from src.db.session import get_db
from src.schema.user import UserCreate, UserRead
from src.service import user_service
from src.service.token_service import TokenService

logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

auth_router = APIRouter()

# Environment-based configuration
REDIRECT_URI = os.getenv(
    "TWITTER_REDIRECT_URI", "http://localhost:8000/auth/callback/twitter"
)
TWITTER_AUTH_URL = "https://twitter.com/i/oauth2/authorize"
TWITTER_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
TWITTER_USER_ME_URL = "https://api.twitter.com/2/users/me"  # https://docs.x.com/x-api/users/user-lookup-me
# Use first URL from FRONTEND_URLS as primary frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URLS", "http://localhost:5173").split(",")[0].strip()

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def _get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = TokenService.verify_token(token, "access")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """
    現在のユーザーを取得する（オプショナル版）
    ログインしていない場合はNoneを返し、エラーを発生させない
    """
    try:
        token = request.cookies.get("access_token")
        if not token:
            return None

        # _verify_token を直接呼ばずに、エラーをキャッチ
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "access":
                return None
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = user_service.get_user(db, user_id=user_id)
        return user
    except Exception:
        return None


# https://docs.x.com/resources/fundamentals/authentication/oauth-2-0/user-access-token
@auth_router.get("/login/twitter")
@limiter.limit("10/minute")  # Prevent auth spam
async def login_twitter(request: Request):
    state = secrets.token_urlsafe(16)
    code_verifier = secrets.token_urlsafe(32)

    request.session["state"] = state
    request.session["code_verifier"] = code_verifier

    code_challenge_hash = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge_hash).decode().rstrip("=")

    params = {
        "response_type": "code",
        "client_id": TWITTER_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "users.read tweet.read",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = httpx.URL(TWITTER_AUTH_URL, params=params)
    logger.info(
        "Twitter auth initiated", client_ip=get_remote_address(request), state=state
    )
    return RedirectResponse(url=str(auth_url))


# This func requests an access token from Twitter's API using code passed from Twitter and redirects to the frontend
@auth_router.get("/callback/twitter")
@limiter.limit("20/minute")  # Higher limit for callback (legitimate flow)
async def auth_twitter_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    if code is None:
        raise HTTPException(status_code=400, detail="Missing code parameter")
    if state is None:
        raise HTTPException(status_code=400, detail="Missing state parameter")

    session_state = request.session.pop("state", None)
    if session_state is None or session_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    code_verifier = request.session.pop("code_verifier", None)
    if code_verifier is None:
        raise HTTPException(
            status_code=400, detail="Code verifier not found in session"
        )

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": TWITTER_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    }
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            TWITTER_TOKEN_URL,
            data=data,
            auth=(TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET),
            headers=headers,
        )
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid token response")

        token_data = token_response.json()
        access_token = token_data["access_token"]

        user_response = await client.get(
            TWITTER_USER_ME_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            params={"user.fields": "profile_image_url,description"},
        )

        if user_response.status_code != 200:
            logger.error(
                f"Twitter API user request failed. Status: {user_response.status_code}, "
                f"Response: {user_response.text}"
            )
            if user_response.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="Twitter API rate limit exceeded. Please try again later.",
                )
            else:
                raise HTTPException(status_code=400, detail="Invalid user data")

        user_response_json = user_response.json()
        logger.info(f"Twitter API response: {user_response_json}")

        if "data" not in user_response_json:
            logger.error(
                f"Missing 'data' field in Twitter response: {user_response_json}"
            )
            raise HTTPException(status_code=400, detail="Invalid user data structure")

        user_data = user_response_json["data"]
        profile_image_url = user_data.get("profile_image_url")

        # By removing `_normal`, we got the original size URL
        high_res_url = (
            profile_image_url.replace("_normal", "") if profile_image_url else None
        )

        user_in = UserCreate(
            user_id=user_data["id"],
            user_name=user_data["username"],
            display_name=user_data["name"],
            bio=user_data.get("description"),
            self_introduction=None,
            icon_url=high_res_url,
        )
        user = user_service.upsert_user(db, user_in=user_in)

        logger.info(
            "User authenticated successfully",
            user_id=user.user_id,
            username=user.user_name,
            client_ip=get_remote_address(request),
        )

        access_token = TokenService.create_access_token(user.user_id)
        refresh_token = TokenService.create_refresh_token(user.user_id)

        response = RedirectResponse(url=f"{FRONTEND_URL}/{user.user_name}")

        response.set_cookie(
            key="access_token",
            value=access_token,
            domain=".hitoq.net" if os.getenv("ENVIRONMENT") == "production" else None,
            path="/",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 15分
            samesite="none" if os.getenv("ENVIRONMENT") == "production" else "lax",
            httponly=True,
            secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            domain=".hitoq.net" if os.getenv("ENVIRONMENT") == "production" else None,
            path="/",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 7日
            samesite="none" if os.getenv("ENVIRONMENT") == "production" else "lax",
            httponly=True,
            secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        )

        return response


@auth_router.post("/refresh-token")
@limiter.limit("100/hour")  # Allow frequent refresh but prevent abuse
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    payload = TokenService.verify_token(refresh_token, "refresh")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access_token = TokenService.create_access_token(user.user_id)

    response = JSONResponse(content={"message": "Token refreshed successfully"})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        domain=".hitoq.net" if os.getenv("ENVIRONMENT") == "production" else None,
        path="/",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="none" if os.getenv("ENVIRONMENT") == "production" else "lax",
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
    )

    return response


@auth_router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user=Depends(_get_current_user)):
    return current_user


@auth_router.get("/csrf-token")
@limiter.limit("50/minute")  # Allow frequent CSRF token requests
async def get_csrf_token(request: Request):
    csrf_token = TokenService.create_csrf_token()

    response = JSONResponse(content={"csrf_token": csrf_token})
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        domain=".hitoq.net" if os.getenv("ENVIRONMENT") == "production" else None,
        path="/",
        max_age=24 * 60 * 60,  # 24時間
        httponly=False,  # JavaScriptからアクセス可能
        samesite="none" if os.getenv("ENVIRONMENT") == "production" else "lax",
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
    )

    return response


@auth_router.post("/logout")
@limiter.limit("30/minute")  # Reasonable limit for logout
async def logout(request: Request):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        TokenService.blacklist_refresh_token(refresh_token)
        logger.info("User logged out", client_ip=get_remote_address(request))

    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    response.delete_cookie(key="csrf_token", path="/")

    return response
