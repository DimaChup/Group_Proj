# Undistortion End-to-End Trace: passive_watch.py

## Date: 2026-04-04

## Summary

Traced the entire frame path from video read to browser stream in `passive_watch.py` running in `--fake` mode. Found and fixed two bugs:

1. **Stream showed raw (non-undistorted) frames in fake mode** -- the browser stream never showed lens correction effects
2. **Double undistortion in inference path** -- frames were undistorted twice (once in get_frame()/display loop, again in detect_in_image()), degrading detection accuracy

## Frame Path (BEFORE fix)

### Fake mode (`--fake`)

```
fake_cap.read()            # Line 3173 — raw video frame, NO undistortion
    |
    +--> frame.copy()      # Line 3211 — copied to _inference_frame
    |       |
    |       +--> inference_worker:
    |               det_frame = frame.copy()       # Line 2710
    |               eyes.detect_in_image(det_frame) # Line 2711
    |                   |
    |                   +--> self.undistort(frame)  # vision.py:487 — undistorts HERE
    |                   +--> detection on undistorted copy
    |                   +--> draws bbox on undistorted copy
    |                   (but this copy is NOT what goes to the stream)
    |
    +--> draw_overlay(frame, ...)  # Line 3301 — overlay on RAW frame
    |
    +--> cv2.imencode(display)     # Line 3329 — RAW frame to JPEG
    |
    +--> latest_jpeg = jpg         # Line 3331 — served at /stream
```

**Result**: Browser stream shows RAW frame. Undistortion invisible to user.

### Non-fake mode (camera)

```
camera_source.get_frame()   # Line 3196 — calls self.undistort() internally (vision.py:726)
    |                         returns UNDISTORTED frame
    |
    +--> frame.copy()        # Line 3211 — copied to _inference_frame (already undistorted)
    |       |
    |       +--> inference_worker:
    |               det_frame = frame.copy()
    |               eyes.detect_in_image(det_frame)
    |                   |
    |                   +--> self.undistort(frame)  # vision.py:487 — DOUBLE undistortion!
    |
    +--> draw_overlay(frame, ...)  # Line 3301 — overlay on undistorted frame (correct)
    |
    +--> cv2.imencode(display)     # Line 3329 — undistorted frame to JPEG (correct)
```

**Result**: Browser stream shows undistorted frame (correct), but inference runs on DOUBLE-undistorted frame (bug — distorts detection accuracy).

## Bugs Found

### Bug 1: Fake mode stream shows raw frames

**Location**: `passive_watch.py` display loop, after line 3200 (frame read).

**Cause**: In `--fake` mode, frames are read directly from `cv2.VideoCapture` (line 3173), bypassing `VisionSystem.get_frame()` which normally applies undistortion (vision.py line 726). The raw frame goes straight to `draw_overlay()` and then to the MJPEG stream.

**Impact**: User cannot see lens correction effects in the browser stream when running in fake mode. The undistortion only happens internally in the inference thread on a separate copy of the frame.

### Bug 2: Double undistortion in inference path

**Location**: `vision.py` line 487 (`detect_in_image`) + either `vision.py` line 726 (`get_frame`) or display loop.

**Cause**: `detect_in_image()` always calls `self.undistort(frame)` at line 487. But the frame it receives has ALREADY been undistorted — either by `get_frame()` (non-fake mode) or by the display loop (after fix). This means frames are undistorted twice before inference, which compounds the lens distortion correction and degrades image quality.

**Impact**: Detection accuracy reduced. With mild calibration (RMS 0.399, real values), effect is small. With extreme test values (dist_coeffs=[-1.5, 0.8, 0, 0, -0.3]), the double correction would heavily warp the image.

## Fix Applied

### Fix 1: Undistort fake-mode frames in display loop

Added `camera_source.undistort(frame)` after reading fake video frames (line ~3203):

```python
if args.fake:
    frame = camera_source.undistort(frame)
```

This ensures the stream shows undistorted frames in fake mode, matching non-fake behavior.

### Fix 2: Separate camera_source and inference_eyes from startup

Changed VisionSystem creation (line ~3076) to create separate objects:

```python
# camera_source: owns camera + undistortion maps (for get_frame + display loop)
camera_source = VisionSystem(camera_index=..., model_path=args.model, undistort=True)

# inference_eyes: AI model only, no undistortion (frames arrive pre-undistorted)
eyes = VisionSystem(camera_index=None, model_path=args.model, undistort=False)
```

Also updated model switching code (line ~3229) to pass `undistort=False` to new inference VisionSystem objects.

### Verification

```
camera_source undistort maps loaded: True   (diff sum: 7,650,000 on test frame)
inference_eyes undistort maps loaded: False  (diff sum: 0 — no double undistortion)
```

## Frame Path (AFTER fix)

```
frame read (fake or camera)
    |
    +--> undistort ONCE (by get_frame or explicit call)
    |
    +--> frame.copy() to _inference_frame (already undistorted)
    |       |
    |       +--> eyes.detect_in_image(det_frame)
    |               self.undistort() is NO-OP (maps are None)
    |               detection runs on correctly undistorted frame
    |
    +--> draw_overlay(frame, ...)  # undistorted frame
    |
    +--> cv2.imencode(display)     # undistorted frame to stream
```

## Calibration Data

```
calibration_data.npz:
  dist_coeffs: [-1.5  0.8  0.   0.  -0.3]   (extreme test values)
  image_size:  [1456 1088]
  camera_matrix: [[1416, 0, 728], [0, 1416, 544], [0, 0, 1]]
  rms_error: 0.399
```

```
config.py:
  UNDISTORT_ENABLED = True
```

## Files Modified

- `field_tools/passive_watch.py` — 3 edits (display loop undistort, split camera/inference eyes, model switch undistort=False)

## Files Inspected (not modified)

- `vision.py` — confirmed detect_in_image() calls self.undistort() at line 487, get_frame() at line 726
- `config.py` — confirmed UNDISTORT_ENABLED = True
- `calibration_data.npz` — confirmed extreme test values loaded correctly
