# Detection Reliability for Aerial SAR

How to maximize the probability of detecting a casualty/dummy from 20-50 m altitude
with the current hardware and software stack.

**System baseline:**

| Parameter | Value |
|-----------|-------|
| Model | YOLOv8n TFLite, 640x640 input, float32 |
| Training data | 300 synthetic + 16 real + 50 negatives at 1456x1088 |
| mAP50 (validation) | 0.995 |
| Inference | ~206 ms TFLite / ~72 ms NCNN on Pi 5 |
| FPS | 4.8 (TFLite) / 13.8 (NCNN) |
| Confidence threshold | 0.2 |
| Camera | IMX296 global shutter, 1456x1088, HFOV 54.4 deg |
| Detection trigger | Single frame (default) or N-consecutive (--smart-detect) |
| Detection queue | GPS-clustered with 5 m dedup radius |

---

## 1. Model Training Improvements

### 1.1 How Much Real Training Data Is Enough?

The current v2 model has **16 real labelled frames**. This is thin. Empirical guidelines
from YOLO fine-tuning literature:

| Real images | Expected effect |
|:-----------:|-----------------|
| 10-20 | Anchors the model to real sensor characteristics. Current state. |
| 50-100 | Substantial improvement in edge cases (partial occlusion, unusual poses). Sweet spot for a single-class detector. |
| 200-500 | Diminishing returns for a single class on uniform terrain. Worth it if the terrain is varied (woodland, urban, water edge). |
| 1000+ | Only needed for multi-class or highly variable scenes. Overkill for farmland dummy detection. |

**Recommendation:** Collect 50-100 additional real frames during the next flight.
Use `capture_training.py` during manual RC flight, then label with
`tools/label_tool.py --full`. Include:

- Different altitudes (15, 20, 25, 30, 35, 40, 50 m)
- Different lighting (morning, noon, overcast)
- Different poses (supine, prone, fetal, seated)
- Edge cases (half in shadow, near fence, on path edge)
- 30-50 additional negatives from areas that currently cause false positives

### 1.2 Hard Negative Mining

The most sustainable long-term improvement. Each flight makes the model better.

**Process:**
1. During flight, the operator presses X (false positive) in pi_flight.py whenever
   the system triggers on a non-target.
2. Save the raw frame and bounding box crop automatically (add to `capture_training.py`
   or pi_flight.py).
3. After the flight, add these frames to `dataset_v2/images/` as `neg_fp_*.jpg` with
   empty label files.
4. Retrain on Colab. The model learns to suppress site-specific FP patterns (rocks,
   shadows, fence posts, tractor tracks, irrigation marks).

**Expected impact:** 30-50% FP reduction per retraining cycle. After 2-3 cycles, the
model learns the specific visual confusers at the test site.

**Quantitative target:** Collect 20-50 FP crops per flight session. After retraining
with ~100 hard negatives, FP rate should drop from ~5 per scan to ~1-2 per scan.

### 1.3 Test-Time Augmentation (TTA)

Run inference multiple times on transformed versions of the same frame:

| Transform | Cost (ms) | Benefit |
|-----------|:---------:|---------|
| Original | 0 | Baseline |
| Horizontal flip | +206 ms | Catches pose asymmetry bias |
| +/-10% scale | +206 ms each | Catches scale-dependent misses |

TTA doubles or triples inference time. At 4.8 FPS baseline, this drops to 1.6-2.4 FPS.

**Verdict:** Not recommended for real-time search at TFLite speeds. At NCNN speeds
(13.8 FPS), a two-pass TTA (original + flip) drops to ~7 FPS, which is acceptable.
Use TTA only during the VERIFY descent, where the drone is hovering and frame rate
matters less.

**Implementation sketch:**
```python
def detect_with_tta(frame):
    found1, x1, y1, c1 = detect_in_image(frame)
    flipped = cv2.flip(frame, 1)  # horizontal flip
    found2, x2, y2, c2 = detect_in_image(flipped)
    if found2:
        x2 = frame.shape[1] - x2  # un-flip x coordinate
    # Accept if either pass detects
    if c1 >= c2:
        return found1, x1, y1, c1
    return found2, x2, y2, c2
```

### 1.4 Confidence Threshold Tuning

The current threshold of 0.2 is deliberately low. The reasoning: the operator filters
false positives via Y/N/I/X buttons. Missing the actual target is catastrophic; a few
extra FPs are merely annoying.

**How to find the optimal threshold:**

1. Replay DJI flight video through the model at thresholds from 0.1 to 0.9 in steps of 0.05.
2. For each threshold, count true positives (TP) and false positives (FP).
3. Plot a precision-recall curve.
4. Choose the threshold that gives >95% recall with the lowest FP rate.

From the current benchmarks, the model produces detections at 0.966 confidence on the
test image. If real-world detections cluster above 0.8 and FPs cluster below 0.4, a
threshold of 0.3-0.4 would eliminate most FPs without losing any TPs.

**Current evidence suggests 0.2 is too low.** At 0.2, background noise and compression
artefacts can trigger detections. A threshold of 0.25-0.30 would likely eliminate
the noisiest FPs while retaining all real detections (which score >0.8).

**Do not raise above 0.4 without flight data.** At maximum altitude (50 m), the dummy
occupies only ~27 px in frame space (~12 px in model space). Confidence may drop to
0.4-0.6 at that altitude. Raising the threshold above 0.4 risks missing detections at
the altitude ceiling.

### 1.5 Class-Specific Thresholds

Not applicable. The model has a single class ("dummy"). If a multi-class model were
used (e.g., COCO person detector with 80 classes), class-specific thresholds would be
essential -- the "person" class at 0.3 and all others at 0.9 (effectively disabled).

### 1.6 Training Resolution: 640 vs 1088

The v2 model was trained at `imgsz=1088` (native camera resolution) but exported for
inference at 640x640. This is the correct approach:

- **Training at native resolution** lets the model learn features at the actual pixel
  scale it will see in the field. The YOLO training pipeline handles the resize
  internally during augmentation.
- **Inference at 640x640** is the export size and the actual tensor input. Training at
  1088 does not change the inference input size -- it changes what features the model
  learns during training.
- **Training at 640x640** would force the model to learn from pre-downsampled images,
  losing fine detail that may be present in the real camera frames.

Training at higher resolution and inferring at 640 is a well-established pattern (YOLO
documentation recommends `imgsz` at or above camera native resolution during training).
No change needed.

---

## 2. Pre-processing for Better Detection

All preprocessing is in `vision.py` and costs <5 ms total. The key question is whether
any preprocessing improves detection confidence enough to justify the effort.

### 2.1 CLAHE (Contrast Limited Adaptive Histogram Equalization)

CLAHE normalizes local contrast, making targets visible in both shadowed and
sun-bleached regions of the same frame.

```python
def apply_clahe(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
```

**Cost:** ~2-3 ms on Pi 5. **Benefit:** Helps in mixed lighting (half the frame in
shadow, half in sun). Can improve detection confidence by 5-15% in shadowed regions.

**When to use:** Morning/evening flights with long shadows. Not needed at noon with
even lighting. Could be enabled via a config flag.

**Risk:** Can amplify noise in uniformly dark regions. The `clipLimit=2.0` parameter
prevents this for most scenes.

### 2.2 White Balance Correction

Already handled by picamera2 AWB (`CAMERA_AWB_MODE = "auto"` in config.py). The camera
auto-adjusts white balance during the 10-frame warmup. Additional software correction
(`_gray_world()` in vision.py) is available but disabled (`CAMERA_COLOR_CORRECTION = False`).

**Recommendation:** Leave AWB on auto. Only enable gray-world correction if flight
testing reveals persistent color cast (e.g., strong blue sky reflection on wet ground).

### 2.3 Sharpening Filter

A subtle unsharp mask can sharpen edges after resize to 640x640:

```python
def sharpen(frame, amount=0.3):
    blurred = cv2.GaussianBlur(frame, (0, 0), 3)
    return cv2.addWeighted(frame, 1 + amount, blurred, -amount, 0)
```

**Cost:** <1 ms. **Benefit:** Marginal. The resize from 1456x1088 to 640x640 introduces
some softening, but YOLO is trained on resized images and accounts for this. Sharpening
can also amplify JPEG compression artefacts.

**Verdict:** Not recommended for production. Test on flight video first -- if detection
confidence increases measurably (>5%), add it. Otherwise, it adds complexity for no gain.

### 2.4 Contrast Stretching for Hazy Conditions

Simple histogram stretching removes the "washed out" look from fog or haze:

```python
def dehaze_simple(frame):
    for i in range(3):
        lo, hi = np.percentile(frame[:,:,i], (1, 99))
        frame[:,:,i] = np.clip((frame[:,:,i] - lo) * 255.0 / (hi - lo), 0, 255).astype(np.uint8)
    return frame
```

**Cost:** ~1-2 ms. **Benefit:** Useful in foggy/misty conditions where the entire frame
is low contrast. In clear conditions, does nothing (1st and 99th percentiles are already
near 0 and 255).

**Recommendation:** Implement as a config toggle (`CAMERA_DEHAZE = False`). Enable only
if flight testing shows low detection rates in hazy conditions.

### 2.5 Preprocessing Summary

| Technique | Cost (ms) | Default | When to enable |
|-----------|:---------:|:-------:|----------------|
| Lens undistortion | 1.5 | ON | Always (already implemented) |
| CLAHE | 2-3 | OFF | Long shadows, mixed lighting |
| Gray-world AWB | <1 | OFF | Persistent color cast |
| Sharpening | <1 | OFF | Only if measurably helps |
| Contrast stretching | 1-2 | OFF | Haze, fog, mist |

**Total worst-case overhead if all enabled:** ~6 ms (3% of 206 ms inference). Negligible.

---

## 3. Post-processing for Fewer False Positives

See also: `docs/FALSE_POSITIVE_REDUCTION.md` for the full ranked list.

### 3.1 Temporal Filtering (N-of-M Frames)

The single most effective technique. Require N detections within M frames at a
consistent GPS location before triggering investigation.

**Current implementation:** `--smart-detect` flag counts consecutive frames
(`DETECT_CONFIRM_FRAMES = 3`). This is fragile -- a single missed frame resets the
counter. GPS-based clustering (already in pi_flight.py) is more robust.

**Recommended upgrade: sliding window N/M:**

```python
# In state_machine.py _process_detection():
# Maintain a sliding window of the last M frames
# Trigger only if N out of M had a detection within CLUSTER_THRESHOLD_M

TEMPORAL_WINDOW_M = 5    # look at last 5 frames
TEMPORAL_REQUIRED_N = 2  # require 2 hits
CLUSTER_THRESHOLD_M = 5.0  # within 5m GPS radius
```

**Why N=2, M=5 instead of N=3 consecutive:**

At 4.8 FPS and 10 m/s, the drone traverses the dummy's ground footprint (~32 m at
35 m altitude) in ~3.2 seconds = ~15 frames. A true target is visible for 11-17
frames (from VISION_OPTIMIZATION.md Section 6). Requiring only 2 out of 5 is
very achievable for true positives but nearly impossible for random noise (which
is uncorrelated frame-to-frame).

**Expected impact:** 40-60% FP reduction. Transient FPs (single-frame shadow triggers,
sensor noise) are completely eliminated.

### 3.2 Spatial Clustering

Already implemented in pi_flight.py (`_route_to_cluster()` with 5 m dedup radius and
inverse-variance GPS weighting). Detections near the same GPS position are merged into
a single cluster. The operator sees one target, not 15 separate alerts.

**Enhancement:** Weight cluster confidence by detection count:

```python
cluster_confidence = 1 - (1 - avg_conf) ** detection_count
# 3 detections at 0.5 → cluster_confidence = 0.875
# 1 detection at 0.9 → cluster_confidence = 0.900
```

This gives multi-detection clusters higher priority than single high-confidence hits.

### 3.3 Size Filtering (Altitude-Aware)

Reject detections whose bounding box area is inconsistent with a 1.8 m dummy at the
current altitude. This eliminates tiny noise detections and large-scale field patterns.

**Ground truth sizes (frame-space pixels, 1456x1088):**

| Altitude (m) | Expected bbox area (px) | Accept range |
|:------------:|:-----------------------:|:------------:|
| 20 | ~1340 | 400 - 4000 |
| 35 | ~456 | 150 - 1400 |
| 50 | ~216 | 70 - 650 |

Use `GSD = (5.02 * alt) / (5.46 * 1456)` to compute expected size dynamically.
Apply a 3x tolerance band (expected/3 to expected*3) to account for pose variation
and partial visibility.

**Cost:** Zero. Pure arithmetic on existing bbox metadata.

**Expected impact:** 30-50% FP reduction.

### 3.4 Aspect Ratio Filtering

A lying human is roughly 3:1 to 5:1 (length:width). Reject near-square (rocks, dots)
and extremely elongated (tracks, edges) detections.

```python
aspect = max(w, h) / max(min(w, h), 1)
reject = aspect < 1.2 or aspect > 7.0
```

**Expected impact:** 15-25% FP reduction. Especially effective against linear features.

### 3.5 Color Histogram Screening

The dummy has a distinctive color (orange hi-vis clothing). After detection, compute
mean HSV of the cropped bounding box. Reject if the crop is uniformly brown (soil),
green (grass), or grey (rocks).

**Caution:** This is terrain-dependent and assumes knowledge of the dummy's appearance.
In a real SAR scenario with unknown casualty clothing, color filtering would be
disabled. For the competition/assessment with a known dummy, it is a valid optimization.

**Cost:** <1 ms per detection (crop + cvtColor + mean). Only runs when a detection
occurs, not every frame.

**Expected impact:** 20-35% FP reduction on uniform farmland.

---

## 4. Multi-Pass Confirmation (Rescan Strategy)

The system already implements a rescan chain (config.py):

```python
MAX_RESCAN_PASSES = 3
RESCAN_ALT_FACTOR = 0.8    # drop altitude each pass
RESCAN_ALT_FLOOR_M = 15.0  # minimum rescan altitude
```

### 4.1 Two-Threshold Strategy

Use two confidence thresholds to separate detection from confirmation:

| Phase | Threshold | Purpose |
|-------|:---------:|---------|
| Search pass (35 m) | 0.15 | Wide net. Log all candidates. Accept many FPs. |
| Rescan pass | 0.30 | Revisit only candidate locations. Higher bar. |
| Verify hover (15 m) | 0.40 | Close-up confirmation. Operator sees video. |

**Why this works:** At 35 m, the dummy is ~38 px in frame space. Confidence is naturally
lower. A 0.15 threshold catches marginal detections that might be real. During rescan at
a lower altitude (28 m, then 22 m), the dummy is larger and confidence increases. If it
was a false positive (a rock, shadow), the rescan pass will not reproduce the detection.

**Implementation:** The thresholds can be altitude-dependent:

```python
def threshold_for_altitude(alt):
    if alt > 30:
        return 0.15  # high altitude, wide net
    elif alt > 20:
        return 0.25  # mid altitude
    else:
        return 0.35  # low altitude, stricter
```

### 4.2 Candidate List from First Pass

During the search pass, maintain a list of all candidate GPS locations where confidence
exceeded 0.15, even if they were not strong enough to trigger immediate investigation.
After the search pass completes:

1. Cluster candidates spatially (5 m radius).
2. Rank by total detection weight (sum of confidences across all detections in cluster).
3. Rescan visits only the top-N candidate clusters, not the entire search area.

This avoids a full-area rescan (which doubles mission time) in favor of targeted
revisits to promising locations.

---

## 5. Ensemble Methods

### 5.1 YOLO + Simple Color Detector

Run the YOLO model as primary. For each YOLO detection, run a fast color check:

```python
def color_confirms(frame, cx, cy, bw, bh):
    """Check if the detection bbox contains non-background colors."""
    x1 = max(0, cx - bw)
    y1 = max(0, cy - bh)
    x2 = min(frame.shape[1], cx + bw)
    y2 = min(frame.shape[0], cy + bh)
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return True  # can't check, accept
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    # Check for non-green, non-brown pixels (potential dummy)
    non_bg = ((hsv[:,:,0] < 35) | (hsv[:,:,0] > 85)) & (hsv[:,:,1] > 30)
    ratio = non_bg.sum() / max(non_bg.size, 1)
    return ratio > 0.1  # at least 10% non-background pixels
```

**Cost:** <2 ms per detection. Only runs on YOLO-positive frames.

**Expected impact:** 15-25% FP reduction. Rejects detections that are entirely
green/brown (grass/soil patterns that YOLO mistakenly fires on).

### 5.2 Dual YOLO Models

Run two YOLO models and accept only when both agree (IoU > 0.3):

| Option | Models | FPS impact | FP reduction |
|--------|--------|:----------:|:------------:|
| A | YOLOv8n custom + YOLOv8n COCO | 2.4 FPS (TFLite) | 40-60% |
| B | YOLOv8n TFLite + YOLOv8n NCNN | ~4 FPS (interleaved) | 30-50% |

**Verdict:** Option A halves FPS, which is marginal at TFLite speeds. With NCNN
(13.8 FPS), dual-model drops to ~7 FPS, which is acceptable. Option B uses two
different backends on the same model, which provides no diversity benefit.

**Better alternative:** Single model + temporal voting achieves similar FP reduction
without the FPS penalty. Dual models are only justified if temporal voting alone
is insufficient (FP rate still >3 per scan).

### 5.3 YOLO + Motion Detector

Use frame differencing to detect moving objects (or rather, confirm that a detection
is on a static object, since the dummy does not move):

```python
# Compare detection location across 2 frames, compensating for drone motion
# If the ground feature at the detection GPS stays constant → static → possible target
# If the detection only appears in 1 frame → transient → likely FP
```

This is effectively temporal voting (Section 3.1) with explicit motion compensation.

---

## 6. Environmental Robustness

### 6.1 Sun Glare and Shadows

| Condition | Effect on detection | Mitigation |
|-----------|--------------------|----|
| Direct sun glare | Washed-out region, low contrast | CLAHE preprocessing (Section 2.1) |
| Long shadows (morning/evening) | Shadow edges trigger FPs | Aspect ratio filtering rejects linear shadows |
| Dummy in shadow | Lower contrast, confidence drops ~20% | CLAHE + lower threshold |
| Specular reflection (wet ground) | Bright spots, possible FPs | Size filtering (reflections are small) |

### 6.2 Seasonal Variation

| Season | Ground appearance | Impact | Training data coverage |
|--------|-------------------|--------|----------------------|
| Spring | Green grass, mud patches | Best case: high contrast vs dummy | Well covered by synthetic data |
| Summer | Dry grass, brown/yellow | Dummy-ground contrast reduced | Partially covered (DJI video is late winter) |
| Autumn | Mixed leaves, mud | More visual clutter, more FPs | Not covered |
| Winter | Brown/bare, frost | Good contrast | Covered (DJI video is March) |

**Key gap:** Summer dry-grass training data. If the assessment is in summer, collect
training images on dry grass. The orange dummy on brown grass has lower contrast than
on green grass.

### 6.3 Time of Day

| Time | Lighting | Detection impact |
|------|----------|-----------------|
| Early morning (6-8) | Low angle, long shadows | Shadows cause FPs. Lower detection altitude helps. |
| Mid-morning (8-11) | Good, even | Best detection conditions. |
| Noon (11-13) | Harsh, minimal shadows | Good detection. Possible glare. |
| Afternoon (13-16) | Good, lengthening shadows | Similar to mid-morning. |
| Late afternoon (16-18) | Low angle, golden | Shadows return. Color shift may affect AWB. |

**Recommendation:** Schedule flights between 8:00 and 16:00 for best detection
reliability.

### 6.4 How Synthetic Data Handles Environmental Variation

The `generate_dataset_v2.py` script applies:

- Brightness variation: +/-30%
- Contrast variation: +/-20%
- Gaussian blur: sigma 0-2
- Rotation: +/-20 degrees
- Scale variation: simulating 15-50 m altitude

**What it does not cover:**

- Shadows falling on the dummy
- Wet/shiny dummy surface
- Partial occlusion by vegetation
- Camouflage or dark clothing

These gaps are addressed by collecting real training data in varied conditions.

---

## 7. Metrics to Track

### 7.1 Primary Metrics

| Metric | Target | How to measure | Current status |
|--------|:------:|----------------|:--------------:|
| True positive rate (sensitivity) | >95% | TP / (TP + FN) over all frames where dummy is visible | Unknown (no real flight data) |
| False positive rate | <5 per scan | Count FP triggers per complete search pattern | ~5 per scan (estimated from video replay) |
| Detection latency (frames) | <5 frames | Frames from dummy entering FOV to first detection | ~1-3 frames (from video test) |
| Detection altitude ceiling | >35 m with >90% TP rate | Passive flight at increasing altitudes | Unknown (bench test only) |
| GPS estimation error (CEP50) | <3 m | Distance from estimated to known GPS position | 2.3 m (from DJI video analysis) |

### 7.2 Per-Flight Data Collection

After every flight, record:

```
Flight date, time, weather, wind speed
Total scan area (m^2), scan duration (s)
True positives: count, avg confidence, avg altitude, avg distance from target
False positives: count, avg confidence, causes (shadow/rock/track/other)
Missed detections: count, altitude, speed, lighting condition
GPS estimation error: CEP50, CEP95, max error
Detection latency: frames from FOV entry to first detection
```

### 7.3 Derived Metrics

**Frames per target pass:**
At 4.8 FPS, 10 m/s, 35 m altitude (32 m footprint width):
- Time in FOV: 32 / 10 = 3.2 s
- Frames: 3.2 * 4.8 = **15 frames** per pass
- At 6 m/s: 32 / 6 = 5.3 s = **25 frames** per pass

**Single-frame detection probability needed for >95% pass detection:**

If each frame has independent detection probability p, and we need P(at least 1
detection in N frames) > 0.95:

```
P(detect in N frames) = 1 - (1 - p)^N > 0.95
(1 - p)^N < 0.05
p > 1 - 0.05^(1/N)
```

| Frames per pass | Required per-frame p for 95% pass detection |
|:---------------:|:-------------------------------------------:|
| 5 | 0.45 |
| 10 | 0.26 |
| 15 | 0.18 |
| 20 | 0.14 |
| 25 | 0.11 |

With 15 frames per pass, even a per-frame detection rate of 18% guarantees 95%
detection over the entire pass. The current model detects at 0.966 confidence
(effectively 100% per-frame rate on the test image), so we have massive margin.

**The real risk is not per-frame sensitivity but altitude/blur edge cases** where
per-frame detection rate drops to 0-10%. These must be calibrated with real flight
data.

### 7.4 Detection Altitude Ceiling

Expected target size in YOLO input space (640x640) at various altitudes:

| Altitude (m) | Dummy pixels (frame) | Dummy pixels (model input) | Detection likelihood |
|:------------:|:-------------------:|:--------------------------:|:--------------------:|
| 20 | ~67 px tall | ~29 px tall | Very high (>99%) |
| 25 | ~54 px | ~24 px | Very high (>98%) |
| 30 | ~45 px | ~20 px | High (>95%) |
| 35 | ~38 px | ~17 px | High (>90%) |
| 40 | ~33 px | ~15 px | Moderate (70-90%) |
| 50 | ~27 px | ~12 px | Uncertain (50-80%) |

Below ~10 px in model input space, YOLO detection degrades rapidly. The practical
ceiling is likely 40-45 m for reliable detection (>90% per-frame).

**At the configured search altitude of 35 m, the dummy is ~17 px in model space.**
This is above the critical threshold but not by a large margin. If flight testing shows
confidence dropping below 0.5 at 35 m, consider reducing TARGET_ALT to 30 m (where the
dummy is ~20 px, safely above the threshold).

---

## 8. Implementation Priority

Ranked by expected impact per hour of development effort:

| Priority | Technique | Effort | Impact | Section |
|:--------:|-----------|:------:|:------:|:-------:|
| 1 | Size filtering (altitude-aware) | 15 min | High | 3.3 |
| 2 | Aspect ratio filtering | 15 min | Medium | 3.4 |
| 3 | Temporal voting (2/5 sliding window) | 2 hr | Very high | 3.1 |
| 4 | Hard negative mining pipeline | 1 hr setup | High (compounding) | 1.2 |
| 5 | Color confirmation check | 30 min | Medium | 5.1 |
| 6 | Altitude-dependent threshold | 30 min | Medium | 4.1 |
| 7 | CLAHE preprocessing (config toggle) | 15 min | Low-Medium | 2.1 |
| 8 | Collect 50+ real training images | 1 flight | High | 1.1 |
| 9 | TTA during VERIFY only | 1 hr | Low | 1.3 |
| 10 | Dual-model ensemble | 2 hr | Medium | 5.2 |

Items 1-3 should be implemented before the next flight. Items 4-6 should be
implemented after the first flight with real data. Items 7-10 are refinements for
subsequent iterations.

---

## 9. Summary

The detection pipeline has four layers of defense:

```
Layer 1: YOLO inference (low threshold 0.15-0.2, catch everything)
    |
Layer 2: Post-filters (size, aspect ratio, edge proximity, color)
    |
Layer 3: Temporal voting (2/5 frames at consistent GPS location)
    |
Layer 4: Operator confirmation (Y/N/I/X buttons in ground station)
```

Each layer reduces false positives by a multiplicative factor. Layers 1-3 are
automated and run in real time. Layer 4 is the human safety net.

**With all automated layers active, expected FP rate: <1 per scan.**
**True positive rate: >95% for dummy within the detection altitude ceiling (40-45 m).**

The biggest unknowns are altitude-dependent detection rate and site-specific false
positive patterns. Both can only be resolved with real flight data. The system is
designed to improve with each flight through hard negative mining and threshold
calibration.
