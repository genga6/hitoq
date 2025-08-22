from unittest.mock import patch

import pytest
from fastapi import status

from src.db.tables import Visit
from src.main import app
from src.router.auth import _get_current_user


@pytest.mark.integration
class TestVisitRouter:
    def test_record_visit_authenticated_success(
        self, client, test_db_session, create_user, csrf_headers
    ):
        visitor = create_user(user_id="visitor_user", user_name="visitoruser")
        visited = create_user(user_id="visited_user", user_name="visiteduser")

        with patch("src.router.visit_router._get_current_user") as mock_get_user:
            mock_get_user.return_value = test_db_session.merge(visitor)
            response = client.post(
                f"/users/{visited.user_id}/visit", headers=csrf_headers
            )

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["message"] == "Visit processed successfully"

        # データベースセッションをリフレッシュしてから確認
        visited_user_id = visited.user_id
        visitor_user_id = visitor.user_id
        test_db_session.expunge_all()

        visit = (
            test_db_session.query(Visit)
            .filter(
                Visit.visited_user_id == visited_user_id,
                Visit.visitor_user_id == visitor_user_id,
            )
            .first()
        )
        assert visit is not None
        assert visit.is_anonymous is False

    def test_record_visit_anonymous_success(
        self, client, test_db_session, create_user, csrf_headers
    ):
        visited = create_user(user_id="visited_anon", user_name="visitedanon")

        # 匿名訪問なので認証のみをクリア（DBセッションは残す）
        app.dependency_overrides.pop(_get_current_user, None)
        response = client.post(f"/users/{visited.user_id}/visit", headers=csrf_headers)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["message"] == "Visit processed successfully"

        # データベースセッションをリフレッシュしてから確認
        visited_user_id = visited.user_id
        test_db_session.expunge_all()
        visit = (
            test_db_session.query(Visit)
            .filter(
                Visit.visited_user_id == visited_user_id,
                Visit.visitor_user_id.is_(None),
            )
            .first()
        )
        assert visit is not None
        assert visit.is_anonymous is True

    def test_record_visit_nonexistent_user(self, client, csrf_headers):
        # 認証のみをクリア（DBセッションは残す）
        app.dependency_overrides.pop(_get_current_user, None)
        response = client.post("/users/nonexistent_user/visit", headers=csrf_headers)

        # The current implementation silently handles nonexistent users and returns success
        assert response.status_code == status.HTTP_201_CREATED

    def test_record_self_visit(
        self, client, create_user, test_db_session, csrf_headers
    ):
        user = create_user(user_id="self_visit_user", user_name="selfvisituser")

        with patch("src.router.visit_router._get_current_user") as mock_get_user:
            mock_get_user.return_value = test_db_session.merge(user)
            response = client.post(f"/users/{user.user_id}/visit", headers=csrf_headers)

        # The current implementation silently handles self-visits and returns success
        assert response.status_code == status.HTTP_201_CREATED

    def test_get_user_visits_visible_success(
        self, client, test_db_session, create_user, csrf_headers
    ):
        visitor = create_user(
            user_id="get_visitor", user_name="getvisitor", display_name="Get Visitor"
        )
        visited = create_user(
            user_id="get_visited", user_name="getvisited", visits_visible=True
        )

        visit = Visit(
            visitor_user_id=visitor.user_id,
            visited_user_id=visited.user_id,
            is_anonymous=False,
        )
        test_db_session.add(visit)
        test_db_session.commit()

        response = client.get(f"/users/{visited.user_id}/visits")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) >= 1

        visit_data = response_data[0]
        assert visit_data["visitor_info"]["user_id"] == visitor.user_id
        assert visit_data["visitor_info"]["display_name"] == "Get Visitor"
        assert visit_data["is_anonymous"] is False

    def test_get_user_visits_not_visible(self, client, create_user):
        visited = create_user(
            user_id="private_visited", user_name="privatevisited", visits_visible=False
        )

        response = client.get(f"/users/{visited.user_id}/visits")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) == 0

    def test_get_user_visits_with_anonymous(self, client, test_db_session, create_user):
        visitor = create_user(
            user_id="mixed_visitor",
            user_name="mixedvisitor",
            display_name="Mixed Visitor",
        )
        visited = create_user(
            user_id="mixed_visited", user_name="mixedvisited", visits_visible=True
        )

        # 認証済み訪問と匿名訪問を作成
        visits = [
            Visit(
                visitor_user_id=visitor.user_id,
                visited_user_id=visited.user_id,
                is_anonymous=False,
            ),
            Visit(
                visitor_user_id=None, visited_user_id=visited.user_id, is_anonymous=True
            ),
        ]

        for visit in visits:
            test_db_session.add(visit)
        test_db_session.commit()

        response = client.get(f"/users/{visited.user_id}/visits")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert len(response_data) >= 2

        # 認証済み訪問と匿名訪問の両方が含まれることを確認
        has_authenticated = any(not visit["is_anonymous"] for visit in response_data)
        has_anonymous = any(visit["is_anonymous"] for visit in response_data)

        assert has_authenticated
        assert has_anonymous

    def test_get_user_visits_pagination(self, client, test_db_session, create_user):
        visited = create_user(
            user_id="paginated_visited",
            user_name="paginatedvisited",
            visits_visible=True,
        )

        # 複数の訪問記録を作成
        visitors = []
        for i in range(15):
            visitor = create_user(
                user_id=f"pag_visitor_{i}", user_name=f"pagvisitor{i}"
            )
            visitors.append(visitor)

            visit = Visit(
                visitor_user_id=visitor.user_id,
                visited_user_id=visited.user_id,
                is_anonymous=False,
            )
            test_db_session.add(visit)
        test_db_session.commit()

        # 制限付きで取得
        response = client.get(f"/users/{visited.user_id}/visits?limit=10")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert len(response_data) == 10

    def test_get_user_visits_invalid_limit(self, client, create_user):
        visited = create_user(
            user_id="limit_visited", user_name="limitvisited", visits_visible=True
        )

        # 上限を超えるlimit
        response = client.get(f"/users/{visited.user_id}/visits?limit=200")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_user_visits_nonexistent_user(self, client):
        response = client.get("/users/nonexistent_user/visits")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) == 0

    def test_update_visits_visibility_success(
        self, client, test_db_session, create_user, csrf_headers
    ):
        user = create_user(
            user_id="visibility_user", user_name="visibilityuser", visits_visible=False
        )

        update_data = {"visible": True}

        with patch("src.router.visit_router._get_current_user") as mock_get_user:
            mock_get_user.return_value = test_db_session.merge(user)
            response = client.put(
                f"/users/{user.user_id}/visits-visibility",
                json=update_data,
                headers=csrf_headers,
            )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # データベースで更新されていることを確認
        test_db_session.refresh(user)
        assert user.visits_visible is True

    def test_update_visits_visibility_nonexistent_user(
        self, client, create_user, test_db_session, csrf_headers
    ):
        user = create_user(user_id="auth_user", user_name="authuser")
        update_data = {"visible": True}

        with patch("src.router.visit_router._get_current_user") as mock_get_user:
            mock_get_user.return_value = test_db_session.merge(user)
            response = client.put(
                "/users/nonexistent_user/visits-visibility",
                json=update_data,
                headers=csrf_headers,
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_visits_visibility_success(self, client, create_user, test_db_session):
        user = create_user(
            user_id="get_vis_user", user_name="getvisuser", visits_visible=True
        )

        with patch("src.router.visit_router._get_current_user") as mock_get_user:
            mock_get_user.return_value = test_db_session.merge(user)
            response = client.get(f"/users/{user.user_id}/visits-visibility")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["visible"] is True

    def test_get_visits_visibility_nonexistent_user(
        self, client, create_user, test_db_session, csrf_headers
    ):
        user = create_user(user_id="auth_user2", user_name="authuser2")

        with patch("src.router.visit_router._get_current_user") as mock_get_user:
            mock_get_user.return_value = test_db_session.merge(user)
            response = client.get("/users/nonexistent_user/visits-visibility")

        assert response.status_code == status.HTTP_403_FORBIDDEN
