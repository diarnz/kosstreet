"""audit visibility flags

Revision ID: 0006_audit_visible
Revises: 0005_report_visible
Create Date: 2026-06-06 19:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_audit_visible"
down_revision: str | None = "0005_report_visible"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "audit_runs",
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "audit_suggestions",
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("idx_audit_runs_is_visible", "audit_runs", ["is_visible"])
    op.create_index("idx_audit_suggestions_is_visible", "audit_suggestions", ["is_visible"])


def downgrade() -> None:
    op.drop_index("idx_audit_suggestions_is_visible", table_name="audit_suggestions")
    op.drop_index("idx_audit_runs_is_visible", table_name="audit_runs")
    op.drop_column("audit_suggestions", "is_visible")
    op.drop_column("audit_runs", "is_visible")
