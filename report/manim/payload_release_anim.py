"""
Payload Release Animation — Side-view of drone descending and deploying payload.

Shows the full sequence:
  - Drone at 35m altitude, 7.5m offset from target casualty
  - Smooth descent: 35m -> 15m -> 5m -> 3m
  - HOVER_TARGET state with timer
  - 2-stage servo release (partial at 3s, full at 6s)
  - Payload falls to ground
  - Drone climbs back to 35m and flies away

Run:
  python -m manim -pqh payload_release_anim.py PayloadReleaseScene
  python -m manim -pql payload_release_anim.py PayloadReleaseScene   # low quality
"""

from manim import *
import numpy as np


class PayloadReleaseScene(Scene):
    def construct(self):
        # ── Layout constants ──
        # Side view: x = horizontal, y = vertical (altitude)
        GROUND_Y = -3.2
        MAX_ALT_Y = 3.2          # 35m mapped here
        TARGET_X = -1.5          # casualty position
        DRONE_X = TARGET_X + 2.5  # 7.5m offset (scaled)
        FLYAWAY_X = 7.0

        # Altitude mapping: 0m -> GROUND_Y, 35m -> MAX_ALT_Y
        def alt_to_y(alt_m):
            return GROUND_Y + (alt_m / 35.0) * (MAX_ALT_Y - GROUND_Y)

        # ── Ground ──
        ground = Line(
            start=np.array([-7, GROUND_Y, 0]),
            end=np.array([7, GROUND_Y, 0]),
            stroke_width=3,
            color=GREEN_D,
        )
        grass_lines = VGroup()
        for gx in np.arange(-6.5, 7.0, 0.5):
            gl = Line(
                start=np.array([gx, GROUND_Y, 0]),
                end=np.array([gx - 0.15, GROUND_Y - 0.2, 0]),
                stroke_width=1,
                color=GREEN_E,
            )
            grass_lines.add(gl)

        # ── Target casualty (red cross) ──
        cross_size = 0.25
        cross_v = Line(
            np.array([TARGET_X, GROUND_Y + cross_size, 0]),
            np.array([TARGET_X, GROUND_Y + 0.05, 0]),
            stroke_width=5, color=RED,
        )
        cross_h = Line(
            np.array([TARGET_X - cross_size * 0.5, GROUND_Y + cross_size * 0.6, 0]),
            np.array([TARGET_X + cross_size * 0.5, GROUND_Y + cross_size * 0.6, 0]),
            stroke_width=5, color=RED,
        )
        cross_circle = Circle(
            radius=0.35, stroke_width=2, color=RED, fill_opacity=0.15, fill_color=RED,
        ).move_to(np.array([TARGET_X, GROUND_Y + cross_size * 0.6, 0]))
        casualty = VGroup(cross_circle, cross_v, cross_h)
        casualty_label = Text("Casualty", font_size=18, color=RED_B).next_to(
            casualty, DOWN, buff=0.15
        )

        # ── 7.5m offset indicator ──
        offset_line = DashedVMobject(
            Line(
                np.array([TARGET_X, GROUND_Y + 0.6, 0]),
                np.array([DRONE_X, GROUND_Y + 0.6, 0]),
                stroke_width=2, color=YELLOW,
            ),
            num_dashes=12,
        )
        offset_label = Text("7.5m offset", font_size=18, color=YELLOW).next_to(
            offset_line, DOWN, buff=0.1
        )
        offset_group = VGroup(offset_line, offset_label)

        # ── Drone body ──
        drone_body = Rectangle(
            width=0.9, height=0.25,
            fill_color=BLUE_D, fill_opacity=1.0,
            stroke_width=2, stroke_color=BLUE_B,
        )
        # Rotor arms
        arm_l = Line(np.array([-0.45, 0, 0]), np.array([-0.7, 0.2, 0]),
                      stroke_width=2, color=BLUE_C)
        arm_r = Line(np.array([0.45, 0, 0]), np.array([0.7, 0.2, 0]),
                      stroke_width=2, color=BLUE_C)
        rotor_l = Ellipse(width=0.4, height=0.08, fill_color=GREY, fill_opacity=0.6,
                          stroke_width=1, color=GREY_B).move_to(arm_l.get_end())
        rotor_r = Ellipse(width=0.4, height=0.08, fill_color=GREY, fill_opacity=0.6,
                          stroke_width=1, color=GREY_B).move_to(arm_r.get_end())

        # Servo hatch (under drone body)
        hatch_left = Line(
            np.array([-0.15, -0.125, 0]),
            np.array([-0.15, -0.3, 0]),
            stroke_width=3, color=ORANGE,
        )
        hatch_right = Line(
            np.array([0.15, -0.125, 0]),
            np.array([0.15, -0.3, 0]),
            stroke_width=3, color=ORANGE,
        )

        # Payload (small square attached under hatch)
        payload = Square(
            side_length=0.18,
            fill_color=GOLD_D, fill_opacity=1.0,
            stroke_width=1.5, stroke_color=GOLD_A,
        )
        payload.move_to(np.array([0, -0.33, 0]))

        drone = VGroup(arm_l, arm_r, rotor_l, rotor_r, drone_body,
                        hatch_left, hatch_right, payload)
        drone.move_to(np.array([DRONE_X, alt_to_y(35), 0]))

        # ── Altitude labels ──
        alt_label = Text("35m", font_size=20, color=WHITE).next_to(drone, RIGHT, buff=0.3)

        # ── Altitude scale on the left ──
        alt_axis = Line(
            np.array([-6.2, GROUND_Y, 0]),
            np.array([-6.2, MAX_ALT_Y, 0]),
            stroke_width=1, color=GREY,
        )
        alt_ticks = VGroup()
        for am in [0, 5, 10, 15, 20, 25, 30, 35]:
            y = alt_to_y(am)
            tick = Line(
                np.array([-6.3, y, 0]), np.array([-6.1, y, 0]),
                stroke_width=1, color=GREY,
            )
            lbl = Text(f"{am}m", font_size=12, color=GREY_B).next_to(tick, LEFT, buff=0.08)
            alt_ticks.add(VGroup(tick, lbl))

        # ── State label ──
        state_label = Text("DESCENDING", font_size=26, color=TEAL_B,
                           weight=BOLD).to_edge(UP, buff=0.3)

        # ── Timer (hidden initially) ──
        timer_label = Text("0s", font_size=22, color=WHITE).to_corner(UR, buff=0.5)
        timer_label.set_opacity(0)

        # ══════════════════════════════════════════
        # SCENE BUILD
        # ══════════════════════════════════════════

        # Fade in environment
        self.play(
            FadeIn(ground), FadeIn(grass_lines),
            FadeIn(casualty), FadeIn(casualty_label),
            FadeIn(alt_axis), FadeIn(alt_ticks),
            run_time=0.7,
        )
        self.play(
            FadeIn(drone), FadeIn(alt_label),
            FadeIn(offset_group),
            FadeIn(state_label),
            run_time=0.6,
        )
        self.wait(0.3)

        # ── Descent: 35m -> 15m ──
        target_y_15 = alt_to_y(15)
        new_alt_15 = Text("15m", font_size=20, color=WHITE)

        self.play(
            drone.animate.move_to(np.array([DRONE_X, target_y_15, 0])),
            Transform(alt_label, new_alt_15.next_to(
                np.array([DRONE_X + 0.75, target_y_15, 0]), RIGHT, buff=0)),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.2)

        # ── Descent: 15m -> 5m ──
        target_y_5 = alt_to_y(5)
        new_alt_5 = Text("5m", font_size=20, color=WHITE)

        self.play(
            drone.animate.move_to(np.array([DRONE_X, target_y_5, 0])),
            Transform(alt_label, new_alt_5.next_to(
                np.array([DRONE_X + 0.75, target_y_5, 0]), RIGHT, buff=0)),
            run_time=1.2,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.2)

        # ── Descent: 5m -> 3m ──
        target_y_3 = alt_to_y(3)
        new_alt_3 = Text("3m", font_size=20, color=YELLOW)

        self.play(
            drone.animate.move_to(np.array([DRONE_X, target_y_3, 0])),
            Transform(alt_label, new_alt_3.next_to(
                np.array([DRONE_X + 0.75, target_y_3, 0]), RIGHT, buff=0)),
            run_time=0.8,
            rate_func=rate_functions.ease_in_out_cubic,
        )

        # ── State: HOVER_TARGET ──
        new_state = Text("HOVER_TARGET", font_size=26, color=GOLD,
                         weight=BOLD).to_edge(UP, buff=0.3)
        self.play(
            Transform(state_label, new_state),
            run_time=0.4,
        )

        # ── Timer: 0s -> 3s (partial release) ──
        timer_label.set_opacity(1)
        timer_label.become(Text("Timer: 0s", font_size=22, color=WHITE).to_corner(UR, buff=0.5))
        self.play(FadeIn(timer_label), run_time=0.3)

        # Animate timer 0->3s
        for sec in [1, 2, 3]:
            col = YELLOW if sec == 3 else WHITE
            new_timer = Text(f"Timer: {sec}s", font_size=22, color=col).to_corner(UR, buff=0.5)
            self.play(Transform(timer_label, new_timer), run_time=0.35)

        # ── Servo partial release at 3s ──
        servo_label = Text("Servo: PARTIAL", font_size=18, color=ORANGE).next_to(
            state_label, DOWN, buff=0.2
        )
        self.play(FadeIn(servo_label), run_time=0.3)

        # Open hatch doors partway (rotate outward)
        self.play(
            hatch_left.animate.rotate(PI / 6, about_point=hatch_left.get_start()),
            hatch_right.animate.rotate(-PI / 6, about_point=hatch_right.get_start()),
            run_time=0.5,
        )
        self.wait(0.2)

        # ── Timer: 3s -> 6s (full release) ──
        for sec in [4, 5, 6]:
            col = RED_B if sec == 6 else WHITE
            new_timer = Text(f"Timer: {sec}s", font_size=22, color=col).to_corner(UR, buff=0.5)
            self.play(Transform(timer_label, new_timer), run_time=0.35)

        # ── Full release at 6s ──
        new_servo = Text("Servo: FULL RELEASE", font_size=18, color=RED_B).next_to(
            state_label, DOWN, buff=0.2
        )
        self.play(
            Transform(servo_label, new_servo),
            hatch_left.animate.rotate(PI / 6, about_point=hatch_left.get_start()),
            hatch_right.animate.rotate(-PI / 6, about_point=hatch_right.get_start()),
            run_time=0.4,
        )

        # ── Payload detach and fall ──
        # Remove payload from drone group so it can move independently
        drone.remove(payload)
        payload_pos = payload.get_center()
        payload.move_to(payload_pos)  # keep absolute position
        self.add(payload)

        ground_land_y = GROUND_Y + 0.12
        self.play(
            payload.animate.move_to(np.array([payload_pos[0], ground_land_y, 0])),
            run_time=0.6,
            rate_func=rate_functions.ease_in_quad,
        )

        # Bounce
        self.play(
            payload.animate.shift(UP * 0.12),
            run_time=0.1,
            rate_func=rate_functions.ease_out_quad,
        )
        self.play(
            payload.animate.shift(DOWN * 0.12),
            run_time=0.1,
            rate_func=rate_functions.ease_in_quad,
        )

        # ── Timer continues to 15s ──
        for sec in [9, 12, 15]:
            new_timer = Text(f"Timer: {sec}s", font_size=22,
                             color=GREEN if sec == 15 else WHITE).to_corner(UR, buff=0.5)
            self.play(Transform(timer_label, new_timer), run_time=0.3)

        # ── PAYLOAD DEPLOYED ──
        deploy_text = Text("PAYLOAD DEPLOYED", font_size=30, color=GREEN,
                           weight=BOLD).move_to(np.array([0, 0.5, 0]))
        deploy_box = SurroundingRectangle(deploy_text, color=GREEN, buff=0.15,
                                           stroke_width=2, fill_color=BLACK,
                                           fill_opacity=0.7)
        self.play(
            FadeIn(deploy_box), FadeIn(deploy_text),
            run_time=0.5,
        )
        self.wait(0.5)
        self.play(FadeOut(deploy_box), FadeOut(deploy_text), run_time=0.3)

        # ── Drone climbs: 3m -> 35m ──
        climb_state = Text("CLIMBING", font_size=26, color=TEAL_B,
                           weight=BOLD).to_edge(UP, buff=0.3)
        self.play(
            Transform(state_label, climb_state),
            FadeOut(servo_label),
            run_time=0.3,
        )

        new_alt_35 = Text("35m", font_size=20, color=WHITE)
        self.play(
            drone.animate.move_to(np.array([DRONE_X, alt_to_y(35), 0])),
            Transform(alt_label, new_alt_35.next_to(
                np.array([DRONE_X + 0.75, alt_to_y(35), 0]), RIGHT, buff=0)),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_cubic,
        )

        # ── RETURN_HOME: drone flies away ──
        rtl_state = Text("RETURN_HOME", font_size=26, color=BLUE_B,
                         weight=BOLD).to_edge(UP, buff=0.3)
        self.play(
            Transform(state_label, rtl_state),
            FadeOut(timer_label),
            run_time=0.3,
        )

        self.play(
            drone.animate.move_to(np.array([FLYAWAY_X, alt_to_y(35), 0])),
            FadeOut(alt_label),
            FadeOut(offset_group),
            run_time=1.5,
            rate_func=rate_functions.ease_in_cubic,
        )

        # ── Final stats bar ──
        stats_text = Text(
            "Landing offset: 7.5m  |  Deploy altitude: 3m  |  Servo: 2-stage",
            font_size=20, color=WHITE,
        ).to_edge(DOWN, buff=0.4)
        stats_bg = SurroundingRectangle(
            stats_text, color=BLUE_D, buff=0.12,
            stroke_width=1, fill_color=BLACK, fill_opacity=0.8,
        )
        self.play(FadeIn(stats_bg), FadeIn(stats_text), run_time=0.5)
        self.wait(1.0)

        # Fade out
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
