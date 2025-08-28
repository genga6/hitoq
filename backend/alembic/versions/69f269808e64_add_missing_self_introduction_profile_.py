"""add_missing_self_introduction_profile_item_for_existing_users

Revision ID: 69f269808e64
Revises: 1cf365427cbd
Create Date: 2025-08-27 06:17:45.119261

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "69f269808e64"
down_revision: Union[str, Sequence[str], None] = "1cf365427cbd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
