from unittest.mock import MagicMock, patch
from uuid import UUID

import httpx

from app.core.config import Settings
from app.schemas.report_helpers import report_image_proxy_url, report_image_url
from app.storage.supabase import SupabaseStorage


def test_report_image_proxy_url_uses_api_prefix() -> None:
    report_id = UUID("df453268-f459-4746-bd3a-fd4f841539a8")
    assert report_image_proxy_url(report_id) == f"/api/v1/reports/{report_id}/image"


def test_report_image_url_returns_proxy_for_stored_paths() -> None:
    report = MagicMock()
    report.id = UUID("df453268-f459-4746-bd3a-fd4f841539a8")
    report.image_path = "abc.jpg"

    url = report_image_url(report)

    assert url == "/api/v1/reports/df453268-f459-4746-bd3a-fd4f841539a8/image"


def test_report_image_url_passes_through_absolute_urls() -> None:
    report = MagicMock()
    report.id = UUID("df453268-f459-4746-bd3a-fd4f841539a8")
    report.image_path = "https://cdn.example.com/photo.jpg"

    assert report_image_url(report) == "https://cdn.example.com/photo.jpg"


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


def test_supabase_read_bytes_uses_authenticated_object_url() -> None:
    storage = SupabaseStorage(
        Settings.model_validate(
            {
                "KOSTREET_SUPABASE_URL": "https://demo.supabase.co",
                "KOSTREET_SUPABASE_SERVICE_ROLE_KEY": "service-key",
                "KOSTREET_SUPABASE_STORAGE_BUCKET": "report-images",
            }
        )
    )
    response = httpx.Response(
        200,
        content=b"jpeg-bytes",
        headers={"content-type": "image/jpeg"},
        request=httpx.Request(
            "GET",
            "https://demo.supabase.co/storage/v1/object/report-images/reports/abc.jpg",
        ),
    )

    with patch("app.storage.supabase.httpx.get", return_value=response) as get:
        payload, content_type = storage.read_bytes("abc.jpg")

    assert payload == b"jpeg-bytes"
    assert content_type == "image/jpeg"
    assert get.call_args.args[0].endswith("/storage/v1/object/report-images/reports/abc.jpg")
