"""
Interactive Search Pattern Visualizer
=====================================
Visualizes how the lawnmower search pattern changes with different parameters.
Uses the real PathPlanner from planning.py and GeoTransformer from utils.py.

Usage:
    python tools/pattern_visualizer.py              # default polygon from config/KML
    python tools/pattern_visualizer.py --draw       # draw custom polygon on map

Controls:
    Sliders adjust altitude, overlap, scan angle, and NFZ buffer in real time.
    LEFT-CLICK  = add polygon vertex (in --draw mode)
    RIGHT-CLICK = close polygon (in --draw mode)
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

# Add project root to path so we can import project modules
_proj_root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

import config
from utils import GeoTransformer
from planning import PathPlanner


# ── Constants ──────────────────────────────────────────────────────────

MAX_DISPLAY = 1000          # max window dimension in pixels
WIN_NAME = "Search Pattern Visualizer"

# Color palette (BGR)
CLR_SCAN       = (0, 255, 0)       # green  — scan lines
CLR_UTURN      = (0, 255, 255)     # yellow — U-turns
CLR_NFZ        = (0, 0, 255)       # red    — NFZ polygon
CLR_NFZ_BUF    = (0, 0, 180)       # dark red — NFZ buffer
CLR_SEARCH     = (0, 200, 0)       # green  — search polygon outline
CLR_SEARCH_FIL = (30, 60, 30)      # dark green — search polygon fill
CLR_FOOTPRINT  = (200, 200, 0)     # cyan   — camera footprint
CLR_START      = (0, 255, 0)       # green  — start marker
CLR_END        = (0, 0, 255)       # red    — end marker
CLR_WP         = (255, 255, 255)   # white  — waypoint dots
CLR_FOCUS      = (255, 165, 0)     # orange — focus area
CLR_TEXT        = (220, 220, 220)   # light grey


# ── Helpers ────────────────────────────────────────────────────────────

def gps_distance_m(a, b):
    """Haversine-lite distance between two (lat, lon) points in metres."""
    dlat = (b[0] - a[0]) * 111320
    dlon = (b[1] - a[1]) * 111320 * math.cos(math.radians(a[0]))
    return math.sqrt(dlat ** 2 + dlon ** 2)


def polygon_area_m2(gps_pts):
    """Shoelace area of a GPS polygon in square metres."""
    if len(gps_pts) < 3:
        return 0.0
    n = len(gps_pts)
    ref_lat = gps_pts[0][0]
    cos_lat = math.cos(math.radians(ref_lat))
    # convert to local metres
    xs = [(p[1] - gps_pts[0][1]) * 111320 * cos_lat for p in gps_pts]
    ys = [(p[0] - gps_pts[0][0]) * 111320 for p in gps_pts]
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += xs[i] * ys[j] - xs[j] * ys[i]
    return abs(area) / 2.0


def offset_polygon(gps_pts, buffer_m):
    """Naive polygon offset (expand each vertex outward by buffer_m).

    This is a simple centroid-based expansion, not a true Minkowski offset,
    but it is good enough for visualization purposes.
    """
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


# ── Main Visualizer ──────────────────────────────────────────────────

class PatternVisualizer:
    def __init__(self, map_path, draw_mode=False):
        self.draw_mode = draw_mode

        # Load KML zones
        config.load_kml_zones()

        # Load map
        self.map_orig = cv2.imread(map_path)
        if self.map_orig is None:
            print(f"[ERROR] Cannot load map: {map_path}")
            sys.exit(1)
        map_h, map_w = self.map_orig.shape[:2]
        print(f"Map loaded: {map_w}x{map_h}")

        # Scale for display
        self.disp_scale = min(MAX_DISPLAY / map_w, MAX_DISPLAY / map_h, 1.0)
        self.disp_w = int(map_w * self.disp_scale)
        self.disp_h = int(map_h * self.disp_scale)
        self.map_disp = cv2.resize(self.map_orig, (self.disp_w, self.disp_h))

        # GeoTransformer at display resolution
        self.geo = GeoTransformer(map_w_px=self.disp_w)

        # Search polygon (pixel coords in display space)
        self.search_poly_px = []
        self.polygon_closed = False

        if not draw_mode:
            self._load_default_polygon()
            self.polygon_closed = True

        # Slider state
        self.altitude = int(config.TARGET_ALT)
        self.overlap_pct = 20       # percent
        self.scan_angle = 181       # 181 = auto
        self.nfz_buffer = int(config.NFZ_WAYPOINT_BUFFER_M)

        # Cached results
        self._cached_key = None
        self._cached_waypoints = []
        self._cached_stats = {}

    def _load_default_polygon(self):
        """Load SEARCH_AREA_GPS into pixel coords."""
        self.search_poly_px = []
        for lat, lon in config.SEARCH_AREA_GPS:
            px = self.geo.gps_to_pixels(lat, lon)
            self.search_poly_px.append((int(px[0]), int(px[1])))
        print(f"Loaded search area: {len(self.search_poly_px)} vertices")

    def _gps_poly_to_px(self, gps_pts):
        """Convert GPS polygon to display pixel coords."""
        return [tuple(int(c) for c in self.geo.gps_to_pixels(p[0], p[1])) for p in gps_pts]

    def _generate_pattern(self):
        """Generate pattern using PathPlanner (cached)."""
        cache_key = (tuple(self.search_poly_px), self.altitude, self.overlap_pct, self.scan_angle)
        if cache_key == self._cached_key:
            return self._cached_waypoints

        if len(self.search_poly_px) < 3:
            self._cached_waypoints = []
            self._cached_stats = {}
            self._cached_key = cache_key
            return []

        # Build planner
        planner = PathPlanner(self.geo, list(self.search_poly_px))
        planner._no_turn = True

        # Override overlap in the planner by monkey-patching the generate method
        # We call generate_search_pattern with alt_override and handle overlap/angle
        # by temporarily modifying the planner internals.
        alt = float(self.altitude)
        overlap = self.overlap_pct / 100.0

        # Save originals
        orig_generate = planner.generate_search_pattern

        def patched_generate(map_w, map_h, drone_gps=None, alt_override=None):
            """Patched version that respects custom overlap and scan angle."""
            if len(planner.search_polygon) < 3:
                return []
            search_alt = alt

            mask = np.zeros((map_h, map_w), dtype=np.uint8)
            poly_pts = np.array([planner.search_polygon], dtype=np.int32)
            cv2.fillPoly(mask, poly_pts, 255)
            planner.virtual_polygon = poly_pts.reshape(-1, 1, 2)

            rect = cv2.minAreaRect(poly_pts[0])
            (center, size, angle) = rect

            # Scan angle: auto or manual
            if self.scan_angle > 180:
                s_angle = angle + 90 if size[0] < size[1] else angle
            else:
                s_angle = float(self.scan_angle)

            rotation_mat = cv2.getRotationMatrix2D(center, s_angle, 1.0)
            inverse_rotation = cv2.invertAffineTransform(rotation_mat)
            rotated_mask = cv2.warpAffine(mask, rotation_mat, (map_w, map_h))

            ground_footprint_m = (config.SENSOR_WIDTH_MM * search_alt) / config.FOCAL_LENGTH_MM
            if planner._no_turn:
                aspect = config.IMAGE_H / config.IMAGE_W
                ground_footprint_m = ground_footprint_m * aspect
                custom_overlap = 0.0
            else:
                custom_overlap = overlap
            swath_m = ground_footprint_m * (1.0 - custom_overlap)
            strip_spacing_px = max(1, int(swath_m * planner.pix_per_m))

            points = cv2.findNonZero(rotated_mask)
            if points is None:
                return []
            bbox_x, bbox_y, bbox_w, bbox_h = cv2.boundingRect(points)

            all_strips = []
            inset_px = strip_spacing_px // 3
            bottom_limit = bbox_y + bbox_h - inset_px

            scan_lines = list(range(bbox_y + inset_px, bbox_y + bbox_h, strip_spacing_px))
            if not scan_lines or scan_lines[-1] < bottom_limit:
                scan_lines.append(bottom_limit)

            for scan_y in scan_lines:
                scan_y = min(scan_y, bottom_limit)
                row = rotated_mask[scan_y, :]
                filled_cols = np.where(row == 255)[0]
                if len(filled_cols) > 0:
                    x_start = filled_cols[0] + inset_px
                    x_end = filled_cols[-1] - inset_px
                    if x_end > x_start:
                        all_strips.append([(x_start, scan_y), (x_end, scan_y)])

            direction = 1
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

            # Dedup
            if len(waypoints) >= 2:
                deduped = [waypoints[0]]
                for wp in waypoints[1:]:
                    if abs(wp[0] - deduped[-1][0]) > 1e-9 or abs(wp[1] - deduped[-1][1]) > 1e-9:
                        deduped.append(wp)
                waypoints = deduped

            return waypoints

        waypoints = patched_generate(self.disp_w, self.disp_h)
        self._cached_waypoints = waypoints
        self._cached_key = cache_key

        # Compute stats
        if waypoints:
            total_dist = sum(gps_distance_m(waypoints[i], waypoints[i + 1])
                             for i in range(len(waypoints) - 1))
            speed = config.speed_for_altitude(alt)
            search_time = total_dist / speed if speed > 0 else 0
            # transit from takeoff
            transit_dist = gps_distance_m(config.TAKEOFF_GPS, waypoints[0])
            transit_time = transit_dist / config.TRANSIT_SPEED_MPS if config.TRANSIT_SPEED_MPS > 0 else 0
            total_time = search_time + 2 * transit_time  # out + back

            # Coverage area
            search_area = polygon_area_m2(
                [self.geo.pixels_to_gps(p[0], p[1]) for p in self.search_poly_px])
            ground_fp_w = (config.SENSOR_WIDTH_MM * alt) / config.FOCAL_LENGTH_MM
            ground_fp_h = ground_fp_w * config.IMAGE_H / config.IMAGE_W
            n_strips = len(waypoints) // 2
            covered_area = sum(
                gps_distance_m(waypoints[i * 2], waypoints[i * 2 + 1]) * ground_fp_h
                for i in range(n_strips) if i * 2 + 1 < len(waypoints))
            coverage_pct = min(100.0, (covered_area / search_area * 100)) if search_area > 0 else 0

            # Energy estimate (rough: 15 W/m of flight for a ~3kg drone)
            energy_wh = total_dist * 15 / 3600

            self._cached_stats = {
                "n_wp": len(waypoints),
                "n_strips": n_strips,
                "total_dist_m": total_dist,
                "transit_dist_m": transit_dist,
                "search_time_s": search_time,
                "total_time_s": total_time,
                "speed_mps": speed,
                "coverage_pct": coverage_pct,
                "search_area_m2": search_area,
                "energy_wh": energy_wh,
                "footprint_w": ground_fp_w,
                "footprint_h": ground_fp_h,
            }
        else:
            self._cached_stats = {}

        return waypoints

    def _draw(self):
        """Render the current state to a display image."""
        vis = self.map_disp.copy()
        alt = float(self.altitude)

        # ── SSSI polygon (NFZ) ──
        if config.SSSI_GPS and len(config.SSSI_GPS) >= 3:
            sssi_px = self._gps_poly_to_px(config.SSSI_GPS)
            sssi_arr = np.array(sssi_px, np.int32)

            # NFZ buffer zone
            if self.nfz_buffer > 0:
                buf_gps = offset_polygon(config.SSSI_GPS, self.nfz_buffer)
                buf_px = self._gps_poly_to_px(buf_gps)
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
            foc_px = self._gps_poly_to_px(config.FOCUS_AREA_GPS)
            foc_arr = np.array(foc_px, np.int32)
            cv2.polylines(vis, [foc_arr], True, CLR_FOCUS, 1, cv2.LINE_AA)

        # ── Search polygon ──
        if len(self.search_poly_px) >= 3 and self.polygon_closed:
            poly_arr = np.array(self.search_poly_px, np.int32)
            overlay = vis.copy()
            cv2.fillPoly(overlay, [poly_arr], CLR_SEARCH_FIL)
            cv2.addWeighted(overlay, 0.4, vis, 0.6, 0, vis)
            cv2.polylines(vis, [poly_arr], True, CLR_SEARCH, 2, cv2.LINE_AA)

        # ── Drawing mode: show vertices being placed ──
        if not self.polygon_closed:
            for i, pt in enumerate(self.search_poly_px):
                cv2.circle(vis, pt, 5, CLR_SEARCH, -1)
                if i > 0:
                    cv2.line(vis, self.search_poly_px[i - 1], pt, CLR_SEARCH, 2)
            msg = f"Vertices: {len(self.search_poly_px)} | LEFT-CLICK=add, RIGHT-CLICK=close"
            cv2.putText(vis, msg, (10, self.disp_h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, CLR_TEXT, 1, cv2.LINE_AA)
            return vis

        # ── Generate and draw pattern ──
        waypoints = self._generate_pattern()
        if not waypoints:
            cv2.putText(vis, "No waypoints (polygon too small or invalid)",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            return vis

        wp_px = [tuple(int(c) for c in self.geo.gps_to_pixels(w[0], w[1])) for w in waypoints]

        # Draw path segments (green scan, yellow U-turn)
        for i in range(len(wp_px) - 1):
            if i % 2 == 0:
                cv2.line(vis, wp_px[i], wp_px[i + 1], CLR_SCAN, 2, cv2.LINE_AA)
            else:
                cv2.line(vis, wp_px[i], wp_px[i + 1], CLR_UTURN, 1, cv2.LINE_AA)

        # Draw waypoint numbers (every other to avoid clutter)
        for i, pt in enumerate(wp_px):
            cv2.circle(vis, pt, 3, CLR_WP, -1)
            if i % 4 == 0 or i == 0 or i == len(wp_px) - 1:
                cv2.putText(vis, str(i + 1), (pt[0] + 5, pt[1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.28, CLR_WP, 1, cv2.LINE_AA)

        # Start / end markers
        cv2.circle(vis, wp_px[0], 8, CLR_START, 2, cv2.LINE_AA)
        cv2.putText(vis, "START", (wp_px[0][0] + 10, wp_px[0][1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, CLR_START, 1, cv2.LINE_AA)
        cv2.circle(vis, wp_px[-1], 8, CLR_END, 2, cv2.LINE_AA)
        cv2.putText(vis, "END", (wp_px[-1][0] + 10, wp_px[-1][1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, CLR_END, 1, cv2.LINE_AA)

        # Takeoff marker
        toff_px = tuple(int(c) for c in self.geo.gps_to_pixels(*config.TAKEOFF_GPS))
        cv2.drawMarker(vis, toff_px, (0, 255, 255), cv2.MARKER_DIAMOND, 12, 2)
        cv2.putText(vis, "TOL", (toff_px[0] + 8, toff_px[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1, cv2.LINE_AA)

        # ── Camera footprint rectangle at first waypoint ──
        stats = self._cached_stats
        if stats:
            fp_w_px = int(stats["footprint_w"] * self.geo.pix_per_m)
            fp_h_px = int(stats["footprint_h"] * self.geo.pix_per_m)
            fp_cx, fp_cy = wp_px[0]
            tl = (fp_cx - fp_w_px // 2, fp_cy - fp_h_px // 2)
            br = (fp_cx + fp_w_px // 2, fp_cy + fp_h_px // 2)
            cv2.rectangle(vis, tl, br, CLR_FOOTPRINT, 1, cv2.LINE_AA)
            cv2.putText(vis, f"footprint {stats['footprint_w']:.1f}x{stats['footprint_h']:.1f}m",
                        (tl[0], tl[1] - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.28, CLR_FOOTPRINT, 1)

        # ── Stats panel ──
        if stats:
            lines = [
                f"Altitude: {self.altitude}m   Speed: {stats['speed_mps']:.1f} m/s",
                f"Waypoints: {stats['n_wp']}   Strips: {stats['n_strips']}",
                f"Search dist: {stats['total_dist_m']:.0f}m   Transit: {stats['transit_dist_m']:.0f}m",
                f"Search time: {stats['search_time_s']:.0f}s ({stats['search_time_s']/60:.1f}min)",
                f"Total time:  {stats['total_time_s']:.0f}s ({stats['total_time_s']/60:.1f}min)",
                f"Coverage: {stats['coverage_pct']:.0f}%   Area: {stats['search_area_m2']:.0f}m2",
                f"Energy est: {stats['energy_wh']:.1f} Wh",
                f"Footprint: {stats['footprint_w']:.1f}x{stats['footprint_h']:.1f}m",
                f"Overlap: {self.overlap_pct}%   Angle: {'auto' if self.scan_angle > 180 else str(self.scan_angle) + ' deg'}",
                f"NFZ buffer: {self.nfz_buffer}m",
            ]
            panel_h = 14 * len(lines) + 10
            panel_w = 340
            cv2.rectangle(vis, (0, 0), (panel_w, panel_h), (0, 0, 0), -1)
            cv2.rectangle(vis, (0, 0), (panel_w, panel_h), (60, 60, 60), 1)
            for i, line in enumerate(lines):
                cv2.putText(vis, line, (6, 14 + i * 14),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.36, CLR_TEXT, 1, cv2.LINE_AA)

        # ── Scale bar (bottom-right) ──
        scale_m = 50
        scale_px = int(scale_m * self.geo.pix_per_m)
        if scale_px > self.disp_w // 3:
            scale_m = 20
            scale_px = int(scale_m * self.geo.pix_per_m)
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
            self.search_poly_px.append((mx, my))
        elif event == cv2.EVENT_RBUTTONDOWN and not self.polygon_closed and len(self.search_poly_px) >= 3:
            self.polygon_closed = True
            self._cached_key = None  # force regeneration

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

    def run(self):
        cv2.namedWindow(WIN_NAME, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(WIN_NAME, self._on_mouse)

        # Create trackbars
        cv2.createTrackbar("Altitude (m)", WIN_NAME, self.altitude, 50, self._on_altitude)
        cv2.setTrackbarMin("Altitude (m)", WIN_NAME, 15)
        cv2.createTrackbar("Overlap (%)", WIN_NAME, self.overlap_pct, 50, self._on_overlap)
        cv2.createTrackbar("Scan Angle", WIN_NAME, self.scan_angle, 181, self._on_angle)
        cv2.createTrackbar("NFZ Buffer (m)", WIN_NAME, self.nfz_buffer, 50, self._on_nfz_buffer)

        print(f"\nVisualizer ready. Window: {self.disp_w}x{self.disp_h}")
        print(f"  Sliders: Altitude, Overlap, Scan Angle (181=auto), NFZ Buffer")
        print(f"  Keys: R=reset/draw, S=save, Q=quit")

        while True:
            vis = self._draw()
            cv2.imshow(WIN_NAME, vis)
            key = cv2.waitKey(30) & 0xFF

            if key in (ord('q'), 27):
                break
            elif key == ord('r'):
                self.search_poly_px = []
                self.polygon_closed = False
                self._cached_key = None
                print("  Polygon reset. Draw a new one (LEFT-CLICK, RIGHT-CLICK to close).")
            elif key == ord('s'):
                out_path = os.path.join(_proj_root, "pattern_visualizer.png")
                cv2.imwrite(out_path, vis)
                print(f"  Saved: {out_path}")

        cv2.destroyAllWindows()


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
        # Try project root fallback
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
