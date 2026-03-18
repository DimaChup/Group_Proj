# gps_utils.py — Shared GPS math utilities
# Pure math functions with NO dependencies on mavlink, vision, or config objects.
# All parameters are explicit.

import math

R_EARTH = 6378137.0  # WGS-84 Earth radius in meters


def gps_distance(lat1, lon1, lat2, lon2):
    """Haversine distance in meters between two GPS coordinates.

    Uses the full haversine formula (accurate at all distances).
    Copied from pi_flight.py _gps_distance().

    Args:
        lat1, lon1: First point (degrees).
        lat2, lon2: Second point (degrees).

    Returns:
        Distance in meters.
    """
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) ** 2)
    return R_EARTH * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def calculate_target_from_pixels(u, v, drone_alt, drone_yaw, drone_lat, drone_lon,
                                  image_w, image_h, sensor_width_mm, focal_length_mm):
    """Convert a pixel detection (u, v) to an estimated GPS position.

    Projects camera-frame pixel offsets through the drone's altitude and yaw
    to produce a world-frame GPS coordinate. Copied from main.py
    calculate_target_gps().

    Args:
        u, v: Detection centre in pixels (image coordinates).
        drone_alt: Drone altitude in meters (AGL).
        drone_yaw: Drone heading in radians (0 = North, CW positive).
        drone_lat, drone_lon: Drone GPS position (degrees).
        image_w, image_h: Image dimensions in pixels.
        sensor_width_mm: Camera sensor physical width in mm.
        focal_length_mm: Camera focal length in mm.

    Returns:
        (est_lat, est_lon) — estimated target GPS position in degrees.
    """
    Cx = image_w / 2
    Cy = image_h / 2

    # Ground sample distance (meters per pixel at current altitude)
    gsd_m = (sensor_width_mm * drone_alt) / (focal_length_mm * image_w)

    # Pixel offsets from image centre
    delta_x_px = u - Cx
    delta_y_px = v - Cy

    # Camera-frame offsets (forward/right in meters)
    fwd_m = -delta_y_px * gsd_m
    right_m = delta_x_px * gsd_m

    # Rotate by yaw to get North/East offsets
    offset_n = fwd_m * math.cos(drone_yaw) - right_m * math.sin(drone_yaw)
    offset_e = fwd_m * math.sin(drone_yaw) + right_m * math.cos(drone_yaw)

    # Convert metre offsets to lat/lon deltas
    dLat = (offset_n / R_EARTH) * (180 / math.pi)
    dLon = (offset_e / (R_EARTH * math.cos(math.radians(drone_lat)))) * (180 / math.pi)

    est_lat = drone_lat + dLat
    est_lon = drone_lon + dLon
    return est_lat, est_lon


def offset_gps_by_distance(lat, lon, north_m, east_m):
    """Offset a GPS position by a given North/East displacement in meters.

    Uses the same R_EARTH projection as calculate_target_from_pixels().

    Args:
        lat, lon: Starting GPS position (degrees).
        north_m: Northward offset in meters (positive = north).
        east_m: Eastward offset in meters (positive = east).

    Returns:
        (new_lat, new_lon) in degrees.
    """
    dLat = (north_m / R_EARTH) * (180 / math.pi)
    dLon = (east_m / (R_EARTH * math.cos(math.radians(lat)))) * (180 / math.pi)
    return lat + dLat, lon + dLon


def landing_offset_7_5m(target_lat, target_lon, direction):
    """Calculate a landing point 7.5 m away from the target in the given direction.

    Copied from main.py calculate_landing_spot().

    Args:
        target_lat, target_lon: Target GPS position (degrees).
        direction: One of 'n', 's', 'e', 'w' (case-insensitive).

    Returns:
        (landing_lat, landing_lon) in degrees.
    """
    offset_dist = 7.5  # meters
    dLat = 0.0
    dLon = 0.0

    d = direction.lower()
    if d == 'n':
        dLat = (offset_dist / R_EARTH) * (180 / math.pi)
    elif d == 's':
        dLat = -(offset_dist / R_EARTH) * (180 / math.pi)
    elif d == 'e':
        dLon = (offset_dist / (R_EARTH * math.cos(math.radians(target_lat)))) * (180 / math.pi)
    elif d == 'w':
        dLon = -(offset_dist / (R_EARTH * math.cos(math.radians(target_lat)))) * (180 / math.pi)

    return target_lat + dLat, target_lon + dLon
