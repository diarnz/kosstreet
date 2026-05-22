from enum import StrEnum


class IssueCategory(StrEnum):
    pothole = "pothole"
    garbage = "garbage"
    broken_streetlight = "broken_streetlight"
    blocked_sidewalk = "blocked_sidewalk"
    damaged_sign = "damaged_sign"
    other = "other"


class TicketStatus(StrEnum):
    new = "new"
    verified = "verified"
    assigned = "assigned"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"


class ReportSource(StrEnum):
    citizen = "citizen"
    street_audit = "street_audit"


class AuditRunStatus(StrEnum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class AuditSuggestionStatus(StrEnum):
    pending_review = "pending_review"
    accepted = "accepted"
    rejected = "rejected"
    needs_manual_review = "needs_manual_review"
    converted_to_report = "converted_to_report"


class AuditSuggestionSeverity(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ActorType(StrEnum):
    municipality = "municipality"
    system = "system"
