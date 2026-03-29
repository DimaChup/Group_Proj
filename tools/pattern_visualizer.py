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
    P           = toggle pattern type (Lawnmower / Spiral)
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


def coverage_area_m2(waypoints_gps, footprint_h_m):
    """Compute scanned area as sum of strip_length * footprint_height."""
    if len(waypoints_gps) < 2:
        return 0.0
    area = 0.0
    # Scan segments are at even indices (0-1, 2-3, 4-5, ...)
    for i in range(0, len(waypoints_gps) - 1, 2):
        strip_len = gps_distance_m(waypoints_gps[i], waypoints_gps[i + 1])
        area += strip_len * footprint_h_m
    return area


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

        # Pattern type: "lawnmower" or "spiral"
        self.pattern_type = "lawnmower"

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
        if self.pattern_type == "spiral":
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
                inset = shape_poly.buffer(-offset)
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
                simplified = ring_poly.simplify(strip_spacing_m * 0.5, preserve_topology=True)
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

            # Coverage
            search_area = polygon_area_m2(self.search_poly_gps)
            if self.pattern_type == "spiral":
                # Spiral: approximate coverage as path length * footprint width
                covered = total_dist * ground_fp_w if total_dist > 0 else 0
            else:
                covered = coverage_area_m2(waypoints, ground_fp_h)
            coverage_pct = min(100.0, (covered / search_area * 100)) if search_area > 0 else 0

            # Energy (momentum theory model)
            if self.pattern_type == "spiral":
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

    def _compute_segment_speeds(self, waypoints):
        """Compute expected speed for each segment considering NFZ slowdown + momentum.

        Returns a list of (speed_mps, is_nfz_zone) tuples, one per segment.
        """
        if len(waypoints) < 2:
            return []

        alt = float(self.altitude)
        cruise_speed = config.speed_for_altitude(alt)

        # Build geofence for distance queries
        geofence = NFZGeofence(self.geo_canvas)
        has_nfz = bool(config.SSSI_GPS) and len(config.SSSI_GPS) >= 3

        segment_speeds = []
        prev_speed = cruise_speed  # assume starting at cruise

        for i in range(len(waypoints) - 1):
            wp_a = waypoints[i]
            wp_b = waypoints[i + 1]

            # Midpoint GPS
            mid_lat = (wp_a[0] + wp_b[0]) / 2.0
            mid_lon = (wp_a[1] + wp_b[1]) / 2.0

            seg_len = gps_distance_m(wp_a, wp_b)

            # Target speed based on NFZ distance
            target_speed = cruise_speed
            in_nfz_zone = False

            if has_nfz:
                dist_m, is_inside = geofence.distance_to_boundary(mid_lat, mid_lon)
                if is_inside or dist_m <= config.NFZ_SCALAR_ZERO_M:
                    target_speed = config.NFZ_MIN_SPEED_MPS
                    in_nfz_zone = True
                elif dist_m < config.NFZ_SLOW_ZONE_M:
                    ratio = (dist_m - config.NFZ_SCALAR_ZERO_M) / (
                        config.NFZ_SLOW_ZONE_M - config.NFZ_SCALAR_ZERO_M)
                    target_speed = min(ratio * config.NFZ_ZONE_MAX_SPEED_MPS, cruise_speed)
                    in_nfz_zone = True

            # Momentum model: can't instantly reach target speed
            # v_new = min(v_target, v_prev + accel * dt) where dt = seg_len / v_avg
            if seg_len > 0.01 and prev_speed < target_speed:
                # Estimate time to traverse at average of prev and target
                v_avg = max(0.5, (prev_speed + target_speed) / 2.0)
                dt = seg_len / v_avg
                actual_speed = min(target_speed, prev_speed + ACCEL_MPS2 * dt)
            elif seg_len > 0.01 and prev_speed > target_speed:
                # Decelerating: assume same accel for braking
                v_avg = max(0.5, (prev_speed + target_speed) / 2.0)
                dt = seg_len / v_avg
                actual_speed = max(target_speed, prev_speed - ACCEL_MPS2 * dt)
            else:
                actual_speed = target_speed

            actual_speed = max(actual_speed, 0.0)
            segment_speeds.append((actual_speed, in_nfz_zone))
            prev_speed = actual_speed

        return segment_speeds

    def _speed_to_color(self, speed, cruise_speed):
        """Map speed to BGR color: green (fast), yellow (medium), red (slow)."""
        if cruise_speed <= 0:
            return CLR_HEAT_SLOW
        ratio = speed / cruise_speed
        if ratio > 0.8:
            return CLR_HEAT_FAST
        elif ratio > 0.4:
            # Interpolate green to yellow
            t = (ratio - 0.4) / 0.4  # 0..1
            b = int(0 * (1 - t) + 0 * t)
            g = int(0 * (1 - t) + 200 * t)
            r = int(220 * (1 - t) + 200 * t)
            return (b, g, r)
        else:
            # Interpolate red to yellow
            t = ratio / 0.4  # 0..1
            b = int(0 * (1 - t) + 0 * t)
            g = int(0 * (1 - t) + 0 * t)
            r = int(220 * (1 - t) + 220 * t)
            return (b, g, r)

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

        # Compute segment speeds if heatmap is enabled
        seg_speeds = None
        if self.show_heatmap:
            seg_speeds = self._compute_segment_speeds(waypoints)
            cruise_speed = config.speed_for_altitude(float(self.altitude))

        # Draw path segments
        for i in range(len(wp_px) - 1):
            if self.show_heatmap and seg_speeds:
                color = self._speed_to_color(seg_speeds[i][0], cruise_speed)
                cv2.line(vis, wp_px[i], wp_px[i + 1], color, 2, cv2.LINE_AA)
            elif self.pattern_type == "spiral":
                cv2.line(vis, wp_px[i], wp_px[i + 1], CLR_SCAN, 2, cv2.LINE_AA)
            elif i % 2 == 0:
                cv2.line(vis, wp_px[i], wp_px[i + 1], CLR_SCAN, 2, cv2.LINE_AA)
            else:
                cv2.line(vis, wp_px[i], wp_px[i + 1], CLR_UTURN, 1, cv2.LINE_AA)

        # Draw waypoint dots and numbers
        # Spiral has many more waypoints — label less frequently
        label_every = 20 if self.pattern_type == "spiral" else 4
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

            pat_label = "Spiral" if self.pattern_type == "spiral" else "Lawnmower"
            lines = [
                f"Pattern: {pat_label}   (P to toggle)",
                f"Altitude: {self.altitude}m   Speed: {stats['speed_mps']:.1f} m/s",
                f"Waypoints: {stats['n_wp']}   {'Points' if self.pattern_type == 'spiral' else 'Strips'}: {stats['n_strips']}",
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
            if self.show_heatmap and seg_speeds:
                nfz_time_s = 0.0
                total_time_hm = 0.0
                speed_sum = 0.0
                for idx, (spd, in_zone) in enumerate(seg_speeds):
                    seg_dist = gps_distance_m(waypoints[idx], waypoints[idx + 1])
                    seg_time = seg_dist / max(spd, 0.1)
                    total_time_hm += seg_time
                    speed_sum += spd
                    if in_zone:
                        nfz_time_s += seg_time
                avg_speed = speed_sum / len(seg_speeds) if seg_speeds else 0
                nfz_pct = (nfz_time_s / total_time_hm * 100) if total_time_hm > 0 else 0
                lines.append(f"Heatmap ON   Avg speed: {avg_speed:.1f} m/s")
                lines.append(f"NFZ zone time: {nfz_time_s:.0f}s ({nfz_pct:.0f}%)")
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
        print(f"  Keys: P=toggle pattern, H=speed heatmap, R=reset/draw, S=save, Q=quit")

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
                if self.pattern_type == "lawnmower":
                    self.pattern_type = "spiral"
                else:
                    self.pattern_type = "lawnmower"
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
