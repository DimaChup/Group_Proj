"""
Mission Performance Profile — Spider/Radar Web Chart Animation.
Desired envelope vs actual selected configuration.

Run:
  python -m manim -pqh spider_web_anim.py SpiderWebChart
"""

from manim import *
import numpy as np


class SpiderWebChart(Scene):
    def construct(self):
        # ── Configuration ──────────────────────────────────
        labels = ["Coverage", "Detection", "Time⁻¹", "Energy⁻¹", "Safety"]
        n_axes = len(labels)
        desired_vals = [1.0, 1.0, 0.5, 0.5, 1.0]
        actual_vals  = [0.96, 0.93, 0.38, 0.40, 1.00]
        actual_pcts  = ["96%", "93%", "38%", "40%", "100%"]
        scale_ticks  = [0.2, 0.4, 0.6, 0.8, 1.0]
        radius = 2.8
        center = ORIGIN + DOWN * 0.3  # shift chart down slightly for title room

        # Angle for each axis: start from top (90°), go clockwise
        angles = [PI / 2 - i * 2 * PI / n_axes for i in range(n_axes)]

        def polar_point(angle, value):
            """Convert (angle, normalised value) to scene coordinates."""
            return center + value * radius * np.array([np.cos(angle), np.sin(angle), 0])

        # ══════════════════════════════════════════════════
        # 1. Title fades in (1s)
        # ══════════════════════════════════════════════════
        title = Text("Mission Performance Profile", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.4)
        self.play(FadeIn(title), run_time=1)

        # ══════════════════════════════════════════════════
        # 2. Draw 5 axes radiating from center + labels (2s)
        # ══════════════════════════════════════════════════
        axes_group = VGroup()
        label_group = VGroup()

        for i, angle in enumerate(angles):
            # Axis line
            end = polar_point(angle, 1.0)
            axis_line = Line(center, end, color=GREY_B, stroke_width=1.5)
            axes_group.add(axis_line)

            # Label at the tip, pushed outward
            label_pos = polar_point(angle, 1.18)
            lbl = Text(labels[i], font_size=18, color=GREY_A)
            lbl.move_to(label_pos)
            label_group.add(lbl)

        self.play(
            *[Create(ax) for ax in axes_group],
            run_time=1.2,
        )
        self.play(
            *[FadeIn(lbl) for lbl in label_group],
            run_time=0.8,
        )

        # ══════════════════════════════════════════════════
        # 3. Concentric pentagons for scale (1s)
        # ══════════════════════════════════════════════════
        grid_group = VGroup()
        for tick in scale_ticks:
            pts = [polar_point(a, tick) for a in angles]
            ring = Polygon(*pts, color=GREY_E, stroke_width=1, stroke_opacity=0.5)
            grid_group.add(ring)

        # Tick labels on the first axis (top)
        tick_labels = VGroup()
        for tick in scale_ticks:
            pos = polar_point(angles[0], tick) + RIGHT * 0.25
            tl = Text(f"{tick:.1f}", font_size=11, color=GREY_C)
            tl.move_to(pos)
            tick_labels.add(tl)

        self.play(
            *[Create(ring) for ring in grid_group],
            *[FadeIn(tl) for tl in tick_labels],
            run_time=1,
        )

        # ══════════════════════════════════════════════════
        # 4. Desired envelope — dashed grey pentagon (2s)
        # ══════════════════════════════════════════════════
        desired_pts = [polar_point(angles[i], desired_vals[i]) for i in range(n_axes)]
        desired_poly = Polygon(*desired_pts, color=GREY_B, stroke_width=2.5)
        desired_dashed = DashedVMobject(desired_poly, num_dashes=30)

        desired_label = Text("Desired envelope", font_size=20, color=GREY_B)
        desired_label.next_to(title, DOWN, buff=0.2).align_to(title, LEFT)

        self.play(FadeIn(desired_label), run_time=0.5)
        self.play(Create(desired_dashed), run_time=1.5)

        # ══════════════════════════════════════════════════
        # 5. Selected configuration — filled blue polygon (2s)
        # ══════════════════════════════════════════════════
        actual_pts = [polar_point(angles[i], actual_vals[i]) for i in range(n_axes)]
        actual_poly = Polygon(
            *actual_pts,
            color=BLUE_D,
            fill_color=BLUE_D,
            fill_opacity=0.3,
            stroke_width=2.5,
        )

        config_label = Text("Selected configuration", font_size=20, color=BLUE_D)
        config_label.next_to(desired_label, DOWN, buff=0.15).align_to(desired_label, LEFT)

        self.play(FadeIn(config_label), run_time=0.5)
        self.play(DrawBorderThenFill(actual_poly), run_time=1.5)

        # ══════════════════════════════════════════════════
        # 6. Data labels on each vertex (1s)
        # ══════════════════════════════════════════════════
        pct_group = VGroup()
        for i in range(n_axes):
            # Position label slightly inside the actual vertex
            direction = np.array([np.cos(angles[i]), np.sin(angles[i]), 0])
            pos = polar_point(angles[i], actual_vals[i]) - direction * 0.28
            pct = Text(actual_pcts[i], font_size=16, color=WHITE, weight=BOLD)
            pct.move_to(pos)
            pct_group.add(pct)

        # Small dots on actual vertices
        dots = VGroup()
        for pt in actual_pts:
            dot = Dot(pt, radius=0.05, color=BLUE)
            dots.add(dot)

        self.play(
            *[FadeIn(d) for d in dots],
            *[FadeIn(p) for p in pct_group],
            run_time=1,
        )

        # ══════════════════════════════════════════════════
        # 7. Success annotation (1s)
        # ══════════════════════════════════════════════════
        annotation = Text(
            "Fits within desired envelope  \u2713",
            font_size=24, color=GREEN, weight=BOLD,
        )
        annotation.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(annotation, shift=UP * 0.3), run_time=1)

        # ══════════════════════════════════════════════════
        # 8. Hold (2s)
        # ══════════════════════════════════════════════════
        self.wait(2)
