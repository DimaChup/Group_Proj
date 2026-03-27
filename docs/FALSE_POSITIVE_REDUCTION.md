# False Positive Reduction for Aerial SAR Detection

## Context

- **Model**: YOLOv8n (TFLite, float32, 640x640 input) detecting a single lying dummy on farmland
- **Altitude range**: 20-50 m (search at 35 m, verify at 15 m)
- **Camera**: IMX296 global shutter, 1456x1088, HFOV 54.4 deg
- **Inference**: ~206 ms on Pi 5 (4.8 FPS via XNNPACK)
- **Current threshold**: 0.2 (`CONFIDENCE_THRESHOLD` in config.py) -- low by design, operator filters via Y/N/I buttons in pi_flight.py
- **Common false positives**: shadows, rocks, fence posts, tractor tracks, irrigation marks, field boundary patterns
- **Goal**: reduce FP rate from ~5 per scan to <1 per scan without losing true positives

Ground truth for expected dummy size at altitude:

| Altitude (m) | GSD (cm/px) | Dummy (1.8 m) in pixels | BBox area (px) |
|---------------|-------------|-------------------------|-----------------|
| 20            | 2.7         | ~67 px tall             | ~1340           |
| 35            | 4.7         | ~38 px tall             | ~456            |
| 50            | 6.7         | ~27 px tall             | ~216            |

GSD calculated from: `GSD = (SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)` = `(5.02 * alt) / (5.46 * 1456)`.

Note: YOLO resizes to 640x640 internally, so detections are mapped back to frame coordinates. The pixel sizes above are in frame space (1456x1088).

---

## Techniques (ranked by implementation effort)

### Easy (<1 hour)

#### 1. Size filtering

Reject bounding boxes smaller than `MIN_AREA` or larger than `MAX_AREA` pixels for the current altitude. A lying dummy at 35 m occupies roughly 38x13 px (~500 px area). Rocks and fence posts are typically <100 px area; tractor tracks span >2000 px.

**Implementation**: In `vision.py` `detect_in_image()`, after NMS, filter by `w * h` of each detection. Use altitude from telemetry if available, otherwise use a conservative range covering 20-50 m.

```python
# Example thresholds (frame-space pixels, 1456x1088)
MIN_BBOX_AREA = 100    # below this is noise/rocks at any altitude
MAX_BBOX_AREA = 5000   # above this is field patterns/shadows
MIN_BBOX_DIM = 8       # reject if either w or h < 8 px
```

**Expected impact**: 30-50% FP reduction. Eliminates tiny noise detections and large-scale field patterns.

#### 2. Aspect ratio filtering

A lying human body is roughly 3:1 (width:height) to 5:1 depending on pose. A sitting/curled casualty might be closer to 1.5:1. Reject detections that are near-square (1:1) or extremely elongated (>8:1) -- those are typically shadows, lines, or field edges.

**Implementation**: After NMS, compute `aspect = max(w, h) / min(w, h)` and reject if outside `[1.2, 7.0]`.

```python
MIN_ASPECT = 1.2   # reject near-square (rocks, dots)
MAX_ASPECT = 7.0   # reject extreme rectangles (tracks, edges)
```

**Expected impact**: 15-25% FP reduction. Especially effective against linear features (tracks, fences, shadows of posts).

#### 3. Confidence histogram with adaptive threshold

Track the running distribution of confidence scores over the last N frames. If background clutter consistently triggers 0.2-0.3 scores, raise the effective threshold to the 90th percentile of recent background scores. True positives with conf >0.9 will still pass easily.

**Implementation**: Maintain a circular buffer of the last 100 confidence values (all detections including rejected ones). Set `adaptive_thresh = max(CONFIDENCE_THRESHOLD, percentile_90 + 0.05)`.

**Expected impact**: 20-30% FP reduction. Self-calibrates to terrain -- grassy fields need lower adaptation than cluttered farmland with machinery.

#### 4. Edge proximity rejection

Detections at frame edges are often partial objects entering/leaving the FOV. They produce distorted bounding boxes and lower confidence. Reject any detection whose center is within 5% of frame edges.

**Implementation**: Reject if `cx < 0.05 * W` or `cx > 0.95 * W` or `cy < 0.05 * H` or `cy > 0.95 * H`.

**Expected impact**: 10-15% FP reduction. Low but essentially free -- eliminates a class of FPs that are never useful (partial views cannot be confirmed anyway).

---

### Medium (1-4 hours)

#### 5. Temporal voting (GPS-based clustering)

Require a detection to appear in at least 2 out of 5 consecutive frames at a consistent GPS position (within `DETECT_LOCK_RADIUS_M = 5.0 m`). Single-frame spikes from shadows or sensor noise are discarded. This is partially implemented via `DETECT_CONFIRM_FRAMES = 3` in config.py, but currently counts consecutive frames rather than GPS-clustered hits.

**Implementation**: Maintain a sliding window of the last 5 detection GPS estimates. A candidate is promoted to "confirmed" only if 2+ estimates cluster within 5 m radius. Use the existing `GeoTransformer` in `utils.py` for pixel-to-GPS conversion.

**Expected impact**: 40-60% FP reduction. This is the single highest-impact technique because transient FPs (shadows, momentary angle-dependent rock shapes) almost never repeat at the same GPS location across multiple frames.

#### 6. Color histogram screening

Compute the mean HSV color of each detection bounding box. Reject detections whose color profile matches known background: uniform brown (bare soil H=10-25, S<80), uniform green (grass H=35-85, S>40), or uniform grey (rocks/concrete). The dummy is orange/red hi-vis clothing and flesh-toned, which are spectrally distinct from farmland.

**Implementation**: After detection, crop the bbox, convert to HSV, compute mean and std of H/S/V channels. Reject if std_H < 10 (uniform color = background) AND mean hue falls in soil/grass ranges.

```python
# Reject if bbox is uniformly brown soil or green grass
hsv_crop = cv2.cvtColor(bbox_crop, cv2.COLOR_BGR2HSV)
mean_h, mean_s, mean_v = hsv_crop.mean(axis=(0,1))
std_h = hsv_crop[:,:,0].std()
is_uniform = std_h < 10
is_soil = (10 < mean_h < 25) and (mean_s < 80)
is_grass = (35 < mean_h < 85) and (mean_s > 40)
reject = is_uniform and (is_soil or is_grass)
```

**Expected impact**: 20-35% FP reduction. Highly terrain-dependent -- works well on uniform farmland, less useful on mixed terrain with debris.

#### 7. Multi-scale verification (crop-and-rerun)

After initial detection at full frame, crop a 2x-padded region around the bbox, resize it to 640x640, and run inference again. If the second pass does not detect the target, discard. This effectively gives the model a "zoomed in" view, similar to what happens during descent to VERIFY_ALT.

**Implementation**: Crop region = bbox expanded by 2x in each direction (clamped to frame). Resize to 640x640. Run `detect_in_image()` on the crop. Accept only if second pass also detects with conf > 0.3.

**Cost**: Doubles inference time per detection (adds ~206 ms only when a detection occurs, not every frame). At 4.8 FPS with ~5 FPs per scan over ~200 frames, this adds <1 second total per scan.

**Expected impact**: 25-40% FP reduction. Particularly effective because YOLO sees the target at higher effective resolution, which helps distinguish real body shapes from amorphous blobs.

#### 8. Frame differencing for static object confirmation

The dummy is static; shadows rotate slowly; the drone moves, so background shifts between frames. Compare detection locations across 2-3 frames accounting for drone motion (using GPS/heading delta). If the detected object moves with the background (i.e., it is a ground feature incorrectly matched), it is likely a true positive. If it appears in only one frame and vanishes, it is likely noise.

**Implementation**: This overlaps with technique 5 (temporal voting) but adds explicit motion compensation. Store detection GPS coordinates from the last 3 frames. Compute pairwise distances. A static ground target should produce GPS estimates within ~2-3 m of each other (GPS noise floor).

**Expected impact**: 30-40% FP reduction when combined with temporal voting. Marginal if temporal voting is already implemented.

---

### Hard (1+ day)

#### 9. Two-stage detector (YOLO + classifier)

Use YOLO as a proposal generator (keep threshold at 0.2), then pass each cropped proposal through a lightweight binary classifier (MobileNetV3-Small or EfficientNet-Lite0) trained on "dummy vs background" crops. The classifier sees only the cropped region at 224x224 and learns texture/shape features that YOLO misses.

**Implementation**: Train the classifier on cropped detections from existing flight video (true positives from labelled frames, false positives from background crops). Export to TFLite. Add a second inference call in `vision.py` after YOLO NMS.

**Cost**: ~15-30 ms per crop on Pi 5 (MobileNetV3-Small TFLite). With ~2-5 proposals per frame, adds 30-150 ms.

**Expected impact**: 60-80% FP reduction. Industry standard for high-precision detection. The classifier can learn "this is a rock" vs "this is a body" from texture alone.

#### 10. Thermal camera fusion

A thermal camera (e.g., FLIR Lepton 3.5, ~$200) differentiates warm bodies from cold ground. At 35 m, a human body appears as a clear hotspot even when visually camouflaged. Fuse thermal detection with RGB detection: require both modalities to agree.

**Implementation**: Add a second camera to the Pi (USB or I2C thermal module). Run a simple threshold on the thermal image at the RGB detection location. If the thermal reading is within ambient+2C, reject.

**Cost**: Hardware ($200+), calibration, weight on drone, additional processing (~50 ms).

**Expected impact**: 80-95% FP reduction. Thermal is the gold standard for SAR -- almost no ground object mimics a warm body. However, this is out of scope for our current hardware.

#### 11. Ensemble of models

Run two YOLOv8n models trained on different data splits (or one YOLOv8n + one YOLOv8s). Accept only detections where both models agree (IoU > 0.3 between their bboxes). Disagreements are likely FPs triggered by model-specific biases.

**Implementation**: Load two TFLite interpreters in `vision.py`. Run both on each frame. Match detections by IoU. This doubles inference time (~412 ms, 2.4 FPS).

**Expected impact**: 40-60% FP reduction. Effective but the FPS drop to 2.4 may be unacceptable at search speed. Better suited if NCNN or FP16 brings single-model inference under 100 ms first.

#### 12. Hard negative mining + retraining

Collect every false positive from flight testing (the operator presses X in pi_flight.py). Save the frame + bbox. Add these as negative examples in the next training round. This is the most sustainable long-term approach -- each flight makes the model better.

**Implementation**: Already partially supported -- `capture_training.py` saves photos. Add automatic FP crop saving when operator presses X. Accumulate 50-100 FP crops, add to `dataset_v2/`, retrain on Colab.

**Expected impact**: 30-50% FP reduction per retraining cycle, compounding. After 2-3 cycles with real flight data, the model learns site-specific false positive patterns (the specific rocks, shadows, and field features at the test site).

---

## Recommended implementation order for our project

| Priority | Technique | Effort | Expected FP reduction | Cumulative |
|----------|-----------|--------|----------------------|------------|
| 1        | Size filtering (#1) | 15 min | 30-50% | 30-50% |
| 2        | Aspect ratio filtering (#2) | 15 min | 15-25% | 45-65% |
| 3        | Temporal voting (#5) | 2 hr | 40-60% | 75-85% |
| 4        | Edge proximity (#4) | 10 min | 10-15% | 80-90% |
| 5        | Hard negative mining (#12) | ongoing | 30-50% per cycle | 90%+ |

**Notes on the recommended stack:**

- **Keep threshold at 0.2** -- better to catch everything and filter post-detection. Raising the threshold risks missing the dummy at max altitude where confidence drops to 0.3-0.5.
- **Size + aspect ratio first** because they are trivial to implement, have zero computational cost, and eliminate the most obvious FP classes (tiny noise, linear features).
- **Temporal voting is the biggest single win** because it exploits a fundamental property: real targets persist across frames, noise does not. The existing `DETECT_CONFIRM_FRAMES = 3` partially does this but should be upgraded to GPS-based clustering.
- **Hard negative mining is the long game** -- every flight improves the model. Save FP crops automatically when the operator presses X.
- **Skip color histogram and multi-scale verification** unless FP rate remains >1 per scan after the first 4 techniques. They add complexity and terrain-dependent tuning.
- **Two-stage detector (#9) is the nuclear option** -- only pursue if we need guaranteed <0.1 FPs per scan for autonomous operation without operator confirmation.

## Where to implement

All filtering logic should live in `vision.py` (the single CV module) or in a new `detection_filter.py` that `vision.py` calls. No other file should contain detection filtering logic.

```
vision.py::detect_in_image(frame)
  1. YOLO inference (existing)
  2. NMS (existing)
  3. Size filter (new)           ← reject by area
  4. Aspect ratio filter (new)   ← reject by shape
  5. Edge proximity filter (new) ← reject frame edges
  6. Return candidates to caller

Caller (main.py / pi_flight.py):
  7. Temporal voting (new)       ← GPS-cluster across frames
  8. Operator confirmation       ← existing Y/N/I/X buttons
```

Temporal voting belongs in the caller rather than vision.py because it requires GPS state that vision.py intentionally does not have (vision.py is a pure CV module with no MAVLink dependency).
