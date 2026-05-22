from dataclasses import dataclass
import math
from typing import Protocol

import httpx

METADATA_URL = "https://maps.googleapis.com/maps/api/streetview/metadata"
SNAP_RADII_METERS = (50, 100, 200, 500)
NO_IMAGERY_MAX_BYTES = 20_000


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

    def _build_params(self, request: StreetImageryFrameRequest) -> dict[str, str | int]:
        return {
            "size": f"{self.size}x{self.size}",
            "location": f"{request.latitude},{request.longitude}",
            "heading": request.heading,
            "pitch": request.pitch,
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
            timeout=20,
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
    return len(image_bytes) < NO_IMAGERY_MAX_BYTES


def expand_point_to_corridor(
    api_key: str,
    latitude: float,
    longitude: float,
    *,
    max_waypoints: int = 10,
    spacing_meters: float = 35,
) -> list[tuple[float, float]]:
    start = snap_to_nearest_panorama(api_key, latitude, longitude)
    if start is None:
        raise ValueError(f"No Street View coverage near {latitude}, {longitude}")

    waypoints: list[tuple[float, float]] = [start]
    seen = {_waypoint_key(start)}

    lat_step = spacing_meters / 111_320
    lng_step = spacing_meters / (111_320 * max(math.cos(math.radians(start[0])), 0.2))

    for step in range(1, max_waypoints):
        for lat_delta, lng_delta in (
            (step * lat_step, 0.0),
            (-step * lat_step, 0.0),
            (0.0, step * lng_step),
            (0.0, -step * lng_step),
        ):
            snapped = snap_to_nearest_panorama(
                api_key,
                start[0] + lat_delta,
                start[1] + lng_delta,
            )
            if snapped is None:
                continue

            key = _waypoint_key(snapped)
            if key in seen:
                continue

            seen.add(key)
            waypoints.append(snapped)
            if len(waypoints) >= max_waypoints:
                return waypoints

    return waypoints


def _waypoint_key(point: tuple[float, float]) -> tuple[float, float]:
    return (round(point[0], 5), round(point[1], 5))
