"""Unit tests for gps_utils.py — shared GPS math."""
import pytest
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gps_utils import (
    gps_distance,
    calculate_target_from_pixels,
    offset_gps_by_distance,
    landing_offset_7_5m,
)


class TestGpsDistance:
    def test_zero_distance(self):
        assert gps_distance(51.42, -2.67, 51.42, -2.67) == pytest.approx(0, abs=0.01)

    def test_known_distance_100m_north(self):
        # 0.0009 degrees lat ≈ 100m
        d = gps_distance(51.42, -2.67, 51.4209, -2.67)
        assert 95 < d < 105

    def test_known_distance_100m_east(self):
        # At 51.4N, 0.00143 degrees lon ≈ 100m
        d = gps_distance(51.42, -2.67, 51.42, -2.66857)
        assert 80 < d < 120

    def test_symmetry(self):
        d1 = gps_distance(51.42, -2.67, 51.43, -2.68)
        d2 = gps_distance(51.43, -2.68, 51.42, -2.67)
        assert d1 == pytest.approx(d2, rel=1e-6)

    def test_returns_float(self):
        d = gps_distance(51.42, -2.67, 51.43, -2.68)
        assert isinstance(d, float)


class TestCalculateTargetFromPixels:
    def test_center_pixel_returns_drone_position(self):
        """Detection at frame center should return drone's GPS position."""
        lat, lon = calculate_target_from_pixels(
            u=728, v=544,  # center of 1456x1088
            drone_alt=30, drone_yaw=0,
            drone_lat=51.42, drone_lon=-2.67,
            image_w=1456, image_h=1088,
            sensor_width_mm=5.02, focal_length_mm=5.46
        )
        assert abs(lat - 51.42) < 0.0001
        assert abs(lon - (-2.67)) < 0.0001

    def test_offset_pixel_returns_different_position(self):
        """Detection away from center should offset the GPS."""
        lat_center, lon_center = calculate_target_from_pixels(
            728, 544, 30, 0, 51.42, -2.67, 1456, 1088, 5.02, 5.46)
        lat_off, lon_off = calculate_target_from_pixels(
            1000, 544, 30, 0, 51.42, -2.67, 1456, 1088, 5.02, 5.46)
        # Right of center → east → higher longitude
        assert lon_off > lon_center

    def test_higher_altitude_larger_offset(self):
        """Same pixel offset at higher altitude should give larger GPS offset."""
        _, lon_low = calculate_target_from_pixels(
            1000, 544, 20, 0, 51.42, -2.67, 1456, 1088, 5.02, 5.46)
        _, lon_high = calculate_target_from_pixels(
            1000, 544, 50, 0, 51.42, -2.67, 1456, 1088, 5.02, 5.46)
        offset_low = abs(lon_low - (-2.67))
        offset_high = abs(lon_high - (-2.67))
        assert offset_high > offset_low

    def test_returns_tuple_of_floats(self):
        result = calculate_target_from_pixels(
            728, 544, 30, 0, 51.42, -2.67, 1456, 1088, 5.02, 5.46)
        assert len(result) == 2
        assert isinstance(result[0], float)
        assert isinstance(result[1], float)


class TestOffsetGps:
    def test_zero_offset(self):
        lat, lon = offset_gps_by_distance(51.42, -2.67, 0, 0)
        assert lat == pytest.approx(51.42, abs=1e-8)
        assert lon == pytest.approx(-2.67, abs=1e-8)

    def test_north_offset_increases_lat(self):
        lat, lon = offset_gps_by_distance(51.42, -2.67, 100, 0)
        assert lat > 51.42

    def test_east_offset_increases_lon(self):
        lat, lon = offset_gps_by_distance(51.42, -2.67, 0, 100)
        assert lon > -2.67

    def test_south_offset_decreases_lat(self):
        lat, lon = offset_gps_by_distance(51.42, -2.67, -100, 0)
        assert lat < 51.42

    def test_100m_offset_magnitude(self):
        lat, lon = offset_gps_by_distance(51.42, -2.67, 100, 0)
        d = gps_distance(51.42, -2.67, lat, lon)
        assert 95 < d < 105


class TestLandingOffset:
    def test_north_offset(self):
        lat, lon = landing_offset_7_5m(51.42, -2.67, 'n')
        assert lat > 51.42
        assert lon == pytest.approx(-2.67, abs=1e-6)

    def test_south_offset(self):
        lat, lon = landing_offset_7_5m(51.42, -2.67, 's')
        assert lat < 51.42

    def test_east_offset(self):
        lat, lon = landing_offset_7_5m(51.42, -2.67, 'e')
        assert lon > -2.67

    def test_west_offset(self):
        lat, lon = landing_offset_7_5m(51.42, -2.67, 'w')
        assert lon < -2.67

    def test_offset_distance_is_7_5m(self):
        lat, lon = landing_offset_7_5m(51.42, -2.67, 'n')
        d = gps_distance(51.42, -2.67, lat, lon)
        assert 7.0 < d < 8.0
