# geofence.py — SSSI No-Fly Zone enforcement with potential-field repulsion
#
# Three layers of protection:
#   1. Waypoint filtering at plan time  (skip waypoints near NFZ)
#   2. Runtime position check            (slow down / RTL if too close)
#   3. Repulsive potential-field offset   (nudge waypoints away from boundary)
#
# Uses cv2.pointPolygonTest for fast signed-distance computation.
# No extra dependencies beyond numpy + cv2 (already required by vision.py).

import numpy as np
import cv2
import config


class NFZGeofence:
    """No-Fly Zone enforcement around the SSSI polygon.

    Provides three complementary safety mechanisms that keep the drone away
    from the SSSI (Site of Special Scientific Interest) boundary:

    1. **Plan-time filtering** -- ``filter_waypoints()`` removes any
       lawnmower waypoint that falls inside or within a configurable
       buffer of the NFZ.

    2. **Runtime position check** -- ``check_position()`` returns a
       traffic-light status (safe / warning / critical) and a speed-
       reduction factor so the flight controller can decelerate or RTL.

    3. **Repulsive offset** -- ``repulsive_offset()`` computes a small
       GPS delta that pushes the target waypoint away from the nearest
       boundary edge, using an inverse-distance potential field.

    All distance calculations are performed in a local pixel coordinate
    frame via ``GeoTransformer`` (see utils.py) and then converted back
    to GPS.

    Args:
        geo_transformer: A ``GeoTransformer`` instance that converts
            between GPS (lat, lon) and pixel (x, y) coordinates.
    """

    def __init__(self, geo_transformer):
        self.geo = geo_transformer
        self.sssi_polygon_gps = config.SSSI_GPS
        self._sssi_contour = None  # Cached cv2 contour (pixel coords)

        # Buffer distances (metres) loaded from config.py
        self.HARD_BOUNDARY = config.NFZ_HARD_BOUNDARY_M
        self.SOFT_BOUNDARY = config.NFZ_SOFT_BOUNDARY_M
        self.WAYPOINT_BUFFER = config.NFZ_WAYPOINT_BUFFER_M

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_contour(self):
        """Return the SSSI polygon as a cv2 contour (Nx1x2 float32).

        The contour is computed once from ``config.SSSI_GPS`` via the
        geo-transformer and cached for the lifetime of the object.

        Returns:
            numpy.ndarray or None: Contour array suitable for
            ``cv2.pointPolygonTest``, or *None* if no polygon is
            configured.
        """
        if self._sssi_contour is None and self.sssi_polygon_gps:
            pts = np.array([
                self.geo.gps_to_pixels(lat, lon)
                for lat, lon in self.sssi_polygon_gps
            ], dtype=np.float32)
            self._sssi_contour = pts.reshape((-1, 1, 2))
        return self._sssi_contour

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def distance_to_boundary(self, lat, lon):
        """Compute the shortest distance from a GPS point to the NFZ boundary.

        Internally uses ``cv2.pointPolygonTest`` which returns a
        **signed** pixel distance:

        * **positive** -- point is **inside** the polygon
        * **negative** -- point is **outside** the polygon
        * **zero**     -- point lies exactly on an edge

        The sign is consumed here and exposed as the boolean
        ``is_inside``; the returned ``distance_m`` is always
        non-negative.

        Args:
            lat: Latitude in decimal degrees.
            lon: Longitude in decimal degrees.

        Returns:
            tuple[float, bool]:
                * ``distance_m`` -- perpendicular distance to the
                  nearest boundary edge, in metres (always >= 0).
                * ``is_inside`` -- *True* when the point is inside
                  the NFZ polygon.  If no polygon is configured,
                  returns ``(inf, False)``.
        """
        contour = self._get_contour()
        if contour is None:
            return float('inf'), False

        px, py = self.geo.gps_to_pixels(lat, lon)
        point = (float(px), float(py))

        # cv2.pointPolygonTest: positive = inside, negative = outside
        signed_dist_px = cv2.pointPolygonTest(contour, point, True)

        is_inside = signed_dist_px > 0
        dist_px = abs(signed_dist_px)
        dist_m = dist_px / self.geo.pix_per_m

        return dist_m, is_inside

    def filter_waypoints(self, waypoints_gps):
        """Remove waypoints that are inside or too close to the NFZ.

        Any waypoint whose distance to the boundary is less than
        ``WAYPOINT_BUFFER`` (or that lies inside the polygon) is
        dropped from the list.

        Args:
            waypoints_gps: List of ``(lat, lon)`` tuples.

        Returns:
            tuple[list, int]:
                * Filtered list of ``(lat, lon)`` waypoints that are
                  safely outside the buffer.
                * Number of waypoints that were removed.
        """
        if not self.sssi_polygon_gps or len(self.sssi_polygon_gps) < 3:
            return waypoints_gps, 0

        filtered = []
        skipped = 0

        for lat, lon in waypoints_gps:
            dist_m, is_inside = self.distance_to_boundary(lat, lon)

            if is_inside or dist_m < self.WAYPOINT_BUFFER:
                skipped += 1
            else:
                filtered.append((lat, lon))

        if skipped > 0:
            print(f"[GEOFENCE] Filtered {skipped} waypoints within {self.WAYPOINT_BUFFER}m of SSSI")

        return filtered, skipped

    def check_position(self, lat, lon):
        """Runtime flight-safety check against the NFZ boundary.

        Classifies the drone's current position into one of three zones:

        * **safe** (distance > ``SOFT_BOUNDARY``) -- full speed.
        * **warning** (between soft and hard boundary) -- speed
          reduces linearly from 100 % at the soft boundary down to
          30 % at the hard boundary.
        * **critical** (inside polygon or distance < ``HARD_BOUNDARY``)
          -- speed factor 0 (stop / RTL).

        Args:
            lat: Current latitude in decimal degrees.
            lon: Current longitude in decimal degrees.

        Returns:
            tuple[str, float]:
                * ``status`` -- one of ``'safe'``, ``'warning'``,
                  ``'critical'``.
                * ``speed_factor`` -- multiplier in the range [0.0, 1.0]
                  to apply to the commanded speed.
        """
        if not self.sssi_polygon_gps or len(self.sssi_polygon_gps) < 3:
            return 'safe', 1.0

        dist_m, is_inside = self.distance_to_boundary(lat, lon)

        if is_inside or dist_m < self.HARD_BOUNDARY:
            return 'critical', 0.0

        if dist_m < self.SOFT_BOUNDARY:
            # Linear gradient: 100 % at soft edge -> 30 % at hard edge
            ratio = (dist_m - self.HARD_BOUNDARY) / (self.SOFT_BOUNDARY - self.HARD_BOUNDARY)
            speed_factor = 0.3 + 0.7 * ratio  # 0.3 to 1.0
            return 'warning', speed_factor

        return 'safe', 1.0

    def repulsive_offset(self, lat, lon):
        """Compute a GPS offset that pushes the drone away from the NFZ.

        Uses an inverse-distance potential field: the closer the drone
        is to the boundary, the stronger the repulsive push.  The push
        direction is always perpendicular to (away from) the nearest
        polygon edge.

        **Sign convention (critical):**
        The pixel-to-GPS conversion via ``GeoTransformer.pixels_to_gps``
        followed by subtracting the reference origin produces an
        *inverted* result.  The returned offsets are therefore
        **negated** so that adding them to a target waypoint pushes
        the drone *away* from the NFZ.  Without the negation the force
        would *attract* the drone into the NFZ.

        Callers should apply the offset as::

            target_lat += offset_lat
            target_lon += offset_lon

        Args:
            lat: Current latitude in decimal degrees.
            lon: Current longitude in decimal degrees.

        Returns:
            tuple[float, float]:
                * ``offset_lat`` -- latitude delta to **add** to the
                  target waypoint (positive = push north).
                * ``offset_lon`` -- longitude delta to **add** to the
                  target waypoint (positive = push east).
                * Returns ``(0.0, 0.0)`` when the drone is farther
                  than ``SOFT_BOUNDARY`` from the NFZ or when no
                  polygon is configured.
        """
        if not self.sssi_polygon_gps or len(self.sssi_polygon_gps) < 3:
            return 0.0, 0.0

        dist_m, is_inside = self.distance_to_boundary(lat, lon)

        if dist_m > self.SOFT_BOUNDARY:
            return 0.0, 0.0

        # --- Find the nearest point on the boundary polygon edges ---
        contour = self._get_contour()
        px, py = self.geo.gps_to_pixels(lat, lon)

        min_dist = float('inf')
        closest_pt = None
        pts = contour.reshape(-1, 2)

        for i in range(len(pts)):
            p1 = pts[i]
            p2 = pts[(i + 1) % len(pts)]
            edge = p2 - p1
            edge_len_sq = np.dot(edge, edge)

            if edge_len_sq < 1e-6:
                dist = np.linalg.norm(np.array([px, py]) - p1)
                cp = p1
            else:
                t = np.clip(np.dot(np.array([px, py]) - p1, edge) / edge_len_sq, 0, 1)
                cp = p1 + t * edge
                dist = np.linalg.norm(np.array([px, py]) - cp)

            if dist < min_dist:
                min_dist = dist
                closest_pt = cp

        if closest_pt is None or min_dist < 1e-6:
            return 0.0, 0.0

        # --- Compute push vector (pixel space, away from boundary) ---
        push_dx = px - closest_pt[0]
        push_dy = py - closest_pt[1]
        push_len = np.sqrt(push_dx**2 + push_dy**2)

        if push_len < 1e-6:
            return 0.0, 0.0

        # Strength grows linearly as the drone approaches the boundary
        repulsion_strength = max(0, (self.SOFT_BOUNDARY - dist_m)) * 0.5  # metres
        push_dx = (push_dx / push_len) * repulsion_strength * self.geo.pix_per_m
        push_dy = (push_dy / push_len) * repulsion_strength * self.geo.pix_per_m

        # --- Convert pixel offset to GPS offset (see sign note above) ---
        offset_lat, offset_lon = self.geo.pixels_to_gps(push_dx, push_dy)
        offset_lat -= config.REF_LAT
        offset_lon -= config.REF_LON

        return -offset_lat, -offset_lon
