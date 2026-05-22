import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AuditRunStatus, AuditSuggestionStatus, AuditScanSource


class AuditRun(Base):
    __tablename__ = "audit_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    municipality: Mapped[str] = mapped_column(
        String(200), nullable=False, default="Prishtina"
    )
    route_name: Mapped[str] = mapped_column(String(200), nullable=False)
    scan_latitude: Mapped[float | None] = mapped_column(Float)
    scan_longitude: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=AuditRunStatus.queued
    )
    frames_total: Mapped[int] = mapped_column(Integer, default=0)
    frames_done: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    suggestions: Mapped[list["AuditSuggestion"]] = relationship(
        "AuditSuggestion",
        back_populates="audit_run",
        cascade="all, delete-orphan",
        order_by="AuditSuggestion.created_at",
    )
    frames: Mapped[list["AuditFrame"]] = relationship(
        "AuditFrame",
        back_populates="audit_run",
        cascade="all, delete-orphan",
        order_by="AuditFrame.frame_index",
    )


class AuditSuggestion(Base):
    __tablename__ = "audit_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    audit_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audit_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(40), nullable=False, default=AuditSuggestionStatus.pending_review
    )
    location: Mapped[object] = mapped_column(
        Geography("POINT", srid=4326), nullable=False
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)
    model_name: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    image_attribution: Mapped[str | None] = mapped_column(Text)
    department: Mapped[str | None] = mapped_column(String(100))
    heading: Mapped[int | None] = mapped_column(Integer)
    pitch: Mapped[int | None] = mapped_column(Integer)
    frame_index: Mapped[int | None] = mapped_column(Integer)
    detection_regions: Mapped[list[dict[str, float]] | None] = mapped_column(JSONB)
    converted_report_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reports.id"), nullable=True
    )
    reviewer_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    audit_run: Mapped["AuditRun"] = relationship("AuditRun", back_populates="suggestions")
    frame: Mapped["AuditFrame | None"] = relationship(
        "AuditFrame",
        back_populates="suggestion",
        uselist=False,
    )


class AuditFrame(Base):
    __tablename__ = "audit_frames"
    __table_args__ = (
        UniqueConstraint("audit_run_id", "frame_index", name="uq_audit_frames_run_index"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    audit_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audit_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    frame_index: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    heading: Mapped[int] = mapped_column(Integer, nullable=False)
    pitch: Mapped[int] = mapped_column(Integer, default=0)
    is_civic_issue: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[str | None] = mapped_column(String(50))
    confidence: Mapped[float | None] = mapped_column(Float)
    severity: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    detection_regions: Mapped[list[dict[str, float]] | None] = mapped_column(JSONB)
    scan_source: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AuditScanSource.pipeline
    )
    model_name: Mapped[str | None] = mapped_column(Text)
    suggestion_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audit_suggestions.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    audit_run: Mapped["AuditRun"] = relationship("AuditRun", back_populates="frames")
    suggestion: Mapped["AuditSuggestion | None"] = relationship(
        "AuditSuggestion",
        back_populates="frame",
    )
