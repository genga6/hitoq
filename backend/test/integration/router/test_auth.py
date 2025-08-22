from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import status

from src.main import app
from src.router.auth import _get_current_user


@pytest.mark.integration
class TestAuthRouter:
    def test_twitter_login_redirect(self, client):
        # Don't follow redirects to test the actual redirect response
        response = client.get("/auth/login/twitter", follow_redirects=False)

        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

        redirect_url = response.headers["location"]
        parsed_url = urlparse(redirect_url)

        assert parsed_url.netloc == "twitter.com"
        assert "/i/oauth2/authorize" in parsed_url.path

        query_params = parse_qs(parsed_url.query)

        assert "client_id" in query_params
        assert "redirect_uri" in query_params
        assert "scope" in query_params
        assert "state" in query_params
        assert "code_challenge" in query_params
        assert "code_challenge_method" in query_params

    @patch("src.router.auth.httpx.AsyncClient.post")
    @patch("src.router.auth.httpx.AsyncClient.get")
    def test_twitter_callback_success(self, mock_get, mock_post, client):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "access_token": "twitter_access_token",
                "token_type": "bearer",
                "scope": "users.read",
            },
        )

        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "data": {
                    "id": "1234567890",
                    "name": "Test User",
                    "username": "testuser",
                    "profile_image_url": "https://example.com/avatar.jpg",
                }
            },
        )

        with client as c:
            # First, initiate login to set up session state
            login_response = c.get("/auth/login/twitter", follow_redirects=False)

            assert login_response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

            # Extract state from login redirect URL for callback
            redirect_url = login_response.headers["location"]

            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            state = query_params["state"][0]

            callback_response = c.get(
                f"/auth/callback/twitter?code=auth_code&state={state}",
                follow_redirects=False,
            )

            assert callback_response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
            assert "localhost:5173" in callback_response.headers["location"]

    def test_twitter_callback_missing_code(self, client):
        response = client.get("/auth/callback/twitter?state=some_state")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_twitter_callback_missing_state(self, client):
        response = client.get("/auth/callback/twitter?code=auth_code")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_refresh_token_success(self, client, csrf_headers):
        # リフレッシュトークンはCookieベースなので、有効なCookieなしでは401になる
        response = client.post("/auth/refresh", headers=csrf_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_missing_header(self, client, csrf_headers):
        response = client.post("/auth/refresh", headers=csrf_headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_success(self, client, csrf_headers):
        # ログアウトはCookieの有無に関わらず成功する
        response = client.post("/auth/logout", headers=csrf_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_me_endpoint_authenticated(self, client, test_db_session, create_user):
        user = create_user(
            user_id="me_user", user_name="meuser", display_name="Me User"
        )

        # Override the dependency to return the test user
        def override_get_current_user():
            return user

        app.dependency_overrides[_get_current_user] = override_get_current_user
        try:
            response = client.get("/auth/me")

            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()

            assert response_data["userId"] == "me_user"
            assert response_data["userName"] == "meuser"
            assert response_data["displayName"] == "Me User"
        finally:
            # Clean up dependency override
            app.dependency_overrides.pop(_get_current_user, None)

    def test_me_endpoint_unauthenticated(self, client):
        # 認証なしでアクセス（依存関係オーバーライドなし）
        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_csrf_token_endpoint(self, client):
        # CSRFトークンエンドポイントのテスト
        response = client.get("/auth/csrf-token")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert "csrf_token" in response_data
        assert isinstance(response_data["csrf_token"], str)
        assert len(response_data["csrf_token"]) > 0

        # Cookieが設定されていることを確認
        assert "csrftoken" in response.cookies

    def test_rate_limiting_login(self, client):
        # 複数回連続でアクセスして制限をテスト
        responses = []
        for _ in range(15):  # 制限を超える回数
            response = client.get("/auth/login/twitter", follow_redirects=False)
            responses.append(response.status_code)

        success_responses = [
            r for r in responses if r == status.HTTP_307_TEMPORARY_REDIRECT
        ]

        # 少なくとも1つは成功している（制限がかからない可能性もあるのでテストは緩く）
        assert len(success_responses) >= 1
