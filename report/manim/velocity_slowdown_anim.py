"""
Velocity Slowdown Animation — Drone approaching NFZ with scalar field braking.

Zoomed-in view showing:
  - NFZ boundary (thick red line, right side)
  - Color gradient zones: green (safe) -> yellow (slowing) -> red (near stop)
  - Drone with velocity arrow that shrinks as it enters the slowdown zone
  - Speed and distance labels updating in real time
  - Velocity decomposition: total -> toward NFZ + parallel components
  - Repulsive push arrows at 3m
  - Drone stops, curves away, flies parallel

Run:
  python -m manim -pqh velocity_slowdown_anim.py VelocitySlowdownScene
  python -m manim -pql velocity_slowdown_anim.py VelocitySlowdownScene   # low quality
"""

from manim import *
import numpy as np


class VelocitySlowdownScene(Scene):
    def construct(self):
        # ── Layout constants ──
        # NFZ boundary is a vertical line on the right side
        NFZ_X = 4.5          # x position of NFZ boundary
        ZONE_WIDTH = 5.5      # 20m zone mapped to screen units
        SAFE_LEFT = NFZ_X - ZONE_WIDTH  # where green zone starts (x = -1)

        # Scale: ZONE_WIDTH screen units = 20 meters
        M_PER_UNIT = 20.0 / ZONE_WIDTH

        # Drone path
        DRONE_START_X = -5.5
        DRONE_Y = 0.0
        DRONE_CLOSEST_X = NFZ_X - (2.0 / M_PER_UNIT)  # 2m from boundary
        MAX_SPEED = 8.0       # m/s at full speed

        # ── NFZ boundary ──
        nfz_line = Line(
            start=np.array([NFZ_X, -4, 0]),
            end=np.array([NFZ_X, 4, 0]),
            stroke_width=6,
            color=RED,
        )
        nfz_label = Text("NFZ\nBoundary", font_size=22, color=RED).next_to(
            nfz_line, RIGHT, buff=0.2
        )

        # ── Color gradient zones ──
        # Three rectangles: green (safe), yellow (slowing), red (danger)
        zone_height = 8.0

        # Red zone: 0-5m from boundary
        red_w = 5.0 / M_PER_UNIT
        red_zone = Rectangle(
            width=red_w, height=zone_height,
            fill_color=RED, fill_opacity=0.15,
            stroke_width=0,
        ).move_to(np.array([NFZ_X - red_w / 2, 0, 0]))

        # Yellow zone: 5-15m
        yellow_w = 10.0 / M_PER_UNIT
        yellow_zone = Rectangle(
            width=yellow_w, height=zone_height,
            fill_color=YELLOW, fill_opacity=0.12,
            stroke_width=0,
        ).move_to(np.array([NFZ_X - red_w - yellow_w / 2, 0, 0]))

        # Green zone: 15-20m
        green_w = 5.0 / M_PER_UNIT
        green_zone = Rectangle(
            width=green_w, height=zone_height,
            fill_color=GREEN, fill_opacity=0.10,
            stroke_width=0,
        ).move_to(np.array([NFZ_X - red_w - yellow_w - green_w / 2, 0, 0]))

        # Zone labels at top
        zone_label_y = 3.3
        safe_label = Text("Safe\n>20m", font_size=16, color=GREEN_C).move_to(
            np.array([SAFE_LEFT - 1.0, zone_label_y, 0])
        )
        slow_label = Text("Slowing\n10-20m", font_size=16, color=YELLOW_C).move_to(
            np.array([NFZ_X - red_w - yellow_w / 2, zone_label_y, 0])
        )
        danger_label = Text("Near Stop\n<5m", font_size=16, color=RED_C).move_to(
            np.array([NFZ_X - red_w / 2, zone_label_y, 0])
        )

        # ── Drone ──
        drone_pos = ValueTracker(DRONE_START_X)
        drone_y_offset = ValueTracker(0.0)  # for curving away

        drone_dot = always_redraw(lambda: Dot(
            point=np.array([drone_pos.get_value(), DRONE_Y + drone_y_offset.get_value(), 0]),
            radius=0.15, color=BLUE, z_index=5,
        ))
        drone_label = always_redraw(lambda: Text(
            "Drone", font_size=18, color=BLUE
        ).next_to(drone_dot, DOWN, buff=0.2))

        # ── Distance calculation ──
        def get_distance_m():
            """Distance from drone to NFZ boundary in meters."""
            dx = NFZ_X - drone_pos.get_value()
            return max(dx * M_PER_UNIT, 0.0)

        def get_speed_scalar():
            """Speed scalar based on distance to NFZ (from config.py logic)."""
            d = get_distance_m()
            if d >= 20.0:
                return 1.0
            elif d <= 2.0:
                return 0.0
            else:
                return (d - 2.0) / (20.0 - 2.0)

        def get_current_speed():
            return MAX_SPEED * get_speed_scalar()

        # ── Velocity arrow (toward NFZ = rightward) ──
        def make_velocity_arrow():
            x = drone_pos.get_value()
            y = DRONE_Y + drone_y_offset.get_value()
            speed = get_current_speed()
            arrow_len = max(speed / MAX_SPEED * 2.0, 0.05)  # scale arrow length
            color = interpolate_color(RED, GREEN, speed / MAX_SPEED)
            return Arrow(
                start=np.array([x, y, 0]),
                end=np.array([x + arrow_len, y, 0]),
                buff=0,
                stroke_width=4,
                color=color,
                max_tip_length_to_length_ratio=0.3,
                z_index=6,
            )

        velocity_arrow = always_redraw(make_velocity_arrow)

        # ── Speed text ──
        speed_text = always_redraw(lambda: Text(
            f"Speed: {get_current_speed():.1f} m/s",
            font_size=24, color=WHITE,
        ).to_corner(UL, buff=0.4))

        # ── Distance text ──
        distance_text = always_redraw(lambda: Text(
            f"Distance to NFZ: {get_distance_m():.1f}m",
            font_size=24, color=WHITE,
        ).next_to(speed_text, DOWN, aligned_edge=LEFT, buff=0.15))

        # ── Scalar value text ──
        scalar_text = always_redraw(lambda: Text(
            f"Speed scalar: {get_speed_scalar():.2f}",
            font_size=20, color=YELLOW_C,
        ).next_to(distance_text, DOWN, aligned_edge=LEFT, buff=0.15))

        # ── Build scene ──
        self.add(
            green_zone, yellow_zone, red_zone,
            nfz_line, nfz_label,
            safe_label, slow_label, danger_label,
        )
        self.play(
            FadeIn(drone_dot), FadeIn(drone_label),
            FadeIn(velocity_arrow),
            FadeIn(speed_text), FadeIn(distance_text), FadeIn(scalar_text),
            run_time=0.8,
        )

        # ── Phase 1: Fly toward NFZ (fast in safe zone) ──
        # Move from start to edge of slowdown zone
        edge_of_zone_x = NFZ_X - ZONE_WIDTH
        self.play(
            drone_pos.animate.set_value(edge_of_zone_x),
            run_time=1.5,
            rate_func=linear,
        )

        # ── Phase 2: Enter slowdown zone — show velocity decomposition ──
        # Add decomposition labels
        decomp_title = Text(
            "Velocity Decomposition", font_size=22, color=WHITE
        ).to_corner(DL, buff=0.5)

        # Components: "toward NFZ" (horizontal, shrinks) and "parallel" (vertical, stays)
        # We'll show these as arrows below the drone
        COMP_Y = -2.0

        toward_label = Text("Toward NFZ (reduced)", font_size=16, color=RED_C)
        parallel_label = Text("Parallel (unchanged)", font_size=16, color=GREEN_C)

        def make_toward_arrow():
            scalar = get_speed_scalar()
            length = max(scalar * 2.0, 0.05)
            color = interpolate_color(RED, ORANGE, scalar)
            arr = Arrow(
                start=np.array([-3.5, COMP_Y, 0]),
                end=np.array([-3.5 + length, COMP_Y, 0]),
                buff=0, stroke_width=4, color=color,
                max_tip_length_to_length_ratio=0.3,
            )
            return arr

        def make_parallel_arrow():
            # Parallel component stays full
            arr = Arrow(
                start=np.array([-3.5, COMP_Y - 0.8, 0]),
                end=np.array([-3.5 + 1.5, COMP_Y - 0.8, 0]),
                buff=0, stroke_width=4, color=GREEN_C,
                max_tip_length_to_length_ratio=0.3,
            )
            return arr

        toward_arrow = always_redraw(make_toward_arrow)
        parallel_arrow = always_redraw(make_parallel_arrow)

        toward_label_dyn = always_redraw(lambda: Text(
            f"Toward NFZ: {get_current_speed():.1f} m/s", font_size=16, color=RED_C
        ).next_to(toward_arrow, UP, buff=0.1))

        parallel_label_fixed = Text(
            "Parallel: 3.0 m/s", font_size=16, color=GREEN_C
        )

        self.play(
            FadeIn(decomp_title),
            FadeIn(toward_arrow), FadeIn(toward_label_dyn),
            FadeIn(parallel_arrow),
            run_time=0.6,
        )
        parallel_label_fixed.next_to(parallel_arrow, UP, buff=0.1)
        self.add(parallel_label_fixed)

        # Separation line
        sep_line = DashedLine(
            start=np.array([-4.5, COMP_Y + 0.5, 0]),
            end=np.array([0.5, COMP_Y + 0.5, 0]),
            color=GREY,
            stroke_width=1,
        )
        self.add(sep_line)

        # ── Phase 3: Slow approach through the gradient ──
        # Move from 20m to 5m — arrow shrinks visibly
        stop_x = NFZ_X - (5.0 / M_PER_UNIT)  # 5m from boundary
        self.play(
            drone_pos.animate.set_value(stop_x),
            run_time=3.0,
            rate_func=linear,
        )

        # ── Phase 4: Danger zone — repulsive push arrows appear ──
        push_label = Text(
            "Repulsive push (3m zone)", font_size=18, color=ORANGE,
        ).move_to(np.array([NFZ_X - 1.5, 2.2, 0]))

        # Create push arrows pointing LEFT (away from boundary)
        push_arrows = VGroup()
        for y_off in [-1.0, -0.3, 0.4, 1.1]:
            pa = Arrow(
                start=np.array([NFZ_X - 0.2, y_off, 0]),
                end=np.array([NFZ_X - 1.2, y_off, 0]),
                buff=0, stroke_width=3, color=ORANGE,
                max_tip_length_to_length_ratio=0.35,
            )
            push_arrows.add(pa)

        # Continue into danger zone, then push arrows appear
        danger_x = NFZ_X - (3.0 / M_PER_UNIT)  # 3m from boundary
        self.play(
            drone_pos.animate.set_value(danger_x),
            run_time=1.5,
            rate_func=linear,
        )

        self.play(
            FadeIn(push_arrows, shift=LEFT * 0.3),
            FadeIn(push_label),
            run_time=0.5,
        )

        # Approach to closest point (2m)
        self.play(
            drone_pos.animate.set_value(DRONE_CLOSEST_X),
            run_time=1.0,
            rate_func=smooth,
        )
        self.wait(0.3)

        # ── Phase 5: Pushed back and curve away ──
        pushed_back_x = NFZ_X - (8.0 / M_PER_UNIT)  # pushed back to 8m

        # Flash the drone red briefly
        flash_dot = Dot(
            point=np.array([drone_pos.get_value(), DRONE_Y, 0]),
            radius=0.25, color=RED, fill_opacity=0.6, z_index=4,
        )
        self.play(FadeIn(flash_dot, scale=1.5), run_time=0.3)
        self.play(FadeOut(flash_dot), run_time=0.3)

        # Push back + curve upward (parallel flight)
        self.play(
            drone_pos.animate.set_value(pushed_back_x),
            drone_y_offset.animate.set_value(1.5),
            run_time=2.0,
            rate_func=smooth,
        )

        # ── Phase 6: Fly parallel to boundary ──
        # Remove old decomposition, show "Flying parallel" label
        result_text = Text(
            "Drone deflected — flying parallel to boundary",
            font_size=22, color=GREEN_C,
        ).to_edge(DOWN, buff=0.5)

        self.play(
            FadeOut(push_arrows), FadeOut(push_label),
            FadeOut(decomp_title), FadeOut(toward_arrow), FadeOut(toward_label_dyn),
            FadeOut(parallel_arrow), FadeOut(parallel_label_fixed), FadeOut(sep_line),
            FadeIn(result_text),
            run_time=0.8,
        )

        # Continue upward (parallel flight)
        self.play(
            drone_y_offset.animate.set_value(3.5),
            run_time=2.0,
            rate_func=linear,
        )

        self.wait(0.5)
