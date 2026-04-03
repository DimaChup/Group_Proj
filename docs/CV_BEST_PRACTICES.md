# CV Best Practices — Aerial SAR Dummy Detection

Reference document for all future YOLOv8n model training on this project.
Compiled from research and experimentation across sessions.

For step-by-step retraining workflow, see `docs/TRAINING_GUIDE.md`.

---

## 1. Data Augmentation Ranking (by impact for aerial SAR)

Ranked by how much each augmentation improves real-world aerial detection performance.

| Rank | Augmentation | Why it matters for aerial SAR | YOLO config |
|------|-------------|------------------------------|-------------|
| 1 | **Motion blur** | Drone movement at 5 m/s causes directional blur, especially at low altitude. This is the #1 failure mode in real flights. | Custom in `generate_dataset_v2.py` (kernel size 5-15px, random angle) |
| 2 | **Color/brightness jitter** | Lighting changes drastically between morning/afternoon/cloud cover. Dummy appearance shifts with sun angle. | `hsv_h=0.015, hsv_s=0.7, hsv_v=0.4` (YOLO defaults) |
| 3 | **Gaussian noise** | Camera sensor noise increases at high shutter speeds (needed to reduce motion blur). Pi IMX296 global shutter has moderate noise. | Custom in dataset generator (sigma 5-20) |
| 4 | **Shadow overlays** | Trees, buildings, and the drone itself cast shadows. Dummy in shadow looks very different from dummy in sun. | Custom: composite dark rectangles/circles on background before placing dummy |
| 5 | **Perspective transforms** | Drone is rarely perfectly nadir. 5-15 degree tilt is normal, more during wind gusts or manoeuvres. | `degrees=5, perspective=0.0005` |
| 6 | **Random erasing** | Partial occlusion by vegetation, debris, or shadow edges. Forces model to detect from partial features. | `erasing=0.3` |
| 7 | **Copy-paste** | Places object instances onto new backgrounds. Useful when real labelled images are scarce. | `copy_paste=0.1` (YOLO built-in) |
| 8 | **Fog/haze** | UK weather. Reduces contrast and color saturation. Simulated by blending frame toward grey. | Custom: `frame = cv2.addWeighted(frame, alpha, grey, 1-alpha, 0)` with alpha 0.7-0.9 |

**Key insight**: Motion blur and brightness jitter together cover 70%+ of real-world failure cases. Prioritise these over exotic augmentations.

---

## 2. Dataset Composition Guidelines

### Minimum sizes

| Dataset size | Expected result |
|-------------|----------------|
| < 200 images | Underfitting, poor generalisation |
| 200-500 | Works for single class if augmentation is aggressive |
| **500-1000** | **Recommended minimum for single-class aerial detection** |
| 1000+ | Diminishing returns unless adding diverse real data |

### Composition ratios

| Component | Ratio | Notes |
|-----------|-------|-------|
| Synthetic images | 50-75% | Generated from `generate_dataset_v2.py`. Cheap to produce. |
| **Real labelled images** | **25-50%** | From flight video via `tools/label_tool.py --full`. Most impactful addition. |
| **Negatives (no target)** | **15-25%** | Empty label files. Reduces false positives on grass, rocks, shadows. |
| Hard negatives | 5-10% (subset of negatives) | Frames where the model previously made false positive detections. |

### Current dataset (v2): 366 images

- 300 synthetic, 16 real, 50 negatives
- Real:total ratio = 4.4% (too low — target 25%+)
- Negative ratio = 13.6% (acceptable, could increase to 20%)

### Train/val split

- **MUST** use 80/20 train/val split. Never train on 100% of data.
- YOLO `data.yaml` must define separate `train:` and `val:` paths.
- Val set should include both real and synthetic images.
- Never put the same image in both train and val.

### Hard negative mining workflow

1. Run current model on unlabelled flight video
2. Save frames where model fires false positives (conf > 0.3)
3. Add these as negatives (empty label files) to training set
4. Retrain — false positive rate drops significantly

---

## 3. Training Parameters for YOLOv8n Aerial Detection

### Recommended Colab training cell

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # pretrained weights

results = model.train(
    data='/content/dataset_v2/dataset.yaml',
    imgsz=640,              # TFLite input is 640x640 — train at inference size
    epochs=250,             # more epochs with small dataset
    batch=16,               # 16 fits on Colab T4 GPU
    patience=50,            # early stopping if val loss plateaus
    degrees=5,              # slight rotation (drone tilt)
    scale=0.3,              # zoom augmentation (altitude variation)
    flipud=0.1,             # vertical flip (drone can approach from any direction)
    fliplr=0.5,             # horizontal flip (default)
    erasing=0.3,            # random erasing (partial occlusion)
    close_mosaic=10,        # disable mosaic for last 10 epochs (stabilise)
    label_smoothing=0.1,    # regularisation, prevents overconfident predictions
    hsv_h=0.015,            # hue jitter
    hsv_s=0.7,              # saturation jitter
    hsv_v=0.4,              # value/brightness jitter
    mosaic=1.0,             # mosaic augmentation (default)
    mixup=0.1,              # light mixup
    copy_paste=0.1,         # copy-paste augmentation
    project='runs/train',
    name='sar_v3',
)
```

### Why imgsz=640 (not 1088)

- TFLite model input is fixed at `[1, 640, 640, 3]` regardless of training imgsz.
- Training at 1088 means YOLO learns features at 1088 resolution, but inference always resizes to 640.
- Training at 640 means learned features match inference resolution exactly.
- The v2 model trained at imgsz=1088 works because YOLO's internal resize handles it, but 640 is theoretically optimal.
- Exception: if you plan to export at a different resolution, match imgsz to export size.

### Parameter rationale

| Parameter | Value | Why |
|-----------|-------|-----|
| `epochs=250` | More than default 100 | Small dataset benefits from longer training with early stopping |
| `batch=16` | Colab T4 limit | Larger batch = more stable gradients. Use 8 if OOM. |
| `degrees=5` | Slight rotation | Drone tilt during flight, not extreme rotation |
| `scale=0.3` | Zoom range | Simulates altitude variation (dummy appears larger/smaller) |
| `flipud=0.1` | Low probability | Dummy orientation is usually upright, but drone can approach from south |
| `erasing=0.3` | Moderate | Simulates partial occlusion by grass, shadow edges |
| `close_mosaic=10` | Last 10 epochs | Mosaic is great for learning but noisy for fine-tuning — disable near end |
| `label_smoothing=0.1` | Regularisation | Prevents the model from being 0.999 confident on training data and brittle on new data |

---

## 4. Export Best Practices

### TFLite (primary deployment on Pi)

```python
model = YOLO('runs/train/sar_v3/weights/best.pt')

model.export(
    format='tflite',
    imgsz=640,          # must match inference pipeline
    half=False,         # float32 — FP16 TFLite has compatibility issues
    int8=False,         # see INT8 section below
    nms=True,           # include NMS in the model graph
)
```

- Output: `best_float32.tflite` (~11.7 MB for YOLOv8n)
- Input shape: `[1, 640, 640, 3]` float32
- Output shape: `[1, 5, 8400]` (x, y, w, h, conf for 8400 anchors)
- Drop-in replacement: `cp best_float32.tflite ~/sar-drone/best.tflite`

### NCNN (faster inference on Pi, ~15 FPS expected)

```python
model.export(
    format='ncnn',
    imgsz=640,
    half=True,          # FP16 — Pi 5 ARM has native FP16 support
)
```

- Output: `best_ncnn_model/` directory (param + bin files)
- Copy entire directory to Pi
- vision.py supports NCNN backend via `--ncnn` flag or `backend="ncnn"`
- ~2-3x faster than TFLite on Pi 5

### INT8 quantization (experimental)

```python
model.export(
    format='tflite',
    imgsz=640,
    int8=True,
    data='dataset.yaml',  # calibration dataset required
)
```

- Potential 2x speedup over float32
- Requires representative calibration dataset (100+ images)
- May reduce detection accuracy by 1-3% mAP — test before deploying
- Worth testing if inference speed is a bottleneck (currently 206ms / 4.8 FPS)

### Export checklist

- [ ] Verify input shape: `[1, 640, 640, 3]`
- [ ] Verify output shape: `[1, 5, 8400]`
- [ ] Test on Pi with `tests/hardware/benchmark.py`
- [ ] Compare detection rate on known test images vs previous model
- [ ] Check file size (YOLOv8n float32 should be ~11-12 MB)

---

## 5. Domain Gap Mitigation

The biggest risk with synthetic training data is the domain gap: the model learns to detect
synthetic composites but struggles with real camera images. These techniques reduce the gap.

### Composite edge blending

Bad: sharp rectangular paste of dummy onto background.
Good: Gaussian blur on the alpha mask edges (3-5px kernel).

```python
# In generate_dataset_v2.py
mask = np.zeros(dummy.shape[:2], dtype=np.float32)
mask[dummy_alpha > 128] = 1.0
mask = cv2.GaussianBlur(mask, (7, 7), 0)  # soft edges
composite = bg * (1 - mask[..., None]) + dummy_rgb * mask[..., None]
```

This prevents the model from learning "sharp rectangular edge = dummy".

### Background-aware color matching

Match the dummy's brightness/contrast to the background region where it's placed:

```python
# Match mean brightness of dummy to local background patch
bg_patch = background[y:y+h, x:x+w]
bg_mean = np.mean(bg_patch)
dummy_mean = np.mean(dummy_rgb)
dummy_rgb = np.clip(dummy_rgb * (bg_mean / dummy_mean), 0, 255).astype(np.uint8)
```

Without this, the model may learn brightness discontinuity rather than dummy shape.

### Multiple background sources

- v1 dataset used a single `map.jpg` background — model overfit to that specific grass texture.
- v2 uses DJI video frames as backgrounds (more variety).
- Future: add Google Earth screenshots, other flight videos, different fields.
- Minimum 20+ distinct background images for robust training.

### More real labelled frames

The single most effective way to close the domain gap:

| Real frames | Expected impact |
|------------|-----------------|
| 0 (synthetic only) | Model works in sim, fails outdoors |
| 10-20 | Noticeable improvement, still fragile |
| **50-100** | **Robust outdoor detection** |
| 200+ | Diminishing returns unless scenes vary |

Current dataset has 16 real frames. Priority for next training round: label 50+ frames
from flight video using `tools/label_tool.py --full`.

### Scale consistency

Dummy size in synthetic images must match real appearance at each altitude:

```
apparent_size_px = (real_height_m * focal_length_px) / altitude_m
```

At 30m altitude with 1416px focal length and 1.8m dummy:
`1.8 * 1416 / 30 = 85 pixels` tall in a 1088-high frame.

Generate synthetic images across the full altitude range (15-50m) with correct scaling.

---

## 6. Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Training at 1088, inference at 640 | Slight accuracy loss from resolution mismatch | Train at imgsz=640 |
| No negatives in dataset | High false positive rate on grass/rocks/shadows | Add 15-25% negative images |
| No train/val split | Inflated mAP, poor generalisation | Always split 80/20 |
| Single background image | Model memorises background texture | Use 20+ diverse backgrounds |
| Sharp composite edges | Model detects paste boundary, not dummy | Gaussian blur on alpha mask |
| Overconfident threshold | Misses detections at altitude | Lower conf from 0.4 to 0.25-0.3 |
| Too few real images | Good in sim, poor in real | Label 50+ real frames |
| Motion blur not augmented | Misses detections during movement | Add directional blur augmentation |

---

## 7. Model Performance Tracking

Track every trained model for comparison:

| Version | Dataset | imgsz | Epochs | mAP50 | Pi FPS | Notes |
|---------|---------|-------|--------|-------|--------|-------|
| v1 | 200 syn @ 640 | 640 | 100 | ~0.95 | 4.8 | Original, single background |
| v2 (sar_v2_1088) | 300 syn + 16 real + 50 neg @ 1088 | 1088 | 150 | 0.995 | 4.8 | Current best |
| v3 (planned) | 500+ syn + 50+ real + 100 neg @ 640 | 640 | 250 | TBD | TBD | Next iteration |

Always benchmark on Pi with `tests/hardware/benchmark.py` before deploying.
Always test on DJI flight video with `tests/laptop/video_test.py` before deploying.

---

## 8. Quick Reference — Next Training Round Checklist

1. [ ] Label 50+ real frames: `python tools/label_tool.py --full "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"`
2. [ ] Generate 500+ synthetic images with motion blur + shadows: `python generate_dataset_v2.py`
3. [ ] Add 100+ negatives (15-25% of total), including hard negatives from false positive mining
4. [ ] Verify 80/20 train/val split in `dataset.yaml`
5. [ ] Train on Colab: imgsz=640, epochs=250, batch=16 (see Section 3)
6. [ ] Export TFLite float32: `model.export(format='tflite', imgsz=640)`
7. [ ] Test on DJI video: `python tests/laptop/video_test.py --model new_model.tflite`
8. [ ] Benchmark on Pi: `python tests/hardware/benchmark.py`
9. [ ] Deploy: `cp new_model.tflite best.tflite`
10. [ ] Update this table (Section 7) with results
