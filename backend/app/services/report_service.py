from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportCreate, ReportRead


class ReportService:
    def __init__(self, repository: ReportRepository) -> None:
        self.repository = repository

    def list_reports(self) -> list[ReportRead]:
        return self.repository.list()

    def create_report(self, payload: ReportCreate) -> ReportRead:
        return self.repository.create(payload)


report_service = ReportService(repository=ReportRepository())

