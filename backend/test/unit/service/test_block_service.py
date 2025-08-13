from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.db.tables import ReportStatusEnum, ReportTypeEnum
from src.schema.block import BlockCreate, ReportCreate, ReportUpdate
from src.service import block_service


@pytest.mark.unit
class TestBlockService:
    def test_create_block_success(self, test_db_session, create_user):
        create_user(
            user_id="blocker_user", user_name="blockeruser", display_name="Blocker User"
        )
        create_user(
            user_id="blocked_user", user_name="blockeduser", display_name="Blocked User"
        )

        # ブロック作成
        block_data = BlockCreate(blocked_user_id="blocked_user")
        result = block_service.create_block(test_db_session, "blocker_user", block_data)

        assert result.blocker_user_id == "blocker_user"
        assert result.blocked_user_id == "blocked_user"
        assert result.block_id is not None
        assert result.created_at is not None

    def test_create_block_already_exists(self, test_db_session, create_user):
        create_user(
            user_id="blocker_user2",
            user_name="blockeruser2",
            display_name="Blocker User 2",
        )
        create_user(
            user_id="blocked_user2",
            user_name="blockeduser2",
            display_name="Blocked User 2",
        )

        # 最初のブロック
        block_data = BlockCreate(blocked_user_id="blocked_user2")
        first_block = block_service.create_block(
            test_db_session, "blocker_user2", block_data
        )

        # 二回目のブロック（同じものを返す）
        second_block = block_service.create_block(
            test_db_session, "blocker_user2", block_data
        )

        assert first_block.block_id == second_block.block_id
        assert first_block.created_at == second_block.created_at

    def test_create_block_self_block(self, test_db_session, create_user):
        create_user(user_id="self_user", user_name="selfuser", display_name="Self User")

        block_data = BlockCreate(blocked_user_id="self_user")

        with pytest.raises(ValueError, match="Cannot block yourself"):
            block_service.create_block(test_db_session, "self_user", block_data)

    def test_remove_block_success(self, test_db_session, create_user):
        create_user(
            user_id="remove_blocker",
            user_name="removeblocker",
            display_name="Remove Blocker",
        )
        create_user(
            user_id="remove_blocked",
            user_name="removeblocked",
            display_name="Remove Blocked",
        )

        # ブロック作成
        block_data = BlockCreate(blocked_user_id="remove_blocked")
        block_service.create_block(test_db_session, "remove_blocker", block_data)

        # ブロック解除
        result = block_service.remove_block(
            test_db_session, "remove_blocker", "remove_blocked"
        )

        assert result is True

        # ブロックが削除されていることを確認
        is_blocked = block_service.is_blocked(
            test_db_session, "remove_blocker", "remove_blocked"
        )
        assert is_blocked is False

    def test_remove_block_not_exists(self, test_db_session):
        """存在しないブロックの解除"""
        result = block_service.remove_block(
            test_db_session, "nonexistent_blocker", "nonexistent_blocked"
        )
        assert result is False

    def test_get_blocked_users(self, test_db_session, create_user):
        create_user(
            user_id="list_blocker", user_name="listblocker", display_name="List Blocker"
        )
        create_user(
            user_id="list_blocked1",
            user_name="listblocked1",
            display_name="List Blocked 1",
        )
        create_user(
            user_id="list_blocked2",
            user_name="listblocked2",
            display_name="List Blocked 2",
        )

        # ブロック作成
        block_data1 = BlockCreate(blocked_user_id="list_blocked1")
        block_data2 = BlockCreate(blocked_user_id="list_blocked2")
        block_service.create_block(test_db_session, "list_blocker", block_data1)
        block_service.create_block(test_db_session, "list_blocker", block_data2)

        # ブロック一覧取得
        result = block_service.get_blocked_users(test_db_session, "list_blocker")

        assert len(result) == 2
        blocked_user_ids = [block.blocked_user_id for block in result]
        assert "list_blocked1" in blocked_user_ids
        assert "list_blocked2" in blocked_user_ids

    def test_is_blocked_true(self, test_db_session, create_user):
        create_user(
            user_id="check_blocker",
            user_name="checkblocker",
            display_name="Check Blocker",
        )
        create_user(
            user_id="check_blocked",
            user_name="checkblocked",
            display_name="Check Blocked",
        )

        block_data = BlockCreate(blocked_user_id="check_blocked")
        block_service.create_block(test_db_session, "check_blocker", block_data)

        result = block_service.is_blocked(
            test_db_session, "check_blocker", "check_blocked"
        )
        assert result is True

    def test_is_blocked_false(self, test_db_session):
        """ブロック状態確認（ブロック未実施）"""
        result = block_service.is_blocked(test_db_session, "no_blocker", "no_blocked")
        assert result is False


@pytest.mark.unit
class TestReportService:
    """レポートサービスのユニットテスト"""

    def test_create_report_success(self, test_db_session, create_user):
        create_user(
            user_id="reporter_user",
            user_name="reporteruser",
            display_name="Reporter User",
        )
        create_user(
            user_id="reported_user",
            user_name="reporteduser",
            display_name="Reported User",
        )

        # レポート作成
        report_data = ReportCreate(
            reported_user_id="reported_user",
            report_type=ReportTypeEnum.spam,
            description="スパム行為を確認しました",
        )
        result = block_service.create_report(
            test_db_session, "reporter_user", report_data
        )

        assert result.reporter_user_id == "reporter_user"
        assert result.reported_user_id == "reported_user"
        assert result.report_type == ReportTypeEnum.spam
        assert result.description == "スパム行為を確認しました"
        assert result.status == ReportStatusEnum.pending
        assert result.created_at is not None

    def test_create_report_self_report(self, test_db_session, create_user):
        create_user(
            user_id="self_report_user",
            user_name="selfreportuser",
            display_name="Self Report User",
        )

        report_data = ReportCreate(
            reported_user_id="self_report_user",
            report_type=ReportTypeEnum.other,
            description="自分をレポート",
        )

        with pytest.raises(ValueError, match="Cannot report yourself"):
            block_service.create_report(
                test_db_session, "self_report_user", report_data
            )

    def test_create_report_all_types(self, test_db_session, create_user):
        create_user(
            user_id="type_reporter",
            user_name="typereporter",
            display_name="Type Reporter",
        )
        create_user(
            user_id="type_reported",
            user_name="typereported",
            display_name="Type Reported",
        )

        report_types = [
            (ReportTypeEnum.spam, "スパム報告"),
            (ReportTypeEnum.harassment, "ハラスメント報告"),
            (ReportTypeEnum.inappropriate_content, "不適切なコンテンツ報告"),
            (ReportTypeEnum.other, "その他の問題"),
        ]

        for report_type, description in report_types:
            report_data = ReportCreate(
                reported_user_id="type_reported",
                report_type=report_type,
                description=description,
            )
            result = block_service.create_report(
                test_db_session, "type_reporter", report_data
            )

            assert result.report_type == report_type
            assert result.description == description

    def test_get_reports_pagination(self, test_db_session, create_user):
        create_user(
            user_id="pagination_reporter",
            user_name="paginationreporter",
            display_name="Pagination Reporter",
        )
        create_user(
            user_id="pagination_reported",
            user_name="paginationreported",
            display_name="Pagination Reported",
        )

        # 複数のレポートを作成
        for i in range(15):
            report_data = ReportCreate(
                reported_user_id="pagination_reported",
                report_type=ReportTypeEnum.spam,
                description=f"レポート {i}",
            )
            block_service.create_report(
                test_db_session, "pagination_reporter", report_data
            )

        # ページネーションテスト
        first_page = block_service.get_reports(test_db_session, skip=0, limit=10)
        second_page = block_service.get_reports(test_db_session, skip=10, limit=10)

        assert len(first_page) == 10
        assert len(second_page) == 5

        # 重複がないことを確認
        first_page_ids = {report.report_id for report in first_page}
        second_page_ids = {report.report_id for report in second_page}
        assert len(first_page_ids.intersection(second_page_ids)) == 0

    def test_get_report_by_id_exists(self, test_db_session, create_user):
        create_user(
            user_id="id_reporter", user_name="idreporter", display_name="ID Reporter"
        )
        create_user(
            user_id="id_reported", user_name="idreported", display_name="ID Reported"
        )

        report_data = ReportCreate(
            reported_user_id="id_reported",
            report_type=ReportTypeEnum.harassment,
            description="テストレポート",
        )
        created_report = block_service.create_report(
            test_db_session, "id_reporter", report_data
        )

        # ID指定で取得
        result = block_service.get_report_by_id(
            test_db_session, created_report.report_id
        )

        assert result is not None
        assert result.report_id == created_report.report_id
        assert result.reporter_user_id == "id_reporter"
        assert result.reported_user_id == "id_reported"

    def test_get_report_by_id_not_exists(self, test_db_session):
        """レポートID指定取得（存在しない場合）"""
        non_existent_id = uuid4()
        result = block_service.get_report_by_id(test_db_session, non_existent_id)
        assert result is None

    def test_update_report_success(self, test_db_session, create_user):
        create_user(
            user_id="update_reporter",
            user_name="updatereporter",
            display_name="Update Reporter",
        )
        create_user(
            user_id="update_reported",
            user_name="updatereported",
            display_name="Update Reported",
        )

        report_data = ReportCreate(
            reported_user_id="update_reported",
            report_type=ReportTypeEnum.other,
            description="更新前レポート",
        )
        created_report = block_service.create_report(
            test_db_session, "update_reporter", report_data
        )

        # レポート更新
        update_data = ReportUpdate(
            status=ReportStatusEnum.resolved, reviewed_at=datetime.now(timezone.utc)
        )
        result = block_service.update_report(
            test_db_session, created_report.report_id, update_data
        )

        assert result is not None
        assert result.status == ReportStatusEnum.resolved
        assert result.reviewed_at is not None

    def test_update_report_not_found(self, test_db_session):
        """存在しないレポートの更新"""
        non_existent_id = uuid4()
        update_data = ReportUpdate(status=ReportStatusEnum.dismissed)

        result = block_service.update_report(
            test_db_session, non_existent_id, update_data
        )
        assert result is None

    def test_update_report_all_statuses(self, test_db_session, create_user):
        create_user(
            user_id="status_reporter",
            user_name="statusreporter",
            display_name="Status Reporter",
        )
        create_user(
            user_id="status_reported",
            user_name="statusreported",
            display_name="Status Reported",
        )

        statuses = [
            ReportStatusEnum.pending,
            ReportStatusEnum.reviewing,
            ReportStatusEnum.resolved,
            ReportStatusEnum.dismissed,
        ]

        for status in statuses:
            # 各ステータス用のレポートを作成
            report_data = ReportCreate(
                reported_user_id="status_reported",
                report_type=ReportTypeEnum.spam,
                description=f"ステータステスト {status.value}",
            )
            created_report = block_service.create_report(
                test_db_session, "status_reporter", report_data
            )

            # ステータス更新
            update_data = ReportUpdate(status=status)
            result = block_service.update_report(
                test_db_session, created_report.report_id, update_data
            )

            assert result is not None
            assert result.status == status


@pytest.mark.unit
class TestBlockServiceIntegration:
    """ブロックサービスの統合的なテスト"""

    def test_block_and_report_workflow(self, test_db_session, create_user):
        create_user(
            user_id="workflow_user1",
            user_name="workflowuser1",
            display_name="Workflow User 1",
        )
        create_user(
            user_id="workflow_user2",
            user_name="workflowuser2",
            display_name="Workflow User 2",
        )

        # 1. レポート作成
        report_data = ReportCreate(
            reported_user_id="workflow_user2",
            report_type=ReportTypeEnum.harassment,
            description="ハラスメント行為",
        )
        report = block_service.create_report(
            test_db_session, "workflow_user1", report_data
        )
        assert report.status == ReportStatusEnum.pending

        # 2. ブロック実行
        block_data = BlockCreate(blocked_user_id="workflow_user2")
        block = block_service.create_block(
            test_db_session, "workflow_user1", block_data
        )
        assert block.blocked_user_id == "workflow_user2"

        # 3. レポート状況確認・更新
        update_data = ReportUpdate(
            status=ReportStatusEnum.resolved, reviewed_at=datetime.now(timezone.utc)
        )
        updated_report = block_service.update_report(
            test_db_session, report.report_id, update_data
        )
        assert updated_report.status == ReportStatusEnum.resolved

        # 4. ブロック状況確認
        is_blocked = block_service.is_blocked(
            test_db_session, "workflow_user1", "workflow_user2"
        )
        assert is_blocked is True

        # 5. ブロック解除
        unblock_result = block_service.remove_block(
            test_db_session, "workflow_user1", "workflow_user2"
        )
        assert unblock_result is True

        # 6. ブロック解除確認
        is_still_blocked = block_service.is_blocked(
            test_db_session, "workflow_user1", "workflow_user2"
        )
        assert is_still_blocked is False
