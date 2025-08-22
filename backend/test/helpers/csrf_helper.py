"""テスト用CSRF関連ヘルパー関数"""

from src.service.token_service import TokenService


def get_csrf_headers():
    """CSRFトークン付きヘッダーを生成する"""
    csrf_token = TokenService.create_csrf_token()
    return {"X-CSRFToken": csrf_token, "Cookie": f"csrf_token={csrf_token}"}


def add_csrf_to_headers(headers=None):
    """既存のヘッダーにCSRFトークンを追加する"""
    if headers is None:
        headers = {}

    csrf_token = TokenService.create_csrf_token()
    headers.update(
        {
            "X-CSRFToken": csrf_token,
        }
    )

    # Cookieヘッダーがある場合は追加、ない場合は新規作成
    cookie_header = headers.get("Cookie", "")
    if cookie_header:
        headers["Cookie"] = f"{cookie_header}; csrf_token={csrf_token}"
    else:
        headers["Cookie"] = f"csrf_token={csrf_token}"

    return headers


def setup_csrf_for_client(client):
    """TestClientにCSRFトークンを設定する"""
    csrf_token = TokenService.create_csrf_token()
    client.cookies.set("csrf_token", csrf_token)
    return {"X-CSRFToken": csrf_token}


def make_csrf_request(client, method, url, csrf_headers=None, **kwargs):
    """CSRF対応のリクエストを送信する"""
    csrf_token = TokenService.create_csrf_token()

    # クッキーを設定
    client.cookies.set("csrf_token", csrf_token)

    # ヘッダーを準備
    headers = kwargs.get("headers", {})
    headers["X-CSRFToken"] = csrf_token

    # 既存のCSRFヘッダーがある場合はマージ
    if csrf_headers:
        headers.update(csrf_headers)
        # CSRFトークンは新しく生成したものを使用
        headers["X-CSRFToken"] = csrf_token

    kwargs["headers"] = headers

    # リクエストを送信
    return getattr(client, method.lower())(url, **kwargs)
