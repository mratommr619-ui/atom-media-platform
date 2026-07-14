"""Add target counts for broadcast progress reporting."""

from alembic import op
import sqlalchemy as sa

revision = "20260714_0002"
down_revision = "20260708_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("broadcasts", sa.Column("total_users_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("broadcasts", sa.Column("target_count", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("broadcasts", "target_count")
    op.drop_column("broadcasts", "total_users_count")
