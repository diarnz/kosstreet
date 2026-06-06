import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import PROJECT_ROOT


def migrate_legacy_upload_dirs(target: Path) -> int:
    """Move files saved under cwd-relative paths into the canonical upload directory."""
    target.mkdir(parents=True, exist_ok=True)
    resolved_target = target.resolve()
    legacy_dirs = [
        PROJECT_ROOT / "backend" / "backend" / "uploads",
        Path.cwd() / "backend" / "uploads",
    ]
    moved = 0
    for legacy_dir in legacy_dirs:
        if not legacy_dir.is_dir() or legacy_dir.resolve() == resolved_target:
            continue
        for item in legacy_dir.iterdir():
            if not item.is_file():
                continue
            dest = target / item.name
            if dest.exists():
                continue
            shutil.move(str(item), str(dest))
            moved += 1
    return moved


class LocalFileStorage:
    def __init__(self, upload_dir: str | Path) -> None:
        self.base_path = Path(upload_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, contents: bytes, *, suffix: str = ".jpg") -> str:
        relative = f"{uuid.uuid4()}{suffix}"
        dest = self.base_path / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(contents)
        return relative

    async def save(self, file: UploadFile) -> str:
        suffix = Path(file.filename or "upload").suffix.lower() or ".jpg"
        contents = await file.read()
        return self.save_bytes(contents, suffix=suffix)

    def url_for(self, path: str) -> str:
        return f"/uploads/{path}"
