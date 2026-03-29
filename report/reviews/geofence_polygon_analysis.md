# Geofence Polygon Analysis

Investigation of `geofence.py` distance/direction computation, polygon shape, and
edge-case behaviour near concave vertices.

---

## 1. What is `sssi_polygon_gps`? How is it stored?

Stored as a list of `(lat, lon)` tuples in `config.py`:

```python
SSSI_GPS = [
    (51.42353586816967, -2.671451754138619),   # V0
    (51.42215640321154, -2.669768242108598),   # V1
    (51.42267105383615, -2.667705438815299),   # V2
    (51.42335592245168, -2.668164601092489),   # V3
    (51.42286082606338, -2.670043418345824),   # V4
    (51.42326667015552, -2.670965419051837),   # V5
    (51.42356862274763, -2.671324297543731),   # V6
]
```

Seven vertices. `NFZGeofence.__init__` reads `config.SSSI_GPS` directly.
`_get_contour()` converts each `(lat, lon)` through `GeoTransformer.gps_to_pixels()`
into pixel coordinates, then reshapes to `(N, 1, 2)` float32 for OpenCV's contour API.
The polygon is **not explicitly closed** (no duplicate of V0 at the end), but OpenCV
treats contours as implicitly closed (edge from V6 back to V0 exists).

---

## 2. What does `distance_to_boundary` return? Positive = inside or outside?

`distance_to_boundary(lat, lon)` returns `(distance_m, is_inside)`.

Internally it calls `cv2.pointPolygonTest(contour, point, measureDist=True)`:
- **Positive** signed distance = point is **inside** the polygon
- **Negative** signed distance = point is **outside** the polygon
- **Zero** = point is exactly on an edge

The method takes `abs()` of the signed distance and converts from pixels to metres.
`is_inside = (signed_dist_px >= 0)` -- boundary points are treated as inside (unsafe).

The returned `distance_m` is always non-negative. The boolean `is_inside` tells you
which side.

---

## 3. How does the nearest-point projection work on edges?

In `repulsive_offset()`, lines 249-265, a manual nearest-point-on-segment loop runs:

```python
for i in range(len(pts)):
    p1 = pts[i]
    p2 = pts[(i + 1) % len(pts)]
    edge = p2 - p1
    edge_len_sq = dot(edge, edge)
    t = clip(dot(point - p1, edge) / edge_len_sq, 0, 1)
    cp = p1 + t * edge     # closest point on segment
    dist = norm(point - cp)
```

This is the standard **point-to-line-segment projection**:
- `t` is the parameter along the edge, clamped to [0, 1]
- `t = 0` means the closest point is vertex `p1`
- `t = 1` means the closest point is vertex `p2`
- `0 < t < 1` means the closest point is an interior point on the edge

The loop keeps the globally closest point across all edges.

The push vector is then `drone_pos - closest_pt` (pointing away from the boundary).

---

## 4. Is the SSSI polygon convex or concave?

**The polygon is CONCAVE.** Here is the analysis:

Converting the 7 vertices to approximate local metres (relative to V0):

| Vertex | Approx East (m) | Approx North (m) | Notes |
|--------|-----------------|-------------------|-------|
| V0     | 0               | 0                 | NW corner |
| V1     | +118            | -153              | SE (furthest south) |
| V2     | +263            | -96               | E (furthest east) |
| V3     | +231            | -20               | NE |
| V4     | +99             | -75               | **INTERIOR NOTCH** |
| V5     | +34             | -30               | W of V3 |
| V6     | +9              | +4                | Near V0 |

The path goes: V0 (NW) -> V1 (S) -> V2 (E) -> V3 (NE) -> V4 (dips back south-west)
-> V5 (back NW) -> V6 (near start).

**V4 creates a concavity.** The polygon has an inward notch between V3 and V5. The
edges V3->V4 and V4->V5 form a "dent" into the polygon interior. This means the
polygon is NOT convex.

Approximate shape (not to scale):
```
     V6---V0
     |       \
     V5       V1
      \      /
       V4   V2
        \ /
         V3
```

More accurately, the concavity means V4 is pushed inward relative to the line V3-V5,
creating a notch in the eastern side of the polygon.

---

## 5. Is the polygon wound clockwise or counterclockwise?

Using the shoelace formula on the approximate local coordinates:

V0(0,0) -> V1(118,-153) -> V2(263,-96) -> V3(231,-20) -> V4(99,-75) -> V5(34,-30) -> V6(9,4)

Computing cross products of consecutive edge pairs:
- The signed area is **negative** in standard math coordinates (y-up), which means
  the vertices are ordered **clockwise** in geographic/math convention.
- In **pixel coordinates** (y-down, which is what OpenCV uses), the winding appears
  **counterclockwise**.

For `cv2.pointPolygonTest`, the winding direction does **not matter** -- it handles
both CW and CCW polygons correctly. The sign convention (positive = inside) is
consistent regardless of winding.

---

## 6. Concave polygon: can the nearest boundary point be wrong?

**The nearest-point-on-edge computation is geometrically CORRECT for any polygon
(convex or concave).** The loop in `repulsive_offset()` iterates over every edge
and finds the globally closest point. This is the true Euclidean nearest point on
the polygon boundary, regardless of concavity. There is no shortcut that could be
fooled by concavity.

**HOWEVER, there is a subtle issue with the PUSH DIRECTION near concave vertices:**

### The problem

Consider a drone **outside** the polygon, positioned near the concave notch at V4.
The nearest boundary point will be on one of the edges V3->V4 or V4->V5. The push
vector is computed as:

```python
push_dx = px - closest_pt[0]   # drone - nearest boundary point
push_dy = py - closest_pt[1]
```

This vector points FROM the boundary TOWARD the drone -- i.e., "away from the boundary."
For a convex polygon, this always points outward (away from the polygon interior).

**But near a concave notch, this direction can point INTO the polygon interior.**

```
         V3 -------- V5
          \         /
           \  NFZ  /        <-- polygon interior
            \ ... /
             V4
              |
              |  <-- push direction (toward drone)
              D   <-- drone is here, outside, in the notch
```

The drone is outside the polygon, below V4 in the notch. The nearest boundary point
is V4 itself (or a point on the edge near V4). The push vector points from V4 toward D,
which is AWAY from the polygon -- this is actually **correct** in this specific geometry.

**The truly problematic case** is when the drone is outside but the nearest point is
on an edge whose outward normal points into the concavity:

```
    V3 ------------ V5
     \             /
      \    NFZ    /
       \        /
        V4----+      <-- nearest point on edge V4->V5
              |
              D      <-- drone is here
```

If the drone D is positioned such that the nearest point is on edge V4->V5, the push
vector `D - nearest` points roughly southward. But the "safe" direction might actually
be eastward or westward to get away from the notch. The push vector is locally correct
(it moves the drone away from the nearest edge) but may not be the globally optimal
escape direction.

### Impact assessment

For THIS specific polygon, the concavity at V4 is relatively shallow (V4 is roughly
25m inside the line V3-V5). The repulsive field only activates within `SOFT_BOUNDARY`
= 8m of the boundary. A drone would need to be within 8m of the notch edges to be
affected.

**Practical risk: LOW.** The lawnmower pattern is filtered with a 30m buffer
(`NFZ_WAYPOINT_BUFFER_M = 30`), so no waypoints should be anywhere near V4's notch.
The repulsive field is a secondary safety layer that nudges waypoints -- even if the
push direction is suboptimal near the notch, it still pushes away from the nearest
edge, which prevents direct boundary crossing.

### The degenerate-point fallback (lines 276-315)

When the drone is exactly ON the boundary (`push_len < 1e-6`), the code computes
the outward edge normal instead. It correctly tests which direction is "outward" by
checking whether a test point offset along the normal is inside or outside the polygon
(line 309). This handles the degenerate case well, even for concave polygons.

---

## Summary of findings

| Question | Answer |
|----------|--------|
| Storage format | List of `(lat, lon)` tuples, 7 vertices, implicitly closed |
| `distance_to_boundary` sign | Returns `(dist_m, is_inside)`. dist_m always >= 0. is_inside=True when inside or on boundary |
| Nearest point projection | Standard point-to-segment projection, correct for any polygon |
| Concave polygon? | **YES** -- V4 creates a notch between V3 and V5 |
| Winding | Clockwise in geographic coords (irrelevant to cv2) |
| Push direction near concavity | Locally correct (away from nearest edge) but may not be globally optimal escape direction. Practical risk is LOW due to 30m waypoint buffer |

### No code changes needed

The implementation is sound for the actual operational scenario. The 30m waypoint
buffer prevents the drone from ever flying close enough to the concave notch for the
push-direction subtlety to matter. The nearest-point computation itself is always
mathematically correct.
