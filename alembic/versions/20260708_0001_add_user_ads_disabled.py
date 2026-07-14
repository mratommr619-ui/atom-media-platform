"""add user ads disabled flag

Revision ID: 20260708_0001
Revises:
Create Date: 2026-07-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260708_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("ads_disabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("users", "ads_disabled", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "ads_disabled")
