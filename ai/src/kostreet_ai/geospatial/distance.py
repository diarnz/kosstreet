from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_METERS = 6_371_000


def haversine_distance_meters(
    first_latitude: float,
    first_longitude: float,
    second_latitude: float,
    second_longitude: float,
) -> float:
    first_latitude_rad = radians(first_latitude)
    second_latitude_rad = radians(second_latitude)
    latitude_delta = radians(second_latitude - first_latitude)
    longitude_delta = radians(second_longitude - first_longitude)

    a = (
        sin(latitude_delta / 2) ** 2
        + cos(first_latitude_rad) * cos(second_latitude_rad) * sin(longitude_delta / 2) ** 2
    )
    return 2 * EARTH_RADIUS_METERS * asin(sqrt(a))

