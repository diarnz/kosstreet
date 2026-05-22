from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt

from kostreet_ai.schemas import FramePlan


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in meters between two (lat, lng) points."""
    R = 6_371_000
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lam = radians(lon2 - lon1)
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lam / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def build_heading_plan(
    latitude: float,
    longitude: float,
    headings: tuple[int, ...] | list[int] = (0, 60, 120, 180, 240, 300),
    pitches: tuple[int, ...] | list[int] = (-10, 0),
) -> list[FramePlan]:
    """
    Return the cartesian product of headings × pitches as a flat list of
    FramePlan objects at the given location.

    Outer loop: headings. Inner loop: pitches.
    Example: headings=(0, 90), pitches=(-10, 0) →
        [FramePlan(0, -10), FramePlan(0, 0), FramePlan(90, -10), FramePlan(90, 0)]
    """
    return [
        FramePlan(latitude=latitude, longitude=longitude, heading=h, pitch=p)
        for h in headings
        for p in pitches
    ]


def interpolate_route_points(
    waypoints: list[tuple[float, float]],
    step_meters: float = 30.0,
) -> list[tuple[float, float]]:
    """
    Walk the polyline defined by waypoints and place a new point every
    step_meters along each segment using linear interpolation.

    Always includes the first waypoint. Always includes the final waypoint.
    Remainder distance from one segment carries forward to the next so
    spacing stays consistent across segment boundaries.
    """
    if not waypoints:
        return []
    if len(waypoints) == 1:
        return list(waypoints)

    result: list[tuple[float, float]] = [waypoints[0]]
    remainder = 0.0

    for i in range(len(waypoints) - 1):
        a_lat, a_lng = waypoints[i]
        b_lat, b_lng = waypoints[i + 1]
        segment_len = haversine_meters(a_lat, a_lng, b_lat, b_lng)

        if segment_len == 0:
            continue

        walked = remainder
        while walked + step_meters <= segment_len:
            walked += step_meters
            t = walked / segment_len
            new_lat = a_lat + t * (b_lat - a_lat)
            new_lng = a_lng + t * (b_lng - a_lng)
            result.append((new_lat, new_lng))

        remainder = segment_len - walked

    last = waypoints[-1]
    if result[-1] != last:
        result.append(last)

    return result


def build_audit_scan_plan(
    waypoints: list[tuple[float, float]],
    step_meters: float = 30.0,
    headings: list[int] | tuple[int, ...] = (0, 60, 120, 180, 240, 300),
    pitches: list[int] | tuple[int, ...] = (-10, 0),
) -> list[FramePlan]:
    """
    Full scan plan for a street route.

    Interpolates scan points every step_meters along the route, then
    generates a heading/pitch frame plan at every scan point.
    Returns a flat list of all FramePlan objects for the entire route.
    """
    scan_points = interpolate_route_points(waypoints, step_meters)
    frames: list[FramePlan] = []
    for lat, lng in scan_points:
        frames.extend(build_heading_plan(lat, lng, headings, pitches))
    return frames
