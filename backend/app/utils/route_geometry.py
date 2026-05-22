"""Geometric helpers for route-based street audit scanning."""

from __future__ import annotations

import math
from dataclasses import dataclass


def bearing_degrees(
    latitude_from: float,
    longitude_from: float,
    latitude_to: float,
    longitude_to: float,
) -> int:
    """Return compass heading (0–359) from one point toward another."""
    lat1 = math.radians(latitude_from)
    lat2 = math.radians(latitude_to)
    delta_lon = math.radians(longitude_to - longitude_from)

    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    bearing = math.degrees(math.atan2(x, y))
    return int(round((bearing + 360) % 360))


def heading_along_route(
    waypoints: list[tuple[float, float]],
    index: int,
) -> int:
    """Camera heading for a scan point: toward the next waypoint, or from previous at route end."""
    if len(waypoints) <= 1:
        return 0

    if index < len(waypoints) - 1:
        lat_from, lon_from = waypoints[index]
        lat_to, lon_to = waypoints[index + 1]
    else:
        lat_from, lon_from = waypoints[index - 1]
        lat_to, lon_to = waypoints[index]

    return bearing_degrees(lat_from, lon_from, lat_to, lon_to)


@dataclass(frozen=True)
class ScanFrameSpec:
    index: int
    latitude: float
    longitude: float
    heading: int
    pitch: int = 0


def build_scan_frames(waypoints: list[tuple[float, float]]) -> list[ScanFrameSpec]:
    """One scan frame per waypoint, facing direction of travel."""
    return [
        ScanFrameSpec(
            index=index,
            latitude=latitude,
            longitude=longitude,
            heading=heading_along_route(waypoints, index),
            pitch=0,
        )
        for index, (latitude, longitude) in enumerate(waypoints)
    ]
