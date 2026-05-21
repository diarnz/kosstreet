from dataclasses import dataclass


@dataclass(frozen=True)
class AISettings:
    model_name: str = "google/paligemma-3b-mix-224"
    confidence_threshold: float = 0.55
    duplicate_radius_meters: float = 20.0


settings = AISettings()

