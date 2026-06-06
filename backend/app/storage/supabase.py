import logging
import mimetypes
import uuid
from pathlib import Path

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)

REPORT_OBJECT_PREFIX = "reports"


class SupabaseStorage:
    def __init__(self, settings: Settings) -> None:
        base_url = settings.resolved_supabase_url
        service_role_key = settings.supabase_service_role_key.strip()
        if not base_url or not service_role_key:
            raise ValueError("Supabase storage requires URL and service role key")

        self.base_url = base_url
        self.service_role_key = service_role_key
        self.bucket = settings.supabase_storage_bucket
        self.local_fallback_path = settings.upload_path

    def save_bytes(self, contents: bytes, *, suffix: str = ".jpg") -> str:
        filename = f"{uuid.uuid4()}{suffix}"
        object_key = self._object_key(filename)
        self._upload(object_key, contents, _content_type_for_suffix(suffix))
        return filename

    def read_bytes(self, path: str) -> tuple[bytes, str]:
        object_key = self._object_key(path)
        response = httpx.get(
            f"{self.base_url}/storage/v1/object/{self.bucket}/{object_key}",
            headers={
                "Authorization": f"Bearer {self.service_role_key}",
                "apikey": self.service_role_key,
            },
            timeout=60,
        )
        if response.status_code == 404:
            local_source = self.local_fallback_path / Path(path).name
            if local_source.is_file():
                suffix = local_source.suffix.lower() or ".jpg"
                return local_source.read_bytes(), _content_type_for_suffix(suffix)
            raise FileNotFoundError(path)
        response.raise_for_status()
        content_type = response.headers.get("content-type", _content_type_for_suffix(Path(path).suffix))
        return response.content, content_type

    def url_for(self, path: str) -> str:
        object_key = self._object_key(path)
        return f"{self.base_url}/storage/v1/object/public/{self.bucket}/{object_key}"

    def upload_local_file(self, filename: str) -> bool:
        source = self.local_fallback_path / filename
        if not source.is_file():
            return False

        object_key = self._object_key(filename)
        if self._object_exists(object_key):
            return True

        contents = source.read_bytes()
        suffix = source.suffix or ".jpg"
        self._upload(object_key, contents, _content_type_for_suffix(suffix))
        logger.info("Migrated local report image %s to Supabase storage", filename)
        return True

    def _object_key(self, path: str) -> str:
        normalized = path.replace("\\", "/").lstrip("/")
        if normalized.startswith(f"{REPORT_OBJECT_PREFIX}/"):
            return normalized
        return f"{REPORT_OBJECT_PREFIX}/{normalized}"

    def _upload(self, object_key: str, contents: bytes, content_type: str) -> None:
        response = httpx.post(
            f"{self.base_url}/storage/v1/object/{self.bucket}/{object_key}",
            content=contents,
            headers={
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            timeout=60,
        )
        if response.status_code not in {200, 201}:
            raise RuntimeError(
                f"Supabase upload failed ({response.status_code}): {response.text[:300]}",
            )

    def _object_exists(self, object_key: str) -> bool:
        response = httpx.head(
            f"{self.base_url}/storage/v1/object/public/{self.bucket}/{object_key}",
            timeout=20,
        )
        return response.status_code == 200


def migrate_local_report_images(storage: SupabaseStorage) -> int:
    upload_dir = storage.local_fallback_path
    if not upload_dir.is_dir():
        return 0

    migrated = 0
    for item in upload_dir.iterdir():
        if item.is_file():
            if storage.upload_local_file(item.name):
                migrated += 1
    return migrated


def _content_type_for_suffix(suffix: str) -> str:
    normalized = suffix if suffix.startswith(".") else f".{suffix}"
    return mimetypes.types_map.get(normalized.lower(), "application/octet-stream")
