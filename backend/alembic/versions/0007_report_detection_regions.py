"""report AI detection overlays

Revision ID: 0007_report_detection
Revises: 0006_audit_visible
Create Date: 2026-06-06 20:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_report_detection"
down_revision: str | None = "0006_audit_visible"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("reports", sa.Column("severity", sa.String(length=20), nullable=True))
    op.add_column(
        "reports",
        sa.Column("detection_regions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("reports", "detection_regions")
    op.drop_column("reports", "severity")
