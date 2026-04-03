#!/usr/bin/env python3
"""
Planning Unit Test -- tests PathPlanner lawnmower pattern generation.

Verifies waypoint generation, flight-area containment, NFZ avoidance,
search-area coverage, strip spacing, altitude effects, and edge cases.

Usage:
  python tests/automated/test_planning.py

No SITL, no camera, no flight -- pure geometry tests.
"""

import sys
import os
import math

# Add project root to path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, PROJECT_ROOT)

import config
from utils import GeoTransformer
from planning import PathPlanner


# -- Helpers ----------------------------------------------------------------

def gps_distance(lat1, lon1, lat2, lon2):
    """Haversine distance in meters."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def point_in_polygon_gps(lat, lon, polygon, margin_m=0):
    """Check if a GPS point is inside a polygon (ray-casting), with optional margin.

    margin_m > 0 means the point can be up to margin_m outside the polygon
    and still count as 'inside'. This accounts for floating-point inset in
    the planner (strips are inset by strip_spacing/3 from the polygon edge).
    """
    # Expand polygon outward by margin_m if requested
    if margin_m > 0:
        # Simple expansion: move each vertex outward from centroid
        clat = sum(p[0] for p in polygon) / len(polygon)
        clon = sum(p[1] for p in polygon) / len(polygon)
        expanded = []
        for p in polygon:
            dlat = p[0] - clat
            dlon = p[1] - clon
            dist = gps_distance(clat, clon, p[0], p[1])
            if dist > 0:
                scale = (dist + margin_m) / dist
                expanded.append((clat + dlat * scale, clon + dlon * scale))
            else:
                expanded.append(p)
        polygon = expanded

    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i]
        yj, xj = polygon[j]
        if ((yi > lat) != (yj > lat)) and \
           (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def polygon_centroid(polygon):
    """Simple average of polygon vertices."""
    lats = [p[0] for p in polygon]
    lons = [p[1] for p in polygon]
    return sum(lats) / len(lats), sum(lons) / len(lons)


def make_planner(search_poly_gps, map_w=2000):
    """Create a GeoTransformer and PathPlanner for the given GPS polygon."""
    geo = GeoTransformer(map_w)
    search_poly_px = [geo.gps_to_pixels(lat, lon) for lat, lon in search_poly_gps]
    return geo, PathPlanner(geo, search_poly_px), map_w


# -- Test runner (same pattern as geofence_unit_test.py) --------------------

class PlanningTestRunner:
    def __init__(self):
        self.results = []

    def record(self, name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        self.results.append((name, passed, detail))
        print(f"  [{status}] {name}" + (f" -- {detail}" if detail else ""))

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
                line += f" -- {detail}"
            print(line)
        print("=" * 60)
        if passed == total:
            print("  ALL TESTS PASSED")
        else:
            print(f"  {total - passed} TEST(S) FAILED")
        print("=" * 60)


# -- Tests ------------------------------------------------------------------

def run_tests():
    t = PlanningTestRunner()

    # Use the real search area from config
    search_poly = config.SEARCH_AREA_GPS
    flight_poly = config.FLIGHT_AREA_GPS
    sssi_poly = config.SSSI_GPS

    t.assert_true("Search area has >= 3 vertices",
                  len(search_poly) >= 3,
                  f"{len(search_poly)} vertices")
    t.assert_true("Flight area has >= 3 vertices",
                  len(flight_poly) >= 3,
                  f"{len(flight_poly)} vertices")
    t.assert_true("SSSI polygon has >= 3 vertices",
                  len(sssi_poly) >= 3,
                  f"{len(sssi_poly)} vertices")

    # ── Test 1: Lawnmower pattern generates waypoints ─────────────────────
    print("\n--- Test 1: Lawnmower pattern generates waypoints ---")

    MAP_W = 2000
    MAP_H = 1500
    geo, planner, _ = make_planner(search_poly, MAP_W)
    waypoints = planner.generate_search_pattern(MAP_W, MAP_H, alt_override=35)

    t.assert_true("Waypoints list is not empty",
                  len(waypoints) > 0,
                  f"{len(waypoints)} waypoints")
    t.assert_true("At least 4 waypoints (min 2 strips)",
                  len(waypoints) >= 4,
                  f"{len(waypoints)} waypoints")
    t.assert_true("Waypoints are (lat, lon) tuples",
                  all(isinstance(wp, tuple) and len(wp) == 2 for wp in waypoints))

    # ── Test 2: All waypoints inside flight area ──────────────────────────
    print("\n--- Test 2: All waypoints inside flight area ---")

    # The planner insets strips, and the search area itself should be inside
    # the flight area. Allow a small margin for floating-point edge effects.
    FLIGHT_MARGIN_M = 30  # generous margin for inset + projection error
    outside_flight = []
    for i, wp in enumerate(waypoints):
        if not point_in_polygon_gps(wp[0], wp[1], flight_poly, margin_m=FLIGHT_MARGIN_M):
            outside_flight.append((i, wp))

    t.assert_true("All waypoints within flight area (30m margin)",
                  len(outside_flight) == 0,
                  f"{len(outside_flight)} outside" if outside_flight
                  else f"all {len(waypoints)} inside")
    if outside_flight:
        for idx, wp in outside_flight[:3]:
            print(f"    wp[{idx}] = ({wp[0]:.7f}, {wp[1]:.7f})")

    # ── Test 3: No waypoints inside NFZ ───────────────────────────────────
    print("\n--- Test 3: No waypoints inside NFZ ---")

    inside_nfz = []
    for i, wp in enumerate(waypoints):
        if point_in_polygon_gps(wp[0], wp[1], sssi_poly):
            inside_nfz.append((i, wp))

    t.assert_true("No waypoints inside SSSI NFZ",
                  len(inside_nfz) == 0,
                  f"{len(inside_nfz)} inside NFZ" if inside_nfz
                  else f"all {len(waypoints)} clear")
    if inside_nfz:
        for idx, wp in inside_nfz[:3]:
            print(f"    wp[{idx}] = ({wp[0]:.7f}, {wp[1]:.7f})")

    # ── Test 4: Pattern covers search area ────────────────────────────────
    print("\n--- Test 4: Pattern covers search area ---")

    # Check that waypoints span the search polygon (bounding box coverage)
    wp_lats = [wp[0] for wp in waypoints]
    wp_lons = [wp[1] for wp in waypoints]
    sa_lats = [p[0] for p in search_poly]
    sa_lons = [p[1] for p in search_poly]

    wp_lat_range = max(wp_lats) - min(wp_lats)
    sa_lat_range = max(sa_lats) - min(sa_lats)
    wp_lon_range = max(wp_lons) - min(wp_lons)
    sa_lon_range = max(sa_lons) - min(sa_lons)

    # Waypoints should span at least 50% of the search area in each axis
    # (inset strips reduce coverage slightly, but should still cover most)
    lat_coverage = wp_lat_range / sa_lat_range if sa_lat_range > 0 else 0
    lon_coverage = wp_lon_range / sa_lon_range if sa_lon_range > 0 else 0

    t.assert_true("Lat coverage >= 50% of search area",
                  lat_coverage >= 0.5,
                  f"{lat_coverage * 100:.0f}%")
    t.assert_true("Lon coverage >= 50% of search area",
                  lon_coverage >= 0.5,
                  f"{lon_coverage * 100:.0f}%")

    # Check centroid of waypoints is near centroid of search area
    wp_centroid = (sum(wp_lats) / len(wp_lats), sum(wp_lons) / len(wp_lons))
    sa_centroid = polygon_centroid(search_poly)
    centroid_dist = gps_distance(wp_centroid[0], wp_centroid[1],
                                 sa_centroid[0], sa_centroid[1])
    t.assert_true("Waypoint centroid within 100m of search area centroid",
                  centroid_dist < 100,
                  f"offset={centroid_dist:.1f}m")

    # ── Test 5: Strip spacing matches expected FOV ────────────────────────
    print("\n--- Test 5: Strip spacing correct ---")

    alt = 35.0
    ground_footprint_m = (config.SENSOR_WIDTH_MM * alt) / config.FOCAL_LENGTH_MM
    overlap = 0.2
    expected_swath_m = ground_footprint_m * (1.0 - overlap)

    # Measure distance between strip endpoints (waypoints come in pairs:
    # start-end of each strip, alternating direction)
    # Strips go: wp[0]-wp[1] = strip1, wp[2]-wp[3] = strip2, etc.
    # Distance between strip midpoints gives approximate spacing.
    strip_midpoints = []
    for i in range(0, len(waypoints) - 1, 2):
        mid_lat = (waypoints[i][0] + waypoints[i + 1][0]) / 2
        mid_lon = (waypoints[i][1] + waypoints[i + 1][1]) / 2
        strip_midpoints.append((mid_lat, mid_lon))

    if len(strip_midpoints) >= 2:
        spacings = []
        for i in range(len(strip_midpoints) - 1):
            d = gps_distance(strip_midpoints[i][0], strip_midpoints[i][1],
                             strip_midpoints[i + 1][0], strip_midpoints[i + 1][1])
            spacings.append(d)

        avg_spacing = sum(spacings) / len(spacings)
        t.assert_approx("Average strip spacing matches FOV swath",
                         avg_spacing, expected_swath_m, expected_swath_m * 0.5, "m")
        t.assert_true("Strip spacing > 0",
                      avg_spacing > 0,
                      f"{avg_spacing:.1f}m")
    else:
        t.record("Strip spacing (not enough strips)", False,
                 f"only {len(strip_midpoints)} strip(s)")

    # ── Test 6: Altitude affects spacing ──────────────────────────────────
    print("\n--- Test 6: Altitude affects spacing ---")

    geo_lo, planner_lo, _ = make_planner(search_poly, MAP_W)
    geo_hi, planner_hi, _ = make_planner(search_poly, MAP_W)

    wp_low = planner_lo.generate_search_pattern(MAP_W, MAP_H, alt_override=20)
    wp_high = planner_hi.generate_search_pattern(MAP_W, MAP_H, alt_override=50)

    t.assert_true("Low alt (20m) produces waypoints",
                  len(wp_low) > 0, f"{len(wp_low)} waypoints")
    t.assert_true("High alt (50m) produces waypoints",
                  len(wp_high) > 0, f"{len(wp_high)} waypoints")
    t.assert_true("Higher altitude = fewer waypoints (wider strips)",
                  len(wp_high) <= len(wp_low),
                  f"low={len(wp_low)}, high={len(wp_high)}")

    # Verify the footprint math: 50m alt should have 2.5x wider strips than 20m
    footprint_20 = (config.SENSOR_WIDTH_MM * 20) / config.FOCAL_LENGTH_MM
    footprint_50 = (config.SENSOR_WIDTH_MM * 50) / config.FOCAL_LENGTH_MM
    t.assert_approx("50m footprint is 2.5x wider than 20m",
                     footprint_50 / footprint_20, 2.5, 0.01)

    # ── Test 7: Edge cases ────────────────────────────────────────────────
    print("\n--- Test 7: Edge cases ---")

    # 7a: Very small polygon (10m x 10m)
    center_lat, center_lon = 51.4234, -2.6714
    tiny_poly = [
        (center_lat + 0.00005, center_lon - 0.00005),
        (center_lat + 0.00005, center_lon + 0.00005),
        (center_lat - 0.00005, center_lon + 0.00005),
        (center_lat - 0.00005, center_lon - 0.00005),
    ]
    geo_tiny, planner_tiny, _ = make_planner(tiny_poly, MAP_W)
    wp_tiny = planner_tiny.generate_search_pattern(MAP_W, MAP_H, alt_override=35)
    t.assert_true("Tiny polygon returns waypoints (or single centroid)",
                  len(wp_tiny) >= 1,
                  f"{len(wp_tiny)} waypoints")

    # 7b: Very large polygon (~2km x 2km)
    large_poly = [
        (center_lat + 0.009, center_lon - 0.014),
        (center_lat + 0.009, center_lon + 0.014),
        (center_lat - 0.009, center_lon + 0.014),
        (center_lat - 0.009, center_lon - 0.014),
    ]
    geo_large, planner_large, _ = make_planner(large_poly, MAP_W)
    wp_large = planner_large.generate_search_pattern(MAP_W, MAP_H, alt_override=35)
    t.assert_true("Large polygon returns many waypoints",
                  len(wp_large) > 10,
                  f"{len(wp_large)} waypoints")

    # 7c: Degenerate polygon (3 collinear points)
    degen_poly = [
        (center_lat, center_lon - 0.001),
        (center_lat, center_lon),
        (center_lat, center_lon + 0.001),
    ]
    geo_degen, planner_degen, _ = make_planner(degen_poly, MAP_W)
    wp_degen = planner_degen.generate_search_pattern(MAP_W, MAP_H, alt_override=35)
    # Collinear points form a zero-area polygon; planner may return empty or few points
    t.assert_true("Collinear polygon does not crash",
                  isinstance(wp_degen, list),
                  f"{len(wp_degen)} waypoints (expected 0 or few)")

    # 7d: Polygon with fewer than 3 vertices (should return empty)
    geo_2pt, planner_2pt, _ = make_planner([(51.42, -2.67), (51.43, -2.68)], MAP_W)
    wp_2pt = planner_2pt.generate_search_pattern(MAP_W, MAP_H)
    t.assert_true("2-vertex polygon returns empty list",
                  len(wp_2pt) == 0,
                  f"{len(wp_2pt)} waypoints")

    # 7e: Single vertex
    geo_1pt, planner_1pt, _ = make_planner([(51.42, -2.67)], MAP_W)
    wp_1pt = planner_1pt.generate_search_pattern(MAP_W, MAP_H)
    t.assert_true("1-vertex polygon returns empty list",
                  len(wp_1pt) == 0,
                  f"{len(wp_1pt)} waypoints")

    # ── Test 8: Drone position affects start corner ───────────────────────
    print("\n--- Test 8: Drone position affects start corner ---")

    drone_north = (max(sa_lats) + 0.001, sa_centroid[1])
    drone_south = (min(sa_lats) - 0.001, sa_centroid[1])

    geo_n, planner_n, _ = make_planner(search_poly, MAP_W)
    geo_s, planner_s, _ = make_planner(search_poly, MAP_W)

    wp_from_north = planner_n.generate_search_pattern(MAP_W, MAP_H,
                                                       drone_gps=drone_north,
                                                       alt_override=35)
    wp_from_south = planner_s.generate_search_pattern(MAP_W, MAP_H,
                                                       drone_gps=drone_south,
                                                       alt_override=35)

    if len(wp_from_north) > 0 and len(wp_from_south) > 0:
        # First waypoint should be closer to the respective drone position
        d_north_start = gps_distance(drone_north[0], drone_north[1],
                                      wp_from_north[0][0], wp_from_north[0][1])
        d_south_start = gps_distance(drone_south[0], drone_south[1],
                                      wp_from_south[0][0], wp_from_south[0][1])
        # Both should start near their drone
        t.assert_true("North drone starts near north",
                      d_north_start < 500,
                      f"dist={d_north_start:.0f}m")
        t.assert_true("South drone starts near south",
                      d_south_start < 500,
                      f"dist={d_south_start:.0f}m")

        # First waypoints should differ (different start corners)
        first_diff = gps_distance(wp_from_north[0][0], wp_from_north[0][1],
                                   wp_from_south[0][0], wp_from_south[0][1])
        t.assert_true("Different drone positions give different start points",
                      first_diff > 1.0,
                      f"first wp diff={first_diff:.1f}m")
    else:
        t.record("Drone position test", False, "no waypoints generated")

    # ── Test 9: Smooth waypoints ──────────────────────────────────────────
    print("\n--- Test 9: Smooth waypoints ---")

    if len(waypoints) >= 4:
        smoothed = PathPlanner.smooth_waypoints(waypoints)
        t.assert_true("Smoothed has more waypoints than original",
                      len(smoothed) > len(waypoints),
                      f"original={len(waypoints)}, smoothed={len(smoothed)}")
        t.assert_true("Smoothed starts at same point",
                      smoothed[0] == waypoints[0])
        t.assert_true("Smoothed ends at same point",
                      smoothed[-1] == waypoints[-1])

        # Smoothing with < 4 waypoints returns unchanged
        short = [(51.42, -2.67), (51.43, -2.68), (51.44, -2.69)]
        smoothed_short = PathPlanner.smooth_waypoints(short)
        t.assert_true("Smoothing < 4 waypoints returns unchanged",
                      smoothed_short == short)
    else:
        t.record("Smooth waypoints", False, "not enough waypoints to test")

    # ── Summary ───────────────────────────────────────────────────────────
    t.print_summary()


if __name__ == "__main__":
    print("=" * 60)
    print("  PLANNING UNIT TEST")
    print("=" * 60)
    run_tests()
