"""
Cinematic SAR Drone Mission Animation -- Part 1 (Scenes 1-4).

Scenes:
  1. OverviewScene   (5 s) — bird's eye, all zones labelled, title
  2. TransitScene    (5 s) — takeoff, TOL -> T1 -> T2 -> T3 -> first search WP
  3. SearchScene     (8 s) — inward spiral with camera footprint, coverage fill
  4. BeaconScene     (4 s) — PLB flash, focus area, zoom in, tighter spiral at 5 m/s

Run individual scenes:
  python -m manim -ql cinematic_part1.py OverviewScene
  python -m manim -ql cinematic_part1.py TransitScene
  python -m manim -ql cinematic_part1.py SearchScene
  python -m manim -ql cinematic_part1.py BeaconScene
"""

from manim import *
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon, LineString
from shapely.ops import unary_union

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
    """Compute ref point, scale, and offset so the field fills ~80% of screen."""
    all_lats = [p[0] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
    all_lons = [p[1] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
    ref_lat = np.mean(all_lats)
    ref_lon = np.mean(all_lons)

    extents = []
    for lat, lon in FLIGHT_AREA_GPS:
        extents.append(gps_to_meters(lat, lon, ref_lat, ref_lon))
    xs = [p[0] for p in extents]
    ys = [p[1] for p in extents]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    extent = max(width, height)

    # Scale to fill ~80% of manim frame (frame is ~14 units wide at default)
    frame_size = 10.0
    scale = frame_size / extent
    offset = np.array([0.0, 0.0])
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
TRANSIT_PTS = [gps_to_screen(lat, lon) for lat, lon in TRANSIT_WAYPOINTS_GPS]


# ═══════════════════════════════════════════════════════════════
#  SPIRAL PATTERN GENERATION
# ═══════════════════════════════════════════════════════════════

def generate_spiral_path(screen_pts, strip_spacing_m, num_loops=6):
    """Generate an inward spiral path that follows the polygon shape.

    Returns a list of np.array([x, y, 0]) waypoints forming the spiral.
    The spiral starts from the outer edge and works inward.
    """
    pts_2d = [(p[0], p[1]) for p in screen_pts]
    shapely_poly = ShapelyPolygon(pts_2d)
    spacing_screen = m2s(strip_spacing_m)

    # Generate concentric inset polygons
    rings = []
    for i in range(num_loops + 1):
        inset = spacing_screen * i * 0.5
        shrunk = shapely_poly.buffer(-inset)
        if shrunk.is_empty or shrunk.area < spacing_screen * spacing_screen * 0.1:
            break
        if shrunk.geom_type == 'MultiPolygon':
            shrunk = max(shrunk.geoms, key=lambda g: g.area)
        rings.append(shrunk)

    if len(rings) < 2:
        # Fallback: just return polygon boundary
        coords = list(shapely_poly.exterior.coords)
        return [np.array([c[0], c[1], 0.0]) for c in coords]

    # Build spiral by interpolating between consecutive rings
    waypoints = []
    num_points_per_ring = 40  # points sampled around each ring

    for ring_idx in range(len(rings) - 1):
        outer_ring = rings[ring_idx]
        inner_ring = rings[ring_idx + 1]

        outer_coords = list(outer_ring.exterior.coords)[:-1]  # remove closing duplicate
        inner_coords = list(inner_ring.exterior.coords)[:-1]

        # Resample both rings to same number of points
        outer_line = LineString(list(outer_ring.exterior.coords))
        inner_line = LineString(list(inner_ring.exterior.coords))

        for j in range(num_points_per_ring):
            t = j / num_points_per_ring
            # Progress around the ring
            frac_along = t
            # Blend between outer and inner ring
            blend = (ring_idx + t) / len(rings)

            outer_pt = outer_line.interpolate(frac_along, normalized=True)
            inner_pt = inner_line.interpolate(frac_along, normalized=True)

            # Linear interpolation between outer and inner
            x = outer_pt.x * (1 - t) + inner_pt.x * t
            y = outer_pt.y * (1 - t) + inner_pt.y * t

            waypoints.append(np.array([x, y, 0.0]))

    # Add center point
    cx, cy = shapely_poly.centroid.x, shapely_poly.centroid.y
    waypoints.append(np.array([cx, cy, 0.0]))

    return waypoints


# ═══════════════════════════════════════════════════════════════
#  LAWNMOWER PATTERN GENERATION (kept for reference/coverage calc)
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
    """Generate lawnmower scan lines clipped to a polygon."""
    pts_2d = [(p[0], p[1]) for p in screen_pts]
    shapely_poly = ShapelyPolygon(pts_2d)

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


# ═══════════════════════════════════════════════════════════════
#  HELPER: build background zone polygons (used by multiple scenes)
# ═══════════════════════════════════════════════════════════════

def _make_zones(dim=False):
    """Return (flight_poly, search_poly, sssi_poly) manim objects."""
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


def _clip_footprint_to_poly(center, fw, fh, poly_pts):
    """Create a camera footprint rectangle clipped to a polygon boundary.

    Returns a manim Polygon clipped to the search area.
    """
    from shapely.geometry import box as shapely_box

    half_w = fw / 2
    half_h = fh / 2
    cx, cy = center[0], center[1]

    rect = shapely_box(cx - half_w, cy - half_h, cx + half_w, cy + half_h)
    poly_2d = [(p[0], p[1]) for p in poly_pts]
    shapely_poly = ShapelyPolygon(poly_2d)

    clipped = rect.intersection(shapely_poly)

    if clipped.is_empty:
        # Return a tiny invisible polygon
        return Polygon(
            np.array([cx, cy, 0]), np.array([cx + 0.01, cy, 0]),
            np.array([cx + 0.01, cy + 0.01, 0]),
            stroke_color=TEAL, stroke_width=1.5,
            fill_opacity=0.05, fill_color=TEAL,
        )

    if clipped.geom_type == 'MultiPolygon':
        clipped = max(clipped.geoms, key=lambda g: g.area)

    coords = list(clipped.exterior.coords)[:-1]
    pts_3d = [np.array([c[0], c[1], 0.0]) for c in coords]

    if len(pts_3d) < 3:
        return Polygon(
            np.array([cx, cy, 0]), np.array([cx + 0.01, cy, 0]),
            np.array([cx + 0.01, cy + 0.01, 0]),
            stroke_color=TEAL, stroke_width=1.5,
            fill_opacity=0.05, fill_color=TEAL,
        )

    return Polygon(*pts_3d,
                   stroke_color=TEAL, stroke_width=1.5,
                   fill_opacity=0.05, fill_color=TEAL)


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
        tol_dot = Dot(TOL_PT, radius=0.10, color=GREEN)
        tol_label = Text("TOL", font_size=18, color=GREEN).next_to(tol_dot, DOWN, buff=0.12)

        # Zone labels
        sssi_centroid = _centroid(SSSI_PTS)
        search_centroid = _centroid(SEARCH_PTS)
        sssi_label = Text("SSSI No-Fly Zone", font_size=16, color=RED)
        sssi_label.move_to(sssi_centroid)
        search_label = Text("Search Area", font_size=16, color=BLUE)
        search_label.move_to(search_centroid + np.array([0, -0.3, 0]))

        # Flight area label
        flight_label = Text("Flight Area", font_size=14, color=GREY_B)
        flight_label.next_to(
            Polygon(*FLIGHT_PTS, stroke_opacity=0), DOWN, buff=0.1
        )

        # Animate
        self.play(
            FadeIn(title, shift=DOWN * 0.2),
            FadeIn(subtitle),
            run_time=0.5,
        )
        self.play(Create(flight_poly), FadeIn(flight_label), run_time=1.0)
        self.play(FadeIn(sssi_poly), FadeIn(sssi_label), run_time=1.0)
        self.play(FadeIn(search_poly), FadeIn(search_label), run_time=1.0)
        self.play(FadeIn(tol_dot, scale=0.5), FadeIn(tol_label), run_time=0.5)
        self.wait(1.0)


# ═══════════════════════════════════════════════════════════════
#  SCENE 2: TRANSIT (5 seconds)
# ═══════════════════════════════════════════════════════════════

class TransitScene(Scene):
    def construct(self):
        # Background zones (dimmed)
        flight_poly, search_poly, sssi_poly = _make_zones(dim=True)
        self.add(flight_poly, search_poly, sssi_poly)

        # TOL dot
        tol_dot = Dot(TOL_PT, radius=0.08, color=GREEN)
        tol_label = Text("TOL", font_size=14, color=GREEN).next_to(tol_dot, DOWN, buff=0.08)
        self.add(tol_dot, tol_label)

        # Drone
        drone = _make_drone(0.14)
        drone.move_to(TOL_PT)

        # Compute the first search waypoint (closest search polygon vertex to T3)
        t3_pt = TRANSIT_PTS[2]
        dists = [np.linalg.norm(sp - t3_pt) for sp in SEARCH_PTS]
        first_search_wp = SEARCH_PTS[np.argmin(dists)]

        # State badge (top right)
        state_bg = RoundedRectangle(
            corner_radius=0.05, width=2.4, height=0.35,
            fill_color=DARK_GREY, fill_opacity=0.8,
            stroke_width=0,
        ).to_corner(UR, buff=0.15)
        state_text = Text("ARMING", font_size=14, color=YELLOW)
        state_text.move_to(state_bg)
        self.add(state_bg, state_text)

        # Speed label
        speed_label = Text("15 m/s", font_size=14, color=YELLOW)
        speed_label.next_to(state_bg, DOWN, buff=0.1)

        # Small altitude indicator (compact, left side)
        alt_label = Text("ALT: 0 m", font_size=13, color=TEAL)
        alt_label.to_corner(UL, buff=0.2)

        self.add(alt_label)

        # Animate

        # 0.0-0.5s: drone appears
        self.play(FadeIn(drone, scale=0.5), run_time=0.5)

        # 0.5-1.3s: takeoff
        new_state = Text("TAKEOFF", font_size=14, color=YELLOW).move_to(state_bg)
        new_alt = Text("ALT: 35 m", font_size=13, color=TEAL).to_corner(UL, buff=0.2)
        self.play(
            Transform(state_text, new_state),
            Transform(alt_label, new_alt),
            run_time=0.8,
        )

        # 1.3-1.6s: state PRE_WAYPOINTS
        new_state2 = Text("PRE_WAYPOINTS", font_size=12, color=YELLOW).move_to(state_bg)
        self.play(
            Transform(state_text, new_state2),
            FadeIn(speed_label),
            run_time=0.3,
        )

        # Build transit path: TOL -> T1 -> T2 -> T3
        path_points = [TOL_PT] + TRANSIT_PTS
        wp_names = ["T1", "T2", "T3"]

        # Traced path
        traced = TracedPath(drone.get_center, stroke_color=YELLOW,
                            stroke_width=2, stroke_opacity=0.8)
        self.add(traced)

        # 1.6-3.7s: fly TOL -> T1 -> T2 -> T3
        segment_times = [0.5, 0.8, 0.8]
        for i in range(3):
            target = path_points[i + 1]
            angle = _angle_between(path_points[i], target)

            wp_dot = Dot(target, radius=0.06, color=YELLOW)
            wp_label = Text(wp_names[i], font_size=14, color=YELLOW)
            wp_label.next_to(wp_dot, DOWN, buff=0.06)

            self.play(
                drone.animate.move_to(target),
                run_time=segment_times[i],
                rate_func=linear,
            )
            self.play(FadeIn(wp_dot), FadeIn(wp_label), run_time=0.1)

        # 3.7-4.5s: T3 -> first search waypoint (smooth transition)
        new_state3 = Text("TRANSIT_TO_SEARCH", font_size=10, color=YELLOW).move_to(state_bg)
        self.play(
            Transform(state_text, new_state3),
            drone.animate.move_to(first_search_wp),
            run_time=0.8,
            rate_func=smooth,
        )

        # Entry dot
        entry_dot = Dot(first_search_wp, radius=0.06, color=BLUE)
        entry_label = Text("Search Entry", font_size=12, color=BLUE)
        entry_label.next_to(entry_dot, DOWN, buff=0.06)
        self.play(FadeIn(entry_dot), FadeIn(entry_label), run_time=0.3)

        self.wait(0.3)


# ═══════════════════════════════════════════════════════════════
#  SCENE 3: SEARCH PATTERN -- SPIRAL (8 seconds)
# ═══════════════════════════════════════════════════════════════

class SearchScene(Scene):
    def construct(self):
        # Background zones
        flight_poly, search_poly, sssi_poly = _make_zones(dim=True)
        search_poly_vis = Polygon(*SEARCH_PTS, fill_color=BLUE_C, fill_opacity=0.10,
                                  stroke_color=BLUE, stroke_width=1.5)
        self.add(flight_poly, search_poly_vis, sssi_poly)

        # Generate spiral waypoints
        strip_spacing_m = GROUND_FOOTPRINT_W_M * 0.8
        spiral_wps = generate_spiral_path(SEARCH_PTS, strip_spacing_m, num_loops=10)

        if len(spiral_wps) < 2:
            self.add(Text("No spiral waypoints generated", color=RED))
            self.wait(2)
            return

        # Draw faint spiral preview
        spiral_preview = VGroup()
        for i in range(len(spiral_wps) - 1):
            spiral_preview.add(
                Line(spiral_wps[i], spiral_wps[i + 1],
                     stroke_color=WHITE, stroke_width=0.5, stroke_opacity=0.15)
            )
        self.add(spiral_preview)

        # Drone
        drone = _make_drone(0.12)
        drone.move_to(spiral_wps[0])

        # Camera footprint dimensions
        fw = m2s(GROUND_FOOTPRINT_W_M)
        fh = m2s(GROUND_FOOTPRINT_H_M)

        # Clipped camera footprint (updated each frame)
        cam_footprint = _clip_footprint_to_poly(spiral_wps[0], fw, fh, SEARCH_PTS)
        self.add(cam_footprint)

        # State badge
        state_bg = RoundedRectangle(
            corner_radius=0.05, width=2.0, height=0.3,
            fill_color=DARK_GREY, fill_opacity=0.8,
            stroke_width=0,
        ).to_corner(UR, buff=0.15)
        state_text = Text("SEARCH", font_size=14, color=YELLOW).move_to(state_bg)
        speed_label = Text("8 m/s", font_size=13, color=YELLOW)
        speed_label.next_to(state_bg, DOWN, buff=0.08)

        # Coverage counter
        coverage_text = Text("Coverage: 0%", font_size=16, color=GREEN)
        coverage_text.to_corner(UL, buff=0.2)

        self.add(state_bg, state_text, speed_label, coverage_text)

        # Animate

        # 0.0-0.5s: drone enters
        self.play(FadeIn(drone, scale=0.5), run_time=0.5)

        # 0.5-7.0s: fly the spiral
        # Group waypoints into segments for smooth animation
        total_wps = len(spiral_wps)
        num_segments = min(20, total_wps - 1)  # animate in chunks
        segment_size = max(1, (total_wps - 1) // num_segments)
        time_per_segment = 6.0 / num_segments

        # Shapely polygon for coverage tracking
        search_shapely = ShapelyPolygon([(p[0], p[1]) for p in SEARCH_PTS])
        covered_area = None

        for seg_idx in range(num_segments):
            start_idx = seg_idx * segment_size
            end_idx = min(start_idx + segment_size, total_wps - 1)
            if start_idx >= total_wps - 1:
                break

            target_pt = spiral_wps[end_idx]

            # Remove old footprint
            self.remove(cam_footprint)

            # Move drone
            self.play(
                drone.animate.move_to(target_pt),
                run_time=time_per_segment,
                rate_func=linear,
            )

            # Add coverage trail (circle around each visited point, clipped)
            for wp_idx in range(start_idx, end_idx + 1):
                wp = spiral_wps[wp_idx]
                from shapely.geometry import Point as ShapelyPoint
                cov_circle = ShapelyPoint(wp[0], wp[1]).buffer(fw * 0.4)
                cov_clipped = cov_circle.intersection(search_shapely)
                if not cov_clipped.is_empty:
                    if covered_area is None:
                        covered_area = cov_clipped
                    else:
                        covered_area = covered_area.union(cov_clipped)

            # Draw coverage fill
            if covered_area is not None and not covered_area.is_empty:
                pct = int(100 * covered_area.area / search_shapely.area)
                pct = min(pct, 100)
            else:
                pct = 0

            # Add a small green trail segment
            if end_idx > 0:
                trail_line = Line(
                    spiral_wps[start_idx], spiral_wps[end_idx],
                    stroke_color=GREEN, stroke_width=max(fw * 5, 3),
                    stroke_opacity=0.15,
                )
                self.add(trail_line)

            # New clipped footprint
            cam_footprint = _clip_footprint_to_poly(target_pt, fw, fh, SEARCH_PTS)
            self.add(cam_footprint)

            # Update coverage text
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
        # Background zones (dimmed)
        flight_poly, search_poly, sssi_poly = _make_zones(dim=True)
        self.add(flight_poly, search_poly, sssi_poly)

        # Show partial coverage from earlier search
        fw = m2s(GROUND_FOOTPRINT_W_M)

        # Generate partial spiral coverage (first 60%)
        strip_spacing_m = GROUND_FOOTPRINT_W_M * 0.8
        spiral_wps = generate_spiral_path(SEARCH_PTS, strip_spacing_m, num_loops=10)
        show_count = int(len(spiral_wps) * 0.4)

        old_coverage = VGroup()
        for i in range(0, show_count - 1, 2):
            old_coverage.add(
                Line(spiral_wps[i], spiral_wps[i + 1],
                     stroke_color=GREEN, stroke_width=max(fw * 5, 3),
                     stroke_opacity=0.1)
            )
        self.add(old_coverage)

        # Drone mid-search
        drone = _make_drone(0.12)
        if show_count > 0:
            drone.move_to(spiral_wps[show_count - 1])
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

        # 0.0-0.5s: PLB FLASH
        plb_text = Text("PLB SIGNAL RECEIVED", font_size=36, color=ORANGE, weight=BOLD)
        plb_text.move_to(ORIGIN + UP * 0.5)

        rings = VGroup()
        for r in [0.4, 0.8, 1.2]:
            ring = Circle(radius=r, stroke_color=ORANGE, stroke_width=2, stroke_opacity=0.6)
            ring.move_to(focus_centroid)
            rings.add(ring)

        self.play(
            FadeIn(plb_text, scale=1.2),
            *[GrowFromCenter(ring) for ring in rings],
            run_time=0.5,
        )

        # 0.5-1.2s: focus area appears, rings fade
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
            run_time=0.7,
        )

        # 1.2-2.0s: zoom in on focus area + speed change
        # Generate spiral inside focus area
        focus_spiral_wps = generate_spiral_path(FOCUS_PTS, GROUND_FOOTPRINT_W_M * 0.5, num_loops=4)

        # New speed label
        new_speed = Text("5 m/s", font_size=13, color=YELLOW)
        new_speed.next_to(state_bg, DOWN, buff=0.08)

        new_state = Text("BEACON_REDIRECT", font_size=11, color=ORANGE).move_to(state_bg)

        # Zoom: scale up and center on focus area
        zoom_scale = 4.0
        shift_vec = -focus_centroid

        # Group everything for zoom
        scene_group = VGroup(
            flight_poly, search_poly, sssi_poly, old_coverage,
            focus_poly, focus_label, drone,
        )

        # Draw faint focus spiral (in pre-zoom coords, will be scaled with group)
        focus_spiral_preview = VGroup()
        for i in range(len(focus_spiral_wps) - 1):
            focus_spiral_preview.add(
                Line(focus_spiral_wps[i], focus_spiral_wps[i + 1],
                     stroke_color=WHITE, stroke_width=0.5, stroke_opacity=0.3)
            )

        self.play(
            scene_group.animate.scale(zoom_scale).shift(shift_vec * zoom_scale),
            FadeIn(focus_spiral_preview.scale(zoom_scale).shift(shift_vec * zoom_scale)),
            Transform(speed_label, new_speed),
            Transform(state_text, new_state),
            run_time=0.8,
        )

        # 2.0-3.7s: fly focus spiral (zoomed coordinates)
        # Camera footprint (scaled)
        fh_z = m2s(GROUND_FOOTPRINT_H_M) * zoom_scale
        fw_z = m2s(GROUND_FOOTPRINT_W_M) * zoom_scale

        cam_footprint = Rectangle(
            width=fw_z, height=fh_z,
            stroke_color=TEAL, stroke_width=1.5,
            fill_opacity=0.05, fill_color=TEAL,
        )
        cam_footprint.move_to(drone.get_center())
        cam_footprint.add_updater(lambda m: m.move_to(drone.get_center()))
        self.add(cam_footprint)

        # Fly through focus spiral waypoints
        focus_coverage = VGroup()
        num_focus_wps = len(focus_spiral_wps)
        segments_to_show = min(8, num_focus_wps - 1)
        seg_size = max(1, (num_focus_wps - 1) // segments_to_show)
        time_per = 1.5 / max(segments_to_show, 1)

        for seg_idx in range(segments_to_show):
            start_i = seg_idx * seg_size
            end_i = min(start_i + seg_size, num_focus_wps - 1)
            if start_i >= num_focus_wps - 1:
                break

            target = focus_spiral_wps[end_i]
            # Transform to zoomed coordinates
            t_z = target * zoom_scale + np.array([*shift_vec[:2] * zoom_scale, 0])

            self.play(
                drone.animate.move_to(t_z),
                run_time=time_per,
                rate_func=linear,
            )

            # Coverage trail
            if end_i > 0:
                s_z = focus_spiral_wps[start_i] * zoom_scale + np.array([*shift_vec[:2] * zoom_scale, 0])
                strip = Line(s_z, t_z, stroke_color=GREEN,
                             stroke_width=max(fw_z * 4, 4), stroke_opacity=0.2)
                focus_coverage.add(strip)
                self.add(strip)

        # 3.7-4.0s: detection flash
        det_flash = Circle(radius=0.3, stroke_color=RED, stroke_width=3,
                           fill_color=RED, fill_opacity=0.3)
        det_flash.move_to(drone.get_center())
        det_label = Text("TARGET DETECTED", font_size=16, color=RED, weight=BOLD)
        det_label.next_to(det_flash, UP, buff=0.15)

        self.play(
            GrowFromCenter(det_flash),
            FadeIn(det_label),
            run_time=0.3,
        )

        self.wait(0.2)
