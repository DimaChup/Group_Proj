"""
Cinematic SAR Mission Animation — Scenes 5-8.

Scene 5: DetectionScene (3s)  — AI detection, GPS cluster, operator confirm
Scene 6: PayloadDescentScene (5s) — Side view descent + dual servo payload release
Scene 7: ReturnHomeScene (5s) — Bird's eye return transit T3->T2->T1->TOL
Scene 8: MissionCompleteScene (3s) — Stats panel, checkmark, fade out

Run individual scenes:
  python -m manim -ql --media_dir report/manim/media report/manim/cinematic_part2.py PayloadDescentScene
"""

from manim import *
import numpy as np

# ── GPS coordinates from config.py ────────────────────────────
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

TRANSIT_GPS = [
    (51.42176480, -2.67011737),   # T1
    (51.42247427, -2.66713882),   # T2
    (51.42410412, -2.66830869),   # T3
]

# Flight parameters
TARGET_ALT = 35.0
HOVER_ALT = 3.0
LANDING_OFFSET_M = 7.5
TRANSIT_SPEED_MPS = 15.0


# ── Coordinate conversion (same as nfz_field_anim.py) ────────

def gps_to_meters(lat, lon, ref_lat, ref_lon):
    """GPS -> local metres (East, North)."""
    dlat = lat - ref_lat
    dlon = lon - ref_lon
    north = dlat * 111320.0
    east = dlon * 111320.0 * np.cos(np.radians(ref_lat))
    return east, north


def gps_poly_to_screen(gps_coords, ref_lat, ref_lon, scale, offset):
    pts = []
    for lat, lon in gps_coords:
        ex, ny = gps_to_meters(lat, lon, ref_lat, ref_lon)
        sx = ex * scale + offset[0]
        sy = ny * scale + offset[1]
        pts.append(np.array([sx, sy, 0]))
    return pts


def gps_point_to_screen(lat, lon, ref_lat, ref_lon, scale, offset):
    ex, ny = gps_to_meters(lat, lon, ref_lat, ref_lon)
    return np.array([ex * scale + offset[0], ny * scale + offset[1], 0])


def _setup_birdseye():
    """Shared setup: compute ref, scale, offset, polygon screen coords."""
    all_lats = [p[0] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
    all_lons = [p[1] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
    ref_lat = np.mean(all_lats)
    ref_lon = np.mean(all_lons)

    all_m = [gps_to_meters(lat, lon, ref_lat, ref_lon) for lat, lon in FLIGHT_AREA_GPS]
    xs = [p[0] for p in all_m]
    ys = [p[1] for p in all_m]
    extent = max(max(xs) - min(xs), max(ys) - min(ys))

    frame_size = 5.5
    scale = frame_size / extent
    offset = np.array([0.0, -0.3])

    search_pts = gps_poly_to_screen(SEARCH_AREA_GPS, ref_lat, ref_lon, scale, offset)
    sssi_pts = gps_poly_to_screen(SSSI_GPS, ref_lat, ref_lon, scale, offset)
    flight_pts = gps_poly_to_screen(FLIGHT_AREA_GPS, ref_lat, ref_lon, scale, offset)
    focus_pts = gps_poly_to_screen(FOCUS_AREA_GPS, ref_lat, ref_lon, scale, offset)
    tol_screen = gps_point_to_screen(*TAKEOFF_GPS, ref_lat, ref_lon, scale, offset)
    transit_pts = [
        gps_point_to_screen(lat, lon, ref_lat, ref_lon, scale, offset)
        for lat, lon in TRANSIT_GPS
    ]

    return dict(
        ref_lat=ref_lat, ref_lon=ref_lon, scale=scale, offset=offset,
        search_pts=search_pts, sssi_pts=sssi_pts, flight_pts=flight_pts,
        focus_pts=focus_pts, tol_screen=tol_screen, transit_pts=transit_pts,
    )


def _make_background_zones(d):
    """Create dimmed background zone polygons."""
    flight_poly = Polygon(
        *d["flight_pts"], color=WHITE, stroke_width=1.5, stroke_opacity=0.3,
        fill_opacity=0.0,
    )
    flight_poly = DashedVMobject(flight_poly, num_dashes=30)
    search_poly = Polygon(
        *d["search_pts"], color=BLUE, stroke_width=1.5,
        fill_color=BLUE, fill_opacity=0.06,
    )
    sssi_poly = Polygon(
        *d["sssi_pts"], color=RED, stroke_width=2,
        fill_color=RED, fill_opacity=0.15,
    )
    return VGroup(flight_poly, search_poly, sssi_poly)


def _make_drone_icon(pos, scale_factor=0.10):
    """Create a white triangle drone icon."""
    drone = Triangle(fill_color=WHITE, fill_opacity=1, stroke_width=0).scale(scale_factor)
    drone.move_to(pos)
    return drone


def _make_state_badge(text_str, color=WHITE):
    """State badge for top-right corner."""
    bg = RoundedRectangle(
        corner_radius=0.05, width=2.4, height=0.35,
        fill_color=DARK_GREY, fill_opacity=0.85, stroke_width=0,
    )
    txt = Text(text_str, font_size=16, color=color, weight=BOLD)
    txt.move_to(bg.get_center())
    badge = VGroup(bg, txt)
    badge.to_corner(UR, buff=0.2)
    return badge


# ══════════════════════════════════════════════════════════════
#  SCENE 5: Detection
# ══════════════════════════════════════════════════════════════

class DetectionScene(Scene):
    def construct(self):
        d = _setup_birdseye()
        focus_pts = d["focus_pts"]

        # Background zones (dimmed)
        bg = _make_background_zones(d)
        self.add(bg)

        # Focus area polygon
        focus_poly = Polygon(
            *focus_pts, fill_color=ORANGE, fill_opacity=0.15,
            stroke_color=ORANGE, stroke_width=2,
        )
        self.add(focus_poly)

        # Dummy position: centroid of focus area
        dummy_pos = np.mean(focus_pts, axis=0)

        # Drone starts slightly offset (mid-strip)
        drone_start = dummy_pos + np.array([0.3, 0.2, 0])
        drone = _make_drone_icon(drone_start)
        self.add(drone)

        state_badge = _make_state_badge("SEARCH", BLUE)
        self.add(state_badge)

        # ── 0.0-0.5s: Red flash + dummy appears ──
        dummy_dot = Dot(dummy_pos, radius=0.06, color=RED, fill_opacity=0.9)
        red_flash = Circle(radius=0.3, fill_color=RED, fill_opacity=0.5, stroke_width=0)
        red_flash.move_to(dummy_pos)

        self.play(
            FadeIn(red_flash, scale=0.5),
            FadeIn(dummy_dot),
            run_time=0.3,
        )
        self.play(FadeOut(red_flash), run_time=0.2)

        # ── 0.5-1.2s: Bounding box + confidence + GPS dots ──
        bbox = Rectangle(
            width=0.18, height=0.24, stroke_color=RED, stroke_width=3,
            fill_opacity=0,
        ).move_to(dummy_pos)
        conf_label = Text("0.94", font_size=14, color=RED, weight=BOLD)
        conf_label.next_to(bbox, UR, buff=0.04)

        # State -> CENTERING
        new_badge = _make_state_badge("CENTERING", YELLOW)

        # GPS estimation dots (scattered within ~0.15 screen units of true pos)
        np.random.seed(42)
        gps_offsets = np.random.randn(5, 2) * 0.08
        gps_dots = VGroup(*[
            Dot(dummy_pos + np.array([ox, oy, 0]), radius=0.025, color=YELLOW)
            for ox, oy in gps_offsets
        ])

        self.play(
            Create(bbox),
            FadeIn(conf_label),
            Transform(state_badge, new_badge),
            FadeIn(gps_dots, lag_ratio=0.2),
            run_time=0.7,
        )

        # ── 1.2-2.0s: Drone moves to cluster center, VERIFY ──
        cluster_center = dummy_pos + np.mean(
            [np.array([ox, oy, 0]) for ox, oy in gps_offsets], axis=0
        )

        verify_badge = _make_state_badge("VERIFY", TEAL)

        # Converge GPS dots toward true position
        converge_anims = [
            dot.animate.move_to(dummy_pos + np.array([ox * 0.2, oy * 0.2, 0]))
            for dot, (ox, oy) in zip(gps_dots, gps_offsets)
        ]

        self.play(
            drone.animate.move_to(cluster_center),
            *converge_anims,
            Transform(state_badge, verify_badge),
            run_time=0.8,
        )

        # ── 2.0-2.5s: Operator prompt ──
        prompt = Text("Confirm Target?   Y / N / I", font_size=20, color=WHITE)
        prompt.to_edge(DOWN, buff=0.5)

        self.play(FadeIn(prompt, shift=UP * 0.1), run_time=0.3)
        self.wait(0.2)

        # ── 2.5-3.0s: Y confirm ──
        y_key = Text("Y", font_size=36, color=GREEN, weight=BOLD)
        y_key.move_to(prompt.get_center())

        confirmed = Text("TARGET CONFIRMED", font_size=22, color=GREEN, weight=BOLD)
        confirmed.to_edge(DOWN, buff=0.5)

        approach_badge = _make_state_badge("APPROACH", GREEN)

        self.play(
            FadeOut(prompt),
            FadeIn(y_key, scale=2.0),
            run_time=0.15,
        )
        self.play(
            Transform(y_key, confirmed),
            Transform(state_badge, approach_badge),
            run_time=0.35,
        )


# ══════════════════════════════════════════════════════════════
#  SCENE 6: Payload Descent (SIDE VIEW)
# ══════════════════════════════════════════════════════════════

class PayloadDescentScene(Scene):
    def construct(self):
        # ── Side-view coordinate system ──
        # X axis = horizontal distance (metres), Y axis = altitude (metres)
        # Frame: ~50m wide, 0-40m tall
        # Map: 1 manim unit = ~5.7m to fit nicely

        alt_max = 40.0
        horiz_range = 50.0
        frame_h = 6.5   # manim units for altitude
        frame_w = 10.0   # manim units horizontal
        alt_scale = frame_h / alt_max       # manim units per metre altitude
        horiz_scale = frame_w / horiz_range  # manim units per metre horizontal

        ground_y = -3.0  # manim Y of ground line
        def alt_to_y(alt_m):
            return ground_y + alt_m * alt_scale

        def horiz_to_x(dist_m):
            return dist_m * horiz_scale

        # ── Sky gradient background ──
        sky = Rectangle(
            width=14, height=8, fill_color=ManimColor("#16213e"),
            fill_opacity=0.25, stroke_width=0,
        ).move_to(ORIGIN + UP * 0.5)
        self.add(sky)

        # ── Ground ──
        ground = Rectangle(
            width=14, height=0.6, fill_color=ManimColor("#3d5a1e"),
            fill_opacity=0.7, stroke_width=0,
        )
        ground.move_to(np.array([0, ground_y - 0.3, 0]))
        ground_line = Line(
            np.array([-7, ground_y, 0]), np.array([7, ground_y, 0]),
            color=ManimColor("#5a8a2a"), stroke_width=3,
        )
        self.add(ground, ground_line)

        # ── Altitude scale (left side) ──
        alt_ticks = VGroup()
        for alt_val in [0, 10, 20, 30, 35]:
            y = alt_to_y(alt_val)
            tick = Line(
                np.array([-6.2, y, 0]), np.array([-5.9, y, 0]),
                color=WHITE, stroke_width=1.5, stroke_opacity=0.6,
            )
            label = Text(f"{alt_val}m", font_size=11, color=GREY_B)
            label.next_to(tick, LEFT, buff=0.08)
            alt_ticks.add(tick, label)

        alt_axis_line = Line(
            np.array([-6.0, ground_y, 0]),
            np.array([-6.0, alt_to_y(37), 0]),
            color=WHITE, stroke_width=1.5, stroke_opacity=0.4,
        )
        self.add(alt_axis_line, alt_ticks)

        # ── Dummy on ground (centre-left) ──
        dummy_x = -0.8
        dummy_head = Circle(
            radius=0.08, fill_color=RED, fill_opacity=0.9, stroke_width=1, stroke_color=RED,
        ).move_to(np.array([dummy_x, ground_y + 0.08, 0]))
        dummy_body = Line(
            np.array([dummy_x, ground_y, 0]),
            np.array([dummy_x, ground_y + 0.18, 0]),
            color=RED, stroke_width=2.5,
        )
        dummy_label = Text("Casualty", font_size=12, color=RED)
        dummy_label.next_to(dummy_body, DOWN, buff=0.12)
        dummy_group = VGroup(dummy_head, dummy_body, dummy_label)
        self.add(dummy_group)

        # ── Landing spot (7.5m offset to the right) ──
        offset_screen = LANDING_OFFSET_M * horiz_scale
        landing_x = dummy_x + offset_screen
        landing_dot = Dot(
            np.array([landing_x, ground_y, 0]),
            radius=0.05, color=GREEN, fill_opacity=0.8,
        )
        landing_label = Text("Landing\nSpot", font_size=10, color=GREEN)
        landing_label.next_to(landing_dot, DOWN, buff=0.08)

        # 7.5m dimension line on ground
        dim_line = Line(
            np.array([dummy_x, ground_y - 0.35, 0]),
            np.array([landing_x, ground_y - 0.35, 0]),
            color=GREY_B, stroke_width=1.5,
        )
        dim_tick_l = Line(
            np.array([dummy_x, ground_y - 0.3, 0]),
            np.array([dummy_x, ground_y - 0.4, 0]),
            color=GREY_B, stroke_width=1.5,
        )
        dim_tick_r = Line(
            np.array([landing_x, ground_y - 0.3, 0]),
            np.array([landing_x, ground_y - 0.4, 0]),
            color=GREY_B, stroke_width=1.5,
        )
        dim_label = Text("7.5 m", font_size=11, color=GREY_B)
        dim_label.next_to(dim_line, DOWN, buff=0.04)
        dim_group = VGroup(dim_line, dim_tick_l, dim_tick_r, dim_label)

        self.add(landing_dot, landing_label, dim_group)

        # ── Build drone body (rectangle + rotors) ──
        def make_drone_side(pos):
            body = Rectangle(
                width=0.55, height=0.10,
                fill_color=WHITE, fill_opacity=0.95,
                stroke_color=GREY_B, stroke_width=1.5,
            )
            # Rotor arms
            arm_l = Line(ORIGIN, UP * 0.10 + LEFT * 0.05, color=GREY_B, stroke_width=2)
            arm_r = Line(ORIGIN, UP * 0.10 + RIGHT * 0.05, color=GREY_B, stroke_width=2)
            arm_l.move_to(body.get_left() + UP * 0.05)
            arm_r.move_to(body.get_right() + UP * 0.05)
            # Rotor discs
            rotor_l = Line(LEFT * 0.12, RIGHT * 0.12, color=BLUE_C, stroke_width=2.5)
            rotor_l.move_to(arm_l.get_end())
            rotor_r = Line(LEFT * 0.12, RIGHT * 0.12, color=BLUE_C, stroke_width=2.5)
            rotor_r.move_to(arm_r.get_end())
            # Hatch (bottom center) — will open for payload release
            hatch_l = Line(LEFT * 0.08, ORIGIN, color=ORANGE, stroke_width=3)
            hatch_r = Line(ORIGIN, RIGHT * 0.08, color=ORANGE, stroke_width=3)
            hatch_l.move_to(body.get_bottom() + LEFT * 0.04)
            hatch_r.move_to(body.get_bottom() + RIGHT * 0.04)

            drone_grp = VGroup(body, arm_l, arm_r, rotor_l, rotor_r, hatch_l, hatch_r)
            drone_grp.move_to(pos)
            return drone_grp

        # Drone starts at 35m, offset 7.5m right of dummy
        # (above landing spot initially, but we show approach diagonal)
        drone_start_pos = np.array([landing_x + 0.3, alt_to_y(TARGET_ALT), 0])
        drone = make_drone_side(drone_start_pos)

        # State badge
        state_badge = _make_state_badge("APPROACH", YELLOW)

        # Altitude label that follows drone
        alt_label = Text(f"{TARGET_ALT:.0f} m", font_size=14, color=TEAL)
        alt_label.next_to(drone, RIGHT, buff=0.15)

        self.play(FadeIn(drone), FadeIn(state_badge), FadeIn(alt_label), run_time=0.4)

        # ── 0.5-1.5s: Descent from 35m to 3m ──
        # Diagonal descent to position above landing spot at 3m
        hover_pos = np.array([landing_x, alt_to_y(HOVER_ALT), 0])

        # Animate descent with altitude label updating
        alt_tracker = ValueTracker(TARGET_ALT)
        alt_label.add_updater(
            lambda m: m.become(
                Text(f"{alt_tracker.get_value():.0f} m", font_size=14, color=TEAL)
            ).next_to(drone, RIGHT, buff=0.15)
        )

        self.play(
            drone.animate.move_to(hover_pos),
            alt_tracker.animate.set_value(HOVER_ALT),
            run_time=1.0,
            rate_func=smooth,
        )

        # ── 1.5-2.0s: HOVER_TARGET, timer starts ──
        hover_badge = _make_state_badge("HOVER_TARGET", ORANGE)
        timer_text = Text("0 / 15 s", font_size=14, color=WHITE)
        timer_text.to_corner(UL, buff=0.3)

        self.play(
            Transform(state_badge, hover_badge),
            FadeIn(timer_text),
            run_time=0.3,
        )
        self.wait(0.2)

        # ── 2.0-2.5s: Stage 1 — Partial release ──
        timer_3 = Text("3 / 15 s", font_size=14, color=WHITE)
        timer_3.to_corner(UL, buff=0.3)

        stage1_label = Text("Stage 1: Partial Release", font_size=16, color=ORANGE, weight=BOLD)
        stage1_label.next_to(drone, LEFT, buff=0.5)

        # Orange flash on drone
        flash1 = Circle(
            radius=0.35, fill_color=ORANGE, fill_opacity=0.4, stroke_width=0,
        ).move_to(drone.get_center())

        # Access hatch parts (indices 5, 6 in the VGroup)
        hatch_l = drone[5]
        hatch_r = drone[6]

        # Payload — golden square, initially at drone bottom
        payload = Square(
            side_length=0.12, fill_color=ManimColor("#FFD700"),
            fill_opacity=1.0, stroke_color=ManimColor("#DAA520"), stroke_width=1.5,
        )
        payload.move_to(drone.get_bottom() + DOWN * 0.06)

        self.play(
            Transform(timer_text, timer_3),
            FadeIn(flash1, scale=0.5),
            FadeIn(stage1_label),
            run_time=0.2,
        )

        # Open hatch stage 1 — doors angle outward slightly
        self.play(
            hatch_l.animate.rotate(25 * DEGREES, about_point=hatch_l.get_right()),
            hatch_r.animate.rotate(-25 * DEGREES, about_point=hatch_r.get_left()),
            FadeOut(flash1),
            FadeIn(payload),
            run_time=0.3,
        )

        # Payload hangs slightly lower (held by second latch)
        payload_partial_pos = drone.get_bottom() + DOWN * 0.18
        dashed_tether = DashedLine(
            drone.get_bottom(), payload_partial_pos,
            color=GREY_B, stroke_width=1.5,
        )

        self.play(
            payload.animate.move_to(payload_partial_pos),
            Create(dashed_tether),
            run_time=0.3,
        )

        # ── 2.5-3.5s: Stage 2 — Full release, payload drops ──
        timer_6 = Text("6 / 15 s", font_size=14, color=WHITE)
        timer_6.to_corner(UL, buff=0.3)

        stage2_label = Text("Stage 2: Full Release", font_size=16, color=ORANGE, weight=BOLD)
        stage2_label.move_to(stage1_label.get_center())

        flash2 = Circle(
            radius=0.35, fill_color=ORANGE, fill_opacity=0.4, stroke_width=0,
        ).move_to(drone.get_center())

        self.play(
            Transform(timer_text, timer_6),
            FadeOut(stage1_label),
            FadeIn(stage2_label),
            FadeIn(flash2, scale=0.5),
            run_time=0.2,
        )

        # Fully open hatch
        self.play(
            hatch_l.animate.rotate(25 * DEGREES, about_point=hatch_l.get_right()),
            hatch_r.animate.rotate(-25 * DEGREES, about_point=hatch_r.get_left()),
            FadeOut(flash2),
            FadeOut(dashed_tether),
            run_time=0.2,
        )

        # Payload falls to ground with accelerating motion
        ground_landing_pos = np.array([landing_x, ground_y + 0.06, 0])

        # Drop trajectory line (faint)
        drop_line = DashedLine(
            payload.get_center(), ground_landing_pos,
            color=ORANGE, stroke_width=1, stroke_opacity=0.3,
        )
        self.add(drop_line)

        self.play(
            payload.animate.move_to(ground_landing_pos),
            run_time=0.4,
            rate_func=rate_functions.ease_in_quad,
        )

        # Impact puff
        impact_ring = Circle(
            radius=0.15, stroke_color=ManimColor("#DAA520"), stroke_width=2,
            fill_opacity=0,
        ).move_to(ground_landing_pos)

        deployed_txt = Text("PAYLOAD DEPLOYED", font_size=20, color=GREEN, weight=BOLD)
        deployed_txt.to_edge(DOWN, buff=0.6)

        self.play(
            GrowFromCenter(impact_ring),
            FadeOut(stage2_label),
            FadeIn(deployed_txt),
            FadeOut(drop_line),
            run_time=0.3,
        )
        self.play(FadeOut(impact_ring), run_time=0.2)

        # ── 3.5-4.0s: Timer fast-forward, drone climbs ──
        timer_15 = Text("15 / 15 s", font_size=14, color=WHITE)
        timer_15.to_corner(UL, buff=0.3)

        return_badge = _make_state_badge("RETURN_TRANSIT", GREY_B)

        # Remove alt label updater before climbing
        alt_label.clear_updaters()

        climb_pos = np.array([landing_x, alt_to_y(TARGET_ALT), 0])
        alt_label_final = Text(f"{TARGET_ALT:.0f} m", font_size=14, color=TEAL)
        alt_label_final.next_to(climb_pos, RIGHT, buff=0.15)

        self.play(
            Transform(timer_text, timer_15),
            run_time=0.2,
        )

        # Close hatch back
        self.play(
            hatch_l.animate.rotate(-50 * DEGREES, about_point=hatch_l.get_right()),
            hatch_r.animate.rotate(50 * DEGREES, about_point=hatch_r.get_left()),
            run_time=0.15,
        )

        self.play(
            drone.animate.move_to(climb_pos),
            Transform(state_badge, return_badge),
            FadeOut(deployed_txt),
            Transform(alt_label, alt_label_final),
            run_time=0.8,
            rate_func=smooth,
        )

        self.wait(0.3)


# ══════════════════════════════════════════════════════════════
#  SCENE 7: Return Home (bird's eye)
# ══════════════════════════════════════════════════════════════

class ReturnHomeScene(Scene):
    def construct(self):
        d = _setup_birdseye()
        tol_screen = d["tol_screen"]
        transit_pts = d["transit_pts"]

        # Background zones
        bg = _make_background_zones(d)
        self.add(bg)

        # TOL marker
        tol_dot = Dot(tol_screen, radius=0.08, color=GREEN, fill_opacity=0.9)
        tol_label = Text("TOL", font_size=12, color=GREEN, weight=BOLD)
        tol_label.next_to(tol_dot, DOWN, buff=0.08)
        self.add(tol_dot, tol_label)

        # Transit waypoint markers (dimmed yellow, showing outbound path)
        wp_labels_text = ["T1", "T2", "T3"]
        wp_dots = VGroup()
        wp_labels = VGroup()
        for i, (pt, name) in enumerate(zip(transit_pts, wp_labels_text)):
            dot = Dot(pt, radius=0.05, color=YELLOW, fill_opacity=0.4)
            label = Text(name, font_size=11, color=YELLOW_A)
            label.next_to(dot, DOWN, buff=0.06)
            wp_dots.add(dot)
            wp_labels.add(label)
        self.add(wp_dots, wp_labels)

        # Outbound transit path (dimmed yellow dashed)
        outbound_path = VGroup()
        outbound_pts = [tol_screen] + transit_pts
        for i in range(len(outbound_pts) - 1):
            seg = DashedLine(
                outbound_pts[i], outbound_pts[i + 1],
                color=YELLOW, stroke_width=1.5, stroke_opacity=0.2,
            )
            outbound_path.add(seg)
        self.add(outbound_path)

        # Payload deployed marker (in focus area)
        focus_center = np.mean(d["focus_pts"], axis=0)
        payload_marker = Square(
            side_length=0.1, fill_color=ManimColor("#FFD700"),
            fill_opacity=0.8, stroke_width=0,
        ).move_to(focus_center)
        payload_label = Text("Payload", font_size=9, color=ManimColor("#DAA520"))
        payload_label.next_to(payload_marker, DOWN, buff=0.05)
        self.add(payload_marker, payload_label)

        # Drone starts near focus area (dummy location)
        drone = _make_drone_icon(focus_center, scale_factor=0.12)
        state_badge = _make_state_badge("RETURN_TRANSIT", GREY_B)
        speed_label = Text("15 m/s", font_size=13, color=GREY_B)
        speed_label.to_corner(UL, buff=0.3).shift(DOWN * 0.4)

        self.play(
            FadeIn(drone),
            FadeIn(state_badge),
            FadeIn(speed_label),
            run_time=0.3,
        )

        # ── 0.5-1.0s: Drone flies to T3 ──
        # Return path: focus_center -> T3 -> T2 -> T1 -> TOL
        return_waypoints = [transit_pts[2], transit_pts[1], transit_pts[0], tol_screen]
        return_wp_names = ["T3", "T2", "T1", "TOL"]

        # Build return path as traced grey dashed line
        traced_segments = VGroup()

        prev_pos = focus_center.copy()
        segment_times = [0.7, 1.0, 1.0, 1.0]  # time per segment

        for i, (wp, name, seg_time) in enumerate(
            zip(return_waypoints, return_wp_names, segment_times)
        ):
            # Grey dashed line segment
            seg_line = DashedLine(
                prev_pos, wp,
                color=GREY, stroke_width=2, stroke_opacity=0.7,
            )

            # Rotate drone toward target
            direction = wp - drone.get_center()
            angle = np.arctan2(direction[1], direction[0]) - PI / 2
            drone.rotate(angle)

            # Pulse waypoint dot on arrival
            if i < 3:  # T3, T2, T1
                pulse = Circle(
                    radius=0.15, stroke_color=GREY, stroke_width=2, fill_opacity=0,
                ).move_to(wp)
                self.play(
                    drone.animate.move_to(wp),
                    Create(seg_line),
                    run_time=seg_time,
                    rate_func=smooth,
                )
                self.play(
                    GrowFromCenter(pulse),
                    run_time=0.15,
                )
                self.play(FadeOut(pulse), run_time=0.1)
            else:
                # Final segment to TOL: state -> LANDING -> DONE
                home_badge = _make_state_badge("RETURN_HOME", GREEN)
                self.play(
                    Transform(state_badge, home_badge),
                    run_time=0.2,
                )

                landing_badge = _make_state_badge("LANDING", GREEN)
                self.play(
                    drone.animate.move_to(wp),
                    Create(seg_line),
                    run_time=seg_time * 0.6,
                    rate_func=smooth,
                )
                self.play(
                    Transform(state_badge, landing_badge),
                    run_time=0.15,
                )

                # Landing animation: drone shrinks slightly
                done_badge = _make_state_badge("DONE", GREEN)
                self.play(
                    drone.animate.scale(0.7),
                    Transform(state_badge, done_badge),
                    run_time=0.3,
                )

            traced_segments.add(seg_line)
            prev_pos = wp.copy()

        # Green pulse on TOL
        tol_pulse = Circle(
            radius=0.25, stroke_color=GREEN, stroke_width=3, fill_opacity=0,
        ).move_to(tol_screen)
        self.play(GrowFromCenter(tol_pulse), run_time=0.3)
        self.play(FadeOut(tol_pulse), run_time=0.2)


# ══════════════════════════════════════════════════════════════
#  SCENE 8: Mission Complete
# ══════════════════════════════════════════════════════════════

class MissionCompleteScene(Scene):
    def construct(self):
        d = _setup_birdseye()

        # Dimmed background
        bg = _make_background_zones(d)
        for mob in bg:
            mob.set_opacity(0.3)
        self.add(bg)

        # ── 0.0-0.5s: Background dims ──
        dim_rect = Rectangle(
            width=15, height=10, fill_color=BLACK, fill_opacity=0.5, stroke_width=0,
        )
        self.play(FadeIn(dim_rect), run_time=0.5)

        # ── 0.5-1.5s: Stats appear one by one ──
        stats_data = [
            ("Coverage:", "96%", GREEN),
            ("Flight Time:", "8 min 32 s", TEAL),
            ("Detections:", "1 confirmed", YELLOW),
            ("Payload:", "Deployed", ORANGE),
        ]

        stats_group = VGroup()
        for label_str, value_str, color in stats_data:
            label = Text(label_str, font_size=22, color=GREY_B)
            value = Text(f" {value_str}", font_size=22, color=color, weight=BOLD)
            row = VGroup(label, value).arrange(RIGHT, buff=0.1)
            stats_group.add(row)

        stats_group.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        stats_group.move_to(UP * 0.8)

        for row in stats_group:
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.2)

        self.wait(0.2)

        # ── 1.5-2.0s: Green checkmark ──
        # Construct checkmark from two line segments
        check_start = np.array([-0.4, 0, 0])
        check_mid = np.array([-0.1, -0.35, 0])
        check_end = np.array([0.5, 0.4, 0])

        checkmark = VMobject(color=GREEN, stroke_width=7)
        checkmark.set_points_as_corners([check_start, check_mid, check_end])
        checkmark.move_to(DOWN * 1.0)

        self.play(Create(checkmark), run_time=0.5)

        # ── 2.0-2.5s: MISSION COMPLETE text ──
        complete_txt = Text(
            "MISSION COMPLETE", font_size=36, color=GREEN, weight=BOLD,
        )
        complete_txt.next_to(checkmark, DOWN, buff=0.3)

        self.play(FadeIn(complete_txt, shift=UP * 0.1), run_time=0.3)

        # ── 2.5-3.0s: Hold, then fade to black ──
        self.wait(0.3)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
