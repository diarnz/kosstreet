from fastapi import APIRouter, status

from app.schemas.report import ReportCreate, ReportRead
from app.services.report_service import report_service

router = APIRouter()


@router.get("", response_model=list[ReportRead])
def list_reports() -> list[ReportRead]:
    return report_service.list_reports()


@router.post("", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate) -> ReportRead:
    return report_service.create_report(payload)

