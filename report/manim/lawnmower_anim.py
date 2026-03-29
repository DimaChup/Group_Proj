"""
Lawnmower Search Pattern Animation — Fenswood Farm SAR Drone.

Shows the full mission: takeoff, transit, lawnmower search with coverage,
detection, verification, offset landing, and return.

Run:
  python -m manim -pqh lawnmower_anim.py SearchPatternExecution
  python -m manim -pql lawnmower_anim.py SearchPatternExecution   # low quality (fast)
"""

from manim import *
import numpy as np


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


def generate_lawnmower_lines(search_pts_screen, angle_deg, num_lines):
    """Generate lawnmower scan lines across the search polygon at a given angle.
    Returns list of (start, end) point pairs in screen coords."""
    pts = np.array(search_pts_screen)[:, :2]
    cx, cy = pts.mean(axis=0)

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

    margin = 0.05 * (y_max - y_min)
    ys = np.linspace(y_min + margin, y_max - margin, num_lines)

    lines = []
    for i, y in enumerate(ys):
        if i % 2 == 0:
            start_r = np.array([x_min - 0.1, y])
            end_r = np.array([x_max + 0.1, y])
        else:
            start_r = np.array([x_max + 0.1, y])
            end_r = np.array([x_min - 0.1, y])

        start_s = inv_rotate(start_r, center)
        end_s = inv_rotate(end_r, center)
        lines.append((
            np.array([start_s[0], start_s[1], 0]),
            np.array([end_s[0], end_s[1], 0])
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

        # Convert all polygons
        flight_pts = gps_poly_to_screen(FLIGHT_AREA_GPS, ref_lat, ref_lon, scale, offset)
        search_pts = gps_poly_to_screen(SEARCH_AREA_GPS, ref_lat, ref_lon, scale, offset)
        sssi_pts = gps_poly_to_screen(SSSI_GPS, ref_lat, ref_lon, scale, offset)
        tol_x, tol_y = gps_to_meters(*TAKEOFF_GPS, ref_lat, ref_lon)
        tol_screen = np.array([tol_x * scale + offset[0], tol_y * scale + offset[1], 0])

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
        flight_poly.set_stroke(dash_length=0.15)

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
        # Place label inside the polygon roughly
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

        # Hatching lines inside SSSI
        sssi_center = np.mean(sssi_pts, axis=0)
        hatch_group = VGroup()
        sssi_arr = np.array(sssi_pts)
        sssi_xmin = sssi_arr[:, 0].min()
        sssi_xmax = sssi_arr[:, 0].max()
        sssi_ymin = sssi_arr[:, 1].min()
        sssi_ymax = sssi_arr[:, 1].max()

        for i in range(20):
            t = i / 19.0
            x = sssi_xmin + t * (sssi_xmax - sssi_xmin)
            hatch_line = Line(
                [x, sssi_ymin - 0.1, 0], [x, sssi_ymax + 0.1, 0],
                color=RED, stroke_width=0.8, stroke_opacity=0.3,
            )
            hatch_group.add(hatch_line)

        # Clip hatching visually by making it part of the SSSI group
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
        # Approximate 30m buffer by shrinking SSSI outward
        buffer_m = 30.0
        buffer_scale_factor = 1.0 + (buffer_m * scale) / 2.5  # approximate expansion
        sssi_np = np.array(sssi_pts)
        sssi_cx, sssi_cy = sssi_np[:, 0].mean(), sssi_np[:, 1].mean()

        buffer_pts = []
        for pt in sssi_pts:
            dx = pt[0] - sssi_cx
            dy = pt[1] - sssi_cy
            buffer_pts.append([
                sssi_cx + dx * buffer_scale_factor,
                sssi_cy + dy * buffer_scale_factor,
                0,
            ])

        buffer_poly = Polygon(
            *buffer_pts,
            color=ORANGE,
            stroke_width=1.8,
            stroke_opacity=0.7,
            fill_opacity=0.0,
        )
        buffer_poly.set_stroke(dash_length=0.1)

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
        # 7. LAWNMOWER PATTERN LINES (70 deg angle, 6 lines)
        # ══════════════════════════════════════════════════════
        scan_angle = 70  # degrees
        num_scan_lines = 6
        lawnmower = generate_lawnmower_lines(search_pts, scan_angle, num_scan_lines)

        # Clip lines to approximate search area bounds (visual trimming)
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
        # 8. DRONE TRANSITS TO FIRST WAYPOINT
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

        # Transit to first scan line start
        first_wp = pattern_points[0]
        transit_line = DashedLine(
            tol_screen, first_wp,
            color=YELLOW_A, stroke_width=1.5, dash_length=0.08,
        )
        self.play(Create(transit_line), run_time=0.3)
        self.play(drone.animate.move_to(first_wp), run_time=0.7)

        # ══════════════════════════════════════════════════════
        # 9. FLY LAWNMOWER + GREEN COVERAGE OVERLAY
        # ══════════════════════════════════════════════════════
        # Remove old trace, start fresh for search pattern
        self.remove(trace)
        search_trace = TracedPath(
            drone.get_center, stroke_color=GREEN, stroke_width=2.5, stroke_opacity=0.6,
        )
        self.add(search_trace)

        coverage_strips = VGroup()
        detection_line_idx = 3  # Detection happens on 4th line
        detection_t = 0.6       # 60% along that line
        detection_pos = None

        for i in range(0, len(pattern_points), 2):
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
        # 10. DETECTION FLASH
        # ══════════════════════════════════════════════════════
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
        # 11. DRONE DIVERTS TO DETECTION — VERIFICATION
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
        # 12. OFFSET LANDING
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
        # 13. RETURN TO TOL (grey dashed)
        # ══════════════════════════════════════════════════════
        self.remove(land_trace)
        self.play(drone.animate.scale(1 / 0.6), run_time=0.2)

        return_path = DashedLine(
            landing_pos, tol_screen,
            color=GREY_B, stroke_width=1.5, dash_length=0.1,
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
        # 14. STATS OVERLAY
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
