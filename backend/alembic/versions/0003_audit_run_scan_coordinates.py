"""audit run scan coordinates

Revision ID: 0003_scan_coordinates
Revises: 0002_audit_frames
Create Date: 2026-05-22 20:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_scan_coordinates"
down_revision: str | None = "0002_audit_frames"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("audit_runs", sa.Column("scan_latitude", sa.Float(), nullable=True))
    op.add_column("audit_runs", sa.Column("scan_longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("audit_runs", "scan_longitude")
    op.drop_column("audit_runs", "scan_latitude")
