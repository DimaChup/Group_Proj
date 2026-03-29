"""
NFZ Protection System Animation — Real Fenswood Farm Geometry.

Uses ACTUAL polygon coordinates from config.py (AENGM0074.kml).
Shows: search area, SSSI no-fly zone, transit path, lawnmower pattern,
speed scalar field, repulsive vectors, and drone deflection with
velocity decomposition near the NFZ.

Run:
  python -m manim -pqh nfz_field_anim.py NFZFieldScene
  python -m manim -pql nfz_field_anim.py NFZFieldScene   # low quality (fast)
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

# Transit waypoints from flight_plans/transit.json (path around NFZ)
TRANSIT_GPS = [
    (51.421764800829834, -2.6701173714965023),  # T1
    (51.422474266363814, -2.667138823903503),    # T2
    (51.42410411961755, -2.6683086927255597),    # T3
]

# NFZ parameters (from config.py)
NFZ_HARD_M = 3.0
NFZ_SLOW_ZONE_M = 20.0
NFZ_SCALAR_ZERO_M = 2.0
NFZ_MAX_SPEED = 3.0       # m/s at outer edge of slow zone
NFZ_PUSH_SPEED = 5.0      # repulsive push speed
NFZ_INNER_RANGE_M = 3.0   # repulsion active within ~3m from boundary
SEARCH_SPEED = 10.0        # normal search speed m/s


# ── GPS to screen coordinate conversion (same as lawnmower_anim) ──

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


def gps_point_to_screen(lat, lon, ref_lat, ref_lon, scale, offset):
    """Convert single GPS point to screen coords."""
    ex, ny = gps_to_meters(lat, lon, ref_lat, ref_lon)
    return np.array([ex * scale + offset[0], ny * scale + offset[1], 0])


# ── Geometry helpers ──

def closest_point_on_polygon_edges(point, poly_pts):
    """Find closest point on polygon boundary and distance (screen units)."""
    min_dist = float('inf')
    closest = poly_pts[0].copy()
    n = len(poly_pts)
    for i in range(n):
        a = np.array(poly_pts[i][:2])
        b = np.array(poly_pts[(i + 1) % n][:2])
        ab = b - a
        ap = np.array(point[:2]) - a
        ab_sq = np.dot(ab, ab)
        if ab_sq < 1e-10:
            proj = a.copy()
        else:
            t = np.clip(np.dot(ap, ab) / ab_sq, 0, 1)
            proj = a + t * ab
        d = np.linalg.norm(np.array(point[:2]) - proj)
        if d < min_dist:
            min_dist = d
            closest = np.array([proj[0], proj[1], 0])
    return closest, min_dist


def point_in_polygon(px, py, poly_pts):
    """Ray casting test: is (px,py) inside polygon?"""
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


def line_polygon_intersections(p1, p2, poly_pts):
    """Find all intersections of line segment p1-p2 with polygon edges.
    Returns sorted list of t values where 0=p1, 1=p2."""
    ts = []
    n = len(poly_pts)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    for i in range(n):
        a = poly_pts[i]
        b = poly_pts[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        denom = dx * ey - dy * ex
        if abs(denom) < 1e-12:
            continue
        t = ((a[0] - p1[0]) * ey - (a[1] - p1[1]) * ex) / denom
        s = ((a[0] - p1[0]) * dy - (a[1] - p1[1]) * dx) / denom
        if -0.001 <= t <= 1.001 and -0.001 <= s <= 1.001:
            ts.append(np.clip(t, 0, 1))
    ts.sort()
    return ts


def clip_line_to_polygon(p1, p2, poly_pts):
    """Clip a line segment to the interior of a polygon.
    Returns list of (start, end) segments that lie inside."""
    ts = line_polygon_intersections(p1, p2, poly_pts)
    # Add endpoints if inside
    all_t = [0.0] + ts + [1.0]
    all_t = sorted(set(all_t))

    segments = []
    for i in range(len(all_t) - 1):
        t_mid = (all_t[i] + all_t[i + 1]) / 2.0
        mid = np.array([
            p1[0] + t_mid * (p2[0] - p1[0]),
            p1[1] + t_mid * (p2[1] - p1[1]),
        ])
        if point_in_polygon(mid[0], mid[1], poly_pts):
            s = np.array([
                p1[0] + all_t[i] * (p2[0] - p1[0]),
                p1[1] + all_t[i] * (p2[1] - p1[1]),
                0,
            ])
            e = np.array([
                p1[0] + all_t[i + 1] * (p2[0] - p1[0]),
                p1[1] + all_t[i + 1] * (p2[1] - p1[1]),
                0,
            ])
            if np.linalg.norm(e - s) > 0.01:
                segments.append((s, e))
    return segments


def inset_polygon(poly_pts, inset_screen):
    """Inset (shrink) a polygon by moving each vertex toward the centroid.
    inset_screen is in screen units.  Returns new list of 3-element arrays."""
    arr = np.array(poly_pts)
    c = arr.mean(axis=0)
    result = []
    for pt in arr:
        d = pt - c
        norm = np.linalg.norm(d[:2])
        if norm < 1e-6:
            result.append(pt.copy())
        else:
            # Move toward centroid by inset_screen
            shrink = max(0, norm - inset_screen) / norm
            result.append(c + d * shrink)
    return result


def generate_lawnmower_lines(search_pts_screen, angle_deg, num_lines, lane_inset_frac=1.0/3.0):
    """Generate lawnmower scan lines across the search polygon at a given angle.
    lane_inset_frac: fraction of lane spacing to inset from polygon edges (matches planning.py).
    Returns list of (start, end) point pairs CLIPPED to the inset polygon,
    with alternating direction so consecutive lines form a U-turn pattern."""
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

    # Lane spacing = total height / num_lines
    lane_spacing = (y_max - y_min) / num_lines
    # Inset from polygon edges by fraction of lane spacing (matches planning.py inset_px = strip_spacing // 3)
    inset = lane_spacing * lane_inset_frac

    # Inset the clipping polygon so scan lines don't touch edges
    inset_pts = inset_polygon(search_pts_screen, inset)

    ys = np.linspace(y_min + inset, y_max - inset, num_lines)

    lines = []
    for i, y in enumerate(ys):
        if i % 2 == 0:
            start_r = np.array([x_min - 0.5, y])
            end_r = np.array([x_max + 0.5, y])
        else:
            start_r = np.array([x_max + 0.5, y])
            end_r = np.array([x_min - 0.5, y])

        start_s = inv_rotate(start_r, center)
        end_s = inv_rotate(end_r, center)

        raw_start = np.array([start_s[0], start_s[1], 0])
        raw_end = np.array([end_s[0], end_s[1], 0])

        # Clip to inset polygon
        clipped = clip_line_to_polygon(raw_start, raw_end, inset_pts)
        for seg_s, seg_e in clipped:
            lines.append((seg_s, seg_e))

    return lines


def offset_polygon_screen(pts, dist_screen):
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
            result.append(pt + d / norm * dist_screen)
    return result


def speed_at_distance(dist_m):
    """Speed scalar: 0 at zero_m, linear to max at slow_zone_m."""
    if dist_m <= NFZ_SCALAR_ZERO_M:
        return 0.0
    if dist_m >= NFZ_SLOW_ZONE_M:
        return NFZ_MAX_SPEED
    return NFZ_MAX_SPEED * (dist_m - NFZ_SCALAR_ZERO_M) / (NFZ_SLOW_ZONE_M - NFZ_SCALAR_ZERO_M)


class NFZFieldScene(Scene):
    def construct(self):
        # ── Coordinate transform setup ──────────────────────
        all_lats = [p[0] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
        all_lons = [p[1] for p in FLIGHT_AREA_GPS + SEARCH_AREA_GPS + SSSI_GPS]
        ref_lat = np.mean(all_lats)
        ref_lon = np.mean(all_lons)

        # Find extent from flight area
        all_m = []
        for lat, lon in FLIGHT_AREA_GPS:
            all_m.append(gps_to_meters(lat, lon, ref_lat, ref_lon))
        xs = [p[0] for p in all_m]
        ys = [p[1] for p in all_m]
        extent = max(max(xs) - min(xs), max(ys) - min(ys))

        frame_size = 5.5
        scale = frame_size / extent
        offset = np.array([0.0, -0.3])

        # Meters-to-screen helper
        def m2s(meters):
            return meters * scale

        # Convert all polygons to screen coords
        search_pts = gps_poly_to_screen(SEARCH_AREA_GPS, ref_lat, ref_lon, scale, offset)
        sssi_pts = gps_poly_to_screen(SSSI_GPS, ref_lat, ref_lon, scale, offset)
        flight_pts = gps_poly_to_screen(FLIGHT_AREA_GPS, ref_lat, ref_lon, scale, offset)
        tol_screen = gps_point_to_screen(*TAKEOFF_GPS, ref_lat, ref_lon, scale, offset)

        sssi_center = np.mean(sssi_pts, axis=0)

        # ══════════════════════════════════════════════════════
        # 1. TITLE
        # ══════════════════════════════════════════════════════
        title = Text("NFZ Protection System", font_size=36, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.25)
        subtitle = Text("Fenswood Farm SSSI Geofence", font_size=18, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.1)

        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.6)
        self.play(FadeIn(subtitle), run_time=0.3)
        self.wait(0.5)

        # ══════════════════════════════════════════════════════
        # 2. DRAW SEARCH AREA + SSSI + TAKEOFF
        # ══════════════════════════════════════════════════════
        # Flight area (dashed blue boundary)
        flight_poly = Polygon(
            *flight_pts, color=BLUE, stroke_width=2, stroke_opacity=0.6,
            fill_opacity=0.0,
        )
        flight_poly = DashedVMobject(flight_poly, num_dashes=30)
        flight_label = Text("Flight Area", font_size=11, color=BLUE_B)
        flight_label.next_to(flight_poly, DOWN, buff=0.08)

        # Search area (green)
        search_poly = Polygon(
            *search_pts, color=GREEN, stroke_width=2,
            fill_color=GREEN, fill_opacity=0.1,
        )
        search_label = Text("Search Area", font_size=12, color=GREEN_B)
        search_center = np.mean(search_pts, axis=0)
        search_label.move_to(search_center + np.array([0, -0.3, 0]))

        # SSSI polygon (red filled with hatching)
        sssi_poly = Polygon(
            *sssi_pts, color=RED, stroke_width=3,
            fill_color=RED, fill_opacity=0.25,
        )
        # Diagonal hatching
        hatch = VGroup()
        sssi_arr = np.array(sssi_pts)
        xmin, xmax = sssi_arr[:, 0].min() - 0.1, sssi_arr[:, 0].max() + 0.1
        ymin, ymax = sssi_arr[:, 1].min() - 0.1, sssi_arr[:, 1].max() + 0.1
        for k in range(20):
            t = k / 19
            d = (xmin + ymin) + t * ((xmax + ymax) - (xmin + ymin))
            x1 = max(xmin, d - ymax)
            x2 = min(xmax, d - ymin)
            if x2 > x1:
                hatch.add(Line(
                    [x1, d - x1, 0], [x2, d - x2, 0],
                    color=RED, stroke_width=0.8, stroke_opacity=0.35,
                ))

        sssi_label = Text("SSSI No-Fly Zone", font_size=14, color=RED, weight=BOLD)
        sssi_label.move_to(sssi_center)

        # Takeoff point
        tol_star = Star(
            n=5, outer_radius=0.15, inner_radius=0.06,
            color=YELLOW, fill_color=YELLOW, fill_opacity=1.0,
        )
        tol_star.move_to(tol_screen)
        tol_label = Text("TOL", font_size=12, color=YELLOW, weight=BOLD)
        tol_label.next_to(tol_star, UP, buff=0.08)

        self.play(Create(flight_poly), FadeIn(flight_label), run_time=0.7)
        self.play(Create(search_poly), FadeIn(search_label), run_time=0.7)
        self.play(
            Create(sssi_poly), FadeIn(hatch, lag_ratio=0.03),
            run_time=0.7,
        )
        self.play(FadeIn(sssi_label), run_time=0.3)
        self.play(FadeIn(tol_star, scale=1.5), FadeIn(tol_label), run_time=0.4)
        self.wait(0.5)

        # Scale bar
        bar_start = np.array([-5.5, -3.5, 0])
        bar_20m = Line(bar_start, bar_start + RIGHT * m2s(20),
                       color=WHITE, stroke_width=2)
        bar_text = Text("20 m", font_size=10, color=WHITE)
        bar_text.next_to(bar_20m, DOWN, buff=0.05)
        self.play(Create(bar_20m), FadeIn(bar_text), run_time=0.3)

        # ══════════════════════════════════════════════════════
        # 3. TRANSIT PATH from TOL around NFZ to search area
        # ══════════════════════════════════════════════════════
        # Convert transit waypoints to screen coords
        transit_screen_pts = [
            gps_point_to_screen(lat, lon, ref_lat, ref_lon, scale, offset)
            for lat, lon in TRANSIT_GPS
        ]
        # Find first search waypoint (closest to last transit point)
        dists = [np.linalg.norm(np.array(sp) - transit_screen_pts[-1]) for sp in search_pts]
        first_search_idx = np.argmin(dists)
        first_search_pt = search_pts[first_search_idx]

        # Full transit path: TOL -> T1 -> T2 -> T3 -> first search waypoint
        transit_path_pts = [tol_screen] + transit_screen_pts + [first_search_pt]

        transit_lines = VGroup()
        transit_dots = VGroup()
        for i in range(len(transit_path_pts) - 1):
            seg = DashedLine(
                transit_path_pts[i], transit_path_pts[i + 1],
                color=YELLOW_A, stroke_width=2,
            )
            transit_lines.add(seg)
        for i, tpt in enumerate(transit_screen_pts):
            tdot = Dot(tpt, radius=0.05, color=YELLOW_A, fill_opacity=0.8)
            transit_dots.add(tdot)

        transit_label = Text("Transit (avoids NFZ)", font_size=10, color=YELLOW_A)
        transit_mid = (transit_screen_pts[0] + transit_screen_pts[1]) / 2
        transit_label.move_to(transit_mid + np.array([0.0, -0.2, 0]))

        self.play(
            LaggedStart(*[Create(l) for l in transit_lines], lag_ratio=0.3),
            FadeIn(transit_dots),
            run_time=0.8,
        )
        self.play(FadeIn(transit_label), run_time=0.3)
        self.wait(0.3)

        # ══════════════════════════════════════════════════════
        # 4. LAWNMOWER SEARCH PATTERN (clipped, inset, with U-turns)
        # ══════════════════════════════════════════════════════
        scan_angle = 70
        num_scan_lines = 7
        lawnmower = generate_lawnmower_lines(search_pts, scan_angle, num_scan_lines)

        pattern_group = VGroup()
        # Draw scan lines
        for start, end in lawnmower:
            line = Line(start, end, color=GREEN_A, stroke_width=1.5, stroke_opacity=0.6)
            pattern_group.add(line)

        # Draw U-turn connectors between consecutive scan lines
        uturn_group = VGroup()
        for i in range(len(lawnmower) - 1):
            _, end_cur = lawnmower[i]
            start_next, _ = lawnmower[i + 1]
            # Small arc connector
            connector = Line(
                end_cur, start_next,
                color=GREEN_A, stroke_width=1.2, stroke_opacity=0.4,
            )
            uturn_group.add(connector)

        self.play(
            LaggedStart(*[Create(l) for l in pattern_group], lag_ratio=0.12),
            run_time=1.5,
        )
        self.play(
            LaggedStart(*[Create(l) for l in uturn_group], lag_ratio=0.1),
            run_time=0.6,
        )
        self.wait(0.5)

        # ══════════════════════════════════════════════════════
        # 5. SPEED SCALAR FIELD around SSSI (20m gradient)
        # ══════════════════════════════════════════════════════
        self.play(FadeOut(title), FadeOut(subtitle), run_time=0.3)
        layer1_title = Text("Layer 1: Speed Scalar Field", font_size=22,
                            color=YELLOW, weight=BOLD)
        layer1_title.to_edge(UP, buff=0.2)
        self.play(FadeIn(layer1_title), run_time=0.4)

        # Gradient bands (concentric offset polygons)
        num_bands = 14
        gradient_bands = VGroup()
        for i in range(num_bands, 0, -1):
            outer_m = NFZ_SCALAR_ZERO_M + (NFZ_SLOW_ZONE_M - NFZ_SCALAR_ZERO_M) * (i / num_bands)
            inner_m = NFZ_SCALAR_ZERO_M + (NFZ_SLOW_ZONE_M - NFZ_SCALAR_ZERO_M) * ((i - 1) / num_bands)
            outer_pts = offset_polygon_screen(sssi_pts, m2s(outer_m))
            # Color: red close -> yellow mid -> green far
            frac = i / num_bands
            if frac > 0.5:
                color = interpolate_color(YELLOW, GREEN, (frac - 0.5) * 2)
            else:
                color = interpolate_color(RED, YELLOW, frac * 2)

            band = Polygon(
                *outer_pts, color=color, stroke_width=0,
                fill_color=color, fill_opacity=0.12,
            )
            gradient_bands.add(band)

        # Dead zone (0-2m, solid red)
        dead_pts = offset_polygon_screen(sssi_pts, m2s(NFZ_SCALAR_ZERO_M))
        dead_zone = Polygon(
            *dead_pts, color=RED, stroke_width=0,
            fill_color=RED, fill_opacity=0.2,
        )
        gradient_bands.add(dead_zone)

        self.play(FadeIn(gradient_bands, lag_ratio=0.03), run_time=1.5)

        # Speed labels along a reference direction
        ref_dir = np.array([1.0, 0.5, 0])
        ref_dir = ref_dir / np.linalg.norm(ref_dir[:2])
        cp_ref, _ = closest_point_on_polygon_edges(sssi_center + ref_dir * 5, sssi_pts)

        speed_labels = VGroup()
        for dist_m, txt, col in [
            (20, "3.0 m/s", GREEN),
            (11, "1.5 m/s", YELLOW),
            (2, "0 m/s", RED),
        ]:
            pos = cp_ref + ref_dir * m2s(dist_m)
            lbl = Text(txt, font_size=11, color=col, weight=BOLD)
            lbl.move_to(pos)
            bg = BackgroundRectangle(lbl, color=BLACK, fill_opacity=0.7, buff=0.04)
            speed_labels.add(VGroup(bg, lbl))

        self.play(FadeIn(speed_labels, lag_ratio=0.15), run_time=0.7)
        self.wait(0.8)

        # ══════════════════════════════════════════════════════
        # 6. REPULSIVE VECTORS at 3m from SSSI boundary
        # ══════════════════════════════════════════════════════
        layer2_title = Text("Layer 2: Repulsive Vector Field (3 m)", font_size=22,
                            color="#FF6B6B", weight=BOLD)
        layer2_title.to_edge(UP, buff=0.2)
        self.play(FadeOut(layer1_title), FadeIn(layer2_title), run_time=0.4)

        repulsive_arrows = VGroup()
        n_verts = len(sssi_pts)
        arrows_per_edge = 3

        for i in range(n_verts):
            a = np.array(sssi_pts[i])
            b = np.array(sssi_pts[(i + 1) % n_verts])
            edge = b - a
            edge_len = np.linalg.norm(edge[:2])
            if edge_len < 0.01:
                continue

            # Outward normal
            normal = np.array([-edge[1], edge[0], 0])
            normal = normal / np.linalg.norm(normal[:2])
            mid = (a + b) / 2
            if np.dot((mid + normal * 0.1 - sssi_center)[:2], normal[:2]) < 0:
                normal = -normal

            for j in range(arrows_per_edge):
                t = (j + 1) / (arrows_per_edge + 1)
                base = a + t * edge
                arrow_start = base + normal * m2s(1.5)
                arrow_end = arrow_start + normal * m2s(5.0)

                arrow = Arrow(
                    arrow_start, arrow_end,
                    color=RED, stroke_width=3,
                    max_tip_length_to_length_ratio=0.3,
                    buff=0,
                )
                repulsive_arrows.add(arrow)

        self.play(
            LaggedStart(*[GrowArrow(a) for a in repulsive_arrows], lag_ratio=0.03),
            run_time=1.2,
        )

        push_label = Text("5 m/s repulsive push", font_size=12, color=RED, weight=BOLD)
        push_label.to_edge(RIGHT, buff=0.3).shift(UP * 2.0)
        push_bg = BackgroundRectangle(push_label, color=BLACK, fill_opacity=0.7, buff=0.05)
        self.play(FadeIn(push_bg), FadeIn(push_label), run_time=0.3)

        # Pulse
        self.play(
            repulsive_arrows.animate.set_opacity(0.3),
            run_time=0.25, rate_func=there_and_back,
        )
        self.play(
            repulsive_arrows.animate.set_opacity(1.0),
            run_time=0.25, rate_func=there_and_back,
        )
        self.wait(0.5)

        # ══════════════════════════════════════════════════════
        # 7. HARD BOUNDARY (3m)
        # ══════════════════════════════════════════════════════
        layer3_title = Text("Layer 3: Hard Boundary (3 m)", font_size=22,
                            color="#FF4444", weight=BOLD)
        layer3_title.to_edge(UP, buff=0.2)
        self.play(FadeOut(layer2_title), FadeIn(layer3_title), run_time=0.4)

        hard_pts = offset_polygon_screen(sssi_pts, m2s(NFZ_HARD_M))
        hard_boundary = Polygon(
            *hard_pts, color="#FF0000", stroke_width=4, fill_opacity=0.0,
        )

        am_label = Text("AUTO -> MANUAL", font_size=13, color="#FF4444", weight=BOLD)
        hb_top = max(hard_pts, key=lambda p: p[1])
        am_label.move_to(np.array([hb_top[0], hb_top[1] + 0.25, 0]))
        am_bg = BackgroundRectangle(am_label, color=BLACK, fill_opacity=0.7, buff=0.05)

        self.play(Create(hard_boundary), run_time=0.6)
        self.play(FadeIn(am_bg), FadeIn(am_label), run_time=0.3)
        self.wait(0.5)

        # ══════════════════════════════════════════════════════
        # 8. DRONE FLYING SEARCH PATTERN NEAR SSSI
        # ══════════════════════════════════════════════════════
        all_title = Text("Drone Deflection Near NFZ", font_size=22,
                         color=WHITE, weight=BOLD)
        all_title.to_edge(UP, buff=0.2)
        self.play(
            FadeOut(layer3_title), FadeOut(am_bg), FadeOut(am_label),
            FadeIn(all_title),
            run_time=0.3,
        )

        # Find a scan line that passes NEAR the SSSI (closest approach)
        best_line_idx = 0
        min_approach = float('inf')
        for li, (ls, le) in enumerate(lawnmower):
            # Sample points along line
            for t in np.linspace(0, 1, 20):
                pt = ls + t * (le - ls)
                _, d = closest_point_on_polygon_edges(pt, sssi_pts)
                if d < min_approach:
                    min_approach = d
                    best_line_idx = li

        # Build a path: from TOL, transit, then fly scan lines up to and including
        # the line near SSSI. We pick the near-SSSI line and one before+after.
        near_idx = max(0, best_line_idx - 1)
        path_lines = lawnmower[near_idx:min(near_idx + 3, len(lawnmower))]

        # Drone starts at TOL (takeoff location)
        drone_start = tol_screen.copy()
        drone = Dot(drone_start, radius=0.1, color=BLUE, fill_opacity=1.0)
        drone_ring = Circle(radius=0.16, color=BLUE_B, stroke_width=2,
                            stroke_opacity=0.5, fill_opacity=0.0)
        drone_ring.add_updater(lambda m: m.move_to(drone.get_center()))

        drone_trail = TracedPath(
            drone.get_center, stroke_color=BLUE, stroke_width=2.5, stroke_opacity=0.7,
        )

        # Speed indicator
        speed_bar_frame = Rectangle(width=1.6, height=0.18, color=GREY_B,
                                     stroke_width=1.5, fill_color=GREY_D, fill_opacity=0.8)
        speed_bar_frame.to_corner(DR, buff=0.4).shift(UP * 0.3)
        speed_fill = Rectangle(width=1.6, height=0.18, color=GREEN,
                                fill_color=GREEN, fill_opacity=0.9, stroke_width=0)
        speed_fill.move_to(speed_bar_frame).align_to(speed_bar_frame, LEFT)
        speed_txt = Text("10.0 m/s", font_size=12, color=WHITE)
        speed_txt.next_to(speed_bar_frame, UP, buff=0.05)
        speed_lbl = Text("Speed", font_size=9, color=GREY_B)
        speed_lbl.next_to(speed_bar_frame, DOWN, buff=0.05)

        self.add(drone_trail, drone, drone_ring)
        self.play(
            FadeIn(drone, scale=2),
            FadeIn(speed_bar_frame), FadeIn(speed_fill),
            FadeIn(speed_txt), FadeIn(speed_lbl),
            run_time=0.4,
        )

        # ── Fly transit path: TOL -> T1 -> T2 -> T3 -> first scan line ──
        for tpt in transit_path_pts[1:]:  # skip TOL (already there)
            self.play(drone.animate.move_to(tpt), run_time=0.5, rate_func=linear)

        # Move to start of first scan line
        first_scan_start = path_lines[0][0]
        if np.linalg.norm(drone.get_center() - first_scan_start) > 0.05:
            self.play(drone.animate.move_to(first_scan_start), run_time=0.4, rate_func=linear)

        # ── Fly each scan line with physics (scalar + repulsion) ──
        # Velocity arrow on drone
        vel_arrow = Arrow(ORIGIN, RIGHT * 0.5, color=BLUE, stroke_width=3, buff=0)
        vel_arrow.move_to(drone.get_center())

        dt = 0.04
        repel_active_shown = False
        zoom_done = False

        for line_i, (line_start, line_end) in enumerate(path_lines):
            # Move to line start if not already there
            current_pos = drone.get_center().copy()
            if np.linalg.norm(current_pos - line_start) > 0.05:
                self.play(drone.animate.move_to(line_start), run_time=0.4)

            # Simulate flight along this line with physics
            direction = line_end - line_start
            total_dist = np.linalg.norm(direction)
            if total_dist < 0.01:
                continue
            dir_hat = direction / total_dist

            # Determine if this line gets close to SSSI
            close_approach = False
            for t in np.linspace(0, 1, 30):
                pt = line_start + t * (line_end - line_start)
                _, d = closest_point_on_polygon_edges(pt, sssi_pts)
                dist_m = d / scale
                if dist_m < NFZ_SLOW_ZONE_M:
                    close_approach = True
                    break

            pos = line_start.copy()
            vel = dir_hat * (SEARCH_SPEED * scale)  # screen units/s

            num_steps = int(total_dist / (np.linalg.norm(vel) * dt)) + 1
            num_steps = min(num_steps, 200)
            path_sim = [pos.copy()]

            for step in range(num_steps):
                cp_pt, dist_s = closest_point_on_polygon_edges(pos, sssi_pts)
                dist_m = dist_s / scale  # convert screen distance to meters

                # Speed scalar field
                if dist_m < NFZ_SLOW_ZONE_M:
                    max_spd_m = speed_at_distance(dist_m)
                    max_spd_s = max_spd_m * scale
                    spd = np.linalg.norm(vel[:2])
                    if spd > max_spd_s and max_spd_s > 0:
                        vel[:2] = vel[:2] / spd * max_spd_s

                # Repulsive force within 3m
                if dist_m < NFZ_INNER_RANGE_M + 2:
                    repel_dir = pos - cp_pt
                    rn = np.linalg.norm(repel_dir[:2])
                    if rn > 1e-6:
                        repel_dir = repel_dir / rn
                        strength = max(0, 1.0 - dist_m / (NFZ_INNER_RANGE_M + 2))
                        vel[:2] += repel_dir[:2] * strength * NFZ_PUSH_SPEED * scale * dt

                pos = pos + vel * dt
                pos[2] = 0

                # Don't wander too far from the line
                progress = np.dot((pos - line_start)[:2], dir_hat[:2])
                if progress >= total_dist:
                    pos = line_end.copy()
                    path_sim.append(pos.copy())
                    break
                path_sim.append(pos.copy())

            # Animate in chunks
            chunk_size = 6
            n_chunks = max(1, (len(path_sim) - 1 + chunk_size - 1) // chunk_size)
            anim_time = 2.5 if close_approach else 1.2

            for c in range(n_chunks):
                idx = min((c + 1) * chunk_size, len(path_sim) - 1)
                target = path_sim[idx]

                cp_pt, dist_s = closest_point_on_polygon_edges(target, sssi_pts)
                dist_m = dist_s / scale

                # Update speed bar
                if dist_m < NFZ_SLOW_ZONE_M:
                    spd_m = speed_at_distance(dist_m)
                else:
                    spd_m = SEARCH_SPEED
                frac = min(spd_m / SEARCH_SPEED, 1.0)
                bar_col = interpolate_color(RED, GREEN, frac)
                new_fill = Rectangle(
                    width=max(1.6 * frac, 0.02), height=0.18,
                    color=bar_col, fill_color=bar_col, fill_opacity=0.9, stroke_width=0,
                )
                new_fill.move_to(speed_bar_frame).align_to(speed_bar_frame, LEFT)

                new_txt = Text(f"{spd_m:.1f} m/s", font_size=12, color=WHITE)
                new_txt.next_to(speed_bar_frame, UP, buff=0.05)

                anims = [
                    drone.animate.move_to(target),
                    Transform(speed_fill, new_fill),
                    Transform(speed_txt, new_txt),
                ]

                # Show velocity decomposition when entering scalar field
                if close_approach and dist_m < NFZ_SLOW_ZONE_M and not zoom_done:
                    zoom_done = True
                    # Show velocity arrow
                    vel_dir = target - path_sim[max(0, idx - chunk_size)]
                    vn = np.linalg.norm(vel_dir[:2])
                    if vn > 0.01:
                        vel_dir_n = vel_dir / vn

                        # Velocity arrow (blue)
                        vel_end = target + vel_dir_n * 0.6
                        v_arrow = Arrow(target, vel_end, color=BLUE,
                                        stroke_width=3, buff=0, max_tip_length_to_length_ratio=0.25)

                        # Component toward NFZ (red) and tangent (green)
                        to_nfz = cp_pt - target
                        tn = np.linalg.norm(to_nfz[:2])
                        if tn > 0.01:
                            to_nfz_hat = to_nfz / tn
                            # Project velocity onto NFZ direction
                            v_nfz_comp = np.dot(vel_dir_n[:2], to_nfz_hat[:2])
                            v_tang_comp = vel_dir_n - to_nfz_hat * v_nfz_comp

                            nfz_arrow_end = target + to_nfz_hat * v_nfz_comp * 0.6
                            tang_arrow_end = target + v_tang_comp * 0.6

                            a_nfz = Arrow(target, nfz_arrow_end, color=RED,
                                          stroke_width=3, buff=0,
                                          max_tip_length_to_length_ratio=0.3)
                            a_tang = Arrow(target, tang_arrow_end, color=GREEN,
                                           stroke_width=3, buff=0,
                                           max_tip_length_to_length_ratio=0.3)

                            # Labels
                            nfz_comp_label = Text("v_NFZ (reduced)", font_size=10, color=RED)
                            nfz_comp_label.next_to(a_nfz, DOWN, buff=0.05)
                            tang_label = Text("v_tangent (kept)", font_size=10, color=GREEN)
                            tang_label.next_to(a_tang, UP, buff=0.05)
                            vel_label = Text("v_total", font_size=10, color=BLUE)
                            vel_label.next_to(v_arrow, UP, buff=0.05)

                            decomp_group = VGroup(v_arrow, a_nfz, a_tang,
                                                   nfz_comp_label, tang_label, vel_label)

                            # First move drone, then show decomposition
                            self.play(*anims, run_time=anim_time / n_chunks, rate_func=linear)
                            self.play(
                                FadeIn(v_arrow), FadeIn(vel_label),
                                run_time=0.4,
                            )
                            self.play(
                                FadeIn(a_nfz), FadeIn(nfz_comp_label),
                                FadeIn(a_tang), FadeIn(tang_label),
                                run_time=0.5,
                            )

                            # Explain
                            explain = Text(
                                "NFZ-facing component reduced by scalar field",
                                font_size=13, color=YELLOW,
                            )
                            explain.to_edge(DOWN, buff=0.3)
                            ex_bg = BackgroundRectangle(explain, color=BLACK,
                                                         fill_opacity=0.8, buff=0.08)
                            self.play(FadeIn(ex_bg), FadeIn(explain), run_time=0.4)
                            self.wait(1.5)

                            self.play(
                                FadeOut(decomp_group),
                                FadeOut(ex_bg), FadeOut(explain),
                                run_time=0.4,
                            )
                            continue  # skip normal animation for this chunk

                # Show repulsion activation near boundary
                if close_approach and dist_m < NFZ_INNER_RANGE_M + 2 and not repel_active_shown:
                    repel_active_shown = True
                    repel_note = Text(
                        "Repulsive push: 5 m/s away from NFZ",
                        font_size=13, color=RED, weight=BOLD,
                    )
                    repel_note.to_edge(DOWN, buff=0.3)
                    rn_bg = BackgroundRectangle(repel_note, color=BLACK,
                                                 fill_opacity=0.8, buff=0.08)
                    anims.extend([FadeIn(rn_bg), FadeIn(repel_note)])

                    self.play(*anims, run_time=anim_time / n_chunks, rate_func=linear)
                    self.wait(1.0)
                    self.play(FadeOut(rn_bg), FadeOut(repel_note), run_time=0.3)
                    continue

                self.play(*anims, run_time=anim_time / n_chunks, rate_func=linear)

        self.wait(0.5)

        # ══════════════════════════════════════════════════════
        # 9. SPEED PROFILE GRAPH (inset)
        # ══════════════════════════════════════════════════════
        self.play(FadeOut(all_title), run_time=0.2)
        graph_title = Text("Speed Profile vs Distance", font_size=20,
                           color=WHITE, weight=BOLD)
        graph_title.to_edge(UP, buff=0.2)
        self.play(FadeIn(graph_title), run_time=0.3)

        axes = Axes(
            x_range=[0, 22, 5],
            y_range=[0, 3.5, 1],
            x_length=3.5, y_length=2.0,
            axis_config={"color": GREY_B, "stroke_width": 2,
                         "include_numbers": True, "font_size": 14},
            tips=False,
        )
        axes.to_corner(DR, buff=0.4)

        xl = Text("Distance from SSSI (m)", font_size=10, color=GREY_B)
        xl.next_to(axes, DOWN, buff=0.08)
        yl = Text("Speed (m/s)", font_size=10, color=GREY_B)
        yl.next_to(axes, LEFT, buff=0.08).rotate(PI / 2)

        graph = axes.plot(speed_at_distance, x_range=[0, 22, 0.1],
                          color=YELLOW, stroke_width=3)

        danger_shade = axes.get_area(graph, x_range=[0, 2], color=RED, opacity=0.3)
        slow_shade = axes.get_area(graph, x_range=[2, 20], color=YELLOW, opacity=0.12)

        zero_dash = DashedLine(axes.c2p(2, 0), axes.c2p(2, 3.5),
                               color=RED, stroke_width=1.5)
        zone_dash = DashedLine(axes.c2p(20, 0), axes.c2p(20, 3.5),
                               color=GREEN, stroke_width=1.5)

        zl = Text("2m", font_size=8, color=RED)
        zl.next_to(zero_dash, UP, buff=0.03)
        zl2 = Text("20m", font_size=8, color=GREEN)
        zl2.next_to(zone_dash, UP, buff=0.03)

        gbg = BackgroundRectangle(VGroup(axes, xl, yl), color=BLACK,
                                   fill_opacity=0.8, buff=0.12)

        self.play(FadeIn(gbg), Create(axes), FadeIn(xl), FadeIn(yl), run_time=0.5)
        self.play(
            Create(graph),
            FadeIn(danger_shade), FadeIn(slow_shade),
            Create(zero_dash), Create(zone_dash),
            FadeIn(zl), FadeIn(zl2),
            run_time=0.8,
        )
        self.wait(0.8)

        # ══════════════════════════════════════════════════════
        # 10. STATS BAR
        # ══════════════════════════════════════════════════════
        stats = VGroup(
            Text("Layers: 3", font_size=13, color=WHITE),
            Text("|", font_size=13, color=GREY),
            Text("Scalar: 20m ramp", font_size=13, color=YELLOW),
            Text("|", font_size=13, color=GREY),
            Text("Repulsion: 5 m/s", font_size=13, color=RED),
            Text("|", font_size=13, color=GREY),
            Text("Hard: 3m cutoff", font_size=13, color="#FF4444"),
        ).arrange(RIGHT, buff=0.1)
        stats.to_edge(DOWN, buff=0.15)
        stats_bg = BackgroundRectangle(stats, color=BLACK, fill_opacity=0.8, buff=0.08)

        self.play(FadeIn(stats_bg), FadeIn(stats), run_time=0.5)
        self.wait(2.0)

        # Final fade
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.0)
