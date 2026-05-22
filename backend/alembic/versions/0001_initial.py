"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-22 13:25:00

"""
from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "reports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="new", nullable=False),
        sa.Column("source", sa.String(length=30), server_default="citizen", nullable=False),
        sa.Column(
            "location",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                spatial_index=False,
            ),
            nullable=False,
        ),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("image_path", sa.Text(), nullable=True),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_reports_status", "reports", ["status"])
    op.create_index("idx_reports_category", "reports", ["category"])
    op.create_index("idx_reports_created_at", "reports", [sa.text("created_at DESC")])
    op.create_index(
        "idx_reports_location",
        "reports",
        ["location"],
        postgresql_using="gist",
    )

    op.create_table(
        "report_workflow_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_status", sa.String(length=30), nullable=True),
        sa.Column("to_status", sa.String(length=30), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("actor_type", sa.String(length=30), nullable=False),
        sa.Column("actor_label", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_workflow_report_id",
        "report_workflow_events",
        ["report_id", "created_at"],
    )

    op.create_table(
        "audit_runs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "municipality",
            sa.String(length=200),
            server_default="Prishtina",
            nullable=False,
        ),
        sa.Column("route_name", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), server_default="queued", nullable=False),
        sa.Column("frames_total", sa.Integer(), server_default="0", nullable=False),
        sa.Column("frames_done", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_runs_status", "audit_runs", ["status"])

    op.create_table(
        "audit_suggestions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("audit_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.String(length=40),
            server_default="pending_review",
            nullable=False,
        ),
        sa.Column(
            "location",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                spatial_index=False,
            ),
            nullable=False,
        ),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("model_name", sa.Text(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("image_attribution", sa.Text(), nullable=True),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("heading", sa.Integer(), nullable=True),
        sa.Column("pitch", sa.Integer(), nullable=True),
        sa.Column("converted_report_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewer_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["audit_run_id"], ["audit_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["converted_report_id"], ["reports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_suggestions_run_id",
        "audit_suggestions",
        ["audit_run_id", "created_at"],
    )
    op.create_index("idx_suggestions_status", "audit_suggestions", ["status"])
    op.create_index(
        "idx_suggestions_location",
        "audit_suggestions",
        ["location"],
        postgresql_using="gist",
    )


def downgrade() -> None:
    op.drop_index("idx_suggestions_location", table_name="audit_suggestions")
    op.drop_index("idx_suggestions_status", table_name="audit_suggestions")
    op.drop_index("idx_suggestions_run_id", table_name="audit_suggestions")
    op.drop_table("audit_suggestions")

    op.drop_index("idx_audit_runs_status", table_name="audit_runs")
    op.drop_table("audit_runs")

    op.drop_index("idx_workflow_report_id", table_name="report_workflow_events")
    op.drop_table("report_workflow_events")

    op.drop_index("idx_reports_location", table_name="reports")
    op.drop_index("idx_reports_created_at", table_name="reports")
    op.drop_index("idx_reports_category", table_name="reports")
    op.drop_index("idx_reports_status", table_name="reports")
    op.drop_table("reports")
