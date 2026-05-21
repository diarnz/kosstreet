from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class StreetImageryFrameRequest:
    latitude: float
    longitude: float
    heading: int
    pitch: int = 0


@dataclass(frozen=True)
class StreetImageryFrame:
    source: str
    content_type: str
    data: bytes


class StreetImageryClient(Protocol):
    """Boundary for Google Street View or alternative street-imagery providers."""

    def fetch_frame(self, request: StreetImageryFrameRequest) -> StreetImageryFrame: ...
