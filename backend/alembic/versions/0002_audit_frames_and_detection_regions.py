"""audit frames and detection regions

Revision ID: 0002_audit_frames
Revises: 0001_initial
Create Date: 2026-05-22 18:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_audit_frames"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_frames",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("audit_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("frame_index", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("heading", sa.Integer(), nullable=False),
        sa.Column("pitch", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_civic_issue", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("detection_regions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("model_name", sa.Text(), nullable=True),
        sa.Column("suggestion_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["audit_run_id"], ["audit_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["suggestion_id"], ["audit_suggestions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("audit_run_id", "frame_index", name="uq_audit_frames_run_index"),
    )
    op.create_index("idx_audit_frames_run_id", "audit_frames", ["audit_run_id"])
    op.create_index("idx_audit_frames_suggestion_id", "audit_frames", ["suggestion_id"])

    op.add_column(
        "audit_suggestions",
        sa.Column("frame_index", sa.Integer(), nullable=True),
    )
    op.add_column(
        "audit_suggestions",
        sa.Column(
            "detection_regions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("audit_suggestions", "detection_regions")
    op.drop_column("audit_suggestions", "frame_index")
    op.drop_index("idx_audit_frames_suggestion_id", table_name="audit_frames")
    op.drop_index("idx_audit_frames_run_id", table_name="audit_frames")
    op.drop_table("audit_frames")
