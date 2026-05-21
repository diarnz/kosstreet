from app.repositories.audit_repository import AuditRunRepository
from app.schemas.audit import AuditRunCreate, AuditRunRead


class AuditService:
    def __init__(self, repository: AuditRunRepository) -> None:
        self.repository = repository

    def list_audit_runs(self) -> list[AuditRunRead]:
        return self.repository.list()

    def create_audit_run(self, payload: AuditRunCreate) -> AuditRunRead:
        return self.repository.create(payload)


audit_service = AuditService(repository=AuditRunRepository())

