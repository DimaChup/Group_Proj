"""
Interactive Search Pattern Visualizer
=====================================
Visualizes how the lawnmower search pattern changes with different parameters.
Uses the REAL PathPlanner from planning.py (no reimplementation).

Usage:
    python tools/pattern_visualizer.py              # default polygon from config/KML
    python tools/pattern_visualizer.py --draw       # draw custom polygon on map

Controls:
    Sliders adjust altitude, overlap, scan angle, and NFZ buffer in real time.
    LEFT-CLICK  = add polygon vertex (in --draw mode)
    RIGHT-CLICK = place drone entry point (green dot)
    P           = toggle pattern type (Lawnmower / Spiral / Zian Spiral)
    H           = toggle speed heatmap (colors segments by expected speed near NFZ)
    R           = reset polygon (enter drawing mode)
    S           = save current view to pattern_visualizer.png
    Q / ESC     = quit
"""

import sys
import os
import math
import argparse

import cv2
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon

# Add project root to path
_proj_root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

import config
from utils import GeoTransformer
from planning import PathPlanner
from geofence import NFZGeofence


# ── Constants ──────────────────────────────────────────────────────────

CANVAS_SIZE = 4800              # Same as main.py REAL_CANVAS_SIZE
MAX_DISPLAY = 1000              # max window dimension in pixels
WIN_NAME = "Search Pattern Visualizer"

# Color palette (BGR)
CLR_SCAN       = (0, 255, 0)       # green  -- scan lines
CLR_UTURN      = (0, 255, 255)     # yellow -- U-turns
CLR_NFZ        = (0, 0, 255)       # red    -- NFZ polygon
CLR_NFZ_BUF    = (0, 0, 180)       # dark red -- NFZ buffer
CLR_SEARCH     = (0, 200, 0)       # green  -- search polygon outline
CLR_SEARCH_FIL = (30, 60, 30)      # dark green -- search polygon fill
CLR_FOOTPRINT  = (200, 200, 0)     # cyan   -- camera footprint
CLR_START      = (0, 255, 0)       # green  -- start marker
CLR_END        = (0, 0, 255)       # red    -- end marker
CLR_WP         = (255, 255, 255)   # white  -- waypoint dots
CLR_FILTERED   = (0, 0, 255)       # red    -- filtered waypoints (X marks)
CLR_FOCUS      = (255, 165, 0)     # orange -- focus area
CLR_DRONE      = (0, 255, 0)       # green  -- drone entry point
CLR_TEXT       = (220, 220, 220)   # light grey
CLR_HEAT_FAST  = (0, 200, 0)      # green  -- full speed (>80% cruise)
CLR_HEAT_MED   = (0, 200, 200)    # yellow -- medium speed (40-80% cruise)
CLR_HEAT_SLOW  = (0, 0, 220)      # red    -- slow (<40% cruise or NFZ zone)

# Energy model constants (from optimize_path.py momentum theory)
HOVER_POWER_W  = 150.0    # Watts to stay airborne
DRAG_COEFF_W   = 50.0     # Watts at DRAG_REF_SPEED
DRAG_REF_SPEED = 5.0      # m/s reference
U_TURN_TIME_S  = 2.0      # seconds per U-turn
ACCEL_MPS2     = 3.0      # acceleration for momentum model (m/s^2)


# ── Helpers ────────────────────────────────────────────────────────────

def gps_distance_m(a, b):
    """Haversine-lite distance between two (lat, lon) points in metres."""
    dlat = (b[0] - a[0]) * 111320
    dlon = (b[1] - a[1]) * 111320 * math.cos(math.radians(a[0]))
    return math.sqrt(dlat * dlat + dlon * dlon)


def polygon_area_m2(gps_pts):
    """Shoelace area of a GPS polygon in square metres."""
    if len(gps_pts) < 3:
        return 0.0
    n = len(gps_pts)
    ref_lat = gps_pts[0][0]
    cos_lat = math.cos(math.radians(ref_lat))
    xs = [(p[1] - gps_pts[0][1]) * 111320 * cos_lat for p in gps_pts]
    ys = [(p[0] - gps_pts[0][0]) * 111320 for p in gps_pts]
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += xs[i] * ys[j] - xs[j] * ys[i]
    return abs(area) / 2.0


def energy_wh(distance_m, speed_mps, n_uturns):
    """Momentum theory energy estimate: hover power + drag power + U-turn penalties."""
    if speed_mps <= 0 or distance_m <= 0:
        return 0.0
    flight_time_s = distance_m / speed_mps
    # Drag power scales with v^2
    drag_power = DRAG_COEFF_W * (speed_mps / DRAG_REF_SPEED) ** 2
    total_power = HOVER_POWER_W + drag_power
    # Flight energy
    flight_energy_j = total_power * flight_time_s
    # U-turn energy (hovering during turns)
    uturn_energy_j = HOVER_POWER_W * U_TURN_TIME_S * n_uturns
    total_j = flight_energy_j + uturn_energy_j
    return total_j / 3600.0  # Joules to Wh


def coverage_area_m2(waypoints_gps, footprint_cross_m, search_poly_gps=None,
                     scan_only=True):
    """Compute unique scanned area using Shapely geometry (handles overlaps).

    For each path segment, creates a swept rectangle (segment_length x footprint_cross_m),
    unions them all (removing double-counted overlap), then clips to the search polygon.

    Args:
        waypoints_gps: list of (lat, lon) waypoints
        footprint_cross_m: cross-track footprint width in metres
        search_poly_gps: optional (lat, lon) polygon to clip coverage to
        scan_only: if True, only count scan segments (even indices: 0-1, 2-3, ...)
                   if False, count all segments (useful for spiral patterns)

    Returns:
        covered area in square metres
    """
    from shapely.ops import unary_union

    if len(waypoints_gps) < 2 or footprint_cross_m <= 0:
        return 0.0

    # Convert GPS to local metres (relative to first waypoint)
    ref_lat = waypoints_gps[0][0]
    ref_lon = waypoints_gps[0][1]
    cos_lat = math.cos(math.radians(ref_lat))

    def to_m(lat, lon):
        return ((lon - ref_lon) * 111320 * cos_lat,
                (lat - ref_lat) * 111320)

    half_w = footprint_cross_m / 2.0
    strips = []

    if scan_only:
        # Lawnmower: scan segments at even indices (0-1, 2-3, ...)
        indices = range(0, len(waypoints_gps) - 1, 2)
    else:
        # Spiral / all segments
        indices = range(len(waypoints_gps) - 1)

    for i in indices:
        ax, ay = to_m(*waypoints_gps[i])
        bx, by = to_m(*waypoints_gps[i + 1])
        dx, dy = bx - ax, by - ay
        seg_len = math.sqrt(dx * dx + dy * dy)
        if seg_len < 0.01:
            continue
        # Unit normal (perpendicular to segment direction)
        nx, ny = -dy / seg_len, dx / seg_len
        # Four corners of the swept rectangle
        corners = [
            (ax + nx * half_w, ay + ny * half_w),
            (ax - nx * half_w, ay - ny * half_w),
            (bx - nx * half_w, by - ny * half_w),
            (bx + nx * half_w, by + ny * half_w),
        ]
        rect = ShapelyPolygon(corners)
        if rect.is_valid and rect.area > 0:
            strips.append(rect)

    if not strips:
        return 0.0

    # Union all strips (removes double-counted overlaps)
    swept = unary_union(strips)

    # Clip to search polygon if provided
    if search_poly_gps and len(search_poly_gps) >= 3:
        search_m = [to_m(lat, lon) for lat, lon in search_poly_gps]
        search_shape = ShapelyPolygon(search_m)
        if not search_shape.is_valid:
            search_shape = search_shape.buffer(0)
        swept = swept.intersection(search_shape)

    return swept.area if not swept.is_empty else 0.0


# ── Zian's Perimeter Spiral Algorithm ────────────────────────────────
#
# Adapted from Zian/path_planner/perimeter_planner.py
# Progressively insets the search polygon by HALF_SWATH + k*SWATH,
# handling edge degeneration as edges collapse inward.
# CCW traversal starting from the vertex nearest the drone entry point.

def _zian_offset_line(poly_m, edge_idx, offset):
    """Inset line for edge edge_idx of a CCW polygon shifted inward by offset metres.
    Returns (point_on_line, unit_direction).
    Inward normal for CCW = (-ey, ex)."""
    n = len(poly_m)
    ax, ay = poly_m[edge_idx]
    bx, by = poly_m[(edge_idx + 1) % n]
    ex, ey = bx - ax, by - ay
    length = math.hypot(ex, ey)
    if length < 1e-12:
        return (ax, ay), (1.0, 0.0)
    ex, ey = ex / length, ey / length
    nx, ny = -ey, ex  # inward normal (CCW)
    return (ax + nx * offset, ay + ny * offset), (ex, ey)


def _zian_line_intersection(p1, d1, p2, d2):
    """Intersect lines L1 = p1+t*d1 and L2 = p2+s*d2. Returns (x, y) or None."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < 1e-12:
        return None
    t = (dx * d2[1] - dy * d2[0]) / cross
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def _zian_inset_polygon(poly_m, offset):
    """Full inset of poly_m by offset metres.
    Returns list of vertices or None if collapsed (negative area)."""
    n = len(poly_m)
    if n < 3:
        return None
    lines = [_zian_offset_line(poly_m, i, offset) for i in range(n)]
    verts = []
    for i in range(n):
        pt = _zian_line_intersection(
            lines[(i - 1) % n][0], lines[(i - 1) % n][1],
            lines[i][0], lines[i][1])
        if pt is None:
            return None
        verts.append(pt)
    # Signed area check: positive means CCW (valid)
    area2 = sum(verts[i][0] * verts[(i + 1) % n][1] -
                verts[(i + 1) % n][0] * verts[i][1] for i in range(n))
    return verts if area2 > 0 else None


def _zian_edge_length_at_offset(poly_m, edge_idx, offset):
    """Return the length of edge edge_idx when polygon is inset by offset."""
    n = len(poly_m)
    line_prev = _zian_offset_line(poly_m, (edge_idx - 1) % n, offset)
    line_cur = _zian_offset_line(poly_m, edge_idx, offset)
    line_next = _zian_offset_line(poly_m, (edge_idx + 1) % n, offset)
    p_start = _zian_line_intersection(line_prev[0], line_prev[1],
                                       line_cur[0], line_cur[1])
    p_end = _zian_line_intersection(line_cur[0], line_cur[1],
                                     line_next[0], line_next[1])
    if p_start is None or p_end is None:
        return 0.0
    return math.hypot(p_end[0] - p_start[0], p_end[1] - p_start[1])


def _zian_segments_cross(a1, a2, b1, b2, tol=1e-6):
    """True if segment a1->a2 properly crosses b1->b2 (interior intersection)."""
    def cross2(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    d1 = cross2(b1, b2, a1)
    d2 = cross2(b1, b2, a2)
    d3 = cross2(a1, a2, b1)
    d4 = cross2(a1, a2, b2)
    if ((d1 > tol and d2 < -tol) or (d1 < -tol and d2 > tol)) and \
       ((d3 > tol and d4 < -tol) or (d3 < -tol and d4 > tol)):
        return True
    return False


def generate_zian_spiral(search_poly_gps, strip_spacing_m, drone_gps=None,
                         edge_margin_m=0.0):
    """Generate Zian's perimeter spiral pattern.

    Algorithm:
    1. Convert GPS polygon to local metres
    2. Ensure CCW winding
    3. For each lap k, inset by edge_margin + HALF_SWATH + k*SWATH
       (where HALF_SWATH = strip_spacing/2, SWATH = strip_spacing)
    4. Handle edge degeneration (drop collapsed edges)
    5. Start from vertex nearest drone, traverse CCW
    6. Stop when inset collapses, crosses previous segments, or proximity limit

    Returns list of (lat, lon) waypoints.
    """
    if len(search_poly_gps) < 3 or strip_spacing_m <= 0:
        return []

    # Convert GPS to local metres (relative to centroid)
    ref_lat = sum(p[0] for p in search_poly_gps) / len(search_poly_gps)
    ref_lon = sum(p[1] for p in search_poly_gps) / len(search_poly_gps)
    cos_lat = math.cos(math.radians(ref_lat))

    def to_m(lat, lon):
        return ((lon - ref_lon) * 111320 * cos_lat,
                (lat - ref_lat) * 111320)

    def to_gps(x, y):
        return (y / 111320 + ref_lat,
                x / (111320 * cos_lat) + ref_lon)

    poly_m = [to_m(lat, lon) for lat, lon in search_poly_gps]

    # Ensure CCW winding (positive signed area)
    area2 = sum(poly_m[i][0] * poly_m[(i + 1) % len(poly_m)][1] -
                poly_m[(i + 1) % len(poly_m)][0] * poly_m[i][1]
                for i in range(len(poly_m)))
    if area2 < 0:
        poly_m = poly_m[::-1]

    half_swath = strip_spacing_m / 2.0
    swath = strip_spacing_m

    # Max radius for sanity check
    cx_m = sum(p[0] for p in poly_m) / len(poly_m)
    cy_m = sum(p[1] for p in poly_m) / len(poly_m)
    max_poly_r = max(math.hypot(p[0] - cx_m, p[1] - cy_m) for p in poly_m)

    # Find start vertex: nearest to drone entry point
    if drone_gps:
        drone_m = to_m(drone_gps[0], drone_gps[1])
    else:
        drone_m = poly_m[0]

    # Working polygon starts as the full polygon
    orig_poly = list(poly_m)
    all_lap_points = []   # list of lists of (x, y) per lap
    survey_segs = []      # accumulated survey segments for crossing check

    k = 0
    max_laps = 100  # safety limit
    while k < max_laps:
        offset = edge_margin_m + half_swath + k * swath

        # Try to inset the current working polygon
        inset = _zian_inset_polygon(orig_poly, offset)
        if inset is None:
            break

        # Sanity: reject if any vertex is far beyond original polygon
        if any(math.hypot(v[0] - cx_m, v[1] - cy_m) > max_poly_r * 1.5
               for v in inset):
            break

        # Edge degeneration: check which edges survive at this offset
        n = len(orig_poly)
        surviving = []
        for i in range(n):
            edge_len = _zian_edge_length_at_offset(orig_poly, i, offset)
            if edge_len > 0.01:  # threshold for edge survival
                surviving.append(i)

        if len(surviving) < 3:
            break

        # If some edges collapsed, rebuild reduced polygon and re-inset
        if len(surviving) < n:
            # Keep only vertices where both adjacent edges survive
            surviving_verts = []
            for v in range(n):
                if (v - 1) % n in surviving and v in surviving:
                    surviving_verts.append(v)
            if len(surviving_verts) < 3:
                break
            # Never reduce below quad (4 vertices) — triangle insets are unstable
            if len(surviving_verts) < 4:
                break
            reduced = [orig_poly[v] for v in surviving_verts]
            inset = _zian_inset_polygon(reduced, offset)
            if inset is None:
                break
            # Update working polygon for future laps
            orig_poly = reduced

        # Rotate vertices so the first is nearest to drone (or last lap's end)
        if all_lap_points:
            ref_pt = all_lap_points[-1][-1]
        else:
            ref_pt = drone_m

        best_j = 0
        best_d = float('inf')
        for j, v in enumerate(inset):
            d = (v[0] - ref_pt[0]) ** 2 + (v[1] - ref_pt[1]) ** 2
            if d < best_d:
                best_d = d
                best_j = j
        # Rotate to start from best_j
        lap_pts = inset[best_j:] + inset[:best_j]
        # Close the loop back to the start
        lap_pts.append(lap_pts[0])

        # Crossing check: does any new segment cross a previous survey segment?
        crossing = False
        new_segs = []
        for i in range(len(lap_pts) - 1):
            seg = (lap_pts[i], lap_pts[i + 1])
            for prev_seg in survey_segs:
                if _zian_segments_cross(seg[0], seg[1], prev_seg[0], prev_seg[1]):
                    crossing = True
                    break
            if crossing:
                break
            new_segs.append(seg)

        if crossing:
            break

        # Commit this lap
        survey_segs.extend(new_segs)
        all_lap_points.append(lap_pts)

        k += 1

    # Flatten all laps into a single waypoint list
    waypoints_m = []
    for lap_pts in all_lap_points:
        for pt in lap_pts:
            # Deduplicate consecutive points
            if waypoints_m and math.hypot(pt[0] - waypoints_m[-1][0],
                                           pt[1] - waypoints_m[-1][1]) < 0.01:
                continue
            waypoints_m.append(pt)

    # Add centroid as final waypoint (like Zian's algorithm)
    if waypoints_m:
        waypoints_m.append((cx_m, cy_m))

    # Convert back to GPS
    return [to_gps(x, y) for x, y in waypoints_m]


# ── Main Visualizer ──────────────────────────────────────────────────

class PatternVisualizer:
    def __init__(self, map_path, draw_mode=False):
        self.draw_mode = draw_mode

        # Load KML zones
        kml_path = os.path.join(_proj_root, "flight_plans", "AENGM0074.kml")
        config.load_kml_zones(kml_path)

        # Load map image
        self.map_orig = cv2.imread(map_path)
        if self.map_orig is None:
            print(f"[ERROR] Cannot load map: {map_path}")
            sys.exit(1)
        self.map_h, self.map_w = self.map_orig.shape[:2]
        print(f"Map loaded: {self.map_w}x{self.map_h}")

        # Display scaling
        self.disp_scale = min(MAX_DISPLAY / self.map_w, MAX_DISPLAY / self.map_h, 1.0)
        self.disp_w = int(self.map_w * self.disp_scale)
        self.disp_h = int(self.map_h * self.disp_scale)
        self.map_disp = cv2.resize(self.map_orig, (self.disp_w, self.disp_h))

        # GeoTransformers: one at CANVAS_SIZE for pattern generation,
        # one at display size for rendering
        self.geo_canvas = GeoTransformer(map_w_px=CANVAS_SIZE)
        self.geo_disp = GeoTransformer(map_w_px=self.disp_w)

        # Search polygon stored as GPS coords (source of truth)
        self.search_poly_gps = []
        self.polygon_closed = False

        # Drone entry point (GPS). Default = TAKEOFF_GPS
        self.drone_gps = config.TAKEOFF_GPS

        if not draw_mode:
            self.search_poly_gps = list(config.SEARCH_AREA_GPS)
            self.polygon_closed = True

        # Slider state
        self.altitude = int(config.TARGET_ALT)
        self.overlap_pct = 20       # percent (0 = _no_turn mode like main.py)
        self.scan_angle = 181       # 181 = auto
        self.nfz_buffer = int(config.NFZ_WAYPOINT_BUFFER_M)

        # Pattern type: "lawnmower", "spiral", or "zian_spiral"
        self.pattern_type = "lawnmower"
        self._pattern_types = ["lawnmower", "spiral", "zian_spiral"]

        # Speed heatmap toggle (H key)
        self.show_heatmap = False

        # Cached results
        self._cached_key = None
        self._cached_waypoints = []
        self._cached_filtered_wps = []  # waypoints removed by NFZ
        self._cached_stats = {}

    def _gps_to_disp(self, lat, lon):
        """Convert GPS to display pixel coords."""
        x, y = self.geo_disp.gps_to_pixels(lat, lon)
        return (int(x), int(y))

    def _gps_poly_to_disp(self, gps_pts):
        """Convert GPS polygon to display pixel coords."""
        return [self._gps_to_disp(p[0], p[1]) for p in gps_pts]

    def _generate_pattern(self):
        """Generate pattern using the REAL PathPlanner at CANVAS_SIZE."""
        cache_key = (
            tuple(self.search_poly_gps), self.altitude, self.overlap_pct,
            self.scan_angle, self.nfz_buffer,
            self.drone_gps[0], self.drone_gps[1],
            self.pattern_type,
        )
        if cache_key == self._cached_key:
            return self._cached_waypoints

        if len(self.search_poly_gps) < 3:
            self._cached_waypoints = []
            self._cached_filtered_wps = []
            self._cached_stats = {}
            self._cached_key = cache_key
            return []

        # Convert GPS polygon to pixel coords at CANVAS_SIZE
        canvas_poly_px = []
        for lat, lon in self.search_poly_gps:
            px = self.geo_canvas.gps_to_pixels(lat, lon)
            canvas_poly_px.append((int(px[0]), int(px[1])))

        # Build planner with canvas-sized geo transformer
        planner = PathPlanner(self.geo_canvas, canvas_poly_px)

        # Set overlap behavior:
        # overlap_pct == 0  =>  _no_turn = True  (matches main.py default)
        # overlap_pct > 0   =>  _no_turn = False, but we need to inject
        #                       the custom overlap into the planner
        if self.overlap_pct == 0:
            planner._no_turn = True
        else:
            planner._no_turn = False

        # Handle custom scan angle by temporarily patching the planner
        alt = float(self.altitude)
        custom_overlap = self.overlap_pct / 100.0
        custom_angle = None if self.scan_angle > 180 else float(self.scan_angle)

        # We need to intercept the overlap value used inside
        # generate_search_pattern. The planner hardcodes 0.2 overlap when
        # _no_turn is False. We monkey-patch a wrapper to fix this.
        orig_method = planner.generate_search_pattern

        viz = self  # capture for closure

        def _patched_generate(map_w, map_h, drone_gps=None, alt_override=None):
            """Wrapper that fixes overlap and scan angle."""
            if len(planner.search_polygon) < 3:
                return []
            search_alt = alt_override or alt

            # 1. Rasterise
            mask = np.zeros((map_h, map_w), dtype=np.uint8)
            poly_pts = np.array([planner.search_polygon], dtype=np.int32)
            cv2.fillPoly(mask, poly_pts, 255)
            planner.virtual_polygon = poly_pts.reshape(-1, 1, 2)

            # 2. Rotation
            rect = cv2.minAreaRect(poly_pts[0])
            (center, size, angle) = rect
            if custom_angle is not None:
                s_angle = custom_angle
            else:
                s_angle = angle + 90 if size[0] < size[1] else angle
            planner.last_scan_angle = s_angle

            rotation_mat = cv2.getRotationMatrix2D(center, s_angle, 1.0)
            inverse_rotation = cv2.invertAffineTransform(rotation_mat)
            rotated_mask = cv2.warpAffine(mask, rotation_mat, (map_w, map_h))

            # 3. Strip spacing
            ground_footprint_m = (config.SENSOR_WIDTH_MM * search_alt) / config.FOCAL_LENGTH_MM
            if planner._no_turn:
                aspect = config.IMAGE_H / config.IMAGE_W
                ground_footprint_m = ground_footprint_m * aspect
                effective_overlap = 0.0
            else:
                effective_overlap = custom_overlap
            swath_m = ground_footprint_m * (1.0 - effective_overlap)
            strip_spacing_px = max(1, int(swath_m * planner.pix_per_m))

            points = cv2.findNonZero(rotated_mask)
            if points is None:
                return []
            bbox_x, bbox_y, bbox_w, bbox_h = cv2.boundingRect(points)

            # 3b. Single-flyover check
            bbox_w_m = bbox_w / planner.pix_per_m if planner.pix_per_m else bbox_w
            bbox_h_m = bbox_h / planner.pix_per_m if planner.pix_per_m else bbox_h
            if bbox_w_m <= ground_footprint_m and bbox_h_m <= ground_footprint_m:
                cx = bbox_x + bbox_w // 2
                cy = bbox_y + bbox_h // 2
                pt = np.array([[(cx, cy)]], dtype=np.float32)
                pt_orig = cv2.transform(pt, inverse_rotation)[0][0]
                return [planner.geo.pixels_to_gps(pt_orig[0], pt_orig[1])]

            # 4. Scan lines
            all_strips = []
            # Edge margin slider controls how far waypoints are from polygon edges
            inset_px = max(1, int(self.nfz_buffer * planner.pix_per_m)) if self.nfz_buffer > 0 else strip_spacing_px // 3
            bottom_limit = bbox_y + bbox_h - inset_px
            prev_scan_y = -999

            scan_lines = list(range(bbox_y + inset_px, bbox_y + bbox_h, strip_spacing_px))
            if not scan_lines or scan_lines[-1] < bottom_limit:
                scan_lines.append(bottom_limit)

            for scan_y in scan_lines:
                scan_y = min(scan_y, bottom_limit)
                if scan_y == prev_scan_y:
                    continue
                prev_scan_y = scan_y
                row = rotated_mask[scan_y, :]
                filled_cols = np.where(row == 255)[0]
                if len(filled_cols) > 0:
                    x_start = filled_cols[0] + inset_px
                    x_end = filled_cols[-1] - inset_px
                    if x_end > x_start:
                        all_strips.append([(x_start, scan_y), (x_end, scan_y)])
                    else:
                        x_mid = (filled_cols[0] + filled_cols[-1]) // 2
                        all_strips.append([(x_mid, scan_y), (x_mid, scan_y)])

            # 5. Start corner closest to drone
            direction = 1
            if drone_gps and all_strips:
                drone_px = planner.geo.gps_to_pixels(drone_gps[0], drone_gps[1])

                def _sq_dist_to_map(rotated_pt):
                    pt_arr = np.array([[rotated_pt]], dtype=np.float32)
                    map_pt = cv2.transform(pt_arr, inverse_rotation)[0][0]
                    return (map_pt[0] - drone_px[0]) ** 2 + (map_pt[1] - drone_px[1]) ** 2

                first_strip = all_strips[0]
                last_strip = all_strips[-1]
                d_top_left = _sq_dist_to_map(first_strip[0])
                d_top_right = _sq_dist_to_map(first_strip[1])
                d_bot_left = _sq_dist_to_map(last_strip[0])
                d_bot_right = _sq_dist_to_map(last_strip[1])
                min_dist = min(d_top_left, d_top_right, d_bot_left, d_bot_right)

                if min_dist == d_bot_left or min_dist == d_bot_right:
                    all_strips.reverse()
                    d_left = _sq_dist_to_map(all_strips[0][0])
                    d_right = _sq_dist_to_map(all_strips[0][1])
                else:
                    d_left = d_top_left
                    d_right = d_top_right
                if d_right < d_left:
                    direction = -1

            # 6. Un-rotate and convert to GPS
            waypoints = []
            for strip in all_strips:
                if direction == -1:
                    pt_start, pt_end = strip[1], strip[0]
                else:
                    pt_start, pt_end = strip[0], strip[1]
                pts_rot = np.array([[pt_start, pt_end]], dtype=np.float32)
                pts_orig = cv2.transform(pts_rot, inverse_rotation)[0]
                waypoints.append(planner.geo.pixels_to_gps(pts_orig[0][0], pts_orig[0][1]))
                waypoints.append(planner.geo.pixels_to_gps(pts_orig[1][0], pts_orig[1][1]))
                direction *= -1

            # 7. Dedup
            if len(waypoints) >= 2:
                deduped = [waypoints[0]]
                for wp in waypoints[1:]:
                    if abs(wp[0] - deduped[-1][0]) > 1e-9 or abs(wp[1] - deduped[-1][1]) > 1e-9:
                        deduped.append(wp)
                waypoints = deduped

            return waypoints

        # Choose pattern generator based on pattern type
        if self.pattern_type == "zian_spiral":
            # Zian's perimeter spiral: progressive polygon inset with degeneration
            ground_footprint_m = (config.SENSOR_WIDTH_MM * alt) / config.FOCAL_LENGTH_MM
            strip_spacing_m = ground_footprint_m * (1.0 - custom_overlap)
            if strip_spacing_m <= 0:
                strip_spacing_m = ground_footprint_m * 0.8
            edge_margin = float(self.nfz_buffer)
            waypoints = generate_zian_spiral(
                self.search_poly_gps,
                strip_spacing_m,
                drone_gps=self.drone_gps,
                edge_margin_m=edge_margin,
            )
        elif self.pattern_type == "spiral":
            # Shapely-based polygon-following spiral
            # 1. Compute strip spacing in metres (same formula as lawnmower)
            ground_footprint_m = (config.SENSOR_WIDTH_MM * alt) / config.FOCAL_LENGTH_MM
            strip_spacing_m = ground_footprint_m * (1.0 - custom_overlap)
            if strip_spacing_m <= 0:
                strip_spacing_m = ground_footprint_m * 0.8

            # 2. Convert search polygon GPS to metres relative to centroid
            ref_lat = sum(p[0] for p in self.search_poly_gps) / len(self.search_poly_gps)
            ref_lon = sum(p[1] for p in self.search_poly_gps) / len(self.search_poly_gps)
            cos_lat = math.cos(math.radians(ref_lat))
            poly_m = [((lon - ref_lon) * 111320 * cos_lat, (lat - ref_lat) * 111320)
                       for lat, lon in self.search_poly_gps]
            shape_poly = ShapelyPolygon(poly_m)
            if not shape_poly.is_valid:
                shape_poly = shape_poly.buffer(0)

            # 3. Generate concentric inset rings
            #    First ring starts at edge_margin metres inside the polygon,
            #    each subsequent ring is strip_spacing_m deeper.
            spiral_waypoints = []
            edge_margin = max(float(self.nfz_buffer), strip_spacing_m * 0.5)
            offset = edge_margin
            all_rings = []
            while True:
                inset = shape_poly.buffer(-offset, join_style='mitre', mitre_limit=5.0)
                if inset.is_empty or inset.area < strip_spacing_m ** 2:
                    break
                if inset.geom_type == 'Polygon':
                    coords = list(inset.exterior.coords)
                elif inset.geom_type == 'MultiPolygon':
                    # Use the largest polygon fragment
                    largest = max(inset.geoms, key=lambda g: g.area)
                    coords = list(largest.exterior.coords)
                else:
                    break
                all_rings.append(coords)
                offset += strip_spacing_m

            # 4. Simplify each ring to essential corners only, then
            #    connect rings inward: Ring1 corners -> Ring2 corners -> ... -> center
            simplified_rings = []
            for coords in all_rings:
                ring_poly = ShapelyPolygon(coords)
                # Simplify to remove redundant points along edges, keep corners
                simplified = ring_poly.simplify(strip_spacing_m * 0.1, preserve_topology=True)
                if simplified.is_empty or simplified.geom_type != 'Polygon':
                    continue
                # Get corner vertices (drop closing duplicate)
                verts = list(simplified.exterior.coords)[:-1]
                if len(verts) >= 3:
                    simplified_rings.append(verts)

            # 5. For each ring, rotate its vertices so the first vertex is
            #    closest to the last vertex of the previous ring (smooth connection)
            for ring_idx, verts in enumerate(simplified_rings):
                if ring_idx == 0 and self.drone_gps:
                    # First ring: start from corner nearest drone entry
                    drone_m = ((self.drone_gps[1] - ref_lon) * 111320 * cos_lat,
                               (self.drone_gps[0] - ref_lat) * 111320)
                    ref_pt = drone_m
                elif ring_idx > 0 and simplified_rings[ring_idx - 1]:
                    ref_pt = simplified_rings[ring_idx - 1][-1]
                else:
                    continue
                # Find closest vertex to ref_pt
                best_j = 0
                best_d = float('inf')
                for j, v in enumerate(verts):
                    dx = v[0] - ref_pt[0]
                    dy = v[1] - ref_pt[1]
                    d = dx * dx + dy * dy
                    if d < best_d:
                        best_d = d
                        best_j = j
                simplified_rings[ring_idx] = verts[best_j:] + verts[:best_j]

            # 6. Build spiral waypoints: all corners of each ring, inward
            for verts in simplified_rings:
                for v in verts:
                    gps_lat = v[1] / 111320 + ref_lat
                    gps_lon = v[0] / (111320 * cos_lat) + ref_lon
                    spiral_waypoints.append((gps_lat, gps_lon))

            # 7. Add center point as final waypoint
            centroid = shape_poly.centroid
            if not centroid.is_empty:
                center_lat = centroid.y / 111320 + ref_lat
                center_lon = centroid.x / (111320 * cos_lat) + ref_lon
                spiral_waypoints.append((center_lat, center_lon))

            waypoints = spiral_waypoints
        elif self.overlap_pct == 0 and self.scan_angle > 180:
            # Default lawnmower behavior matches main.py exactly
            waypoints = planner.generate_search_pattern(
                CANVAS_SIZE, CANVAS_SIZE,
                drone_gps=self.drone_gps,
                alt_override=alt,
            )
        else:
            # Custom overlap or angle: use patched lawnmower version
            waypoints = _patched_generate(
                CANVAS_SIZE, CANVAS_SIZE,
                drone_gps=self.drone_gps,
                alt_override=alt,
            )

        # No waypoint filtering — edge margin slider pushes waypoints back from edges
        # (handled by inset_px in the pattern generation above)
        self._cached_waypoints = waypoints
        self._cached_filtered_wps = []
        self._cached_key = cache_key

        # Compute stats
        if waypoints:
            total_dist = sum(gps_distance_m(waypoints[i], waypoints[i + 1])
                             for i in range(len(waypoints) - 1))
            speed = config.speed_for_altitude(alt)
            search_time = total_dist / speed if speed > 0 else 0

            # Transit from drone entry point
            transit_dist = gps_distance_m(self.drone_gps, waypoints[0])
            transit_time = transit_dist / config.TRANSIT_SPEED_MPS if config.TRANSIT_SPEED_MPS > 0 else 0
            total_time = search_time + 2 * transit_time  # out + back

            # Footprint
            ground_fp_w = (config.SENSOR_WIDTH_MM * alt) / config.FOCAL_LENGTH_MM
            ground_fp_h = ground_fp_w * config.IMAGE_H / config.IMAGE_W

            # Coverage — Shapely-based (handles overlaps correctly)
            search_area = polygon_area_m2(self.search_poly_gps)
            if self.pattern_type in ("spiral", "zian_spiral"):
                # Spiral: all segments are scan segments
                covered = coverage_area_m2(waypoints, ground_fp_w,
                                           search_poly_gps=self.search_poly_gps,
                                           scan_only=False)
            else:
                # Lawnmower: cross-track footprint depends on yaw mode
                # _no_turn=True (overlap==0): drone doesn't yaw, narrow dim is cross-track
                # _no_turn=False (overlap>0): drone yaws, full sensor width is cross-track
                if self.overlap_pct == 0:
                    cross_track = ground_fp_h   # narrow (IMAGE_H based)
                else:
                    cross_track = ground_fp_w   # wide (full sensor)
                covered = coverage_area_m2(waypoints, cross_track,
                                           search_poly_gps=self.search_poly_gps,
                                           scan_only=True)
            coverage_pct = min(100.0, (covered / search_area * 100)) if search_area > 0 else 0

            # Energy (momentum theory model)
            if self.pattern_type in ("spiral", "zian_spiral"):
                n_strips = len(waypoints)
                n_uturns = 0  # spiral has no U-turns
            else:
                n_strips = len(waypoints) // 2
                n_uturns = max(0, n_strips - 1)
            total_energy = energy_wh(total_dist + 2 * transit_dist, speed, n_uturns)

            scan_angle_val = getattr(planner, 'last_scan_angle', None)

            self._cached_stats = {
                "n_wp": len(waypoints),
                "n_strips": n_strips,
                "n_filtered": 0,
                "total_dist_m": total_dist,
                "transit_dist_m": transit_dist,
                "search_time_s": search_time,
                "total_time_s": total_time,
                "speed_mps": speed,
                "coverage_pct": coverage_pct,
                "search_area_m2": search_area,
                "energy_wh": total_energy,
                "footprint_w": ground_fp_w,
                "footprint_h": ground_fp_h,
                "scan_angle": scan_angle_val,
            }
        else:
            self._cached_stats = {}

        return waypoints

    def _compute_continuous_speeds(self, waypoints):
        """Compute speed at sub-segment resolution along the entire path.

        Subdivides every segment into ~2m sub-segments. For each sub-segment
        midpoint, computes the NFZ scalar-field target speed. Then applies a
        continuous momentum model (acceleration/deceleration at ACCEL_MPS2)
        along the whole path so speed ramps smoothly.

        At U-turns (odd-indexed segments in lawnmower mode), the drone
        decelerates to ~1 m/s then accelerates back.

        Returns a list of dicts, one per sub-segment:
            {
                "lat1", "lon1", "lat2", "lon2":  GPS endpoints,
                "px1", "px2":  display pixel endpoints (int tuples),
                "speed":       actual speed after momentum (m/s),
                "target":      target speed from scalar field (m/s),
                "in_nfz":      bool — inside NFZ slow zone,
                "dist_m":      sub-segment length (m),
                "seg_idx":     index of the parent segment,
            }
        """
        SUB_SEG_M = 2.0   # target sub-segment length in metres
        U_TURN_SPEED = 1.0  # speed at U-turn apex

        if len(waypoints) < 2:
            return []

        alt = float(self.altitude)
        cruise_speed = config.speed_for_altitude(alt)

        # Build geofence for distance queries
        geofence = NFZGeofence(self.geo_canvas)
        has_nfz = bool(config.SSSI_GPS) and len(config.SSSI_GPS) >= 3

        # --- Pass 1: build all sub-segments with their TARGET speeds ---
        all_subs = []
        for seg_idx in range(len(waypoints) - 1):
            wp_a = waypoints[seg_idx]
            wp_b = waypoints[seg_idx + 1]
            seg_len = gps_distance_m(wp_a, wp_b)

            # Is this a U-turn segment? (odd index in lawnmower mode)
            is_uturn = (self.pattern_type not in ("spiral", "zian_spiral") and seg_idx % 2 == 1)

            # How many sub-segments?
            n_sub = max(1, int(math.ceil(seg_len / SUB_SEG_M)))
            for k in range(n_sub):
                t0 = k / n_sub
                t1 = (k + 1) / n_sub
                t_mid = (t0 + t1) / 2.0

                lat1 = wp_a[0] + (wp_b[0] - wp_a[0]) * t0
                lon1 = wp_a[1] + (wp_b[1] - wp_a[1]) * t0
                lat2 = wp_a[0] + (wp_b[0] - wp_a[0]) * t1
                lon2 = wp_a[1] + (wp_b[1] - wp_a[1]) * t1
                mid_lat = wp_a[0] + (wp_b[0] - wp_a[0]) * t_mid
                mid_lon = wp_a[1] + (wp_b[1] - wp_a[1]) * t_mid

                sub_dist = seg_len / n_sub  # uniform subdivision

                # Target speed from NFZ scalar field
                target = cruise_speed
                in_nfz = False

                if has_nfz:
                    dist_m, is_inside = geofence.distance_to_boundary(mid_lat, mid_lon)
                    if is_inside or dist_m <= config.NFZ_SCALAR_ZERO_M:
                        target = config.NFZ_MIN_SPEED_MPS
                        in_nfz = True
                    elif dist_m < config.NFZ_SLOW_ZONE_M:
                        ratio = (dist_m - config.NFZ_SCALAR_ZERO_M) / (
                            config.NFZ_SLOW_ZONE_M - config.NFZ_SCALAR_ZERO_M)
                        target = min(ratio * config.NFZ_ZONE_MAX_SPEED_MPS, cruise_speed)
                        in_nfz = True

                # U-turn override: target speed drops to U_TURN_SPEED
                if is_uturn:
                    target = min(target, U_TURN_SPEED)

                px1 = self._gps_to_disp(lat1, lon1)
                px2 = self._gps_to_disp(lat2, lon2)

                all_subs.append({
                    "lat1": lat1, "lon1": lon1,
                    "lat2": lat2, "lon2": lon2,
                    "px1": px1, "px2": px2,
                    "target": target,
                    "in_nfz": in_nfz,
                    "dist_m": sub_dist,
                    "seg_idx": seg_idx,
                    "speed": 0.0,  # filled in pass 2
                })

        if not all_subs:
            return all_subs

        # --- Pass 2: forward pass — apply acceleration/deceleration momentum ---
        cur_speed = 0.0  # start from rest
        for sub in all_subs:
            target = sub["target"]
            d = sub["dist_m"]
            if d < 0.001:
                sub["speed"] = target
                cur_speed = target
                continue

            if cur_speed < target:
                # Accelerating: v^2 = v0^2 + 2*a*d
                v_new = math.sqrt(cur_speed ** 2 + 2.0 * ACCEL_MPS2 * d)
                cur_speed = min(v_new, target)
            elif cur_speed > target:
                # Decelerating: v^2 = v0^2 - 2*a*d
                v_sq = cur_speed ** 2 - 2.0 * ACCEL_MPS2 * d
                cur_speed = max(math.sqrt(max(v_sq, 0.0)), target)
            else:
                cur_speed = target
            sub["speed"] = cur_speed

        # --- Pass 3: backward pass — ensure drone can decelerate in time ---
        # Walk backwards: if a future sub-segment requires a lower speed,
        # the drone must start slowing down earlier.
        cur_speed = all_subs[-1]["speed"]
        for sub in reversed(all_subs):
            target = sub["target"]
            d = sub["dist_m"]
            # The speed here can't be so high that the drone can't slow
            # to the NEXT sub-segment's speed in time.
            if cur_speed < sub["speed"]:
                # Need to be slower here to decelerate to cur_speed ahead
                v_sq = cur_speed ** 2 + 2.0 * ACCEL_MPS2 * d
                max_here = math.sqrt(max(v_sq, 0.0))
                sub["speed"] = min(sub["speed"], max_here)
            cur_speed = sub["speed"]

        return all_subs

    def _speed_to_color(self, speed, cruise_speed):
        """Map speed to BGR color: smooth green-yellow-red gradient.

        ratio 1.0  -> pure green  (0, 220, 0)
        ratio 0.5  -> yellow      (0, 220, 220)
        ratio 0.0  -> red         (0, 0, 220)
        """
        if cruise_speed <= 0:
            return CLR_HEAT_SLOW
        ratio = max(0.0, min(1.0, speed / cruise_speed))
        if ratio >= 0.5:
            # green to yellow: green channel stays high, red ramps up as ratio drops
            t = (ratio - 0.5) / 0.5   # 1 at ratio=1, 0 at ratio=0.5
            r = int(220 * (1.0 - t))   # 0 at full speed, 220 at half
            g = 220
        else:
            # yellow to red: red stays high, green drops
            t = ratio / 0.5           # 1 at ratio=0.5, 0 at ratio=0
            r = 220
            g = int(220 * t)           # 220 at half, 0 at zero
        return (0, g, r)

    def _draw(self):
        """Render the current state to a display image."""
        vis = self.map_disp.copy()
        alt = float(self.altitude)

        # ── SSSI polygon (NFZ) ──
        if config.SSSI_GPS and len(config.SSSI_GPS) >= 3:
            sssi_px = self._gps_poly_to_disp(config.SSSI_GPS)
            sssi_arr = np.array(sssi_px, np.int32)

            # NFZ buffer zone visualization (fixed to config value, NOT affected by Edge Margin slider)
            nfz_vis_buffer = config.NFZ_WAYPOINT_BUFFER_M
            if nfz_vis_buffer > 0:
                # Draw a buffer around the SSSI using centroid expansion (visual only)
                buf_gps = _offset_polygon_centroid(config.SSSI_GPS, nfz_vis_buffer)
                buf_px = self._gps_poly_to_disp(buf_gps)
                buf_arr = np.array(buf_px, np.int32)
                overlay = vis.copy()
                cv2.fillPoly(overlay, [buf_arr], (0, 0, 80))
                cv2.addWeighted(overlay, 0.3, vis, 0.7, 0, vis)
                cv2.polylines(vis, [buf_arr], True, CLR_NFZ_BUF, 1, cv2.LINE_AA)

            # SSSI fill
            overlay = vis.copy()
            cv2.fillPoly(overlay, [sssi_arr], (0, 0, 120))
            cv2.addWeighted(overlay, 0.35, vis, 0.65, 0, vis)
            cv2.polylines(vis, [sssi_arr], True, CLR_NFZ, 2, cv2.LINE_AA)

            # Label
            cx = sum(p[0] for p in sssi_px) // len(sssi_px)
            cy = sum(p[1] for p in sssi_px) // len(sssi_px)
            cv2.putText(vis, "SSSI NFZ", (cx - 30, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, CLR_NFZ, 1, cv2.LINE_AA)

        # ── Focus area ──
        if config.FOCUS_AREA_GPS and len(config.FOCUS_AREA_GPS) >= 3:
            foc_px = self._gps_poly_to_disp(config.FOCUS_AREA_GPS)
            foc_arr = np.array(foc_px, np.int32)
            cv2.polylines(vis, [foc_arr], True, CLR_FOCUS, 1, cv2.LINE_AA)

        # ── Search polygon ──
        if len(self.search_poly_gps) >= 3 and self.polygon_closed:
            poly_px = self._gps_poly_to_disp(self.search_poly_gps)
            poly_arr = np.array(poly_px, np.int32)
            overlay = vis.copy()
            cv2.fillPoly(overlay, [poly_arr], CLR_SEARCH_FIL)
            cv2.addWeighted(overlay, 0.4, vis, 0.6, 0, vis)
            cv2.polylines(vis, [poly_arr], True, CLR_SEARCH, 2, cv2.LINE_AA)

        # ── Drawing mode: show vertices being placed ──
        if not self.polygon_closed:
            for i, gps_pt in enumerate(self.search_poly_gps):
                pt = self._gps_to_disp(gps_pt[0], gps_pt[1])
                cv2.circle(vis, pt, 5, CLR_SEARCH, -1)
                if i > 0:
                    prev = self._gps_to_disp(self.search_poly_gps[i - 1][0],
                                             self.search_poly_gps[i - 1][1])
                    cv2.line(vis, prev, pt, CLR_SEARCH, 2)
            msg = f"Vertices: {len(self.search_poly_gps)} | LEFT-CLICK=add, RIGHT-CLICK=close/set drone"
            cv2.putText(vis, msg, (10, self.disp_h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, CLR_TEXT, 1, cv2.LINE_AA)
            return vis

        # ── Generate and draw pattern ──
        waypoints = self._generate_pattern()

        # Draw filtered waypoints as red X marks
        for wp in self._cached_filtered_wps:
            px = self._gps_to_disp(wp[0], wp[1])
            sz = 5
            cv2.line(vis, (px[0] - sz, px[1] - sz), (px[0] + sz, px[1] + sz), CLR_FILTERED, 2)
            cv2.line(vis, (px[0] + sz, px[1] - sz), (px[0] - sz, px[1] + sz), CLR_FILTERED, 2)

        if not waypoints:
            cv2.putText(vis, "No waypoints (polygon too small or all filtered by NFZ)",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            return vis

        wp_px = [self._gps_to_disp(w[0], w[1]) for w in waypoints]

        # Compute sub-segment speeds if heatmap is enabled
        sub_segs = None
        if self.show_heatmap:
            sub_segs = self._compute_continuous_speeds(waypoints)
            cruise_speed = config.speed_for_altitude(float(self.altitude))

        # Draw path segments
        if self.show_heatmap and sub_segs:
            # Draw each sub-segment with its own color
            for sub in sub_segs:
                color = self._speed_to_color(sub["speed"], cruise_speed)
                cv2.line(vis, sub["px1"], sub["px2"], color, 2, cv2.LINE_AA)
        else:
            for i in range(len(wp_px) - 1):
                if self.pattern_type in ("spiral", "zian_spiral"):
                    cv2.line(vis, wp_px[i], wp_px[i + 1], CLR_SCAN, 2, cv2.LINE_AA)
                elif i % 2 == 0:
                    cv2.line(vis, wp_px[i], wp_px[i + 1], CLR_SCAN, 2, cv2.LINE_AA)
                else:
                    cv2.line(vis, wp_px[i], wp_px[i + 1], CLR_UTURN, 1, cv2.LINE_AA)

        # Draw waypoint dots and numbers
        # Spiral has many more waypoints — label less frequently
        label_every = 20 if self.pattern_type in ("spiral", "zian_spiral") else 4
        for i, pt in enumerate(wp_px):
            cv2.circle(vis, pt, 3, CLR_WP, -1)
            if i % label_every == 0 or i == 0 or i == len(wp_px) - 1:
                cv2.putText(vis, str(i + 1), (pt[0] + 5, pt[1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.28, CLR_WP, 1, cv2.LINE_AA)

        # Start / end markers
        cv2.circle(vis, wp_px[0], 8, CLR_START, 2, cv2.LINE_AA)
        cv2.putText(vis, "START", (wp_px[0][0] + 10, wp_px[0][1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, CLR_START, 1, cv2.LINE_AA)
        cv2.circle(vis, wp_px[-1], 8, CLR_END, 2, cv2.LINE_AA)
        cv2.putText(vis, "END", (wp_px[-1][0] + 10, wp_px[-1][1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, CLR_END, 1, cv2.LINE_AA)

        # Drone entry point marker
        drone_px = self._gps_to_disp(self.drone_gps[0], self.drone_gps[1])
        cv2.drawMarker(vis, drone_px, CLR_DRONE, cv2.MARKER_DIAMOND, 14, 2)
        cv2.putText(vis, "DRONE", (drone_px[0] + 10, drone_px[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, CLR_DRONE, 1, cv2.LINE_AA)

        # Takeoff marker (if different from drone entry)
        toff_px = self._gps_to_disp(*config.TAKEOFF_GPS)
        if abs(self.drone_gps[0] - config.TAKEOFF_GPS[0]) > 1e-7 or \
           abs(self.drone_gps[1] - config.TAKEOFF_GPS[1]) > 1e-7:
            cv2.drawMarker(vis, toff_px, (0, 255, 255), cv2.MARKER_DIAMOND, 12, 2)
            cv2.putText(vis, "TOL", (toff_px[0] + 8, toff_px[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1, cv2.LINE_AA)

        # ── Camera footprint rectangle at first waypoint ──
        stats = self._cached_stats
        if stats:
            fp_w_px = int(stats["footprint_w"] * self.geo_disp.pix_per_m)
            fp_h_px = int(stats["footprint_h"] * self.geo_disp.pix_per_m)
            fp_cx, fp_cy = wp_px[0]
            tl = (fp_cx - fp_w_px // 2, fp_cy - fp_h_px // 2)
            br = (fp_cx + fp_w_px // 2, fp_cy + fp_h_px // 2)
            cv2.rectangle(vis, tl, br, CLR_FOOTPRINT, 1, cv2.LINE_AA)
            cv2.putText(vis, f"footprint {stats['footprint_w']:.1f}x{stats['footprint_h']:.1f}m",
                        (tl[0], tl[1] - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.28, CLR_FOOTPRINT, 1)

        # ── Stats panel ──
        if stats:
            angle_str = "auto" if self.scan_angle > 180 else f"{self.scan_angle} deg"
            if stats.get("scan_angle") is not None:
                angle_str += f" ({stats['scan_angle']:.1f})"

            pat_labels = {"lawnmower": "Lawnmower", "spiral": "Spiral", "zian_spiral": "Zian Spiral"}
            pat_label = pat_labels.get(self.pattern_type, self.pattern_type)
            lines = [
                f"Pattern: {pat_label}   (P to toggle)",
                f"Altitude: {self.altitude}m   Speed: {stats['speed_mps']:.1f} m/s",
                f"Waypoints: {stats['n_wp']}   {'Points' if self.pattern_type in ('spiral', 'zian_spiral') else 'Strips'}: {stats['n_strips']}",
                f"NFZ filtered: {stats['n_filtered']}",
                f"Search dist: {stats['total_dist_m']:.0f}m   Transit: {stats['transit_dist_m']:.0f}m",
                f"Search time: {stats['search_time_s']:.0f}s ({stats['search_time_s']/60:.1f}min)",
                f"Total time:  {stats['total_time_s']:.0f}s ({stats['total_time_s']/60:.1f}min) incl transit",
                f"Coverage: {stats['coverage_pct']:.0f}%   Area: {stats['search_area_m2']:.0f}m2",
                f"Energy est: {stats['energy_wh']:.1f} Wh (hover+drag+turns)",
                f"Footprint: {stats['footprint_w']:.1f}x{stats['footprint_h']:.1f}m",
                f"Overlap: {self.overlap_pct}%   Scan angle: {angle_str}",
                f"Edge margin: {self.nfz_buffer}m",
            ]

            # Heatmap stats (only when enabled and computed)
            if self.show_heatmap and sub_segs:
                nfz_time_s = 0.0
                total_time_hm = 0.0
                total_energy_j = 0.0
                speed_sum = 0.0
                dist_sum = 0.0
                for sub in sub_segs:
                    spd = max(sub["speed"], 0.1)
                    d = sub["dist_m"]
                    seg_time = d / spd
                    total_time_hm += seg_time
                    speed_sum += spd * d  # distance-weighted speed
                    dist_sum += d
                    if sub["in_nfz"]:
                        nfz_time_s += seg_time
                    # Energy: hover + drag for this sub-segment
                    drag_power = DRAG_COEFF_W * (spd / DRAG_REF_SPEED) ** 2
                    total_energy_j += (HOVER_POWER_W + drag_power) * seg_time
                avg_speed = speed_sum / dist_sum if dist_sum > 0 else 0
                nfz_pct = (nfz_time_s / total_time_hm * 100) if total_time_hm > 0 else 0
                total_energy_wh = total_energy_j / 3600.0
                lines.append(f"Heatmap ON   Avg speed: {avg_speed:.1f} m/s")
                lines.append(f"NFZ zone time: {nfz_time_s:.0f}s ({nfz_pct:.0f}%)")
                lines.append(f"Est. energy: {total_energy_wh:.1f} Wh")
                lines.append(f"Est. search time: {total_time_hm:.0f}s ({total_time_hm/60:.1f}min)")
            elif self.show_heatmap:
                lines.append("Heatmap ON (no NFZ data)")

            panel_h = 14 * len(lines) + 10
            panel_w = 360
            cv2.rectangle(vis, (0, 0), (panel_w, panel_h), (0, 0, 0), -1)
            cv2.rectangle(vis, (0, 0), (panel_w, panel_h), (60, 60, 60), 1)
            for i, line in enumerate(lines):
                cv2.putText(vis, line, (6, 14 + i * 14),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.36, CLR_TEXT, 1, cv2.LINE_AA)

        # ── Speed heatmap color bar legend ──
        if self.show_heatmap and waypoints:
            cruise_spd = config.speed_for_altitude(float(self.altitude))
            bar_x = self.disp_w - 180
            bar_y = 10
            bar_w = 160
            bar_h = 16
            # Background
            cv2.rectangle(vis, (bar_x - 5, bar_y - 5),
                          (bar_x + bar_w + 5, bar_y + bar_h + 22), (0, 0, 0), -1)
            cv2.rectangle(vis, (bar_x - 5, bar_y - 5),
                          (bar_x + bar_w + 5, bar_y + bar_h + 22), (60, 60, 60), 1)
            # Gradient bar
            for px_i in range(bar_w):
                frac = px_i / bar_w
                spd = frac * cruise_spd
                col = self._speed_to_color(spd, cruise_spd)
                cv2.line(vis, (bar_x + px_i, bar_y),
                         (bar_x + px_i, bar_y + bar_h), col, 1)
            # Labels
            cv2.putText(vis, "Speed: 0", (bar_x, bar_y + bar_h + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, CLR_TEXT, 1, cv2.LINE_AA)
            label_r = f"{cruise_spd:.0f} m/s"
            cv2.putText(vis, label_r, (bar_x + bar_w - 40, bar_y + bar_h + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, CLR_TEXT, 1, cv2.LINE_AA)

        # ── Scale bar (bottom-right) ──
        scale_m = 50
        scale_px = int(scale_m * self.geo_disp.pix_per_m)
        if scale_px > self.disp_w // 3:
            scale_m = 20
            scale_px = int(scale_m * self.geo_disp.pix_per_m)
        sx = self.disp_w - scale_px - 15
        sy = self.disp_h - 20
        cv2.line(vis, (sx, sy), (sx + scale_px, sy), (255, 255, 255), 2)
        cv2.line(vis, (sx, sy - 5), (sx, sy + 5), (255, 255, 255), 2)
        cv2.line(vis, (sx + scale_px, sy - 5), (sx + scale_px, sy + 5), (255, 255, 255), 2)
        cv2.putText(vis, f"{scale_m}m", (sx + scale_px // 2 - 10, sy - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        return vis

    def _on_mouse(self, event, mx, my, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and not self.polygon_closed:
            # In draw mode: add vertex (convert display pixel to GPS)
            gps = self.geo_disp.pixels_to_gps(mx, my)
            self.search_poly_gps.append(gps)
        elif event == cv2.EVENT_RBUTTONDOWN:
            if not self.polygon_closed and len(self.search_poly_gps) >= 3:
                # Close polygon
                self.polygon_closed = True
                self._cached_key = None
            elif self.polygon_closed:
                # Place drone entry point
                gps = self.geo_disp.pixels_to_gps(mx, my)
                self.drone_gps = gps
                self._cached_key = None
                print(f"  Drone entry: ({gps[0]:.7f}, {gps[1]:.7f})")

    def _on_altitude(self, val):
        self.altitude = max(15, val)
        self._cached_key = None

    def _on_overlap(self, val):
        self.overlap_pct = val
        self._cached_key = None

    def _on_angle(self, val):
        self.scan_angle = val
        self._cached_key = None

    def _on_nfz_buffer(self, val):
        self.nfz_buffer = val
        self._cached_key = None

    def run(self):
        cv2.namedWindow(WIN_NAME, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(WIN_NAME, self._on_mouse)

        # Create trackbars
        cv2.createTrackbar("Altitude (m)", WIN_NAME, self.altitude, 50, self._on_altitude)
        cv2.setTrackbarMin("Altitude (m)", WIN_NAME, 15)
        cv2.createTrackbar("Overlap (%)", WIN_NAME, self.overlap_pct, 50, self._on_overlap)
        cv2.createTrackbar("Scan Angle", WIN_NAME, self.scan_angle, 181, self._on_angle)
        cv2.createTrackbar("Edge Margin (m)", WIN_NAME, self.nfz_buffer, 50, self._on_nfz_buffer)

        print(f"\nVisualizer ready. Window: {self.disp_w}x{self.disp_h}")
        print(f"  Pattern generated at {CANVAS_SIZE}x{CANVAS_SIZE} (same as main.py)")
        print(f"  Sliders: Altitude, Overlap (0=no-turn), Scan Angle (181=auto), Edge Margin")
        print(f"  LEFT-CLICK: add vertex (draw mode)   RIGHT-CLICK: set drone entry point")
        print(f"  Keys: P=toggle pattern (Lawnmower/Spiral/Zian Spiral), H=heatmap, R=reset, S=save, Q=quit")

        while True:
            vis = self._draw()
            cv2.imshow(WIN_NAME, vis)
            key = cv2.waitKey(30) & 0xFF

            if key in (ord('q'), 27):
                break
            elif key == ord('r'):
                self.search_poly_gps = []
                self.polygon_closed = False
                self.draw_mode = True
                self._cached_key = None
                print("  Polygon reset. Draw a new one (LEFT-CLICK, RIGHT-CLICK to close).")
            elif key == ord('p'):
                idx = self._pattern_types.index(self.pattern_type)
                self.pattern_type = self._pattern_types[(idx + 1) % len(self._pattern_types)]
                self._cached_key = None
                print(f"  Pattern type: {self.pattern_type}")
            elif key == ord('h'):
                self.show_heatmap = not self.show_heatmap
                print(f"  Speed heatmap: {'ON' if self.show_heatmap else 'OFF'}")
            elif key == ord('s'):
                out_path = os.path.join(_proj_root, "pattern_visualizer.png")
                cv2.imwrite(out_path, vis)
                print(f"  Saved: {out_path}")

        cv2.destroyAllWindows()


def _offset_polygon_centroid(gps_pts, buffer_m):
    """Naive centroid-based polygon expansion for visualization."""
    if len(gps_pts) < 3 or buffer_m <= 0:
        return gps_pts
    clat = sum(p[0] for p in gps_pts) / len(gps_pts)
    clon = sum(p[1] for p in gps_pts) / len(gps_pts)
    result = []
    lat_m = 111320.0
    lon_m = 111320.0 * math.cos(math.radians(clat))
    for p in gps_pts:
        dx = (p[1] - clon) * lon_m
        dy = (p[0] - clat) * lat_m
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.01:
            result.append(p)
            continue
        scale = (dist + buffer_m) / dist
        result.append((clat + dy * scale / lat_m, clon + dx * scale / lon_m))
    return result


# ── Entry point ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Interactive search pattern visualizer")
    parser.add_argument("--draw", action="store_true",
                        help="Start in drawing mode (click to define polygon)")
    parser.add_argument("--map", default=None,
                        help="Path to map image (default: config.MAP_FILE)")
    args = parser.parse_args()

    map_path = args.map or os.path.join(_proj_root, config.MAP_FILE)
    if not os.path.exists(map_path):
        alt = os.path.join(_proj_root, "map.jpg")
        if os.path.exists(alt):
            map_path = alt
        else:
            print(f"[ERROR] Map not found: {map_path}")
            print(f"  Place map.jpg in {_proj_root} or use --map <path>")
            sys.exit(1)

    viz = PatternVisualizer(map_path, draw_mode=args.draw)
    viz.run()


if __name__ == "__main__":
    main()
