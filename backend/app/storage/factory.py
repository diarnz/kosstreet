from functools import lru_cache

from app.core.config import settings
from app.storage.base import FileStorage
from app.storage.local import LocalFileStorage
from app.storage.supabase import SupabaseStorage


@lru_cache
def get_file_storage() -> FileStorage:
    if settings.supabase_storage_enabled:
        return SupabaseStorage(settings)
    return LocalFileStorage(settings.upload_path)
