# Training Workflow v3 -- Step-by-Step Guide

Complete workflow for training a new YOLOv8n dummy detector model, from dataset
generation to Pi deployment.

---

## Prerequisites

- Laptop with `test_env` venv activated (has Ultralytics, OpenCV, NumPy)
- Google account for Colab (free T4 GPU)
- SSH access to Pi for deployment
- DJI flight video in `RealVideo/` (for real frame backgrounds)
- `dummy.png` in project root (foreground with alpha channel)

---

## Step 1: Generate the Dataset

```bash
cd "c:\Users\Bristol\Desktop\AI for Robotics\v3"
python training/generate_dataset_v2.py --count 500 --negatives 100 --output dataset_v3
```

This creates `dataset_v3/` with:

```
dataset_v3/
  dataset.yaml          YOLO data config (1 class: dummy)
  images/
    syn_0000.jpg        500 synthetic images (dummy composited on flight backgrounds)
    ...
    neg_0000.jpg        100 negative images (no dummy, empty labels)
    ...
    real_*.jpg          Any real labelled frames copied in
  labels/
    syn_0000.txt        YOLO format: class x_center y_center width height
    ...
    neg_0000.txt        Empty files (no objects)
    ...
```

**What the generator does:**
- Crops random patches from DJI video frames (or `map.jpg`) as backgrounds
- Composites `dummy.png` at altitude-correct scales (close/medium/far distribution)
- Applies augmentation: rotation, brightness, contrast, blur
- Creates YOLO-format labels normalised to 0-1
- Negative images teach the model what "no target" looks like

**Optional -- add real labelled frames first:**
```bash
# Label real video frames at native resolution (interactive GUI)
python tools/label_tool.py --full "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
# Click dummy center, scroll to resize box, S to save, N to skip, Q to quit
# Copy output into dataset_v3/images/ and dataset_v3/labels/ before zipping
```

---

## Step 2: Zip for Upload

```bash
# Windows (PowerShell)
Compress-Archive -Path dataset_v3 -DestinationPath dataset_v3.zip

# Or right-click dataset_v3 folder -> Send to -> Compressed (zipped) folder

# Linux/WSL
zip -r dataset_v3.zip dataset_v3/
```

Upload `dataset_v3.zip` to Google Drive root (or a known folder).

**Expected size:** ~200-400 MB depending on image count and resolution.

---

## Step 3: Train on Google Colab

Open a new Colab notebook. Set runtime to **GPU** (Runtime > Change runtime type > T4 GPU).

### Cell 1 -- Install Ultralytics

```python
!pip install ultralytics
import ultralytics
ultralytics.checks()
```

Expected output: Ultralytics version, Python version, torch with CUDA, T4 GPU detected.

### Cell 2 -- Upload and Unzip Dataset

```python
from google.colab import drive
drive.mount('/content/drive')

!cp "/content/drive/MyDrive/dataset_v3.zip" /content/
!unzip -q /content/dataset_v3.zip -d /content/

# Verify contents
!ls /content/dataset_v3/
!ls /content/dataset_v3/images/ | head -10
!wc -l /content/dataset_v3/labels/*.txt | tail -5
```

Expected output: `dataset.yaml`, `images/`, `labels/` directories. 600+ files in images.

### Cell 3 -- Fix dataset.yaml Path for Colab

```python
import yaml

with open('/content/dataset_v3/dataset.yaml', 'r') as f:
    data = yaml.safe_load(f)

data['path'] = '/content/dataset_v3'
data['train'] = 'images'
data['val'] = 'images'

with open('/content/dataset_v3/dataset.yaml', 'w') as f:
    yaml.dump(data, f)

print("Updated dataset.yaml:")
!cat /content/dataset_v3/dataset.yaml
```

Expected output:
```yaml
names:
- dummy
nc: 1
path: /content/dataset_v3
train: images
val: images
```

**Note:** Using the same images for train and val inflates metrics. For rigorous
evaluation, split 80/20. For our use case (small dataset, visual verification on
real video), this is acceptable.

### Cell 4 -- Train

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # pretrained COCO weights (downloads automatically)

results = model.train(
    data='/content/dataset_v3/dataset.yaml',
    epochs=150,
    imgsz=1088,          # native Pi camera resolution (NOT 640)
    batch=8,             # fits T4 GPU memory at 1088
    patience=30,         # early stopping if no improvement for 30 epochs
    device=0,            # GPU

    # Augmentation tuned for aerial drone detection
    degrees=20.0,        # rotation (drone approaches from any angle)
    scale=0.7,           # aggressive scale (simulates altitude variation)
    shear=3.0,           # mild perspective
    perspective=0.0005,  # subtle camera angle
    mosaic=1.0,          # critical for small objects
    mixup=0.1,           # mild blending
    copy_paste=0.2,      # paste dummy onto different backgrounds
    erasing=0.0,         # disable -- would erase our tiny target
    fliplr=0.5,          # horizontal flip
    flipud=0.0,          # no vertical flip (sky doesn't go below ground)

    project='runs',
    name='sar_v3',
)
```

Training takes ~30-60 minutes on T4. Watch for:
- `box_loss` and `cls_loss` decreasing steadily
- Early stopping if patience triggers before 150 epochs
- Final line shows mAP50 and mAP50-95

### Cell 5 -- Evaluate Results

```python
from IPython.display import Image, display

# Training curves (loss, mAP over epochs)
display(Image('runs/sar_v3/results.png'))

# Confusion matrix
display(Image('runs/sar_v3/confusion_matrix.png'))
```

```python
# Quantitative metrics
metrics = model.val()
print(f"mAP50:    {metrics.box.map50:.3f}")
print(f"mAP50-95: {metrics.box.map:.3f}")
print(f"Precision: {metrics.box.mp:.3f}")
print(f"Recall:    {metrics.box.mr:.3f}")
```

**Target metrics:**
| Metric | Good | Great |
|--------|------|-------|
| mAP50 | > 0.95 | > 0.99 |
| mAP50-95 | > 0.60 | > 0.80 |
| Precision | > 0.90 | > 0.95 |
| Recall | > 0.90 | > 0.95 |

If mAP50 < 0.90, something is wrong -- check dataset labels and augmentation settings.

### Cell 6 -- Export TFLite

```python
# TFLite float32 -- drop-in replacement for Pi
model.export(format='tflite', imgsz=640)
```

**Why `imgsz=640` when trained at 1088?**
Training at 1088 improves feature learning (the model sees more detail during training).
But the TFLite runtime on Pi always uses 640x640 input -- `vision.py` resizes every
frame to 640x640 before inference. Exporting at 640 matches this pipeline.

**Expected output:**
- File: `runs/sar_v3/weights/best_float32.tflite`
- Size: ~11-12 MB (float32, YOLOv8n)
- Input shape: `[1, 640, 640, 3]` (float32, 0.0-1.0 normalised, RGB)
- Output shape: `[1, 5, 8400]` (x, y, w, h, confidence per anchor)

### Cell 7 -- Export NCNN (optional, faster on Pi)

```python
# NCNN -- ~15 FPS on Pi 5 (vs ~5 FPS TFLite)
model.export(format='ncnn', imgsz=640)
```

**Expected output:**
- Directory: `runs/sar_v3/weights/best_ncnn_model/`
- Contains: `model.ncnn.bin`, `model.ncnn.param`, `metadata.yaml`, `model_ncnn.py`
- Input shape: `[1, 3, 640, 640]` (NCHW format -- NCNN handles this internally)
- Output shape: `[1, 5, 8400]` (same as TFLite)

### Cell 8 -- Download Everything

```python
from google.colab import files
import shutil, os, glob

os.makedirs('export', exist_ok=True)

# 1. Best weights (.pt) -- for future fine-tuning
shutil.copy('runs/sar_v3/weights/best.pt', 'export/best.pt')

# 2. TFLite model
tflite_files = glob.glob('runs/sar_v3/weights/**/*.tflite', recursive=True)
for f in tflite_files:
    shutil.copy(f, f'export/{os.path.basename(f)}')
    print(f"TFLite: {f} ({os.path.getsize(f) / 1e6:.1f} MB)")

# 3. NCNN model directory
ncnn_dirs = glob.glob('runs/sar_v3/weights/*_ncnn_model')
if ncnn_dirs:
    shutil.copytree(ncnn_dirs[0], 'export/ncnn', dirs_exist_ok=True)
    for f in os.listdir(ncnn_dirs[0]):
        print(f"NCNN: {f}")

# 4. Training artifacts (results, confusion matrix)
for f in ['results.png', 'confusion_matrix.png', 'confusion_matrix_normalized.png']:
    src = f'runs/sar_v3/{f}'
    if os.path.exists(src):
        shutil.copy(src, f'export/{f}')

# 5. Zip and trigger download
shutil.make_archive('sar_v3_export', 'zip', 'export')
files.download('sar_v3_export.zip')
```

**Expected download:** `sar_v3_export.zip` (~18-20 MB) containing:
- `best.pt` (~6 MB) -- full YOLO weights
- `best_float32.tflite` (~12 MB) -- TFLite model for Pi
- `ncnn/` -- NCNN model directory (~7 MB)
- `results.png` -- training curves
- `confusion_matrix.png` -- confusion matrix

---

## Step 4: Save Model Locally

Unzip `sar_v3_export.zip` and copy into the project:

```bash
cd "c:\Users\Bristol\Desktop\AI for Robotics\v3"

mkdir cv_models\sar_v3

# Copy from wherever you unzipped the download
copy export\best.pt cv_models\sar_v3\
copy export\best_float32.tflite cv_models\sar_v3\best.tflite
xcopy /E /I export\ncnn cv_models\sar_v3\ncnn
copy export\results.png cv_models\sar_v3\
copy export\confusion_matrix.png cv_models\sar_v3\
```

**Resulting structure:**
```
cv_models/sar_v3/
  best.pt               ~6 MB    Full YOLO weights (for future fine-tuning)
  best.tflite           ~12 MB   TFLite float32 (Pi deployment)
  ncnn/                          NCNN model (faster Pi deployment)
    best_ncnn_model/
      model.ncnn.bin
      model.ncnn.param
      metadata.yaml
      model_ncnn.py
  results.png                    Training curves
  confusion_matrix.png           Confusion matrix
```

---

## Step 5: Test on Laptop

### Quick test with video replay

```bash
# Test new model against DJI flight video
python tests/laptop/video_test.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --model cv_models/sar_v3/best.tflite

# Compare old (v2) vs new (v3) model side by side
python tests/laptop/video_test_compare.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4"
# Press M to switch between models live
```

### Verify TFLite model shape

```python
# Quick sanity check (run in Python)
import numpy as np

# TFLite
try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter

interp = Interpreter(model_path="cv_models/sar_v3/best.tflite")
interp.allocate_tensors()

inp = interp.get_input_details()[0]
out = interp.get_output_details()[0]

print(f"Input:  shape={inp['shape']}, dtype={inp['dtype']}")
print(f"Output: shape={out['shape']}, dtype={out['dtype']}")

# Expected:
#   Input:  shape=[1, 640, 640, 3], dtype=<class 'numpy.float32'>
#   Output: shape=[1, 5, 8400],     dtype=<class 'numpy.float32'>
```

If the shapes do not match `[1, 640, 640, 3]` input and `[1, 5, 8400]` output, the
model is NOT a drop-in replacement -- `vision.py` will crash or produce garbage.

---

## Step 6: Deploy to Pi

### Option A: Quick swap (copy over active model)

```bash
# On laptop -- overwrite the active model file
copy cv_models\sar_v3\best.tflite best.tflite

# Push to git
git add best.tflite
git commit -m "Deploy sar_v3 model"
git push

# On Pi (SSH)
cd ~/sar-drone && git pull
```

### Option B: Use --model flag (no file copy)

```bash
# Push model to git
git add cv_models/sar_v3/
git commit -m "Add sar_v3 trained model"
git push

# On Pi
cd ~/sar-drone && git pull
python main.py --model cv_models/sar_v3/best.tflite --headless
```

### Option C: NCNN backend (faster, ~15 FPS)

```bash
# On Pi -- vision.py auto-detects NCNN when passed the directory
python main.py --model cv_models/sar_v3/ncnn/best_ncnn_model --headless
# Or for passive_watch:
python passive_watch.py --model cv_models/sar_v3/ncnn/best_ncnn_model
```

Requires `ncnn` pip package on Pi (`pip install ncnn`).

---

## Step 7: Benchmark on Pi

```bash
# On Pi (SSH)
source pienv/bin/activate
cd ~/sar-drone

# Quick benchmark (50 inference runs, timing report)
python tests/hardware/benchmark.py

# Full benchmark (all models, system info, preprocessing)
python tests/hardware/benchmark_full.py
```

**Expected results (Pi 5, TFLite, XNNPACK CPU):**

| Metric | Expected |
|--------|----------|
| Inference time | 200-210 ms per frame |
| FPS | ~4.8 |
| Detection rate | 50/50 on test image |
| Confidence | > 0.90 |
| TFLite model size | ~12 MB |

If inference time is significantly different from v2, check model size -- a much
larger file may indicate accidental FP64 export or wrong architecture.

---

## Step 8: Verify with Passive Watch

Run the new model during a manual flight (or bench test with static dummy):

```bash
# On Pi
python passive_watch.py --headless
# Open browser: http://PI_IP:8090

# With specific model:
python passive_watch.py --model cv_models/sar_v3/best.tflite --headless
```

**What to check:**
- Detection rate: does it find the dummy at expected altitudes?
- False positive rate: does it trigger on grass, shadows, people?
- Confidence levels: should be > 0.4 for real dummy
- GPS estimate: detection overlay and GPS coords should be sensible
- Saved images: check `detections/` folder for detection snapshots

Compare against v2 results. If v3 is worse, keep v2 as active model and investigate
(check dataset quality, training curves, augmentation settings).

---

## Model Format Reference

### TFLite (primary deployment)

| Property | Value |
|----------|-------|
| Input shape | `[1, 640, 640, 3]` |
| Input dtype | float32 (0.0 - 1.0 normalised) |
| Input format | RGB (vision.py handles BGR-to-RGB conversion) |
| Output shape | `[1, 5, 8400]` |
| Output format | `[x_center, y_center, width, height, confidence]` per anchor |
| Coordinate range | 0-640 (pixel coords) or 0-1 (normalised) -- vision.py handles both |
| File size | ~11-12 MB (float32 YOLOv8n) |
| Pi inference | ~200 ms / ~5 FPS |

### NCNN (faster alternative)

| Property | Value |
|----------|-------|
| Input shape | `[1, 3, 640, 640]` (NCHW -- handled by NCNN internally) |
| Output shape | `[1, 5, 8400]` (same as TFLite) |
| Files | `model.ncnn.bin` + `model.ncnn.param` + `metadata.yaml` |
| File size | ~7 MB total |
| Pi inference | ~70 ms / ~15 FPS (expected) |
| Requirement | `pip install ncnn` on Pi |

### PyTorch (.pt)

| Property | Value |
|----------|-------|
| File size | ~6 MB |
| Use case | Future fine-tuning, re-export to other formats |
| NOT for Pi | Requires full PyTorch + Ultralytics (too heavy for Pi) |

---

## Troubleshooting

### "Model input shape mismatch"
Export was done with wrong `imgsz`. Re-export on Colab with `imgsz=640`.

### TFLite file is 3.3 MB instead of ~12 MB
This is likely the old model format. The retrained float32 model is larger. Both
work -- the size difference is due to export settings, not architecture.

### Detection rate drops compared to v2
- Check training curves (`results.png`) -- was training loss still decreasing?
- Verify dataset quality: open random images in `dataset_v3/images/`, check labels
- Try lowering confidence threshold: edit `CONFIDENCE_THRESHOLD` in `config.py`
- Compare models on DJI video: `python tests/laptop/video_test_compare.py`

### NCNN crashes on Pi
- Verify `ncnn` package is installed: `pip install ncnn`
- Check model files exist: `ls cv_models/sar_v3/ncnn/best_ncnn_model/`
- Try TFLite instead (always works, just slower)

### "No module named tflite_runtime"
On Pi with Python 3.13, use `ai-edge-litert` instead:
```bash
pip install ai-edge-litert
```
vision.py tries both automatically.

---

## Model History

| Version | Location | Dataset | imgsz | mAP50 | Notes |
|---------|----------|---------|-------|-------|-------|
| v1 | `best.tflite` (root, 3.3MB) | 200 syn at 640 | 640 | ~0.95 | Original, single background |
| sar_640 | `cv_models/sar_640/` | Improved syn | 640 | -- | Earlier experiment |
| sar_1280 | `cv_models/sar_1280/` | Improved syn | 1280 | -- | Earlier experiment |
| sar_v2_1088 | `cv_models/sar_v2_1088/` | 300 syn + 16 real + 50 neg | 1088 | 0.995 | Current best |
| **sar_v3** | `cv_models/sar_v3/` | 500 syn + real + 100 neg | 1088 | TBD | **This guide** |

---

## Quick Reference (Copy-Paste Commands)

```bash
# === LAPTOP ===
# 1. Generate dataset
python training/generate_dataset_v2.py --count 500 --negatives 100 --output dataset_v3

# 2. Zip
# (Windows) Right-click dataset_v3 -> Send to -> Compressed
# (Linux)   zip -r dataset_v3.zip dataset_v3/

# 3. Train on Colab (see cells above)

# 4. Save model
mkdir cv_models\sar_v3
copy export\best_float32.tflite cv_models\sar_v3\best.tflite
copy export\best.pt cv_models\sar_v3\

# 5. Quick swap
copy cv_models\sar_v3\best.tflite best.tflite

# 6. Push
git add best.tflite cv_models/sar_v3/
git commit -m "Deploy sar_v3 model"
git push

# === PI (SSH) ===
cd ~/sar-drone && git pull
python tests/hardware/benchmark.py
python passive_watch.py --headless
```
