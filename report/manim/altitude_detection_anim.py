"""
Altitude Detection Animation — Finding the optimal search altitude.

Side-view scene showing:
  - Ground level with a dummy figure (1.8m)
  - Drone rising from 10m to 63m with camera FOV cone
  - Inset "camera view" showing the dummy shrinking + bounding box + confidence
  - Sweet spot at 35m (selected), detection limit at 63m
  - Drone returns to 35m with safety margin annotation
  - Final altitude bar summary

Run:
  python -m manim -pqh altitude_detection_anim.py AltitudeDetectionScene
  python -m manim -pql altitude_detection_anim.py AltitudeDetectionScene   # low quality
"""

from manim import *
import numpy as np


# ── Altitude data points ──
# (altitude_m, confidence, label, color)
ALT_POINTS = [
    (10,  0.98, None,              GREEN),
    (20,  0.95, None,              GREEN),
    (35,  0.90, "SELECTED",        GREEN),
    (50,  0.60, None,              YELLOW),
    (63,  0.20, "DETECTION LIMIT", RED),
]

# Scale: screen units per meter (side view, vertical axis)
# Frame is ~8 units tall, we need 0..63m visible
SCALE = 5.5 / 63.0   # 5.5 screen units for 63m
GROUND_Y = -3.2       # ground level screen y
DRONE_X = -1.5        # drone x position (left side)
DUMMY_X = -1.5        # dummy directly below drone
FOV_HALF_ANGLE = 27.2 # degrees (54.4 HFOV / 2)

# Inset camera view position (right side)
INSET_CENTER = np.array([4.0, 0.5, 0])
INSET_W = 3.2
INSET_H = 2.4


def alt_to_y(alt_m):
    """Convert altitude in meters to screen y coordinate."""
    return GROUND_Y + alt_m * SCALE


def make_drone_icon(scale=0.35):
    """Simple drone icon: body + 4 rotors."""
    body = Rectangle(width=0.6 * scale, height=0.25 * scale,
                     fill_color=BLUE_D, fill_opacity=1, stroke_width=1.5, stroke_color=WHITE)
    arm1 = Line(ORIGIN + LEFT * 0.4 * scale, ORIGIN + RIGHT * 0.4 * scale,
                stroke_width=2, color=GREY_B)
    arm2 = Line(ORIGIN + LEFT * 0.4 * scale, ORIGIN + RIGHT * 0.4 * scale,
                stroke_width=2, color=GREY_B).rotate(PI / 2)
    rotors = VGroup()
    for dx, dy in [(-0.4, 0), (0.4, 0), (0, 0.4), (0, -0.4)]:
        rotor = Circle(radius=0.15 * scale, stroke_width=1.5, stroke_color=GREY_A,
                       fill_color=BLUE_C, fill_opacity=0.3)
        rotor.move_to(np.array([dx * scale, dy * scale, 0]))
        rotors.add(rotor)
    # Camera dot underneath
    cam = Dot(point=DOWN * 0.15 * scale, radius=0.04 * scale, color=RED_C)
    return VGroup(arm1, arm2, body, rotors, cam)


def make_stick_figure(height=0.8, color=ORANGE):
    """Simple stick figure for the dummy."""
    h = height
    head = Circle(radius=h * 0.12, stroke_width=2, stroke_color=color,
                  fill_color=color, fill_opacity=0.3)
    head.move_to(UP * h * 0.88)
    body_line = Line(UP * h * 0.76, UP * h * 0.35, stroke_width=2.5, color=color)
    l_arm = Line(UP * h * 0.65, UP * h * 0.45 + LEFT * h * 0.2, stroke_width=2, color=color)
    r_arm = Line(UP * h * 0.65, UP * h * 0.45 + RIGHT * h * 0.2, stroke_width=2, color=color)
    l_leg = Line(UP * h * 0.35, LEFT * h * 0.15, stroke_width=2, color=color)
    r_leg = Line(UP * h * 0.35, RIGHT * h * 0.15, stroke_width=2, color=color)
    fig = VGroup(head, body_line, l_arm, r_arm, l_leg, r_leg)
    return fig


class AltitudeDetectionScene(Scene):
    def construct(self):
        # ============================================================
        # 1. GROUND + DUMMY + SCENE SETUP
        # ============================================================
        # Ground line
        ground = Line(
            start=np.array([-7, GROUND_Y, 0]),
            end=np.array([1.0, GROUND_Y, 0]),
            stroke_width=3, color=GREEN_E,
        )
        ground_fill = Rectangle(
            width=8, height=0.3,
            fill_color=GREEN_E, fill_opacity=0.2, stroke_width=0,
        ).move_to(np.array([-3, GROUND_Y - 0.15, 0]))

        # Grass texture (little lines)
        grass = VGroup()
        for gx in np.linspace(-6.5, 0.5, 25):
            blade = Line(
                start=np.array([gx, GROUND_Y, 0]),
                end=np.array([gx + 0.05, GROUND_Y + 0.08, 0]),
                stroke_width=1, color=GREEN_D,
            )
            grass.add(blade)

        # Dummy figure at ground level
        dummy_height_screen = 1.8 * SCALE  # 1.8m dummy
        dummy = make_stick_figure(height=dummy_height_screen, color=ORANGE)
        dummy.move_to(np.array([DUMMY_X, GROUND_Y + dummy_height_screen / 2, 0]))

        dummy_label = Text("Dummy\n1.8 m", font_size=16, color=ORANGE).next_to(
            dummy, RIGHT, buff=0.15
        )

        self.play(
            FadeIn(ground), FadeIn(ground_fill), FadeIn(grass),
            FadeIn(dummy), FadeIn(dummy_label),
            run_time=0.8,
        )

        # ============================================================
        # 2. DRONE + FOV CONE + ALTITUDE LABEL
        # ============================================================
        start_alt = 10
        drone = make_drone_icon(scale=0.4)
        drone.move_to(np.array([DRONE_X, alt_to_y(start_alt), 0]))

        # Altitude label next to drone
        alt_text = always_redraw(
            lambda: Text(
                f"{self.current_alt:.0f} m",
                font_size=20, color=WHITE,
            ).next_to(drone, LEFT, buff=0.2)
        )
        self.current_alt = start_alt

        # FOV cone: two lines from drone down to ground
        def make_fov_lines():
            dy = drone.get_center()[1] - GROUND_Y
            if dy < 0.1:
                dy = 0.1
            spread = dy * np.tan(np.radians(FOV_HALF_ANGLE))
            drone_pos = drone.get_center()
            left_pt = np.array([drone_pos[0] - spread, GROUND_Y, 0])
            right_pt = np.array([drone_pos[0] + spread, GROUND_Y, 0])
            l1 = DashedLine(drone_pos, left_pt, stroke_width=1.5, color=YELLOW_C,
                            dashed_ratio=0.5)
            l2 = DashedLine(drone_pos, right_pt, stroke_width=1.5, color=YELLOW_C,
                            dashed_ratio=0.5)
            # Fill triangle
            tri = Polygon(drone_pos, left_pt, right_pt,
                          fill_color=YELLOW, fill_opacity=0.06, stroke_width=0)
            return VGroup(tri, l1, l2)

        fov_cone = always_redraw(make_fov_lines)

        self.play(
            FadeIn(drone), FadeIn(alt_text), FadeIn(fov_cone),
            run_time=0.6,
        )

        # ============================================================
        # 3. INSET CAMERA VIEW
        # ============================================================
        # Outer frame
        inset_border = Rectangle(
            width=INSET_W, height=INSET_H,
            stroke_width=2, stroke_color=WHITE,
            fill_color=BLACK, fill_opacity=0.85,
        ).move_to(INSET_CENTER)
        inset_title = Text("Camera View", font_size=16, color=GREY_B).next_to(
            inset_border, UP, buff=0.08
        )

        # Confidence text (updated each altitude)
        self.conf_val = 0.98
        conf_text = always_redraw(
            lambda: Text(
                f"Conf: {self.conf_val:.2f}",
                font_size=18,
                color=GREEN if self.conf_val >= 0.7 else (YELLOW if self.conf_val >= 0.4 else RED),
            ).move_to(INSET_CENTER + DOWN * (INSET_H / 2 - 0.2))
        )

        # Dummy in inset: size depends on altitude
        # At 10m the dummy is large, at 63m it's tiny
        def dummy_inset_size(alt):
            """Apparent size of dummy in camera view (screen units)."""
            # Real angular size: 1.8m at alt meters
            # Map to inset: at 10m dummy fills ~60% of inset height
            ref_size = INSET_H * 0.6  # size at 10m
            return ref_size * (10.0 / max(alt, 1.0))

        def make_inset_dummy():
            alt = max(self.current_alt, 1)
            sz = dummy_inset_size(alt)
            sz = min(sz, INSET_H * 0.85)  # clamp
            # Simple rectangle for dummy in camera view
            fig = make_stick_figure(height=sz, color=ORANGE)
            fig.move_to(INSET_CENTER + DOWN * 0.05)
            # Bounding box
            pad = 0.08
            bbox = Rectangle(
                width=sz * 0.6 + pad * 2, height=sz + pad * 2,
                stroke_width=2,
                stroke_color=GREEN if self.conf_val >= 0.7 else (YELLOW if self.conf_val >= 0.4 else RED),
            ).move_to(INSET_CENTER + DOWN * 0.05)
            return VGroup(fig, bbox)

        inset_dummy = always_redraw(make_inset_dummy)

        self.play(
            FadeIn(inset_border), FadeIn(inset_title),
            FadeIn(conf_text), FadeIn(inset_dummy),
            run_time=0.6,
        )
        self.wait(0.3)

        # ============================================================
        # 4. ALTITUDE RULER (right edge, subtle)
        # ============================================================
        ruler_x = -5.5
        ruler = Line(
            start=np.array([ruler_x, GROUND_Y, 0]),
            end=np.array([ruler_x, alt_to_y(65), 0]),
            stroke_width=1.5, color=GREY_C,
        )
        ruler_ticks = VGroup()
        for m in [0, 10, 20, 30, 35, 50, 63]:
            y = alt_to_y(m)
            tick = Line(
                np.array([ruler_x - 0.1, y, 0]),
                np.array([ruler_x + 0.1, y, 0]),
                stroke_width=1.5, color=GREY_C,
            )
            lbl = Text(f"{m}", font_size=12, color=GREY_B).next_to(tick, LEFT, buff=0.05)
            ruler_ticks.add(tick, lbl)

        ruler_label = Text("Alt (m)", font_size=14, color=GREY_B).next_to(
            ruler, UP, buff=0.1
        )

        self.play(
            FadeIn(ruler), FadeIn(ruler_ticks), FadeIn(ruler_label),
            run_time=0.5,
        )

        # ============================================================
        # 5. ANIMATE DRONE RISING THROUGH ALTITUDE POINTS
        # ============================================================
        annotations = VGroup()  # collect annotations for cleanup

        for alt, conf, label, color in ALT_POINTS:
            # Animate drone moving up
            target_y = alt_to_y(alt)
            self.play(
                drone.animate.move_to(np.array([DRONE_X, target_y, 0])),
                UpdateFromFunc(drone, lambda m: self._update_alt(m)),
                run_time=0.8 if alt <= 20 else 1.0,
            )
            self.conf_val = conf
            self.wait(0.3)

            # Altitude marker on ruler
            marker_dot = Dot(
                point=np.array([ruler_x, target_y, 0]),
                radius=0.06, color=color,
            )
            self.play(FadeIn(marker_dot), run_time=0.2)
            annotations.add(marker_dot)

            # Special labels
            if label == "SELECTED":
                sel_box = Rectangle(
                    width=2.0, height=0.4,
                    stroke_width=2, stroke_color=GREEN,
                    fill_color=GREEN, fill_opacity=0.15,
                ).move_to(np.array([DRONE_X + 1.8, target_y, 0]))
                sel_text = Text("SELECTED: 35 m", font_size=18, color=GREEN,
                                weight=BOLD).move_to(sel_box)
                sel_group = VGroup(sel_box, sel_text)

                # Horizontal line across
                sel_line = DashedLine(
                    np.array([ruler_x, target_y, 0]),
                    np.array([1.0, target_y, 0]),
                    stroke_width=1.5, color=GREEN, dashed_ratio=0.4,
                )
                self.play(
                    FadeIn(sel_group), Create(sel_line),
                    run_time=0.6,
                )
                annotations.add(sel_group, sel_line)
                self.wait(0.5)

            elif label == "DETECTION LIMIT":
                lim_box = Rectangle(
                    width=2.8, height=0.4,
                    stroke_width=2, stroke_color=RED,
                    fill_color=RED, fill_opacity=0.15,
                ).move_to(np.array([DRONE_X + 2.2, target_y, 0]))
                lim_text = Text("DETECTION LIMIT", font_size=16, color=RED,
                                weight=BOLD).move_to(lim_box)
                lim_group = VGroup(lim_box, lim_text)

                # Threshold line
                thresh_line = DashedLine(
                    np.array([ruler_x, target_y, 0]),
                    np.array([1.0, target_y, 0]),
                    stroke_width=2, color=RED, dashed_ratio=0.3,
                )
                # Confidence threshold annotation
                thresh_label = Text(
                    "conf < 0.25 threshold", font_size=14, color=RED_B,
                ).next_to(thresh_line, RIGHT, buff=0.1)

                self.play(
                    FadeIn(lim_group), Create(thresh_line), FadeIn(thresh_label),
                    run_time=0.6,
                )
                annotations.add(lim_group, thresh_line, thresh_label)
                self.wait(0.6)

        # ============================================================
        # 6. DRONE DESCENDS BACK TO 35m — SAFETY MARGIN
        # ============================================================
        self.wait(0.3)
        target_35_y = alt_to_y(35)
        self.play(
            drone.animate.move_to(np.array([DRONE_X, target_35_y, 0])),
            UpdateFromFunc(drone, lambda m: self._update_alt(m)),
            run_time=1.2,
        )
        self.conf_val = 0.90

        # Safety margin annotation: bracket from 35m to ~41m (15% of 63m ~ 9.5m margin)
        margin_top_y = alt_to_y(63)
        margin_bot_y = alt_to_y(35)

        # Double-headed arrow for margin
        margin_arrow = DoubleArrow(
            start=np.array([-4.2, margin_bot_y, 0]),
            end=np.array([-4.2, margin_top_y, 0]),
            stroke_width=2, color=BLUE_C, tip_length=0.15,
            buff=0,
        )
        margin_label = Text(
            "44% safety\nmargin", font_size=14, color=BLUE_C,
        ).next_to(margin_arrow, LEFT, buff=0.1)

        self.play(
            GrowFromCenter(margin_arrow), FadeIn(margin_label),
            run_time=0.6,
        )
        self.wait(0.5)

        # ============================================================
        # 7. FINAL SUMMARY — ALTITUDE BAR
        # ============================================================
        # Highlight 35m on the ruler with a thicker green band
        band_h = 3.0 * SCALE  # +/- 1.5m visual band
        sweet_band = Rectangle(
            width=0.3, height=band_h,
            fill_color=GREEN, fill_opacity=0.3,
            stroke_width=1, stroke_color=GREEN,
        ).move_to(np.array([ruler_x, target_35_y, 0]))

        sweet_label = Text(
            "Optimal\n35 m", font_size=15, color=GREEN, weight=BOLD,
        ).next_to(sweet_band, LEFT, buff=0.15)

        # Summary text box (top right)
        summary_lines = VGroup(
            Text("Search Altitude Selection", font_size=20, color=WHITE, weight=BOLD),
            Text("Dummy: 1.8 m human figure", font_size=14, color=GREY_B),
            Text("Max detection: 63 m (conf 0.20)", font_size=14, color=RED_B),
            Text("Selected: 35 m (conf 0.90)", font_size=14, color=GREEN),
            Text("Safety margin: 44%", font_size=14, color=BLUE_C),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        summary_box = SurroundingRectangle(
            summary_lines, buff=0.2,
            stroke_color=WHITE, stroke_width=1.5,
            fill_color=BLACK, fill_opacity=0.7,
        )
        summary = VGroup(summary_box, summary_lines).move_to(
            np.array([4.0, -2.2, 0])
        )

        self.play(
            FadeIn(sweet_band), FadeIn(sweet_label),
            FadeIn(summary),
            run_time=0.8,
        )
        self.wait(1.5)

    # ── Helper: update current_alt from drone position ──
    def _update_alt(self, mob):
        y = mob.get_center()[1]
        self.current_alt = max(0, (y - GROUND_Y) / SCALE)
