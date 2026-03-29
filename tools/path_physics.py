"""
Path Physics Simulation Engine
==============================

Reusable module that simulates a drone flying along a GPS waypoint path with
realistic physics: momentum, NFZ speed limits, energy consumption, and
camera coverage.

No cv2 dependency -- pure computation (math + numpy only).

Usage:
    from tools.path_physics import simulate_path, PathPoint, PathSummary

    result = simulate_path(
        waypoints_gps=[(51.423, -2.670), ...],
        altitude_m=35.0,
        sssi_polygon_gps=config.SSSI_GPS,
        config_params={},   # optional overrides
    )
    print(result.summary)
    for pt in result.points:
        print(pt.time_s, pt.speed_mps, pt.energy_wh)
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np


# ============================================================
#  Constants (defaults -- overridable via config_params)
# ============================================================

EARTH_R = 6_371_000.0  # metres

# Momentum
MAX_ACCEL_MPS2 = 3.0
MAX_DECEL_MPS2 = 3.0

# Energy
HOVER_POWER_W = 150.0
DRAG_COEFF_W = 50.0
DRAG_REF_SPEED_MPS = 5.0

# Camera (defaults from config.py)
SENSOR_WIDTH_MM = 5.02
FOCAL_LENGTH_MM = 5.46
IMAGE_W = 1456
IMAGE_H = 1088

# NFZ speed ramp defaults
NFZ_BUFFER_OUTER_M = 40.0   # distance at which ramp starts
NFZ_BUFFER_INNER_M = 2.0    # distance at which speed reaches zero
NFZ_RAMP_MAX_SPEED_MPS = 3.0  # speed at outer edge of ramp

# Simulation resolution
STEP_DISTANCE_M = 1.0  # sample every ~1 m along the path


# ============================================================
#  Data classes
# ============================================================

@dataclass
class PathPoint:
    """State of the drone at one sample point along the path."""
    lat: float
    lon: float
    x_m: float                # local east (metres from ref)
    y_m: float                # local north (metres from ref)
    speed_mps: float          # actual speed at this point
    target_speed_mps: float   # what the drone *wants* to fly
    dist_to_nfz_m: float     # shortest distance to SSSI boundary
    is_inside_nfz: bool       # True if inside the polygon
    cumulative_time_s: float  # seconds since start
    cumulative_energy_wh: float  # watt-hours since start
    segment_index: int        # which waypoint segment (0-based)
    heading_deg: float        # current heading (0=north, CW)


@dataclass
class PathSummary:
    """Aggregate statistics for the entire simulated path."""
    total_time_s: float
    total_energy_wh: float
    avg_speed_mps: float
    max_speed_mps: float
    total_distance_m: float
    nfz_time_s: float
    nfz_time_pct: float
    nfz_entries: int
    coverage_width_m: float   # camera ground footprint width
    coverage_height_m: float  # camera ground footprint height
    num_waypoints: int
    num_points: int


@dataclass
class SimulationResult:
    """Full output of a path simulation."""
    points: List[PathPoint]
    summary: PathSummary


# ============================================================
#  Coordinate helpers (no cv2, no GeoTransformer)
# ============================================================

def gps_to_local(lat: float, lon: float,
                 ref_lat: float, ref_lon: float) -> Tuple[float, float]:
    """Convert GPS (lat, lon) to local (x_east, y_north) in metres."""
    lat_r = math.radians(ref_lat)
    dy = (lat - ref_lat) * (math.pi / 180.0) * EARTH_R
    dx = (lon - ref_lon) * (math.pi / 180.0) * EARTH_R * math.cos(lat_r)
    return dx, dy


def local_to_gps(x_m: float, y_m: float,
                 ref_lat: float, ref_lon: float) -> Tuple[float, float]:
    """Convert local (x_east, y_north) in metres back to GPS."""
    lat_r = math.radians(ref_lat)
    d_lat = y_m / (EARTH_R * math.pi / 180.0)
    d_lon = x_m / (EARTH_R * math.pi / 180.0 * math.cos(lat_r))
    return ref_lat + d_lat, ref_lon + d_lon


# ============================================================
#  Geometry helpers (pure math, no cv2)
# ============================================================

def _point_to_segment_dist(px, py, ax, ay, bx, by):
    """Shortest distance from point (px,py) to segment (ax,ay)-(bx,by)."""
    dx, dy = bx - ax, by - ay
    len_sq = dx * dx + dy * dy
    if len_sq < 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / len_sq))
    proj_x = ax + t * dx
    proj_y = ay + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def point_to_polygon_dist(px: float, py: float,
                          poly: np.ndarray) -> float:
    """Minimum unsigned distance from point to polygon edges.

    Args:
        poly: Nx2 array of (x, y) vertices in local metres.
    """
    n = len(poly)
    min_d = float("inf")
    for i in range(n):
        j = (i + 1) % n
        d = _point_to_segment_dist(px, py,
                                   poly[i, 0], poly[i, 1],
                                   poly[j, 0], poly[j, 1])
        if d < min_d:
            min_d = d
    return min_d


def point_in_polygon(px: float, py: float,
                     poly: np.ndarray) -> bool:
    """Ray-casting test. poly is Nx2."""
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and \
           (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def nfz_distance(px: float, py: float,
                 nfz_poly: Optional[np.ndarray]) -> Tuple[float, bool]:
    """Compute distance to NFZ boundary and inside/outside status.

    Returns:
        (distance_m, is_inside)
    """
    if nfz_poly is None or len(nfz_poly) < 3:
        return float("inf"), False
    dist = point_to_polygon_dist(px, py, nfz_poly)
    inside = point_in_polygon(px, py, nfz_poly)
    return dist, inside


# ============================================================
#  Speed model
# ============================================================

def compute_target_speed(dist_to_nfz: float, is_inside_nfz: bool,
                         base_speed: float,
                         buffer_outer: float, buffer_inner: float,
                         ramp_max_speed: float) -> float:
    """Compute the target speed at a point, accounting for NFZ proximity.

    Outside the buffer zone: base_speed (from altitude).
    Inside NFZ: 0.0 m/s.
    In the buffer (buffer_inner..buffer_outer): linear ramp from 0 to
    ramp_max_speed, capped at base_speed.
    """
    if is_inside_nfz:
        return 0.0

    if dist_to_nfz >= buffer_outer:
        return base_speed

    if dist_to_nfz <= buffer_inner:
        return 0.0

    # Linear ramp: 0 at buffer_inner, ramp_max_speed at buffer_outer
    ratio = (dist_to_nfz - buffer_inner) / (buffer_outer - buffer_inner)
    ramped = ratio * ramp_max_speed
    return min(ramped, base_speed)


def turn_speed_factor(angle_rad: float) -> float:
    """Speed reduction factor for a turn of given angle (radians).

    0 rad (straight) -> 1.0
    pi rad (180 U-turn) -> 0.0  (must stop)
    """
    # Normalise to [0, pi]
    a = min(abs(angle_rad), math.pi)
    return max(0.0, 1.0 - a / math.pi)


# ============================================================
#  Energy model
# ============================================================

def power_at_speed(speed_mps: float,
                   hover_w: float = HOVER_POWER_W,
                   drag_w: float = DRAG_COEFF_W,
                   drag_ref: float = DRAG_REF_SPEED_MPS) -> float:
    """Total power consumption at a given forward speed.

    P_total = P_hover + P_drag
    P_drag  = drag_w * (speed / drag_ref)^2
    """
    p_drag = drag_w * (speed_mps / drag_ref) ** 2
    return hover_w + p_drag


# ============================================================
#  Camera footprint
# ============================================================

def camera_footprint(altitude_m: float,
                     sensor_w_mm: float = SENSOR_WIDTH_MM,
                     focal_mm: float = FOCAL_LENGTH_MM,
                     img_w: int = IMAGE_W,
                     img_h: int = IMAGE_H) -> Tuple[float, float]:
    """Ground footprint (width_m, height_m) at given altitude."""
    ground_w = (sensor_w_mm * altitude_m) / focal_mm
    ground_h = ground_w * (img_h / img_w)
    return ground_w, ground_h


# ============================================================
#  Main simulation
# ============================================================

def simulate_path(
    waypoints_gps: List[Tuple[float, float]],
    altitude_m: float,
    sssi_polygon_gps: Optional[List[Tuple[float, float]]] = None,
    config_params: Optional[dict] = None,
) -> SimulationResult:
    """Simulate a drone flying along the given GPS waypoint path.

    Produces a list of PathPoint sampled approximately every 1 m along
    the path, with realistic momentum, NFZ speed limits, energy
    consumption, and camera coverage.

    Args:
        waypoints_gps: Ordered list of (lat, lon) waypoints.
        altitude_m: Flight altitude in metres.
        sssi_polygon_gps: Optional SSSI polygon as list of (lat, lon).
            If None, NFZ checks are skipped.
        config_params: Optional dict to override defaults. Keys:
            max_accel, max_decel, hover_power_w, drag_coeff_w,
            drag_ref_speed, sensor_width_mm, focal_length_mm,
            image_w, image_h, nfz_buffer_outer_m, nfz_buffer_inner_m,
            nfz_ramp_max_speed, step_distance_m, speed_for_altitude
            (callable(alt) -> float).

    Returns:
        SimulationResult with .points and .summary.
    """
    if not waypoints_gps or len(waypoints_gps) < 2:
        empty_summary = PathSummary(
            total_time_s=0, total_energy_wh=0, avg_speed_mps=0,
            max_speed_mps=0, total_distance_m=0, nfz_time_s=0,
            nfz_time_pct=0, nfz_entries=0, coverage_width_m=0,
            coverage_height_m=0, num_waypoints=0, num_points=0,
        )
        return SimulationResult(points=[], summary=empty_summary)

    # --- Unpack config overrides ---
    cfg = config_params or {}
    max_accel = cfg.get("max_accel", MAX_ACCEL_MPS2)
    max_decel = cfg.get("max_decel", MAX_DECEL_MPS2)
    hover_w = cfg.get("hover_power_w", HOVER_POWER_W)
    drag_w = cfg.get("drag_coeff_w", DRAG_COEFF_W)
    drag_ref = cfg.get("drag_ref_speed", DRAG_REF_SPEED_MPS)
    sensor_w = cfg.get("sensor_width_mm", SENSOR_WIDTH_MM)
    focal_mm = cfg.get("focal_length_mm", FOCAL_LENGTH_MM)
    img_w = cfg.get("image_w", IMAGE_W)
    img_h = cfg.get("image_h", IMAGE_H)
    buf_outer = cfg.get("nfz_buffer_outer_m", NFZ_BUFFER_OUTER_M)
    buf_inner = cfg.get("nfz_buffer_inner_m", NFZ_BUFFER_INNER_M)
    ramp_max = cfg.get("nfz_ramp_max_speed", NFZ_RAMP_MAX_SPEED_MPS)
    step_m = cfg.get("step_distance_m", STEP_DISTANCE_M)

    # Speed function: either from config_params or default linear interp
    speed_fn = cfg.get("speed_for_altitude", None)
    if speed_fn is not None:
        base_speed = speed_fn(altitude_m)
    else:
        # Default: import-free linear interpolation matching config.py
        alt_low = cfg.get("speed_alt_low", 20.0)
        alt_high = cfg.get("speed_alt_high", 50.0)
        spd_low = cfg.get("speed_at_low", 6.0)
        spd_high = cfg.get("speed_at_high", 10.0)
        if altitude_m <= alt_low:
            base_speed = spd_low
        elif altitude_m >= alt_high:
            base_speed = spd_high
        else:
            ratio = (altitude_m - alt_low) / (alt_high - alt_low)
            base_speed = spd_low + ratio * (spd_high - spd_low)

    # --- Reference point: centroid of waypoints ---
    ref_lat = sum(w[0] for w in waypoints_gps) / len(waypoints_gps)
    ref_lon = sum(w[1] for w in waypoints_gps) / len(waypoints_gps)

    # --- Convert waypoints to local metres ---
    wps_local = [gps_to_local(lat, lon, ref_lat, ref_lon)
                 for lat, lon in waypoints_gps]

    # --- Convert NFZ polygon to local metres ---
    nfz_local = None
    if sssi_polygon_gps and len(sssi_polygon_gps) >= 3:
        nfz_local = np.array([gps_to_local(lat, lon, ref_lat, ref_lon)
                              for lat, lon in sssi_polygon_gps])

    # --- Camera footprint ---
    cov_w, cov_h = camera_footprint(altitude_m, sensor_w, focal_mm, img_w, img_h)

    # --- Pre-compute segment lengths, headings, and turn angles ---
    num_segs = len(wps_local) - 1
    seg_lengths = []
    seg_headings = []  # radians, 0=north CW
    for i in range(num_segs):
        dx = wps_local[i + 1][0] - wps_local[i][0]
        dy = wps_local[i + 1][1] - wps_local[i][1]
        seg_lengths.append(math.hypot(dx, dy))
        seg_headings.append(math.atan2(dx, dy))  # atan2(east, north) = heading

    # Turn angles at each interior waypoint
    turn_angles = []  # len = num_segs - 1
    for i in range(num_segs - 1):
        da = seg_headings[i + 1] - seg_headings[i]
        # Normalise to [-pi, pi]
        da = (da + math.pi) % (2 * math.pi) - math.pi
        turn_angles.append(abs(da))

    # --- Walk the path ---
    points: List[PathPoint] = []
    current_speed = 0.0  # start from rest
    cumulative_time = 0.0
    cumulative_energy_j = 0.0
    total_distance = 0.0
    max_speed = 0.0
    nfz_time = 0.0
    nfz_entries = 0
    was_in_nfz = False

    for seg_i in range(num_segs):
        x0, y0 = wps_local[seg_i]
        x1, y1 = wps_local[seg_i + 1]
        seg_len = seg_lengths[seg_i]
        heading = seg_headings[seg_i]
        heading_deg = math.degrees(heading) % 360

        if seg_len < 0.01:
            continue

        # Unit direction vector
        ux = (x1 - x0) / seg_len
        uy = (y1 - y0) / seg_len

        # How many steps along this segment
        num_steps = max(1, int(seg_len / step_m))
        actual_step = seg_len / num_steps

        # If there is a turn at the END of this segment, we need to
        # decelerate to the turn-limited speed before reaching the waypoint.
        if seg_i < num_segs - 1:
            turn_angle = turn_angles[seg_i]
            turn_factor = turn_speed_factor(turn_angle)
            wp_exit_speed = base_speed * turn_factor
        else:
            wp_exit_speed = 0.0  # stop at end

        # Distance needed to decelerate from current speed to wp_exit_speed
        # v^2 = v0^2 - 2*a*d  =>  d = (v0^2 - v^2) / (2*a)
        remaining_in_seg = seg_len

        for step_i in range(num_steps):
            # Position along segment
            frac = (step_i + 0.5) / num_steps
            px = x0 + frac * seg_len * ux
            py = y0 + frac * seg_len * uy

            # NFZ check
            dist_nfz, in_nfz = nfz_distance(px, py, nfz_local)

            # Track NFZ entries
            if in_nfz and not was_in_nfz:
                nfz_entries += 1
            was_in_nfz = in_nfz

            # Target speed from NFZ proximity
            v_target = compute_target_speed(
                dist_nfz, in_nfz, base_speed,
                buf_outer, buf_inner, ramp_max,
            )

            # Distance remaining to end of segment
            remaining_in_seg = seg_len * (1.0 - frac)

            # Deceleration constraint: can we reach wp_exit_speed in remaining dist?
            # v_exit^2 = v^2 - 2*a*d  =>  v_max = sqrt(v_exit^2 + 2*a*d)
            decel_limit = math.sqrt(
                max(0, wp_exit_speed ** 2 + 2 * max_decel * remaining_in_seg)
            )
            v_target = min(v_target, decel_limit)

            # Apply momentum using kinematics (distance-based, not time-based).
            # v^2 = v0^2 + 2*a*ds  for acceleration
            # v^2 = v0^2 - 2*a*ds  for deceleration
            if v_target > current_speed:
                # Accelerate: v = sqrt(v0^2 + 2*a*ds), capped at target
                new_speed = math.sqrt(current_speed ** 2 + 2 * max_accel * actual_step)
                new_speed = min(new_speed, v_target)
            elif v_target < current_speed:
                # Decelerate: v = sqrt(v0^2 - 2*a*ds), floored at target
                v_sq = current_speed ** 2 - 2 * max_decel * actual_step
                new_speed = math.sqrt(max(v_sq, 0.0))
                new_speed = max(new_speed, v_target)
            else:
                new_speed = current_speed

            # Recalculate dt with averaged speed (trapezoidal)
            avg_speed = max((current_speed + new_speed) / 2.0, 0.05)
            dt = actual_step / avg_speed

            # Energy for this step
            power = power_at_speed(avg_speed, hover_w, drag_w, drag_ref)
            cumulative_energy_j += power * dt
            cumulative_time += dt
            total_distance += actual_step

            current_speed = new_speed
            if current_speed > max_speed:
                max_speed = current_speed

            # NFZ time tracking
            if in_nfz or dist_nfz < buf_inner:
                nfz_time += dt

            # Convert position back to GPS
            pt_lat, pt_lon = local_to_gps(px, py, ref_lat, ref_lon)

            points.append(PathPoint(
                lat=pt_lat,
                lon=pt_lon,
                x_m=px,
                y_m=py,
                speed_mps=current_speed,
                target_speed_mps=v_target,
                dist_to_nfz_m=dist_nfz,
                is_inside_nfz=in_nfz,
                cumulative_time_s=cumulative_time,
                cumulative_energy_wh=cumulative_energy_j / 3600.0,
                segment_index=seg_i,
                heading_deg=heading_deg,
            ))

    # --- Summary ---
    avg_speed = total_distance / cumulative_time if cumulative_time > 0 else 0
    nfz_pct = (nfz_time / cumulative_time * 100) if cumulative_time > 0 else 0

    summary = PathSummary(
        total_time_s=cumulative_time,
        total_energy_wh=cumulative_energy_j / 3600.0,
        avg_speed_mps=avg_speed,
        max_speed_mps=max_speed,
        total_distance_m=total_distance,
        nfz_time_s=nfz_time,
        nfz_time_pct=nfz_pct,
        nfz_entries=nfz_entries,
        coverage_width_m=cov_w,
        coverage_height_m=cov_h,
        num_waypoints=len(waypoints_gps),
        num_points=len(points),
    )

    return SimulationResult(points=points, summary=summary)


# ============================================================
#  Convenience: print summary
# ============================================================

def print_summary(result: SimulationResult, label: str = "") -> None:
    """Print a human-readable summary of the simulation."""
    s = result.summary
    hdr = f"  Path Physics: {label}  " if label else "  Path Physics Summary  "
    print(f"\n{'=' * len(hdr)}")
    print(hdr)
    print(f"{'=' * len(hdr)}")
    print(f"  Waypoints:    {s.num_waypoints}")
    print(f"  Sample pts:   {s.num_points}")
    print(f"  Distance:     {s.total_distance_m:.0f} m")
    print(f"  Total time:   {s.total_time_s:.1f} s  ({s.total_time_s / 60:.1f} min)")
    print(f"  Avg speed:    {s.avg_speed_mps:.2f} m/s")
    print(f"  Max speed:    {s.max_speed_mps:.2f} m/s")
    print(f"  Energy:       {s.total_energy_wh:.1f} Wh")
    print(f"  NFZ time:     {s.nfz_time_s:.1f} s  ({s.nfz_time_pct:.1f}%)")
    print(f"  NFZ entries:  {s.nfz_entries}")
    print(f"  Footprint:    {s.coverage_width_m:.1f} x {s.coverage_height_m:.1f} m")
    print()


# ============================================================
#  Self-test
# ============================================================

if __name__ == "__main__":
    import sys
    import os

    # Add project root for config import
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, PROJECT_ROOT)
    import config

    config.load_kml_zones(os.path.join(PROJECT_ROOT, "flight_plans", "AENGM0074.kml"))

    # Use search area as a simple test path
    test_wps = list(config.SEARCH_AREA_GPS) + [config.SEARCH_AREA_GPS[0]]

    result = simulate_path(
        waypoints_gps=test_wps,
        altitude_m=35.0,
        sssi_polygon_gps=config.SSSI_GPS,
        config_params={"speed_for_altitude": config.speed_for_altitude},
    )
    print_summary(result, "Search area perimeter at 35m")

    # Print first 10 points as a sample
    print("First 10 sample points:")
    print(f"{'#':>4}  {'Speed':>6}  {'Target':>6}  {'NFZ_d':>6}  {'Time':>7}  {'Energy':>7}")
    for i, pt in enumerate(result.points[:10]):
        print(f"{i:4d}  {pt.speed_mps:6.2f}  {pt.target_speed_mps:6.2f}  "
              f"{pt.dist_to_nfz_m:6.1f}  {pt.cumulative_time_s:7.1f}  "
              f"{pt.cumulative_energy_wh:7.3f}")
