from __future__ import annotations

import io

from PIL import Image

from kostreet_ai.preprocessing.street_view_sim import simulate_street_view_frame


def _make_jpeg_bytes(width: int = 1280, height: int = 720) -> bytes:
    image = Image.new("RGB", (width, height), color=(120, 140, 90))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


def test_simulate_street_view_frame_downscales_width() -> None:
    original = _make_jpeg_bytes(width=1600, height=900)
    simulated = simulate_street_view_frame(original, target_width_px=640)
    with Image.open(io.BytesIO(simulated)) as img:
        assert img.width == 640
        assert img.height < 900


def test_simulate_street_view_frame_returns_jpeg_bytes() -> None:
    simulated = simulate_street_view_frame(_make_jpeg_bytes())
    assert simulated[:2] == b"\xff\xd8"
