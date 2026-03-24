"""
Coverage simulation for SAR drone lawnmower path at different altitudes.

For each altitude, simulates turning and no-turn modes, computing:
- Number of strips and waypoints
- Coverage percentage of the search polygon
- Uncovered area (m^2)
- Strip spacing (m)
- Minimum overlap between adjacent strips
"""
import sys, os, math
import numpy as np
import cv2

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

import config
from utils import GeoTransformer
from planning import PathPlanner

# ── Constants ──────────────────────────────────────────────────────────
MAP_SIZE = 3000  # virtual map pixels
ALTITUDES = [15, 20, 25, 30, 40, 50]
SENSOR_W = config.SENSOR_WIDTH_MM   # 5.02
FOCAL    = config.FOCAL_LENGTH_MM   # 5.46
IMG_W    = config.IMAGE_W           # 1456
IMG_H    = config.IMAGE_H           # 1088
OVERLAP  = 0.2                      # 20% overlap (matches planner)


def ground_footprint(alt, sensor_w_mm, focal_mm, img_w, img_h):
    """Return (ground_width_m, ground_height_m) at given altitude."""
    gw = (sensor_w_mm * alt) / focal_mm
    gh = gw * (img_h / img_w)
    return gw, gh


def polygon_area_m2(gps_poly):
    """Shoelace formula for polygon area in m^2 from GPS coords."""
    n = len(gps_poly)
    if n < 3:
        return 0.0
    lat0 = gps_poly[0][0]
    lat_m = 111132.954 - 559.822 * math.cos(2 * math.radians(lat0))
    lon_m = 111132.954 * math.cos(math.radians(lat0))
    # Convert to local metres
    pts = []
    for lat, lon in gps_poly:
        x = (lon - gps_poly[0][1]) * lon_m
        y = (lat - gps_poly[0][0]) * lat_m
        pts.append((x, y))
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i][0] * pts[j][1]
        area -= pts[j][0] * pts[i][1]
    return abs(area) / 2.0


def build_coverage_mask(geo, search_poly_px, waypoints_gps, alt, no_turn, scan_angle_deg):
    """
    Build a binary mask (1px = 1m) covering the polygon bounding box,
    then paint the camera footprint along each strip.
    Returns (polygon_mask, coverage_mask, pix_per_m_coverage).
    """
    # Bounding box of polygon in pixels
    poly_arr = np.array(search_poly_px, dtype=np.float64)
    min_x, min_y = poly_arr.min(axis=0)
    max_x, max_y = poly_arr.max(axis=0)

    # Resolution: 1 pixel = 1 metre
    ppm = geo.pix_per_m  # map pixels per metre
    width_m = (max_x - min_x) / ppm
    height_m = (max_y - min_y) / ppm
    # Add margin
    margin = 20  # metres
    cw = int(width_m + 2 * margin)
    ch = int(height_m + 2 * margin)
    if cw < 1 or ch < 1:
        return None, None, 1.0

    # Polygon mask in coverage-space (1px = 1m)
    poly_coverage = []
    for px, py in search_poly_px:
        cx = (px - min_x) / ppm + margin
        cy = (py - min_y) / ppm + margin
        poly_coverage.append([int(cx), int(cy)])
    poly_coverage = np.array([poly_coverage], dtype=np.int32)

    poly_mask = np.zeros((ch, cw), dtype=np.uint8)
    cv2.fillPoly(poly_mask, poly_coverage, 255)

    coverage_mask = np.zeros((ch, cw), dtype=np.uint8)

    # Camera footprint in metres
    gw, gh = ground_footprint(alt, SENSOR_W, FOCAL, IMG_W, IMG_H)

    # Process waypoints pairwise (each pair = one strip)
    for i in range(0, len(waypoints_gps) - 1, 2):
        lat1, lon1 = waypoints_gps[i]
        lat2, lon2 = waypoints_gps[i + 1]

        # Convert to coverage-space
        px1, py1 = geo.gps_to_pixels(lat1, lon1)
        px2, py2 = geo.gps_to_pixels(lat2, lon2)
        cx1 = (px1 - min_x) / ppm + margin
        cy1 = (py1 - min_y) / ppm + margin
        cx2 = (px2 - min_x) / ppm + margin
        cy2 = (py2 - min_y) / ppm + margin

        # Strip direction vector
        dx = cx2 - cx1
        dy = cy2 - cy1
        length = math.sqrt(dx * dx + dy * dy)
        if length < 0.01:
            continue

        if no_turn:
            # Fixed orientation: camera faces along scan_angle_deg
            # Footprint: gw perpendicular to scan angle, gh along scan angle
            # But the perpendicular coverage is gh (shorter dim) because camera
            # is fixed along the scan line → height is perpendicular
            half_perp = gh / 2.0  # perpendicular half-width
            half_along = gw / 2.0  # along-strip half-width
        else:
            # Turning mode: drone yaws to face travel direction each strip
            # Camera width is perpendicular to travel
            half_perp = gw / 2.0
            half_along = gh / 2.0

        # Unit vectors
        ux, uy = dx / length, dy / length  # along strip
        nx, ny = -uy, ux  # perpendicular (normal)

        # Rectangle corners: extend strip endpoints by half_along, widen by half_perp
        # Start a bit before p1, end a bit after p2
        corners = np.array([
            [cx1 - ux * half_along + nx * half_perp, cy1 - uy * half_along + ny * half_perp],
            [cx1 - ux * half_along - nx * half_perp, cy1 - uy * half_along - ny * half_perp],
            [cx2 + ux * half_along - nx * half_perp, cy2 + uy * half_along - ny * half_perp],
            [cx2 + ux * half_along + nx * half_perp, cy2 + uy * half_along + ny * half_perp],
        ], dtype=np.int32)

        cv2.fillConvexPoly(coverage_mask, corners, 255)

    return poly_mask, coverage_mask, 1.0


def compute_min_overlap(geo, waypoints_gps, alt, no_turn, search_poly_px):
    """
    Compute the minimum overlap percentage between adjacent strips.
    """
    if len(waypoints_gps) < 4:
        return 0.0

    gw, gh = ground_footprint(alt, SENSOR_W, FOCAL, IMG_W, IMG_H)
    ppm = geo.pix_per_m

    min_overlap_pct = 100.0

    for i in range(0, len(waypoints_gps) - 3, 2):
        # Strip i: waypoints[i], waypoints[i+1]
        # Strip i+1: waypoints[i+2], waypoints[i+3]
        lat1, lon1 = waypoints_gps[i]
        lat2, lon2 = waypoints_gps[i + 1]
        lat3, lon3 = waypoints_gps[i + 2]
        lat4, lon4 = waypoints_gps[i + 3]

        # Midpoints in pixels
        px1, py1 = geo.gps_to_pixels(lat1, lon1)
        px2, py2 = geo.gps_to_pixels(lat2, lon2)
        px3, py3 = geo.gps_to_pixels(lat3, lon3)
        px4, py4 = geo.gps_to_pixels(lat4, lon4)

        mid1x = (px1 + px2) / 2.0
        mid1y = (py1 + py2) / 2.0
        mid2x = (px3 + px4) / 2.0
        mid2y = (py3 + py4) / 2.0

        # Distance between strip centres in metres
        dist_px = math.sqrt((mid2x - mid1x)**2 + (mid2y - mid1y)**2)
        dist_m = dist_px / ppm

        if no_turn:
            # Perpendicular coverage = gh
            strip_width = gh
        else:
            strip_width = gw

        # Overlap = 2 * half_width - centre_distance
        overlap_m = strip_width - dist_m
        if strip_width > 0:
            overlap_pct = (overlap_m / strip_width) * 100.0
        else:
            overlap_pct = 0.0

        min_overlap_pct = min(min_overlap_pct, overlap_pct)

    return min_overlap_pct


def run_simulation():
    # Load KML zones
    config.load_kml_zones()
    search_poly = config.SEARCH_AREA_GPS

    if len(search_poly) < 3:
        print("ERROR: No search polygon loaded. Check KML file.")
        return

    total_area = polygon_area_m2(search_poly)
    print(f"\nSearch polygon: {len(search_poly)} corners")
    print(f"Total polygon area: {total_area:,.0f} m^2 ({total_area/10000:.2f} hectares)\n")

    # Build GeoTransformer
    geo = GeoTransformer(MAP_SIZE)

    # Convert polygon to pixels
    search_poly_px = [geo.gps_to_pixels(lat, lon) for lat, lon in search_poly]

    # Header
    header = (
        f"{'Alt(m)':>6} | {'Mode':<8} | {'Strips':>6} | {'Waypts':>7} | "
        f"{'Coverage%':>9} | {'Uncovered(m²)':>14} | {'Strip_sp(m)':>11} | {'Min_Overlap%':>12}"
    )
    sep = "-" * len(header)
    print(header)
    print(sep)

    for alt in ALTITUDES:
        gw, gh = ground_footprint(alt, SENSOR_W, FOCAL, IMG_W, IMG_H)

        for no_turn in [False, True]:
            mode_name = "no-turn" if no_turn else "turning"

            # Strip spacing
            if no_turn:
                perp_coverage = gh
            else:
                perp_coverage = gw

            strip_spacing = perp_coverage * (1.0 - OVERLAP)

            # Build planner
            planner = PathPlanner(geo, search_poly_px)
            planner._no_turn = no_turn

            # Generate waypoints (suppress planner prints)
            import io, contextlib
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                wps = planner.generate_search_pattern(MAP_SIZE, MAP_SIZE, alt_override=alt)

            n_waypoints = len(wps)
            n_strips = n_waypoints // 2

            # Build coverage mask
            poly_mask, cov_mask, _ = build_coverage_mask(
                geo, search_poly_px, wps, alt, no_turn,
                getattr(planner, 'last_scan_angle', 0)
            )

            if poly_mask is None:
                print(f"{alt:>6} | {mode_name:<8} | {n_strips:>6} | {n_waypoints:>7} | "
                      f"{'N/A':>9} | {'N/A':>14} | {strip_spacing:>11.1f} | {'N/A':>12}")
                continue

            # Count pixels inside polygon that are covered
            poly_pixels = np.count_nonzero(poly_mask)
            covered_pixels = np.count_nonzero(poly_mask & cov_mask)
            uncovered_pixels = poly_pixels - covered_pixels

            if poly_pixels > 0:
                coverage_pct = (covered_pixels / poly_pixels) * 100.0
            else:
                coverage_pct = 0.0

            # Each pixel = 1m^2
            uncovered_m2 = uncovered_pixels

            # Min overlap
            min_olap = compute_min_overlap(geo, wps, alt, no_turn, search_poly_px)

            print(f"{alt:>6} | {mode_name:<8} | {n_strips:>6} | {n_waypoints:>7} | "
                  f"{coverage_pct:>8.1f}% | {uncovered_m2:>14,.0f} | {strip_spacing:>11.1f} | "
                  f"{min_olap:>11.1f}%")

    # Summary
    print(f"\n{'='*80}")
    print("Camera specs: SENSOR_WIDTH={:.2f}mm, FOCAL={:.2f}mm, IMAGE={}x{}".format(
        SENSOR_W, FOCAL, IMG_W, IMG_H))
    print(f"Overlap factor: {OVERLAP*100:.0f}%")
    print("\nFootprint at each altitude:")
    for alt in ALTITUDES:
        gw, gh = ground_footprint(alt, SENSOR_W, FOCAL, IMG_W, IMG_H)
        print(f"  {alt:>3}m: {gw:.1f}m x {gh:.1f}m (ground width x height)")


if __name__ == "__main__":
    run_simulation()
