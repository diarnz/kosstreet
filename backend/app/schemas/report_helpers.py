from uuid import UUID

from app.core.config import settings
from app.models.report import Report
from app.schemas.report import DetectionRegion, ReportDetail, ReportSummary


def report_image_proxy_url(report_id: UUID) -> str:
    return f"{settings.api_v1_prefix}/reports/{report_id}/image"


def report_image_url(report: Report) -> str | None:
    if not report.image_path:
        return None
    if report.image_path.startswith(("http://", "https://")):
        return report.image_path
    return report_image_proxy_url(report.id)


def report_detection_regions(report: Report) -> list[DetectionRegion]:
    if not report.detection_regions:
        return []
    return [DetectionRegion.model_validate(region) for region in report.detection_regions]


def report_to_summary(report: Report) -> ReportSummary:
    return ReportSummary.model_validate(
        {
            **ReportSummary.model_validate(report).model_dump(),
            "image_url": report_image_url(report),
            "detection_regions": report_detection_regions(report),
        }
    )


def report_to_detail(report: Report) -> ReportDetail:
    return ReportDetail.model_validate(
        {
            **ReportDetail.model_validate(report).model_dump(),
            "image_url": report_image_url(report),
            "detection_regions": report_detection_regions(report),
        }
    )
