from dataclasses import dataclass
from typing import Protocol

import httpx


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


class GoogleStreetViewClient:
    base_url = "https://maps.googleapis.com/maps/api/streetview"

    def __init__(self, api_key: str, size: int = 640) -> None:
        self.api_key = api_key
        self.size = size

    def fetch_frame(self, request: StreetImageryFrameRequest) -> StreetImageryFrame:
        response = httpx.get(
            self.base_url,
            params=self._build_params(request),
            timeout=30,
        )
        response.raise_for_status()

        return StreetImageryFrame(
            source="google_sv",
            content_type=response.headers.get("content-type", "image/jpeg"),
            data=response.content,
        )

    def build_frame_url(self, request: StreetImageryFrameRequest) -> str:
        query = httpx.QueryParams(self._build_params(request))
        return f"{self.base_url}?{query}"

    def fetch_frame_by_url(self, image_url: str) -> StreetImageryFrame:
        response = httpx.get(image_url, timeout=30)
        response.raise_for_status()
        return StreetImageryFrame(
            source="google_sv",
            content_type=response.headers.get("content-type", "image/jpeg"),
            data=response.content,
        )

    def _build_params(self, request: StreetImageryFrameRequest) -> dict[str, str | int]:
        return {
            "size": f"{self.size}x{self.size}",
            "location": f"{request.latitude},{request.longitude}",
            "heading": request.heading,
            "pitch": request.pitch,
            "key": self.api_key,
        }
