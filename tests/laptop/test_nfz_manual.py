#!/usr/bin/env python3
"""
Test NFZ manual-mode velocity clamping WITHOUT SITL.

Replicates the math from:
  - main.py _enforce_geofence()  (toward-vector + max speed computation)
  - state_machine.py _handle_manual_flight()  (body->NED + directional clamp)

Uses actual SSSI_GPS polygon from config.py.
Simulates drone at various positions near the NFZ with different yaw/key combos.
Prints input velocity, clamped velocity, and PASS/FAIL for each test case.
"""

import math
import sys
import os

# ── Add project root so we can import config ─────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import config

# ── Config constants ─────────────────────────────────────────────────────────
SSSI_GPS = config.SSSI_GPS
NFZ_SLOW_ZONE_M = config.NFZ_SLOW_ZONE_M        # 40.0
NFZ_SCALAR_ZERO_M = config.NFZ_SCALAR_ZERO_M    # 2.0
NFZ_ZONE_MAX_SPEED_MPS = config.NFZ_ZONE_MAX_SPEED_MPS  # 3.0
MANUAL_FLY_SPEED_MPS = config.MANUAL_FLY_SPEED_MPS      # 5.0


# ══════════════════════════════════════════════════════════════════════════════
# Math copied from main.py _enforce_geofence (L666-706)
# ══════════════════════════════════════════════════════════════════════════════

def point_in_polygon(lat, lon, poly):
    """Ray-casting point-in-polygon (replaces cv2.pointPolygonTest)."""
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        yi, xi = poly[i]
        yj, xj = poly[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def closest_point_on_segment(lat, lon, p1_lat, p1_lon, p2_lat, p2_lon):
    """Project (lat, lon) onto segment p1-p2, return closest point in metres."""
    cos_lat = math.cos(math.radians(lat))
    e_n = (p2_lat - p1_lat) * 111320
    e_e = (p2_lon - p1_lon) * 111320 * cos_lat
    d_n = (lat - p1_lat) * 111320
    d_e = (lon - p1_lon) * 111320 * cos_lat
    e_len_sq = e_n * e_n + e_e * e_e
    t = max(0.0, min(1.0, (d_n * e_n + d_e * e_e) / e_len_sq)) if e_len_sq > 1e-12 else 0.0
    c_lat = p1_lat + t * (p2_lat - p1_lat)
    c_lon = p1_lon + t * (p2_lon - p1_lon)
    return c_lat, c_lon


def compute_nfz_fields(lat, lon):
    """Replicate _enforce_geofence() — compute toward-vector and max speed.

    Returns:
        (toward_n, toward_e): unit vector pointing toward nearest NFZ edge, or None
        nfz_max_speed: max allowed speed toward NFZ, or None (no limit)
        nfz_dist: distance to NFZ boundary in metres
        is_inside: True if inside NFZ
    """
    poly = SSSI_GPS
    is_inside = point_in_polygon(lat, lon, poly)

    # Find nearest point on boundary
    best_dist_sq = float('inf')
    nfz_lat, nfz_lon = lat, lon
    for i in range(len(poly)):
        p1_lat, p1_lon = poly[i]
        p2_lat, p2_lon = poly[(i + 1) % len(poly)]
        c_lat, c_lon = closest_point_on_segment(lat, lon, p1_lat, p1_lon, p2_lat, p2_lon)
        cos_lat = math.cos(math.radians(lat))
        dsq = ((lat - c_lat) * 111320) ** 2 + ((lon - c_lon) * 111320 * cos_lat) ** 2
        if dsq < best_dist_sq:
            best_dist_sq = dsq
            nfz_lat, nfz_lon = c_lat, c_lon

    nfz_dist = math.sqrt(best_dist_sq)

    # Compute toward-vector and max speed (same logic as main.py L670-706)
    toward_vec = None
    nfz_max_speed = None

    if not is_inside and nfz_dist < NFZ_SLOW_ZONE_M:
        if nfz_dist <= NFZ_SCALAR_ZERO_M:
            nfz_max_speed = 0.3
        else:
            ratio = (nfz_dist - NFZ_SCALAR_ZERO_M) / (NFZ_SLOW_ZONE_M - NFZ_SCALAR_ZERO_M)
            nfz_max_speed = ratio * NFZ_ZONE_MAX_SPEED_MPS

        cos_lat = math.cos(math.radians(lat))
        dx = (nfz_lon - lon) * 111320 * cos_lat  # east component
        dy = (nfz_lat - lat) * 111320              # north component
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0.1:
            toward_vec = (dy / dist, dx / dist)  # (toward_n, toward_e)

    return toward_vec, nfz_max_speed, nfz_dist, is_inside


# ══════════════════════════════════════════════════════════════════════════════
# Math copied from state_machine.py _handle_manual_flight (L852-894)
# ══════════════════════════════════════════════════════════════════════════════

def apply_manual_clamp(key, yaw, toward_vec, nfz_max_speed):
    """Simulate _handle_manual_flight body->NED conversion and NFZ clamping.

    Args:
        key: 'w', 'a', 's', 'd'
        yaw: heading in radians (0 = north, pi/2 = east)
        toward_vec: (toward_n, toward_e) unit vector or None
        nfz_max_speed: max approach speed or None

    Returns:
        (vn_in, ve_in): NED velocity BEFORE clamping
        (vn_out, ve_out): NED velocity AFTER clamping
        clamped: True if clamping was applied
    """
    spd = MANUAL_FLY_SPEED_MPS

    # Body-frame velocity from key
    vf, vr = 0, 0
    if key == 'w':   vf = spd
    elif key == 's': vf = -spd
    elif key == 'a': vr = -spd
    elif key == 'd': vr = spd

    # Body->NED conversion
    vn = vf * math.cos(yaw) - vr * math.sin(yaw)
    ve = vf * math.sin(yaw) + vr * math.cos(yaw)

    vn_in, ve_in = vn, ve

    clamped = False
    if toward_vec is not None and nfz_max_speed is not None and (vf != 0 or vr != 0):
        toward_n, toward_e = toward_vec
        v_toward = vn * toward_n + ve * toward_e
        if v_toward > nfz_max_speed:
            reduction = v_toward - nfz_max_speed
            vn -= toward_n * reduction
            ve -= toward_e * reduction
            clamped = True

    return (vn_in, ve_in), (vn, ve), clamped


# ══════════════════════════════════════════════════════════════════════════════
# Helper: offset a GPS position by metres
# ══════════════════════════════════════════════════════════════════════════════

def offset_gps(lat, lon, north_m, east_m):
    """Move a GPS point by (north, east) metres."""
    new_lat = lat + north_m / 111320
    new_lon = lon + east_m / (111320 * math.cos(math.radians(lat)))
    return new_lat, new_lon


# ══════════════════════════════════════════════════════════════════════════════
# Build test cases
# ══════════════════════════════════════════════════════════════════════════════

def find_reference_point():
    """Find a point on the western edge of the SSSI polygon and offset west from it.
    This gives us a known position where 'east' is toward the NFZ."""
    # Use midpoint of the westernmost edge (vertices 0 and 6 are the western top)
    # The SSSI polygon's western side is roughly vertex 0 to vertex 6 (top-left area)
    # Pick vertex 0 as reference — it's the northwest corner
    ref_lat, ref_lon = SSSI_GPS[0]
    return ref_lat, ref_lon


def make_test_position(offset_m):
    """Create a test position offset_m west of the NFZ western boundary."""
    # Start from vertex 0 (northwest corner of SSSI) and go west
    ref_lat, ref_lon = find_reference_point()
    return offset_gps(ref_lat, ref_lon, 0, -offset_m)


# ══════════════════════════════════════════════════════════════════════════════
# Test runner
# ══════════════════════════════════════════════════════════════════════════════

def run_test(name, lat, lon, yaw, key, expect_clamped, expect_max_speed_approx=None):
    """Run one test case and print results."""
    toward_vec, nfz_max, nfz_dist, is_inside = compute_nfz_fields(lat, lon)
    (vn_in, ve_in), (vn_out, ve_out), clamped = apply_manual_clamp(key, yaw, toward_vec, nfz_max)

    speed_in = math.sqrt(vn_in ** 2 + ve_in ** 2)
    speed_out = math.sqrt(vn_out ** 2 + ve_out ** 2)

    # Determine pass/fail
    passed = True
    reasons = []

    if expect_clamped and not clamped:
        passed = False
        reasons.append("expected clamping but none applied")
    if not expect_clamped and clamped:
        passed = False
        reasons.append("unexpected clamping applied")

    if expect_max_speed_approx is not None and clamped:
        # Check that toward-NFZ component is near expected max
        if toward_vec:
            v_toward_out = vn_out * toward_vec[0] + ve_out * toward_vec[1]
            if abs(v_toward_out - nfz_max) > 0.1:
                passed = False
                reasons.append(f"toward component {v_toward_out:.2f} != expected max {nfz_max:.2f}")

    status = "PASS" if passed else "FAIL"

    # Print results
    yaw_deg = math.degrees(yaw)
    print(f"\n{'='*70}")
    print(f"  TEST: {name}")
    print(f"  {status}" + (f"  ({', '.join(reasons)})" if reasons else ""))
    print(f"{'='*70}")
    print(f"  Position:       lat={lat:.8f}, lon={lon:.8f}")
    print(f"  NFZ distance:   {nfz_dist:.1f} m  (inside={is_inside})")
    print(f"  NFZ max speed:  {nfz_max if nfz_max is not None else 'None (no limit)'}")
    if toward_vec:
        print(f"  Toward-NFZ vec: ({toward_vec[0]:+.4f} N, {toward_vec[1]:+.4f} E)")
    else:
        print(f"  Toward-NFZ vec: None")
    print(f"  Input:          key='{key}', yaw={yaw_deg:.0f} deg")
    print(f"  Body velocity:  vf={'%.1f' % (MANUAL_FLY_SPEED_MPS if key in ('w',) else (-MANUAL_FLY_SPEED_MPS if key == 's' else 0))}, "
          f"vr={'%.1f' % (MANUAL_FLY_SPEED_MPS if key == 'd' else (-MANUAL_FLY_SPEED_MPS if key == 'a' else 0))}")
    print(f"  NED before:     vn={vn_in:+.2f}, ve={ve_in:+.2f}  (speed={speed_in:.2f} m/s)")
    print(f"  NED after:      vn={vn_out:+.2f}, ve={ve_out:+.2f}  (speed={speed_out:.2f} m/s)")
    print(f"  Clamped:        {clamped}")
    if toward_vec and clamped:
        v_toward_in = vn_in * toward_vec[0] + ve_in * toward_vec[1]
        v_toward_out = vn_out * toward_vec[0] + ve_out * toward_vec[1]
        print(f"  Toward comp:    {v_toward_in:+.2f} -> {v_toward_out:+.2f} m/s")

    return passed


def main():
    print("NFZ Manual-Mode Velocity Clamping Test")
    print("=" * 70)
    print(f"Config values:")
    print(f"  MANUAL_FLY_SPEED_MPS  = {MANUAL_FLY_SPEED_MPS}")
    print(f"  NFZ_SLOW_ZONE_M       = {NFZ_SLOW_ZONE_M}")
    print(f"  NFZ_SCALAR_ZERO_M     = {NFZ_SCALAR_ZERO_M}")
    print(f"  NFZ_ZONE_MAX_SPEED_MPS= {NFZ_ZONE_MAX_SPEED_MPS}")
    print(f"  SSSI polygon:           {len(SSSI_GPS)} vertices")

    results = []

    # All test positions are WEST of the NFZ, so "toward NFZ" is roughly east (+ve)
    # At 15m west of NFZ boundary:
    #   ratio = (15-2)/(40-2) = 13/38 = 0.342
    #   nfz_max = 0.342 * 3.0 = 1.03 m/s

    lat_15, lon_15 = make_test_position(15)
    lat_5, lon_5 = make_test_position(5)
    lat_50, lon_50 = make_test_position(50)

    # Verify distances
    _, _, d15, _ = compute_nfz_fields(lat_15, lon_15)
    _, _, d5, _ = compute_nfz_fields(lat_5, lon_5)
    _, _, d50, _ = compute_nfz_fields(lat_50, lon_50)
    print(f"\nTest positions (west of NFZ vertex 0):")
    print(f"  15m offset -> actual NFZ dist: {d15:.1f} m")
    print(f"   5m offset -> actual NFZ dist: {d5:.1f} m")
    print(f"  50m offset -> actual NFZ dist: {d50:.1f} m")

    # ── Test 1: 15m from NFZ, yaw=0 (north), press D (east toward NFZ) ──────
    results.append(run_test(
        "15m, yaw=0 (N), D (east toward NFZ) -> should clamp",
        lat_15, lon_15, yaw=0, key='d',
        expect_clamped=True, expect_max_speed_approx=1.0
    ))

    # ── Test 2: 15m from NFZ, yaw=0, press A (west away from NFZ) ───────────
    results.append(run_test(
        "15m, yaw=0 (N), A (west away from NFZ) -> no clamp",
        lat_15, lon_15, yaw=0, key='a',
        expect_clamped=False
    ))

    # ── Test 3: 15m from NFZ, yaw=0, press W (north, parallel) ──────────────
    results.append(run_test(
        "15m, yaw=0 (N), W (north, parallel) -> no clamp",
        lat_15, lon_15, yaw=0, key='w',
        expect_clamped=False
    ))

    # ── Test 4: 15m from NFZ, yaw=pi (south), press W (forward=south) ───────
    results.append(run_test(
        "15m, yaw=pi (S), W (forward=south, parallel) -> no clamp",
        lat_15, lon_15, yaw=math.pi, key='w',
        expect_clamped=False
    ))

    # ── Test 5: 15m from NFZ, yaw=pi/2 (east), press W (forward=east) ───────
    results.append(run_test(
        "15m, yaw=pi/2 (E), W (forward=east toward NFZ) -> should clamp",
        lat_15, lon_15, yaw=math.pi / 2, key='w',
        expect_clamped=True, expect_max_speed_approx=1.0
    ))

    # ── Test 6: 5m from NFZ, yaw=0, press D (east toward NFZ) ───────────────
    results.append(run_test(
        "5m, yaw=0 (N), D (east toward NFZ) -> heavy clamp (~0.24 m/s)",
        lat_5, lon_5, yaw=0, key='d',
        expect_clamped=True, expect_max_speed_approx=0.24
    ))

    # ── Test 7: 50m from NFZ (outside buffer), press D ───────────────────────
    results.append(run_test(
        "50m, yaw=0 (N), D (east) -> outside buffer, no clamp",
        lat_50, lon_50, yaw=0, key='d',
        expect_clamped=False
    ))

    # ── Test 8: 15m from NFZ, yaw=pi/4 (NE), press W (diagonal toward NFZ) ─
    results.append(run_test(
        "15m, yaw=pi/4 (NE), W (forward=NE, partial toward) -> should clamp",
        lat_15, lon_15, yaw=math.pi / 4, key='w',
        expect_clamped=True
    ))

    # ── Test 9: 15m from NFZ, yaw=pi/4 (NE), press A (left=NW, away) ───────
    results.append(run_test(
        "15m, yaw=pi/4 (NE), A (left=NW, away from NFZ) -> no clamp",
        lat_15, lon_15, yaw=math.pi / 4, key='a',
        expect_clamped=False
    ))

    # ── Summary ──────────────────────────────────────────────────────────────
    n_pass = sum(results)
    n_total = len(results)
    print(f"\n{'='*70}")
    print(f"  SUMMARY: {n_pass}/{n_total} passed")
    print(f"{'='*70}")

    return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
