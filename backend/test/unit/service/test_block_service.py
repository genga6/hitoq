from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.db.tables import ReportStatusEnum, ReportTypeEnum
from src.schema.block import BlockCreate, ReportCreate, ReportUpdate
from src.service import block_service


@pytest.mark.unit
class TestBlockService:
    @pytest.mark.parametrize(
        "scenario, blocker_user_info, blocked_user_info, initial_block, expected_error, error_message",
        [
            (
                "success",
                {"user_id": "blocker1", "user_name": "blocker1"},
                {"user_id": "blocked1", "user_name": "blocked1"},
                False,
                None,
                None,
            ),
            (
                "already_exists",
                {"user_id": "blocker2", "user_name": "blocker2"},
                {"user_id": "blocked2", "user_name": "blocked2"},
                True,
                None,
                None,
            ),
            (
                "self_block",
                {"user_id": "self_blocker", "user_name": "self_blocker"},
                {"user_id": "self_blocker", "user_name": "self_blocker"},
                False,
                ValueError,
                "Cannot block yourself",
            ),
        ],
    )
    def test_create_block_scenarios(
        self,
        test_db_session,
        create_user,
        scenario,
        blocker_user_info,
        blocked_user_info,
        initial_block,
        expected_error,
        error_message,
    ):
        blocker = create_user(**blocker_user_info)
        # In self-blocking case, the user is already created.
        if blocker_user_info["user_id"] != blocked_user_info["user_id"]:
            create_user(**blocked_user_info)

        if initial_block:
            block_data = BlockCreate(blocked_user_id=blocked_user_info["user_id"])
            block_service.create_block(test_db_session, blocker.user_id, block_data)

        block_data = BlockCreate(blocked_user_id=blocked_user_info["user_id"])

        if expected_error:
            with pytest.raises(expected_error, match=error_message):
                block_service.create_block(test_db_session, blocker.user_id, block_data)
        else:
            result = block_service.create_block(
                test_db_session, blocker.user_id, block_data
            )
            assert result.blocker_user_id == blocker.user_id
            assert result.blocked_user_id == blocked_user_info["user_id"]

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

    @pytest.mark.parametrize(
        "blocker_user, blocked_user, do_block, expected_result",
        [
            # Test case 1: is_blocked is True
            (
                {"user_id": "check_blocker", "user_name": "checkblocker"},
                {"user_id": "check_blocked", "user_name": "checkblocked"},
                True,
                True,
            ),
            # Test case 2: is_blocked is False
            (
                {"user_id": "no_blocker", "user_name": "noblocker"},
                {"user_id": "no_blocked", "user_name": "noblocked"},
                False,
                False,
            ),
        ],
    )
    def test_is_blocked(
        self,
        test_db_session,
        create_user,
        blocker_user,
        blocked_user,
        do_block,
        expected_result,
    ):
        create_user(**blocker_user)
        create_user(**blocked_user)

        if do_block:
            block_data = BlockCreate(blocked_user_id=blocked_user["user_id"])
            block_service.create_block(
                test_db_session, blocker_user["user_id"], block_data
            )

        result = block_service.is_blocked(
            test_db_session, blocker_user["user_id"], blocked_user["user_id"]
        )
        assert result is expected_result


@pytest.mark.unit
class TestReportService:
    @pytest.mark.parametrize(
        "scenario, reporter_info, reported_info, report_data, expected_error, error_message",
        [
            (
                "success",
                {"user_id": "reporter1", "user_name": "reporter1"},
                {"user_id": "reported1", "user_name": "reported1"},
                {
                    "report_type": ReportTypeEnum.spam,
                    "description": "スパム行為を確認しました",
                },
                None,
                None,
            ),
            (
                "self_report",
                {"user_id": "self_reporter", "user_name": "self_reporter"},
                {"user_id": "self_reporter", "user_name": "self_reporter"},
                {"report_type": ReportTypeEnum.other, "description": "自分をレポート"},
                ValueError,
                "Cannot report yourself",
            ),
        ],
    )
    def test_create_report_scenarios(
        self,
        test_db_session,
        create_user,
        scenario,
        reporter_info,
        reported_info,
        report_data,
        expected_error,
        error_message,
    ):
        reporter = create_user(**reporter_info)
        if reporter_info["user_id"] != reported_info["user_id"]:
            create_user(**reported_info)

        report_data["reported_user_id"] = reported_info["user_id"]
        report_in = ReportCreate(**report_data)

        if expected_error:
            with pytest.raises(expected_error, match=error_message):
                block_service.create_report(
                    test_db_session, reporter.user_id, report_in
                )
        else:
            result = block_service.create_report(
                test_db_session, reporter.user_id, report_in
            )
            assert result.reporter_user_id == reporter.user_id
            assert result.reported_user_id == reported_info["user_id"]
            assert result.report_type == report_data["report_type"]
            assert result.description == report_data["description"]

    @pytest.mark.parametrize(
        "report_type, description",
        [
            (ReportTypeEnum.spam, "スパム報告"),
            (ReportTypeEnum.harassment, "ハラスメント報告"),
            (ReportTypeEnum.inappropriate_content, "不適切なコンテンツ報告"),
            (ReportTypeEnum.other, "その他の問題"),
        ],
    )
    def test_create_report_all_types(
        self, test_db_session, create_user, report_type, description
    ):
        create_user(user_id="type_reporter", user_name="typereporter")
        create_user(user_id="type_reported", user_name="typereported")

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

    @pytest.mark.parametrize(
        "report_id_exists, expected_found",
        [
            (True, True),  # Report exists
            (False, False),  # Report does not exist
        ],
    )
    def test_get_report_by_id(
        self, test_db_session, create_user, report_id_exists, expected_found
    ):
        reporter = create_user(user_id="id_reporter", user_name="idreporter")
        reported = create_user(user_id="id_reported", user_name="idreported")

        report_id = uuid4()
        if report_id_exists:
            report_data = ReportCreate(
                reported_user_id=reported.user_id,
                report_type=ReportTypeEnum.harassment,
                description="テストレポート",
            )
            created_report = block_service.create_report(
                test_db_session, reporter.user_id, report_data
            )
            report_id = created_report.report_id

        result = block_service.get_report_by_id(test_db_session, report_id)

        if expected_found:
            assert result is not None
            assert result.report_id == report_id
        else:
            assert result is None

    @pytest.mark.parametrize(
        "report_exists, expected_success",
        [
            (True, True),  # Report exists and should be updated
            (False, False),  # Report does not exist
        ],
    )
    def test_update_report(
        self, test_db_session, create_user, report_exists, expected_success
    ):
        reporter = create_user(user_id="update_reporter", user_name="updatereporter")
        reported = create_user(user_id="update_reported", user_name="updatereported")

        report_id = uuid4()
        if report_exists:
            report_data = ReportCreate(
                reported_user_id=reported.user_id,
                report_type=ReportTypeEnum.other,
                description="更新前レポート",
            )
            created_report = block_service.create_report(
                test_db_session, reporter.user_id, report_data
            )
            report_id = created_report.report_id

        update_data = ReportUpdate(
            status=ReportStatusEnum.resolved, reviewed_at=datetime.now(timezone.utc)
        )
        result = block_service.update_report(test_db_session, report_id, update_data)

        if expected_success:
            assert result is not None
            assert result.status == ReportStatusEnum.resolved
            assert result.reviewed_at is not None
        else:
            assert result is None

    @pytest.mark.parametrize(
        "status",
        [
            ReportStatusEnum.pending,
            ReportStatusEnum.reviewing,
            ReportStatusEnum.resolved,
            ReportStatusEnum.dismissed,
        ],
    )
    def test_update_report_all_statuses(self, test_db_session, create_user, status):
        create_user(user_id="status_reporter", user_name="statusreporter")
        create_user(user_id="status_reported", user_name="statusreported")

        report_data = ReportCreate(
            reported_user_id="status_reported",
            report_type=ReportTypeEnum.spam,
            description=f"ステータステスト {status.value}",
        )
        created_report = block_service.create_report(
            test_db_session, "status_reporter", report_data
        )

        update_data = ReportUpdate(status=status)
        result = block_service.update_report(
            test_db_session, created_report.report_id, update_data
        )

        assert result is not None
        assert result.status == status


@pytest.mark.unit
class TestBlockServiceIntegration:
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
