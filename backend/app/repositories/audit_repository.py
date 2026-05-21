from app.schemas.audit import AuditRunCreate, AuditRunRead


class AuditRunRepository:
    def __init__(self) -> None:
        self._audit_runs: list[AuditRunRead] = []

    def list(self) -> list[AuditRunRead]:
        return self._audit_runs

    def create(self, payload: AuditRunCreate) -> AuditRunRead:
        audit_run = AuditRunRead(**payload.model_dump())
        self._audit_runs.append(audit_run)
        return audit_run

