from pathlib import Path

from PIL import Image, ImageOps


def load_rgb_image(path: str | Path) -> Image.Image:
    image = Image.open(path)
    image = ImageOps.exif_transpose(image)
    return image.convert("RGB")

