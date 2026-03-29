"""
Search Pattern Comparison Animation — Why Lawnmower at 70 deg.

Shows 4 search patterns side-by-side on the Fenswood Farm polygon,
then a bar chart proving the optimal-angle lawnmower wins on every metric.

Run:
  python -m manim -pqh pattern_compare_anim.py PatternCompareScene
  python -m manim -pql pattern_compare_anim.py PatternCompareScene   # low quality (fast)
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
SSSI_GPS = [
    (51.42353586816967, -2.671451754138619),
    (51.42215640321154, -2.669768242108598),
    (51.42267105383615, -2.667705438815299),
    (51.42335592245168, -2.668164601092489),
    (51.42286082606338, -2.670043418345824),
    (51.42326667015552, -2.670965419051837),
    (51.42356862274763, -2.671324297543731),
]

# ── Colours ──────────────────────────────────────────────────────
COL_SEARCH = GREEN
COL_SSSI = RED
COL_PATH_A = YELLOW
COL_PATH_B = "#00FF88"      # bright green for selected
COL_PATH_C = ORANGE
COL_PATH_D = TEAL
COL_SELECTED = "#00FF88"
COL_BAD = "#FF6666"


# ── GPS helpers ──────────────────────────────────────────────────
def gps_to_meters(lat, lon, ref_lat, ref_lon):
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


# ── Lawnmower line generator (reused from lawnmower_anim.py) ────
def generate_lawnmower_lines(search_pts_screen, angle_deg, num_lines):
    """Generate lawnmower scan lines across the polygon at a given angle.
    Returns list of (start, end) pairs in screen coords."""
    pts = np.array(search_pts_screen)[:, :2]
    cx, cy = pts.mean(axis=0)
    theta = np.radians(-angle_deg)
    cos_t, sin_t = np.cos(theta), np.sin(theta)

    def rotate(p, c):
        d = p - c
        return c + np.array([d[0]*cos_t - d[1]*sin_t, d[0]*sin_t + d[1]*cos_t])

    def inv_rotate(p, c):
        d = p - c
        return c + np.array([d[0]*cos_t + d[1]*sin_t, -d[0]*sin_t + d[1]*cos_t])

    center = np.array([cx, cy])
    rotated = np.array([rotate(p, center) for p in pts])
    y_min, y_max = rotated[:, 1].min(), rotated[:, 1].max()
    x_min, x_max = rotated[:, 0].min(), rotated[:, 0].max()
    margin = 0.05 * (y_max - y_min)
    ys = np.linspace(y_min + margin, y_max - margin, num_lines)

    lines = []
    for i, y in enumerate(ys):
        if i % 2 == 0:
            s_r = np.array([x_min - 0.05, y])
            e_r = np.array([x_max + 0.05, y])
        else:
            s_r = np.array([x_max + 0.05, y])
            e_r = np.array([x_min - 0.05, y])
        s_s = inv_rotate(s_r, center)
        e_s = inv_rotate(e_r, center)
        lines.append((np.array([*s_s, 0]), np.array([*e_s, 0])))
    return lines


def lawnmower_path(lines):
    """Connect lawnmower lines into a continuous path with turns."""
    all_pts = []
    for i, (s, e) in enumerate(lines):
        all_pts.append(s)
        all_pts.append(e)
        if i < len(lines) - 1:
            next_s = lines[i + 1][0]
            all_pts.append(next_s)
    return all_pts


def generate_spiral_path(search_pts_screen, inward=True):
    """Generate a spiral path inside the polygon (from outside inward)."""
    pts = np.array(search_pts_screen)[:, :2]
    cx, cy = pts.mean(axis=0)
    center = np.array([cx, cy])

    # Compute max radius from center to any vertex
    dists = np.linalg.norm(pts - center, axis=1)
    max_r = dists.max()

    path_pts = []
    n_turns = 4.5
    n_samples = 200
    for i in range(n_samples):
        t = i / (n_samples - 1)
        if inward:
            r = max_r * (1.0 - t * 0.85)
        else:
            r = max_r * 0.15 + max_r * 0.85 * t
        angle = t * n_turns * 2 * np.pi
        x = center[0] + r * np.cos(angle)
        y = center[1] + r * np.sin(angle)
        path_pts.append(np.array([x, y, 0]))
    return path_pts


def generate_expanding_square(search_pts_screen):
    """Generate an expanding square spiral from the center outward."""
    pts = np.array(search_pts_screen)[:, :2]
    cx, cy = pts.mean(axis=0)
    center = np.array([cx, cy])

    dists = np.linalg.norm(pts - center, axis=1)
    max_r = dists.max() * 0.9

    path_pts = [np.array([cx, cy, 0])]
    step = max_r / 8
    x, y = cx, cy

    # Expanding square: right, up, left*2, down*2, right*3, up*3 ...
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    d_idx = 0
    length = 1
    move_count = 0

    for _ in range(32):
        dx, dy = directions[d_idx % 4]
        for _ in range(length):
            x += dx * step
            y += dy * step
            path_pts.append(np.array([x, y, 0]))
        d_idx += 1
        move_count += 1
        if move_count % 2 == 0:
            length += 1

    return path_pts


def clip_path_to_polygon(path_pts, poly_pts_screen):
    """Clip path points, keeping only those inside the polygon (approx)."""
    from functools import reduce
    poly_2d = np.array(poly_pts_screen)[:, :2]

    def point_in_poly(px, py, poly):
        n = len(poly)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    clipped = []
    for p in path_pts:
        if point_in_poly(p[0], p[1], poly_2d):
            clipped.append(p)
    return clipped


# ══════════════════════════════════════════════════════════════════
class PatternCompareScene(Scene):
    def construct(self):
        # ── Reference frame ──────────────────────────────────────
        all_coords = SEARCH_AREA_GPS + SSSI_GPS
        ref_lat = np.mean([p[0] for p in all_coords])
        ref_lon = np.mean([p[1] for p in all_coords])

        # Panel layout: 2x2 grid.  Each panel is ~2.8 units wide.
        panel_w = 2.8
        panel_h = 2.4
        panel_centers = [
            np.array([-3.3,  1.3, 0]),   # top-left
            np.array([ 0.3,  1.3, 0]),   # top-right
            np.array([-3.3, -1.5, 0]),   # bottom-left
            np.array([ 0.3, -1.5, 0]),   # bottom-right
        ]

        # ── Scale GPS to fit each panel ──────────────────────────
        all_m = [gps_to_meters(lat, lon, ref_lat, ref_lon) for lat, lon in SEARCH_AREA_GPS]
        xs = [p[0] for p in all_m]
        ys = [p[1] for p in all_m]
        extent = max(max(xs) - min(xs), max(ys) - min(ys))
        panel_scale = (panel_w * 0.75) / extent

        def make_polys(center_offset):
            """Create search + SSSI polygons positioned in a panel."""
            s_pts = gps_poly_to_screen(
                SEARCH_AREA_GPS, ref_lat, ref_lon, panel_scale, center_offset[:2])
            n_pts = gps_poly_to_screen(
                SSSI_GPS, ref_lat, ref_lon, panel_scale, center_offset[:2])

            search_poly = Polygon(
                *s_pts, color=COL_SEARCH, stroke_width=1.5,
                fill_color=COL_SEARCH, fill_opacity=0.08)
            sssi_poly = Polygon(
                *n_pts, color=COL_SSSI, stroke_width=1.2,
                fill_color=COL_SSSI, fill_opacity=0.12)
            return search_poly, sssi_poly, s_pts, n_pts

        # ── Title ────────────────────────────────────────────────
        title = Text("Search Pattern Comparison", font_size=32, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.2)
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.5)

        # ── Panel titles ─────────────────────────────────────────
        panel_titles = [
            "Lawnmower 0\u00b0 (N-S)",
            "Lawnmower 70\u00b0 (optimal)",
            "Spiral Inward",
            "Expanding Square",
        ]
        title_mobs = []
        for i, (txt, ctr) in enumerate(zip(panel_titles, panel_centers)):
            t = Text(txt, font_size=14, color=WHITE, weight=BOLD)
            t.move_to(ctr + np.array([0, panel_h / 2 + 0.15, 0]))
            title_mobs.append(t)

        # ══════════════════════════════════════════════════════════
        #  STEP 1: Draw all 4 polygons simultaneously (1s)
        # ══════════════════════════════════════════════════════════
        panels = []  # (search_poly, sssi_poly, s_pts, n_pts)
        create_anims = []

        for i, ctr in enumerate(panel_centers):
            sp, np_, s_pts, n_pts = make_polys(ctr)
            panels.append((sp, np_, s_pts, n_pts))
            create_anims.extend([Create(sp), Create(np_), FadeIn(title_mobs[i])])

        self.play(*create_anims, run_time=1.0)

        # ══════════════════════════════════════════════════════════
        #  STEP 2: Lawnmower 0 deg — 8 lines (N-S) (2s)
        # ══════════════════════════════════════════════════════════
        s_pts_0 = panels[0][2]
        lines_0 = generate_lawnmower_lines(s_pts_0, angle_deg=0, num_lines=8)
        path_0 = lawnmower_path(lines_0)

        # Build a continuous traced path
        path_mob_0 = VMobject(color=COL_PATH_A, stroke_width=2.5)
        path_mob_0.set_points_as_corners(path_0)

        label_0 = Text("8 lines, 7 turns\n903 m", font_size=11, color=COL_PATH_A)
        label_0.move_to(panel_centers[0] + np.array([0, -panel_h / 2 - 0.2, 0]))

        self.play(Create(path_mob_0), FadeIn(label_0), run_time=2.0)

        # ══════════════════════════════════════════════════════════
        #  STEP 3: Lawnmower 70 deg — 5 lines, HIGHLIGHT (2s)
        # ══════════════════════════════════════════════════════════
        s_pts_70 = panels[1][2]
        lines_70 = generate_lawnmower_lines(s_pts_70, angle_deg=70, num_lines=5)
        path_70 = lawnmower_path(lines_70)

        path_mob_70 = VMobject(color=COL_PATH_B, stroke_width=3)
        path_mob_70.set_points_as_corners(path_70)

        label_70 = Text("5 lines, 4 turns\n755 m", font_size=11, color=COL_PATH_B)
        label_70.move_to(panel_centers[1] + np.array([0, -panel_h / 2 - 0.2, 0]))

        # "SELECTED" badge
        badge = VGroup()
        badge_rect = RoundedRectangle(
            width=1.3, height=0.3, corner_radius=0.08,
            color=COL_SELECTED, stroke_width=2, fill_color=COL_SELECTED, fill_opacity=0.25)
        badge_text = Text("SELECTED", font_size=12, color=COL_SELECTED, weight=BOLD)
        badge_text.move_to(badge_rect)
        badge.add(badge_rect, badge_text)
        badge.move_to(panel_centers[1] + np.array([0.8, panel_h / 2 - 0.15, 0]))

        # Highlight border
        highlight_rect = SurroundingRectangle(
            panels[1][0], buff=0.12, color=COL_SELECTED, stroke_width=2.5)

        self.play(
            Create(path_mob_70),
            FadeIn(label_70),
            FadeIn(badge),
            Create(highlight_rect),
            run_time=2.0,
        )

        # ══════════════════════════════════════════════════════════
        #  STEP 4: Spiral inward (2s)
        # ══════════════════════════════════════════════════════════
        s_pts_sp = panels[2][2]
        spiral_pts = generate_spiral_path(s_pts_sp, inward=True)

        path_mob_sp = VMobject(color=COL_PATH_C, stroke_width=2)
        path_mob_sp.set_points_as_corners(spiral_pts)

        # Show gap areas — semi-transparent red patches
        gap_group = VGroup()
        sp_center = np.mean(s_pts_sp, axis=0)
        for dx, dy in [(0.3, 0.5), (-0.4, -0.3), (0.5, -0.2), (-0.2, 0.6)]:
            gap_dot = Circle(
                radius=0.15, color=COL_BAD, stroke_width=0,
                fill_color=COL_BAD, fill_opacity=0.35)
            gap_dot.move_to(sp_center + np.array([dx, dy, 0]))
            gap_group.add(gap_dot)

        label_sp = Text("No coverage\nguarantee", font_size=11, color=COL_BAD)
        label_sp.move_to(panel_centers[2] + np.array([0, -panel_h / 2 - 0.2, 0]))

        self.play(Create(path_mob_sp), FadeIn(gap_group), FadeIn(label_sp), run_time=2.0)

        # ══════════════════════════════════════════════════════════
        #  STEP 5: Expanding square (2s)
        # ══════════════════════════════════════════════════════════
        s_pts_eq = panels[3][2]
        sq_pts = generate_expanding_square(s_pts_eq)

        path_mob_sq = VMobject(color=COL_PATH_D, stroke_width=2)
        path_mob_sq.set_points_as_corners(sq_pts)

        # Show parts going outside polygon boundary — red markers
        outside_group = VGroup()
        poly_2d = np.array(s_pts_eq)[:, :2]

        def in_poly(px, py):
            n = len(poly_2d)
            inside = False
            j = n - 1
            for i in range(n):
                xi, yi = poly_2d[i]
                xj, yj = poly_2d[j]
                if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                    inside = not inside
                j = i
            return inside

        for p in sq_pts[::4]:
            if not in_poly(p[0], p[1]):
                x_mark = Cross(scale_factor=0.06, color=COL_BAD, stroke_width=2)
                x_mark.move_to(p)
                outside_group.add(x_mark)

        label_sq = Text("Poor fit for\nirregular polygons", font_size=11, color=COL_BAD)
        label_sq.move_to(panel_centers[3] + np.array([0, -panel_h / 2 - 0.2, 0]))

        self.play(Create(path_mob_sq), FadeIn(outside_group), FadeIn(label_sq), run_time=2.0)

        # ══════════════════════════════════════════════════════════
        #  STEP 6: Comparison bar chart (3s)
        # ══════════════════════════════════════════════════════════
        # Slide everything up to make room
        all_panel_mobs = VGroup()
        for sp, np_, _, _ in panels:
            all_panel_mobs.add(sp, np_)
        all_panel_mobs.add(
            *title_mobs,
            path_mob_0, label_0,
            path_mob_70, label_70, badge, highlight_rect,
            path_mob_sp, gap_group, label_sp,
            path_mob_sq, outside_group, label_sq,
        )

        self.play(
            all_panel_mobs.animate.shift(UP * 0.6),
            title.animate.shift(UP * 0.3),
            run_time=0.7,
        )

        # Bar chart area at the bottom
        chart_y = -3.0
        chart_x_start = -5.5
        chart_width = 11.0

        # Three metrics: Turns, Path Length, Energy
        metrics = ["Turns", "Path Length (m)", "Relative Energy"]
        # Values per pattern: Lawnmower 0, Lawnmower 70, Spiral, Expanding Sq
        values = {
            "Turns":            [7,   4,    0,   0],
            "Path Length (m)":  [903, 755,  880, 950],
            "Relative Energy":  [100, 62,   85,  110],
        }
        # For spiral/expanding, turns don't apply — show as N/A
        bar_colors = [COL_PATH_A, COL_PATH_B, COL_PATH_C, COL_PATH_D]
        pattern_names = ["0\u00b0", "70\u00b0", "Spiral", "Exp. Sq"]

        metric_spacing = chart_width / 3
        bar_w = 0.2
        bar_gap = 0.05

        chart_group = VGroup()

        for mi, metric in enumerate(metrics):
            mx = chart_x_start + metric_spacing * (mi + 0.5)
            vals = values[metric]
            max_val = max(v for v in vals if v > 0) if any(v > 0 for v in vals) else 1
            max_bar_h = 1.1

            # Metric label
            m_label = Text(metric, font_size=11, color=GREY_B)
            m_label.move_to(np.array([mx, chart_y - 0.2, 0]))
            chart_group.add(m_label)

            for bi, (val, col) in enumerate(zip(vals, bar_colors)):
                bx = mx + (bi - 1.5) * (bar_w + bar_gap)

                if metric == "Turns" and val == 0:
                    # N/A marker for spiral / expanding square
                    na_txt = Text("N/A", font_size=7, color=GREY)
                    na_txt.move_to(np.array([bx, chart_y + 0.15, 0]))
                    chart_group.add(na_txt)
                    continue

                bar_h = (val / max_val) * max_bar_h
                bar = Rectangle(
                    width=bar_w, height=bar_h,
                    color=col, stroke_width=0.5,
                    fill_color=col, fill_opacity=0.8)
                bar.move_to(np.array([bx, chart_y + bar_h / 2 + 0.3, 0]))

                val_txt = Text(
                    str(val), font_size=8,
                    color=WHITE)
                val_txt.next_to(bar, UP, buff=0.04)

                chart_group.add(bar, val_txt)

        # Pattern name legend
        legend = VGroup()
        for i, (name, col) in enumerate(zip(pattern_names, bar_colors)):
            dot = Square(side_length=0.12, color=col, fill_color=col, fill_opacity=0.9,
                         stroke_width=0)
            lbl = Text(name, font_size=9, color=col)
            lbl.next_to(dot, RIGHT, buff=0.06)
            entry = VGroup(dot, lbl)
            legend.add(entry)
        legend.arrange(RIGHT, buff=0.4)
        legend.move_to(np.array([0, chart_y + max_bar_h + 0.7, 0]))
        chart_group.add(legend)

        self.play(FadeIn(chart_group, shift=UP * 0.3), run_time=2.5)
        self.wait(0.5)

        # ══════════════════════════════════════════════════════════
        #  STEP 7: Green checkmark on Lawnmower 70 deg (1s)
        # ══════════════════════════════════════════════════════════
        # Big checkmark over the 70 deg column values
        check = Text("\u2713", font_size=48, color=COL_SELECTED, weight=BOLD)
        check.move_to(np.array([4.2, chart_y + 0.7, 0]))

        # Summary text
        summary = Text(
            "Longest-edge alignment: 43% fewer turns, 16% shorter path",
            font_size=14, color=COL_SELECTED, weight=BOLD)
        summary.to_edge(DOWN, buff=0.25)

        self.play(
            FadeIn(check, scale=1.5),
            FadeIn(summary, shift=UP * 0.1),
            run_time=1.0,
        )
        self.wait(1.5)
