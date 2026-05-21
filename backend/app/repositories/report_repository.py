from app.schemas.report import ReportCreate, ReportRead


class ReportRepository:
    def __init__(self) -> None:
        self._reports: list[ReportRead] = []

    def list(self) -> list[ReportRead]:
        return self._reports

    def create(self, payload: ReportCreate) -> ReportRead:
        report = ReportRead(**payload.model_dump())
        self._reports.append(report)
        return report

