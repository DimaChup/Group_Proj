# Model Training Guide — YOLOv8n Dummy Detector

## Quick Summary

**What we did before:**
1. `generate_dataset.py` created 200 synthetic images (dummy.png composited on map.jpg)
2. Uploaded `project_data/` to Google Colab
3. Ran `train_model.py` on Colab GPU (~50 epochs, ~15 min)
4. Downloaded `best_float32.tflite` → copied to `best.tflite` in project root

**What we need to improve:**
- More images (1000+, not 200)
- Train/val split (currently same images for both — inflates accuracy)
- More diverse backgrounds (currently just one map.jpg)
- Negative images (10-15% with no dummy)
- Better augmentation (motion blur, brightness, shadows)

---

## Step-by-Step: Retrain on Google Colab

### 1. Prepare Dataset Locally

```bash
cd "c:\Users\Bristol\Desktop\AI for Robotics\v3"
python generate_dataset.py    # generates dataset/ with images + labels
```

**Dataset structure required:**
```
project_data/
├── data.yaml
└── dataset/
    ├── images/
    │   ├── train/     # 80% of images
    │   └── val/       # 20% of images
    └── labels/
        ├── train/     # matching .txt files
        └── val/       # matching .txt files
```

**IMPORTANT:** Train and val MUST be different images. Split them:
```python
# Quick split script (run once after generating)
import os, shutil, random
os.makedirs('dataset/images/train', exist_ok=True)
os.makedirs('dataset/images/val', exist_ok=True)
os.makedirs('dataset/labels/train', exist_ok=True)
os.makedirs('dataset/labels/val', exist_ok=True)

imgs = sorted(os.listdir('dataset/images'))
imgs = [f for f in imgs if f.endswith('.jpg')]
random.shuffle(imgs)
split = int(0.8 * len(imgs))

for f in imgs[:split]:
    shutil.move(f'dataset/images/{f}', f'dataset/images/train/{f}')
    shutil.move(f'dataset/labels/{f.replace(".jpg",".txt")}', f'dataset/labels/train/')
for f in imgs[split:]:
    shutil.move(f'dataset/images/{f}', f'dataset/images/val/{f}')
    shutil.move(f'dataset/labels/{f.replace(".jpg",".txt")}', f'dataset/labels/val/')
```

Update `data.yaml`:
```yaml
path: /content/project_data/dataset
train: images/train
val: images/val
nc: 1
names: ['dummy']
```

### 2. Zip and Upload to Colab

Zip `project_data/` folder and upload to Google Drive or directly to Colab.

### 3. Colab Notebook Cells

**Cell 1 — Setup:**
```python
!pip install ultralytics
import ultralytics
ultralytics.checks()
```

**Cell 2 — Upload dataset:**
```python
# Option A: From Google Drive
from google.colab import drive
drive.mount('/content/drive')
!cp /content/drive/MyDrive/project_data.zip /content/
!unzip -q /content/project_data.zip -d /content/

# Option B: Direct upload
from google.colab import files
uploaded = files.upload()  # select project_data.zip
!unzip -q project_data.zip -d /content/
```

**Cell 3 — Train:**
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # pretrained COCO weights

results = model.train(
    data='/content/project_data/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    patience=20,         # early stopping
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
    name='dummy_detect',
)
```

**Cell 4 — Check results:**
```python
# View training curves
from IPython.display import Image
Image('runs/dummy_detect/results.png')
```

```python
# Validate
metrics = model.val()
print(f"mAP50: {metrics.box.map50:.3f}")
print(f"mAP50-95: {metrics.box.map:.3f}")
```

**Cell 5 — Export to TFLite:**
```python
# Float32 (baseline, ~6MB)
model.export(format='tflite', imgsz=640)

# INT8 quantized (fastest on Pi, ~2MB)
model.export(format='tflite', imgsz=640, int8=True,
             data='/content/project_data/data.yaml')
```

**Cell 6 — Download:**
```python
from google.colab import files

# The .tflite file is inside the saved_model directory
import glob
tflite_files = glob.glob('runs/dummy_detect/weights/*.tflite') + \
               glob.glob('runs/dummy_detect/weights/**/*.tflite', recursive=True)
print("TFLite files found:", tflite_files)

# Download
for f in tflite_files:
    files.download(f)

# Also download best.pt (full weights, for future fine-tuning)
files.download('runs/dummy_detect/weights/best.pt')
```

### 4. Deploy to Pi

```bash
# On laptop: copy downloaded .tflite to project root
cp ~/Downloads/best_float32.tflite best.tflite

# Push to git
git add best.tflite
git commit -m "Retrained model v2"
git push

# On Pi: pull
cd ~/dima/Group_Proj && git pull
```

---

## Dataset Improvement Checklist

### More Images
- [ ] Generate 1000-1500 images (not 200)
- [ ] Change `NUM_IMAGES = 1500` in generate_dataset.py

### Background Diversity (BIGGEST impact)
- [ ] Collect 20-50 different aerial/grass background images
- [ ] Google Earth screenshots of the actual flight field
- [ ] Different grass types (mowed, wild, brown, green)
- [ ] Different lighting (sunny, overcast, shadows)
- [ ] Save as `backgrounds/*.jpg` and modify generate_dataset.py to use them

### Negative Images (10-15% of dataset)
- [ ] Include images with NO dummy (just background)
- [ ] Create matching empty .txt label files (0 bytes)
- [ ] Teaches model what "nothing here" looks like → fewer false positives

### Dummy Variations
- [ ] Multiple dummy images if possible (different angles, poses)
- [ ] Different clothing/colors on the dummy
- [ ] Partially occluded dummy (behind tall grass)

### Additional Augmentations (in generate_dataset.py)
- [ ] Motion blur (simulates drone movement)
- [ ] Brightness/contrast variation (sun vs shade)
- [ ] Gaussian noise (camera sensor noise)
- [ ] Shadow overlays (tree/building shadows on grass)

---

## Current generate_dataset.py Pipeline

What it does now:
1. Loads `map.jpg` (background) and `dummy.png` (foreground with alpha)
2. For each image:
   - Random 640×640 crop from map.jpg
   - Scale dummy to 10-40% (simulates altitude)
   - Random 0-360° rotation
   - Alpha-blend onto background at random position
3. Saves image + YOLO label (`0 x_center y_center width height`)

Parameters:
| Setting | Current | Recommended |
|---------|---------|-------------|
| NUM_IMAGES | 200 | 1000-1500 |
| IMG_SIZE | 640 | 640 (keep) |
| Scale range | 0.1-0.4 | 0.05-0.5 (wider range) |
| Backgrounds | 1 (map.jpg) | 20-50 different |
| Negatives | 0% | 10-15% |

---

## Model Variants for Flight Day

Export multiple models, bring all to flight day:

| Model | Size | Pi Speed | Use Case |
|-------|------|----------|----------|
| custom_float32.tflite | ~6MB | ~250ms | Default — best accuracy |
| custom_int8.tflite | ~2MB | ~120ms | Speed mode — search phase |
| human.tflite | ~13MB | ~300ms | COCO person fallback |

Swap on Pi: `cp models/X.tflite best.tflite` then restart script.

---

## Confidence Threshold

Current: 0.4 (in vision.py)

| Threshold | Best for |
|-----------|----------|
| 0.25 | Search phase (catch everything, accept false positives) |
| 0.35-0.4 | Balanced |
| 0.5+ | Verification (high confidence only) |

Can change in `config.py` → `CONFIDENCE_THRESHOLD` without retraining.

---

## Common Pitfalls

1. **Same images in train AND val** — metrics are meaningless. Always split.
2. **Only one background** — model memorizes grass texture, fails on real field.
3. **No negatives** — model always predicts something → false positives everywhere.
4. **Overfitting** — if train loss near 0 but val loss high, reduce epochs or add data.
5. **Wrong input format** — TFLite expects 0-255 uint8 input, NOT 0-1 float.
