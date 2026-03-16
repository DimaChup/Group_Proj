# Model Training Guide — YOLOv8n Dummy Detector

## Quick Summary

**Current best model:** `cv_models/sar_v2_1088/best.tflite`
- Trained on: 300 synthetic + 16 real labelled + 50 negatives, all at 1456x1088
- Training: imgsz=1088, epochs=150, batch=8, mAP50=0.995
- Output: float32 TFLite (11.7MB), same input [1,640,640,3] / output [1,5,8400] as original
- Drop-in replacement: `cp cv_models/sar_v2_1088/best.tflite best.tflite`

**Model history:**
| Version | Location | Dataset | imgsz | mAP50 | Notes |
|---------|----------|---------|-------|-------|-------|
| v1 (original) | `best.tflite` (root) | 200 synthetic 640x640 | 640 | ~0.95 | First model, single background |
| sar_640 | `cv_models/sar_640/` | Improved synthetic | 640 | — | Earlier experiment |
| sar_1280 | `cv_models/sar_1280/` | Improved synthetic | 1280 | — | Earlier experiment |
| **sar_v2_1088** | `cv_models/sar_v2_1088/` | **300 syn + 16 real + 50 neg at 1456x1088** | **1088** | **0.995** | **Current best** |

---

## Complete Retraining Workflow (v2)

### Step 1: Collect Real Frames from Flight Video

Extract and label real frames from DJI flight footage:

```bash
# Label real frames at native resolution (no squishing)
python tools/label_tool.py --full "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
```

**How label_tool.py --full works:**
- Scroll through video with A/D keys (or arrow keys)
- When you see the dummy, click top-left then bottom-right to draw bounding box
- Press S to save the labelled frame
- Press Q when done
- Output: `real_frame_*.jpg` + matching `.txt` YOLO label files
- The `--full` flag ensures frames are saved at native resolution (1456x1088), not squished to 640x640
- Label at multiple altitudes (15m, 25m, 35m, 50m) for best training coverage

### Step 2: Generate Synthetic + Negative Images

```bash
cd "c:\Users\Bristol\Desktop\AI for Robotics\v3"
python generate_dataset_v2.py
```

**What generate_dataset_v2.py does:**
1. Loads `dummy.png` (foreground with alpha channel) and DJI video frame backgrounds
2. Generates 300 synthetic images at 1456x1088:
   - Random background crops from real flight footage
   - Dummy scaled based on simulated altitude (correct pixel size for altitude)
   - Random rotation, brightness, contrast, blur augmentation
   - YOLO format labels (class x_center y_center width height)
3. Generates 50 negative images (backgrounds with NO dummy, empty label files)
4. Copies real labelled frames into the dataset
5. Creates `dataset.yaml` for YOLO training

**Dataset structure after generation:**
```
dataset_v2/
├── dataset.yaml        ← YOLO data config (path, train, val, class names)
├── images/
│   ├── syn_0000.jpg    ← 300 synthetic images (dummy composited on backgrounds)
│   ├── ...
│   ├── real_frame_*.jpg ← 16 real labelled frames
│   ├── neg_0000.jpg    ← 50 negative images (no dummy)
│   └── ...
├── labels/
│   ├── syn_0000.txt    ← YOLO labels (0 x_center y_center w h)
│   ├── ...
│   ├── real_frame_*.txt ← Real frame labels
│   ├── neg_0000.txt    ← Empty files (no objects)
│   └── ...
└── preview_50m/        ← Preview images showing dummy at simulated 50m altitude
```

### Step 3: Zip and Upload to Colab

```bash
# On Windows (PowerShell or cmd)
# dataset_v2.zip should already exist after running generate_dataset_v2.py
# If not, zip manually:
# Right-click dataset_v2 → Send to → Compressed (zipped) folder
```

Upload `dataset_v2.zip` to Google Drive (root or a known folder).

### Step 4: Train on Google Colab (GPU)

Open a new Colab notebook with GPU runtime (Runtime → Change runtime type → T4 GPU).

**Cell 1 — Install Ultralytics:**
```python
!pip install ultralytics
import ultralytics
ultralytics.checks()
```

**Cell 2 — Mount Drive and copy dataset:**
```python
from google.colab import drive
drive.mount('/content/drive')

!cp "/content/drive/MyDrive/dataset_v2.zip" /content/
!unzip -q /content/dataset_v2.zip -d /content/
```

**Cell 3 — Fix dataset.yaml path for Colab:**
```python
import yaml

with open('/content/dataset_v2/dataset.yaml', 'r') as f:
    data = yaml.safe_load(f)

data['path'] = '/content/dataset_v2'
data['train'] = 'images'
data['val'] = 'images'

with open('/content/dataset_v2/dataset.yaml', 'w') as f:
    yaml.dump(data, f)

print("Updated dataset.yaml:")
!cat /content/dataset_v2/dataset.yaml
```

**Cell 4 — Train:**
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # pretrained COCO weights

results = model.train(
    data='/content/dataset_v2/dataset.yaml',
    epochs=150,
    imgsz=1088,          # native resolution (NOT 640)
    batch=8,             # fits in T4 GPU memory at 1088
    patience=30,         # early stopping
    device=0,            # GPU

    # Augmentation tuned for aerial drone detection
    degrees=20.0,        # rotation (drone approaches from any angle)
    scale=0.7,           # aggressive scale (simulates altitude variation)
    shear=3.0,           # mild perspective
    perspective=0.0005,  # subtle camera angle
    mosaic=1.0,          # critical for small objects
    mixup=0.1,           # mild blending
    copy_paste=0.2,      # paste dummy onto different backgrounds
    erasing=0.0,         # disable — would erase our tiny target
    fliplr=0.5,          # horizontal flip
    flipud=0.0,          # no vertical flip

    project='runs',
    name='sar_v2_1088',
)
```

**Cell 5 — Check results:**
```python
from IPython.display import Image
Image('runs/sar_v2_1088/results.png')
```

```python
metrics = model.val()
print(f"mAP50: {metrics.box.map50:.3f}")
print(f"mAP50-95: {metrics.box.map:.3f}")
```

**Cell 6 — Export TFLite + NCNN:**
```python
# TFLite (float32) — drop-in replacement for Pi
model.export(format='tflite', imgsz=640)
# Output shape: [1, 640, 640, 3] input, [1, 5, 8400] output
# NOTE: export imgsz=640 even though trained at 1088 — TFLite runtime always resizes to 640

# NCNN — faster inference on Pi (~15 FPS expected)
model.export(format='ncnn', imgsz=640)
```

**Cell 7 — Download:**
```python
from google.colab import files
import glob, shutil, os

# Create output directory
os.makedirs('export', exist_ok=True)

# Copy weights
shutil.copy('runs/sar_v2_1088/weights/best.pt', 'export/best.pt')

# Find TFLite
tflite_files = glob.glob('runs/sar_v2_1088/weights/**/*.tflite', recursive=True)
for f in tflite_files:
    shutil.copy(f, f'export/{os.path.basename(f)}')
    print(f"TFLite: {f} ({os.path.getsize(f)/1e6:.1f} MB)")

# Find NCNN
ncnn_dir = glob.glob('runs/sar_v2_1088/weights/*_ncnn_model')
if ncnn_dir:
    shutil.copytree(ncnn_dir[0], 'export/ncnn', dirs_exist_ok=True)
    print(f"NCNN dir: {ncnn_dir[0]}")

# Copy results
for f in ['results.png', 'confusion_matrix.png']:
    src = f'runs/sar_v2_1088/{f}'
    if os.path.exists(src):
        shutil.copy(src, f'export/{f}')

# Zip and download
shutil.make_archive('sar_v2_1088_export', 'zip', 'export')
files.download('sar_v2_1088_export.zip')
```

### Step 5: Save Model Locally

```bash
# Unzip downloaded export
# Copy to cv_models directory:
mkdir -p cv_models/sar_v2_1088
cp export/best.tflite cv_models/sar_v2_1088/
cp export/best.pt cv_models/sar_v2_1088/
cp -r export/ncnn cv_models/sar_v2_1088/
cp export/results.png cv_models/sar_v2_1088/  # optional
cp export/confusion_matrix.png cv_models/sar_v2_1088/  # optional
```

### Step 6: Test on Laptop with Video

```bash
# Test new model against DJI flight video
python tests/laptop/video_test.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --model cv_models/sar_v2_1088/best.tflite

# Compare old vs new model side by side
python tests/laptop/video_test_compare.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
# Press M to switch between models live
```

### Step 7: Deploy to Pi

```bash
# Option A: Copy directly to active model slot
cp cv_models/sar_v2_1088/best.tflite best.tflite

# Option B: Use --model flag (no copy needed)
python main.py --model cv_models/sar_v2_1088/best.tflite

# Push to git, pull on Pi
git add best.tflite  # or cv_models/
git commit -m "Update model to sar_v2_1088"
git push

# On Pi:
cd ~/sar-drone && git pull
# Model is now active — no code changes needed
```

---

## Dataset Improvement Checklist

### What v2 already has (improvements over v1)
- [x] Native resolution (1456x1088 instead of 640x640)
- [x] Real labelled frames (16 from DJI flight video at various altitudes)
- [x] Negative images (50 frames with no dummy — reduces false positives)
- [x] Altitude-correct scaling (dummy pixel size matches real altitude)
- [x] Real flight video backgrounds (not just map.jpg)
- [x] Augmentation (brightness, contrast, blur, rotation, scale)

### Still possible improvements
- [ ] More real labelled frames (currently 16, aim for 50-100)
- [ ] Multiple flight videos (currently just one flight)
- [ ] Different dummy poses/clothing
- [ ] Partially occluded dummy (behind tall grass)
- [ ] Different weather/lighting conditions
- [ ] INT8 quantized export (faster inference, ~2x speedup on Pi)
- [ ] Proper train/val split (currently same images for both — inflates metrics)

---

## Model Architecture Notes

All models use YOLOv8n (nano) architecture:
- **Input**: [1, 640, 640, 3] float32 (0-255 range, RGB)
- **Output**: [1, 5, 8400] float32 (x, y, w, h, confidence per detection)
- **Classes**: 1 (dummy)
- **TFLite size**: 3.3MB (original) to 11.7MB (float32 retrained)
  - Size difference is due to different export settings, NOT different architecture

vision.py handles all preprocessing and postprocessing:
- Resizes input frame to 640x640
- Runs inference
- Filters by confidence threshold (0.4 default, configurable)
- Returns `(found, x, y, conf)` — normalized coordinates

**Any TFLite model with input [1,640,640,3] and output [1,5,8400] is a drop-in replacement.**

---

## Confidence Threshold

Current: 0.4 (in vision.py, configurable via config.py CONFIDENCE_THRESHOLD)

| Threshold | Best for |
|-----------|----------|
| 0.25 | Search phase (catch everything, accept false positives) |
| 0.3 | Video analysis default (used in video_test.py) |
| 0.35-0.4 | Balanced (flight default) |
| 0.5+ | Verification (high confidence only) |

---

## Common Pitfalls

1. **Same images in train AND val** — metrics are meaningless. Current dataset_v2 uses same split (val=train). For rigorous evaluation, split 80/20.
2. **Only one background** — v1 had just map.jpg. v2 uses real flight video frames (much better).
3. **No negatives** — v1 had none. v2 has 50 negative images (reduces false positives).
4. **Overfitting** — if train loss near 0 but val loss high, reduce epochs or add data.
5. **Wrong imgsz for export** — always export TFLite with `imgsz=640` even if trained at 1088. The training resolution just improves feature learning; TFLite runtime uses 640x640.
6. **6fps video for analysis** — SRT telemetry is at 30fps. Using 6fps video causes altitude/GPS misalignment. Always use 30fps video.
7. **label_tool.py without --full** — without the flag, frames are squished to 640x640 for labelling. Use `--full` to label at native resolution.

---

## Previous Training (v1, for reference)

**What v1 did:**
1. `generate_dataset.py` created 200 synthetic images at 640x640 (dummy.png composited on map.jpg)
2. Uploaded `project_data/` to Google Colab
3. Trained: imgsz=640, epochs=100, batch=16
4. Downloaded `best_float32.tflite` → copied to `best.tflite`

**v1 limitations (all fixed in v2):**
- Only 200 images (v2: 366)
- Single background (map.jpg) — model memorized texture
- No real frames — only synthetic composites
- No negatives — model always predicted something
- 640x640 resolution — lost detail at altitude
