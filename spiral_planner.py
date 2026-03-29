"""Standalone perimeter spiral planner — works on any GPS polygon.

Adapted from Zian's perimeter_planner.py algorithm:
progressively insets the polygon, handles edge degeneration,
CCW traversal from nearest vertex to drone entry point.

Usage:
    from spiral_planner import generate_spiral
    wps = generate_spiral(polygon_gps, strip_spacing_m, drone_gps, edge_margin_m)
"""
import math


def _offset_line(poly_m, edge_idx, offset):
    """Inset line for edge of a CCW polygon shifted inward by offset metres."""
    n = len(poly_m)
    ax, ay = poly_m[edge_idx]
    bx, by = poly_m[(edge_idx + 1) % n]
    ex, ey = bx - ax, by - ay
    length = math.hypot(ex, ey)
    if length < 1e-12:
        return (ax, ay), (1.0, 0.0)
    ex, ey = ex / length, ey / length
    nx, ny = -ey, ex  # inward normal (CCW)
    return (ax + nx * offset, ay + ny * offset), (ex, ey)


def _line_intersection(p1, d1, p2, d2):
    """Intersect lines L1 = p1+t*d1 and L2 = p2+s*d2."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < 1e-12:
        return None
    t = (dx * d2[1] - dy * d2[0]) / cross
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def _inset_polygon(poly_m, offset):
    """Full inset of poly_m by offset metres.
    Returns list of vertices or None if collapsed."""
    n = len(poly_m)
    if n < 3:
        return None
    lines = [_offset_line(poly_m, i, offset) for i in range(n)]
    verts = []
    for i in range(n):
        pt = _line_intersection(
            lines[(i - 1) % n][0], lines[(i - 1) % n][1],
            lines[i][0], lines[i][1])
        if pt is None:
            return None
        verts.append(pt)
    area2 = sum(verts[i][0] * verts[(i + 1) % n][1] -
                verts[(i + 1) % n][0] * verts[i][1] for i in range(n))
    return verts if area2 > 0 else None


def _edge_length_at_offset(poly_m, edge_idx, offset):
    """Return the length of edge edge_idx when polygon is inset by offset."""
    n = len(poly_m)
    line_prev = _offset_line(poly_m, (edge_idx - 1) % n, offset)
    line_cur = _offset_line(poly_m, edge_idx, offset)
    line_next = _offset_line(poly_m, (edge_idx + 1) % n, offset)
    p_start = _line_intersection(line_prev[0], line_prev[1],
                                  line_cur[0], line_cur[1])
    p_end = _line_intersection(line_cur[0], line_cur[1],
                                line_next[0], line_next[1])
    if p_start is None or p_end is None:
        return 0.0
    return math.hypot(p_end[0] - p_start[0], p_end[1] - p_start[1])


def _segments_cross(a1, a2, b1, b2, tol=1e-6):
    """True if segment a1->a2 properly crosses b1->b2."""
    def cross2(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    d1 = cross2(b1, b2, a1)
    d2 = cross2(b1, b2, a2)
    d3 = cross2(a1, a2, b1)
    d4 = cross2(a1, a2, b2)
    if ((d1 > tol and d2 < -tol) or (d1 < -tol and d2 > tol)) and \
       ((d3 > tol and d4 < -tol) or (d3 < -tol and d4 > tol)):
        return True
    return False


def generate_spiral(search_poly_gps, strip_spacing_m, drone_gps=None,
                    edge_margin_m=0.0):
    """Generate perimeter spiral waypoints for any GPS polygon.

    Args:
        search_poly_gps: list of (lat, lon) polygon vertices
        strip_spacing_m: distance between concentric rings (metres)
        drone_gps: (lat, lon) entry point, or None (uses first vertex)
        edge_margin_m: extra inset from polygon edge before first ring

    Returns:
        list of (lat, lon) waypoints
    """
    if len(search_poly_gps) < 3 or strip_spacing_m <= 0:
        return []

    ref_lat = sum(p[0] for p in search_poly_gps) / len(search_poly_gps)
    ref_lon = sum(p[1] for p in search_poly_gps) / len(search_poly_gps)
    cos_lat = math.cos(math.radians(ref_lat))

    def to_m(lat, lon):
        return ((lon - ref_lon) * 111320 * cos_lat,
                (lat - ref_lat) * 111320)

    def to_gps(x, y):
        return (y / 111320 + ref_lat,
                x / (111320 * cos_lat) + ref_lon)

    poly_m = [to_m(lat, lon) for lat, lon in search_poly_gps]

    # Ensure CCW winding
    area2 = sum(poly_m[i][0] * poly_m[(i + 1) % len(poly_m)][1] -
                poly_m[(i + 1) % len(poly_m)][0] * poly_m[i][1]
                for i in range(len(poly_m)))
    if area2 < 0:
        poly_m = poly_m[::-1]

    half_swath = strip_spacing_m / 2.0
    swath = strip_spacing_m

    cx_m = sum(p[0] for p in poly_m) / len(poly_m)
    cy_m = sum(p[1] for p in poly_m) / len(poly_m)
    max_poly_r = max(math.hypot(p[0] - cx_m, p[1] - cy_m) for p in poly_m)

    drone_m = to_m(drone_gps[0], drone_gps[1]) if drone_gps else poly_m[0]

    orig_poly = list(poly_m)
    all_lap_points = []
    survey_segs = []

    k = 0
    while k < 100:
        offset = edge_margin_m + half_swath + k * swath

        inset = _inset_polygon(orig_poly, offset)
        if inset is None:
            break

        if any(math.hypot(v[0] - cx_m, v[1] - cy_m) > max_poly_r * 1.5
               for v in inset):
            break

        # Edge degeneration
        n = len(orig_poly)
        surviving = []
        for i in range(n):
            if _edge_length_at_offset(orig_poly, i, offset) > 0.01:
                surviving.append(i)

        if len(surviving) < 3:
            break

        if len(surviving) < n:
            surviving_verts = []
            for v in range(n):
                if (v - 1) % n in surviving and v in surviving:
                    surviving_verts.append(v)
            if len(surviving_verts) < 3:
                break
            reduced = [orig_poly[v] for v in surviving_verts]
            inset = _inset_polygon(reduced, offset)
            if inset is None:
                break
            orig_poly = reduced

        # Rotate to start from nearest vertex
        ref_pt = all_lap_points[-1][-1] if all_lap_points else drone_m
        best_j = min(range(len(inset)),
                     key=lambda j: (inset[j][0] - ref_pt[0])**2 +
                                   (inset[j][1] - ref_pt[1])**2)
        lap_pts = inset[best_j:] + inset[:best_j]

        # Crossing check
        crossing = False
        new_segs = []
        for i in range(len(lap_pts) - 1):
            seg = (lap_pts[i], lap_pts[i + 1])
            for prev_seg in survey_segs:
                if _segments_cross(seg[0], seg[1], prev_seg[0], prev_seg[1]):
                    crossing = True
                    break
            if crossing:
                break
            new_segs.append(seg)

        if crossing:
            break

        survey_segs.extend(new_segs)
        all_lap_points.append(lap_pts)
        k += 1

    # Flatten
    waypoints_m = []
    for lap_pts in all_lap_points:
        for pt in lap_pts:
            if waypoints_m and math.hypot(pt[0] - waypoints_m[-1][0],
                                           pt[1] - waypoints_m[-1][1]) < 0.01:
                continue
            waypoints_m.append(pt)

    if waypoints_m:
        waypoints_m.append((cx_m, cy_m))

    return [to_gps(x, y) for x, y in waypoints_m]
