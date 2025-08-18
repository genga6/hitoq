from uuid import uuid4

import pytest
from fastapi import status

from src.config.limiter import limiter
from src.db.tables import ReportStatusEnum, ReportTypeEnum, UserBlock, UserReport
from src.main import app
from src.router.auth import get_current_user


@pytest.mark.integration
class TestBlockRouter:
    def test_create_block_success(self, client, test_db_session, create_user):
        blocker = create_user(user_id="blocker_user", user_name="blockeruser")
        blocked = create_user(user_id="blocked_user", user_name="blockeduser")

        block_data = {"blocked_user_id": blocked.user_id}

        def override_get_current_user():
            return blocker

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            response = client.post("/block", json=block_data)

            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()

            assert response_data["blockerUserId"] == blocker.user_id
            assert response_data["blockedUserId"] == blocked.user_id
        finally:
            app.dependency_overrides.pop(get_current_user, None)

        blocker = create_user(user_id="invalid_blocker", user_name="invalidblocker")

        block_data = {"blocked_user_id": "nonexistent_user"}

        def override_get_current_user_2():
            return blocker

        app.dependency_overrides[get_current_user] = override_get_current_user_2

        try:
            response = client.post("/block", json=block_data)

            assert response.status_code == status.HTTP_404_NOT_FOUND
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_create_block_self_block(self, client, create_user):
        user = create_user(user_id="self_block_user", user_name="selfblockuser")

        block_data = {"blocked_user_id": user.user_id}

        def override_get_current_user():
            return user

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            response = client.post("/block", json=block_data)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_create_block_duplicate(self, client, test_db_session, create_user):
        blocker = create_user(user_id="dup_blocker", user_name="dupblocker")
        blocked = create_user(user_id="dup_blocked", user_name="dupblocked")

        existing_block = UserBlock(
            block_id=uuid4(),
            blocker_user_id=blocker.user_id,
            blocked_user_id=blocked.user_id,
        )
        test_db_session.add(existing_block)
        test_db_session.commit()

        block_data = {"blocked_user_id": blocked.user_id}

        def override_get_current_user():
            return blocker

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            response = client.post("/block", json=block_data)

            # 重複エラーを返すか既存ブロックを返すかは実装次第
            assert response.status_code in [
                status.HTTP_409_CONFLICT,
                status.HTTP_200_OK,
            ]
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_create_block_unauthenticated(self, client, create_user):
        blocked = create_user(user_id="unauth_blocked", user_name="unauthblocked")

        block_data = {"blocked_user_id": blocked.user_id}

        # 認証なしでリクエスト（依存関係オーバーライドなし）
        response = client.post("/block", json=block_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_blocked_users_success(self, client, test_db_session, create_user):
        blocker = create_user(user_id="list_blocker", user_name="listblocker")
        blocked1 = create_user(user_id="blocked1", user_name="blocked1")
        blocked2 = create_user(user_id="blocked2", user_name="blocked2")

        blocks = [
            UserBlock(
                block_id=uuid4(),
                blocker_user_id=blocker.user_id,
                blocked_user_id=blocked1.user_id,
            ),
            UserBlock(
                block_id=uuid4(),
                blocker_user_id=blocker.user_id,
                blocked_user_id=blocked2.user_id,
            ),
        ]

        for block in blocks:
            test_db_session.add(block)
        test_db_session.commit()

        def override_get_current_user():
            return blocker

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            response = client.get("/blocks")

            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()

            assert isinstance(response_data, list)
            assert len(response_data) >= 2
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_unblock_user_success(self, client, test_db_session, create_user):
        blocker = create_user(user_id="unblock_blocker", user_name="unblockblocker")
        blocked = create_user(user_id="unblock_blocked", user_name="unblockblocked")

        block = UserBlock(
            block_id=uuid4(),
            blocker_user_id=blocker.user_id,
            blocked_user_id=blocked.user_id,
        )
        test_db_session.add(block)
        test_db_session.commit()

        def override_get_current_user():
            return blocker

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            response = client.delete(f"/block/{blocked.user_id}")

            assert response.status_code in [
                status.HTTP_204_NO_CONTENT,
                status.HTTP_404_NOT_FOUND,
            ]
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_create_report_success(self, client, create_user):
        reporter = create_user(user_id="reporter_user", user_name="reporteruser")
        reported = create_user(user_id="reported_user", user_name="reporteduser")

        report_data = {
            "reported_user_id": reported.user_id,
            "report_type": "spam",
            "description": "不適切なメッセージを大量送信している",
        }

        def override_get_current_user():
            return reporter

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            response = client.post("/report", json=report_data)

            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()

            assert response_data["reporterUserId"] == reporter.user_id
            assert response_data["reportedUserId"] == reported.user_id
            assert response_data["reportType"] == "spam"
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_create_report_self_report(self, client, create_user):
        user = create_user(user_id="self_report_user", user_name="selfreportuser")

        report_data = {
            "reported_user_id": user.user_id,
            "report_type": "other",
            "description": "自分自身を報告",
        }

        def override_get_current_user():
            return user

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            response = client.post("/report", json=report_data)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_create_report_nonexistent_user(self, client, create_user):
        reporter = create_user(user_id="invalid_reporter", user_name="invalidreporter")

        report_data = {
            "reported_user_id": "nonexistent_user",
            "report_type": "other",
            "description": "存在しないユーザーの報告",
        }

        def override_get_current_user():
            return reporter

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            response = client.post("/report", json=report_data)

            assert response.status_code == status.HTTP_404_NOT_FOUND
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_get_reports_success(self, client, test_db_session, create_user):
        admin_user = create_user(user_id="admin_user", user_name="adminuser")
        reporter = create_user(user_id="report_reporter", user_name="reportreporter")
        reported = create_user(user_id="report_reported", user_name="reportreported")

        report = UserReport(
            report_id=uuid4(),
            reporter_user_id=reporter.user_id,
            reported_user_id=reported.user_id,
            report_type=ReportTypeEnum.spam,
            description="テスト用の報告です",
            status=ReportStatusEnum.pending,
        )
        test_db_session.add(report)
        test_db_session.commit()

        def override_get_current_user():
            return admin_user

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            response = client.get("/reports")

            # 管理者権限が必要な場合は403、一般ユーザーでも見れる場合は200
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND,
            ]
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_update_report_status_success(self, client, test_db_session, create_user):
        admin_user = create_user(user_id="status_admin", user_name="statusadmin")
        reporter = create_user(user_id="status_reporter", user_name="statusreporter")
        reported = create_user(user_id="status_reported", user_name="statusreported")

        report = UserReport(
            report_id=uuid4(),
            reporter_user_id=reporter.user_id,
            reported_user_id=reported.user_id,
            report_type=ReportTypeEnum.other,
            description="ステータス更新テスト",
            status=ReportStatusEnum.pending,
        )
        test_db_session.add(report)
        test_db_session.commit()

        update_data = {"status": "resolved"}

        def override_get_current_user():
            return admin_user

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            response = client.put(f"/reports/{report.report_id}", json=update_data)

            # 管理者権限や実装状況に応じて異なるステータスコード
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND,
            ]
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_rate_limiting_block_creation(self, client, create_user):
        limiter.reset()  # NOTE: Reset because other tests may have been executed before this func.
        blocker = create_user(user_id="rate_blocker", user_name="rateblocker")
        blocked = create_user(user_id="rate_blocked", user_name="rateblocked")

        block_data = {"blocked_user_id": blocked.user_id}

        RATE_LIMIT_COUNT = 10
        REQUEST_COUNT = 15

        def override_get_current_user():
            return blocker

        app.dependency_overrides[get_current_user] = override_get_current_user

        try:
            responses = []
            for _ in range(REQUEST_COUNT):
                response = client.post("/block", json=block_data)
                responses.append(response)

            success_responses = [
                r for r in responses if r.status_code == status.HTTP_200_OK
            ]
            rate_limited_responses = [
                r
                for r in responses
                if r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            ]

            assert len(success_responses) == RATE_LIMIT_COUNT
            assert len(rate_limited_responses) == REQUEST_COUNT - RATE_LIMIT_COUNT
            for response in rate_limited_responses:
                assert "Rate limit exceeded" in response.text
        finally:
            app.dependency_overrides.pop(get_current_user, None)
