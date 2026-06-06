from app.models.report import Report
from app.schemas.report import DetectionRegion, ReportDetail, ReportSummary


def report_image_url(report: Report) -> str | None:
    if not report.image_path:
        return None
    return f"/uploads/{report.image_path}"


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
