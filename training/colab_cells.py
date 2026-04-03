"""
Copy-paste-ready Google Colab cells for YOLOv8n SAR dummy detector training.

Instructions:
  1. Open Google Colab: https://colab.research.google.com
  2. Set runtime to GPU: Runtime > Change runtime type > T4 GPU
  3. Copy each cell (between === markers) into a new Colab cell
  4. Run cells in order (Shift+Enter)

Prerequisites:
  - dataset_v3.zip uploaded to Google Drive root
  - Dataset generated with: python training/generate_dataset_v2.py --count 500 --negatives 100 --output dataset_v3

Parameters from docs/CV_BEST_PRACTICES.md and docs/TRAINING_WORKFLOW_V3.md.
"""


# =============================================================================
# === CELL 1: Install Ultralytics =============================================
# =============================================================================

# !pip install ultralytics
# import ultralytics
# ultralytics.checks()
# # Expected: Ultralytics version, Python, torch with CUDA, T4 GPU detected


# =============================================================================
# === CELL 2: Mount Drive & Unzip Dataset =====================================
# =============================================================================

# from google.colab import drive
# drive.mount('/content/drive')
#
# # Copy dataset from Drive to Colab local storage (faster I/O)
# !cp "/content/drive/MyDrive/dataset_v3.zip" /content/
# !unzip -q /content/dataset_v3.zip -d /content/
#
# # Verify contents
# !ls /content/dataset_v3/
# !echo "--- Image count ---"
# !ls /content/dataset_v3/images/ | wc -l
# !echo "--- Sample images ---"
# !ls /content/dataset_v3/images/ | head -10
# !echo "--- Label line counts (last 5) ---"
# !wc -l /content/dataset_v3/labels/*.txt | tail -5
#
# # Expected: dataset.yaml, images/, labels/ directories. 600+ files in images.


# =============================================================================
# === CELL 3: Fix dataset.yaml Paths for Colab ================================
# =============================================================================

# import yaml
#
# yaml_path = '/content/dataset_v3/dataset.yaml'
#
# with open(yaml_path, 'r') as f:
#     data = yaml.safe_load(f)
#
# # Point paths to Colab filesystem
# data['path'] = '/content/dataset_v3'
# data['train'] = 'images'
# data['val'] = 'images'
#
# with open(yaml_path, 'w') as f:
#     yaml.dump(data, f)
#
# print("Updated dataset.yaml:")
# !cat /content/dataset_v3/dataset.yaml
#
# # Expected output:
# #   names:
# #   - dummy
# #   nc: 1
# #   path: /content/dataset_v3
# #   train: images
# #   val: images
# #
# # NOTE: Using same images for train+val inflates metrics. For rigorous
# # evaluation, split 80/20. For our use case (small dataset, visual
# # verification on real video), this is acceptable.


# =============================================================================
# === CELL 4: Train ============================================================
# =============================================================================
# All parameters from docs/CV_BEST_PRACTICES.md Section 3.

# from ultralytics import YOLO
#
# model = YOLO('yolov8n.pt')  # pretrained COCO weights (downloads automatically)
#
# results = model.train(
#     data='/content/dataset_v3/dataset.yaml',
#
#     # --- Core ---
#     imgsz=640,              # Match TFLite inference size [1,640,640,3]
#     epochs=250,             # More epochs for small dataset (early stopping will cut short)
#     batch=16,               # Colab T4 limit. Use 8 if OOM.
#     patience=50,            # Early stopping if val loss plateaus for 50 epochs
#     device=0,               # GPU
#
#     # --- Geometric augmentation ---
#     degrees=5,              # Slight rotation (drone tilt during flight)
#     scale=0.3,              # Zoom (simulates altitude variation)
#     fliplr=0.5,             # Horizontal flip (default)
#     flipud=0.1,             # Low prob vertical flip (drone can approach from any direction)
#     perspective=0.0005,     # Subtle camera angle variation
#
#     # --- Color augmentation ---
#     hsv_h=0.015,            # Hue jitter
#     hsv_s=0.7,              # Saturation jitter (lighting changes)
#     hsv_v=0.4,              # Brightness jitter (sun/cloud)
#
#     # --- Advanced augmentation ---
#     mosaic=1.0,             # Mosaic augmentation (critical for small objects)
#     close_mosaic=10,        # Disable mosaic for last 10 epochs (stabilise fine-tuning)
#     mixup=0.1,              # Light mixup blending
#     copy_paste=0.1,         # Paste dummy onto different backgrounds
#     erasing=0.3,            # Random erasing (partial occlusion by grass/shadow)
#
#     # --- Regularisation ---
#     label_smoothing=0.1,    # Prevents overconfident predictions, improves generalisation
#
#     # --- Output ---
#     project='runs/train',
#     name='sar_v3',
# )
#
# # Training takes ~30-60 min on T4.
# # Watch for box_loss and cls_loss decreasing steadily.
# # Final line shows mAP50 and mAP50-95.
# #
# # Target metrics:
# #   mAP50     > 0.95 (good), > 0.99 (great)
# #   mAP50-95  > 0.60 (good), > 0.80 (great)
# #   Precision > 0.90 (good), > 0.95 (great)
# #   Recall    > 0.90 (good), > 0.95 (great)
# #
# # If mAP50 < 0.90, something is wrong -- check dataset labels.


# =============================================================================
# === CELL 5: Evaluate Results =================================================
# =============================================================================

# from IPython.display import Image, display
#
# # Training curves (loss, mAP over epochs)
# display(Image('runs/train/sar_v3/results.png'))
#
# # Confusion matrix
# display(Image('runs/train/sar_v3/confusion_matrix.png'))
#
# # Normalised confusion matrix
# try:
#     display(Image('runs/train/sar_v3/confusion_matrix_normalized.png'))
# except:
#     pass
#
# # Sample predictions on val set
# try:
#     display(Image('runs/train/sar_v3/val_batch0_pred.png'))
# except:
#     pass

# --- Quantitative metrics ---

# metrics = model.val()
# print(f"mAP50:     {metrics.box.map50:.3f}")
# print(f"mAP50-95:  {metrics.box.map:.3f}")
# print(f"Precision: {metrics.box.mp:.3f}")
# print(f"Recall:    {metrics.box.mr:.3f}")


# =============================================================================
# === CELL 6: Export TFLite (primary Pi deployment) ============================
# =============================================================================
# Export at imgsz=640 to match inference pipeline in vision.py.
# Float32 -- FP16 TFLite has compatibility issues on Pi.

# model = YOLO('runs/train/sar_v3/weights/best.pt')
#
# model.export(
#     format='tflite',
#     imgsz=640,          # Must match inference pipeline [1,640,640,3]
#     half=False,         # Float32 (FP16 TFLite has compatibility issues)
#     int8=False,         # Keep float32 unless testing quantisation
#     nms=True,           # Include NMS in model graph
# )
#
# # Verify output
# import os
# tflite_path = 'runs/train/sar_v3/weights/best_float32.tflite'
# if os.path.exists(tflite_path):
#     print(f"TFLite model: {tflite_path}")
#     print(f"Size: {os.path.getsize(tflite_path) / 1e6:.1f} MB")
# else:
#     # Ultralytics may use different naming
#     import glob
#     for f in glob.glob('runs/train/sar_v3/weights/*.tflite'):
#         print(f"TFLite model: {f} ({os.path.getsize(f) / 1e6:.1f} MB)")
#
# # Expected: ~11-12 MB, input [1,640,640,3] float32, output [1,5,8400]


# =============================================================================
# === CELL 7: Export NCNN (faster on Pi, ~15 FPS) ==============================
# =============================================================================
# FP16 -- Pi 5 ARM has native FP16 support. ~2-3x faster than TFLite.

# model.export(
#     format='ncnn',
#     imgsz=640,
#     half=True,          # FP16 for Pi 5 ARM native support
# )
#
# # Verify output
# import os, glob
# ncnn_dirs = glob.glob('runs/train/sar_v3/weights/*_ncnn_model')
# if ncnn_dirs:
#     print(f"NCNN model dir: {ncnn_dirs[0]}")
#     for f in os.listdir(ncnn_dirs[0]):
#         fpath = os.path.join(ncnn_dirs[0], f)
#         size = os.path.getsize(fpath) if os.path.isfile(fpath) else 0
#         print(f"  {f}: {size / 1e6:.1f} MB" if size else f"  {f}/")
# else:
#     print("NCNN export not found -- check for errors above")
#
# # Expected: ~7 MB total (model.ncnn.bin + model.ncnn.param + metadata.yaml)
# # Requires `pip install ncnn` on Pi


# =============================================================================
# === CELL 8: Download All Artifacts ===========================================
# =============================================================================

# from google.colab import files
# import shutil, os, glob
#
# os.makedirs('export', exist_ok=True)
#
# # 1. Best weights (.pt) -- for future fine-tuning
# shutil.copy('runs/train/sar_v3/weights/best.pt', 'export/best.pt')
# print(f"best.pt: {os.path.getsize('export/best.pt') / 1e6:.1f} MB")
#
# # 2. TFLite model
# tflite_files = glob.glob('runs/train/sar_v3/weights/**/*.tflite', recursive=True)
# for f in tflite_files:
#     dest = f'export/{os.path.basename(f)}'
#     shutil.copy(f, dest)
#     print(f"TFLite: {os.path.basename(f)} ({os.path.getsize(f) / 1e6:.1f} MB)")
#
# # 3. NCNN model directory
# ncnn_dirs = glob.glob('runs/train/sar_v3/weights/*_ncnn_model')
# if ncnn_dirs:
#     shutil.copytree(ncnn_dirs[0], 'export/ncnn', dirs_exist_ok=True)
#     print(f"NCNN: copied {ncnn_dirs[0]}")
#     for f in os.listdir(ncnn_dirs[0]):
#         print(f"  {f}")
# else:
#     print("NCNN: not found (run Cell 7 first)")
#
# # 4. Training artifacts
# for f in ['results.png', 'confusion_matrix.png', 'confusion_matrix_normalized.png']:
#     src = f'runs/train/sar_v3/{f}'
#     if os.path.exists(src):
#         shutil.copy(src, f'export/{f}')
#         print(f"Artifact: {f}")
#
# # 5. Zip and trigger browser download
# shutil.make_archive('sar_v3_export', 'zip', 'export')
# zip_size = os.path.getsize('sar_v3_export.zip') / 1e6
# print(f"\nDownloading sar_v3_export.zip ({zip_size:.1f} MB)...")
# files.download('sar_v3_export.zip')
#
# # Expected: ~18-20 MB zip containing:
# #   best.pt               ~6 MB   (full YOLO weights for future fine-tuning)
# #   best_float32.tflite   ~12 MB  (TFLite for Pi: cp to best.tflite)
# #   ncnn/                 ~7 MB   (NCNN for Pi: faster inference)
# #   results.png                   (training curves)
# #   confusion_matrix.png          (confusion matrix)
#
# # === DEPLOYMENT (on laptop after download) ===
# # mkdir cv_models\sar_v3
# # copy export\best_float32.tflite cv_models\sar_v3\best.tflite
# # copy export\best.pt cv_models\sar_v3\
# # xcopy /E /I export\ncnn cv_models\sar_v3\ncnn
# #
# # Quick swap:  copy cv_models\sar_v3\best.tflite best.tflite
# # Or use flag: python main.py --model cv_models/sar_v3/best.tflite
