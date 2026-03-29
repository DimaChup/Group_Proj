"""
Lawnmower Search Pattern Animation — Fenswood Farm SAR Drone.

Shows the full mission: takeoff, transit via T1-T2-T3, lawnmower search with
coverage (scan lines clipped to polygon, inset from edges, avoiding SSSI NFZ),
detection, verification, offset landing, and return.

Run:
  python -m manim -pqh lawnmower_anim.py SearchPatternExecution
  python -m manim -pql lawnmower_anim.py SearchPatternExecution   # low quality (fast)
"""

from manim import *
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon, LineString, MultiLineString


# ── GPS coordinates from config.py (AENGM0074.kml) ──────────────
SEARCH_AREA_GPS = [
    (51.42326956502679, -2.670948345438704),
    (51.42287025017865, -2.670045428650557),
    (51.42336622593724, -2.668169295906676),
    (51.42421477437771, -2.668809768621569),
    (51.42354069739116, -2.671277780473196),
]
FLIGHT_AREA_GPS = [
    (51.42342595349562, -2.671720766408759),
    (51.42124623420381, -2.670134027271237),
    (51.42244011936099, -2.66568781888585),
    (51.42469179370701, -2.667060227266051),
]
SSSI_GPS = [
    (51.42353586816967, -2.671451754138619),
    (51.42215640321154, -2.669768242108598),
    (51.42267105383615, -2.667705438815299),
    (51.42335592245168, -2.668164601092489),
    (51.42286082606338, -2.670043418345824),
    (51.42326667015552, -2.670965419051837),
    (51.42356862274763, -2.671324297543731),
]
TAKEOFF_GPS = (51.42340640206451, -2.671446029622069)

# Transit waypoints from flight_plans/transit.json
TRANSIT_GPS = [
    (51.421764800829834, -2.6701173714965023),  # T1
    (51.422474266363814, -2.667138823903503),    # T2
    (51.42410411961755, -2.6683086927255597),    # T3
]

# Camera / mission parameters from config.py
SENSOR_WIDTH_MM = 5.02
FOCAL_LENGTH_MM = 5.46
TARGET_ALT = 35.0
IMAGE_W = 1456
IMAGE_H = 1088
NFZ_WAYPOINT_BUFFER_M = 30.0


def gps_to_meters(lat, lon, ref_lat, ref_lon):
    """Convert GPS to local meters (East, North) from reference point."""
    dlat = lat - ref_lat
    dlon = lon - ref_lon
    north = dlat * 111320.0
    east = dlon * 111320.0 * np.cos(np.radians(ref_lat))
    return east, north


def gps_poly_to_screen(gps_coords, ref_lat, ref_lon, scale, offset):
    """Convert GPS polygon to manim screen coordinates."""
    pts = []
    for lat, lon in gps_coords:
        ex, ny = gps_to_meters(lat, lon, ref_lat, ref_lon)
        sx = ex * scale + offset[0]
        sy = ny * scale + offset[1]
        pts.append([sx, sy, 0])
    return pts


def gps_to_screen(lat, lon, ref_lat, ref_lon, scale, offset):
    """Convert a single GPS point to manim screen coordinates."""
    ex, ny = gps_to_meters(lat, lon, ref_lat, ref_lon)
    return np.array([ex * scale + offset[0], ny * scale + offset[1], 0])


def _compute_scan_angle(search_pts_screen):
    """Compute the optimal scan angle aligned to the polygon's longest edge,
    matching planning.py's minAreaRect approach."""
    pts_2d = np.array(search_pts_screen)[:, :2]
    n = len(pts_2d)
    best_len = 0
    best_angle = 0
    for i in range(n):
        j = (i + 1) % n
        dx = pts_2d[j][0] - pts_2d[i][0]
        dy = pts_2d[j][1] - pts_2d[i][1]
        edge_len = np.hypot(dx, dy)
        if edge_len > best_len:
            best_len = edge_len
            best_angle = np.degrees(np.arctan2(dy, dx))
    return best_angle


def _compute_num_lines(search_pts_screen):
    """Compute the number of scan lines based on camera footprint at TARGET_ALT,
    matching planning.py's strip spacing calculation."""
    # Ground footprint perpendicular to flight (using image height / width ratio)
    ground_footprint_m = (SENSOR_WIDTH_MM * TARGET_ALT) / FOCAL_LENGTH_MM
    aspect = IMAGE_H / IMAGE_W
    swath_m = ground_footprint_m * aspect  # no-turn mode: use height dimension, 0% overlap

    # Compute polygon extent perpendicular to scan direction
    pts_2d = np.array(search_pts_screen)[:, :2]
    angle = _compute_scan_angle([[p[0], p[1], 0] for p in pts_2d])
    theta = np.radians(-angle)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    cx, cy = pts_2d.mean(axis=0)

    rotated = []
    for p in pts_2d:
        d = p - np.array([cx, cy])
        rotated.append([d[0] * cos_t - d[1] * sin_t, d[0] * sin_t + d[1] * cos_t])
    rotated = np.array(rotated)
    perp_extent = rotated[:, 1].max() - rotated[:, 1].min()

    # Convert swath to screen units: need meters-to-screen scale
    # Approximate from the polygon's GPS extent
    search_lats = [p[0] for p in SEARCH_AREA_GPS]
    search_lons = [p[1] for p in SEARCH_AREA_GPS]
    lat_range = max(search_lats) - min(search_lats)
    lon_range = max(search_lons) - min(search_lons)
    meters_range = max(lat_range * 111320, lon_range * 111320 * np.cos(np.radians(np.mean(search_lats))))

    screen_pts = np.array(search_pts_screen)[:, :2]
    screen_range = max(screen_pts[:, 0].max() - screen_pts[:, 0].min(),
                       screen_pts[:, 1].max() - screen_pts[:, 1].min())
    m_to_screen = screen_range / meters_range if meters_range > 0 else 1.0

    swath_screen = swath_m * m_to_screen
    num_lines = max(2, int(np.ceil(perp_extent / swath_screen)))
    return num_lines


def generate_lawnmower_lines(search_pts_screen, sssi_pts_screen, nfz_buffer_m, m_to_screen):
    """Generate lawnmower scan lines clipped to the search polygon and avoiding
    the SSSI NFZ buffer zone. Lines are inset from edges (matching planning.py).

    Returns list of (start, end) point pairs in screen coords."""
    pts = np.array(search_pts_screen)[:, :2]
    cx, cy = pts.mean(axis=0)

    # Use longest-edge alignment (like planning.py's minAreaRect)
    angle_deg = _compute_scan_angle(search_pts_screen)
    num_lines = _compute_num_lines(search_pts_screen)

    # Rotate polygon to align scan lines with x-axis
    theta = np.radians(-angle_deg)
    cos_t, sin_t = np.cos(theta), np.sin(theta)

    def rotate(p, around):
        d = p - around
        return around + np.array([
            d[0] * cos_t - d[1] * sin_t,
            d[0] * sin_t + d[1] * cos_t
        ])

    def inv_rotate(p, around):
        d = p - around
        return around + np.array([
            d[0] * cos_t + d[1] * sin_t,
            -d[0] * sin_t + d[1] * cos_t
        ])

    center = np.array([cx, cy])
    rotated = np.array([rotate(p, center) for p in pts])

    y_min, y_max = rotated[:, 1].min(), rotated[:, 1].max()
    x_min, x_max = rotated[:, 0].min(), rotated[:, 0].max()

    # Inset margin (matching planning.py: strip_spacing // 3)
    strip_spacing = (y_max - y_min) / num_lines
    inset = strip_spacing / 3.0
    ys = np.linspace(y_min + inset, y_max - inset, num_lines)

    # Build Shapely polygon for clipping
    search_poly_2d = [(p[0], p[1]) for p in pts]
    search_shapely = ShapelyPolygon(search_poly_2d)
    # Inset the polygon slightly for scan line clipping (like planning.py inset_px)
    search_inset = search_shapely.buffer(-inset * 0.3)
    if search_inset.is_empty:
        search_inset = search_shapely

    # Build NFZ exclusion zone (SSSI + buffer)
    sssi_2d = [(p[0], p[1]) for p in np.array(sssi_pts_screen)[:, :2]]
    sssi_shapely = ShapelyPolygon(sssi_2d)
    nfz_buffer_screen = nfz_buffer_m * m_to_screen
    nfz_exclusion = sssi_shapely.buffer(nfz_buffer_screen)

    lines = []
    for i, y in enumerate(ys):
        # Create a long horizontal line in rotated space
        start_r = np.array([x_min - 0.5, y])
        end_r = np.array([x_max + 0.5, y])

        # Inverse-rotate to screen space
        start_s = inv_rotate(start_r, center)
        end_s = inv_rotate(end_r, center)

        # Clip to search polygon using Shapely
        raw_line = LineString([(start_s[0], start_s[1]), (end_s[0], end_s[1])])
        clipped = raw_line.intersection(search_inset)

        if clipped.is_empty:
            continue

        # Subtract NFZ exclusion zone
        safe_line = clipped.difference(nfz_exclusion)
        if safe_line.is_empty:
            continue

        # Extract the longest segment
        if isinstance(safe_line, MultiLineString):
            segments = list(safe_line.geoms)
        elif isinstance(safe_line, LineString):
            segments = [safe_line]
        else:
            continue

        # Use longest segment for this scan line
        best_seg = max(segments, key=lambda s: s.length)
        coords = list(best_seg.coords)
        if len(coords) < 2:
            continue

        seg_start = np.array([coords[0][0], coords[0][1]])
        seg_end = np.array([coords[-1][0], coords[-1][1]])

        # Alternate direction for zigzag
        if i % 2 == 1:
            seg_start, seg_end = seg_end, seg_start

        lines.append((
            np.array([seg_start[0], seg_start[1], 0]),
            np.array([seg_end[0], seg_end[1], 0])
        ))

    return lines


class SearchPatternExecution(Scene):
    def construct(self):
        # ── Coordinate transform setup ──────────────────────
        # Reference: centroid of all polygons
        all_lats = [p[0] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
        all_lons = [p[1] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
        ref_lat = np.mean(all_lats)
        ref_lon = np.mean(all_lons)

        # Convert everything to meters first to find extent
        all_m = []
        for lat, lon in FLIGHT_AREA_GPS:
            all_m.append(gps_to_meters(lat, lon, ref_lat, ref_lon))
        xs = [p[0] for p in all_m]
        ys = [p[1] for p in all_m]
        extent_x = max(xs) - min(xs)
        extent_y = max(ys) - min(ys)
        extent = max(extent_x, extent_y)

        # Scale to fit manim frame (leave margin)
        frame_size = 5.5
        scale = frame_size / extent
        offset = np.array([0.0, -0.3])  # slight downward shift for title

        # Meters-to-screen conversion factor
        m_to_screen = scale

        # Convert all polygons
        flight_pts = gps_poly_to_screen(FLIGHT_AREA_GPS, ref_lat, ref_lon, scale, offset)
        search_pts = gps_poly_to_screen(SEARCH_AREA_GPS, ref_lat, ref_lon, scale, offset)
        sssi_pts = gps_poly_to_screen(SSSI_GPS, ref_lat, ref_lon, scale, offset)
        tol_screen = gps_to_screen(*TAKEOFF_GPS, ref_lat, ref_lon, scale, offset)

        # Transit waypoints
        transit_screens = [gps_to_screen(lat, lon, ref_lat, ref_lon, scale, offset)
                           for lat, lon in TRANSIT_GPS]

        # ══════════════════════════════════════════════════════
        # 1. TITLE
        # ══════════════════════════════════════════════════════
        title = Text("Search Pattern Execution", font_size=36, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.25)
        subtitle = Text("Fenswood Farm SAR Mission", font_size=18, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.1)

        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.7)
        self.play(FadeIn(subtitle), run_time=0.3)

        # ══════════════════════════════════════════════════════
        # 2. FLIGHT AREA BOUNDARY (blue dashed)
        # ══════════════════════════════════════════════════════
        flight_poly = Polygon(
            *flight_pts,
            color=BLUE,
            stroke_width=2.5,
            stroke_opacity=0.8,
            fill_opacity=0.0,
        )
        flight_poly = DashedVMobject(flight_poly, num_dashes=30)

        flight_label = Text("Flight Area", font_size=12, color=BLUE_B)
        flight_label.next_to(flight_poly, DOWN, buff=0.1)

        self.play(Create(flight_poly), FadeIn(flight_label), run_time=1.0)

        # ══════════════════════════════════════════════════════
        # 3. SEARCH AREA (green semi-transparent)
        # ══════════════════════════════════════════════════════
        search_poly = Polygon(
            *search_pts,
            color=GREEN,
            stroke_width=2,
            fill_color=GREEN,
            fill_opacity=0.15,
        )
        search_label = Text("Search Area", font_size=12, color=GREEN_B)
        search_center = np.mean(search_pts, axis=0)
        search_label.move_to(search_center + np.array([0, -0.3, 0]))

        self.play(Create(search_poly), FadeIn(search_label), run_time=1.0)

        # ══════════════════════════════════════════════════════
        # 4. SSSI NO-FLY ZONE (red hatched)
        # ══════════════════════════════════════════════════════
        sssi_poly = Polygon(
            *sssi_pts,
            color=RED,
            stroke_width=2.5,
            fill_color=RED,
            fill_opacity=0.2,
        )

        # Hatching lines clipped to SSSI polygon using intersection
        sssi_center = np.mean(sssi_pts, axis=0)
        hatch_group = VGroup()
        sssi_arr = np.array(sssi_pts)
        sssi_xmin = sssi_arr[:, 0].min()
        sssi_xmax = sssi_arr[:, 0].max()
        sssi_ymin = sssi_arr[:, 1].min()
        sssi_ymax = sssi_arr[:, 1].max()

        sssi_shapely = ShapelyPolygon([(p[0], p[1]) for p in sssi_arr[:, :2]])
        for i in range(20):
            t = i / 19.0
            x = sssi_xmin + t * (sssi_xmax - sssi_xmin)
            raw_line = LineString([(x, sssi_ymin - 0.1), (x, sssi_ymax + 0.1)])
            clipped = raw_line.intersection(sssi_shapely)
            if clipped.is_empty:
                continue
            if isinstance(clipped, MultiLineString):
                segs = list(clipped.geoms)
            elif isinstance(clipped, LineString):
                segs = [clipped]
            else:
                continue
            for seg in segs:
                coords = list(seg.coords)
                if len(coords) >= 2:
                    hatch_line = Line(
                        [coords[0][0], coords[0][1], 0],
                        [coords[-1][0], coords[-1][1], 0],
                        color=RED, stroke_width=0.8, stroke_opacity=0.3,
                    )
                    hatch_group.add(hatch_line)

        sssi_label = Text("SSSI No-Fly", font_size=13, color=RED, weight=BOLD)
        sssi_label.move_to(sssi_center + np.array([0.0, 0.0, 0]))

        self.play(
            Create(sssi_poly),
            FadeIn(hatch_group, lag_ratio=0.05),
            run_time=0.7,
        )
        self.play(FadeIn(sssi_label), run_time=0.3)

        # ══════════════════════════════════════════════════════
        # 5. NFZ BUFFER ZONE (orange dashed, 30m offset)
        # ══════════════════════════════════════════════════════
        # Use Shapely buffer for accurate 30m offset
        buffer_screen = NFZ_WAYPOINT_BUFFER_M * m_to_screen
        sssi_2d = [(p[0], p[1]) for p in sssi_arr[:, :2]]
        sssi_poly_shapely = ShapelyPolygon(sssi_2d)
        buffered = sssi_poly_shapely.buffer(buffer_screen)
        buf_coords = list(buffered.exterior.coords)
        buffer_pts = [[c[0], c[1], 0] for c in buf_coords[:-1]]  # drop closing duplicate

        buffer_poly = Polygon(
            *buffer_pts,
            color=ORANGE,
            stroke_width=1.8,
            stroke_opacity=0.7,
            fill_opacity=0.0,
        )
        buffer_poly = DashedVMobject(buffer_poly, num_dashes=40)

        buffer_label = Text("30m Buffer", font_size=10, color=ORANGE)
        buffer_label.next_to(buffer_poly, LEFT, buff=0.05)

        self.play(Create(buffer_poly), FadeIn(buffer_label), run_time=0.5)

        # ══════════════════════════════════════════════════════
        # 6. TAKEOFF POINT (yellow star)
        # ══════════════════════════════════════════════════════
        tol_star = Star(
            n=5, outer_radius=0.18, inner_radius=0.08,
            color=YELLOW, fill_color=YELLOW, fill_opacity=1.0,
        )
        tol_star.move_to(tol_screen)

        tol_label = Text("TOL", font_size=14, color=YELLOW, weight=BOLD)
        tol_label.next_to(tol_star, UP, buff=0.1)

        self.play(FadeIn(tol_star, scale=1.5), FadeIn(tol_label), run_time=0.5)

        # ══════════════════════════════════════════════════════
        # 7. TRANSIT WAYPOINTS (T1 → T2 → T3)
        # ══════════════════════════════════════════════════════
        transit_dots = VGroup()
        transit_labels_group = VGroup()
        for idx, tpt in enumerate(transit_screens):
            dot = Dot(tpt, radius=0.06, color=BLUE_C, fill_opacity=0.8)
            lbl = Text(f"T{idx+1}", font_size=10, color=BLUE_C)
            lbl.next_to(dot, UR, buff=0.05)
            transit_dots.add(dot)
            transit_labels_group.add(lbl)

        self.play(
            FadeIn(transit_dots, lag_ratio=0.2),
            FadeIn(transit_labels_group, lag_ratio=0.2),
            run_time=0.5,
        )

        # ══════════════════════════════════════════════════════
        # 8. LAWNMOWER PATTERN LINES (aligned to longest edge,
        #    clipped to polygon, avoiding NFZ)
        # ══════════════════════════════════════════════════════
        lawnmower = generate_lawnmower_lines(search_pts, sssi_pts, NFZ_WAYPOINT_BUFFER_M, m_to_screen)

        pattern_lines = VGroup()
        pattern_points = []  # ordered waypoints for drone path

        for i, (start, end) in enumerate(lawnmower):
            line = Line(start, end, color=GREEN_A, stroke_width=1.5, stroke_opacity=0.5)
            pattern_lines.add(line)
            pattern_points.append(start)
            pattern_points.append(end)

        self.play(
            LaggedStart(*[Create(l) for l in pattern_lines], lag_ratio=0.15),
            run_time=2.0,
        )

        # ══════════════════════════════════════════════════════
        # 9. DRONE FLIES TRANSIT → FIRST WAYPOINT
        # ══════════════════════════════════════════════════════
        drone = Dot(
            tol_screen, radius=0.1, color=WHITE,
            fill_color=YELLOW, fill_opacity=1.0,
        )
        drone_label = Text("UAV", font_size=9, color=WHITE)
        drone_label.add_updater(lambda m: m.next_to(drone, UR, buff=0.05))

        # Traced path shows where drone has been
        trace = TracedPath(
            drone.get_center, stroke_color=YELLOW, stroke_width=2, stroke_opacity=0.7,
        )

        self.add(trace, drone, drone_label)
        self.play(FadeIn(drone, scale=2.0), run_time=0.3)

        # Draw transit path: TOL → T1 → T2 → T3
        transit_path_pts = [tol_screen] + transit_screens
        for i in range(len(transit_path_pts) - 1):
            seg = DashedLine(
                transit_path_pts[i], transit_path_pts[i + 1],
                color=BLUE_C, stroke_width=1.5,
            )
            self.play(Create(seg), run_time=0.15)
            self.play(drone.animate.move_to(transit_path_pts[i + 1]), run_time=0.35)

        # Transit from T3 to first scan line start
        if pattern_points:
            first_wp = pattern_points[0]
            transit_to_search = DashedLine(
                transit_screens[-1], first_wp,
                color=YELLOW_A, stroke_width=1.5,
            )
            self.play(Create(transit_to_search), run_time=0.2)
            self.play(drone.animate.move_to(first_wp), run_time=0.5)

        # ══════════════════════════════════════════════════════
        # 10. FLY LAWNMOWER + GREEN COVERAGE OVERLAY
        # ══════════════════════════════════════════════════════
        self.remove(trace)
        search_trace = TracedPath(
            drone.get_center, stroke_color=GREEN, stroke_width=2.5, stroke_opacity=0.6,
        )
        self.add(search_trace)

        coverage_strips = VGroup()
        detection_line_idx = min(3, len(lawnmower) - 1)  # Detection on 4th line (or last)
        detection_t = 0.6       # 60% along that line
        detection_pos = None

        for i in range(0, len(pattern_points), 2):
            if i + 1 >= len(pattern_points):
                break
            line_start = pattern_points[i]
            line_end = pattern_points[i + 1]
            line_idx = i // 2

            # Build coverage strip (filled rectangle along scan line)
            direction = line_end - line_start
            length = np.linalg.norm(direction)
            if length < 0.01:
                continue
            perp = np.array([-direction[1], direction[0], 0]) / length
            strip_width = 0.25  # visual width of coverage strip

            strip = Polygon(
                line_start + perp * strip_width / 2,
                line_end + perp * strip_width / 2,
                line_end - perp * strip_width / 2,
                line_start - perp * strip_width / 2,
                color=GREEN, fill_color=GREEN, fill_opacity=0.12,
                stroke_width=0,
            )

            # If this is the detection line, only fly partway then trigger detection
            if line_idx == detection_line_idx:
                det_point = line_start + detection_t * (line_end - line_start)
                detection_pos = det_point.copy()

                # Fly to detection point
                self.play(
                    drone.animate.move_to(det_point),
                    FadeIn(strip, lag_ratio=0.1),
                    run_time=0.5,
                )
                break
            else:
                # Fly full line with coverage appearing
                self.play(
                    drone.animate.move_to(line_end),
                    FadeIn(strip),
                    run_time=0.6,
                )
                coverage_strips.add(strip)

        # ══════════════════════════════════════════════════════
        # 11. DETECTION FLASH
        # ══════════════════════════════════════════════════════
        if detection_pos is None:
            # Fallback if no detection point computed
            detection_pos = search_center.copy()

        det_flash = Circle(
            radius=0.3, color=RED, fill_color=RED, fill_opacity=0.4,
            stroke_width=3,
        )
        det_flash.move_to(detection_pos)

        det_text = Text("DETECTION", font_size=16, color=RED, weight=BOLD)
        det_text.next_to(det_flash, RIGHT, buff=0.15)

        det_marker = Dot(detection_pos, radius=0.06, color=RED, fill_opacity=1.0)

        self.play(
            Flash(detection_pos, color=RED, flash_radius=0.5, line_length=0.2, run_time=0.5),
            FadeIn(det_flash),
            FadeIn(det_marker),
            FadeIn(det_text),
            run_time=0.5,
        )
        self.wait(0.3)
        self.play(FadeOut(det_flash), run_time=0.2)

        # ══════════════════════════════════════════════════════
        # 12. DRONE DIVERTS TO DETECTION — VERIFICATION
        # ══════════════════════════════════════════════════════
        self.remove(search_trace)
        divert_trace = TracedPath(
            drone.get_center, stroke_color=ORANGE, stroke_width=2, stroke_opacity=0.6,
        )
        self.add(divert_trace)

        verify_icon = VGroup(
            Circle(radius=0.15, color=ORANGE, stroke_width=2),
            Text("?", font_size=16, color=ORANGE, weight=BOLD),
        )
        verify_icon.move_to(detection_pos + np.array([0, 0.3, 0]))

        self.play(
            drone.animate.move_to(detection_pos),
            FadeIn(verify_icon),
            run_time=0.6,
        )

        # Verification confirmed
        confirm_text = Text("CONFIRMED", font_size=14, color=GREEN, weight=BOLD)
        confirm_text.move_to(verify_icon.get_center())
        self.play(
            FadeOut(verify_icon),
            FadeIn(confirm_text),
            run_time=0.4,
        )

        # ══════════════════════════════════════════════════════
        # 13. OFFSET LANDING
        # ══════════════════════════════════════════════════════
        landing_offset = np.array([0.4, -0.3, 0])  # 7.5m offset (visual)
        landing_pos = detection_pos + landing_offset

        land_marker = VGroup(
            Cross(stroke_color=YELLOW, stroke_width=3, scale_factor=0.12),
        )
        land_marker.move_to(landing_pos)

        land_label = Text("LAND", font_size=12, color=YELLOW, weight=BOLD)
        land_label.next_to(land_marker, DOWN, buff=0.08)

        self.remove(divert_trace)
        land_trace = TracedPath(
            drone.get_center, stroke_color=YELLOW, stroke_width=2,
            stroke_opacity=0.5,
        )
        self.add(land_trace)

        self.play(
            FadeIn(land_marker), FadeIn(land_label),
            drone.animate.move_to(landing_pos),
            run_time=0.5,
        )

        # Landing animation
        land_ring = Circle(radius=0.2, color=YELLOW, stroke_width=2, stroke_opacity=0.6)
        land_ring.move_to(landing_pos)
        self.play(
            drone.animate.scale(0.6),
            Create(land_ring),
            run_time=0.3,
        )
        self.wait(0.2)

        # ══════════════════════════════════════════════════════
        # 14. RETURN TO TOL (grey dashed, via transit in reverse)
        # ══════════════════════════════════════════════════════
        self.remove(land_trace)
        self.play(drone.animate.scale(1 / 0.6), run_time=0.2)

        return_path = DashedLine(
            landing_pos, tol_screen,
            color=GREY_B, stroke_width=1.5,
        )
        return_label = Text("RTL", font_size=10, color=GREY_B)
        return_label.move_to((landing_pos + tol_screen) / 2 + np.array([0.2, 0.15, 0]))

        self.play(Create(return_path), FadeIn(return_label), run_time=0.3)
        self.play(drone.animate.move_to(tol_screen), run_time=0.7)

        # Landing at TOL
        self.play(
            FadeOut(drone_label),
            drone.animate.set_opacity(0.5).scale(0.5),
            run_time=0.3,
        )

        # ══════════════════════════════════════════════════════
        # 15. STATS OVERLAY
        # ══════════════════════════════════════════════════════
        stats_box = VGroup(
            Text("Coverage: 96%", font_size=16, color=GREEN),
            Text("|", font_size=16, color=GREY),
            Text("Time: 112 s", font_size=16, color=BLUE_B),
            Text("|", font_size=16, color=GREY),
            Text("Energy: 12.6 Wh", font_size=16, color=ORANGE),
        ).arrange(RIGHT, buff=0.25)
        stats_box.to_edge(DOWN, buff=0.3)

        stats_bg = BackgroundRectangle(stats_box, color=BLACK, fill_opacity=0.7, buff=0.15)

        self.play(FadeIn(stats_bg), FadeIn(stats_box), run_time=1.0)
        self.wait(2.0)

        # Fade everything
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.0)
