"""
NFZ Protection System Animation — Scalar Field, Repulsive Vectors, Drone Deflection.

Shows the three-layer geofence protection system as a physics simulation:
  Layer 1: Speed scalar field (20m gradient ramp)
  Layer 2: Repulsive vector field (3m push zone)
  Layer 3: Hard boundary (3m auto-manual cutoff)

Uses schematic scale (not real GPS) so the protection layers are clearly visible.

Run:
  python -m manim -pqh nfz_field_anim.py NFZFieldScene
  python -m manim -pql nfz_field_anim.py NFZFieldScene   # low quality (fast)
"""

from manim import *
import numpy as np


# ── Schematic NFZ polygon (irregular 7-sided, centred at origin) ──
# Loosely based on the SSSI shape but scaled so 1 unit ~ 10m
NFZ_VERTICES = [
    np.array([-0.8, 1.5, 0]),
    np.array([-1.8, 0.2, 0]),
    np.array([-1.2, -1.3, 0]),
    np.array([0.0, -1.6, 0]),
    np.array([1.3, -0.8, 0]),
    np.array([1.6, 0.5, 0]),
    np.array([0.5, 1.4, 0]),
]

# Scale: 1 screen unit = 10 meters
SCALE_M = 10.0  # meters per screen unit

# NFZ parameters (from config.py)
NFZ_HARD_M = 3.0
NFZ_SLOW_ZONE_M = 20.0
NFZ_ZERO_M = 2.0
NFZ_MAX_SPEED = 3.0
NFZ_PUSH_SPEED = 5.0
NFZ_REPEL_ZONE_M = 5.0  # visual repulsion zone

# Convert meters to screen
def m2s(m):
    return m / SCALE_M


def closest_point_on_polygon_edges(point, poly_pts):
    """Find closest point on polygon boundary and its distance."""
    min_dist = float('inf')
    closest = poly_pts[0].copy()
    n = len(poly_pts)
    for i in range(n):
        a = poly_pts[i][:2]
        b = poly_pts[(i + 1) % n][:2]
        ab = b - a
        ap = point[:2] - a
        ab_sq = np.dot(ab, ab)
        if ab_sq < 1e-10:
            proj = a.copy()
        else:
            t = np.clip(np.dot(ap, ab) / ab_sq, 0, 1)
            proj = a + t * ab
        d = np.linalg.norm(point[:2] - proj)
        if d < min_dist:
            min_dist = d
            closest = np.array([proj[0], proj[1], 0])
    return closest, min_dist


def offset_polygon_pts(pts, dist):
    """Offset polygon outward by dist (screen units) from centroid."""
    arr = np.array(pts)
    c = arr.mean(axis=0)
    result = []
    for pt in arr:
        d = pt - c
        norm = np.linalg.norm(d[:2])
        if norm < 1e-6:
            result.append(pt.copy())
        else:
            result.append(pt + d / norm * dist)
    return result


def speed_at_distance(dist_m):
    """Speed scalar: 0 at zero_m, linear to max at slow_zone_m."""
    if dist_m <= NFZ_ZERO_M:
        return 0.0
    if dist_m >= NFZ_SLOW_ZONE_M:
        return NFZ_MAX_SPEED
    return NFZ_MAX_SPEED * (dist_m - NFZ_ZERO_M) / (NFZ_SLOW_ZONE_M - NFZ_ZERO_M)


class NFZFieldScene(Scene):
    def construct(self):
        nfz = [v.copy() for v in NFZ_VERTICES]
        nfz_center = np.mean(nfz, axis=0)

        # ══════════════════════════════════════════════════════
        # 1. TITLE
        # ══════════════════════════════════════════════════════
        title = Text("NFZ Protection System", font_size=36, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.25)
        subtitle = Text("Three-Layer Geofence", font_size=18, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.1)

        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.6)
        self.play(FadeIn(subtitle), run_time=0.3)
        self.wait(0.5)

        # ══════════════════════════════════════════════════════
        # 2. DRAW SEARCH AREA + SSSI
        # ══════════════════════════════════════════════════════
        # Search area (large green boundary around everything)
        search_pts = offset_polygon_pts(nfz, m2s(45))
        search_poly = Polygon(
            *search_pts,
            color=GREEN, stroke_width=2, fill_color=GREEN, fill_opacity=0.06,
        )
        search_label = Text("Search Area", font_size=12, color=GREEN_B)
        search_label.move_to(np.array([-4.5, -3.0, 0]))

        # SSSI polygon (red with hatching)
        sssi_poly = Polygon(
            *nfz, color=RED, stroke_width=3, fill_color=RED, fill_opacity=0.3,
        )

        # Diagonal hatching
        hatch = VGroup()
        nfz_arr = np.array(nfz)
        xmin, xmax = nfz_arr[:, 0].min() - 0.1, nfz_arr[:, 0].max() + 0.1
        ymin, ymax = nfz_arr[:, 1].min() - 0.1, nfz_arr[:, 1].max() + 0.1
        for k in range(18):
            t = k / 17
            d = (xmin + ymin) + t * ((xmax + ymax) - (xmin + ymin))
            x1 = max(xmin, d - ymax)
            x2 = min(xmax, d - ymin)
            if x2 > x1:
                hatch.add(Line(
                    [x1, d - x1, 0], [x2, d - x2, 0],
                    color=RED, stroke_width=0.8, stroke_opacity=0.4,
                ))

        sssi_label = Text("SSSI No-Fly Zone", font_size=15, color=RED, weight=BOLD)
        sssi_label.move_to(nfz_center)

        self.play(Create(search_poly), FadeIn(search_label), run_time=0.6)
        self.play(
            Create(sssi_poly), FadeIn(hatch, lag_ratio=0.03),
            run_time=0.7,
        )
        self.play(FadeIn(sssi_label), run_time=0.3)
        self.wait(0.3)

        # Scale bar
        bar_start = np.array([-5.5, -3.5, 0])
        bar_20m = Line(bar_start, bar_start + RIGHT * m2s(20),
                       color=WHITE, stroke_width=2)
        bar_text = Text("20 m", font_size=10, color=WHITE)
        bar_text.next_to(bar_20m, DOWN, buff=0.05)
        self.play(Create(bar_20m), FadeIn(bar_text), run_time=0.3)

        # ══════════════════════════════════════════════════════
        # 3a. LAYER 1: Speed Scalar Field
        # ══════════════════════════════════════════════════════
        self.play(FadeOut(title), FadeOut(subtitle), run_time=0.3)
        layer1_title = Text("Layer 1: Speed Scalar Field", font_size=22,
                            color=YELLOW, weight=BOLD)
        layer1_title.to_edge(UP, buff=0.2)
        self.play(FadeIn(layer1_title), run_time=0.4)

        # Gradient bands (concentric rings, green -> yellow -> red)
        num_bands = 16
        gradient_bands = VGroup()
        for i in range(num_bands, 0, -1):
            outer_m = NFZ_ZERO_M + (NFZ_SLOW_ZONE_M - NFZ_ZERO_M) * (i / num_bands)
            inner_m = NFZ_ZERO_M + (NFZ_SLOW_ZONE_M - NFZ_ZERO_M) * ((i - 1) / num_bands)
            outer_pts = offset_polygon_pts(nfz, m2s(outer_m))
            inner_pts = offset_polygon_pts(nfz, m2s(inner_m))

            # Color gradient: red (close) -> yellow (mid) -> green (far)
            frac = i / num_bands
            if frac > 0.5:
                t = (frac - 0.5) * 2
                color = interpolate_color(YELLOW, GREEN, t)
            else:
                t = frac * 2
                color = interpolate_color(RED, YELLOW, t)

            band = Polygon(
                *outer_pts, color=color, stroke_width=0,
                fill_color=color, fill_opacity=0.15,
            )
            gradient_bands.add(band)

        # Dead zone (0-2m, solid red)
        dead_pts = offset_polygon_pts(nfz, m2s(NFZ_ZERO_M))
        dead_zone = Polygon(
            *dead_pts, color=RED, stroke_width=0,
            fill_color=RED, fill_opacity=0.25,
        )
        gradient_bands.add(dead_zone)

        self.play(FadeIn(gradient_bands, lag_ratio=0.04), run_time=1.5)

        # Speed labels along a reference direction (upper-right)
        ref_dir = np.array([1.0, 0.6, 0])
        ref_dir = ref_dir / np.linalg.norm(ref_dir[:2])
        cp, _ = closest_point_on_polygon_edges(nfz_center + ref_dir * 5, nfz)

        speed_labels = VGroup()
        for dist_m, txt, col in [
            (20, "3.0 m/s", GREEN),
            (11, "1.5 m/s", YELLOW),
            (2, "0 m/s", RED),
        ]:
            pos = cp + ref_dir * m2s(dist_m)
            lbl = Text(txt, font_size=12, color=col, weight=BOLD)
            lbl.move_to(pos)
            bg = BackgroundRectangle(lbl, color=BLACK, fill_opacity=0.7, buff=0.04)
            speed_labels.add(VGroup(bg, lbl))

        self.play(FadeIn(speed_labels, lag_ratio=0.15), run_time=0.8)
        self.wait(0.5)

        # ══════════════════════════════════════════════════════
        # 3b. LAYER 2: Repulsive Vector Field
        # ══════════════════════════════════════════════════════
        layer2_title = Text("Layer 2: Repulsive Vector Field", font_size=22,
                            color="#FF6B6B", weight=BOLD)
        layer2_title.to_edge(UP, buff=0.2)
        self.play(FadeOut(layer1_title), FadeIn(layer2_title), run_time=0.4)

        # Arrows pointing outward from each edge
        repulsive_arrows = VGroup()
        n_verts = len(nfz)
        arrows_per_edge = 3

        for i in range(n_verts):
            a = nfz[i]
            b = nfz[(i + 1) % n_verts]
            edge = b - a
            edge_len = np.linalg.norm(edge[:2])
            if edge_len < 0.01:
                continue

            # Outward normal
            normal = np.array([-edge[1], edge[0], 0])
            normal = normal / np.linalg.norm(normal[:2])
            mid = (a + b) / 2
            if np.dot((mid + normal * 0.1 - nfz_center)[:2], normal[:2]) < 0:
                normal = -normal

            for j in range(arrows_per_edge):
                t = (j + 1) / (arrows_per_edge + 1)
                base = a + t * edge
                arrow_start = base + normal * m2s(1.0)
                arrow_end = arrow_start + normal * m2s(4.0)

                arrow = Arrow(
                    arrow_start, arrow_end,
                    color=RED, stroke_width=3.5,
                    max_tip_length_to_length_ratio=0.3,
                    buff=0,
                )
                repulsive_arrows.add(arrow)

        self.play(
            LaggedStart(*[GrowArrow(a) for a in repulsive_arrows], lag_ratio=0.03),
            run_time=1.2,
        )

        # Label
        push_label = Text("5 m/s repulsive push", font_size=13, color=RED, weight=BOLD)
        push_label.to_edge(RIGHT, buff=0.4).shift(UP * 1.5)
        push_bg = BackgroundRectangle(push_label, color=BLACK, fill_opacity=0.7, buff=0.06)
        self.play(FadeIn(push_bg), FadeIn(push_label), run_time=0.3)

        # Pulse arrows (glow effect)
        self.play(
            repulsive_arrows.animate.set_opacity(0.3),
            run_time=0.25, rate_func=there_and_back,
        )
        self.play(
            repulsive_arrows.animate.set_opacity(1.0),
            run_time=0.25, rate_func=there_and_back,
        )
        self.wait(0.3)

        # ══════════════════════════════════════════════════════
        # 3c. LAYER 3: Hard Boundary
        # ══════════════════════════════════════════════════════
        layer3_title = Text("Layer 3: Hard Boundary (3 m)", font_size=22,
                            color="#FF4444", weight=BOLD)
        layer3_title.to_edge(UP, buff=0.2)
        self.play(FadeOut(layer2_title), FadeIn(layer3_title), run_time=0.4)

        hard_pts = offset_polygon_pts(nfz, m2s(NFZ_HARD_M))
        hard_boundary = Polygon(
            *hard_pts, color="#FF0000", stroke_width=4, fill_opacity=0.0,
        )

        am_label = Text("AUTO \u2192 MANUAL", font_size=14, color="#FF4444", weight=BOLD)
        hb_top = max(hard_pts, key=lambda p: p[1])
        am_label.move_to(np.array([hb_top[0], hb_top[1] + 0.3, 0]))
        am_bg = BackgroundRectangle(am_label, color=BLACK, fill_opacity=0.7, buff=0.06)

        self.play(Create(hard_boundary), run_time=0.6)
        self.play(FadeIn(am_bg), FadeIn(am_label), run_time=0.3)
        self.wait(0.3)

        # ══════════════════════════════════════════════════════
        # 4. DRONE APPROACH #1 — from the left
        # ══════════════════════════════════════════════════════
        all_title = Text("Drone Deflection", font_size=22, color=WHITE, weight=BOLD)
        all_title.to_edge(UP, buff=0.2)
        self.play(FadeOut(layer3_title), FadeIn(all_title), run_time=0.3)

        drone_start = np.array([-6.5, 0.5, 0])
        drone = Dot(drone_start, radius=0.12, color=BLUE, fill_opacity=1.0)
        drone_ring = Circle(radius=0.18, color=BLUE_B, stroke_width=2,
                            stroke_opacity=0.5, fill_opacity=0.0)
        drone_ring.add_updater(lambda m: m.move_to(drone.get_center()))

        drone_trail = TracedPath(
            drone.get_center, stroke_color=BLUE, stroke_width=3, stroke_opacity=0.8,
        )

        # Speed indicator
        speed_bar_frame = Rectangle(width=1.8, height=0.2, color=GREY_B,
                                     stroke_width=1.5, fill_color=GREY_D, fill_opacity=0.8)
        speed_bar_frame.to_corner(DR, buff=0.5).shift(UP * 0.3)
        speed_fill = Rectangle(width=1.8, height=0.2, color=GREEN,
                                fill_color=GREEN, fill_opacity=0.9, stroke_width=0)
        speed_fill.move_to(speed_bar_frame).align_to(speed_bar_frame, LEFT)
        speed_txt = Text("3.0 m/s", font_size=13, color=WHITE)
        speed_txt.next_to(speed_bar_frame, UP, buff=0.06)
        speed_lbl = Text("Speed", font_size=10, color=GREY_B)
        speed_lbl.next_to(speed_bar_frame, DOWN, buff=0.06)

        self.add(drone_trail, drone, drone_ring)
        self.play(
            FadeIn(drone, scale=2),
            FadeIn(speed_bar_frame), FadeIn(speed_fill),
            FadeIn(speed_txt), FadeIn(speed_lbl),
            run_time=0.4,
        )

        # Physics simulation for drone path
        pos = drone_start.copy()
        vel = np.array([3.0, 0.2, 0])  # heading right toward NFZ
        dt = 0.05
        num_steps = 100
        path = [pos.copy()]

        for _ in range(num_steps):
            cp, dist_s = closest_point_on_polygon_edges(pos, nfz)
            dist_m = dist_s * SCALE_M

            # Speed clamp
            max_spd_m = speed_at_distance(dist_m)
            max_spd_s = max_spd_m / SCALE_M * 1.5  # visual speed scaling

            # Repulsive force within repel zone
            if dist_m < NFZ_REPEL_ZONE_M + 3:
                repel_dir = pos - cp
                rn = np.linalg.norm(repel_dir[:2])
                if rn > 1e-6:
                    repel_dir = repel_dir / rn
                    strength = max(0, 1.0 - dist_m / (NFZ_REPEL_ZONE_M + 3))
                    vel[:2] += repel_dir[:2] * strength * 12.0 * dt

            # Clamp speed
            spd = np.linalg.norm(vel[:2])
            if dist_m < NFZ_SLOW_ZONE_M:
                effective_max = max(max_spd_s, 0.05)
                if spd > effective_max:
                    vel[:2] = vel[:2] / spd * effective_max

            pos = pos + vel * dt
            pos[2] = 0
            path.append(pos.copy())

        # Animate in chunks
        chunk = 8
        n_chunks = (len(path) - 1 + chunk - 1) // chunk
        total_time = 5.0

        for c in range(n_chunks):
            idx = min((c + 1) * chunk, len(path) - 1)
            target = path[idx]

            cp, dist_s = closest_point_on_polygon_edges(target, nfz)
            dist_m = dist_s * SCALE_M
            spd = speed_at_distance(dist_m)
            frac = min(spd / NFZ_MAX_SPEED, 1.0)

            bar_col = interpolate_color(RED, GREEN, frac)
            new_fill = Rectangle(
                width=max(1.8 * frac, 0.02), height=0.2,
                color=bar_col, fill_color=bar_col, fill_opacity=0.9, stroke_width=0,
            )
            new_fill.move_to(speed_bar_frame).align_to(speed_bar_frame, LEFT)

            new_txt = Text(f"{spd:.1f} m/s", font_size=13, color=WHITE)
            new_txt.next_to(speed_bar_frame, UP, buff=0.06)

            self.play(
                drone.animate.move_to(target),
                Transform(speed_fill, new_fill),
                Transform(speed_txt, new_txt),
                run_time=total_time / n_chunks,
                rate_func=linear,
            )

        self.wait(0.3)

        # ══════════════════════════════════════════════════════
        # 5. DRONE APPROACH #2 — from the top
        # ══════════════════════════════════════════════════════
        self.play(FadeOut(drone), FadeOut(drone_ring), FadeOut(drone_trail),
                  run_time=0.2)

        drone2_start = np.array([0.5, 4.5, 0])
        drone2 = Dot(drone2_start, radius=0.12, color="#00BFFF", fill_opacity=1.0)
        drone2_ring = Circle(radius=0.18, color="#00BFFF", stroke_width=2,
                             stroke_opacity=0.5, fill_opacity=0.0)
        drone2_ring.add_updater(lambda m: m.move_to(drone2.get_center()))
        drone2_trail = TracedPath(
            drone2.get_center, stroke_color="#00BFFF", stroke_width=3, stroke_opacity=0.8,
        )

        self.add(drone2_trail, drone2, drone2_ring)
        self.play(FadeIn(drone2, scale=2), run_time=0.3)

        # Physics for drone 2
        pos2 = drone2_start.copy()
        vel2 = np.array([0.3, -3.0, 0])
        path2 = [pos2.copy()]

        for _ in range(num_steps):
            cp2, dist_s2 = closest_point_on_polygon_edges(pos2, nfz)
            dist_m2 = dist_s2 * SCALE_M
            max_spd_s2 = speed_at_distance(dist_m2) / SCALE_M * 1.5

            if dist_m2 < NFZ_REPEL_ZONE_M + 3:
                rd = pos2 - cp2
                rn2 = np.linalg.norm(rd[:2])
                if rn2 > 1e-6:
                    rd = rd / rn2
                    s2 = max(0, 1.0 - dist_m2 / (NFZ_REPEL_ZONE_M + 3))
                    vel2[:2] += rd[:2] * s2 * 12.0 * dt

            spd2 = np.linalg.norm(vel2[:2])
            if dist_m2 < NFZ_SLOW_ZONE_M:
                eff2 = max(max_spd_s2, 0.05)
                if spd2 > eff2:
                    vel2[:2] = vel2[:2] / spd2 * eff2

            pos2 = pos2 + vel2 * dt
            pos2[2] = 0
            path2.append(pos2.copy())

        total_time2 = 4.0
        for c in range(n_chunks):
            idx = min((c + 1) * chunk, len(path2) - 1)
            target = path2[idx]

            cp2, dist_s2 = closest_point_on_polygon_edges(target, nfz)
            dist_m2 = dist_s2 * SCALE_M
            spd2 = speed_at_distance(dist_m2)
            frac2 = min(spd2 / NFZ_MAX_SPEED, 1.0)

            bar_col2 = interpolate_color(RED, GREEN, frac2)
            nf2 = Rectangle(
                width=max(1.8 * frac2, 0.02), height=0.2,
                color=bar_col2, fill_color=bar_col2, fill_opacity=0.9, stroke_width=0,
            )
            nf2.move_to(speed_bar_frame).align_to(speed_bar_frame, LEFT)
            nt2 = Text(f"{spd2:.1f} m/s", font_size=13, color=WHITE)
            nt2.next_to(speed_bar_frame, UP, buff=0.06)

            self.play(
                drone2.animate.move_to(target),
                Transform(speed_fill, nf2),
                Transform(speed_txt, nt2),
                run_time=total_time2 / n_chunks,
                rate_func=linear,
            )

        self.wait(0.3)

        # ══════════════════════════════════════════════════════
        # 6. SPEED PROFILE GRAPH
        # ══════════════════════════════════════════════════════
        self.play(
            FadeOut(drone2), FadeOut(drone2_ring), FadeOut(drone2_trail),
            FadeOut(speed_bar_frame), FadeOut(speed_fill),
            FadeOut(speed_txt), FadeOut(speed_lbl),
            FadeOut(all_title),
            run_time=0.3,
        )

        graph_title = Text("Speed Profile", font_size=22, color=WHITE, weight=BOLD)
        graph_title.to_edge(UP, buff=0.2)
        self.play(FadeIn(graph_title), run_time=0.3)

        axes = Axes(
            x_range=[0, 22, 5],
            y_range=[0, 3.5, 1],
            x_length=4.0, y_length=2.2,
            axis_config={"color": GREY_B, "stroke_width": 2,
                         "include_numbers": True, "font_size": 16},
            tips=False,
        )
        axes.to_corner(DR, buff=0.5)

        xl = Text("Distance (m)", font_size=11, color=GREY_B)
        xl.next_to(axes, DOWN, buff=0.1)
        yl = Text("Speed (m/s)", font_size=11, color=GREY_B)
        yl.next_to(axes, LEFT, buff=0.1).rotate(PI / 2)

        graph = axes.plot(speed_at_distance, x_range=[0, 22, 0.1],
                          color=YELLOW, stroke_width=3)

        danger_shade = axes.get_area(graph, x_range=[0, 2], color=RED, opacity=0.3)
        slow_shade = axes.get_area(graph, x_range=[2, 20], color=YELLOW, opacity=0.12)

        zero_dash = DashedLine(axes.c2p(2, 0), axes.c2p(2, 3.5),
                               color=RED, stroke_width=2)
        zone_dash = DashedLine(axes.c2p(20, 0), axes.c2p(20, 3.5),
                               color=GREEN, stroke_width=2)

        zl = Text("2m stop", font_size=9, color=RED)
        zl.next_to(zero_dash, UP, buff=0.04)
        zl2 = Text("20m full", font_size=9, color=GREEN)
        zl2.next_to(zone_dash, UP, buff=0.04)

        gbg = BackgroundRectangle(VGroup(axes, xl, yl), color=BLACK,
                                   fill_opacity=0.8, buff=0.15)

        self.play(FadeIn(gbg), Create(axes), FadeIn(xl), FadeIn(yl), run_time=0.6)
        self.play(
            Create(graph),
            FadeIn(danger_shade), FadeIn(slow_shade),
            Create(zero_dash), Create(zone_dash),
            FadeIn(zl), FadeIn(zl2),
            run_time=1.0,
        )
        self.wait(0.5)

        # ══════════════════════════════════════════════════════
        # 7. STATS
        # ══════════════════════════════════════════════════════
        stats = VGroup(
            Text("Layers: 3", font_size=14, color=WHITE),
            Text("|", font_size=14, color=GREY),
            Text("Activation: 20 m", font_size=14, color=YELLOW),
            Text("|", font_size=14, color=GREY),
            Text("Push: 5 m/s", font_size=14, color=RED),
            Text("|", font_size=14, color=GREY),
            Text("Hard boundary: 3 m", font_size=14, color="#FF4444"),
        ).arrange(RIGHT, buff=0.12)
        stats.to_edge(DOWN, buff=0.2)
        stats_bg = BackgroundRectangle(stats, color=BLACK, fill_opacity=0.8, buff=0.1)

        self.play(FadeIn(stats_bg), FadeIn(stats), run_time=0.6)

        # ══════════════════════════════════════════════════════
        # 8. HOLD + FADE
        # ══════════════════════════════════════════════════════
        self.wait(2.0)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.0)
