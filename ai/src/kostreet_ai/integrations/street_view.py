from __future__ import annotations

from dataclasses import dataclass

import httpx

METADATA_URL = "https://maps.googleapis.com/maps/api/streetview/metadata"
SNAP_RADII_METERS = (50, 100, 200, 500)
NO_IMAGERY_MAX_BYTES = 20_000


@dataclass(frozen=True)
class StreetViewFrameRequest:
    latitude: float
    longitude: float
    heading: int
    pitch: int = 0


@dataclass(frozen=True)
class StreetViewFrame:
    latitude: float
    longitude: float
    heading: int
    pitch: int
    content_type: str
    data: bytes
    snapped: bool = False


class GoogleStreetViewClient:
    """Fetch live Google Street View Static API frames. Images are not persisted by this client."""

    base_url = "https://maps.googleapis.com/maps/api/streetview"

    def __init__(self, api_key: str, size: int = 640) -> None:
        self.api_key = api_key
        self.size = size

    def fetch_frame(self, request: StreetViewFrameRequest) -> StreetViewFrame:
        snapped_lat, snapped_lng, was_snapped = self._resolve_location(request.latitude, request.longitude)
        response = httpx.get(
            self.base_url,
            params=self._build_params(snapped_lat, snapped_lng, request.heading, request.pitch),
            timeout=30.0,
        )
        response.raise_for_status()
        return StreetViewFrame(
            latitude=snapped_lat,
            longitude=snapped_lng,
            heading=request.heading,
            pitch=request.pitch,
            content_type=response.headers.get("content-type", "image/jpeg"),
            data=response.content,
            snapped=was_snapped,
        )

    def _resolve_location(
        self,
        latitude: float,
        longitude: float,
    ) -> tuple[float, float, bool]:
        snapped = snap_to_nearest_panorama(self.api_key, latitude, longitude)
        if snapped is None:
            return latitude, longitude, False
        return snapped[0], snapped[1], True

    def _build_params(
        self,
        latitude: float,
        longitude: float,
        heading: int,
        pitch: int,
    ) -> dict[str, str | int]:
        return {
            "size": f"{self.size}x{self.size}",
            "location": f"{latitude},{longitude}",
            "heading": heading,
            "pitch": pitch,
            "key": self.api_key,
        }


def snap_to_nearest_panorama(
    api_key: str,
    latitude: float,
    longitude: float,
) -> tuple[float, float] | None:
    for radius in SNAP_RADII_METERS:
        response = httpx.get(
            METADATA_URL,
            params={
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "key": api_key,
            },
            timeout=20.0,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "OK":
            continue

        location = data.get("location")
        if not isinstance(location, dict):
            continue

        return float(location["lat"]), float(location["lng"])

    return None


def is_no_imagery_placeholder(image_bytes: bytes) -> bool:
    """Google returns a tiny gray JPEG when no panorama exists at the location."""
    return len(image_bytes) < NO_IMAGERY_MAX_BYTES
