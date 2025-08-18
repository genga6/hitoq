"""
Configuration Update Script

Automatically updates profile labels and question templates from YAML files.
Detects changes and runs migrations when needed.

Usage:
    python scripts/update_config.py                 # Check and migrate all configs
    python scripts/update_config.py --check-only    # Only check for changes
    python scripts/update_config.py --profile-only  # Only migrate profile labels
"""

import argparse
import sys
from datetime import datetime

from src.db.session import get_db
from src.service.config_manager import get_config_manager
from src.service.yaml_loader import get_yaml_loader, load_default_labels


def check_profile_changes(config_manager, db):
    """Check if profile labels need migration."""
    print("=== Checking Profile Labels ===")

    status = config_manager.detect_profile_changes(db)

    if not status:
        print("  ℹ️  No users found - nothing to check")
        return False

    if status.get("needs_migration"):
        print("  ⚠️  Changes detected - migration needed")
        print(f"     Current DB labels ({len(status['db_labels'])}):")
        for i, label in enumerate(status["db_labels"], 1):
            print(f"       {i}. {label}")
        print(f"     Expected labels ({len(status['expected_labels'])}):")
        for i, label in enumerate(status["expected_labels"], 1):
            print(f"       {i}. {label}")
        return True
    else:
        print("  ✅ Profile labels are up to date")
        return False


def check_template_changes():
    """Check if question templates are valid and loadable."""
    print("\n=== Checking Question Templates ===")

    try:
        yaml_loader = get_yaml_loader()
        templates = yaml_loader.load_templates()
        print(f"  ✅ Found {len(templates)} valid templates")

        for template in templates:
            print(
                f"     - {template.category.value}: {template.title} ({len(template.questions)} questions)"
            )

        return True

    except Exception as e:
        print(f"  ❌ Template validation failed: {e}")
        return False


def migrate_profile_labels(config_manager, db):
    """Execute profile labels migration."""
    print("\n=== Migrating Profile Labels ===")

    try:
        # Get current version for potential mapping
        current_version = config_manager.get_current_version("profile_labels")
        mapping = config_manager.get_migration_mapping(
            "profile_labels", current_version
        )

        if mapping:
            print(f"Using migration mapping: {mapping}")
        else:
            print("No specific mapping found - using automatic matching")

        result = config_manager.migrate_profile_labels(db, mapping)

        if result.get("success"):
            print("  ✅ Migration completed successfully!")
            print(
                f"     Users migrated: {result['migrated_users']}/{result['total_users']}"
            )
            if result["mappings_used"]:
                print(f"     Mappings applied: {len(result['mappings_used'])}")
        else:
            print(f"  ❌ Migration failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"  ❌ Migration failed: {e}")
        return False

    return True


def update_version_file(config_type: str):
    """Update version in config_versions.yaml."""
    print(f"\n=== Updating Version for {config_type} ===")

    config_manager = get_config_manager()

    try:
        import yaml

        # Load current data
        with open(config_manager.versions_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Generate new version number
        current_version = data["versions"].get(config_type, "v1.0")
        major, minor = current_version[1:].split(".")
        new_version = f"v{major}.{int(minor) + 1}"

        # Update version
        data["versions"][config_type] = new_version

        # Add migration entry for profile labels
        if config_type == "profile_labels":
            current_labels = load_default_labels()

            new_migration = {
                "version": new_version,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "description": f"Updated to version {new_version}",
                "labels": current_labels,
                "mappings": {},  # Add mappings manually if needed
            }

            if config_type not in data["migrations"]:
                data["migrations"][config_type] = []

            data["migrations"][config_type].append(new_migration)

        # Save updated data
        with open(config_manager.versions_file, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f, allow_unicode=True, default_flow_style=False, sort_keys=False
            )

        print(f"  ✅ Updated version to {new_version}")
        print("     Don't forget to add mappings in config_versions.yaml if needed")

    except Exception as e:
        print(f"  ❌ Failed to update version: {e}")


def main():
    parser = argparse.ArgumentParser(description="Configuration Update Tool")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for changes, do not migrate",
    )
    parser.add_argument(
        "--profile-only", action="store_true", help="Only process profile labels"
    )

    args = parser.parse_args()

    print("🔧 Configuration Update Tool")
    print("=" * 50)

    config_manager = get_config_manager()
    db = next(get_db())

    try:
        # Check profile labels
        profile_needs_migration = check_profile_changes(config_manager, db)

        # Check question templates (unless profile-only)
        template_ok = True
        if not args.profile_only:
            template_ok = check_template_changes()

        # If check-only, just report and exit
        if args.check_only:
            if profile_needs_migration:
                print("\n📋 Summary: Profile migration needed")
                sys.exit(1)
            elif not template_ok:
                print("\n📋 Summary: Template issues found")
                sys.exit(1)
            else:
                print("\n📋 Summary: All configurations are up to date")
                sys.exit(0)

        # Execute migrations if needed
        migration_success = True

        if profile_needs_migration:
            migration_success = migrate_profile_labels(config_manager, db)
            if migration_success:
                update_version_file("profile_labels")

        # Reload templates to ensure they're cached properly
        if not args.profile_only and template_ok:
            yaml_loader = get_yaml_loader()
            yaml_loader.reload_templates()
            print("\n  ✅ Question templates reloaded")

        if migration_success:
            print("\n🎉 All configurations updated successfully!")
        else:
            print("\n❌ Some updates failed")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
