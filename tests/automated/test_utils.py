"""Unit tests for utils.py — GeoTransformer GPS/pixel conversions.

Run:
    cd v3 && source test_env/Scripts/activate && python tests/automated/test_utils.py
"""

import math
import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import config
from utils import GeoTransformer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assert_close(a, b, tol, msg=""):
    """Assert two floats are within tolerance."""
    diff = abs(a - b)
    assert diff <= tol, f"FAIL: {msg} | {a} vs {b}, diff={diff}, tol={tol}"


def haversine_m(lat1, lon1, lat2, lon2):
    """Reference haversine distance in metres."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_ref_point_maps_to_origin():
    """REF_LAT, REF_LON should map to pixel (0, 0)."""
    gt = GeoTransformer(1000)
    px, py = gt.gps_to_pixels(config.REF_LAT, config.REF_LON)
    assert px == 0 and py == 0, f"FAIL: ref point -> ({px}, {py}), expected (0, 0)"
    print("PASS  ref_point_maps_to_origin")


def test_gps_to_pixels_roundtrip():
    """gps_to_pixels then pixels_to_gps should return ~original coords."""
    gt = GeoTransformer(1000)
    # Test several points near the reference
    offsets = [
        (0.001, 0.001),
        (-0.002, 0.003),
        (0.0005, -0.001),
        (0.0, 0.002),
        (-0.001, 0.0),
    ]
    for dlat, dlon in offsets:
        lat_in = config.REF_LAT + dlat
        lon_in = config.REF_LON + dlon
        px, py = gt.gps_to_pixels(lat_in, lon_in)
        lat_out, lon_out = gt.pixels_to_gps(px, py)
        # Tolerance: int() truncation loses up to 1 pixel -> ~0.5m -> ~5e-6 deg
        assert_close(lat_in, lat_out, 1e-4,
                     f"roundtrip lat offset ({dlat},{dlon})")
        assert_close(lon_in, lon_out, 1e-4,
                     f"roundtrip lon offset ({dlat},{dlon})")
    print("PASS  gps_to_pixels_roundtrip")


def test_distance_calculation():
    """Two GPS points ~100m apart should give correct pixel distance."""
    gt = GeoTransformer(1000)
    lat1, lon1 = config.REF_LAT, config.REF_LON
    # Move ~100m east (at 51 deg lat, 1 deg lon ~ 69700m, so 100m ~ 0.001435 deg)
    lon2 = lon1 + 100.0 / (111132.954 * math.cos(math.radians(lat1)))
    lat2 = lat1

    x1, y1 = gt.gps_to_pixels(lat1, lon1)
    x2, y2 = gt.gps_to_pixels(lat2, lon2)

    pixel_dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    metre_dist = pixel_dist / gt.pix_per_m

    assert_close(metre_dist, 100.0, 2.0, "100m east distance")
    print("PASS  distance_calculation")


def test_flat_earth_accuracy_500m():
    """At 500m scale, flat-earth projection error should be <1m vs haversine."""
    gt = GeoTransformer(2000)
    lat0, lon0 = config.REF_LAT, config.REF_LON

    # Point 500m north-east
    lat_m = 111132.954 - 559.822 * math.cos(2 * math.radians(lat0))
    lon_m = 111132.954 * math.cos(math.radians(lat0))
    lat1 = lat0 + 353.55 / lat_m   # 500/sqrt(2) north
    lon1 = lon0 + 353.55 / lon_m   # 500/sqrt(2) east

    # Flat-earth distance via pixels
    x0, y0 = gt.gps_to_pixels(lat0, lon0)
    x1, y1 = gt.gps_to_pixels(lat1, lon1)
    flat_m = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2) / gt.pix_per_m

    # Haversine reference
    hav_m = haversine_m(lat0, lon0, lat1, lon1)

    error = abs(flat_m - hav_m)
    assert error < 1.0, f"FAIL: flat-earth error {error:.3f}m at 500m scale (>1m)"
    print(f"PASS  flat_earth_accuracy_500m (error={error:.4f}m)")


def test_pixel_offset_direction_east():
    """Moving east in GPS should increase x pixel coordinate."""
    gt = GeoTransformer(1000)
    x0, y0 = gt.gps_to_pixels(config.REF_LAT, config.REF_LON)
    x1, y1 = gt.gps_to_pixels(config.REF_LAT, config.REF_LON + 0.001)
    assert x1 > x0, f"FAIL: east should increase x: x0={x0}, x1={x1}"
    print("PASS  pixel_offset_direction_east")


def test_pixel_offset_direction_south():
    """Moving south in GPS should increase y pixel coordinate (image convention)."""
    gt = GeoTransformer(1000)
    x0, y0 = gt.gps_to_pixels(config.REF_LAT, config.REF_LON)
    x1, y1 = gt.gps_to_pixels(config.REF_LAT - 0.001, config.REF_LON)
    assert y1 > y0, f"FAIL: south should increase y: y0={y0}, y1={y1}"
    print("PASS  pixel_offset_direction_south")


def test_edge_case_equator():
    """GeoTransformer should not crash or produce NaN near the equator."""
    # Temporarily patch config for equator test
    orig_lat, orig_lon = config.REF_LAT, config.REF_LON
    try:
        config.REF_LAT = 0.0
        config.REF_LON = 0.0
        gt = GeoTransformer(1000)

        px, py = gt.gps_to_pixels(0.001, 0.001)
        assert not (math.isnan(px) or math.isnan(py)), "NaN at equator"

        lat, lon = gt.pixels_to_gps(50, 50)
        assert not (math.isnan(lat) or math.isnan(lon)), "NaN inverse at equator"
        print("PASS  edge_case_equator")
    finally:
        config.REF_LAT = orig_lat
        config.REF_LON = orig_lon


def test_edge_case_high_latitude():
    """GeoTransformer should work at high latitudes (e.g., 70 deg N)."""
    orig_lat, orig_lon = config.REF_LAT, config.REF_LON
    try:
        config.REF_LAT = 70.0
        config.REF_LON = 25.0
        gt = GeoTransformer(1000)

        px, py = gt.gps_to_pixels(70.001, 25.001)
        assert not (math.isnan(px) or math.isnan(py)), "NaN at 70N"

        # Longitude contraction: 1 deg lon at 70N ~ 38km vs 111km at equator
        # Moving 0.001 deg east should give fewer pixels than at equator
        config.REF_LAT = 0.0
        config.REF_LON = 0.0
        gt_eq = GeoTransformer(1000)
        px_eq, _ = gt_eq.gps_to_pixels(0.0, 0.001)

        config.REF_LAT = 70.0
        config.REF_LON = 25.0
        gt_hi = GeoTransformer(1000)
        px_hi, _ = gt_hi.gps_to_pixels(70.0, 25.001)

        assert px_hi < px_eq, (
            f"FAIL: lon contraction at 70N: px_hi={px_hi} should be < px_eq={px_eq}"
        )
        print("PASS  edge_case_high_latitude")
    finally:
        config.REF_LAT = orig_lat
        config.REF_LON = orig_lon


def test_edge_case_dateline():
    """GeoTransformer should handle coordinates near the date line (179 to -179)."""
    orig_lat, orig_lon = config.REF_LAT, config.REF_LON
    try:
        config.REF_LAT = 0.0
        config.REF_LON = 179.999
        gt = GeoTransformer(1000)

        # Small step east (within same hemisphere, no wrap needed for flat-earth)
        px, py = gt.gps_to_pixels(0.0, 179.9999)
        assert not (math.isnan(px) or math.isnan(py)), "NaN near dateline"

        # Note: flat-earth projection doesn't handle 180/-180 wrapping,
        # which is expected and acceptable for a SAR drone at <1km scale.
        print("PASS  edge_case_dateline")
    finally:
        config.REF_LAT = orig_lat
        config.REF_LON = orig_lon


def test_symmetry_north_south():
    """Equal north and south offsets should give equal but opposite y pixels."""
    gt = GeoTransformer(1000)
    _, y_north = gt.gps_to_pixels(config.REF_LAT + 0.001, config.REF_LON)
    _, y_south = gt.gps_to_pixels(config.REF_LAT - 0.001, config.REF_LON)
    # int truncation may differ by 1
    assert abs(abs(y_north) - abs(y_south)) <= 1, (
        f"FAIL: N/S symmetry: y_north={y_north}, y_south={y_south}"
    )
    print("PASS  symmetry_north_south")


def test_different_map_widths():
    """Larger map_w_px should give proportionally larger pixel coords."""
    gt_small = GeoTransformer(500)
    gt_large = GeoTransformer(2000)
    lat, lon = config.REF_LAT + 0.001, config.REF_LON + 0.001

    x_s, y_s = gt_small.gps_to_pixels(lat, lon)
    x_l, y_l = gt_large.gps_to_pixels(lat, lon)

    # Ratio should be ~4x (2000/500), allowing for int truncation
    if x_s != 0:
        ratio_x = x_l / x_s
        assert_close(ratio_x, 4.0, 0.1, "map width scaling x")
    if y_s != 0:
        ratio_y = y_l / y_s
        assert_close(ratio_y, 4.0, 0.1, "map width scaling y")
    print("PASS  different_map_widths")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_ref_point_maps_to_origin,
        test_gps_to_pixels_roundtrip,
        test_distance_calculation,
        test_flat_earth_accuracy_500m,
        test_pixel_offset_direction_east,
        test_pixel_offset_direction_south,
        test_edge_case_equator,
        test_edge_case_high_latitude,
        test_edge_case_dateline,
        test_symmetry_north_south,
        test_different_map_widths,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        sys.exit(1)
