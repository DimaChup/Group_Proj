# Training Data Quality Analysis

Analysis of `training/dataset_v2/` — the dataset used to train `cv_models/sar_v2_1088/best.tflite`.

---

## 1. Current Dataset Breakdown

| Category | Count | Description |
|----------|-------|-------------|
| Synthetic positives | 300 | dummy.png composited on map.jpg crops |
| Real positives | 16 | Frames from DJI flight video (45-50m altitude only) |
| Negatives | 50 | Background crops with no dummy |
| **Total** | **366** | |

### Is 366 Enough?

For a **single-class detector** with transfer learning (YOLOv8n pretrained on COCO), 366 is workable but tight. Industry guidelines:

| Dataset Size | Typical Outcome |
|-------------|-----------------|
| < 100 | Severe overfitting, unusable without heavy augmentation |
| 100-500 | Viable with pretrained backbone + strong augmentation (we are here) |
| 500-2000 | Solid for single-class, reliable metrics |
| 2000-10000 | Production quality, robust to edge cases |
| 10000+ | Diminishing returns for single-class |

**Verdict**: 366 is on the low end of viable. The pretrained COCO backbone does most of the heavy lifting (general feature extraction), so the fine-tuning data mostly teaches "what a dummy looks like from above." For this specific task (one class, controlled environment, known altitude range), it can work — but the reported mAP50=0.995 is misleading (see Section 5).

### Train/Val Split: Critical Problem

The `dataset.yaml` file shows:

```yaml
train: images
val: images
```

**Train and validation use the exact same images.** This means:
- mAP50 = 0.995 is measured on training data — it tells us nothing about generalization
- The model may have memorized the 366 images rather than learning generalizable features
- With only 366 images and 150 epochs, each image was seen ~150 times — significant overfitting risk
- The real-world performance could be substantially worse than reported

**Fix**: Split 80/20 (293 train / 73 val), ensuring real images are proportionally distributed. Even better: hold out all 16 real images as validation since they represent the actual deployment domain.

---

## 2. Synthetic Data Quality

### Compositing Pipeline (`training/generate_dataset_v2.py`)

The generator does the following:
1. Loads `assets/dummy.png` (1280x714 RGBA) and `assets/map.jpg` as background
2. Crops a random 640x640 patch from map.jpg
3. Scales dummy to a random size (simulating altitude)
4. Rotates 0-360 degrees with alpha blending
5. Applies random brightness/contrast (50% of images)
6. Applies Gaussian blur (30% of images, kernel 3 or 5)

### Scale Distribution (Altitude Simulation)

The code uses three scale bands:

| Band | Scale Range | Approx Altitude | Probability | Count (~) |
|------|-------------|-----------------|-------------|-----------|
| Close | 0.20 - 0.40 | 15-20m | 30% | ~90 |
| Medium | 0.08 - 0.20 | 20-35m | 40% | ~120 |
| Far | 0.03 - 0.08 | 35-60m | 30% | ~90 |

Actual bbox width distribution from labels (normalized, n=300):
- Min: 0.030 (19 px in 640) — smallest dummies, far range
- P25: 0.082 (53 px)
- Median: 0.123 (79 px)
- P75: 0.177 (113 px)
- Max: 0.247 (158 px)

**Problem**: dummy.png is 1280x714. At scale 0.03, the composited dummy is ~38x21 pixels. After rotation, the bbox is even smaller. At the far end, the dummy is close to the minimum detectable size for YOLOv8n (which internally resizes everything to 640x640). This is realistic for 50m altitude but pushes detection limits.

### Augmentation Assessment

| Augmentation | Present? | Quality |
|-------------|----------|---------|
| Random scale (altitude) | Yes | Good — three bands cover 15-60m |
| Random rotation | Yes (0-360) | Good — dummy can face any direction |
| Brightness/contrast | Yes (50%) | Adequate — +/-30 brightness, 0.7-1.3 contrast |
| Gaussian blur | Yes (30%) | Weak — only k=3 or k=5, not directional |
| Alpha blending | Yes | Good — proper transparency compositing |
| Random position | Yes | Good — dummy placed anywhere in frame |

### Missing Augmentations (Significant Gaps)

| Missing Augmentation | Impact | Why It Matters |
|---------------------|--------|----------------|
| **Motion blur (directional)** | HIGH | Drone flies at 6-10 m/s. Real images have directional blur along flight path. Gaussian blur is isotropic — not representative. |
| **Shadows** | MEDIUM | Outdoor scenes have strong shadows. Dummy casts a shadow; the model never sees this in synthetic data. |
| **Partial occlusion** | MEDIUM | Tall grass, bushes, fence posts can partially hide the dummy. Zero occlusion in training = fragile to occlusion at test time. |
| **Color jitter / hue shift** | MEDIUM | Lighting changes (overcast vs sun, morning vs noon) shift color balance. Current augmentation only adjusts brightness/contrast. |
| **Perspective warp** | LOW | Drone camera angle is mostly nadir, but at frame edges there is perspective distortion. |
| **Multiple dummies per image** | LOW | Not mission-critical (single casualty expected), but mosaic augmentation during training partially addresses this. |
| **Weather effects (rain, fog)** | LOW | Flight cancelled for weather — this is realistic but low priority for first deployment. |
| **Different dummy appearances** | HIGH | Only one dummy.png image. The model is learning to detect THIS specific dummy texture/color, not "person lying on ground" generally. |

### Background Diversity Problem

All 300 synthetic images use crops from a single `assets/map.jpg` file. Even though crops are random, the texture palette is limited to one satellite image. The model likely learns "this grass texture + orange blob = dummy" rather than generalizing.

The 50 negatives also come from the same map.jpg — so the model's negative experience is limited to one location's background.

---

## 3. Real Data: Severe Limitations

### The 16 Real Images

All 16 real frames share these characteristics:

| Property | Value | Problem |
|----------|-------|---------|
| Altitude | 45-50m (all frames) | No low-altitude (15-35m) real data |
| Bbox size | 0.027 x 0.037 (all identical) | Single fixed bbox — labels may be approximate, not tight |
| Source | One DJI flight pass | Single lighting condition, single time of day |
| Y-position | 0.67-0.71 (all frames) | Dummy always in bottom third of frame |
| Resolution | 640x640 tiles (default --size) | Not native 1456x1088 despite TRAINING_GUIDE saying otherwise |

**Critical finding**: All 16 real labels have **identical bbox dimensions** (w=0.027473, h=0.036765). This means the labels were generated with a fixed box size, not manually fitted to each frame. At 50m altitude, the dummy is only ~18x24 pixels in the 640px tile — a rough fixed box may be acceptable, but it means the model never sees tightly-fitted real bounding boxes.

**Diversity is near-zero**: same flight, same altitude band (45-50m), same weather, same time of day, same dummy position in the scene (just drifting across the frame as the drone passes over). These 16 images are essentially the same scene captured 16 times with slight position variation.

### What Real Data Should Look Like

For meaningful real training data, you need variation across:
- Altitude: 15m, 25m, 35m, 50m
- Lighting: morning, noon, overcast, direct sun
- Dummy pose: lying flat, curled, arms spread
- Background: grass, dirt path, near bushes, near structures
- Camera angle: directly overhead, slight offset

---

## 4. Negative Mining Strategy

### Current State

- 50 negatives from random map.jpg crops
- All from one background image
- Ratio: 50 negatives / 316 positives = 0.16:1

### Optimal Ratio

Research (YOLO documentation, object detection literature) suggests:
- **1:1 to 3:1 negative:positive ratio** is standard
- For aerial detection with diverse backgrounds: 2:1 recommended
- With 316 positives, target **600-950 negatives**

### Hard Negative Mining (High Priority)

Current negatives are random background crops — they are "easy" negatives. The model needs **hard negatives**: images that look like they might contain a dummy but do not.

Sources for hard negatives:
1. **False positive frames from video_test.py** — run the model on DJI video, save frames where it fires incorrectly
2. **Confusing terrain**: bushes, rocks, trash, shadows that resemble a person
3. **Similar-color objects**: orange/brown patches in grass, equipment on ground
4. **Edge cases**: frame edges where partial objects appear

**Workflow**:
```bash
# 1. Run model on DJI video, save false positive frames
python tests/laptop/video_test.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --save-fp

# 2. Add to dataset as negatives (empty label files)
cp fp_frame_*.jpg training/dataset_v2/images/
touch training/dataset_v2/labels/fp_frame_*.txt  # empty = no objects
```

---

## 5. Model Validation: mAP50 = 0.995 Is Unreliable

### Why the Metric Is Meaningless

1. **No holdout set**: train == val. The model is evaluated on data it trained on.
2. **150 epochs on 366 images**: each image seen ~150 times. Classic overfitting territory.
3. **Synthetic dominance**: 300/316 positives are synthetic. High mAP on synthetic data does not predict real-world performance.

### What We Actually Know About Performance

| Source | Result | Reliability |
|--------|--------|-------------|
| Training mAP50 | 0.995 | Unreliable (no holdout) |
| Pi bench test (best.tflite original) | 50/50 det, 0.966 conf | On static test image only |
| DJI video replay | Detected at 45-50m altitude | Promising but single flight |
| Real outdoor flight | Not yet tested | Unknown |

### Recommended Validation Approach

1. **Immediate**: Re-run training with 80/20 split. Use real images as validation set:
   ```python
   # In dataset.yaml, split images into train/ and val/ subdirectories
   # Move all 16 real_* images to val/
   # Report val mAP50 — this is the real metric
   ```

2. **Before flight**: Run model on full DJI video, manually count true positives, false positives, and false negatives. Calculate precision, recall, F1.

3. **Gold standard**: Collect 50+ real frames from a different flight (different day/time), label them, evaluate. This is the only way to know if the model generalizes.

### Cross-Validation on 366 Images

With only 366 images, k-fold cross-validation (k=5) would give more robust metrics:
- Each fold trains on ~293, validates on ~73
- Average mAP across 5 folds is a better estimate
- But each training run takes ~30 min on Colab — total ~2.5 hours
- Worth doing if no more data is available before flight day

---

## 6. Recommendations for Next Training Round

### Priority Order

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| **1 (critical)** | Fix train/val split | 10 min | Honest metrics — know what you actually have |
| **2 (high)** | Add hard negatives from video FP analysis | 1-2 hrs | Reduces false positives in real deployment |
| **3 (high)** | Add directional motion blur augmentation | 30 min | Matches real flight conditions (6-10 m/s) |
| **4 (high)** | Collect real data at multiple altitudes | Next flight | 15m, 25m, 35m real frames |
| **5 (medium)** | Add more negative images (target 600+) | 30 min | Better negative:positive ratio |
| **6 (medium)** | Use multiple backgrounds for synthetic data | 1 hr | DJI video frames as bg instead of just map.jpg |
| **7 (medium)** | Add shadow augmentation to synthetic pipeline | 1 hr | Realistic outdoor appearance |
| **8 (low)** | Different dummy images/poses | Next opportunity | Generalization beyond one dummy appearance |
| **9 (low)** | Try YOLOv8s if Pi NCNN gives 15+ FPS | 2 hrs | Better accuracy with larger model |

### Concrete Steps for Next Training Round

**Step 1: Fix validation split (do this immediately)**
```bash
cd training/dataset_v2
mkdir -p train/images train/labels val/images val/labels

# Move real images to val (they represent the deployment domain)
mv images/real_* val/images/
mv labels/real_* val/labels/

# Move 20% of synthetic + negatives to val
# (script or manually move every 5th file)

# Update dataset.yaml:
# train: train/images
# val: val/images
```

**Step 2: Add motion blur augmentation to generate_dataset_v2.py**
```python
# Add after Gaussian blur block (line ~99):
if random.random() < 0.3:
    # Directional motion blur (simulates drone movement)
    k_size = random.choice([5, 7, 9, 11])
    kernel = np.zeros((k_size, k_size))
    angle = random.uniform(0, 180)
    # Horizontal motion blur kernel, then rotate
    kernel[k_size // 2, :] = 1.0 / k_size
    M_blur = cv2.getRotationMatrix2D((k_size // 2, k_size // 2), angle, 1.0)
    kernel = cv2.warpAffine(kernel, M_blur, (k_size, k_size))
    kernel = kernel / kernel.sum()
    background = cv2.filter2D(background, -1, kernel)
```

**Step 3: Use DJI video frames as backgrounds (instead of only map.jpg)**
```python
# In generate_synthetic(), load random frames from DJI video as backgrounds:
cap = cv2.VideoCapture("RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4")
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_idx = random.randint(0, total_frames - 1)
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
ret, bg_frame = cap.read()
# Crop 640x640 tile from bg_frame
```

**Step 4: Collect real data at next flight opportunity**

Using `capture_training.py` or `passive_watch.py`:
1. Fly manual passes at 15m, 25m, 35m, 50m over the dummy
2. Save frames with SPACE key (capture_training.py)
3. Label with `tools/label_tool.py --full`
4. Target: 20+ frames per altitude = 80+ real frames minimum

**Step 5: Hard negative collection**
```bash
# Run model on full DJI video, record all detections
python tests/laptop/video_test.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
# Manually identify false positives, save those frames
# Add as negatives to dataset
```

---

## Summary

| Aspect | Current State | Rating | Fix |
|--------|--------------|--------|-----|
| Dataset size (366) | Minimum viable for single-class + pretrained | Adequate | Grow to 800+ with negatives |
| Train/val split | None (same data) | **Critical gap** | Split 80/20 immediately |
| Synthetic quality | Good compositing, weak augmentation | Adequate | Add motion blur, shadows, DJI bg |
| Real data (16 frames) | Single altitude, single flight, fixed bbox | **Poor** | Collect at multiple altitudes |
| Negatives (50) | Too few, no hard negatives | Below target | Target 600+, add FP frames |
| Reported mAP (0.995) | Measured on training data | **Unreliable** | Re-evaluate with proper split |
| Background diversity | Single map.jpg | **Poor** | Use DJI video frames |
| Augmentation | Brightness, contrast, isotropic blur | Partial | Add motion blur, color jitter |

**Bottom line**: The model likely works adequately for the constrained deployment scenario (known field, known dummy, 35-50m altitude, clear weather) because the COCO-pretrained backbone provides strong general features. But the training data has fundamental quality issues that the mAP50=0.995 metric hides. The single most impactful fix is adding a proper train/val split and re-evaluating honestly.
