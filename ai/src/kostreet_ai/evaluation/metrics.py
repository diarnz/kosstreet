from kostreet_ai.detection.schemas import DetectionResult


def confidence_summary(detections: list[DetectionResult]) -> dict[str, float]:
    if not detections:
        return {"count": 0.0, "average_confidence": 0.0}

    average_confidence = sum(detection.confidence for detection in detections) / len(detections)
    return {"count": float(len(detections)), "average_confidence": average_confidence}

