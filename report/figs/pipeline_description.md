# Detection-to-GPS Pipeline Flowchart Description

This document describes the full data-flow from raw camera frame to estimated target
GPS coordinate.  Use it to generate a vertical pipeline/flowchart figure for the report.

---

## Pipeline Stages

### Stage 1 — Image Acquisition

```
[Pi Camera IMX296 (Global Shutter)]
  Output: 1456 x 1088 px, BGR uint8
  Note: sensor labels output "RGB888" but data is actually BGR; no cvtColor needed
```

**Error contribution:** pixel noise +/-2 px (sensor read noise + quantisation)

---

### Stage 2 — Lens Undistortion (optional)

```
[Lens Undistortion]
  Method: cv2.remap() with precomputed maps from calibration_data.npz
  Model: cv2.getOptimalNewCameraMatrix() + cv2.initUndistortRectifyMap()
  Cost: ~1.5 ms per frame
  Condition: skipped if calibration_data.npz does not exist or is corrupt
  Calibration: checkerboard (14x9 board, 13x8 inner corners, 28 mm squares), RMS = 0.399 px
```

**Error contribution:** 0 if applied correctly; IMX296 distortion is minimal (global shutter,
low distortion lens), so skipping adds <1 px error at image edges.

---

### Stage 3 — Resize to Model Input

```
[Resize to 640 x 640]
  Method: cv2.resize(frame, (640, 640))
  Mapping: squish (non-uniform scale), no letterboxing
  Scale factors: sx = 640/1456 = 0.4396, sy = 640/1088 = 0.5882
```

**Error contribution:** 0 (exact inverse mapping applied when rescaling coordinates back)

---

### Stage 4 — Colour Conversion + Normalisation

```
[BGR -> RGB + Float32 Normalisation]
  cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  img = img.astype(np.float32) / 255.0
  Output shape: [1, 640, 640, 3] (batch dimension added)
  dtype: float32, range [0.0, 1.0]
```

**Error contribution:** 0 (lossless transformation)

Note: NCNN backend uses ncnn.Mat.from_pixels with substract_mean_normalize([0,0,0],
[1/255, 1/255, 1/255]) instead of explicit cvtColor, achieving the same result.

---

### Stage 5 — YOLOv8n Inference

```
[YOLOv8n Neural Network]
  Architecture: YOLOv8-nano (3.2 M parameters, 8.7 GFLOPs)
  Model: best.tflite (custom SAR dummy detector, retrained on 366 images)
  Training: 300 synthetic + 16 real + 50 negative images at 1456x1088, mAP50 = 0.995
  Input:  [1, 640, 640, 3] float32
  Output: [1, 5, 8400] float32  (1-class model: cx, cy, w, h, conf per anchor)
          or [1, 9, 8400] for 5-class model (dummy, pants, tshirt, backpack, cone)

  Backend performance (Raspberry Pi 5, ARM Cortex-A76):
    TFLite (XNNPACK CPU): 207 ms / 4.8 FPS
    NCNN (ARM NEON):       72 ms / 9.0 FPS (full pipeline including pre/post-processing)
```

**Error contribution:** bounding box regression +/-3 px (in 640x640 model space)

---

### Stage 6 — NMS + Best Detection Selection

```
[Post-Processing: Threshold + Best Pick]
  1. Transpose output: [1, 5, 8400] -> [8400, 5]
     Each row = [cx, cy, w, h, class_score]
  2. For each of 8400 anchor predictions:
       class_id = argmax(scores[4:])
       conf = scores[4 + class_id]
  3. Filter: keep only detections where conf > CONFIDENCE_THRESHOLD (0.2)
  4. Pick: select single detection with highest confidence
  Output: (raw_cx, raw_cy, raw_w, raw_h, conf) in model-space pixels [0-640]
```

**Error contribution:** threshold too low -> false positives; too high -> missed detections.
Current threshold 0.2 is deliberately low; operator confirms via VERIFY state.

---

### Stage 7 — Coordinate Rescale to Original Frame

```
[Coordinate Rescale: 640x640 -> 1456x1088]
  cx = raw_cx * (1456 / 640)  =  raw_cx * 2.275
  cy = raw_cy * (1088 / 640)  =  raw_cy * 1.700
  bw = raw_w  * (1456 / 640)
  bh = raw_h  * (1088 / 640)

  Note: code checks PIXEL_COORD_THRESHOLD (1.5) to distinguish pixel coords
  from normalised [0,1] coords.  If raw_cx > 1.5 -> pixel coords (multiply by
  frame_w / input_w); otherwise -> normalised (multiply by frame_w directly).
```

**Error contribution:** +/-3 px model error * 2.275 scale = +/-6.8 px in frame coords.

---

### Stage 8 — Pixel Offset from Image Centre

```
[Pixel Offset Calculation]
  delta_x_px = cx - (IMAGE_W / 2)  =  cx - 728
  delta_y_px = cy - (IMAGE_H / 2)  =  cy - 544

  Positive delta_x = target is RIGHT of centre
  Positive delta_y = target is BELOW centre
```

Source: `gps_utils.py:98-99`

---

### Stage 9 — Ground Sample Distance (GSD)

```
[GSD Calculation]
  GSD = (SENSOR_WIDTH_MM * altitude) / (FOCAL_LENGTH_MM * IMAGE_W)
  GSD = (5.02 mm * alt_m) / (5.46 mm * 1456 px)

  Example values:
    alt = 20 m  ->  GSD = 0.01263 m/px  (FOV = 18.4 m x 13.7 m)
    alt = 35 m  ->  GSD = 0.02210 m/px  (FOV = 32.2 m x 24.0 m)
    alt = 50 m  ->  GSD = 0.03157 m/px  (FOV = 46.0 m x 34.3 m)
```

Source: `gps_utils.py:95`

**Error contribution:** altitude uncertainty +/-0.5-1.0 m (barometric drift) causes
+/-1.4-2.9% GSD error.  At 35 m with 10 m pixel offset -> +/-0.3-0.6 m position error.

---

### Stage 10 — Offset in Metres (Camera Frame)

```
[Camera-Frame Offset]
  fwd_m   = -delta_y_px * GSD   (forward = UP in image = negative delta_y)
  right_m =  delta_x_px * GSD   (right = positive delta_x)

  Sign convention:
    fwd_m  > 0  ->  target is AHEAD of drone (above centre in image)
    right_m > 0 ->  target is RIGHT of drone
```

Source: `gps_utils.py:101-103`

---

### Stage 11 — Rotate by Drone Yaw (Camera -> NED Frame)

```
[Yaw Rotation: Camera Frame -> North/East]
  offset_north = fwd_m * cos(yaw) - right_m * sin(yaw)
  offset_east  = fwd_m * sin(yaw) + right_m * cos(yaw)

  yaw: drone heading in radians (0 = North, positive clockwise)
  Source: MAVLink ATTITUDE message, field: yaw
```

Source: `gps_utils.py:106-107`

**Error contribution:** compass accuracy +/-1-2 degrees.
At 10 m offset -> sin(2 deg) * 10 m = +/-0.35 m cross-track error.

**NOT COMPENSATED:** Roll and pitch tilt the camera off-nadir. During forward flight at
5 m/s, typical pitch is ~5 deg, shifting the image footprint forward by
alt * tan(5 deg) = 35 * 0.087 = 3.1 m.  During hover (centering/verify) pitch is <1 deg
-> <0.6 m error.  Roll is typically <2 deg -> <1.2 m.  Combined max during flight: ~6 m.

---

### Stage 12 — GPS Offset (Metres -> Lat/Lon)

```
[Spherical Projection: NED Metres -> WGS-84 Degrees]
  d_lat = (offset_north / R_EARTH) * (180 / pi)
  d_lon = (offset_east / (R_EARTH * cos(lat_rad))) * (180 / pi)

  target_lat = drone_lat + d_lat
  target_lon = drone_lon + d_lon

  R_EARTH = 6,378,137 m (WGS-84 semi-major axis)
  At Bristol (lat 51.4 deg):
    1 deg lat = 111,320 m
    1 deg lon = 111,320 * cos(51.4 deg) = 69,532 m
```

Source: `gps_utils.py:110-113`

**Error contribution:** drone GPS position uncertainty +/-2-3 m (civilian GNSS).
This is the DOMINANT error source and applies as a direct offset to every estimate.

---

### Stage 13 — GPS Timing Lag Compensation

```
[GPS Timing Lag]
  GPS receiver latency: ~100-200 ms
  At search speed 5 m/s -> drone moves 0.5-1.0 m between GPS fix and image capture
  Effect: systematic offset along flight direction
  Status: NOT compensated in current code
  Mitigation: averaging from multiple passes (different headings) cancels directional bias
```

---

### Stage 14 — Detection Validation Filters

```
[Validation Filters]
  1. NFZ check: is target_lat/lon inside SSSI no-fly zone?  -> REJECT
  2. Search area check: is target_lat/lon outside search polygon? -> REJECT
  3. Duplicate check: is target_lat/lon within REJECTED_TARGET_RADIUS_M
     of any previously rejected, IOI, or queued target? -> REJECT
  4. SMART detect (optional, --smart-detect flag):
     Require DETECT_CONFIRM_FRAMES (3) consecutive frames with detections
     before accepting.  Resets count on any frame without detection.
```

Source: `state_machine.py:406-438`

---

### Stage 15 — Detection Queue + State Transition

```
[Detection Queue -> CENTERING]
  Valid detection -> enqueue (lat, lon, conf) in _detect_queue (max 20 entries)
  When SEARCH state checks queue:
    Pop oldest valid target -> set target_lat/lon -> transition to CENTERING
  CENTERING state:
    Fly toward target GPS, re-detect with live CV, lock target position
    Optional GPS averaging (--center-verify): collect N position estimates,
    inverse-variance weighted mean -> refined target_lat/lon
  Then -> DESCENDING -> VERIFY (operator Y/N) -> APPROACH -> LANDING
```

---

## Error Budget Summary

| Source                        | Magnitude        | Type         | When          |
|-------------------------------|------------------|-------------|---------------|
| Sensor pixel noise            | +/-2 px          | Random      | Always        |
| Model bbox regression         | +/-3 px (at 640) | Random      | Always        |
| Coordinate rescale            | +/-6.8 px (at 1456) | Random   | Always        |
| GSD (altitude uncertainty)    | +/-1.4-2.9%      | Systematic  | Always        |
| Compass / yaw                 | +/-0.35 m        | Random      | Always        |
| Roll/pitch (not compensated)  | 0-6 m            | Systematic  | Flight only   |
| Drone GPS position            | +/-2-3 m         | Random      | Always        |
| GPS timing lag                | ~0.5-1.0 m       | Systematic  | Flight only   |
| **Combined (hover)**          | **+/-2.5-4 m**   |             | Centering     |
| **Combined (flight at 5 m/s)**| **+/-4-8 m**     |             | Search pass   |

**Measured performance (DJI flight video analysis):**
  CEP50 = 2.3 m (50% of estimates within 2.3 m of true position)
  Max error = 16.5 m (outlier during high-speed turn)

---

## Flowchart Layout Suggestion

Draw as a vertical pipeline with boxes for each stage.  Left side: data shape/format
annotations.  Right side: error contributions.  Use colour coding:

- **Blue boxes:** Image processing stages (1-4)
- **Green box:** Neural network inference (5)
- **Orange boxes:** Post-processing + coordinate maths (6-12)
- **Red boxes:** Validation + state machine (13-15)
- **Grey side-annotations:** Error magnitudes

Key branch points to show:
- Stage 2: diamond "calibration_data.npz exists?" -> Yes: undistort / No: skip
- Stage 6: diamond "conf > 0.2?" -> Yes: continue / No: discard (no detection)
- Stage 14: diamond "passes all filters?" -> Yes: enqueue / No: reject

Input annotations (left side):
- Drone telemetry feeds into stages 9 (altitude), 11 (yaw), 12 (lat/lon/R_EARTH)
- Config parameters feed into stage 9 (SENSOR_WIDTH_MM, FOCAL_LENGTH_MM)

Output:
- Final box: "Target GPS Estimate (lat, lon)" with CEP50 = 2.3 m annotation
