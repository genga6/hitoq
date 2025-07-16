import base64
import hashlib
import secrets

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.config import SECRET_KEY, TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET
from src.db.session import get_db
from src.schema.user import UserCreate
from src.service import user_service

auth_router = APIRouter()

REDIRECT_URI = "http://127.0.0.1:8000/auth/callback/twitter"
TWITTER_AUTH_URL = "https://twitter.com/i/oauth2/authorize"
TWITTER_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
TWITTER_USER_ME_URL = "https://api.twitter.com/2/users/me"  # https://docs.x.com/x-api/users/user-lookup-me
FRONTEND_URL = "http://localhost:5173"


# https://docs.x.com/resources/fundamentals/authentication/oauth-2-0/user-access-token
@auth_router.get("/login/twitter")
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
    return RedirectResponse(url=str(auth_url))


# This func requests an access token from Twitter's API using code passed from Twitter and redirects to the frontend
@auth_router.get("/callback/twitter")
async def auth_twitter_callback(
    request: Request, code: str, state: str, db: Session = Depends(get_db)
):
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
            raise HTTPException(status_code=400, detail="Invalid user data")

        user_data = user_response.json()["data"]
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
            icon_url=high_res_url,
        )
        user = user_service.upsert_user(db, user_in=user_in)

        jwt_payload = {"sub": user.user_id}
        jwt_token = jwt.encode(jwt_payload, SECRET_KEY, algorithm="HS256")

        response = RedirectResponse(url=f"{FRONTEND_URL}/{user.user_name}")
        response.set_cookie(
            key="jwt",
            value=jwt_token,
            path="/",
            max_age=2592000,
            samesite="lax",
            httponly=True,
            secure=False,  # TODO: http -> False, https -> True
        )
        return response
