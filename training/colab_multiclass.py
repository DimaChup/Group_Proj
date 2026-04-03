"""
Copy-paste-ready Google Colab cells for multi-class YOLOv8n SAR detector training.

5 classes: dummy (0), cone (1), pants (2), tshirt (3), backpack (4)

Instructions:
  1. Open Google Colab: https://colab.research.google.com
  2. Set runtime to GPU: Runtime > Change runtime type > T4 GPU
  3. Copy each cell (between === markers) into a new Colab cell
  4. Run cells in order (Shift+Enter)

Prerequisites:
  - dataset_multiclass.zip uploaded to Google Drive root
  - Generated with: python training/generate_dataset_multiclass.py --count 600 --negatives 50 --size 1088
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
# !cp "/content/drive/MyDrive/dataset_multiclass.zip" /content/
# !unzip -q /content/dataset_multiclass.zip -d /content/
#
# # Verify structure
# !echo "=== Directory structure ==="
# !find /content/dataset_multiclass -type d
# !echo ""
# !echo "=== Train images ==="
# !ls /content/dataset_multiclass/images/train/ | wc -l
# !echo "=== Val images ==="
# !ls /content/dataset_multiclass/images/val/ | wc -l
# !echo ""
# !echo "=== Sample labels (multi-class check) ==="
# !head -5 /content/dataset_multiclass/labels/train/syn_da_00000.txt 2>/dev/null || echo "(check filename)"
# !echo ""
# !echo "=== Class distribution ==="
# !cat /content/dataset_multiclass/labels/train/*.txt | cut -d' ' -f1 | sort | uniq -c | sort -rn
# !echo "--- Val ---"
# !cat /content/dataset_multiclass/labels/val/*.txt | cut -d' ' -f1 | sort | uniq -c | sort -rn
#
# # Fix dataset.yaml path to point to Colab location
# !sed -i 's|^path:.*|path: /content/dataset_multiclass|' /content/dataset_multiclass/dataset.yaml
# !cat /content/dataset_multiclass/dataset.yaml
#
# # Expected: dataset.yaml with 5 classes, images/train, images/val,
# #           labels/train, labels/val. ~500+ train, ~120+ val images.


# =============================================================================
# === CELL 3: Train YOLOv8n (multi-class) =====================================
# =============================================================================

# from ultralytics import YOLO
#
# model = YOLO('yolov8n.pt')  # Start from pretrained COCO weights
#
# results = model.train(
#     data='/content/dataset_multiclass/dataset.yaml',
#     imgsz=1088,         # Native Pi camera resolution (match --size used in generator)
#     epochs=150,          # 150 epochs (same as v2 training)
#     batch=8,             # Batch size (adjust if OOM: try 4 or 6)
#     patience=30,         # Early stopping patience
#     lr0=0.01,            # Initial learning rate
#     lrf=0.01,            # Final learning rate (lr0 * lrf)
#     mosaic=1.0,          # Mosaic augmentation
#     mixup=0.1,           # Mixup augmentation
#     degrees=15.0,        # Rotation augmentation (+/- degrees)
#     flipud=0.5,          # Vertical flip (drone can approach from any direction)
#     fliplr=0.5,          # Horizontal flip
#     hsv_h=0.015,         # HSV-Hue augmentation
#     hsv_s=0.7,           # HSV-Saturation augmentation
#     hsv_v=0.4,           # HSV-Value augmentation
#     translate=0.2,       # Translation augmentation
#     scale=0.5,           # Scale augmentation
#     project='runs/multiclass',
#     name='sar_multiclass',
#     exist_ok=True,
#     verbose=True,
# )
#
# # Expected: ~150 epochs, mAP50 > 0.9 for all classes.
# # Training takes ~15-30 min on T4 GPU depending on dataset size.


# =============================================================================
# === CELL 4: Validate ========================================================
# =============================================================================

# from ultralytics import YOLO
#
# model = YOLO('runs/multiclass/sar_multiclass/weights/best.pt')
#
# # Validate on the validation split
# metrics = model.val(
#     data='/content/dataset_multiclass/dataset.yaml',
#     imgsz=1088,
#     batch=8,
#     verbose=True,
# )
#
# # Print per-class metrics
# print("\n=== Per-class mAP50 ===")
# class_names = ['dummy', 'cone', 'pants', 'tshirt', 'backpack']
# for i, name in enumerate(class_names):
#     if i < len(metrics.box.ap50):
#         print(f"  {name:10s}: mAP50 = {metrics.box.ap50[i]:.3f}")
#
# print(f"\n  Overall mAP50:    {metrics.box.map50:.3f}")
# print(f"  Overall mAP50-95: {metrics.box.map:.3f}")
#
# # Expected: mAP50 > 0.9 for each class, overall > 0.95


# =============================================================================
# === CELL 5: Export to TFLite ================================================
# =============================================================================

# from ultralytics import YOLO
#
# model = YOLO('runs/multiclass/sar_multiclass/weights/best.pt')
#
# # Export to TFLite (float32 — best accuracy, ~12MB)
# model.export(
#     format='tflite',
#     imgsz=1088,          # Must match training imgsz
# )
#
# # Also export to NCNN (faster on Pi, ~15 FPS vs ~5 FPS TFLite)
# model.export(
#     format='ncnn',
#     imgsz=1088,
# )
#
# # Verify exports
# import os
# tflite_path = 'runs/multiclass/sar_multiclass/weights/best_saved_model/best_float32.tflite'
# if os.path.exists(tflite_path):
#     size_mb = os.path.getsize(tflite_path) / (1024 * 1024)
#     print(f"TFLite model: {tflite_path} ({size_mb:.1f} MB)")
# else:
#     # Try alternate path
#     import glob
#     tflite_files = glob.glob('runs/multiclass/sar_multiclass/weights/*.tflite')
#     for f in tflite_files:
#         size_mb = os.path.getsize(f) / (1024 * 1024)
#         print(f"TFLite model: {f} ({size_mb:.1f} MB)")
#
# # Expected: best_float32.tflite (~12MB), ncnn/ directory


# =============================================================================
# === CELL 6: Download Models =================================================
# =============================================================================

# from google.colab import files
# import shutil
#
# # Download best.pt (full weights for future fine-tuning)
# files.download('runs/multiclass/sar_multiclass/weights/best.pt')
#
# # Download TFLite model (for Pi deployment)
# tflite_path = 'runs/multiclass/sar_multiclass/weights/best_saved_model/best_float32.tflite'
# if os.path.exists(tflite_path):
#     # Rename for easier deployment
#     shutil.copy(tflite_path, 'best_multiclass.tflite')
#     files.download('best_multiclass.tflite')
# else:
#     import glob
#     for f in glob.glob('runs/multiclass/sar_multiclass/weights/*.tflite'):
#         files.download(f)
#
# # Download NCNN model (zip the directory)
# ncnn_dir = 'runs/multiclass/sar_multiclass/weights/best_ncnn_model'
# if os.path.exists(ncnn_dir):
#     shutil.make_archive('best_multiclass_ncnn', 'zip', ncnn_dir)
#     files.download('best_multiclass_ncnn.zip')
#
# # Download training results (confusion matrix, curves)
# results_dir = 'runs/multiclass/sar_multiclass/'
# for f in ['results.png', 'confusion_matrix.png', 'confusion_matrix_normalized.png',
#           'PR_curve.png', 'F1_curve.png']:
#     path = os.path.join(results_dir, f)
#     if os.path.exists(path):
#         files.download(path)
#
# # === Deployment on Pi ===
# # 1. Copy best_multiclass.tflite to Pi: scp best_multiclass.tflite pi@PI_IP:~/sar-drone/best.tflite
# # 2. Update config.py class names if needed (vision.py handles multi-class output)
# # 3. Test: python tests/hardware/benchmark.py
#
# print("\n=== Download complete ===")
# print("Deploy to Pi:")
# print("  scp best_multiclass.tflite pi@PI_IP:~/sar-drone/best.tflite")
# print("  # OR for NCNN (faster):")
# print("  scp -r best_multiclass_ncnn/ pi@PI_IP:~/sar-drone/ncnn_model/")
