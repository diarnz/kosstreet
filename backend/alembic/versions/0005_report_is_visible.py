"""report visibility flag

Revision ID: 0005_report_visible
Revises: 0004_scan_source
Create Date: 2026-06-06 18:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_report_visible"
down_revision: str | None = "0004_scan_source"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "reports",
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("idx_reports_is_visible", "reports", ["is_visible"])


def downgrade() -> None:
    op.drop_index("idx_reports_is_visible", table_name="reports")
    op.drop_column("reports", "is_visible")
