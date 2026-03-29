"""
Cinematic SAR Drone Mission Animation -- Part 1 (Scenes 1-4).

Scenes:
  1. OverviewScene   (5 s) — bird's eye, all zones labelled, title
  2. TransitScene    (5 s) — takeoff, TOL -> T1 -> T2 -> T3, altitude gauge
  3. SearchScene     (8 s) — lawnmower with camera footprint, coverage strips
  4. BeaconScene     (4 s) — PLB flash, focus area, tighter pattern at 5 m/s

Run individual scenes:
  python -m manim -ql cinematic_part1.py OverviewScene
  python -m manim -ql cinematic_part1.py TransitScene
  python -m manim -ql cinematic_part1.py SearchScene
  python -m manim -ql cinematic_part1.py BeaconScene
"""

from manim import *
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon, LineString

# ═══════════════════════════════════════════════════════════════
#  GPS DATA (from config.py / AENGM0074.kml)
# ═══════════════════════════════════════════════════════════════

TAKEOFF_GPS = (51.42340640, -2.67144603)

SEARCH_AREA_GPS = [
    (51.42326957, -2.67094835),
    (51.42287025, -2.67004543),
    (51.42336623, -2.66816930),
    (51.42421477, -2.66880977),
    (51.42354070, -2.67127778),
]

FLIGHT_AREA_GPS = [
    (51.42342595, -2.67172077),
    (51.42124623, -2.67013403),
    (51.42244012, -2.66568782),
    (51.42469179, -2.66706023),
]

SSSI_GPS = [
    (51.42353587, -2.67145175),
    (51.42215640, -2.66976824),
    (51.42267105, -2.66770544),
    (51.42335592, -2.66816460),
    (51.42286083, -2.67004342),
    (51.42326667, -2.67096542),
    (51.42356862, -2.67132430),
]

FOCUS_AREA_GPS = [
    (51.42330494, -2.66982370),
    (51.42344371, -2.66949620),
    (51.42352782, -2.66980025),
    (51.42334973, -2.67001828),
]

TRANSIT_WAYPOINTS_GPS = [
    (51.42176480, -2.67011737),  # T1
    (51.42247427, -2.66713882),  # T2
    (51.42410412, -2.66830869),  # T3
]

# Flight parameters
TARGET_ALT = 35.0
TRANSIT_SPEED_MPS = 15.0
SEARCH_SPEED_MPS = 8.0
FOCUS_SPEED_MPS = 5.0
SENSOR_WIDTH_MM = 5.02
FOCAL_LENGTH_MM = 5.46
IMAGE_W = 1456
IMAGE_H = 1088
NFZ_WAYPOINT_BUFFER_M = 30.0

GROUND_FOOTPRINT_W_M = (SENSOR_WIDTH_MM * TARGET_ALT) / FOCAL_LENGTH_MM  # ~32.1 m
GROUND_FOOTPRINT_H_M = GROUND_FOOTPRINT_W_M * (IMAGE_H / IMAGE_W)       # ~24.0 m


# ═══════════════════════════════════════════════════════════════
#  GPS -> SCREEN CONVERSION (shared by all scenes)
# ═══════════════════════════════════════════════════════════════

def gps_to_meters(lat, lon, ref_lat, ref_lon):
    """(lat, lon) -> (east, north) in metres from reference."""
    dlat = lat - ref_lat
    dlon = lon - ref_lon
    north = dlat * 111320.0
    east = dlon * 111320.0 * np.cos(np.radians(ref_lat))
    return east, north


def _compute_transform():
    """Compute ref point, scale, and offset so the field fits nicely on screen."""
    all_lats = [p[0] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
    all_lons = [p[1] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
    ref_lat = np.mean(all_lats)
    ref_lon = np.mean(all_lons)

    extents = []
    for lat, lon in FLIGHT_AREA_GPS:
        extents.append(gps_to_meters(lat, lon, ref_lat, ref_lon))
    xs = [p[0] for p in extents]
    ys = [p[1] for p in extents]
    extent = max(max(xs) - min(xs), max(ys) - min(ys))

    frame_size = 5.5
    scale = frame_size / extent
    offset = np.array([0.0, -0.3])
    return ref_lat, ref_lon, scale, offset


REF_LAT, REF_LON, SCALE, OFFSET = _compute_transform()


def gps_to_screen(lat, lon):
    """GPS -> manim screen point (np.array with z=0)."""
    ex, ny = gps_to_meters(lat, lon, REF_LAT, REF_LON)
    return np.array([ex * SCALE + OFFSET[0], ny * SCALE + OFFSET[1], 0.0])


def gps_poly_to_screen(gps_coords):
    """List of (lat,lon) -> list of np.array screen points."""
    return [gps_to_screen(lat, lon) for lat, lon in gps_coords]


def m2s(metres):
    """Metres to screen units."""
    return metres * SCALE


# Pre-compute screen polygons
SEARCH_PTS = gps_poly_to_screen(SEARCH_AREA_GPS)
FLIGHT_PTS = gps_poly_to_screen(FLIGHT_AREA_GPS)
SSSI_PTS = gps_poly_to_screen(SSSI_GPS)
FOCUS_PTS = gps_poly_to_screen(FOCUS_AREA_GPS)
TOL_PT = gps_to_screen(*TAKEOFF_GPS)
TRANSIT_PTS = [gps_to_screen(lat, lon) for lat, lon, *_ in
               [(51.42176480, -2.67011737),
                (51.42247427, -2.66713882),
                (51.42410412, -2.66830869)]]


# ═══════════════════════════════════════════════════════════════
#  LAWNMOWER PATTERN GENERATION (using Shapely for clipping)
# ═══════════════════════════════════════════════════════════════

def _find_scan_angle(pts_2d):
    """Find the angle of the longest edge of the polygon (degrees from +x axis)."""
    best_len = 0
    best_angle = 0
    n = len(pts_2d)
    for i in range(n):
        dx = pts_2d[(i + 1) % n][0] - pts_2d[i][0]
        dy = pts_2d[(i + 1) % n][1] - pts_2d[i][1]
        length = np.hypot(dx, dy)
        if length > best_len:
            best_len = length
            best_angle = np.degrees(np.arctan2(dy, dx))
    return best_angle


def generate_lawnmower(screen_pts, strip_spacing_m, inset_frac=1.0 / 3.0):
    """Generate lawnmower scan lines clipped to a polygon.

    Returns list of (start_screen, end_screen) pairs forming the zigzag path,
    where each pair is a np.array([x, y, 0]).
    """
    pts_2d = [(p[0], p[1]) for p in screen_pts]
    shapely_poly = ShapelyPolygon(pts_2d)

    # Inset the polygon slightly so lines don't touch edges
    inset_m = strip_spacing_m * inset_frac
    inset_screen = m2s(inset_m)
    inset_poly = shapely_poly.buffer(-inset_screen)
    if inset_poly.is_empty:
        inset_poly = shapely_poly

    angle = _find_scan_angle(pts_2d)
    theta = np.radians(-angle)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    cx, cy = shapely_poly.centroid.x, shapely_poly.centroid.y

    def rotate(x, y):
        dx, dy = x - cx, y - cy
        return cx + dx * cos_t - dy * sin_t, cy + dx * sin_t + dy * cos_t

    def inv_rotate(x, y):
        dx, dy = x - cx, y - cy
        return cx + dx * cos_t + dy * sin_t, cy - dx * sin_t + dy * cos_t

    # Rotate polygon to find extent
    rotated_coords = [rotate(x, y) for x, y in pts_2d]
    ry = [p[1] for p in rotated_coords]
    rx = [p[0] for p in rotated_coords]
    y_min, y_max = min(ry), max(ry)
    x_min, x_max = min(rx), max(rx)

    spacing_screen = m2s(strip_spacing_m)
    inset_y = spacing_screen * inset_frac

    ys = np.arange(y_min + inset_y, y_max - inset_y + spacing_screen * 0.1, spacing_screen)

    lines = []
    for i, y_val in enumerate(ys):
        if i % 2 == 0:
            sx, sy = inv_rotate(x_min - 0.5, y_val)
            ex, ey = inv_rotate(x_max + 0.5, y_val)
        else:
            sx, sy = inv_rotate(x_max + 0.5, y_val)
            ex, ey = inv_rotate(x_min - 0.5, y_val)

        line = LineString([(sx, sy), (ex, ey)])
        clipped = line.intersection(inset_poly)

        if clipped.is_empty:
            continue

        # Handle MultiLineString or LineString
        if clipped.geom_type == "LineString":
            coords = list(clipped.coords)
            if len(coords) >= 2:
                if i % 2 == 0:
                    s, e = coords[0], coords[-1]
                else:
                    s, e = coords[-1], coords[0]
                lines.append((
                    np.array([s[0], s[1], 0.0]),
                    np.array([e[0], e[1], 0.0]),
                ))
        elif clipped.geom_type == "MultiLineString":
            for seg in clipped.geoms:
                coords = list(seg.coords)
                if len(coords) >= 2:
                    if i % 2 == 0:
                        s, e = coords[0], coords[-1]
                    else:
                        s, e = coords[-1], coords[0]
                    lines.append((
                        np.array([s[0], s[1], 0.0]),
                        np.array([e[0], e[1], 0.0]),
                    ))

    return lines


def _build_waypoint_path(scan_lines):
    """Convert scan lines into a single ordered list of waypoints for the drone."""
    if not scan_lines:
        return []
    waypoints = [scan_lines[0][0], scan_lines[0][1]]
    for i in range(1, len(scan_lines)):
        waypoints.append(scan_lines[i][0])
        waypoints.append(scan_lines[i][1])
    return waypoints


# ═══════════════════════════════════════════════════════════════
#  HELPER: build background zone polygons (used by multiple scenes)
# ═══════════════════════════════════════════════════════════════

def _make_zones(dim=False):
    """Return (flight_poly, search_poly, sssi_poly) manim objects.
    If dim=True, reduce fill opacity for background use."""
    f_op = 0.03 if dim else 0.0
    s_op = 0.06 if dim else 0.15
    n_op = 0.12 if dim else 0.25

    flight_raw = Polygon(*FLIGHT_PTS, color=WHITE, stroke_width=1.5,
                         stroke_opacity=0.5 if dim else 0.8, fill_opacity=f_op)
    flight_poly = DashedVMobject(flight_raw, num_dashes=30)

    search_poly = Polygon(*SEARCH_PTS, fill_color=BLUE_C, fill_opacity=s_op,
                          stroke_color=BLUE, stroke_width=1.5)

    sssi_poly = Polygon(*SSSI_PTS, fill_color=RED_C, fill_opacity=n_op,
                        stroke_color=RED, stroke_width=2)

    return flight_poly, search_poly, sssi_poly


def _make_drone(scale_val=0.10):
    """Create a small white triangle drone icon."""
    return Triangle(fill_color=WHITE, fill_opacity=1, stroke_width=0).scale(scale_val)


def _centroid(pts):
    """Centroid of a list of screen points."""
    arr = np.array(pts)
    return arr.mean(axis=0)


def _angle_between(p1, p2):
    """Angle in radians from p1 to p2 (screen coords)."""
    d = p2 - p1
    return np.arctan2(d[1], d[0])


# ═══════════════════════════════════════════════════════════════
#  SCENE 1: OVERVIEW (5 seconds)
# ═══════════════════════════════════════════════════════════════

class OverviewScene(Scene):
    def construct(self):
        # Title
        title = Text("SAR Drone Mission", font_size=42, weight=BOLD, color=WHITE)
        subtitle = Text("Autonomous Search and Rescue", font_size=24, color=GREY_B)
        title.to_edge(UP, buff=0.3)
        subtitle.next_to(title, DOWN, buff=0.1)

        # Zone polygons
        flight_poly, search_poly, sssi_poly = _make_zones(dim=False)

        # TOL marker
        tol_dot = Dot(TOL_PT, radius=0.08, color=GREEN)
        tol_label = Text("TOL", font_size=16, color=GREEN).next_to(tol_dot, DOWN, buff=0.1)

        # Zone labels
        sssi_centroid = _centroid(SSSI_PTS)
        search_centroid = _centroid(SEARCH_PTS)
        sssi_label = Text("SSSI No-Fly Zone", font_size=14, color=RED)
        sssi_label.move_to(sssi_centroid)
        search_label = Text("Search Area", font_size=14, color=BLUE)
        search_label.move_to(search_centroid + np.array([0, -0.25, 0]))

        # Flight area label
        flight_centroid = _centroid(FLIGHT_PTS)
        flight_label = Text("Flight Area", font_size=12, color=GREY_B)
        flight_label.next_to(
            Polygon(*FLIGHT_PTS, stroke_opacity=0), DOWN, buff=0.08
        )

        # ── Animate ──
        # 0.0-0.5s: title
        self.play(
            FadeIn(title, shift=DOWN * 0.2),
            FadeIn(subtitle),
            run_time=0.5,
        )

        # 0.5-1.5s: flight area boundary
        self.play(Create(flight_poly), FadeIn(flight_label), run_time=1.0)

        # 1.5-2.5s: SSSI
        self.play(
            FadeIn(sssi_poly),
            FadeIn(sssi_label),
            run_time=1.0,
        )

        # 2.5-3.5s: search area
        self.play(
            FadeIn(search_poly),
            FadeIn(search_label),
            run_time=1.0,
        )

        # 3.5-4.0s: TOL
        self.play(
            FadeIn(tol_dot, scale=0.5),
            FadeIn(tol_label),
            run_time=0.5,
        )

        # 4.0-5.0s: hold
        self.wait(1.0)


# ═══════════════════════════════════════════════════════════════
#  SCENE 2: TRANSIT (5 seconds)
# ═══════════════════════════════════════════════════════════════

class TransitScene(Scene):
    def construct(self):
        # ── Background zones (dimmed) ──
        flight_poly, search_poly, sssi_poly = _make_zones(dim=True)
        self.add(flight_poly, search_poly, sssi_poly)

        # TOL dot
        tol_dot = Dot(TOL_PT, radius=0.06, color=GREEN)
        tol_label = Text("TOL", font_size=13, color=GREEN).next_to(tol_dot, DOWN, buff=0.08)
        self.add(tol_dot, tol_label)

        # ── Drone ──
        drone = _make_drone(0.12)
        drone.move_to(TOL_PT)

        # ── Altitude gauge (right side) ──
        gauge_x = 3.2
        gauge_bottom = -2.5
        gauge_height = 2.0  # full height = 35 m

        gauge_bg = Rectangle(
            width=0.18, height=gauge_height,
            fill_color=DARK_GREY, fill_opacity=0.6,
            stroke_color=GREY, stroke_width=1,
        ).move_to(np.array([gauge_x, gauge_bottom + gauge_height / 2, 0]))
        gauge_fill = Rectangle(
            width=0.14, height=0.01,
            fill_color=TEAL, fill_opacity=0.9,
            stroke_width=0,
        )
        gauge_fill.move_to(np.array([gauge_x, gauge_bottom, 0]), aligned_edge=DOWN)

        alt_text = Text("0 m", font_size=13, color=TEAL)
        alt_text.next_to(gauge_bg, RIGHT, buff=0.1).align_to(gauge_bg, DOWN)

        gauge_label = Text("Alt", font_size=11, color=GREY_B)
        gauge_label.next_to(gauge_bg, UP, buff=0.05)

        self.add(gauge_bg, gauge_fill, alt_text, gauge_label)

        # ── State badge (top right) ──
        state_bg = RoundedRectangle(
            corner_radius=0.05, width=2.4, height=0.35,
            fill_color=DARK_GREY, fill_opacity=0.8,
            stroke_width=0,
        ).to_corner(UR, buff=0.15)
        state_text = Text("ARMING", font_size=14, color=YELLOW)
        state_text.move_to(state_bg)
        state_group = VGroup(state_bg, state_text)
        self.add(state_group)

        # Speed label
        speed_label = Text("15 m/s", font_size=14, color=YELLOW)
        speed_label.next_to(state_bg, DOWN, buff=0.1)

        # ── Animate ──

        # 0.0-0.5s: drone appears, ARMING
        self.play(FadeIn(drone, scale=0.5), run_time=0.5)

        # 0.5-1.5s: takeoff -- altitude 0->35, state TAKEOFF
        new_state = Text("TAKEOFF", font_size=14, color=YELLOW).move_to(state_bg)
        self.play(
            Transform(state_text, new_state),
            gauge_fill.animate.stretch_to_fit_height(gauge_height).move_to(
                np.array([gauge_x, gauge_bottom, 0]), aligned_edge=DOWN
            ),
            run_time=1.0,
        )
        new_alt = Text("35 m", font_size=13, color=TEAL)
        new_alt.next_to(gauge_bg, RIGHT, buff=0.1).align_to(gauge_bg, UP)
        self.play(Transform(alt_text, new_alt), run_time=0.2)

        # 1.5-2.0s: state PRE_WAYPOINTS, speed appears, start to T1
        new_state2 = Text("PRE_WAYPOINTS", font_size=12, color=YELLOW).move_to(state_bg)
        self.play(
            Transform(state_text, new_state2),
            FadeIn(speed_label),
            run_time=0.3,
        )

        # Build transit waypoints: TOL -> T1 -> T2 -> T3
        path_points = [TOL_PT] + TRANSIT_PTS
        wp_names = ["T1", "T2", "T3"]

        # Traced path (yellow dashed)
        traced = TracedPath(drone.get_center, stroke_color=YELLOW,
                            stroke_width=2, stroke_opacity=0.8)
        self.add(traced)

        # 2.0-4.5s: fly TOL -> T1 -> T2 -> T3
        segment_times = [0.5, 1.0, 1.0]  # seconds per segment
        for i in range(3):
            target = path_points[i + 1]
            angle = _angle_between(path_points[i], target)
            drone.rotate(angle - drone.get_angle() if hasattr(drone, '_angle') else angle - PI / 2)

            # Waypoint dot + label on arrival
            wp_dot = Dot(target, radius=0.05, color=YELLOW)
            wp_label = Text(wp_names[i], font_size=13, color=YELLOW)
            wp_label.next_to(wp_dot, DOWN, buff=0.06)

            self.play(
                drone.animate.move_to(target).rotate(
                    _angle_between(path_points[i], target) - PI / 2
                    if i == 0 else
                    _angle_between(path_points[i], target)
                    - _angle_between(path_points[max(0, i - 1)], path_points[i])
                ),
                run_time=segment_times[i],
            )
            self.play(FadeIn(wp_dot), FadeIn(wp_label), run_time=0.1)

        # 4.5-5.0s: state TRANSIT_TO_SEARCH, drone moves toward search entry
        new_state3 = Text("TRANSIT_TO_SEARCH", font_size=10, color=YELLOW).move_to(state_bg)
        search_entry = SEARCH_PTS[0]  # first search polygon corner
        self.play(
            Transform(state_text, new_state3),
            drone.animate.move_to(search_entry),
            run_time=0.5,
        )


# ═══════════════════════════════════════════════════════════════
#  SCENE 3: SEARCH PATTERN (8 seconds)
# ═══════════════════════════════════════════════════════════════

class SearchScene(Scene):
    def construct(self):
        # ── Background zones ──
        flight_poly, search_poly, sssi_poly = _make_zones(dim=True)
        # Slightly brighter search area
        search_poly_vis = Polygon(*SEARCH_PTS, fill_color=BLUE_C, fill_opacity=0.10,
                                  stroke_color=BLUE, stroke_width=1.5)
        self.add(flight_poly, search_poly_vis, sssi_poly)

        # NFZ buffer polygon (30m inset toward search area)
        # Approximate: shrink SSSI toward its centroid by buffer distance in screen
        sssi_centroid = _centroid(SSSI_PTS)
        buffer_screen = m2s(NFZ_WAYPOINT_BUFFER_M)
        nfz_buffer_pts = []
        for pt in SSSI_PTS:
            d = pt - sssi_centroid
            norm = np.linalg.norm(d[:2])
            if norm > 1e-6:
                shrunk = sssi_centroid + d * max(0, (norm + buffer_screen)) / norm
            else:
                shrunk = pt.copy()
            nfz_buffer_pts.append(shrunk)

        nfz_buffer_raw = Polygon(*nfz_buffer_pts, color=PINK, stroke_width=1, stroke_opacity=0.5,
                                 fill_opacity=0)
        nfz_buffer = DashedVMobject(nfz_buffer_raw, num_dashes=20)
        nfz_buffer_label = Text("NFZ Buffer 30m", font_size=10, color=PINK)
        nfz_buffer_label.move_to(sssi_centroid + np.array([0, 0.6, 0]))

        # ── Generate lawnmower pattern ──
        strip_spacing_m = GROUND_FOOTPRINT_W_M * 0.8  # ~25.7 m
        scan_lines = generate_lawnmower(SEARCH_PTS, strip_spacing_m)
        waypoints = _build_waypoint_path(scan_lines)

        if not waypoints:
            self.add(Text("No waypoints generated", color=RED))
            self.wait(2)
            return

        # Draw faint upcoming pattern
        pattern_lines = VGroup()
        for s, e in scan_lines:
            pattern_lines.add(Line(s, e, stroke_color=WHITE, stroke_width=0.5, stroke_opacity=0.2))
        self.add(pattern_lines)

        # ── Drone + camera footprint ──
        drone = _make_drone(0.10)
        drone.move_to(waypoints[0])

        fw = m2s(GROUND_FOOTPRINT_W_M)
        fh = m2s(GROUND_FOOTPRINT_H_M)
        cam_footprint = Rectangle(
            width=fw, height=fh,
            stroke_color=TEAL, stroke_width=1.5,
            fill_opacity=0.05, fill_color=TEAL,
        )
        cam_footprint.move_to(waypoints[0])

        # Always keep footprint with drone
        cam_footprint.add_updater(lambda m: m.move_to(drone.get_center()))

        # ── State badge ──
        state_bg = RoundedRectangle(
            corner_radius=0.05, width=2.0, height=0.3,
            fill_color=DARK_GREY, fill_opacity=0.8,
            stroke_width=0,
        ).to_corner(UR, buff=0.15)
        state_text = Text("SEARCH", font_size=14, color=YELLOW).move_to(state_bg)
        speed_label = Text("8 m/s", font_size=13, color=YELLOW)
        speed_label.next_to(state_bg, DOWN, buff=0.08)

        # ── Coverage counter ──
        coverage_text = Text("Coverage: 0%", font_size=16, color=GREEN)
        coverage_text.to_corner(UL, buff=0.2)

        # ── Coverage strips (filled as drone passes) ──
        coverage_strips = VGroup()

        self.add(state_bg, state_text, speed_label, coverage_text)

        # ── Animate ──

        # 0.0-0.5s: drone enters, footprint appears
        self.play(FadeIn(drone, scale=0.5), FadeIn(cam_footprint), run_time=0.5)

        # Add NFZ buffer
        self.play(FadeIn(nfz_buffer), FadeIn(nfz_buffer_label), run_time=0.3)

        # 0.5-7.0s: fly the lawnmower pattern
        total_strips = len(scan_lines)
        # Time per strip: distribute ~6.5s across all strips
        time_per_strip = 6.2 / max(total_strips, 1)

        for idx, (s, e) in enumerate(scan_lines):
            # Move drone along scan line (start -> end)
            self.play(
                drone.animate.move_to(s),
                run_time=min(time_per_strip * 0.15, 0.15),
                rate_func=linear,
            )
            self.play(
                drone.animate.move_to(e),
                run_time=time_per_strip * 0.85,
                rate_func=linear,
            )

            # Add coverage strip
            strip_rect = Line(s, e, stroke_color=GREEN, stroke_width=max(fw * 8, 3),
                              stroke_opacity=0.2)
            coverage_strips.add(strip_rect)
            self.add(strip_rect)

            # Update coverage counter
            pct = int(100 * (idx + 1) / total_strips)
            new_cov = Text(f"Coverage: {pct}%", font_size=16, color=GREEN)
            new_cov.to_corner(UL, buff=0.2)
            self.remove(coverage_text)
            coverage_text = new_cov
            self.add(coverage_text)

        # 7.0-8.0s: hold
        self.wait(1.0)


# ═══════════════════════════════════════════════════════════════
#  SCENE 4: BEACON / PLB REDIRECT (4 seconds)
# ═══════════════════════════════════════════════════════════════

class BeaconScene(Scene):
    def construct(self):
        # ── Background zones (dimmed) ──
        flight_poly, search_poly, sssi_poly = _make_zones(dim=True)
        self.add(flight_poly, search_poly, sssi_poly)

        # Faint old coverage (show drone was searching)
        strip_spacing_m = GROUND_FOOTPRINT_W_M * 0.8
        old_scan_lines = generate_lawnmower(SEARCH_PTS, strip_spacing_m)
        old_coverage = VGroup()
        fw = m2s(GROUND_FOOTPRINT_W_M)
        # Show first ~60% of strips as faint green
        show_count = int(len(old_scan_lines) * 0.6)
        for s, e in old_scan_lines[:show_count]:
            old_coverage.add(
                Line(s, e, stroke_color=GREEN, stroke_width=max(fw * 8, 3),
                     stroke_opacity=0.1)
            )
        self.add(old_coverage)

        # Drone mid-search
        drone = _make_drone(0.10)
        if show_count > 0:
            drone.move_to(old_scan_lines[show_count - 1][1])
        else:
            drone.move_to(SEARCH_PTS[0])
        self.add(drone)

        # State badge
        state_bg = RoundedRectangle(
            corner_radius=0.05, width=2.0, height=0.3,
            fill_color=DARK_GREY, fill_opacity=0.8,
            stroke_width=0,
        ).to_corner(UR, buff=0.15)
        state_text = Text("SEARCH", font_size=14, color=YELLOW).move_to(state_bg)
        speed_label = Text("8 m/s", font_size=13, color=YELLOW)
        speed_label.next_to(state_bg, DOWN, buff=0.08)
        self.add(state_bg, state_text, speed_label)

        # Focus area centroid
        focus_centroid = _centroid(FOCUS_PTS)

        # ── 0.0-0.5s: PLB FLASH ──
        plb_text = Text("PLB SIGNAL RECEIVED", font_size=36, color=ORANGE, weight=BOLD)
        plb_text.move_to(ORIGIN + UP * 0.5)

        # Radio rings
        rings = VGroup()
        for r in [0.3, 0.6, 0.9]:
            ring = Circle(radius=r, stroke_color=ORANGE, stroke_width=2, stroke_opacity=0.6)
            ring.move_to(focus_centroid)
            rings.add(ring)

        self.play(
            FadeIn(plb_text, scale=1.2),
            *[GrowFromCenter(ring) for ring in rings],
            run_time=0.5,
        )

        # 0.5-1.5s: focus area appears, rings fade, old coverage dims
        focus_poly = Polygon(*FOCUS_PTS, fill_color=ORANGE, fill_opacity=0.2,
                             stroke_color=ORANGE, stroke_width=2)
        focus_label = Text("Focus Area", font_size=14, color=ORANGE)
        focus_label.next_to(focus_poly, DOWN, buff=0.08)

        self.play(
            FadeOut(plb_text),
            FadeOut(rings),
            FadeIn(focus_poly),
            FadeIn(focus_label),
            old_coverage.animate.set_opacity(0.05),
            run_time=1.0,
        )

        # 1.5-2.5s: zoom in on focus area, generate tighter pattern, speed change
        # Generate tighter lawnmower inside focus area
        focus_strip_spacing = GROUND_FOOTPRINT_W_M * 0.6  # tighter
        focus_scan_lines = generate_lawnmower(FOCUS_PTS, focus_strip_spacing)
        focus_waypoints = _build_waypoint_path(focus_scan_lines)

        # Draw faint pattern lines
        focus_pattern = VGroup()
        for s, e in focus_scan_lines:
            focus_pattern.add(
                Line(s, e, stroke_color=WHITE, stroke_width=0.5, stroke_opacity=0.3)
            )

        # New speed
        new_speed = Text("5 m/s", font_size=13, color=YELLOW)
        new_speed.next_to(state_bg, DOWN, buff=0.08)

        # Camera zoom (scale up + shift to focus area)
        zoom_scale = 3.0
        shift_vec = -focus_centroid  # center on focus area

        # Group everything for zoom
        scene_group = VGroup(
            flight_poly, search_poly, sssi_poly, old_coverage,
            focus_poly, focus_label, drone,
        )

        self.play(
            scene_group.animate.scale(zoom_scale).shift(shift_vec * zoom_scale),
            FadeIn(focus_pattern.scale(zoom_scale).shift(shift_vec * zoom_scale)),
            Transform(speed_label, new_speed),
            run_time=1.0,
        )

        # Camera footprint (scaled)
        fh = m2s(GROUND_FOOTPRINT_H_M) * zoom_scale
        fw_s = m2s(GROUND_FOOTPRINT_W_M) * zoom_scale
        cam_footprint = Rectangle(
            width=fw_s, height=fh,
            stroke_color=TEAL, stroke_width=1.5,
            fill_opacity=0.05, fill_color=TEAL,
        )
        cam_footprint.move_to(drone.get_center())
        cam_footprint.add_updater(lambda m: m.move_to(drone.get_center()))
        self.add(cam_footprint)

        # 2.5-4.0s: fly 2-3 strips of focus pattern
        focus_coverage = VGroup()
        strips_to_show = min(3, len(focus_scan_lines))
        time_per_strip = 1.3 / max(strips_to_show, 1)

        for idx in range(strips_to_show):
            s, e = focus_scan_lines[idx]
            # Transform to zoomed coordinates
            s_z = s * zoom_scale + np.array([*shift_vec[:2] * zoom_scale, 0])
            e_z = e * zoom_scale + np.array([*shift_vec[:2] * zoom_scale, 0])

            self.play(
                drone.animate.move_to(s_z),
                run_time=time_per_strip * 0.2,
                rate_func=linear,
            )
            self.play(
                drone.animate.move_to(e_z),
                run_time=time_per_strip * 0.8,
                rate_func=linear,
            )

            # Coverage strip
            strip = Line(s_z, e_z, stroke_color=GREEN, stroke_width=max(fw_s * 6, 4),
                         stroke_opacity=0.25)
            focus_coverage.add(strip)
            self.add(strip)

        # Hold
        self.wait(0.3)
