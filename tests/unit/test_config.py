"""Unit tests for config.py — configuration validation."""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config


class TestAltitudes:
    def test_target_alt_positive(self):
        assert config.TARGET_ALT > 0, "TARGET_ALT must be positive"

    def test_verify_alt_positive(self):
        assert config.VERIFY_ALT > 0, "VERIFY_ALT must be positive"

    def test_verify_alt_less_than_target(self):
        assert config.VERIFY_ALT < config.TARGET_ALT, \
            f"VERIFY_ALT ({config.VERIFY_ALT}) should be less than TARGET_ALT ({config.TARGET_ALT})"


class TestImageDimensions:
    def test_image_width_positive(self):
        assert config.IMAGE_W > 0

    def test_image_height_positive(self):
        assert config.IMAGE_H > 0

    def test_image_dimensions_reasonable(self):
        # At least 320x240, at most 8K
        assert 320 <= config.IMAGE_W <= 7680, f"IMAGE_W={config.IMAGE_W} outside reasonable range"
        assert 240 <= config.IMAGE_H <= 4320, f"IMAGE_H={config.IMAGE_H} outside reasonable range"


class TestConfidenceThreshold:
    def test_confidence_in_0_1_range(self):
        assert 0.0 < config.CONFIDENCE_THRESHOLD <= 1.0, \
            f"CONFIDENCE_THRESHOLD={config.CONFIDENCE_THRESHOLD} must be in (0, 1]"

    def test_confidence_is_float(self):
        assert isinstance(config.CONFIDENCE_THRESHOLD, float)


class TestSpeeds:
    def test_transit_speed_positive(self):
        assert config.TRANSIT_SPEED_MPS > 0, "TRANSIT_SPEED_MPS must be positive"

    def test_search_speed_positive(self):
        assert config.SEARCH_SPEED_MPS > 0, "SEARCH_SPEED_MPS must be positive"

    def test_search_speed_less_than_transit(self):
        assert config.SEARCH_SPEED_MPS <= config.TRANSIT_SPEED_MPS, \
            "Search speed should not exceed transit speed"


class TestCameraSettings:
    def test_focal_length_realistic(self):
        assert 1.0 <= config.FOCAL_LENGTH_MM <= 20.0, \
            f"FOCAL_LENGTH_MM={config.FOCAL_LENGTH_MM} outside realistic range [1, 20] mm"

    def test_sensor_width_positive(self):
        assert config.SENSOR_WIDTH_MM > 0, "SENSOR_WIDTH_MM must be positive"

    def test_sensor_width_realistic(self):
        # Typical small sensors are 2-10 mm wide
        assert 1.0 <= config.SENSOR_WIDTH_MM <= 15.0, \
            f"SENSOR_WIDTH_MM={config.SENSOR_WIDTH_MM} outside realistic range"

    def test_camera_index_non_negative(self):
        assert config.REAL_CAMERA_INDEX >= 0


class TestSearchAreaGPS:
    def test_is_valid_polygon(self):
        assert len(config.SEARCH_AREA_GPS) >= 3, \
            f"SEARCH_AREA_GPS needs >= 3 points, got {len(config.SEARCH_AREA_GPS)}"

    def test_points_are_tuples_of_two(self):
        for i, pt in enumerate(config.SEARCH_AREA_GPS):
            assert len(pt) == 2, f"Point {i} should be (lat, lon), got {pt}"

    def test_coordinates_in_bristol_area(self):
        """All GPS points should be near Bristol, UK (lat ~51.4, lon ~-2.6)."""
        for i, (lat, lon) in enumerate(config.SEARCH_AREA_GPS):
            assert 51.0 <= lat <= 52.0, \
                f"Point {i} lat={lat} not in Bristol area [51.0, 52.0]"
            assert -3.0 <= lon <= -2.0, \
                f"Point {i} lon={lon} not in Bristol area [-3.0, -2.0]"


class TestMode:
    def test_mode_is_valid(self):
        assert config.MODE in ("SIMULATION", "REAL"), \
            f"MODE={config.MODE!r} must be 'SIMULATION' or 'REAL'"


class TestFilePaths:
    def test_map_file_contains_map(self):
        assert "map" in config.MAP_FILE.lower(), \
            f"MAP_FILE={config.MAP_FILE!r} should contain 'map'"

    def test_dummy_file_contains_dummy(self):
        assert "dummy" in config.DUMMY_FILE.lower(), \
            f"DUMMY_FILE={config.DUMMY_FILE!r} should contain 'dummy'"

    def test_log_file_contains_logs(self):
        assert "logs/" in config.LOG_FILE or "logs\\" in config.LOG_FILE, \
            f"LOG_FILE={config.LOG_FILE!r} should be inside a 'logs/' directory"


class TestConnectionString:
    def test_connection_str_non_empty(self):
        assert isinstance(config.CONNECTION_STR, str)
        assert len(config.CONNECTION_STR) > 0, "CONNECTION_STR must not be empty"

    def test_connection_str_has_protocol(self):
        # Should start with tcp:, udp:, udpin:, udpout:, or serial path
        valid_prefixes = ("tcp:", "udp:", "udpin:", "udpout:", "/dev/")
        assert any(config.CONNECTION_STR.startswith(p) for p in valid_prefixes), \
            f"CONNECTION_STR={config.CONNECTION_STR!r} has unexpected protocol"


class TestLoadKmlZones:
    def test_function_exists(self):
        assert callable(config.load_kml_zones)

    def test_missing_file_returns_false(self):
        result = config.load_kml_zones("nonexistent_file_that_does_not_exist.kml")
        assert result is False

    def test_missing_file_preserves_fallback_search_area(self):
        """When KML is missing, SEARCH_AREA_GPS should keep its fallback value."""
        original = list(config.SEARCH_AREA_GPS)
        config.load_kml_zones("nonexistent_file_that_does_not_exist.kml")
        assert config.SEARCH_AREA_GPS == original

    def test_real_kml_populates_zones(self):
        """If the real KML file exists, load_kml_zones should populate zones."""
        kml_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "flight_plans", "AENGM0074.kml"
        )
        if not os.path.exists(kml_path):
            pytest.skip(f"KML file not found: {kml_path}")

        result = config.load_kml_zones(kml_path)
        assert result is True
        assert len(config.SEARCH_AREA_GPS) >= 3, "KML should populate SEARCH_AREA_GPS"
