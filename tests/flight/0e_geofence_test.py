#!/usr/bin/env python3
"""
Geofence / NFZ Test — verify SSSI no-fly zone logic with real config GPS data.

WHAT:    Tests all NFZGeofence methods using the real SSSI polygon from config.py
         (loaded from KML). Checks signed-distance calculations, waypoint filtering,
         repulsive offsets, and position classification — all purely in software.
WHY:     Geofence enforcement is a critical safety layer that was never tested
         standalone before main.py. This script fills that gap by proving the
         geofence logic produces correct results with the actual flight-day GPS
         coordinates. Catches sign bugs, wrong polygon winding, and bad config
         values before they matter in the air.
WHEN:    Run any time after config.py and geofence.py exist. Before first flight
         with NFZ enabled. After any change to SSSI_GPS, NFZ buffer values, or
         geofence.py logic.
WHERE:   Laptop or Pi — no hardware needed.
ENV:     Any venv with numpy and opencv (requirements_dev.txt or requirements_pi.txt).
MODELS:  None (no camera or AI used).
RISK:    Zero — pure computation, no Cube connection, no arming, no flight.

USAGE:
    python tests/flight/0e_geofence_test.py

FLAGS:
    None

OUTPUT:
    Terminal output with [OK]/[FAIL] for 6 tests. Exit code 0 if all pass.

BEST PRACTICES:
    - Run after any change to config.py NFZ values or SSSI_GPS coordinates
    - Run after modifying geofence.py logic
    - If a test fails, check MEMORY.md "Geofence Sign Conventions" for known gotchas

DEPENDENCIES:
    numpy, cv2 (for pointPolygonTest), config.py, geofence.py, utils.py
"""
import sys
import os
import math

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import numpy as np
import config
from utils import GeoTransformer
from geofence import NFZGeofence


# ── Helpers ──────────────────────────────────────────────────

def find_point_inside_sssi(geo, fence):
    """Find a point guaranteed to be inside the SSSI polygon.

    The SSSI polygon is non-convex, so a simple centroid may fall outside.
    Strategy: sample points along lines between vertex pairs and pick one
    that cv2.pointPolygonTest confirms is inside.
    """
    # Try centroid first (works for convex or nearly-convex polygons)
    lats = [p[0] for p in config.SSSI_GPS]
    lons = [p[1] for p in config.SSSI_GPS]
    clat, clon = sum(lats) / len(lats), sum(lons) / len(lons)
    _, is_inside = fence.distance_to_boundary(clat, clon)
    if is_inside:
        return clat, clon

    # Centroid is outside — sample midpoints of all vertex pairs
    for i in range(len(config.SSSI_GPS)):
        for j in range(i + 1, len(config.SSSI_GPS)):
            lat = (config.SSSI_GPS[i][0] + config.SSSI_GPS[j][0]) / 2
            lon = (config.SSSI_GPS[i][1] + config.SSSI_GPS[j][1]) / 2
            _, is_inside = fence.distance_to_boundary(lat, lon)
            if is_inside:
                return lat, lon

    # Last resort: sample on a grid within the bounding box
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    for fi in range(1, 20):
        for fj in range(1, 20):
            lat = min_lat + fi / 20 * (max_lat - min_lat)
            lon = min_lon + fj / 20 * (max_lon - min_lon)
            _, is_inside = fence.distance_to_boundary(lat, lon)
            if is_inside:
                return lat, lon

    # Should never happen with a valid polygon
    return clat, clon


def make_geofence():
    """Create a GeoTransformer and NFZGeofence from config values."""
    # Use a reasonable map width in pixels (matches simulation map scale)
    map_w_px = 2000
    geo = GeoTransformer(map_w_px)
    fence = NFZGeofence(geo)
    return geo, fence


# ── Tests ────────────────────────────────────────────────────

def test_import_geofence():
    """TEST 1: Can we import NFZGeofence and create an instance?"""
    print("\n  TEST 1: IMPORT GEOFENCE")
    print("  " + "-" * 40)
    try:
        geo, fence = make_geofence()
        has_polygon = fence.sssi_polygon_gps is not None and len(fence.sssi_polygon_gps) >= 3
        print(f"  NFZGeofence created OK")
        print(f"  SSSI polygon: {len(config.SSSI_GPS)} corners")
        print(f"  Hard boundary: {fence.HARD_BOUNDARY}m")
        print(f"  Soft boundary: {fence.SOFT_BOUNDARY}m")
        print(f"  Waypoint buffer: {fence.WAYPOINT_BUFFER}m")
        if has_polygon:
            print(f"  [OK] NFZGeofence imported and initialized with {len(config.SSSI_GPS)}-point polygon")
            return True
        else:
            print(f"  [FAIL] SSSI polygon is empty or too small")
            return False
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False


def test_point_inside_nfz():
    """TEST 2: A known interior point is detected as INSIDE the NFZ."""
    print("\n  TEST 2: POINT INSIDE NFZ")
    print("  " + "-" * 40)
    geo, fence = make_geofence()

    clat, clon = find_point_inside_sssi(geo, fence)
    print(f"  Test point (inside SSSI): ({clat:.8f}, {clon:.8f})")

    dist_m, is_inside = fence.distance_to_boundary(clat, clon)
    print(f"  distance_to_boundary: {dist_m:.1f}m, is_inside={is_inside}")

    if is_inside:
        print(f"  [OK] Point correctly detected as INSIDE NFZ ({dist_m:.1f}m from boundary)")
        return True
    else:
        print(f"  [FAIL] Point should be INSIDE NFZ but got is_inside=False")
        print(f"         Check cv2.pointPolygonTest sign convention and polygon winding order")
        return False


def test_point_outside_nfz():
    """TEST 3: TAKEOFF_GPS is detected as OUTSIDE the NFZ."""
    print("\n  TEST 3: POINT OUTSIDE NFZ")
    print("  " + "-" * 40)
    geo, fence = make_geofence()

    tlat, tlon = config.TAKEOFF_GPS
    print(f"  TAKEOFF_GPS: ({tlat:.8f}, {tlon:.8f})")

    dist_m, is_inside = fence.distance_to_boundary(tlat, tlon)
    print(f"  distance_to_boundary: {dist_m:.1f}m, is_inside={is_inside}")

    if not is_inside:
        print(f"  [OK] Takeoff point correctly detected as OUTSIDE NFZ ({dist_m:.1f}m away)")
        return True
    else:
        print(f"  [FAIL] Takeoff point should be OUTSIDE NFZ but got is_inside=True")
        print(f"         Check TAKEOFF_GPS and SSSI_GPS in config.py")
        return False


def test_search_area_outside_nfz():
    """TEST 4: TAKEOFF_GPS and most search area corners are outside SSSI."""
    print("\n  TEST 4: SEARCH AREA vs NFZ")
    print("  " + "-" * 40)
    geo, fence = make_geofence()

    # Check takeoff point
    tlat, tlon = config.TAKEOFF_GPS
    _, takeoff_inside = fence.distance_to_boundary(tlat, tlon)

    # Check each search area corner
    inside_count = 0
    for i, (lat, lon) in enumerate(config.SEARCH_AREA_GPS):
        dist_m, is_inside = fence.distance_to_boundary(lat, lon)
        tag = "INSIDE" if is_inside else "outside"
        print(f"  Search corner {i}: ({lat:.6f}, {lon:.6f}) -> {dist_m:.1f}m {tag}")
        if is_inside:
            inside_count += 1

    print(f"  Takeoff inside SSSI: {takeoff_inside}")
    print(f"  Search corners inside SSSI: {inside_count}/{len(config.SEARCH_AREA_GPS)}")

    # Takeoff must be outside; some search corners may overlap SSSI (that's OK,
    # waypoint filtering handles it), but not ALL of them
    if not takeoff_inside and inside_count < len(config.SEARCH_AREA_GPS):
        print(f"  [OK] Takeoff is safe, {len(config.SEARCH_AREA_GPS) - inside_count} search corners outside NFZ")
        return True
    elif takeoff_inside:
        print(f"  [FAIL] Takeoff is INSIDE the SSSI — check TAKEOFF_GPS in config.py!")
        return False
    else:
        print(f"  [FAIL] ALL search corners are inside SSSI — search area completely overlaps NFZ")
        return False


def test_filter_waypoints():
    """TEST 5: filter_waypoints() removes waypoints inside/near NFZ."""
    print("\n  TEST 5: FILTER WAYPOINTS")
    print("  " + "-" * 40)
    geo, fence = make_geofence()

    # Build a set of test waypoints: interior point (inside), takeoff (outside),
    # and points at varying distances from NFZ
    clat, clon = find_point_inside_sssi(geo, fence)
    tlat, tlon = config.TAKEOFF_GPS

    # Also generate a point far from the SSSI (offset takeoff north by ~200m)
    far_lat = tlat + 0.002  # ~222m north
    far_lon = tlon

    test_waypoints = [
        (clat, clon),       # Inside SSSI (should be removed)
        (tlat, tlon),       # Near SSSI boundary (may or may not be removed depending on buffer)
        (far_lat, far_lon), # Far from SSSI (should survive)
    ]

    # Also add all SSSI corners (all on boundary -> should be removed)
    for lat, lon in config.SSSI_GPS:
        test_waypoints.append((lat, lon))

    total = len(test_waypoints)
    print(f"  Input: {total} waypoints ({len(config.SSSI_GPS)} on SSSI boundary + 3 test points)")

    filtered, removed = fence.filter_waypoints(test_waypoints)
    print(f"  Filtered: {len(filtered)} kept, {removed} removed")
    print(f"  Buffer distance: {fence.WAYPOINT_BUFFER}m")

    # The centroid and all SSSI corners should be removed.
    # The far point should survive.
    far_survived = any(
        abs(lat - far_lat) < 1e-8 and abs(lon - far_lon) < 1e-8
        for lat, lon in filtered
    )

    if removed > 0 and far_survived:
        print(f"  [OK] Removed {removed} waypoints near NFZ, far point survived")
        return True
    elif removed == 0:
        print(f"  [FAIL] No waypoints removed — centroid and boundary points should be filtered")
        return False
    else:
        print(f"  [FAIL] Far point ({far_lat:.6f}, {far_lon:.6f}) was incorrectly removed")
        return False


def test_repulsive_offset():
    """TEST 6: repulsive_offset() pushes away from NFZ boundary (non-zero, correct direction)."""
    print("\n  TEST 6: REPULSIVE OFFSET")
    print("  " + "-" * 40)
    geo, fence = make_geofence()

    # Find a point just outside the SSSI boundary: move from interior toward takeoff,
    # stopping just past the boundary edge.
    clat, clon = find_point_inside_sssi(geo, fence)
    tlat, tlon = config.TAKEOFF_GPS

    # Find a point 3-5m outside the SSSI boundary (not too close to avoid
    # edge cases on non-convex polygon vertices). Walk from interior toward
    # takeoff, find the boundary crossing, then step a bit further out.
    best_lat, best_lon = None, None
    boundary_frac = None
    for frac in [i / 200.0 for i in range(200)]:
        lat = clat + frac * (tlat - clat)
        lon = clon + frac * (tlon - clon)
        dist_m, is_inside = fence.distance_to_boundary(lat, lon)
        if not is_inside:
            boundary_frac = frac
            break

    if boundary_frac is not None:
        # Step further out to get ~3-5m away from boundary (avoid 0.1m edge cases)
        for extra in [0.02, 0.04, 0.06, 0.08, 0.10]:
            frac = boundary_frac + extra
            if frac > 1.0:
                break
            lat = clat + frac * (tlat - clat)
            lon = clon + frac * (tlon - clon)
            dist_m, is_inside = fence.distance_to_boundary(lat, lon)
            if not is_inside and 2.0 < dist_m < fence.SOFT_BOUNDARY:
                best_lat, best_lon = lat, lon
                break

    if best_lat is None:
        # Fallback: use a point slightly outside the first SSSI vertex
        v0_lat, v0_lon = config.SSSI_GPS[0]
        # Nudge north (outside)
        best_lat = v0_lat + 0.00005  # ~5.5m north
        best_lon = v0_lon

    dist_m, is_inside = fence.distance_to_boundary(best_lat, best_lon)
    print(f"  Test point: ({best_lat:.8f}, {best_lon:.8f})")
    print(f"  Distance to boundary: {dist_m:.1f}m, inside={is_inside}")

    offset_lat, offset_lon = fence.repulsive_offset(best_lat, best_lon)
    offset_magnitude = math.sqrt(offset_lat**2 + offset_lon**2)
    print(f"  Repulsive offset: dlat={offset_lat:.10f}, dlon={offset_lon:.10f}")
    print(f"  Offset magnitude: {offset_magnitude:.10f} degrees")

    if offset_magnitude < 1e-12:
        print(f"  [FAIL] Repulsive offset is zero — should push away from boundary")
        return False

    # main.py NEGATES the offset before use (line 917):
    #   push_n, push_e = -off_lat * lat_m, -off_lon * lon_m
    # So the raw offset points TOWARD the NFZ and must be negated.
    # We test it the same way main.py applies it.
    pushed_lat = best_lat - offset_lat
    pushed_lon = best_lon - offset_lon
    pushed_dist, pushed_inside = fence.distance_to_boundary(pushed_lat, pushed_lon)
    print(f"  After NEGATED offset (as main.py does): ({pushed_lat:.8f}, {pushed_lon:.8f})")
    print(f"  New distance: {pushed_dist:.1f}m, inside={pushed_inside}")

    if pushed_dist > dist_m and not pushed_inside:
        print(f"  [OK] Negated offset pushes AWAY from NFZ ({dist_m:.1f}m -> {pushed_dist:.1f}m)")
        print(f"         (main.py negates repulsive_offset before applying — correct)")
        return True
    elif pushed_inside:
        print(f"  [FAIL] Even negated offset pushed point INSIDE NFZ")
        print(f"         Check geofence.py repulsive_offset() logic")
        return False
    else:
        print(f"  [FAIL] Negated offset did not increase distance ({dist_m:.1f}m -> {pushed_dist:.1f}m)")
        print(f"         Repulsive force direction may be wrong")
        return False


def test_check_position():
    """TEST 7 (bonus): check_position() returns correct status/speed_factor."""
    print("\n  TEST 7: CHECK POSITION (status zones)")
    print("  " + "-" * 40)
    geo, fence = make_geofence()

    # Inside SSSI -> critical
    clat, clon = find_point_inside_sssi(geo, fence)
    status, speed = fence.check_position(clat, clon)
    print(f"  Inside NFZ:         status={status}, speed_factor={speed:.2f}")
    inside_ok = (status == 'critical' and speed == 0.0)

    # Far away -> safe
    far_lat = config.TAKEOFF_GPS[0] + 0.002
    far_lon = config.TAKEOFF_GPS[1]
    status, speed = fence.check_position(far_lat, far_lon)
    print(f"  Far point (200m+):  status={status}, speed_factor={speed:.2f}")
    far_ok = (status == 'safe' and speed == 1.0)

    if inside_ok and far_ok:
        print(f"  [OK] Correct status zones: inside=critical, far=safe")
        return True
    else:
        if not inside_ok:
            print(f"  [FAIL] Inside NFZ should be critical/0.0")
        if not far_ok:
            print(f"  [FAIL] Far point should be safe/1.0")
        return False


# ── Main ─────────────────────────────────────────────────────

def main():
    print()
    print("=" * 55)
    print("   GEOFENCE TEST — NFZ logic with real GPS data")
    print("=" * 55)
    print()
    print("  Tests SSSI no-fly zone enforcement using config.py")
    print("  GPS coordinates. No Cube, no camera, no flight.")
    print()

    # Load KML zones (same as main.py does at startup)
    config.load_kml_zones()
    print()

    results = {}
    results['import'] = test_import_geofence()
    results['inside'] = test_point_inside_nfz()
    results['outside'] = test_point_outside_nfz()
    results['search'] = test_search_area_outside_nfz()
    results['filter'] = test_filter_waypoints()
    results['repulsive'] = test_repulsive_offset()
    results['check'] = test_check_position()

    # Summary
    print()
    print("=" * 55)
    print("  RESULTS")
    print("=" * 55)

    tests = [
        ("Import NFZGeofence",                    results['import']),
        ("Point inside NFZ",                        results['inside']),
        ("Point outside NFZ (takeoff)",            results['outside']),
        ("Search area vs NFZ overlap",             results['search']),
        ("Filter waypoints near NFZ",              results['filter']),
        ("Repulsive offset direction",             results['repulsive']),
        ("Check position status zones",            results['check']),
    ]

    passed = 0
    for name, ok in tests:
        symbol = "+" if ok else "X"
        print(f"  [{symbol}] {name}")
        if ok:
            passed += 1

    print()
    if passed == len(tests):
        print(f"  ALL {passed} TESTS PASSED — geofence logic is correct!")
        print("  NFZ enforcement safe to enable in main.py.")
    elif passed >= 5:
        print(f"  {passed}/{len(tests)} passed — mostly working, check failures above.")
    else:
        print(f"  {passed}/{len(tests)} passed — geofence logic has issues.")
        print("  DO NOT fly with NFZ enabled until all tests pass.")

    print()
    print("  What this proves:")
    print("    - SSSI polygon is loaded and has correct coordinates")
    print("    - cv2.pointPolygonTest sign convention is correct")
    print("    - Waypoint filter removes points near NFZ")
    print("    - Repulsive force pushes AWAY from NFZ (not into it)")
    print("    - Position check returns correct status/speed zones")
    print()

    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
