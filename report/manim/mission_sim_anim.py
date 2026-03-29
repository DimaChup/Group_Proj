"""
Mission Simulation Replay — Fenswood Farm SAR Drone.

Bird's-eye SITL-style replay of the complete mission: takeoff, transit,
lawnmower search with coverage build-up, detection, verification,
offset landing with payload drop, and return home.

Run:
  python -m manim -pqh mission_sim_anim.py MissionSimScene
  python -m manim -pql mission_sim_anim.py MissionSimScene   # low quality (fast)
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
FOCUS_AREA_GPS = [
    (51.42330493862503, -2.669823704225677),
    (51.42344370699984, -2.669496195078445),
    (51.42352782091507, -2.669800245046278),
    (51.42334972740506, -2.67001828046102),
]

# ── Mission parameters from config.py ────────────────────────────
TARGET_ALT = 35.0
VERIFY_ALT = 15.0
TRANSIT_SPEED = 15.0
SEARCH_SPEED = 8.0
NFZ_BUFFER_M = 30.0
LANDING_OFFSET_M = 7.5


# ── Coordinate helpers ───────────────────────────────────────────

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
        pts.append(np.array([sx, sy, 0]))
    return pts


def generate_lawnmower_lines(search_pts_screen, angle_deg, num_lines):
    """Generate lawnmower scan lines across the search polygon."""
    pts = np.array(search_pts_screen)[:, :2]
    cx, cy = pts.mean(axis=0)
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


def point_in_polygon(px, py, poly_pts):
    """Ray-casting point-in-polygon test (2D)."""
    n = len(poly_pts)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly_pts[i][0], poly_pts[i][1]
        xj, yj = poly_pts[j][0], poly_pts[j][1]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# ── HUD helpers ──────────────────────────────────────────────────

HUD_FONT = "Consolas"
HUD_BG_COLOR = BLACK
HUD_BG_OPACITY = 0.65


def make_hud_text(text, font_size=16, color=WHITE):
    return Text(text, font_size=font_size, color=color, font=HUD_FONT)


def make_hud_panel(texts, position, buff=0.08):
    """Create a HUD panel (stacked text lines with background)."""
    group = VGroup(*texts).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    bg = BackgroundRectangle(group, color=HUD_BG_COLOR, fill_opacity=HUD_BG_OPACITY, buff=0.12)
    panel = VGroup(bg, group)
    panel.move_to(position)
    return panel, group


class MissionSimScene(Scene):
    def construct(self):
        # ── Coordinate transform ─────────────────────────────
        all_lats = [p[0] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
        all_lons = [p[1] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
        ref_lat = np.mean(all_lats)
        ref_lon = np.mean(all_lons)

        all_m = [gps_to_meters(lat, lon, ref_lat, ref_lon) for lat, lon in FLIGHT_AREA_GPS]
        xs = [p[0] for p in all_m]
        ys = [p[1] for p in all_m]
        extent = max(max(xs) - min(xs), max(ys) - min(ys))

        frame_size = 5.0
        scale = frame_size / extent
        offset = np.array([0.5, -0.3])

        flight_pts = gps_poly_to_screen(FLIGHT_AREA_GPS, ref_lat, ref_lon, scale, offset)
        search_pts = gps_poly_to_screen(SEARCH_AREA_GPS, ref_lat, ref_lon, scale, offset)
        sssi_pts = gps_poly_to_screen(SSSI_GPS, ref_lat, ref_lon, scale, offset)
        tol_x, tol_y = gps_to_meters(*TAKEOFF_GPS, ref_lat, ref_lon)
        tol_screen = np.array([tol_x * scale + offset[0], tol_y * scale + offset[1], 0])

        # SSSI centroid for buffer expansion
        sssi_np = np.array(sssi_pts)
        sssi_cx, sssi_cy = sssi_np[:, 0].mean(), sssi_np[:, 1].mean()

        # ══════════════════════════════════════════════════════
        #  PHASE 1: SETUP (2s)
        # ══════════════════════════════════════════════════════

        # -- Flight area (blue dashed) --
        flight_poly = Polygon(
            *flight_pts, color=BLUE, stroke_width=2.0, stroke_opacity=0.7, fill_opacity=0.0,
        )
        flight_poly

        # -- Search area (green fill) --
        search_poly = Polygon(
            *search_pts, color=GREEN, stroke_width=2, fill_color=GREEN, fill_opacity=0.1,
        )

        # -- SSSI (red hatched) --
        sssi_poly = Polygon(
            *sssi_pts, color=RED, stroke_width=2.5, fill_color=RED, fill_opacity=0.15,
        )
        # Hatching
        hatch_group = VGroup()
        sssi_xmin, sssi_xmax = sssi_np[:, 0].min(), sssi_np[:, 0].max()
        sssi_ymin, sssi_ymax = sssi_np[:, 1].min(), sssi_np[:, 1].max()
        for i in range(25):
            t = i / 24.0
            x = sssi_xmin + t * (sssi_xmax - sssi_xmin)
            hatch_line = Line(
                [x, sssi_ymin - 0.05, 0], [x, sssi_ymax + 0.05, 0],
                color=RED, stroke_width=0.6, stroke_opacity=0.25,
            )
            hatch_group.add(hatch_line)
        sssi_label = Text("SSSI", font_size=11, color=RED, weight=BOLD)
        sssi_center = np.mean(sssi_pts, axis=0)
        sssi_label.move_to(sssi_center)

        # -- NFZ Buffer (orange dashed) --
        buffer_scale_factor = 1.0 + (NFZ_BUFFER_M * scale) / 2.5
        buffer_pts = []
        for pt in sssi_pts:
            dx = pt[0] - sssi_cx
            dy = pt[1] - sssi_cy
            buffer_pts.append([sssi_cx + dx * buffer_scale_factor, sssi_cy + dy * buffer_scale_factor, 0])
        buffer_poly = Polygon(
            *buffer_pts, color=ORANGE, stroke_width=1.5, stroke_opacity=0.6, fill_opacity=0.0,
        )
        buffer_poly

        # -- TOL marker --
        tol_star = Star(n=5, outer_radius=0.15, inner_radius=0.06,
                        color=YELLOW, fill_color=YELLOW, fill_opacity=1.0)
        tol_star.move_to(tol_screen)
        tol_label_map = Text("TOL", font_size=11, color=YELLOW, weight=BOLD)
        tol_label_map.next_to(tol_star, UP, buff=0.06)

        # -- Legend --
        legend_items = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.3, color=BLUE, stroke_width=2),
                   Text("Flight Area", font_size=9, color=BLUE_B)).arrange(RIGHT, buff=0.08),
            VGroup(Square(side_length=0.15, color=GREEN, fill_color=GREEN, fill_opacity=0.3, stroke_width=1),
                   Text("Search Area", font_size=9, color=GREEN_B)).arrange(RIGHT, buff=0.08),
            VGroup(Square(side_length=0.15, color=RED, fill_color=RED, fill_opacity=0.3, stroke_width=1),
                   Text("SSSI NFZ", font_size=9, color=RED_B)).arrange(RIGHT, buff=0.08),
            VGroup(Line(ORIGIN, RIGHT * 0.3, color=ORANGE, stroke_width=1.5),
                   Text("30m Buffer", font_size=9, color=ORANGE)).arrange(RIGHT, buff=0.08),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        legend_bg = BackgroundRectangle(legend_items, color=BLACK, fill_opacity=0.6, buff=0.1)
        legend = VGroup(legend_bg, legend_items)
        legend.to_corner(DL, buff=0.2)

        # -- HUD elements --
        # State
        state_text = make_hud_text("STATE: INIT", font_size=18, color=YELLOW)
        # Timer
        timer_text = make_hud_text("T+0:00", font_size=16, color=WHITE)
        # Altitude
        alt_text = make_hud_text("ALT: 0 m", font_size=14, color=TEAL_B)
        # Speed
        spd_text = make_hud_text("SPD: 0 m/s", font_size=14, color=BLUE_B)
        # Coverage
        cov_text = make_hud_text("COV: 0%", font_size=14, color=GREEN_B)

        # Arrange HUD panels
        hud_left = VGroup(state_text, alt_text, spd_text).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        hud_left_bg = BackgroundRectangle(hud_left, color=HUD_BG_COLOR, fill_opacity=HUD_BG_OPACITY, buff=0.12)
        hud_left_panel = VGroup(hud_left_bg, hud_left)
        hud_left_panel.to_corner(UL, buff=0.15)

        hud_right = VGroup(timer_text, cov_text).arrange(DOWN, aligned_edge=RIGHT, buff=0.06)
        hud_right_bg = BackgroundRectangle(hud_right, color=HUD_BG_COLOR, fill_opacity=HUD_BG_OPACITY, buff=0.12)
        hud_right_panel = VGroup(hud_right_bg, hud_right)
        hud_right_panel.to_corner(UR, buff=0.15)

        # Helper to update HUD text
        def update_state(new_state, color=YELLOW):
            nonlocal state_text
            new_t = make_hud_text(f"STATE: {new_state}", font_size=18, color=color)
            new_t.move_to(state_text, aligned_edge=LEFT)
            old = state_text
            state_text = new_t
            return Transform(old, new_t)

        def update_alt(val):
            nonlocal alt_text
            new_t = make_hud_text(f"ALT: {val:.0f} m", font_size=14, color=TEAL_B)
            new_t.move_to(alt_text, aligned_edge=LEFT)
            old = alt_text
            alt_text = new_t
            return Transform(old, new_t)

        def update_spd(val):
            nonlocal spd_text
            new_t = make_hud_text(f"SPD: {val:.0f} m/s", font_size=14, color=BLUE_B)
            new_t.move_to(spd_text, aligned_edge=LEFT)
            old = spd_text
            spd_text = new_t
            return Transform(old, new_t)

        def update_timer(seconds):
            nonlocal timer_text
            m, s = divmod(int(seconds), 60)
            new_t = make_hud_text(f"T+{m}:{s:02d}", font_size=16, color=WHITE)
            new_t.move_to(timer_text, aligned_edge=RIGHT)
            old = timer_text
            timer_text = new_t
            return Transform(old, new_t)

        def update_cov(pct):
            nonlocal cov_text
            new_t = make_hud_text(f"COV: {pct:.0f}%", font_size=14, color=GREEN_B)
            new_t.move_to(cov_text, aligned_edge=RIGHT)
            old = cov_text
            cov_text = new_t
            return Transform(old, new_t)

        # -- Animate setup --
        self.play(
            FadeIn(flight_poly),
            FadeIn(search_poly),
            run_time=0.6,
        )
        self.play(
            FadeIn(sssi_poly),
            FadeIn(hatch_group, lag_ratio=0.03),
            FadeIn(sssi_label),
            FadeIn(buffer_poly),
            run_time=0.6,
        )
        self.play(
            FadeIn(tol_star, scale=1.5), FadeIn(tol_label_map),
            FadeIn(legend),
            FadeIn(hud_left_panel), FadeIn(hud_right_panel),
            run_time=0.6,
        )
        self.wait(0.2)

        # ══════════════════════════════════════════════════════
        #  PHASE 2: TAKEOFF (2s)
        # ══════════════════════════════════════════════════════
        # Drone dot
        drone = Dot(tol_screen, radius=0.09, color=WHITE, fill_color=YELLOW, fill_opacity=1.0)
        drone_ring = Circle(radius=0.14, color=YELLOW, stroke_width=1.5, stroke_opacity=0.6)
        drone_ring.add_updater(lambda m: m.move_to(drone.get_center()))

        # FOV rectangle (camera footprint)
        fov_w = 0.35  # visual width at search altitude
        fov_h = 0.26
        fov_rect = Rectangle(
            width=fov_w, height=fov_h,
            color=TEAL, stroke_width=1.0, stroke_opacity=0.5,
            fill_color=TEAL, fill_opacity=0.08,
        )
        fov_rect.add_updater(lambda m: m.move_to(drone.get_center()))

        self.add(drone, drone_ring)
        self.play(
            FadeIn(drone, scale=2.0),
            update_state("ARMING", YELLOW),
            run_time=0.5,
        )

        # Altitude climb
        self.play(
            update_state("TAKEOFF", TEAL_B),
            update_alt(10),
            update_timer(5),
            run_time=0.5,
        )
        self.play(
            update_alt(25),
            update_timer(12),
            run_time=0.5,
        )
        self.play(
            update_alt(TARGET_ALT),
            update_timer(18),
            run_time=0.5,
        )
        self.wait(0.2)

        # ══════════════════════════════════════════════════════
        #  PHASE 3: TRANSIT (2s)
        # ══════════════════════════════════════════════════════
        scan_angle = 70
        num_scan_lines = 7
        lawnmower = generate_lawnmower_lines(search_pts, scan_angle, num_scan_lines)

        # Build ordered waypoints
        pattern_points = []
        for start, end in lawnmower:
            pattern_points.append(start)
            pattern_points.append(end)

        first_wp = pattern_points[0]

        # Transit path (dashed)
        transit_line = DashedLine(
            tol_screen, first_wp,
            color=YELLOW_A, stroke_width=1.5, stroke_opacity=0.7,
        )

        self.play(
            update_state("TRANSIT", BLUE_B),
            update_spd(TRANSIT_SPEED),
            update_timer(20),
            Create(transit_line),
            run_time=0.5,
        )
        self.play(
            drone.animate.move_to(first_wp),
            update_timer(25),
            run_time=1.0,
        )

        # Flash FOV footprint
        self.add(fov_rect)
        self.play(
            fov_rect.animate.set_fill(opacity=0.15).set_stroke(opacity=0.8),
            run_time=0.3,
        )
        self.play(
            fov_rect.animate.set_fill(opacity=0.08).set_stroke(opacity=0.5),
            run_time=0.2,
        )

        # ══════════════════════════════════════════════════════
        #  PHASE 4: SEARCH PATTERN (8s)
        # ══════════════════════════════════════════════════════
        self.play(
            update_state("SEARCH", GREEN),
            update_spd(SEARCH_SPEED),
            update_timer(28),
            run_time=0.3,
        )

        # Coverage strips
        total_lines = num_scan_lines
        detection_line_idx = 4  # detection on 5th line (0-indexed)
        detection_t = 0.55  # 55% along that line
        detection_pos = None

        # Precompute strip width in screen coords
        # At 35m alt with FOV ~54 deg, ground footprint ~37m wide
        # In screen: 37m * scale
        strip_half_w = 0.13

        mission_time = 28  # running timer

        for i in range(0, len(pattern_points), 2):
            line_start = pattern_points[i]
            line_end = pattern_points[i + 1]
            line_idx = i // 2

            direction = line_end - line_start
            length = np.linalg.norm(direction)
            if length < 0.01:
                continue
            perp = np.array([-direction[1], direction[0], 0]) / length

            # Coverage strip
            strip = Polygon(
                line_start + perp * strip_half_w,
                line_end + perp * strip_half_w,
                line_end - perp * strip_half_w,
                line_start - perp * strip_half_w,
                color=GREEN, fill_color=GREEN, fill_opacity=0.12,
                stroke_width=0,
            )

            coverage_pct = min(96, (line_idx + 1) / total_lines * 96)
            mission_time += 12

            # Check if drone path passes near SSSI — show speed reduction
            midpoint = (line_start + line_end) / 2
            near_sssi = np.linalg.norm(midpoint[:2] - np.array([sssi_cx, sssi_cy])) < 1.5

            if line_idx == detection_line_idx:
                # Fly partway, then detect
                det_point = line_start + detection_t * (line_end - line_start)
                detection_pos = det_point.copy()

                # Partial strip up to detection point
                partial_strip = Polygon(
                    line_start + perp * strip_half_w,
                    det_point + perp * strip_half_w,
                    det_point - perp * strip_half_w,
                    line_start - perp * strip_half_w,
                    color=GREEN, fill_color=GREEN, fill_opacity=0.12,
                    stroke_width=0,
                )
                partial_cov = min(96, (line_idx + detection_t) / total_lines * 96)

                self.play(
                    drone.animate.move_to(det_point),
                    FadeIn(partial_strip),
                    update_cov(partial_cov),
                    update_timer(mission_time),
                    run_time=0.5,
                )
                break
            else:
                fly_speed = SEARCH_SPEED
                spd_anims = []
                if near_sssi:
                    fly_speed = 3
                    spd_anims.append(update_spd(3))

                anims = [
                    drone.animate.move_to(line_end),
                    FadeIn(strip),
                    update_cov(coverage_pct),
                    update_timer(mission_time),
                ] + spd_anims

                self.play(*anims, run_time=0.8)

                # Restore speed after SSSI line
                if near_sssi:
                    self.play(update_spd(SEARCH_SPEED), run_time=0.1)

        # ══════════════════════════════════════════════════════
        #  PHASE 5: DETECTION EVENT (3s)
        # ══════════════════════════════════════════════════════
        # Red flash
        det_flash = Circle(
            radius=0.25, color=RED, fill_color=RED, fill_opacity=0.35, stroke_width=3,
        )
        det_flash.move_to(detection_pos)

        det_box = Square(
            side_length=0.2, color=RED, stroke_width=2.5,
        )
        det_box.move_to(detection_pos)

        det_conf = make_hud_text("0.87", font_size=10, color=RED)
        det_conf.next_to(det_box, UR, buff=0.03)

        self.play(
            Flash(detection_pos, color=RED, flash_radius=0.4, line_length=0.15, run_time=0.5),
            FadeIn(det_flash),
            FadeIn(det_box),
            FadeIn(det_conf),
            update_state("CENTERING", ORANGE),
            run_time=0.5,
        )
        self.play(FadeOut(det_flash), run_time=0.2)

        # Drone flies to detection
        self.play(
            drone.animate.move_to(detection_pos),
            update_timer(mission_time + 8),
            run_time=0.5,
        )
        mission_time += 8

        # GPS scatter dots
        scatter_dots = VGroup()
        np.random.seed(42)
        for _ in range(4):
            jitter = np.array([np.random.normal(0, 0.05), np.random.normal(0, 0.05), 0])
            dot = Dot(detection_pos + jitter, radius=0.025, color=ORANGE, fill_opacity=0.8)
            scatter_dots.add(dot)

        gps_avg_dot = Dot(detection_pos, radius=0.035, color=YELLOW, fill_opacity=1.0)

        self.play(
            FadeIn(scatter_dots, lag_ratio=0.2),
            run_time=0.4,
        )
        self.play(FadeIn(gps_avg_dot), run_time=0.2)

        # Verify state
        verify_icon = VGroup(
            Circle(radius=0.12, color=ORANGE, stroke_width=2),
            Text("?", font_size=14, color=ORANGE, weight=BOLD),
        )
        verify_icon.move_to(detection_pos + UP * 0.25)

        self.play(
            FadeIn(verify_icon),
            update_state("VERIFY", ORANGE),
            update_timer(mission_time + 5),
            run_time=0.4,
        )
        mission_time += 5
        self.wait(0.3)

        # Confirmation
        confirm_icon = VGroup(
            Circle(radius=0.12, color=GREEN, stroke_width=2, fill_color=GREEN, fill_opacity=0.3),
            Text("Y", font_size=14, color=GREEN, weight=BOLD),
        )
        confirm_icon.move_to(verify_icon.get_center())

        self.play(
            FadeOut(verify_icon),
            FadeIn(confirm_icon),
            run_time=0.3,
        )
        self.wait(0.2)

        # ══════════════════════════════════════════════════════
        #  PHASE 6: APPROACH + LANDING (3s)
        # ══════════════════════════════════════════════════════
        # 7.5m offset landing point
        landing_offset_screen = np.array([0.35, -0.25, 0])
        landing_pos = detection_pos + landing_offset_screen

        # Distance label
        dist_line = DashedLine(
            detection_pos, landing_pos,
            color=YELLOW, stroke_width=1.5,
        )
        dist_label = Text("7.5m", font_size=11, color=YELLOW, weight=BOLD)
        dist_label.move_to((detection_pos + landing_pos) / 2 + np.array([0.12, 0.08, 0]))

        land_cross = Cross(stroke_color=YELLOW, stroke_width=2.5, scale_factor=0.1)
        land_cross.move_to(landing_pos)

        self.play(
            update_state("APPROACH", BLUE_B),
            update_spd(5),
            Create(dist_line), FadeIn(dist_label),
            FadeIn(land_cross),
            run_time=0.4,
        )

        # Remove FOV rect updater before moving drone
        fov_rect.clear_updaters()

        self.play(
            drone.animate.move_to(landing_pos),
            fov_rect.animate.move_to(landing_pos),
            update_timer(mission_time + 8),
            run_time=0.6,
        )
        mission_time += 8

        # Re-add updater
        fov_rect.add_updater(lambda m: m.move_to(drone.get_center()))

        # Hover + payload
        self.play(
            update_state("HOVER_TARGET", TEAL_B),
            update_spd(0),
            run_time=0.3,
        )

        # Payload drop animation
        payload = Square(
            side_length=0.08, color=MAROON_B, fill_color=MAROON_B, fill_opacity=0.9,
            stroke_width=1,
        )
        payload.move_to(drone.get_center())
        payload_label = Text("DROP", font_size=9, color=MAROON_B, weight=BOLD)
        payload_label.next_to(payload, RIGHT, buff=0.06)

        self.add(payload)
        self.play(
            payload.animate.shift(DOWN * 0.15).set_opacity(0.4),
            FadeIn(payload_label),
            run_time=0.4,
        )

        # Altitude drop
        self.play(
            update_alt(15),
            update_timer(mission_time + 5),
            run_time=0.3,
        )
        mission_time += 5
        self.play(
            update_alt(3),
            update_timer(mission_time + 4),
            run_time=0.3,
        )
        mission_time += 4

        # Landing ring
        land_ring = Circle(radius=0.16, color=YELLOW, stroke_width=2, stroke_opacity=0.5)
        land_ring.move_to(landing_pos)
        self.play(
            Create(land_ring),
            drone.animate.scale(0.7),
            update_state("LANDING", YELLOW),
            run_time=0.3,
        )
        self.wait(0.15)

        # ══════════════════════════════════════════════════════
        #  PHASE 7: RETURN HOME (3s)
        # ══════════════════════════════════════════════════════
        # Scale drone back up
        self.play(
            drone.animate.scale(1 / 0.7),
            update_state("RETURN_HOME", GREY_B),
            update_alt(TARGET_ALT),
            update_spd(TRANSIT_SPEED),
            run_time=0.4,
        )

        # Remove FOV for return
        fov_rect.clear_updaters()
        self.play(FadeOut(fov_rect), run_time=0.15)

        # Return path
        return_line = DashedLine(
            landing_pos, tol_screen,
            color=GREY_B, stroke_width=1.5,
        )
        rtl_label = Text("RTL", font_size=10, color=GREY_B)
        rtl_label.move_to((landing_pos + tol_screen) / 2 + np.array([0.15, 0.12, 0]))

        self.play(
            Create(return_line), FadeIn(rtl_label),
            update_timer(mission_time + 10),
            run_time=0.4,
        )
        mission_time += 10
        self.play(
            drone.animate.move_to(tol_screen),
            update_timer(mission_time + 12),
            run_time=1.0,
        )
        mission_time += 12

        # Landing at TOL
        self.play(
            update_state("LANDING", YELLOW),
            update_alt(10),
            update_spd(0),
            run_time=0.3,
        )
        self.play(
            update_alt(0),
            drone.animate.set_opacity(0.6).scale(0.6),
            run_time=0.4,
        )

        # ══════════════════════════════════════════════════════
        #  PHASE 8: MISSION COMPLETE (2s)
        # ══════════════════════════════════════════════════════
        self.play(
            update_state("DONE", GREEN),
            run_time=0.3,
        )

        # Green checkmark
        check = VGroup(
            Line(ORIGIN, DR * 0.15, color=GREEN, stroke_width=4),
            Line(DR * 0.15, DR * 0.15 + UR * 0.3, color=GREEN, stroke_width=4),
        )
        check.move_to(tol_screen + UP * 0.35)

        self.play(Create(check), run_time=0.3)

        # Final stats bar
        final_time = mission_time
        stats_items = VGroup(
            Text(f"Coverage: 96%", font_size=15, color=GREEN, weight=BOLD),
            Text("|", font_size=15, color=GREY),
            Text(f"Time: {final_time}s", font_size=15, color=BLUE_B),
            Text("|", font_size=15, color=GREY),
            Text("Detections: 1", font_size=15, color=RED_B),
            Text("|", font_size=15, color=GREY),
            Text("Energy: 12.6 Wh", font_size=15, color=ORANGE),
        ).arrange(RIGHT, buff=0.2)
        stats_bg = BackgroundRectangle(stats_items, color=BLACK, fill_opacity=0.75, buff=0.15)
        stats_bar = VGroup(stats_bg, stats_items)
        stats_bar.to_edge(DOWN, buff=0.2)

        self.play(FadeIn(stats_bar), run_time=0.7)
        self.wait(1.5)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.0)
