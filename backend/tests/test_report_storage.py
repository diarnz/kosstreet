from unittest.mock import MagicMock, patch

import httpx

from app.core.config import Settings
from app.schemas.report_helpers import report_image_url
from app.storage.supabase import SupabaseStorage


def test_supabase_url_for_builds_public_object_url() -> None:
    storage = SupabaseStorage(
        Settings.model_validate(
            {
                "KOSTREET_SUPABASE_URL": "https://demo.supabase.co",
                "KOSTREET_SUPABASE_SERVICE_ROLE_KEY": "service-key",
                "KOSTREET_SUPABASE_STORAGE_BUCKET": "report-images",
            }
        )
    )

    assert (
        storage.url_for("abc.jpg")
        == "https://demo.supabase.co/storage/v1/object/public/report-images/reports/abc.jpg"
    )


def test_report_image_url_uses_storage_backend() -> None:
    report = MagicMock()
    report.image_path = "abc.jpg"

    with patch("app.schemas.report_helpers.get_file_storage") as get_storage:
        get_storage.return_value.url_for.return_value = (
            "https://demo.supabase.co/storage/v1/object/public/report-images/reports/abc.jpg"
        )
        url = report_image_url(report)

    assert url is not None
    assert url.startswith("https://demo.supabase.co/")


def test_supabase_save_bytes_uploads_object() -> None:
    storage = SupabaseStorage(
        Settings.model_validate(
            {
                "KOSTREET_SUPABASE_URL": "https://demo.supabase.co",
                "KOSTREET_SUPABASE_SERVICE_ROLE_KEY": "service-key",
                "KOSTREET_SUPABASE_STORAGE_BUCKET": "report-images",
            }
        )
    )
    response = httpx.Response(200, request=httpx.Request("POST", "https://demo.supabase.co"))

    with patch("app.storage.supabase.httpx.post", return_value=response) as post:
        filename = storage.save_bytes(b"image-bytes", suffix=".jpg")

    assert filename.endswith(".jpg")
    assert post.call_args.args[0].endswith("/storage/v1/object/report-images/reports/" + filename)
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer service-key"
