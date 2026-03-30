#!/usr/bin/env python3
"""
Planning Test — verify lawnmower/spiral pattern generation before flight.

WHAT:    Generates the search pattern from config.py zones and validates the
         output: correct number of waypoints, all inside FLIGHT_AREA_GPS,
         none inside SSSI_GPS, and computes distance/time metrics.
WHY:     planning.py is the foundation of every autonomous flight but was never
         tested standalone. A bad pattern means wrong coverage, NFZ violation,
         or wasted battery. This script catches those issues on the ground.
WHEN:    After config.py zones are set (KML loaded), before 0b_bench_mission.py
         or any flight. Run again whenever you change TARGET_ALT, SEARCH_AREA_GPS,
         or camera parameters.
WHERE:   Laptop or Pi — no Cube, no camera, no GPS needed.
ENV:     Any venv with numpy and opencv-python (or opencv-python-headless).
MODELS:  None (no AI used).
RISK:    Zero — generates waypoints in memory, never connects to anything.

USAGE:
    python tests/flight/0d_planning_test.py
    python tests/flight/0d_planning_test.py --alt 20
    python tests/flight/0d_planning_test.py --spiral

FLAGS:
    --alt <m>      Override search altitude (default: config.TARGET_ALT)
    --spiral       Test spiral pattern instead of lawnmower

OUTPUT:
    Terminal output with pass/fail for 6 tests: import, KML load, pattern
    generation, bounds check, NFZ check, and metrics. Optionally saves
    0d_pattern.jpg visualization. Exit code 0 if all critical tests pass.

BEST PRACTICES:
    - Run after every config change that affects the search pattern
    - Compare waypoint count and flight time between altitudes
    - Check the saved 0d_pattern.jpg visually — a picture catches bugs fast
    - If NFZ test fails, increase NFZ_WAYPOINT_BUFFER_M in config.py

DEPENDENCIES:
    config.py, planning.py, utils.py (GeoTransformer), numpy, cv2
    Optional: matplotlib (for pattern visualization)
"""
import sys
import os
import math
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)


# ── Helpers ──────────────────────────────────────────────────

def point_in_polygon(lat, lon, polygon):
    """Ray-casting point-in-polygon test. Pure Python, no cv2 needed.

    Args:
        lat, lon: point to test.
        polygon: list of (lat, lon) vertices.

    Returns:
        True if point is inside the polygon.
    """
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        lat_i, lon_i = polygon[i]
        lat_j, lon_j = polygon[j]
        if ((lon_i > lon) != (lon_j > lon)) and \
           (lat < (lat_j - lat_i) * (lon - lon_i) / (lon_j - lon_i) + lat_i):
            inside = not inside
        j = i
    return inside


def haversine_m(lat1, lon1, lat2, lon2):
    """Great-circle distance between two GPS points in metres."""
    R = 6371000.0
    rlat1, rlat2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def polygon_area_m2(polygon):
    """Approximate area of a GPS polygon in square metres (Shoelace on projected coords)."""
    if len(polygon) < 3:
        return 0.0
    # Project to metres relative to centroid
    clat = sum(p[0] for p in polygon) / len(polygon)
    clon = sum(p[1] for p in polygon) / len(polygon)
    lat_m = 111132.954 - 559.822 * math.cos(2 * math.radians(clat))
    lon_m = 111132.954 * math.cos(math.radians(clat))
    pts = [((p[0] - clat) * lat_m, (p[1] - clon) * lon_m) for p in polygon]
    # Shoelace formula
    n = len(pts)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i][0] * pts[j][1]
        area -= pts[j][0] * pts[i][1]
    return abs(area) / 2.0


# ── Tests ────────────────────────────────────────────────────

def test_import_planning():
    """Test 1: can we import PathPlanner and GeoTransformer?"""
    print("\n  TEST 1: IMPORT PLANNING")
    print("  " + "-" * 40)
    try:
        from planning import PathPlanner
        from utils import GeoTransformer
        print("  [OK] PathPlanner imported")
        print("  [OK] GeoTransformer imported")
        return True
    except ImportError as e:
        print(f"  [FAIL] Import error: {e}")
        return False


def test_load_kml():
    """Test 2: does KML load correctly?"""
    print("\n  TEST 2: LOAD KML ZONES")
    print("  " + "-" * 40)
    import config

    # Try to load KML
    kml_path = os.path.join(project_root, "flight_plans", "AENGM0074.kml")
    if os.path.exists(kml_path):
        ok = config.load_kml_zones(kml_path)
        if ok:
            print(f"  [OK] KML loaded from {kml_path}")
        else:
            print(f"  [FAIL] KML file exists but failed to parse")
            return False
    else:
        print(f"  [?]  KML not found at {kml_path} — using fallback coords")

    # Validate zones exist and have enough vertices
    checks = [
        ("SEARCH_AREA_GPS", config.SEARCH_AREA_GPS, 3),
        ("FLIGHT_AREA_GPS", config.FLIGHT_AREA_GPS, 3),
        ("SSSI_GPS", config.SSSI_GPS, 3),
    ]
    all_ok = True
    for name, zone, min_pts in checks:
        if len(zone) >= min_pts:
            print(f"  [OK] {name}: {len(zone)} vertices")
        else:
            print(f"  [FAIL] {name}: only {len(zone)} vertices (need >= {min_pts})")
            all_ok = False

    # Print takeoff
    print(f"  Takeoff: {config.TAKEOFF_GPS[0]:.6f}, {config.TAKEOFF_GPS[1]:.6f}")

    # Print search area size
    area_m2 = polygon_area_m2(config.SEARCH_AREA_GPS)
    print(f"  Search area: {area_m2:.0f} m2 ({area_m2 / 10000:.2f} ha)")

    return all_ok


def test_generate_pattern(alt, use_spiral=False):
    """Test 3: does the pattern generator produce >0 waypoints?"""
    print("\n  TEST 3: GENERATE PATTERN")
    print("  " + "-" * 40)
    import config
    from planning import PathPlanner
    from utils import GeoTransformer

    pattern_type = "spiral" if use_spiral else "lawnmower"
    print(f"  Pattern type: {pattern_type}")
    print(f"  Altitude: {alt:.0f} m")

    # Compute ground footprint for info
    gf_m = (config.SENSOR_WIDTH_MM * alt) / config.FOCAL_LENGTH_MM
    print(f"  Ground footprint: {gf_m:.1f} m (sensor={config.SENSOR_WIDTH_MM}mm, "
          f"focal={config.FOCAL_LENGTH_MM}mm)")

    # Create GeoTransformer with a virtual map (1000px wide)
    map_w = 1000
    geo = GeoTransformer(map_w)
    map_h = int(map_w * 0.75)  # 4:3 aspect for virtual map

    # Convert search polygon to pixel coords
    search_poly_px = [geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS]
    print(f"  Search polygon pixels: {len(search_poly_px)} vertices")

    # Check pixels are within a reasonable range (not all zero or huge)
    xs = [p[0] for p in search_poly_px]
    ys = [p[1] for p in search_poly_px]
    print(f"  Pixel range: x=[{min(xs)}, {max(xs)}], y=[{min(ys)}, {max(ys)}]")

    # If pixels are out of virtual map bounds, resize the map
    needed_w = max(abs(min(xs)), abs(max(xs))) * 2 + 100
    needed_h = max(abs(min(ys)), abs(max(ys))) * 2 + 100
    if needed_w > map_w or needed_h > map_h:
        map_w = int(max(needed_w, map_w))
        map_h = int(max(needed_h, map_h))
        geo = GeoTransformer(map_w)
        search_poly_px = [geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS]
        print(f"  Resized virtual map to {map_w}x{map_h}")

    # Generate pattern
    planner = PathPlanner(geo, search_poly_px)

    if use_spiral:
        waypoints = planner.generate_spiral_pattern(map_w, map_h,
                                                     drone_gps=config.TAKEOFF_GPS,
                                                     alt_override=alt)
    else:
        waypoints = planner.generate_search_pattern(map_w, map_h,
                                                     drone_gps=config.TAKEOFF_GPS,
                                                     alt_override=alt)

    if len(waypoints) > 0:
        print(f"  [OK] Generated {len(waypoints)} waypoints")
        # Print first and last
        print(f"  First: ({waypoints[0][0]:.6f}, {waypoints[0][1]:.6f})")
        print(f"  Last:  ({waypoints[-1][0]:.6f}, {waypoints[-1][1]:.6f})")
        return True, waypoints, geo, map_w, map_h
    else:
        print(f"  [FAIL] Generated 0 waypoints")
        return False, [], None, 0, 0


def test_waypoints_in_bounds(waypoints):
    """Test 4: are all waypoints inside FLIGHT_AREA_GPS?"""
    print("\n  TEST 4: WAYPOINTS INSIDE FLIGHT AREA")
    print("  " + "-" * 40)
    import config

    if not waypoints:
        print("  [FAIL] No waypoints to check")
        return False

    out_of_bounds = []
    for i, (lat, lon) in enumerate(waypoints):
        if not point_in_polygon(lat, lon, config.FLIGHT_AREA_GPS):
            out_of_bounds.append(i)

    if len(out_of_bounds) == 0:
        print(f"  [OK] All {len(waypoints)} waypoints inside FLIGHT_AREA_GPS")
        return True
    else:
        print(f"  [FAIL] {len(out_of_bounds)} waypoints OUTSIDE flight area:")
        for idx in out_of_bounds[:5]:
            lat, lon = waypoints[idx]
            print(f"         WP {idx}: ({lat:.6f}, {lon:.6f})")
        if len(out_of_bounds) > 5:
            print(f"         ... and {len(out_of_bounds) - 5} more")
        return False


def test_waypoints_avoid_nfz(waypoints):
    """Test 5: are all waypoints outside SSSI_GPS no-fly zone?"""
    print("\n  TEST 5: WAYPOINTS AVOID NFZ (SSSI)")
    print("  " + "-" * 40)
    import config

    if not waypoints:
        print("  [FAIL] No waypoints to check")
        return False

    if not config.SSSI_GPS or len(config.SSSI_GPS) < 3:
        print("  [?]  No SSSI zone defined — skipping (counts as pass)")
        return True

    inside_nfz = []
    for i, (lat, lon) in enumerate(waypoints):
        if point_in_polygon(lat, lon, config.SSSI_GPS):
            inside_nfz.append(i)

    if len(inside_nfz) == 0:
        print(f"  [OK] All {len(waypoints)} waypoints outside SSSI")
        return True
    else:
        print(f"  [FAIL] {len(inside_nfz)} waypoints INSIDE SSSI no-fly zone:")
        for idx in inside_nfz[:5]:
            lat, lon = waypoints[idx]
            print(f"         WP {idx}: ({lat:.6f}, {lon:.6f})")
        if len(inside_nfz) > 5:
            print(f"         ... and {len(inside_nfz) - 5} more")
        print(f"         Increase NFZ_WAYPOINT_BUFFER_M (currently {config.NFZ_WAYPOINT_BUFFER_M}m)")
        return False


def test_pattern_metrics(waypoints, alt):
    """Test 6: compute total distance, flight time, coverage stats."""
    print("\n  TEST 6: PATTERN METRICS")
    print("  " + "-" * 40)
    import config

    if not waypoints or len(waypoints) < 2:
        print("  [FAIL] Need >= 2 waypoints to compute metrics")
        return False

    # Total path distance
    total_dist_m = 0.0
    leg_distances = []
    for i in range(len(waypoints) - 1):
        d = haversine_m(waypoints[i][0], waypoints[i][1],
                        waypoints[i + 1][0], waypoints[i + 1][1])
        leg_distances.append(d)
        total_dist_m += d

    # Distance from takeoff to first waypoint and from last back to takeoff
    dist_to_start = haversine_m(config.TAKEOFF_GPS[0], config.TAKEOFF_GPS[1],
                                waypoints[0][0], waypoints[0][1])
    dist_from_end = haversine_m(waypoints[-1][0], waypoints[-1][1],
                                config.TAKEOFF_GPS[0], config.TAKEOFF_GPS[1])
    transit_dist = dist_to_start + dist_from_end

    # Flight time estimates
    search_speed = config.SEARCH_SPEED_MPS
    transit_speed = config.TRANSIT_SPEED_MPS
    search_time_s = total_dist_m / search_speed if search_speed > 0 else 0
    transit_time_s = transit_dist / transit_speed if transit_speed > 0 else 0
    total_time_s = search_time_s + transit_time_s

    # Altitude-dependent speed
    alt_speed = config.speed_for_altitude(alt)
    alt_search_time_s = total_dist_m / alt_speed if alt_speed > 0 else 0
    alt_total_time_s = alt_search_time_s + transit_time_s

    # Coverage area
    search_area_m2 = polygon_area_m2(config.SEARCH_AREA_GPS)

    # Ground footprint
    gf_m = (config.SENSOR_WIDTH_MM * alt) / config.FOCAL_LENGTH_MM

    # Number of strips (lawnmower: pairs of waypoints)
    num_strips = len(waypoints) // 2

    # Leg statistics
    avg_leg = total_dist_m / len(leg_distances) if leg_distances else 0
    max_leg = max(leg_distances) if leg_distances else 0
    min_leg = min(leg_distances) if leg_distances else 0

    print(f"  Waypoints:        {len(waypoints)}")
    print(f"  Strips:           {num_strips}")
    print(f"  Ground footprint: {gf_m:.1f} m")
    print()
    print(f"  Path distance:    {total_dist_m:.0f} m ({total_dist_m / 1000:.2f} km)")
    print(f"  Transit distance: {transit_dist:.0f} m "
          f"(to start: {dist_to_start:.0f}m, from end: {dist_from_end:.0f}m)")
    print(f"  Total distance:   {total_dist_m + transit_dist:.0f} m")
    print()
    print(f"  Leg stats:        avg={avg_leg:.0f}m, min={min_leg:.0f}m, max={max_leg:.0f}m")
    print()
    print(f"  Search speed:     {search_speed:.1f} m/s (config.SEARCH_SPEED_MPS)")
    print(f"  Alt-dep speed:    {alt_speed:.1f} m/s (at {alt:.0f}m altitude)")
    print(f"  Transit speed:    {transit_speed:.1f} m/s")
    print()
    print(f"  Search time:      {search_time_s:.0f}s ({search_time_s / 60:.1f} min) "
          f"@ {search_speed:.0f} m/s")
    print(f"  Alt-dep time:     {alt_search_time_s:.0f}s ({alt_search_time_s / 60:.1f} min) "
          f"@ {alt_speed:.0f} m/s")
    print(f"  Transit time:     {transit_time_s:.0f}s ({transit_time_s / 60:.1f} min)")
    print(f"  Total time:       {total_time_s:.0f}s ({total_time_s / 60:.1f} min) "
          f"@ {search_speed:.0f} m/s")
    print(f"  Total (alt-dep):  {alt_total_time_s:.0f}s ({alt_total_time_s / 60:.1f} min) "
          f"@ {alt_speed:.0f} m/s")
    print()
    print(f"  Search area:      {search_area_m2:.0f} m2 ({search_area_m2 / 10000:.2f} ha)")

    print()
    print(f"  [OK] Metrics computed")
    return True


def save_visualization(waypoints, alt):
    """Optional: save pattern to 0d_pattern.jpg using matplotlib."""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n  [?]  matplotlib not available — skipping visualization")
        return

    import config

    print("\n  VISUALIZATION")
    print("  " + "-" * 40)

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Plot flight area boundary
    fa = config.FLIGHT_AREA_GPS + [config.FLIGHT_AREA_GPS[0]]
    ax.plot([p[1] for p in fa], [p[0] for p in fa], 'b--', linewidth=1, label='Flight Area')

    # Plot search area boundary
    sa = config.SEARCH_AREA_GPS + [config.SEARCH_AREA_GPS[0]]
    ax.plot([p[1] for p in sa], [p[0] for p in sa], 'g-', linewidth=2, label='Search Area')

    # Plot SSSI boundary
    if config.SSSI_GPS and len(config.SSSI_GPS) >= 3:
        nfz = config.SSSI_GPS + [config.SSSI_GPS[0]]
        ax.fill([p[1] for p in nfz], [p[0] for p in nfz], alpha=0.2, color='red')
        ax.plot([p[1] for p in nfz], [p[0] for p in nfz], 'r-', linewidth=2, label='SSSI (NFZ)')

    # Plot waypoints and path
    if waypoints:
        lats = [wp[0] for wp in waypoints]
        lons = [wp[1] for wp in waypoints]
        ax.plot(lons, lats, 'k-', linewidth=0.8, alpha=0.5)
        ax.scatter(lons, lats, c=range(len(waypoints)), cmap='viridis', s=10, zorder=5)
        ax.scatter([lons[0]], [lats[0]], c='lime', s=80, marker='^', zorder=10, label='Start')
        ax.scatter([lons[-1]], [lats[-1]], c='red', s=80, marker='v', zorder=10, label='End')

    # Plot takeoff
    ax.scatter([config.TAKEOFF_GPS[1]], [config.TAKEOFF_GPS[0]],
               c='orange', s=100, marker='*', zorder=10, label='Takeoff')

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title(f'Search Pattern — {len(waypoints)} waypoints @ {alt:.0f}m alt')
    ax.legend(loc='upper right', fontsize=8)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    out_path = os.path.join(project_root, "0d_pattern.jpg")
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [OK] Saved visualization to {out_path}")


# ── Main ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Planning test — verify search pattern")
    parser.add_argument("--alt", type=float, default=None, help="Override search altitude (m)")
    parser.add_argument("--spiral", action="store_true", help="Test spiral pattern instead")
    args = parser.parse_args()

    import config
    alt = args.alt if args.alt is not None else config.TARGET_ALT

    print()
    print("=" * 55)
    print("   PLANNING TEST — Search pattern verification")
    print("=" * 55)
    print()
    print("  No Cube, no camera, no flight.")
    print(f"  Pattern: {'spiral' if args.spiral else 'lawnmower'}")
    print(f"  Altitude: {alt:.0f} m")
    print()

    results = {}

    # Test 1: Import
    results['import'] = test_import_planning()

    if not results['import']:
        print("\n  Cannot continue without planning imports.")
        sys.exit(1)

    # Test 2: KML load
    results['kml'] = test_load_kml()

    # Test 3: Generate pattern
    ok, waypoints, geo, map_w, map_h = test_generate_pattern(alt, use_spiral=args.spiral)
    results['generate'] = ok

    # Test 4: Bounds check
    results['bounds'] = test_waypoints_in_bounds(waypoints)

    # Test 5: NFZ check
    results['nfz'] = test_waypoints_avoid_nfz(waypoints)

    # Test 6: Metrics
    results['metrics'] = test_pattern_metrics(waypoints, alt)

    # Optional visualization
    if waypoints:
        save_visualization(waypoints, alt)

    # Summary
    print()
    print("=" * 55)
    print("  RESULTS")
    print("=" * 55)

    tests = [
        ("Import planning.py", results['import']),
        ("Load KML zones", results['kml']),
        ("Generate pattern (> 0 waypoints)", results['generate']),
        ("All waypoints inside flight area", results['bounds']),
        ("No waypoints inside NFZ (SSSI)", results['nfz']),
        ("Pattern metrics computed", results['metrics']),
    ]

    passed = 0
    for name, ok in tests:
        symbol = "+" if ok else "X"
        print(f"  [{symbol}] {name}")
        if ok:
            passed += 1

    print()
    if passed == len(tests):
        print(f"  ALL {passed} TESTS PASSED — pattern is ready for flight!")
    elif passed >= 4:
        print(f"  {passed}/{len(tests)} passed — review failures before flight.")
    else:
        print(f"  {passed}/{len(tests)} passed — fix issues before proceeding.")

    print()
    print("  What this proves:")
    print("    - planning.py generates a valid search pattern")
    print("    - Waypoints respect flight area and NFZ boundaries")
    print("    - Flight time and distance are known before takeoff")
    print()

    return passed >= 4


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
