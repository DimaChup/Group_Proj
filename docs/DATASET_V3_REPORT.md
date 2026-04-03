# Dataset v3 Generation Report

How `training/generate_dataset_v3.py` was built and what best practices it applies.

---

## 1. Dataset Composition

**700 images total**, generated from `training/generate_dataset_v3.py` with default flags
(`--count 500 --negatives 100 --real-max 100`).

| Category | Prefix | Count | Altitude range | Description |
|----------|--------|-------|----------------|-------------|
| Close-range synthetic | `syn_close_` | 96 | 15-20 m | Large dummy, ~25% of synthetic |
| Mid-range synthetic | `syn_mid_` | 188 | 20-35 m | Medium dummy, ~40% of synthetic |
| Far-range synthetic | `syn_far_` | 142 | 35-50 m | Small dummy, ~35% of synthetic |
| Multi-target synthetic | `syn_multi_` | 74 | 15-50 m | 2-3 dummies per image, 15% of synthetic |
| Real labelled frames | `real_` | 100 | flight altitude | Tiles extracted from DJI video with CSV detections |
| Negatives | `neg_` | 100 | N/A | No dummy, empty label files |

Synthetic subtotals: 96 + 188 + 142 + 74 = 500 single/multi-target composites.

The altitude distribution is probabilistic: each synthetic image draws from a weighted
random split (25% close / 40% mid / 35% far), so exact counts vary per run.

---

## 2. Altitude Simulation

Dummy pixel size is derived from a physical camera model using the IMX296 sensor
parameters:

```
GSD = (SENSOR_W_MM * altitude_m) / (FOCAL_MM * image_width_px)
pixel_height = DUMMY_REAL_H_M / GSD
```

Constants used:

| Parameter | Value | Source |
|-----------|-------|--------|
| `SENSOR_W_MM` | 5.02 mm | IMX296 global shutter sensor datasheet |
| `FOCAL_MM` | 5.46 mm | Calibrated on Pi (92 cm visible at 1 m height, 2026-03-11) |
| `DUMMY_REAL_H_M` | 1.8 m | Measured dummy/mannequin height |

Example pixel heights (at 640 px image width):

| Altitude | GSD (m/px) | Dummy height (px) |
|----------|------------|-------------------|
| 15 m | 0.0215 | ~84 px |
| 25 m | 0.0359 | ~50 px |
| 35 m | 0.0502 | ~36 px |
| 50 m | 0.0718 | ~25 px |

This matches the scale consistency requirement from `CV_BEST_PRACTICES.md` Section 5:
generate across the full 15-50 m altitude range with physically correct scaling.

---

## 3. Augmentations Applied

Ten augmentations are applied stochastically after compositing. Each image receives a
random subset (not all at once).

| # | Augmentation | Probability | Parameters | Effect |
|---|-------------|------------|------------|--------|
| 1 | HSV color jitter | 50% | H +/-15, S x0.7-1.3, V x0.7-1.3 | Lighting/colour variation |
| 2 | Gamma correction | 40% | gamma 0.6-1.6 | Exposure variation (bright/dark) |
| 3 | Brightness/contrast | 40% | alpha 0.6-1.4, beta -40 to +40 | Linear intensity shift |
| 4 | Gaussian noise | 30% | sigma 5-25 | Sensor noise simulation |
| 5 | Random shadows | 25% | 1-3 convex polygons, darkness 0.4-0.7 | Tree/cloud shadow overlay |
| 6 | Motion blur | 20% | kernel 3-15 px, random angle 0-360 deg | Drone movement blur |
| 7 | Gaussian blur | 20% | kernel 3/5/7 px | General defocus |
| 8 | Haze/fog | 15% | alpha blend 10-40% with off-white (220) | UK weather, reduced contrast |
| 9 | Perspective warp | 15% | 3% corner displacement | Camera tilt/viewing angle |
| 10 | Barrel distortion | 10% | k1 = 0.1-0.4 | Lens fisheye effect |

Negatives receive the same augmentation pipeline as positives, ensuring the model cannot
distinguish negatives by augmentation style alone.

---

## 4. Assets Used

All assets are loaded from `v3/assets/`:

| Asset | File | Purpose |
|-------|------|---------|
| Dummy foreground | `assets/dummy.png` | BGRA image of the SAR dummy, composited onto backgrounds |
| Pants | `assets/pants.png` | Accessory placed near dummy (40% chance per target) |
| T-shirt | `assets/tshirt.png` | Accessory placed near dummy |
| Backpack | `assets/backpack.png` | Accessory placed near dummy |
| Cone | `assets/cone.png` | Accessory placed near dummy |
| Map background | `assets/map.jpg` | Satellite imagery for random background crops |
| DJI video | `RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4` | Real flight footage for background extraction + real frame labelling |
| Detection CSV | `RealVideo/DJI_0001_1456x1088_cropped_30fps_detections.csv` | Bounding box coordinates for real frame extraction |

Accessories are scaled to 30-60% of the dummy's pixel height and placed within 1-3
dummy-heights of the dummy centre. They do not receive their own bounding box labels --
they serve as contextual clutter to make the model more robust.

---

## 5. Background Diversity

Two background sources are pooled and used interchangeably:

1. **Map crops** (100 random crops from `map.jpg`): satellite imagery of the flight site,
   providing grass, paths, hedgerows, and shadows at various locations.

2. **DJI video frames** (50 random frames from the 30 fps flight video, cropped to
   `img_size`): real aerial footage at various altitudes and positions, providing natural
   colour grading, motion characteristics, and terrain variety.

Total background pool: **150 images** (100 map + 50 video). Each synthetic image randomly
selects one background from this pool.

This addresses the `CV_BEST_PRACTICES.md` Section 5 recommendation for 20+ distinct
backgrounds (we have 150) and using multiple background sources to prevent overfitting to
a single texture.

---

## 6. Train/Val Split

The dataset uses an **80/20 train/val split**:

| Split | Images | File |
|-------|--------|------|
| Train | 560 | `training/dataset_v3/train.txt` |
| Val | 140 | `training/dataset_v3/val.txt` |
| **Total** | **700** | |

The `dataset.yaml` references these split files:

```yaml
path: .../training/dataset_v3
train: train.txt
val: val.txt

names:
  0: dummy
```

Both train and val sets contain a mix of synthetic, real, and negative images (not
stratified by category). Seed 42 was used for reproducibility.

---

## 7. Comparison to v2

| Aspect | v2 (`generate_dataset_v2.py`) | v3 (`generate_dataset_v3.py`) |
|--------|------|------|
| **Total images** | 366 | 700 (1.9x larger) |
| **Synthetic** | 300 | 500 |
| **Real frames** | 16 | 100 (6.25x more) |
| **Negatives** | 50 (13.6%) | 100 (14.3%) |
| **Multi-target images** | None | 74 (15% of synthetic, 2-3 dummies each) |
| **Augmentations** | Basic (brightness, blur, rotation) | 10 augmentations (see Section 3) |
| **Motion blur** | Not included | Directional kernel, 3-15 px, random angle |
| **Shadows** | Not included | 1-3 convex polygons per image |
| **Haze/fog** | Not included | Alpha blend with off-white |
| **Barrel distortion** | Not included | Fisheye simulation, k1 0.1-0.4 |
| **Perspective warp** | Not included | Corner displacement up to 3% |
| **Accessories** | None | Pants, t-shirt, backpack, cone near dummy |
| **Background sources** | Map crops + DJI video frames | Same, but larger pool (150 vs ~50) |
| **Altitude model** | Ad hoc scaling | Physics-based GSD formula with calibrated sensor params |
| **Altitude distribution** | Uniform | Weighted: 25% close, 40% mid, 35% far |
| **Train/val split** | Same dir for train+val | Explicit 80/20 split via train.txt/val.txt |
| **Default image size** | 1088 | 640 (matches TFLite inference size) |
| **Output location** | `dataset_v2/` | `training/dataset_v3/` |

Key improvements: 6x more real frames, multi-target support, 7 new augmentation types,
accessory clutter, physics-based altitude scaling, proper train/val split files.

---

## 8. Best Practices Applied

Each augmentation and design choice maps to a specific recommendation in
`docs/CV_BEST_PRACTICES.md`:

| Best Practice (from CV_BEST_PRACTICES.md) | Section | How v3 implements it |
|------------------------------------------|---------|---------------------|
| Motion blur is #1 failure mode | Sec 1, Rank 1 | Directional motion blur kernel (3-15 px, random angle), 20% probability |
| Color/brightness jitter covers 70%+ of failures | Sec 1, Rank 2 | HSV jitter (50%) + gamma (40%) + brightness/contrast (40%) |
| Gaussian noise for sensor simulation | Sec 1, Rank 3 | Gaussian noise sigma 5-25, 30% probability |
| Shadow overlays for lighting variation | Sec 1, Rank 4 | 1-3 random convex polygon shadows, 25% probability |
| Perspective transforms for drone tilt | Sec 1, Rank 5 | 3% corner displacement perspective warp, 15% probability |
| Fog/haze for UK weather | Sec 1, Rank 8 | Alpha blend with off-white, 15% probability |
| 500-1000 images recommended | Sec 2 | 700 images (in recommended range) |
| 25-50% real labelled images | Sec 2 | 100/700 = 14.3% (improved from 4.4%, still below 25% target) |
| 15-25% negatives | Sec 2 | 100/700 = 14.3% (in range) |
| 80/20 train/val split | Sec 2 | 560/140 split via train.txt/val.txt |
| Multiple background sources | Sec 5 | 150 backgrounds from map.jpg + DJI video (exceeds 20+ minimum) |
| Scale consistency (altitude-correct sizing) | Sec 5 | Physics-based GSD formula with calibrated focal length + sensor width |
| Train at imgsz=640 to match inference | Sec 3, Sec 6 | Default `--size 640` matches TFLite input shape |

---

## 9. Known Limitations

1. **Real frame ratio still below target.** At 14.3%, real images are below the
   recommended 25-50%. Labelling more frames from flight video (or future flights) would
   further close the synthetic-to-real domain gap.

2. **No hard negative mining.** Negatives are random background crops, not frames where
   the model previously made false positive detections. Hard negative mining
   (`CV_BEST_PRACTICES.md` Section 2) would specifically target the model's weaknesses.

3. **No composite edge blending.** The alpha-blend compositing uses the raw alpha channel
   from `dummy.png` without Gaussian blur on the mask edges. `CV_BEST_PRACTICES.md`
   Section 5 recommends softening edges to prevent the model learning paste boundaries.

4. **No background-aware colour matching.** The dummy's brightness is not matched to the
   local background patch before compositing. This could create unrealistic brightness
   discontinuities.

5. **No random erasing augmentation.** YOLO's `erasing=0.3` parameter (recommended in
   `CV_BEST_PRACTICES.md` Section 3) simulates partial occlusion. This is applied during
   YOLO training, not in the dataset generator, so it depends on training config.

6. **Perspective warp does not update labels.** The 3% perspective warp shifts bounding
   box positions slightly. The code notes this is negligible at low strength, but at the
   upper range it could introduce small label noise.

7. **Single dummy appearance.** All synthetic images use the same `dummy.png`. Variation
   in dummy pose, clothing colour, or body position would improve robustness.

8. **Single flight video.** All real frames and video backgrounds come from one DJI
   flight. More diverse flight conditions (different times of day, weather, fields) would
   improve generalisation.

---

## 10. How to Regenerate

From the project root (`v3/`):

```bash
# Default: 500 synthetic + 100 real + 100 negatives at 640x640
python training/generate_dataset_v3.py

# Custom counts and size
python training/generate_dataset_v3.py \
    --count 500 \
    --negatives 100 \
    --real-max 100 \
    --size 640 \
    --output training/dataset_v3 \
    --video-bgs 50 \
    --multi-target 0.15 \
    --seed 42

# Larger dataset at 1088 resolution
python training/generate_dataset_v3.py \
    --count 800 \
    --negatives 200 \
    --size 1088 \
    --video-bgs 80
```

### All flags

| Flag | Default | Description |
|------|---------|-------------|
| `--output` | `dataset_v3` | Output directory |
| `--size` | 640 | Square image dimension (px) |
| `--count` | 500 | Number of synthetic images |
| `--negatives` | 100 | Number of negative images |
| `--real-max` | 100 | Max real frames to extract from video |
| `--video` | `RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4` | DJI video path |
| `--csv` | `RealVideo/..._detections.csv` | Detection CSV for real frame extraction |
| `--video-bgs` | 50 | Background crops to extract from DJI video |
| `--multi-target` | 0.15 | Fraction of synthetic images with 2-3 targets |
| `--seed` | None | Random seed for reproducibility |

### After generation

The train/val split (`train.txt` / `val.txt`) must be created separately -- the generator
produces a flat `images/` + `labels/` directory. Split with 80/20 ratio and seed 42.

### Training on Colab

```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model.train(
    data='dataset_v3/dataset.yaml',
    imgsz=640,
    epochs=250,
    batch=16,
    patience=50,
    label_smoothing=0.1,
    erasing=0.3,
    close_mosaic=10,
)
```

### Export and deploy

```bash
yolo export model=best.pt format=tflite imgsz=640
cp best_float32.tflite ~/sar-drone/best.tflite   # on Pi
```
