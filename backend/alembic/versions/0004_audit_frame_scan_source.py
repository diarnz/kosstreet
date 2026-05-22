"""audit frame scan source

Revision ID: 0004_scan_source
Revises: 0003_scan_coordinates
Create Date: 2026-05-22 22:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_scan_source"
down_revision: str | None = "0003_scan_coordinates"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "audit_frames",
        sa.Column(
            "scan_source",
            sa.String(length=20),
            nullable=False,
            server_default="pipeline",
        ),
    )
    op.alter_column("audit_frames", "scan_source", server_default=None)


def downgrade() -> None:
    op.drop_column("audit_frames", "scan_source")
