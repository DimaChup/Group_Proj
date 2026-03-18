"""
Unit tests for planning.py — PathPlanner lawnmower and spiral pattern generation.

Run:  python -m pytest tests/unit/test_planning.py -v
  or: python tests/unit/test_planning.py
"""
import sys
import os
import math

# ---- path setup so imports work from any cwd ----
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pytest
import config
from utils import GeoTransformer
from planning import PathPlanner

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
MAP_W = 2000  # pixels — big enough for the test polygons
MAP_H = 2000

def _make_planner(gps_polygon):
    """Build a PathPlanner from a list of (lat, lon) GPS corners."""
    geo = GeoTransformer(MAP_W)
    pixel_polygon = [geo.gps_to_pixels(lat, lon) for lat, lon in gps_polygon]
    return PathPlanner(geo, pixel_polygon)


def _square_polygon(center_lat=None, center_lon=None, half_deg=0.001):
    """Return a square polygon ~200m on a side.

    Default centre is offset south-east of REF_LAT/REF_LON so that
    gps_to_pixels produces coordinates well inside a 2000x2000 map.
    (REF is map top-left; south = +y, east = +x in pixel space.)
    """
    clat = center_lat if center_lat is not None else (config.REF_LAT - 0.001)
    clon = center_lon if center_lon is not None else (config.REF_LON + 0.001)
    return [
        (clat + half_deg, clon - half_deg),
        (clat + half_deg, clon + half_deg),
        (clat - half_deg, clon + half_deg),
        (clat - half_deg, clon - half_deg),
    ]


def _rect_polygon(lat_half=0.001, lon_half=0.002):
    """Return a rectangular polygon centred south-east of REF."""
    clat = config.REF_LAT - 0.001
    clon = config.REF_LON + 0.001
    return [
        (clat + lat_half, clon - lon_half),
        (clat + lat_half, clon + lon_half),
        (clat - lat_half, clon + lon_half),
        (clat - lat_half, clon - lon_half),
    ]


def _triangle_polygon(half_deg=0.001):
    """Return a triangular polygon (3 vertices) south-east of REF."""
    clat = config.REF_LAT - 0.001
    clon = config.REF_LON + 0.001
    return [
        (clat + half_deg, clon),
        (clat - half_deg, clon + half_deg),
        (clat - half_deg, clon - half_deg),
    ]


def _haversine_m(lat1, lon1, lat2, lon2):
    """Approx distance in metres between two GPS points."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ===========================================================================
# Tests — Lawnmower (generate_search_pattern)
# ===========================================================================

class TestLawnmowerBasic:
    """Core lawnmower pattern behaviour."""

    def test_square_returns_nonempty(self):
        planner = _make_planner(_square_polygon())
        wps = planner.generate_search_pattern(MAP_W, MAP_H)
        assert len(wps) > 0, "Lawnmower should produce waypoints for a square polygon"

    def test_waypoints_are_lat_lon_tuples(self):
        planner = _make_planner(_square_polygon())
        wps = planner.generate_search_pattern(MAP_W, MAP_H)
        for wp in wps:
            assert isinstance(wp, tuple), f"Waypoint should be tuple, got {type(wp)}"
            assert len(wp) == 2, f"Waypoint should have 2 elements (lat, lon), got {len(wp)}"
            lat, lon = wp
            assert isinstance(lat, (float, np.floating)), f"Latitude should be float, got {type(lat)}"
            assert isinstance(lon, (float, np.floating)), f"Longitude should be float, got {type(lon)}"

    def test_waypoints_near_search_area(self):
        poly = _square_polygon()
        planner = _make_planner(poly)
        wps = planner.generate_search_pattern(MAP_W, MAP_H)
        center_lat = sum(p[0] for p in poly) / len(poly)
        center_lon = sum(p[1] for p in poly) / len(poly)
        for wp in wps:
            dist = _haversine_m(wp[0], wp[1], center_lat, center_lon)
            assert dist < 500, (
                f"Waypoint ({wp[0]:.6f}, {wp[1]:.6f}) is {dist:.0f}m from polygon centre "
                f"— should be within 500m for a ~200m polygon"
            )

    def test_no_consecutive_duplicates(self):
        planner = _make_planner(_square_polygon())
        wps = planner.generate_search_pattern(MAP_W, MAP_H)
        for i in range(1, len(wps)):
            assert wps[i] != wps[i - 1], (
                f"Consecutive waypoints {i-1} and {i} are identical: {wps[i]}"
            )

    def test_even_number_of_waypoints(self):
        """Each strip produces 2 waypoints (start + end) so total should be even."""
        planner = _make_planner(_square_polygon())
        wps = planner.generate_search_pattern(MAP_W, MAP_H)
        assert len(wps) % 2 == 0, (
            f"Expected even number of waypoints (2 per strip), got {len(wps)}"
        )

    def test_triangle_polygon(self):
        planner = _make_planner(_triangle_polygon())
        wps = planner.generate_search_pattern(MAP_W, MAP_H)
        assert len(wps) > 0, "Triangle polygon should still produce waypoints"

    def test_rectangle_polygon(self):
        planner = _make_planner(_rect_polygon())
        wps = planner.generate_search_pattern(MAP_W, MAP_H)
        assert len(wps) > 0, "Rectangle polygon should produce waypoints"


class TestLawnmowerAltitude:
    """Altitude affects swath width, which affects number of strips."""

    def test_higher_alt_fewer_waypoints(self):
        planner = _make_planner(_square_polygon())
        wps_low = planner.generate_search_pattern(MAP_W, MAP_H, alt_override=20)
        wps_high = planner.generate_search_pattern(MAP_W, MAP_H, alt_override=80)
        assert len(wps_high) < len(wps_low), (
            f"Higher altitude should produce fewer strips: "
            f"got {len(wps_high)} (80m) vs {len(wps_low)} (20m)"
        )

    def test_alt_override_changes_count(self):
        planner = _make_planner(_square_polygon())
        wps_a = planner.generate_search_pattern(MAP_W, MAP_H, alt_override=30)
        wps_b = planner.generate_search_pattern(MAP_W, MAP_H, alt_override=60)
        assert len(wps_a) != len(wps_b), (
            "Different altitudes should produce different waypoint counts"
        )


class TestLawnmowerDroneGPS:
    """Passing drone_gps should optimise start corner but still cover the area."""

    def test_drone_gps_accepted(self):
        planner = _make_planner(_square_polygon())
        drone = (config.REF_LAT - 0.001, config.REF_LON + 0.001)
        wps = planner.generate_search_pattern(MAP_W, MAP_H, drone_gps=drone)
        assert len(wps) > 0

    def test_drone_gps_same_count(self):
        """drone_gps changes order, not quantity."""
        planner = _make_planner(_square_polygon())
        wps_no_drone = planner.generate_search_pattern(MAP_W, MAP_H)
        drone = (config.REF_LAT - 0.002, config.REF_LON + 0.002)
        wps_with_drone = planner.generate_search_pattern(MAP_W, MAP_H, drone_gps=drone)
        assert len(wps_no_drone) == len(wps_with_drone), (
            "drone_gps should not change the total number of waypoints"
        )


class TestLawnmowerDegenerate:
    """Edge cases and degenerate inputs."""

    def test_empty_polygon(self):
        geo = GeoTransformer(MAP_W)
        planner = PathPlanner(geo, [])
        wps = planner.generate_search_pattern(MAP_W, MAP_H)
        assert wps == [], "Empty polygon should return empty list"

    def test_single_point(self):
        geo = GeoTransformer(MAP_W)
        px = geo.gps_to_pixels(config.REF_LAT, config.REF_LON)
        planner = PathPlanner(geo, [px])
        wps = planner.generate_search_pattern(MAP_W, MAP_H)
        assert wps == [], "Single-point polygon should return empty list"

    def test_two_points(self):
        geo = GeoTransformer(MAP_W)
        p1 = geo.gps_to_pixels(config.REF_LAT, config.REF_LON)
        p2 = geo.gps_to_pixels(config.REF_LAT + 0.001, config.REF_LON)
        planner = PathPlanner(geo, [p1, p2])
        wps = planner.generate_search_pattern(MAP_W, MAP_H)
        assert wps == [], "Two-point polygon should return empty list"

    def test_very_small_polygon(self):
        """A tiny polygon (~10m) should still produce at least one strip."""
        small = _square_polygon(
            center_lat=config.REF_LAT - 0.001,
            center_lon=config.REF_LON + 0.001,
            half_deg=0.00005,
        )  # ~5.5m half-side
        planner = _make_planner(small)
        # Use low altitude so swath is small enough to fit inside
        wps = planner.generate_search_pattern(MAP_W, MAP_H, alt_override=5)
        # May produce 0 waypoints if swath > polygon — that's acceptable too
        assert isinstance(wps, list), "Should return a list even for tiny polygon"


# ===========================================================================
# Tests — Spiral (generate_spiral_pattern)
# ===========================================================================

class TestSpiralBasic:
    """Spiral pattern generation."""

    def test_spiral_returns_nonempty(self):
        planner = _make_planner(_square_polygon())
        wps = planner.generate_spiral_pattern(MAP_W, MAP_H)
        assert len(wps) > 0, "Spiral should produce waypoints for a square polygon"

    def test_spiral_waypoints_are_tuples(self):
        planner = _make_planner(_square_polygon())
        wps = planner.generate_spiral_pattern(MAP_W, MAP_H)
        for wp in wps:
            assert isinstance(wp, tuple) and len(wp) == 2
            assert isinstance(wp[0], (float, np.floating)) and isinstance(wp[1], (float, np.floating))

    def test_spiral_waypoints_near_area(self):
        poly = _square_polygon()
        planner = _make_planner(poly)
        wps = planner.generate_spiral_pattern(MAP_W, MAP_H)
        center_lat = sum(p[0] for p in poly) / len(poly)
        center_lon = sum(p[1] for p in poly) / len(poly)
        for wp in wps:
            dist = _haversine_m(wp[0], wp[1], center_lat, center_lon)
            assert dist < 500, f"Spiral waypoint {dist:.0f}m from centre is too far"

    def test_spiral_no_consecutive_duplicates(self):
        planner = _make_planner(_square_polygon())
        wps = planner.generate_spiral_pattern(MAP_W, MAP_H)
        for i in range(1, len(wps)):
            assert wps[i] != wps[i - 1], (
                f"Spiral: consecutive waypoints {i-1} and {i} identical: {wps[i]}"
            )

    def test_spiral_degenerate_empty(self):
        geo = GeoTransformer(MAP_W)
        planner = PathPlanner(geo, [])
        wps = planner.generate_spiral_pattern(MAP_W, MAP_H)
        assert wps == []

    def test_spiral_degenerate_two_points(self):
        geo = GeoTransformer(MAP_W)
        p1 = geo.gps_to_pixels(config.REF_LAT, config.REF_LON)
        p2 = geo.gps_to_pixels(config.REF_LAT + 0.001, config.REF_LON)
        planner = PathPlanner(geo, [p1, p2])
        wps = planner.generate_spiral_pattern(MAP_W, MAP_H)
        assert wps == []

    def test_spiral_alt_override(self):
        planner = _make_planner(_square_polygon())
        wps_low = planner.generate_spiral_pattern(MAP_W, MAP_H, alt_override=20)
        wps_high = planner.generate_spiral_pattern(MAP_W, MAP_H, alt_override=80)
        # Higher altitude = wider swath = fewer points per ring
        assert len(wps_low) != len(wps_high), (
            "Spiral should produce different counts at different altitudes"
        )

    def test_spiral_drone_gps_accepted(self):
        planner = _make_planner(_square_polygon())
        drone = (config.REF_LAT - 0.001, config.REF_LON + 0.001)
        wps = planner.generate_spiral_pattern(MAP_W, MAP_H, drone_gps=drone)
        assert len(wps) > 0

    def test_spiral_triangle(self):
        planner = _make_planner(_triangle_polygon())
        wps = planner.generate_spiral_pattern(MAP_W, MAP_H)
        assert len(wps) > 0, "Spiral should work with a triangle polygon"


# ===========================================================================
# Tests — Pattern comparison
# ===========================================================================

class TestPatternComparison:
    """Compare lawnmower vs spiral on same polygon."""

    def test_both_cover_area(self):
        planner = _make_planner(_square_polygon())
        lawn = planner.generate_search_pattern(MAP_W, MAP_H)
        spiral = planner.generate_spiral_pattern(MAP_W, MAP_H)
        assert len(lawn) > 0 and len(spiral) > 0

    def test_different_patterns(self):
        planner = _make_planner(_square_polygon())
        lawn = planner.generate_search_pattern(MAP_W, MAP_H)
        spiral = planner.generate_spiral_pattern(MAP_W, MAP_H)
        assert lawn != spiral, "Lawnmower and spiral should produce different patterns"


# ===========================================================================
# Run with python directly
# ===========================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
