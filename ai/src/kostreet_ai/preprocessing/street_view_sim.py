from __future__ import annotations

import io

from PIL import Image, ImageFilter

DEFAULT_SIM_WIDTH_PX = 640
DEFAULT_JPEG_QUALITY = 60
DEFAULT_BLUR_RADIUS = 0.6


def simulate_street_view_frame(
    image_bytes: bytes,
    *,
    target_width_px: int = DEFAULT_SIM_WIDTH_PX,
    jpeg_quality: int = DEFAULT_JPEG_QUALITY,
    blur_radius: float = DEFAULT_BLUR_RADIUS,
) -> bytes:
    """
    Approximate Google Street View compression artifacts using Pillow only.

    Pipeline: RGB convert → downscale width → mild blur → JPEG recompress.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        rgb = img.convert("RGB")
        if rgb.width > target_width_px:
            scale = target_width_px / rgb.width
            target_height = max(1, int(rgb.height * scale))
            rgb = rgb.resize((target_width_px, target_height), Image.LANCZOS)

        if blur_radius > 0:
            rgb = rgb.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        buffer = io.BytesIO()
        rgb.save(buffer, format="JPEG", quality=jpeg_quality, optimize=True)
        return buffer.getvalue()
