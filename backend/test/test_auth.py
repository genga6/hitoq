from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.router.auth import _create_access_token, _create_refresh_token, _verify_token
from test.test_fixtures import create_test_user


class TestAuthHelpers:
    """認証ヘルパー関数のテスト"""

    def test_create_access_token(self):
        """アクセストークンの作成テスト"""
        user_id = "test_user_123"
        token = _create_access_token(user_id)
        assert isinstance(token, str)
        assert len(token) > 0

        payload = _verify_token(token, "access")
        assert payload["sub"] == user_id
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        """リフレッシュトークンの作成テスト"""
        user_id = "test_user_123"
        token = _create_refresh_token(user_id)
        assert isinstance(token, str)
        assert len(token) > 0

        payload = _verify_token(token, "refresh")
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"

    def test_verify_token_invalid_type(self):
        """無効なトークンタイプのテスト"""
        user_id = "test_user_123"
        access_token = _create_access_token(user_id)

        with pytest.raises(HTTPException):
            _verify_token(access_token, "refresh")


class TestAuthEndpoints:
    """認証エンドポイントのテスト"""

    def test_health_endpoint(self, client: TestClient):
        """ヘルスチェックエンドポイントのテスト"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_root_endpoint(self, client: TestClient):
        """ルートエンドポイントのテスト"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to hitoQ API!"}

    @pytest.mark.auth
    def test_login_twitter_redirect(self, client: TestClient):
        """Twitter ログイン エンドポイントのテスト"""
        response = client.get("/auth/login/twitter", follow_redirects=False)
        assert response.status_code in [302, 307]  # Allow both redirect codes

        location = response.headers["location"]
        assert "twitter.com" in location
        assert "oauth2/authorize" in location
        assert "client_id" in location
        assert "code_challenge" in location

    @pytest.mark.auth
    def test_me_endpoint_without_auth(self, client: TestClient):
        """認証なしでの /me エンドポイントテスト"""
        response = client.get("/auth/me")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.auth
    def test_me_endpoint_with_invalid_token(self, client: TestClient):
        """無効なトークンでの /me エンドポイントテスト"""
        client.cookies.set("access_token", "invalid_token")
        response = client.get("/auth/me")
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    @pytest.mark.auth
    def test_logout_endpoint(self, client: TestClient):
        """ログアウトエンドポイントのテスト"""
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    @pytest.mark.auth
    def test_refresh_token_without_token(self, client: TestClient):
        """リフレッシュトークンなしでのトークン更新テスト"""
        response = client.post("/auth/refresh")
        assert response.status_code == 401
        assert "Refresh token not found" in response.json()["detail"]

    @pytest.mark.auth
    @patch("src.router.auth.user_service.get_user")
    def test_me_endpoint_with_valid_token(
        self, mock_get_user, client: TestClient, test_db_session
    ):
        """有効なトークンでの /me エンドポイントテスト"""
        # テストユーザーを作成
        user = create_test_user(test_db_session)
        mock_get_user.return_value = user

        # 有効なアクセストークンを作成
        token = _create_access_token(user.user_id)
        client.cookies.set("access_token", token)

        response = client.get("/auth/me")
        assert response.status_code == 200
        assert response.json()["userId"] == user.user_id
        assert response.json()["userName"] == user.user_name

    @pytest.mark.auth
    @pytest.mark.slow
    @pytest.mark.skip(reason="TestClient doesn't support session_transaction")
    @patch("httpx.AsyncClient")
    def test_twitter_callback_success(self, mock_client_class, client: TestClient):
        """Twitter コールバックの成功テスト"""
        # モッククライアントのセットアップ
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # トークンレスポンスのモック
        token_response = MagicMock()
        token_response.status_code = 200
        token_response.json.return_value = {"access_token": "mock_access_token"}
        mock_client.post.return_value = token_response

        # ユーザーレスポンスのモック
        user_response = MagicMock()
        user_response.status_code = 200
        user_response.json.return_value = {
            "data": {
                "id": "twitter_user_123",
                "username": "twitter_user",
                "name": "Twitter User",
                "description": "Twitter bio",
                "profile_image_url": "https://pbs.twimg.com/profile_images/123/image_normal.jpg",
            }
        }
        mock_client.get.return_value = user_response

        # セッションにstate と code_verifierを設定
        with client:
            with client.session_transaction() as session:
                session["state"] = "test_state"
                session["code_verifier"] = "test_code_verifier"

            response = client.get(
                "/auth/callback/twitter",
                params={"code": "test_code", "state": "test_state"},
                follow_redirects=False,
            )

            assert response.status_code in [302, 307]  # Allow both redirect codes
            assert "localhost:5173" in response.headers["location"]
