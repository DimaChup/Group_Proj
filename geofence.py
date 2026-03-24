# geofence.py — SSSI No-Fly Zone enforcement with potential field repulsion
#
# Two layers of protection:
#   1. Waypoint filtering at plan time (skip waypoints near NFZ)
#   2. Runtime check during flight (slow down / RTL if too close)
#
# Uses cv2.pointPolygonTest for fast signed distance computation.
# No extra dependencies — just numpy + cv2 (already required).

import numpy as np
import cv2
import config


class NFZGeofence:
    """SSSI no-fly zone enforcement with soft + hard boundaries."""

    def __init__(self, geo_transformer):
        self.geo = geo_transformer
        self.sssi_polygon_gps = config.SSSI_GPS
        self._sssi_contour = None  # Cached pixel contour

        # Buffer distances (meters)
        self.HARD_BOUNDARY = 3.0     # Auto-manual if closer than this
        self.SOFT_BOUNDARY = 8.0     # Repulsive push if closer (quadratic, 10 m/s max)
        self.WAYPOINT_BUFFER = 30.0  # For filter_waypoints() if used

    def _get_contour(self):
        """Cache polygon as cv2 contour format."""
        if self._sssi_contour is None and self.sssi_polygon_gps:
            pts = np.array([
                self.geo.gps_to_pixels(lat, lon)
                for lat, lon in self.sssi_polygon_gps
            ], dtype=np.float32)
            self._sssi_contour = pts.reshape((-1, 1, 2))
        return self._sssi_contour

    def distance_to_boundary(self, lat, lon):
        """
        Distance from a GPS point to the SSSI boundary.

        Returns:
            (distance_m, is_inside)
            distance_m: distance to nearest boundary edge in meters
            is_inside: True if point is inside the NFZ
        """
        contour = self._get_contour()
        if contour is None:
            return float('inf'), False

        px, py = self.geo.gps_to_pixels(lat, lon)
        point = (float(px), float(py))

        # cv2.pointPolygonTest returns:
        #   positive = inside, negative = outside, 0 = on edge
        signed_dist_px = cv2.pointPolygonTest(contour, point, True)

        is_inside = signed_dist_px > 0
        dist_px = abs(signed_dist_px)
        dist_m = dist_px / self.geo.pix_per_m

        return dist_m, is_inside

    def filter_waypoints(self, waypoints_gps):
        """
        Remove waypoints that are inside or too close to the SSSI boundary.

        Returns:
            (filtered_waypoints, skipped_count)
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
        """
        Runtime flight safety check.

        Returns:
            (status, speed_factor)
            status: 'safe' | 'warning' | 'critical'
            speed_factor: 1.0 = full speed, 0.5 = half speed, 0.0 = stop/RTL
        """
        if not self.sssi_polygon_gps or len(self.sssi_polygon_gps) < 3:
            return 'safe', 1.0

        dist_m, is_inside = self.distance_to_boundary(lat, lon)

        if is_inside or dist_m < self.HARD_BOUNDARY:
            return 'critical', 0.0

        if dist_m < self.SOFT_BOUNDARY:
            # Gradient: speed reduces linearly from 100% at soft boundary to 30% at hard boundary
            ratio = (dist_m - self.HARD_BOUNDARY) / (self.SOFT_BOUNDARY - self.HARD_BOUNDARY)
            speed_factor = 0.3 + 0.7 * ratio  # 0.3 to 1.0
            return 'warning', speed_factor

        return 'safe', 1.0

    def repulsive_offset(self, lat, lon):
        """
        Compute a repulsive GPS offset pushing away from NFZ boundary.
        Uses inverse-distance potential field.

        Returns:
            (offset_lat, offset_lon) — add to target waypoint to push away
            Returns (0, 0) if far from boundary.
        """
        if not self.sssi_polygon_gps or len(self.sssi_polygon_gps) < 3:
            return 0.0, 0.0

        dist_m, is_inside = self.distance_to_boundary(lat, lon)

        if dist_m > self.SOFT_BOUNDARY:
            return 0.0, 0.0

        # Find nearest point on boundary to compute push direction
        contour = self._get_contour()
        px, py = self.geo.gps_to_pixels(lat, lon)

        # Find closest edge point
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

        # Push direction: away from closest boundary point
        push_dx = px - closest_pt[0]
        push_dy = py - closest_pt[1]
        push_len = np.sqrt(push_dx**2 + push_dy**2)

        if push_len < 1e-6:
            return 0.0, 0.0

        # Normalize and scale by inverse distance (stronger when closer)
        repulsion_strength = max(0, (self.SOFT_BOUNDARY - dist_m)) * 0.5  # meters of push
        push_dx = (push_dx / push_len) * repulsion_strength * self.geo.pix_per_m
        push_dy = (push_dy / push_len) * repulsion_strength * self.geo.pix_per_m

        # Convert pixel offset to GPS offset
        offset_lat, offset_lon = self.geo.pixels_to_gps(int(push_dx), int(push_dy))
        offset_lat -= config.REF_LAT
        offset_lon -= config.REF_LON

        return -offset_lat, -offset_lon
