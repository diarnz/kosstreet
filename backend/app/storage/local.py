import uuid
from pathlib import Path

from fastapi import UploadFile


class LocalFileStorage:
    def __init__(self, upload_dir: str) -> None:
        self.base_path = Path(upload_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile) -> str:
        suffix = Path(file.filename or "upload").suffix.lower() or ".jpg"
        relative = f"{uuid.uuid4()}{suffix}"
        dest = self.base_path / relative
        dest.parent.mkdir(parents=True, exist_ok=True)

        contents = await file.read()
        dest.write_bytes(contents)
        return relative

    def url_for(self, path: str) -> str:
        return f"/uploads/{path}"
