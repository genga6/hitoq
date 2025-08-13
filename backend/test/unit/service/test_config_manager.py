from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.service.config_manager import ConfigManager, get_config_manager


@pytest.mark.unit
class TestConfigManager:
    def test_config_manager_initialization(self, config_manager):
        assert (
            config_manager.config_dir
            == Path(__file__).parent.parent.parent.parent / "src" / "config"
        )
        assert config_manager.versions_file.name == "config_versions.yaml"
        assert config_manager._versions_data is None

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_load_versions_first_time(
        self, mock_yaml_load, mock_file, config_manager, sample_versions_data
    ):
        mock_yaml_load.return_value = sample_versions_data

        result = config_manager.load_versions()

        mock_file.assert_called_once_with(
            config_manager.versions_file, "r", encoding="utf-8"
        )
        mock_yaml_load.assert_called_once()
        assert result == sample_versions_data
        assert config_manager._versions_data == sample_versions_data

    def test_load_versions_cached(self, config_manager, sample_versions_data):
        config_manager._versions_data = sample_versions_data

        with patch("builtins.open") as mock_file:
            result = config_manager.load_versions()

            mock_file.assert_not_called()
            assert result == sample_versions_data

    def test_get_current_version_exists(self, config_manager, sample_versions_data):
        config_manager._versions_data = sample_versions_data

        result = config_manager.get_current_version("profile_labels")
        assert result == "v2.0"

    def test_get_current_version_default(self, config_manager, sample_versions_data):
        config_manager._versions_data = sample_versions_data

        result = config_manager.get_current_version("nonexistent")
        assert result == "v1.0"

    def test_get_migration_path_found(self, config_manager, sample_versions_data):
        config_manager._versions_data = sample_versions_data

        result = config_manager.get_migration_path("profile_labels", "v1.0", "v2.0")

        assert len(result) == 1
        assert result[0]["version"] == "v2.0"
        assert "mappings" in result[0]

    def test_get_migration_path_not_found(self, config_manager, sample_versions_data):
        config_manager._versions_data = sample_versions_data

        result = config_manager.get_migration_path("nonexistent", "v1.0", "v2.0")
        assert result == []

    def test_detect_profile_changes_no_users(self, test_db_session, config_manager):
        result = config_manager.detect_profile_changes(test_db_session)
        assert result is None

    @patch("src.service.config_manager.load_default_labels")
    def test_detect_profile_changes_no_profile_items(
        self, mock_load_labels, test_db_session, create_user, config_manager
    ):
        create_user()
        mock_load_labels.return_value = ["label1", "label2"]

        result = config_manager.detect_profile_changes(test_db_session)
        assert result is None

    @patch("src.service.config_manager.load_default_labels")
    def test_detect_profile_changes_migration_needed(
        self,
        mock_load_labels,
        test_db_session,
        create_user,
        create_profile_item,
        config_manager,
    ):
        user = create_user()
        create_profile_item(
            user.user_id, label="old_label", value="test", display_order=1
        )
        mock_load_labels.return_value = ["new_label", "label2"]

        result = config_manager.detect_profile_changes(test_db_session)

        assert result["needs_migration"] is True
        assert result["config_type"] == "profile_labels"
        assert result["db_labels"] == ["old_label"]
        assert result["expected_labels"] == ["new_label", "label2"]

    @patch("src.service.config_manager.load_default_labels")
    def test_detect_profile_changes_no_migration_needed(
        self,
        mock_load_labels,
        test_db_session,
        create_user,
        create_profile_item,
        config_manager,
    ):
        user = create_user()
        create_profile_item(user.user_id, label="label1", value="test", display_order=1)
        create_profile_item(user.user_id, label="label2", value="test", display_order=2)
        mock_load_labels.return_value = ["label1", "label2"]

        result = config_manager.detect_profile_changes(test_db_session)

        assert result["needs_migration"] is False

    @patch("src.service.config_manager.load_default_labels")
    def test_migrate_profile_labels_success(
        self,
        mock_load_labels,
        test_db_session,
        create_user,
        create_profile_item,
        config_manager,
    ):
        user1 = create_user(user_id="user1")
        user2 = create_user(user_id="user2")

        create_profile_item(
            user1.user_id, label="old_label", value="value1", display_order=1
        )
        create_profile_item(
            user2.user_id, label="old_label", value="value2", display_order=1
        )

        mock_load_labels.return_value = ["new_label"]
        mapping = {"old_label": "new_label"}

        result = config_manager.migrate_profile_labels(test_db_session, mapping)

        assert result["success"] is True
        assert result["migrated_users"] == 2
        assert result["total_users"] == 2
        assert result["mappings_used"] == mapping

    @patch("src.service.config_manager.load_default_labels")
    def test_migrate_profile_labels_no_mapping(
        self,
        mock_load_labels,
        test_db_session,
        create_user,
        create_profile_item,
        config_manager,
    ):
        user = create_user()
        create_profile_item(
            user.user_id, label="same_label", value="value1", display_order=1
        )
        mock_load_labels.return_value = ["same_label", "new_label"]

        result = config_manager.migrate_profile_labels(test_db_session)

        assert result["success"] is True
        assert result["migrated_users"] == 1

    @patch("src.service.config_manager.load_default_labels")
    def test_migrate_profile_labels_with_rollback(
        self, mock_load_labels, test_db_session, create_user, config_manager
    ):
        create_user()
        mock_load_labels.side_effect = Exception("Test error")

        with pytest.raises(Exception, match="Test error"):
            config_manager.migrate_profile_labels(test_db_session)

    def test_get_migration_mapping_found(self, config_manager, sample_versions_data):
        config_manager._versions_data = sample_versions_data

        result = config_manager.get_migration_mapping("profile_labels", "v2.0")

        expected = {"old_label": "new_label", "趣味": "エンタメ"}
        assert result == expected

    def test_get_migration_mapping_not_found(
        self, config_manager, sample_versions_data
    ):
        config_manager._versions_data = sample_versions_data

        result = config_manager.get_migration_mapping("nonexistent", "v2.0")
        assert result == {}

    def test_get_migration_mapping_no_mappings(self, config_manager):
        versions_data = {
            "migrations": {
                "profile_labels": [
                    {"version": "v2.0"}  # mappingsキーなし
                ]
            }
        }
        config_manager._versions_data = versions_data

        result = config_manager.get_migration_mapping("profile_labels", "v2.0")
        assert result == {}


@pytest.mark.unit
class TestConfigManagerGlobal:
    def test_get_config_manager_returns_singleton(self):
        manager1 = get_config_manager()
        manager2 = get_config_manager()

        assert manager1 is manager2
        assert isinstance(manager1, ConfigManager)
