from pathlib import Path
from typing import Protocol

from PIL import Image

from kostreet_ai.detection.schemas import DetectionResult
from kostreet_ai.preprocessing.image import load_rgb_image


class VisionModel(Protocol):
    def analyze(self, image: Image.Image) -> list[DetectionResult]: ...


class InferenceEngine:
    def __init__(self, model: VisionModel) -> None:
        self.model = model

    def analyze_image(self, image_path: str | Path) -> list[DetectionResult]:
        image = load_rgb_image(image_path)
        return self.model.analyze(image)

