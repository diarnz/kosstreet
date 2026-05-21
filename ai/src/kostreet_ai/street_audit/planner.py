from dataclasses import dataclass


@dataclass(frozen=True)
class AuditFrame:
    latitude: float
    longitude: float
    heading: int
    pitch: int


def build_heading_plan(
    latitude: float,
    longitude: float,
    headings: tuple[int, ...] = (0, 60, 120, 180, 240, 300),
    pitches: tuple[int, ...] = (-10, 0),
) -> list[AuditFrame]:
    return [
        AuditFrame(latitude=latitude, longitude=longitude, heading=heading, pitch=pitch)
        for heading in headings
        for pitch in pitches
    ]

