#!/usr/bin/env python3
"""
Vision Unit Test -- tests VisionSystem without camera or flight hardware.

Verifies model loading, detect_in_image interface, confidence threshold,
pixel coordinate handling, and graceful handling of bad inputs.

Usage:
  python tests/automated/test_vision.py

No SITL, no camera, no flight -- pure vision/AI tests.
"""

import sys
import os
import numpy as np

# Add project root to path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, PROJECT_ROOT)


# -- Test runner (same pattern as geofence_unit_test.py) --------------------

class VisionTestRunner:
    def __init__(self):
        self.results = []

    def record(self, name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        self.results.append((name, passed, detail))
        print(f"  [{status}] {name}" + (f" -- {detail}" if detail else ""))

    def assert_true(self, name, condition, detail=""):
        self.record(name, condition, detail)

    def assert_equal(self, name, actual, expected, detail=""):
        ok = actual == expected
        if not detail:
            detail = f"expected {expected}, got {actual}"
        self.record(name, ok, detail)

    def print_summary(self):
        print("\n" + "=" * 60)
        passed = sum(1 for _, p, _ in self.results if p)
        total = len(self.results)
        print(f"  RESULTS: {passed}/{total} tests passed")
        print("=" * 60)
        for name, ok, detail in self.results:
            status = "PASS" if ok else "FAIL"
            line = f"  [{status}] {name}"
            if detail:
                line += f" -- {detail}"
            print(line)
        print("=" * 60)
        if passed == total:
            print("  ALL TESTS PASSED")
        else:
            print(f"  {total - passed} TEST(S) FAILED")
        print("=" * 60)
        return passed == total


# -- Tests ------------------------------------------------------------------

def test_model_loading(t):
    """VisionSystem loads TFLite model and reports AI ready."""
    print("\n--- Test: Model Loading ---")
    from vision import VisionSystem

    model_path = os.path.join(PROJECT_ROOT, "best.tflite")
    t.assert_true("best.tflite exists", os.path.exists(model_path),
                  f"path: {model_path}")

    vs = VisionSystem(camera_index=None, model_path=model_path, undistort=False)
    t.assert_true("using_ai is True", vs.using_ai)
    t.assert_true("model is not None", vs.model is not None)
    t.assert_true("backend is tflite or ultralytics",
                  vs.backend_name in ("tflite", "ultralytics", "ncnn"),
                  f"backend={vs.backend_name}")


def test_missing_model(t):
    """VisionSystem handles missing model gracefully (no crash)."""
    print("\n--- Test: Missing Model ---")
    from vision import VisionSystem

    vs = VisionSystem(camera_index=None, model_path="nonexistent_model.tflite",
                      undistort=False)
    t.assert_true("using_ai is False for missing model", not vs.using_ai)
    t.assert_true("model is None for missing model", vs.model is None)
    t.assert_equal("backend is none", vs.backend_name, "none")


def test_detect_returns_correct_format(t):
    """detect_in_image returns a 4-tuple of (bool, int, int, float)."""
    print("\n--- Test: Return Format ---")
    from vision import VisionSystem

    model_path = os.path.join(PROJECT_ROOT, "best.tflite")
    vs = VisionSystem(camera_index=None, model_path=model_path, undistort=False)

    # Use a blank frame -- should return no detection but correct format
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = vs.detect_in_image(frame)

    t.assert_true("result is a tuple", isinstance(result, tuple))
    t.assert_equal("result has 4 elements", len(result), 4)

    found, cx, cy, conf = result
    t.assert_true("found is bool", isinstance(found, (bool, np.bool_)),
                  f"type={type(found).__name__}")
    t.assert_true("cx is int-like", isinstance(cx, (int, np.integer)),
                  f"type={type(cx).__name__}")
    t.assert_true("cy is int-like", isinstance(cy, (int, np.integer)),
                  f"type={type(cy).__name__}")
    t.assert_true("conf is float-like", isinstance(conf, (float, np.floating)),
                  f"type={type(conf).__name__}")


def test_confidence_threshold(t):
    """Detections below the confidence threshold are filtered out."""
    print("\n--- Test: Confidence Threshold ---")
    from vision import VisionSystem, DEFAULT_CONF_THRESHOLD

    model_path = os.path.join(PROJECT_ROOT, "best.tflite")
    vs = VisionSystem(camera_index=None, model_path=model_path, undistort=False)

    t.assert_true("conf threshold is set", vs._conf_thresh > 0,
                  f"threshold={vs._conf_thresh}")
    t.assert_true("conf threshold is reasonable (0 < t < 1)",
                  0 < vs._conf_thresh < 1,
                  f"threshold={vs._conf_thresh}")

    # Test _pick_best_detection with synthetic predictions
    # Format: [cx, cy, bw, bh, class0_conf]
    # All below threshold
    preds_low = np.array([
        [0.5, 0.5, 0.1, 0.1, 0.1],   # conf 0.1 -- below threshold
        [0.3, 0.3, 0.1, 0.1, 0.05],   # conf 0.05 -- below threshold
    ])
    best_conf, best_det = vs._pick_best_detection(preds_low)
    t.assert_true("low-conf detections filtered", best_det is None,
                  f"best_conf={best_conf}")

    # One above threshold
    preds_high = np.array([
        [0.5, 0.5, 0.1, 0.1, 0.1],   # below threshold
        [0.3, 0.3, 0.1, 0.1, 0.9],   # above threshold
    ])
    best_conf, best_det = vs._pick_best_detection(preds_high)
    t.assert_true("high-conf detection accepted", best_det is not None,
                  f"best_conf={best_conf}")
    t.assert_true("correct conf returned", abs(best_conf - 0.9) < 0.01,
                  f"expected ~0.9, got {best_conf}")


def test_pixel_coord_threshold(t):
    """PIXEL_COORD_THRESHOLD distinguishes pixel coords from normalised."""
    print("\n--- Test: Pixel Coordinate Threshold ---")
    from vision import PIXEL_COORD_THRESHOLD

    t.assert_true("threshold is positive", PIXEL_COORD_THRESHOLD > 0,
                  f"value={PIXEL_COORD_THRESHOLD}")
    t.assert_true("threshold separates normalised from pixel",
                  PIXEL_COORD_THRESHOLD > 1.0,
                  "values > 1.0 are pixel coords, <= 1.0 are normalised")

    # Normalised coords (0-1 range) should be below threshold
    t.assert_true("0.5 is normalised", 0.5 < PIXEL_COORD_THRESHOLD)
    t.assert_true("1.0 is normalised", 1.0 < PIXEL_COORD_THRESHOLD)

    # Pixel coords (e.g. 320, 240) should be above threshold
    t.assert_true("320 is pixel coord", 320 > PIXEL_COORD_THRESHOLD)
    t.assert_true("2.0 is pixel coord", 2.0 > PIXEL_COORD_THRESHOLD)


def test_none_frame(t):
    """detect_in_image(None) returns gracefully without crash."""
    print("\n--- Test: None Frame ---")
    from vision import VisionSystem

    model_path = os.path.join(PROJECT_ROOT, "best.tflite")
    vs = VisionSystem(camera_index=None, model_path=model_path, undistort=False)

    result = vs.detect_in_image(None)
    t.assert_true("no crash on None", True)
    found, cx, cy, conf = result
    t.assert_true("found is False for None frame", not found)
    t.assert_equal("cx is 0 for None frame", cx, 0)
    t.assert_equal("cy is 0 for None frame", cy, 0)
    t.assert_true("conf is 0.0 for None frame", conf == 0.0,
                  f"conf={conf}")


def test_empty_frame(t):
    """detect_in_image on a black frame does not crash."""
    print("\n--- Test: Empty (Black) Frame ---")
    from vision import VisionSystem

    model_path = os.path.join(PROJECT_ROOT, "best.tflite")
    vs = VisionSystem(camera_index=None, model_path=model_path, undistort=False)

    # Small frame
    frame_small = np.zeros((100, 100, 3), dtype=np.uint8)
    result = vs.detect_in_image(frame_small)
    t.assert_true("no crash on 100x100 black frame", True)
    found, cx, cy, conf = result
    t.assert_true("result is valid tuple (small)", isinstance(found, (bool, np.bool_)))

    # Standard frame
    frame_std = np.zeros((480, 640, 3), dtype=np.uint8)
    result2 = vs.detect_in_image(frame_std)
    t.assert_true("no crash on 640x480 black frame", True)
    found2, _, _, _ = result2
    t.assert_true("result is valid tuple (standard)", isinstance(found2, (bool, np.bool_)))

    # Large frame (Pi native resolution)
    frame_large = np.zeros((1088, 1456, 3), dtype=np.uint8)
    result3 = vs.detect_in_image(frame_large)
    t.assert_true("no crash on 1456x1088 black frame", True)


def test_backend_detection(t):
    """Correct backend is selected based on available packages."""
    print("\n--- Test: Backend Detection ---")
    from vision import VisionSystem, TFLiteInterpreter, YOLO

    model_path = os.path.join(PROJECT_ROOT, "best.tflite")
    vs = VisionSystem(camera_index=None, model_path=model_path, undistort=False)

    # For .tflite files, Ultralytics is explicitly skipped (broken bbox coords)
    # So backend should be tflite (or ncnn if requested)
    t.assert_true("backend is tflite for .tflite model",
                  vs.backend_name == "tflite",
                  f"backend={vs.backend_name}")

    if TFLiteInterpreter is not None:
        t.assert_true("TFLite interpreter available", True)
        t.assert_true("_use_tflite_direct is True", vs._use_tflite_direct)
    else:
        t.assert_true("TFLite interpreter not available (expected on some systems)",
                      True, "skipped")

    # Verify Ultralytics is skipped for .tflite
    t.assert_true("Ultralytics skipped for .tflite",
                  vs.backend_name != "ultralytics" or not model_path.endswith('.tflite'),
                  "Ultralytics has broken bbox coords for .tflite models")


def test_undistort_disabled(t):
    """VisionSystem with undistort=False has no remap matrices."""
    print("\n--- Test: Undistort Disabled ---")
    from vision import VisionSystem

    model_path = os.path.join(PROJECT_ROOT, "best.tflite")
    vs = VisionSystem(camera_index=None, model_path=model_path, undistort=False)

    t.assert_true("undistort map1 is None", vs._undistort_map1 is None)
    t.assert_true("undistort map2 is None", vs._undistort_map2 is None)

    # undistort() should return frame unchanged
    frame = np.ones((100, 100, 3), dtype=np.uint8) * 128
    result = vs.undistort(frame)
    t.assert_true("undistort returns same frame",
                  result is frame, "should be identity when disabled")


def test_no_ai_detect(t):
    """detect_in_image returns (False, 0, 0, 0.0) when no model loaded."""
    print("\n--- Test: No AI Detection ---")
    from vision import VisionSystem

    vs = VisionSystem(camera_index=None, model_path="nonexistent.tflite",
                      undistort=False)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = vs.detect_in_image(frame)
    found, cx, cy, conf = result
    t.assert_true("found is False", not found)
    t.assert_equal("cx is 0", cx, 0)
    t.assert_equal("cy is 0", cy, 0)
    t.assert_true("conf is 0.0", conf == 0.0)


def test_constants(t):
    """Vision module constants have expected values."""
    print("\n--- Test: Constants ---")
    from vision import (YOLO_INPUT_SIZE, PIXEL_COORD_THRESHOLD,
                        DEFAULT_CONF_THRESHOLD, DEFAULT_CAM_W, DEFAULT_CAM_H)

    t.assert_equal("YOLO input size", YOLO_INPUT_SIZE, 640)
    t.assert_true("PIXEL_COORD_THRESHOLD > 1", PIXEL_COORD_THRESHOLD > 1.0,
                  f"value={PIXEL_COORD_THRESHOLD}")
    t.assert_true("default conf threshold in (0,1)",
                  0 < DEFAULT_CONF_THRESHOLD < 1,
                  f"value={DEFAULT_CONF_THRESHOLD}")
    t.assert_equal("default cam width", DEFAULT_CAM_W, 640)
    t.assert_equal("default cam height", DEFAULT_CAM_H, 480)


def test_store_bbox_metadata(t):
    """_store_bbox_metadata correctly identifies single vs multi-class."""
    print("\n--- Test: BBox Metadata ---")
    from vision import VisionSystem

    model_path = os.path.join(PROJECT_ROOT, "best.tflite")
    vs = VisionSystem(camera_index=None, model_path=model_path, undistort=False)

    # Single class model: det has 5 values (cx, cy, bw, bh, conf)
    det_single = np.array([0.5, 0.5, 0.1, 0.1, 0.9])
    vs._store_bbox_metadata(det_single, 50, 50)
    t.assert_equal("single class name", vs.last_class_name, "dummy")
    t.assert_equal("bbox width stored", vs.last_bbox_w, 50)
    t.assert_equal("bbox height stored", vs.last_bbox_h, 50)

    # Multi class model: det has more than 5 values
    det_multi = np.array([0.5, 0.5, 0.1, 0.1, 0.9, 0.1, 0.05])
    vs._store_bbox_metadata(det_multi, 80, 120)
    t.assert_true("multi class name is string", isinstance(vs.last_class_name, str))
    t.assert_equal("bbox width updated", vs.last_bbox_w, 80)
    t.assert_equal("bbox height updated", vs.last_bbox_h, 120)


# -- Main -------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  VISION UNIT TESTS")
    print("=" * 60)

    t = VisionTestRunner()

    test_constants(t)
    test_model_loading(t)
    test_missing_model(t)
    test_backend_detection(t)
    test_detect_returns_correct_format(t)
    test_confidence_threshold(t)
    test_pixel_coord_threshold(t)
    test_none_frame(t)
    test_empty_frame(t)
    test_undistort_disabled(t)
    test_no_ai_detect(t)
    test_store_bbox_metadata(t)

    all_passed = t.print_summary()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
