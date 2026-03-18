"""
Unit tests for VisionSystem (vision.py).
All tests run without a camera, model file, or any hardware.
"""

import sys
import os
import unittest
import numpy as np

# Add project root to sys.path so we can import vision
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from vision import VisionSystem


class TestVisionSystemCreation(unittest.TestCase):
    """Tests for VisionSystem constructor."""

    def test_create_no_camera(self):
        """camera_index=None should skip camera setup entirely."""
        vs = VisionSystem(camera_index=None, model_path="nonexistent.tflite")
        self.assertIsNone(vs.cap)
        self.assertIsNone(vs._picam)

    def test_missing_model_file(self):
        """A non-existent model path should result in using_ai=False."""
        vs = VisionSystem(camera_index=None, model_path="this_model_does_not_exist.tflite")
        self.assertFalse(vs.using_ai)
        self.assertIsNone(vs.model)

    def test_attributes_initialized(self):
        """Key attributes should be set even when nothing loads."""
        vs = VisionSystem(camera_index=None, model_path="nonexistent.tflite")
        self.assertFalse(vs.using_ai)
        self.assertEqual(vs.last_bbox_w, 0)
        self.assertEqual(vs.last_bbox_h, 0)
        self.assertEqual(vs.last_class_name, "")


class TestDetectInImage(unittest.TestCase):
    """Tests for detect_in_image with no model loaded."""

    def setUp(self):
        self.vs = VisionSystem(camera_index=None, model_path="nonexistent.tflite")

    def test_none_frame_returns_safe_default(self):
        """detect_in_image(None) should return a safe (False, 0, 0, 0.0) tuple."""
        result = self.vs.detect_in_image(None)
        self.assertEqual(result, (False, 0, 0, 0.0))

    def test_no_model_returns_safe_default(self):
        """With no model loaded, any frame should return (False, 0, 0, 0.0)."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.vs.detect_in_image(frame)
        self.assertEqual(result, (False, 0, 0, 0.0))

    def test_output_is_tuple_of_correct_types(self):
        """Return value should be a tuple of (bool, int/number, int/number, float)."""
        result = self.vs.detect_in_image(None)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 4)
        found, x, y, conf = result
        self.assertIsInstance(found, bool)
        self.assertIsInstance(x, (int, float))
        self.assertIsInstance(y, (int, float))
        self.assertIsInstance(conf, float)

    def test_black_frame_no_detection(self):
        """A blank black frame should produce found=False."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        found, x, y, conf = self.vs.detect_in_image(frame)
        self.assertFalse(found)

    def test_random_noise_frame_no_detection(self):
        """Random noise with no model loaded should still return found=False."""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        found, x, y, conf = self.vs.detect_in_image(frame)
        self.assertFalse(found)


class TestProcessFrameManually(unittest.TestCase):
    """process_frame_manually is a thin wrapper around detect_in_image."""

    def test_delegates_to_detect_in_image(self):
        vs = VisionSystem(camera_index=None, model_path="nonexistent.tflite")
        result = vs.process_frame_manually(None)
        self.assertEqual(result, (False, 0, 0, 0.0))


class TestGetFrame(unittest.TestCase):
    """get_frame with no camera should return None."""

    def test_no_camera_returns_none(self):
        vs = VisionSystem(camera_index=None, model_path="nonexistent.tflite")
        self.assertIsNone(vs.get_frame())


class TestUndistort(unittest.TestCase):
    """undistort should pass through when no calibration is loaded."""

    def test_no_calibration_passthrough(self):
        vs = VisionSystem(camera_index=None, model_path="nonexistent.tflite")
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = vs.undistort(frame)
        self.assertIs(result, frame)

    def test_none_frame_passthrough(self):
        vs = VisionSystem(camera_index=None, model_path="nonexistent.tflite")
        result = vs.undistort(None)
        self.assertIsNone(result)


class TestRelease(unittest.TestCase):
    """release should not raise even with no camera."""

    def test_release_no_camera(self):
        vs = VisionSystem(camera_index=None, model_path="nonexistent.tflite")
        vs.release()  # should not raise


if __name__ == "__main__":
    unittest.main()
