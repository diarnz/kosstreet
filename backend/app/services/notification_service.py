from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.audit import AuditRun, AuditSuggestion
from app.models.enums import AuditRunStatus, AuditSuggestionStatus, TicketStatus
from app.models.report import Report, ReportWorkflowEvent
from app.schemas.notification import NotificationRead, NotificationScope

CATEGORY_LABELS = {
    "pothole": "Pothole",
    "garbage": "Garbage",
    "broken_streetlight": "Broken streetlight",
    "blocked_sidewalk": "Blocked sidewalk",
    "damaged_sign": "Damaged sign",
    "other": "Other",
}

STATUS_LABELS = {
    TicketStatus.new: "New",
    TicketStatus.verified: "Verified",
    TicketStatus.assigned: "Assigned",
    TicketStatus.in_progress: "In progress",
    TicketStatus.resolved: "Resolved",
    TicketStatus.rejected: "Rejected",
}

AUDIT_STATUS_LABELS = {
    AuditRunStatus.queued: "Queued",
    AuditRunStatus.running: "Running",
    AuditRunStatus.completed: "Completed",
    AuditRunStatus.failed: "Failed",
}


class NotificationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_notifications(
        self,
        *,
        scope: NotificationScope = "all",
        limit: int = 40,
    ) -> list[NotificationRead]:
        items: list[NotificationRead] = []

        if scope in {"dashboard", "all"}:
            items.extend(await self._dashboard_notifications())

        if scope in {"audit", "all"}:
            items.extend(await self._audit_notifications())

        items.sort(key=lambda item: item.created_at, reverse=True)
        return items[:limit]

    async def _dashboard_notifications(self) -> list[NotificationRead]:
        items: list[NotificationRead] = []

        report_result = await self.db.execute(
            select(Report)
            .where(Report.is_visible.is_(True))
            .order_by(Report.created_at.desc())
            .limit(20)
        )
        for report in report_result.scalars().all():
            category = CATEGORY_LABELS.get(report.category, report.category.replace("_", " ").title())
            source_label = "AI audit" if report.source == "street_audit" else "Citizen"
            items.append(
                NotificationRead(
                    id=f"report:{report.id}",
                    title=f"New {category} report",
                    description=(
                        report.description.strip()
                        if report.description and report.description.strip()
                        else f"{source_label} report submitted and awaiting triage."
                    ),
                    created_at=report.created_at,
                    scope="dashboard",
                    kind="report_created",
                    target_id=str(report.id),
                )
            )

        event_result = await self.db.execute(
            select(ReportWorkflowEvent)
            .options(joinedload(ReportWorkflowEvent.report))
            .join(Report)
            .where(Report.is_visible.is_(True))
            .where(ReportWorkflowEvent.from_status.is_not(None))
            .order_by(ReportWorkflowEvent.created_at.desc())
            .limit(25)
        )
        for event in event_result.scalars().all():
            report = event.report
            category = CATEGORY_LABELS.get(report.category, report.category.replace("_", " ").title())
            to_status = STATUS_LABELS.get(event.to_status, event.to_status.replace("_", " ").title())
            note = event.note.strip() if event.note and event.note.strip() else None
            items.append(
                NotificationRead(
                    id=f"workflow:{event.id}",
                    title=f"{category} moved to {to_status}",
                    description=note or f"Updated by {event.actor_label}.",
                    created_at=event.created_at,
                    scope="dashboard",
                    kind="report_status_changed",
                    target_id=str(report.id),
                )
            )

        return items

    async def _audit_notifications(self) -> list[NotificationRead]:
        items: list[NotificationRead] = []

        run_result = await self.db.execute(
            select(AuditRun)
            .where(AuditRun.is_visible.is_(True))
            .order_by(AuditRun.updated_at.desc())
            .limit(20)
        )
        for run in run_result.scalars().all():
            status_label = AUDIT_STATUS_LABELS.get(run.status, run.status.replace("_", " ").title())
            if run.status == AuditRunStatus.queued:
                title = "Audit scan queued"
                description = f"{run.route_name} in {run.municipality} is waiting to start."
                created_at = run.created_at
                kind = "audit_run_queued"
            elif run.status == AuditRunStatus.running:
                title = "Audit scan running"
                progress = (
                    f"Frame {run.frames_done} of {run.frames_total}"
                    if run.frames_total > 0
                    else "Pipeline active"
                )
                description = f"{run.route_name} · {progress}"
                created_at = run.updated_at
                kind = "audit_run_running"
            elif run.status == AuditRunStatus.completed:
                title = "Audit scan completed"
                description = f"{run.route_name} is ready for AI review."
                created_at = run.updated_at
                kind = "audit_run_completed"
            else:
                title = "Audit scan failed"
                description = f"{run.route_name} could not finish ({status_label})."
                created_at = run.updated_at
                kind = "audit_run_failed"

            items.append(
                NotificationRead(
                    id=f"audit_run:{run.id}:{run.status}",
                    title=title,
                    description=description,
                    created_at=created_at,
                    scope="audit",
                    kind=kind,
                    target_id=str(run.id),
                )
            )

        suggestion_result = await self.db.execute(
            select(AuditSuggestion)
            .options(joinedload(AuditSuggestion.audit_run))
            .join(AuditRun)
            .where(AuditSuggestion.is_visible.is_(True))
            .where(AuditRun.is_visible.is_(True))
            .where(AuditSuggestion.status == AuditSuggestionStatus.pending_review)
            .order_by(AuditSuggestion.created_at.desc())
            .limit(20)
        )
        for suggestion in suggestion_result.scalars().all():
            category = CATEGORY_LABELS.get(
                suggestion.category,
                suggestion.category.replace("_", " ").title(),
            )
            route_name = suggestion.audit_run.route_name
            items.append(
                NotificationRead(
                    id=f"suggestion:{suggestion.id}",
                    title=f"AI detected {category}",
                    description=(
                        suggestion.description.strip()
                        if suggestion.description and suggestion.description.strip()
                        else f"New detection on {route_name} needs review."
                    ),
                    created_at=suggestion.created_at,
                    scope="audit",
                    kind="audit_suggestion_pending",
                    target_id=str(suggestion.id),
                )
            )

        return items
