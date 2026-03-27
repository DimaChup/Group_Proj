"""Shared GPS math utilities.

Pure math functions with NO dependencies on mavlink, vision, or config objects.
All parameters are explicit. Uses the WGS-84 Earth radius for all projections.
"""

import math

R_EARTH = 6378137.0  # WGS-84 semi-major axis (equatorial radius) in metres


def gps_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute the great-circle distance between two GPS points using the Haversine formula.

    Formula:
        a = sin(dLat/2)^2 + cos(lat1) * cos(lat2) * sin(dLon/2)^2
        d = 2 * R * atan2(sqrt(a), sqrt(1-a))

    Accurate at all distances (unlike the flat-Earth approximation).

    Parameters
    ----------
    lat1, lon1 : float
        First point in decimal degrees.
    lat2, lon2 : float
        Second point in decimal degrees.

    Returns
    -------
    float
        Distance in metres.
    """
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(d_lon / 2) ** 2)
    return R_EARTH * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def calculate_target_from_pixels(
    u: float,
    v: float,
    drone_alt: float,
    drone_yaw: float,
    drone_lat: float,
    drone_lon: float,
    image_w: int,
    image_h: int,
    sensor_width_mm: float,
    focal_length_mm: float,
) -> tuple[float, float]:
    """Project a pixel detection to an estimated GPS position on the ground.

    Steps:
        1. Compute ground sample distance (GSD):
               GSD = (sensor_width_mm * altitude) / (focal_length_mm * image_w)
           This gives metres-per-pixel at the current altitude.
        2. Convert pixel offset from image centre to camera-frame metres
           (forward = -delta_y, right = +delta_x).
        3. Rotate camera-frame offsets by drone yaw to obtain North/East offsets:
               offset_n = fwd * cos(yaw) - right * sin(yaw)
               offset_e = fwd * sin(yaw) + right * cos(yaw)
        4. Convert North/East metre offsets to lat/lon deltas using the
           small-angle spherical projection:
               dLat = offset_n / R_EARTH  (in radians)
               dLon = offset_e / (R_EARTH * cos(lat))  (in radians)

    Parameters
    ----------
    u, v : float
        Detection centre in pixels (image coordinates, origin top-left).
    drone_alt : float
        Drone altitude in metres above ground level (AGL).
    drone_yaw : float
        Drone heading in radians (0 = North, positive clockwise).
    drone_lat, drone_lon : float
        Drone GPS position in decimal degrees.
    image_w, image_h : int
        Image dimensions in pixels.
    sensor_width_mm : float
        Physical sensor width in millimetres.
    focal_length_mm : float
        Camera focal length in millimetres.

    Returns
    -------
    tuple[float, float]
        (est_lat, est_lon) -- estimated target GPS position in decimal degrees.
    """
    cx = image_w / 2
    cy = image_h / 2

    # Ground sample distance: metres per pixel at current altitude
    gsd_m = (sensor_width_mm * drone_alt) / (focal_length_mm * image_w)

    # Pixel offsets from image centre
    delta_x_px = u - cx
    delta_y_px = v - cy

    # Camera-frame offsets (forward = up in image = -delta_y)
    fwd_m = -delta_y_px * gsd_m
    right_m = delta_x_px * gsd_m

    # Rotate by yaw into North/East frame
    offset_n = fwd_m * math.cos(drone_yaw) - right_m * math.sin(drone_yaw)
    offset_e = fwd_m * math.sin(drone_yaw) + right_m * math.cos(drone_yaw)

    # Spherical projection: metre offsets to degree deltas
    d_lat = (offset_n / R_EARTH) * (180 / math.pi)
    d_lon = (offset_e / (R_EARTH * math.cos(math.radians(drone_lat)))) * (180 / math.pi)

    return drone_lat + d_lat, drone_lon + d_lon


def offset_gps_by_distance(
    lat: float, lon: float, north_m: float, east_m: float
) -> tuple[float, float]:
    """Offset a GPS position by a North/East displacement in metres.

    Uses the small-angle spherical projection:
        dLat = north_m / R_EARTH           (radians, then converted to degrees)
        dLon = east_m / (R_EARTH * cos(lat))  (radians, then converted to degrees)

    Parameters
    ----------
    lat, lon : float
        Starting GPS position in decimal degrees.
    north_m : float
        Northward offset in metres (positive = north, negative = south).
    east_m : float
        Eastward offset in metres (positive = east, negative = west).

    Returns
    -------
    tuple[float, float]
        (new_lat, new_lon) in decimal degrees.
    """
    d_lat = (north_m / R_EARTH) * (180 / math.pi)
    d_lon = (east_m / (R_EARTH * math.cos(math.radians(lat)))) * (180 / math.pi)
    return lat + d_lat, lon + d_lon


def landing_offset_7_5m(
    target_lat: float, target_lon: float, direction: str
) -> tuple[float, float]:
    """Compute a landing point 7.5 m away from a target in a cardinal direction.

    Uses the same spherical projection as offset_gps_by_distance().

    Parameters
    ----------
    target_lat, target_lon : float
        Target GPS position in decimal degrees.
    direction : str
        Cardinal direction: 'n', 's', 'e', or 'w' (case-insensitive).

    Returns
    -------
    tuple[float, float]
        (landing_lat, landing_lon) in decimal degrees.
    """
    offset_dist = 7.5  # metres
    d_lat = 0.0
    d_lon = 0.0

    d = direction.lower()
    if d == 'n':
        d_lat = (offset_dist / R_EARTH) * (180 / math.pi)
    elif d == 's':
        d_lat = -(offset_dist / R_EARTH) * (180 / math.pi)
    elif d == 'e':
        d_lon = (offset_dist / (R_EARTH * math.cos(math.radians(target_lat)))) * (180 / math.pi)
    elif d == 'w':
        d_lon = -(offset_dist / (R_EARTH * math.cos(math.radians(target_lat)))) * (180 / math.pi)

    return target_lat + d_lat, target_lon + d_lon
