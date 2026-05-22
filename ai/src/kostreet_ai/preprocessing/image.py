from __future__ import annotations

import base64
import io

from PIL import Image, UnidentifiedImageError


def validate_image(image_bytes: bytes) -> bool:
    """Return True if image_bytes is a valid, non-empty image Pillow can open."""
    if not image_bytes:
        return False
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img.verify()
        return True
    except (UnidentifiedImageError, Exception):
        return False


def encode_image_to_base64(image_bytes: bytes, max_size_px: int = 1024) -> str:
    """
    Resize the image so its longest side is at most max_size_px, convert to
    RGB JPEG, and return a base64-encoded string ready for the OpenRouter API.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        img.thumbnail((max_size_px, max_size_px), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


def decode_base64_to_bytes(b64: str) -> bytes:
    """
    Decode a base64 string back to raw bytes.
    Handles optional data URI prefix: data:image/jpeg;base64,<data>
    """
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)


def base64_to_resized_base64(b64: str, max_size_px: int = 1024) -> str:
    """
    Convenience wrapper: decode an incoming base64 string, resize it, and
    return a clean base64 string. This is the function called by API endpoints
    that receive image_base64 from the frontend or backend.
    """
    raw_bytes = decode_base64_to_bytes(b64)
    return encode_image_to_base64(raw_bytes, max_size_px)
