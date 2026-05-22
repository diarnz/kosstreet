from __future__ import annotations

import base64
import io

import pytest
from PIL import Image

from kostreet_ai.preprocessing.image import (
    decode_base64_to_bytes,
    encode_image_to_base64,
    validate_image,
)


def _make_jpeg(width: int = 100, height: int = 100, color: tuple = (200, 50, 50)) -> bytes:
    """Build a minimal in-memory JPEG using Pillow."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_validate_image_returns_true_for_valid_jpeg() -> None:
    assert validate_image(_make_jpeg()) is True


def test_validate_image_returns_false_for_empty_bytes() -> None:
    assert validate_image(b"") is False


def test_validate_image_returns_false_for_garbage_bytes() -> None:
    assert validate_image(b"this is not an image") is False


def test_encode_image_to_base64_returns_non_empty_string() -> None:
    result = encode_image_to_base64(_make_jpeg(200, 200))
    assert isinstance(result, str)
    assert len(result) > 0


def test_encode_image_to_base64_is_valid_base64() -> None:
    result = encode_image_to_base64(_make_jpeg(200, 200))
    decoded = base64.b64decode(result)
    assert len(decoded) > 0


def test_encode_image_resizes_to_max_size() -> None:
    large_jpeg = _make_jpeg(2000, 2000)
    result = encode_image_to_base64(large_jpeg, max_size_px=64)
    decoded_bytes = base64.b64decode(result)
    img = Image.open(io.BytesIO(decoded_bytes))
    assert img.width <= 64
    assert img.height <= 64


def test_decode_base64_roundtrip() -> None:
    original = _make_jpeg(100, 100)
    b64 = encode_image_to_base64(original)
    recovered = decode_base64_to_bytes(b64)
    assert validate_image(recovered) is True


def test_decode_base64_strips_data_uri_prefix() -> None:
    original = _make_jpeg(100, 100)
    raw_b64 = encode_image_to_base64(original)
    with_prefix = f"data:image/jpeg;base64,{raw_b64}"
    result = decode_base64_to_bytes(with_prefix)
    assert result == decode_base64_to_bytes(raw_b64)
