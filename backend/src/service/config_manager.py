import uuid
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from src.db.tables import ProfileItem, User
from src.service.yaml_loader import load_default_labels


class ConfigManager:
    def __init__(self) -> None:
        self.config_dir = Path(__file__).parent.parent / "config"
        self.versions_file = self.config_dir / "config_versions.yaml"
        self._versions_data: dict | None = None

    def load_versions(self) -> dict:
        if self._versions_data is None:
            with open(self.versions_file, "r", encoding="utf-8") as f:
                self._versions_data = yaml.safe_load(f)
        return self._versions_data

    def get_current_version(self, config_type: str) -> str:
        versions_data = self.load_versions()
        return versions_data["versions"].get(config_type, "v1.0")

    def get_migration_path(
        self, config_type: str, from_version: str, to_version: str
    ) -> list[dict]:
        versions_data = self.load_versions()
        migrations = versions_data["migrations"].get(config_type, [])

        migration_path = []
        for migration in migrations:
            if migration["version"] == to_version:
                migration_path.append(migration)

        return migration_path

    def detect_profile_changes(self, db: Session) -> dict | None:
        current_version = self.get_current_version("profile_labels")

        first_user = db.query(User).first()
        if not first_user:
            return None

        user_items = (
            db.query(ProfileItem)
            .filter(ProfileItem.user_id == first_user.user_id)
            .order_by(ProfileItem.display_order)
            .all()
        )

        if not user_items:
            return None

        db_labels = [item.label for item in user_items]

        expected_labels = load_default_labels()

        if db_labels != expected_labels:
            return {
                "config_type": "profile_labels",
                "current_version": current_version,
                "db_labels": db_labels,
                "expected_labels": expected_labels,
                "needs_migration": True,
            }

        return {"needs_migration": False}

    def migrate_profile_labels(
        self, db: Session, mapping: dict[str, str] | None = None
    ) -> dict:
        new_labels = load_default_labels()
        users = db.query(User).all()

        migration_result: dict = {
            "migrated_users": 0,
            "total_users": len(users),
            "mappings_used": mapping or {},
            "unmapped_labels": [],
        }

        try:
            for user in users:
                current_items = (
                    db.query(ProfileItem)
                    .filter(ProfileItem.user_id == user.user_id)
                    .order_by(ProfileItem.display_order)
                    .all()
                )

                old_values = {}
                for item in current_items:
                    old_values[item.label] = item.value

                for item in current_items:
                    db.delete(item)

                for i, new_label in enumerate(new_labels, 1):
                    value = ""

                    if mapping:
                        for old_label, mapped_label in mapping.items():
                            if mapped_label == new_label and old_label in old_values:
                                value = old_values[old_label]
                                break

                    if not value and new_label in old_values:
                        value = old_values[new_label]

                    new_item = ProfileItem(
                        profile_item_id=uuid.uuid4(),
                        user_id=user.user_id,
                        label=new_label,
                        value=value,
                        display_order=i,
                    )
                    db.add(new_item)

                migration_result["migrated_users"] += 1

            db.commit()
            migration_result["success"] = True

        except Exception as e:
            db.rollback()
            migration_result["success"] = False
            migration_result["error"] = str(e)
            raise

        return migration_result

    def get_migration_mapping(
        self, config_type: str, to_version: str
    ) -> dict[str, str]:
        versions_data = self.load_versions()
        migrations = versions_data["migrations"].get(config_type, [])

        for migration in migrations:
            if migration["version"] == to_version:
                return migration.get("mappings", {})

        return {}


config_manager = ConfigManager()


def get_config_manager() -> ConfigManager:
    return config_manager
