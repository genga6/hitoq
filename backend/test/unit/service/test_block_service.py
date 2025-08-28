import pytest

from src.db.tables import ReportStatusEnum, ReportTypeEnum
from src.schema.block import BlockCreate, ReportCreate
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

        # 3. ブロック状況確認
        is_blocked = block_service.is_blocked(
            test_db_session, "workflow_user1", "workflow_user2"
        )
        assert is_blocked is True

        # 4. ブロック解除
        unblock_result = block_service.remove_block(
            test_db_session, "workflow_user1", "workflow_user2"
        )
        assert unblock_result is True

        # 5. ブロック解除確認
        is_still_blocked = block_service.is_blocked(
            test_db_session, "workflow_user1", "workflow_user2"
        )
        assert is_still_blocked is False
