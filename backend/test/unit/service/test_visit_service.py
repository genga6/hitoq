from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from src.service import visit_service


@pytest.mark.unit
class TestVisitService:
    def test_record_visit_success(self, test_db_session, create_user):
        create_user(user_id="visitor")
        create_user(user_id="visited")

        result = visit_service.record_visit(test_db_session, "visited", "visitor")

        assert result is not None
        assert result.visitor_user_id == "visitor"
        assert result.visited_user_id == "visited"
        assert result.is_anonymous is False
        assert result.visited_at is not None

    def test_record_visit_anonymous(self, test_db_session, create_user):
        create_user(user_id="visited")

        result = visit_service.record_visit(test_db_session, "visited", None)

        assert result is not None
        assert result.visitor_user_id is None
        assert result.visited_user_id == "visited"
        assert result.is_anonymous is True

    def test_record_visit_self_visit(self, test_db_session, create_user):
        create_user(user_id="self_user")

        result = visit_service.record_visit(test_db_session, "self_user", "self_user")

        assert result is None

    def test_record_visit_nonexistent_user(self, test_db_session):
        result = visit_service.record_visit(test_db_session, "nonexistent", "visitor")

        assert result is None

    @patch("src.service.visit_service.datetime")
    def test_record_visit_recent_visit_update(
        self, mock_datetime, test_db_session, create_user
    ):
        create_user(user_id="visitor")
        create_user(user_id="visited")

        base_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = base_time

        # 最初の訪問
        first_visit = visit_service.record_visit(test_db_session, "visited", "visitor")

        # 30分後の再訪問（1時間以内なので既存レコードを更新）
        later_time = base_time + timedelta(minutes=30)
        mock_datetime.utcnow.return_value = later_time

        second_visit = visit_service.record_visit(test_db_session, "visited", "visitor")

        # 同じレコードが更新されている
        assert first_visit.visit_id == second_visit.visit_id
        assert second_visit.visited_at == later_time

    @patch("src.service.visit_service.datetime")
    def test_record_visit_old_visit_new_record(
        self, mock_datetime, test_db_session, create_user
    ):
        create_user(user_id="visitor")
        create_user(user_id="visited")

        base_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = base_time

        # 最初の訪問
        first_visit = visit_service.record_visit(test_db_session, "visited", "visitor")

        # 2時間後の再訪問（1時間を超えているので新しいレコード）
        later_time = base_time + timedelta(hours=2)
        mock_datetime.utcnow.return_value = later_time

        second_visit = visit_service.record_visit(test_db_session, "visited", "visitor")

        # 異なるレコードが作成されている
        assert first_visit.visit_id != second_visit.visit_id
        assert second_visit.visited_at == later_time

    def test_get_user_visits_visible(self, test_db_session, create_user):
        create_user(user_id="visitor", display_name="Visitor User")
        create_user(user_id="visited", visits_visible=True)

        visit_service.record_visit(test_db_session, "visited", "visitor")

        result = visit_service.get_user_visits(test_db_session, "visited")

        assert len(result) == 1
        assert result[0].visitor_user_id == "visitor"
        assert result[0].visitor_user.display_name == "Visitor User"

    def test_get_user_visits_not_visible(self, test_db_session, create_user):
        create_user(user_id="visitor")
        create_user(user_id="visited", visits_visible=False)

        visit_service.record_visit(test_db_session, "visited", "visitor")

        result = visit_service.get_user_visits(test_db_session, "visited")

        assert result == []

    def test_get_user_visits_nonexistent_user(self, test_db_session):
        result = visit_service.get_user_visits(test_db_session, "nonexistent")

        assert result == []

    def test_get_user_visits_multiple_visits_same_visitor(
        self, test_db_session, create_user
    ):
        create_user(user_id="visitor")
        create_user(user_id="visited", visits_visible=True)

        # 同じ訪問者が複数回訪問
        visit_service.record_visit(test_db_session, "visited", "visitor")
        visit_service.record_visit(test_db_session, "visited", "visitor")
        visit3 = visit_service.record_visit(test_db_session, "visited", "visitor")

        result = visit_service.get_user_visits(test_db_session, "visited")

        # 最新の1件のみが返される
        assert len(result) == 1
        assert result[0].visit_id == visit3.visit_id

    def test_get_user_visits_multiple_visitors(self, test_db_session, create_user):
        create_user(user_id="visitor1", display_name="Visitor 1")
        create_user(user_id="visitor2", display_name="Visitor 2")
        create_user(user_id="visited", visits_visible=True)

        visit_service.record_visit(test_db_session, "visited", "visitor1")
        visit_service.record_visit(test_db_session, "visited", "visitor2")

        result = visit_service.get_user_visits(test_db_session, "visited")

        assert len(result) == 2
        visitor_ids = [visit.visitor_user_id for visit in result]
        assert "visitor1" in visitor_ids
        assert "visitor2" in visitor_ids

    def test_get_user_visits_with_anonymous(self, test_db_session, create_user):
        create_user(user_id="visitor")
        create_user(user_id="visited", visits_visible=True)

        visit_service.record_visit(test_db_session, "visited", "visitor")
        visit_service.record_visit(test_db_session, "visited", None)  # 匿名訪問

        result = visit_service.get_user_visits(test_db_session, "visited")

        assert len(result) == 2
        anonymous_visits = [visit for visit in result if visit.is_anonymous]
        named_visits = [visit for visit in result if not visit.is_anonymous]

        assert len(anonymous_visits) == 1
        assert len(named_visits) == 1

    def test_get_user_visits_limit(self, test_db_session, create_user):
        # 個別に訪問者を作成
        visitors = []
        for i in range(10):
            visitor = create_user(user_id=f"visitor_{i}", user_name=f"visitor{i}")
            visitors.append(visitor)

        visited = create_user(
            user_id="visited_user", user_name="visiteduser", visits_visible=True
        )

        # 複数の訪問者が訪問
        for visitor in visitors:
            visit_service.record_visit(
                test_db_session, visited.user_id, visitor.user_id
            )

        result = visit_service.get_user_visits(
            test_db_session, visited.user_id, limit=5
        )

        assert len(result) == 5

    def test_get_visit_count(self, test_db_session, create_user):
        create_user(user_id="visitor1")
        create_user(user_id="visitor2")
        create_user(user_id="visited")

        visit_service.record_visit(test_db_session, "visited", "visitor1")
        visit_service.record_visit(test_db_session, "visited", "visitor2")
        visit_service.record_visit(test_db_session, "visited", None)  # 匿名

        result = visit_service.get_visit_count(test_db_session, "visited")

        assert result == 3

    def test_get_visit_count_no_visits(self, test_db_session, create_user):
        create_user(user_id="visited")

        result = visit_service.get_visit_count(test_db_session, "visited")

        assert result == 0

    def test_update_visits_visibility_true(self, test_db_session, create_user):
        user = create_user(user_id="test_user", visits_visible=False)

        result = visit_service.update_visits_visibility(
            test_db_session, "test_user", True
        )

        assert result is True
        assert user.visits_visible is True

    def test_update_visits_visibility_false(self, test_db_session, create_user):
        user = create_user(user_id="test_user", visits_visible=True)

        result = visit_service.update_visits_visibility(
            test_db_session, "test_user", False
        )

        assert result is True
        assert user.visits_visible is False

    def test_update_visits_visibility_nonexistent_user(self, test_db_session):
        result = visit_service.update_visits_visibility(
            test_db_session, "nonexistent", True
        )

        assert result is False

    def test_get_visits_visibility_true(self, test_db_session, create_user):
        create_user(user_id="test_user", visits_visible=True)

        result = visit_service.get_visits_visibility(test_db_session, "test_user")

        assert result is True

    def test_get_visits_visibility_false(self, test_db_session, create_user):
        create_user(user_id="test_user", visits_visible=False)

        result = visit_service.get_visits_visibility(test_db_session, "test_user")

        assert result is False

    def test_get_visits_visibility_nonexistent_user(self, test_db_session):
        result = visit_service.get_visits_visibility(test_db_session, "nonexistent")

        assert result is False

    def test_visit_workflow(self, test_db_session, create_user):
        create_user(user_id="visitor", display_name="Visitor User")
        create_user(user_id="visited", visits_visible=True)

        # 訪問記録
        visit = visit_service.record_visit(test_db_session, "visited", "visitor")
        assert visit is not None

        # 訪問カウント確認
        count = visit_service.get_visit_count(test_db_session, "visited")
        assert count == 1

        # 訪問リスト取得
        visits = visit_service.get_user_visits(test_db_session, "visited")
        assert len(visits) == 1
        assert visits[0].visitor_user.display_name == "Visitor User"

        # 表示設定を非表示にする
        result = visit_service.update_visits_visibility(
            test_db_session, "visited", False
        )
        assert result is True

        # 非表示設定後は訪問リストが空になる
        visits_hidden = visit_service.get_user_visits(test_db_session, "visited")
        assert visits_hidden == []
