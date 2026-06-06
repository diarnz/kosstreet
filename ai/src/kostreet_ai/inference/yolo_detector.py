from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

GARBAGE_CLASS_ID = 0


@dataclass(frozen=True)
class GarbageYoloHit:
    confidence: float
    class_id: int = GARBAGE_CLASS_ID


class GarbageYoloDetector:
    """Lazy-loaded YOLOv8 garbage detector. Optional dependency: ultralytics."""

    def __init__(self, model_path: Path, threshold: float) -> None:
        self.model_path = model_path
        self.threshold = threshold
        self._model = None

    @property
    def is_available(self) -> bool:
        return self.model_path.is_file()

    def _ensure_model(self) -> bool:
        if self._model is not None:
            return True
        if not self.is_available:
            logger.warning("YOLO model not found at %s", self.model_path)
            return False
        try:
            from ultralytics import YOLO

            self._model = YOLO(str(self.model_path))
            return True
        except Exception as exc:
            logger.warning("Failed to load YOLO model: %s", exc)
            return False

    def detect(self, image_bytes: bytes) -> GarbageYoloHit | None:
        """
        Run inference and return the highest-confidence garbage hit above threshold.
        Returns None when the model is unavailable or nothing is detected.
        """
        if not image_bytes or not self._ensure_model():
            return None

        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as handle:
                handle.write(image_bytes)
                temp_path = Path(handle.name)

            results = self._model.predict(
                source=str(temp_path),
                conf=self.threshold,
                verbose=False,
            )
            best_confidence = 0.0
            for result in results:
                if result.boxes is None:
                    continue
                for box in result.boxes:
                    class_id = int(box.cls.item())
                    if class_id != GARBAGE_CLASS_ID:
                        continue
                    confidence = float(box.conf.item())
                    best_confidence = max(best_confidence, confidence)

            if best_confidence < self.threshold:
                return None
            return GarbageYoloHit(confidence=best_confidence)
        except Exception as exc:
            logger.warning("YOLO inference failed: %s", exc)
            return None
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)


def try_create_detector(model_path: Path, threshold: float) -> GarbageYoloDetector | None:
    if not model_path.is_file():
        return None
    return GarbageYoloDetector(model_path=model_path, threshold=threshold)
