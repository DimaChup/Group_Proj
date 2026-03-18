"""Unit tests for utils.py — GeoTransformer and overlay_image_alpha."""
import pytest
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import config
from utils import GeoTransformer, overlay_image_alpha


# ---------------------------------------------------------------------------
# GeoTransformer — construction
# ---------------------------------------------------------------------------

class TestGeoTransformerCreation:
    def test_default_map_width(self):
        gt = GeoTransformer(1000)
        expected = 1000 / config.MAP_WIDTH_METERS
        assert gt.pix_per_m == pytest.approx(expected)

    def test_different_map_widths(self):
        gt1 = GeoTransformer(500)
        gt2 = GeoTransformer(2000)
        assert gt2.pix_per_m == pytest.approx(gt1.pix_per_m * 4)

    def test_pix_per_m_positive(self):
        gt = GeoTransformer(800)
        assert gt.pix_per_m > 0


# ---------------------------------------------------------------------------
# GeoTransformer — gps_to_pixels
# ---------------------------------------------------------------------------

class TestGpsToPixels:
    @pytest.fixture
    def gt(self):
        return GeoTransformer(1000)

    def test_reference_point_maps_to_origin(self, gt):
        """The reference GPS coord should map to (0, 0)."""
        x, y = gt.gps_to_pixels(config.REF_LAT, config.REF_LON)
        assert x == 0
        assert y == 0

    def test_north_is_negative_y(self, gt):
        """Moving north (higher lat) should produce negative Y."""
        _, y = gt.gps_to_pixels(config.REF_LAT + 0.001, config.REF_LON)
        assert y < 0, "North (higher latitude) should give negative Y"

    def test_south_is_positive_y(self, gt):
        """Moving south (lower lat) should produce positive Y."""
        _, y = gt.gps_to_pixels(config.REF_LAT - 0.001, config.REF_LON)
        assert y > 0, "South (lower latitude) should give positive Y"

    def test_east_is_positive_x(self, gt):
        """Moving east (higher lon) should produce positive X."""
        x, _ = gt.gps_to_pixels(config.REF_LAT, config.REF_LON + 0.001)
        assert x > 0, "East (higher longitude) should give positive X"

    def test_west_is_negative_x(self, gt):
        """Moving west (lower lon) should produce negative X."""
        x, _ = gt.gps_to_pixels(config.REF_LAT, config.REF_LON - 0.001)
        assert x < 0, "West (lower longitude) should give negative X"

    def test_returns_integers(self, gt):
        x, y = gt.gps_to_pixels(config.REF_LAT + 0.0005, config.REF_LON + 0.0003)
        assert isinstance(x, int)
        assert isinstance(y, int)

    def test_symmetric_east_west(self, gt):
        """Equal east and west offsets should produce equal magnitude X."""
        x_east, _ = gt.gps_to_pixels(config.REF_LAT, config.REF_LON + 0.001)
        x_west, _ = gt.gps_to_pixels(config.REF_LAT, config.REF_LON - 0.001)
        # int() truncation can cause +/-1 difference
        assert abs(abs(x_east) - abs(x_west)) <= 1

    def test_symmetric_north_south(self, gt):
        """Equal north and south offsets should produce equal magnitude Y."""
        _, y_north = gt.gps_to_pixels(config.REF_LAT + 0.001, config.REF_LON)
        _, y_south = gt.gps_to_pixels(config.REF_LAT - 0.001, config.REF_LON)
        # Allow small asymmetry from cos(2*lat) term
        assert abs(abs(y_north) - abs(y_south)) <= 2


# ---------------------------------------------------------------------------
# GeoTransformer — pixels_to_gps
# ---------------------------------------------------------------------------

class TestPixelsToGps:
    @pytest.fixture
    def gt(self):
        return GeoTransformer(1000)

    def test_origin_maps_to_reference(self, gt):
        """Pixel (0,0) should map back to the reference GPS coordinate."""
        lat, lon = gt.pixels_to_gps(0, 0)
        assert lat == pytest.approx(config.REF_LAT, abs=1e-9)
        assert lon == pytest.approx(config.REF_LON, abs=1e-9)

    def test_positive_y_is_south(self, gt):
        """Positive Y pixel should map to lower latitude (south)."""
        lat, _ = gt.pixels_to_gps(0, 100)
        assert lat < config.REF_LAT, "Positive Y should be south (lower lat)"

    def test_negative_y_is_north(self, gt):
        """Negative Y pixel should map to higher latitude (north)."""
        lat, _ = gt.pixels_to_gps(0, -100)
        assert lat > config.REF_LAT, "Negative Y should be north (higher lat)"

    def test_positive_x_is_east(self, gt):
        """Positive X pixel should map to higher longitude (east)."""
        _, lon = gt.pixels_to_gps(100, 0)
        assert lon > config.REF_LON, "Positive X should be east (higher lon)"

    def test_negative_x_is_west(self, gt):
        """Negative X pixel should map to lower longitude (west)."""
        _, lon = gt.pixels_to_gps(-100, 0)
        assert lon < config.REF_LON, "Negative X should be west (lower lon)"


# ---------------------------------------------------------------------------
# GeoTransformer — roundtrip accuracy
# ---------------------------------------------------------------------------

class TestRoundtrip:
    @pytest.fixture
    def gt(self):
        return GeoTransformer(1000)

    def test_roundtrip_gps_pixel_gps(self, gt):
        """GPS -> pixel -> GPS should return close to original (within int truncation)."""
        lat0 = config.REF_LAT + 0.001
        lon0 = config.REF_LON + 0.001
        x, y = gt.gps_to_pixels(lat0, lon0)
        lat1, lon1 = gt.pixels_to_gps(x, y)
        # int() truncation in gps_to_pixels loses sub-pixel precision.
        # At ~1000px map, 1 pixel ~ 0.48m ~ 4.3e-6 deg lat.
        assert lat1 == pytest.approx(lat0, abs=1e-4)
        assert lon1 == pytest.approx(lon0, abs=1e-4)

    def test_roundtrip_pixel_gps_pixel(self, gt):
        """Pixel -> GPS -> pixel should return the same pixel (exact for int coords)."""
        x0, y0 = 200, -150
        lat, lon = gt.pixels_to_gps(x0, y0)
        x1, y1 = gt.gps_to_pixels(lat, lon)
        assert abs(x1 - x0) <= 1
        assert abs(y1 - y0) <= 1

    def test_roundtrip_at_reference(self, gt):
        """Reference point roundtrip should be exact zeros."""
        x, y = gt.gps_to_pixels(config.REF_LAT, config.REF_LON)
        lat, lon = gt.pixels_to_gps(x, y)
        assert lat == pytest.approx(config.REF_LAT, abs=1e-9)
        assert lon == pytest.approx(config.REF_LON, abs=1e-9)

    def test_roundtrip_multiple_offsets(self, gt):
        """Test roundtrip at several different offsets."""
        offsets = [
            (0.0005, 0.0005),
            (-0.001, 0.002),
            (0.002, -0.001),
            (-0.0003, -0.0007),
        ]
        for dlat, dlon in offsets:
            lat0 = config.REF_LAT + dlat
            lon0 = config.REF_LON + dlon
            x, y = gt.gps_to_pixels(lat0, lon0)
            lat1, lon1 = gt.pixels_to_gps(x, y)
            assert lat1 == pytest.approx(lat0, abs=1e-4), f"Roundtrip failed for dlat={dlat}, dlon={dlon}"
            assert lon1 == pytest.approx(lon0, abs=1e-4), f"Roundtrip failed for dlat={dlat}, dlon={dlon}"


# ---------------------------------------------------------------------------
# GeoTransformer — map size scaling
# ---------------------------------------------------------------------------

class TestMapScaling:
    def test_larger_map_gives_more_pixels(self):
        """Doubling map width should double the pixel offset for same GPS delta."""
        gt_small = GeoTransformer(500)
        gt_large = GeoTransformer(1000)
        lat_off = config.REF_LAT + 0.001
        x_s, y_s = gt_small.gps_to_pixels(lat_off, config.REF_LON)
        x_l, y_l = gt_large.gps_to_pixels(lat_off, config.REF_LON)
        # int truncation can cause +/-1 difference
        assert abs(y_l - 2 * y_s) <= 2

    def test_pix_per_m_scales_linearly(self):
        """pix_per_m should scale linearly with map_w_px."""
        gt1 = GeoTransformer(1000)
        gt3 = GeoTransformer(3000)
        assert gt3.pix_per_m == pytest.approx(gt1.pix_per_m * 3)

    def test_small_map(self):
        """Very small map width should still produce valid transformer."""
        gt = GeoTransformer(10)
        assert gt.pix_per_m > 0
        x, y = gt.gps_to_pixels(config.REF_LAT, config.REF_LON)
        assert x == 0 and y == 0


# ---------------------------------------------------------------------------
# GeoTransformer — physical distance sanity checks
# ---------------------------------------------------------------------------

class TestPhysicalDistance:
    def test_100m_north_displacement(self):
        """Moving ~100m north should produce roughly 100m of pixel displacement."""
        gt = GeoTransformer(1000)
        # 1 degree lat ~ 111 km, so 100m ~ 0.0009 degrees
        delta_lat = 100.0 / 111132.954
        _, y = gt.gps_to_pixels(config.REF_LAT + delta_lat, config.REF_LON)
        meters = abs(y) / gt.pix_per_m
        assert meters == pytest.approx(100.0, rel=0.02)  # within 2%

    def test_100m_east_displacement(self):
        """Moving ~100m east should produce roughly 100m of pixel displacement."""
        gt = GeoTransformer(1000)
        lon_m = 111132.954 * math.cos(math.radians(config.REF_LAT))
        delta_lon = 100.0 / lon_m
        x, _ = gt.gps_to_pixels(config.REF_LAT, config.REF_LON + delta_lon)
        meters = abs(x) / gt.pix_per_m
        assert meters == pytest.approx(100.0, rel=0.02)

    def test_lat_meter_factor_reasonable(self):
        """The latitude meter-per-degree factor at Bristol (~51.4N) should be ~111 km."""
        lat = config.REF_LAT
        lat_m = 111132.954 - 559.822 * math.cos(2 * math.radians(lat))
        assert 111000 < lat_m < 112000

    def test_lon_meter_factor_reasonable(self):
        """The longitude meter-per-degree factor at Bristol (~51.4N) should be ~69 km."""
        lat = config.REF_LAT
        lon_m = 111132.954 * math.cos(math.radians(lat))
        assert 68000 < lon_m < 71000


# ---------------------------------------------------------------------------
# overlay_image_alpha — basic behaviour
# ---------------------------------------------------------------------------

class TestOverlayImageAlpha:
    def test_overlay_rgba_on_bgr(self):
        """RGBA overlay with full alpha should overwrite background."""
        bg = np.zeros((100, 100, 3), dtype=np.uint8)
        # 10x10 red overlay with full opacity
        ov = np.zeros((10, 10, 4), dtype=np.uint8)
        ov[:, :, 2] = 255  # red channel (BGR order)
        ov[:, :, 3] = 255  # full alpha
        overlay_image_alpha(bg, ov, 50, 50, 10, 10, rotation_deg=0)
        # Center region should be red
        assert bg[50, 50, 2] == 255  # red channel

    def test_overlay_zero_alpha_no_change(self):
        """RGBA overlay with zero alpha should not modify background."""
        bg = np.full((100, 100, 3), 128, dtype=np.uint8)
        ov = np.zeros((10, 10, 4), dtype=np.uint8)
        ov[:, :, 0:3] = 255
        ov[:, :, 3] = 0  # zero alpha
        overlay_image_alpha(bg, ov, 50, 50, 10, 10)
        # Background should remain 128
        assert bg[50, 50, 0] == 128

    def test_overlay_none_is_noop(self):
        """Passing None overlay should not crash."""
        bg = np.zeros((100, 100, 3), dtype=np.uint8)
        overlay_image_alpha(bg, None, 50, 50, 10, 10)
        # No exception, background unchanged
        assert bg.sum() == 0

    def test_overlay_out_of_bounds_is_safe(self):
        """Overlay placed entirely outside background should not crash."""
        bg = np.zeros((100, 100, 3), dtype=np.uint8)
        ov = np.zeros((10, 10, 4), dtype=np.uint8)
        ov[:, :] = 255
        overlay_image_alpha(bg, ov, -500, -500, 10, 10)
        # No exception, background unchanged
        assert bg.sum() == 0

    def test_overlay_partial_clip(self):
        """Overlay partially outside background should not crash."""
        bg = np.zeros((100, 100, 3), dtype=np.uint8)
        ov = np.zeros((20, 20, 4), dtype=np.uint8)
        ov[:, :, 1] = 200
        ov[:, :, 3] = 255
        # Place at corner so it's partially clipped
        overlay_image_alpha(bg, ov, 5, 5, 20, 20)
        # Should not crash; some green pixels should appear
        assert bg[:, :, 1].max() > 0

    def test_zero_target_dimensions(self):
        """Zero target dimensions should be a no-op (early return)."""
        bg = np.zeros((100, 100, 3), dtype=np.uint8)
        ov = np.zeros((10, 10, 4), dtype=np.uint8)
        ov[:, :] = 255
        overlay_image_alpha(bg, ov, 50, 50, 0, 0)
        assert bg.sum() == 0

    def test_auto_width_from_height(self):
        """When target_w=0, width should be auto-calculated from target_h."""
        bg = np.zeros((200, 200, 3), dtype=np.uint8)
        # 20x10 overlay (w x h), scale to target_h=20 -> target_w should become 40
        ov = np.zeros((10, 20, 4), dtype=np.uint8)
        ov[:, :, 0] = 200
        ov[:, :, 3] = 255
        overlay_image_alpha(bg, ov, 100, 100, 0, 20)
        # Should not crash; some pixels should be modified
        assert bg[:, :, 0].max() > 0

    def test_overlay_bgr_no_alpha(self):
        """3-channel overlay (no alpha) should be direct copy."""
        bg = np.zeros((100, 100, 3), dtype=np.uint8)
        ov = np.full((10, 10, 3), 200, dtype=np.uint8)
        overlay_image_alpha(bg, ov, 50, 50, 10, 10)
        # Center should have been overwritten
        assert bg[50, 50, 0] > 0

    def test_rotation(self):
        """Rotation parameter should not crash and should still place pixels."""
        bg = np.zeros((200, 200, 3), dtype=np.uint8)
        ov = np.zeros((20, 20, 4), dtype=np.uint8)
        ov[:, :, 2] = 255
        ov[:, :, 3] = 255
        overlay_image_alpha(bg, ov, 100, 100, 20, 20, rotation_deg=45)
        assert bg[:, :, 2].max() > 0
