# Video Analysis Setup (Working Configuration)

## Quick Start
```bash
# Activate test_env (has Ultralytics + TFLite)
test_env\Scripts\activate

# Run video detection test
python tests/laptop/video_test.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --model best.tflite
```

## Working Configuration (verified 2026-03-16)
| Setting | Value | Notes |
|---------|-------|-------|
| Video | `DJI_0001_1456x1088_cropped_30fps.mp4` | MUST use 30fps — SRT syncs with 30fps frames |
| Resolution | 1456x1088 | Cropped from 3840x2160 DJI 4K |
| Model | `best.tflite` (3.3MB YOLOv8n) | Original custom dummy detector |
| Tiling | 640px, 25% overlap | ~6 tiles per frame, press T to toggle |
| FOV | **54.4 deg HFOV** | Calibrated from 9 samples across 15-50m altitude |
| Confidence | 0.3 | Default, catches most detections |
| Environment | `test_env` | Has Ultralytics backend for TFLite |
| Inference | ~1000ms per frame | Tiled detection on laptop CPU |

## Controls
| Key | Action |
|-----|--------|
| SPACE | Pause/play |
| T | Toggle tiling on/off |
| A/D | Skip 5 seconds back/forward |
| +/- | Speed up/slow down |
| Q | Quit |
| Right-click x2 | Measure distance on main video (meters at current altitude) |
| Middle-click | Clear measurement |

## Windows
1. **Video Detection Test** — main video with detection boxes, scale bar (1m), telemetry overlay
2. **Latest Detection** — snapshot of most recent inference (clean image + info below)
3. **Best Detection (most central)** — best snapshot, left-click x2 to measure
4. **Target GPS Estimates** — two scatter plots (center distance + altitude colored)

All windows are resizable (drag corners, proportions preserved).

## Important: Video/SRT Sync
- SRT telemetry has one entry per frame at **30fps** (6854 entries)
- **30fps video** (6854 frames) matches SRT perfectly
- **6fps video** (1370 frames) does NOT match — altitudes will be wrong
- Always use `DJI_0001_1456x1088_cropped_30fps.mp4` for analysis

## FOV Calibration
Calibrated using `tools/fov_calibrate_video.py`:
- Known dummy height: 1.8m
- 9 samples across 15-50m altitude
- Focal length: 1416 px (+/- 41)
- **HFOV: 54.4 deg**
- Dummy measures 1.7-1.9m consistently at all altitudes

To recalibrate:
```bash
python tools/fov_calibrate_video.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --known-height 1.8
```
Scroll to zoom, right-click top then bottom of dummy at different altitudes. Press Q for results.

## Models Available
| Model | Location | Size | Notes |
|-------|----------|------|-------|
| best.tflite | project root | 3.3MB | Original YOLOv8n dummy detector (current) |
| sar_v2_1088 | cv_models/ | 12MB | Retrained on real+synthetic 1088 data (mAP50=0.995) |
| sar_640 | cv_models/ | 12MB | Earlier training, 640x640 |
| sar_1280 | cv_models/ | 13MB | Earlier training, 1280x1280 |
| human.tflite | models/ | 13MB | COCO person detector (80 classes, backup) |

To test a different model:
```bash
python tests/laptop/video_test.py "RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4" --model cv_models/sar_v2_1088/best.tflite
```

## Dataset (for retraining)
- `dataset_v2/` — 366 images at 1456x1088 (300 synthetic + 16 real labelled + 50 negatives)
- `dataset_v2.zip` — ready for Colab upload
- `tools/label_tool.py --full` — label real frames without squishing
- `generate_dataset_v2.py` — generate synthetic + negatives
- Training: see Colab cells in session log (imgsz=1088, epochs=150, batch=8)
