#!/usr/bin/env python3
"""
Geofence Unit Test — tests NFZGeofence math without SITL.

Verifies distance_to_boundary, check_position, repulsive_offset, and
filter_waypoints using the real SSSI polygon from the KML file.

Usage:
  python tests/automated/geofence_unit_test.py

No SITL, no camera, no flight — pure geometry tests.
"""

import sys
import os
import math

# Add project root to path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, PROJECT_ROOT)

import config
from utils import GeoTransformer
from geofence import NFZGeofence


# ── Helpers ────────────────────────────────────────────────────────────────

def polygon_centroid(polygon):
    """Simple average of polygon vertices (good enough for convex-ish shapes)."""
    lats = [p[0] for p in polygon]
    lons = [p[1] for p in polygon]
    return sum(lats) / len(lats), sum(lons) / len(lons)


def gps_distance(lat1, lon1, lat2, lon2):
    """Haversine distance in meters."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def gps_offset(lat, lon, north_m, east_m):
    """Offset a GPS point by meters. Returns (new_lat, new_lon)."""
    lat_m_per_deg = 111132.954 - 559.822 * math.cos(2 * math.radians(lat))
    lon_m_per_deg = 111132.954 * math.cos(math.radians(lat))
    return lat + north_m / lat_m_per_deg, lon + east_m / lon_m_per_deg


# ── Test runner ────────────────────────────────────────────────────────────

class GeofenceTestRunner:
    def __init__(self):
        self.results = []

    def record(self, name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        self.results.append((name, passed, detail))
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

    def assert_true(self, name, condition, detail=""):
        self.record(name, condition, detail)

    def assert_approx(self, name, actual, expected, tolerance, unit=""):
        diff = abs(actual - expected)
        ok = diff <= tolerance
        detail = f"expected {expected}{unit}, got {actual:.2f}{unit} (tol={tolerance}{unit})"
        self.record(name, ok, detail)

    def print_summary(self):
        print("\n" + "=" * 60)
        passed = sum(1 for _, p, _ in self.results if p)
        total = len(self.results)
        print(f"  RESULTS: {passed}/{total} tests passed")
        print("=" * 60)
        for name, ok, detail in self.results:
            status = "PASS" if ok else "FAIL"
            line = f"  [{status}] {name}"
            if detail:
                line += f" — {detail}"
            print(line)
        print("=" * 60)
        if passed == total:
            print("  ALL TESTS PASSED")
        else:
            print(f"  {total - passed} TEST(S) FAILED")
        print("=" * 60)


# ── Tests ──────────────────────────────────────────────────────────────────

def run_tests():
    t = GeofenceTestRunner()

    # Load KML to get real SSSI polygon
    kml_path = os.path.join(PROJECT_ROOT, "flight_plans", "AENGM0074.kml")
    loaded = config.load_kml_zones(kml_path)
    if not loaded:
        # Fallback: try alternate path
        kml_path = os.path.join(PROJECT_ROOT, "AENGM0074.kml")
        loaded = config.load_kml_zones(kml_path)

    t.assert_true("KML loaded", loaded, kml_path)
    t.assert_true("SSSI polygon has vertices",
                  len(config.SSSI_GPS) >= 3,
                  f"{len(config.SSSI_GPS)} vertices")

    if not loaded or len(config.SSSI_GPS) < 3:
        print("\n  Cannot run geofence tests without SSSI polygon.")
        t.print_summary()
        return

    # Create GeoTransformer and NFZGeofence
    # Use a reasonable map width (1000px) — the exact value doesn't matter
    # as long as we're consistent (all conversions go through the same transformer)
    MAP_W_PX = 1000
    geo = GeoTransformer(MAP_W_PX)
    fence = NFZGeofence(geo)

    sssi_centroid = polygon_centroid(config.SSSI_GPS)
    print(f"\n  SSSI centroid: {sssi_centroid[0]:.6f}, {sssi_centroid[1]:.6f}")
    print(f"  SSSI vertices: {len(config.SSSI_GPS)}")

    # Find a point that's definitely inside the SSSI polygon.
    # The simple centroid might be outside for concave polygons, so we
    # search the midpoints of vertex pairs until we find one inside.
    inside_point = None
    for i in range(len(config.SSSI_GPS)):
        for j in range(i + 1, len(config.SSSI_GPS)):
            mid_lat = (config.SSSI_GPS[i][0] + config.SSSI_GPS[j][0]) / 2
            mid_lon = (config.SSSI_GPS[i][1] + config.SSSI_GPS[j][1]) / 2
            _, check = fence.distance_to_boundary(mid_lat, mid_lon)
            if check:
                inside_point = (mid_lat, mid_lon)
                break
        if inside_point:
            break

    if inside_point is None:
        # Fallback: try centroid anyway
        inside_point = sssi_centroid

    print(f"  Inside test point: {inside_point[0]:.6f}, {inside_point[1]:.6f}")

    # ── Test 1: distance_to_boundary — point inside SSSI ──────────────────
    print("\n--- distance_to_boundary ---")

    dist_inside, is_inside = fence.distance_to_boundary(
        inside_point[0], inside_point[1])
    t.assert_true("Inside point is inside SSSI", is_inside)
    t.assert_true("Inside point distance > 0", dist_inside > 0,
                  f"dist={dist_inside:.1f}m")

    # ── Test 2: distance_to_boundary — point far outside SSSI ─────────────
    # Move 500m south of centroid (definitely outside)
    far_lat, far_lon = gps_offset(sssi_centroid[0], sssi_centroid[1], -500, 0)
    dist_far, is_inside_far = fence.distance_to_boundary(far_lat, far_lon)
    t.assert_true("Far point is outside SSSI", not is_inside_far)
    t.assert_true("Far point distance > 100m", dist_far > 100,
                  f"dist={dist_far:.1f}m")

    # ── Test 3: distance_to_boundary — point on/near boundary ─────────────
    # Use the first SSSI vertex (should be on or very near boundary)
    v0_lat, v0_lon = config.SSSI_GPS[0]
    dist_vertex, _ = fence.distance_to_boundary(v0_lat, v0_lon)
    t.assert_true("Vertex distance ~0m (on boundary)", dist_vertex < 2.0,
                  f"dist={dist_vertex:.2f}m")

    # ── Test 4: check_position — safe, warning, critical zones ────────────
    print("\n--- check_position ---")

    # Safe: 500m away
    status_safe, factor_safe = fence.check_position(far_lat, far_lon)
    t.assert_true("Far point is 'safe'", status_safe == "safe",
                  f"status={status_safe}")
    t.assert_approx("Safe speed factor = 1.0", factor_safe, 1.0, 0.01)

    # Critical: inside the SSSI
    status_crit, factor_crit = fence.check_position(
        inside_point[0], inside_point[1])
    t.assert_true("Inside point is 'critical'", status_crit == "critical",
                  f"status={status_crit}")
    t.assert_approx("Critical speed factor = 0.0", factor_crit, 0.0, 0.01)

    # Warning: move just outside boundary by ~7m (between HARD=5 and SOFT=10)
    # Find a point 7m outside the nearest boundary edge
    # Use vertex 0 and move away from centroid by 7m
    bearing_lat = v0_lat - sssi_centroid[0]
    bearing_lon = v0_lon - sssi_centroid[1]
    bearing_len = math.sqrt(bearing_lat**2 + bearing_lon**2)
    if bearing_len > 0:
        # Normalize and move 7m outward from centroid through vertex
        norm_lat = bearing_lat / bearing_len
        norm_lon = bearing_lon / bearing_len
        # 7m in GPS degrees (approximate)
        warn_lat, warn_lon = gps_offset(v0_lat, v0_lon,
                                         norm_lat * 7.0, norm_lon * 7.0)
        status_warn, factor_warn = fence.check_position(warn_lat, warn_lon)
        # Could be warning or safe depending on geometry — just check it's not critical
        t.assert_true("Near-boundary point is not critical",
                      status_warn != "critical",
                      f"status={status_warn}, factor={factor_warn:.2f}")

    # ── Test 5: check_position — speed gradient in warning zone ───────────
    # At soft boundary (10m out), speed should be ~1.0
    # At hard boundary (5m out), speed should be ~0.3
    # Verify factor is between 0.3 and 1.0 for warning zone
    if status_warn == "warning":
        t.assert_true("Warning speed factor in [0.3, 1.0]",
                      0.29 <= factor_warn <= 1.01,
                      f"factor={factor_warn:.2f}")

    # ── Test 6: repulsive_offset — pushes away from NFZ ──────────────────
    print("\n--- repulsive_offset ---")

    # Point near SSSI vertex (just outside) — should get pushed away from centroid
    near_lat, near_lon = gps_offset(v0_lat, v0_lon,
                                     norm_lat * 3.0, norm_lon * 3.0)
    off_lat, off_lon = fence.repulsive_offset(near_lat, near_lon)

    # Check that offset is non-zero (we're within soft boundary)
    has_offset = abs(off_lat) > 1e-8 or abs(off_lon) > 1e-8
    t.assert_true("Repulsive offset is non-zero near boundary", has_offset,
                  f"offset=({off_lat:.8f}, {off_lon:.8f})")

    # Check direction: the offset should push AWAY from the boundary
    # i.e., distance_to_boundary should increase after applying the offset.
    # NOTE: if this fails, it may indicate a sign bug in geofence.py's
    # repulsive_offset (the GPS offset conversion can flip direction).
    if has_offset:
        dist_before, _ = fence.distance_to_boundary(near_lat, near_lon)
        dist_after, _ = fence.distance_to_boundary(
            near_lat + off_lat, near_lon + off_lon)
        pushes_away = dist_after > dist_before
        t.assert_true("Offset pushes away from boundary",
                      pushes_away,
                      f"before={dist_before:.1f}m, after={dist_after:.1f}m"
                      + (" (BUG: pushes toward boundary)" if not pushes_away else ""))

    # ── Test 7: repulsive_offset — zero when far away ─────────────────────
    off_far_lat, off_far_lon = fence.repulsive_offset(far_lat, far_lon)
    t.assert_true("No offset when far from NFZ",
                  abs(off_far_lat) < 1e-10 and abs(off_far_lon) < 1e-10,
                  f"offset=({off_far_lat}, {off_far_lon})")

    # ── Test 8: filter_waypoints — removes points inside/near NFZ ─────────
    print("\n--- filter_waypoints ---")

    # Create waypoints: some inside SSSI, some outside, some in buffer zone
    test_waypoints = [
        inside_point,                          # inside — should be removed
        config.SSSI_GPS[0],                    # on boundary — should be removed
        (far_lat, far_lon),                    # 500m away — should be kept
        gps_offset(inside_point[0], inside_point[1], -200, 0),  # 200m south — kept
    ]

    filtered, skipped = fence.filter_waypoints(test_waypoints)
    t.assert_true("filter_waypoints removes some points", skipped > 0,
                  f"skipped {skipped} of {len(test_waypoints)}")
    t.assert_true("filter_waypoints keeps far points", len(filtered) > 0,
                  f"kept {len(filtered)}")
    t.assert_true("Inside point was removed",
                  inside_point not in filtered)
    t.assert_true("Far point was kept",
                  (far_lat, far_lon) in filtered)

    # ── Test 9: filter_waypoints — empty SSSI returns all points ──────────
    # Temporarily clear SSSI
    original_sssi = fence.sssi_polygon_gps
    fence.sssi_polygon_gps = []
    fence._sssi_contour = None  # clear cache

    filtered_all, skipped_none = fence.filter_waypoints(test_waypoints)
    t.assert_true("Empty SSSI returns all waypoints",
                  len(filtered_all) == len(test_waypoints) and skipped_none == 0)

    # Restore
    fence.sssi_polygon_gps = original_sssi
    fence._sssi_contour = None

    # ── Test 10: GeoTransformer round-trip ────────────────────────────────
    print("\n--- GeoTransformer round-trip ---")

    test_lat, test_lon = 51.4234, -2.6714
    px, py = geo.gps_to_pixels(test_lat, test_lon)
    rt_lat, rt_lon = geo.pixels_to_gps(px, py)
    rt_error = gps_distance(test_lat, test_lon, rt_lat, rt_lon)
    t.assert_true("GPS->pixel->GPS round-trip < 5m", rt_error < 5.0,
                  f"error={rt_error:.2f}m")

    # ── Summary ───────────────────────────────────────────────────────────
    t.print_summary()


if __name__ == "__main__":
    print("=" * 60)
    print("  GEOFENCE UNIT TEST")
    print("=" * 60)
    run_tests()
