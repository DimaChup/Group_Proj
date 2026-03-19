# Computer Vision — Findings & Benchmarks

Date: 2026-03-19

---

## Models

| Model | Size | Trained on | Input shape |
|---|---|---|---|
| Original (`best.tflite`) | 3.2MB | Synthetic 640x640 | [1,640,640,3] |
| **v2-1088** (`cv_models/sar_v2_1088/best.tflite`) | 11.7MB | 300 syn + 16 real + 50 neg at 1088 | [1,640,640,3] |
| sar_640 | 11.7MB | Earlier training at 640 | [1,640,640,3] |
| sar_1280 | 12.3MB | Earlier training at 1280 | [1,1280,1280,3] |
| human (COCO) | 12.2MB | COCO 80 classes | [1,640,640,3] |

**Best model: v2-1088** — trained on real aerial data, mAP50=0.995

---

## Inference Backends

### TFLite (TensorFlow Lite)
- Google's mobile inference engine
- Uses XNNPACK delegate for CPU optimization
- Available via `ai-edge-litert` (Python 3.13) or `tflite-runtime`
- Loads `.tflite` model files

### NCNN (Neural Network Computing on Mobile)
- Tencent's inference engine, ARM-optimized
- Hand-tuned NEON SIMD assembly for ARM chips (Pi 5)
- Loads `.ncnn.param` + `.ncnn.bin` files
- Exported from same YOLO model — identical detection accuracy

**Why NCNN is faster:** NCNN has hand-written ARM assembly for each neural network operation (convolution, pooling, etc.), specifically optimized for ARM NEON SIMD instructions. TFLite uses a more generic approach (XNNPACK) that works on any CPU but isn't as optimized for ARM.

---

## Pi 5 Benchmark Results (2026-03-19)

### Inference Only (no camera, no display)

| Backend | Model | Avg ms | FPS |
|---|---|---|---|
| TFLite | Original (3.2MB) | 192ms | 5.2 |
| TFLite | v2-1088 (11.7MB) | 319ms | 3.1 |
| TFLite | human COCO (12.2MB) | 358ms | 2.8 |
| TFLite | sar_1280 (12.3MB) | 1351ms | 0.7 |
| **NCNN** | **v2-1088 (11.7MB)** | **72ms** | **13.8** |

### Full Pipeline (video file + preprocess + inference + draw + display)

| Backend | Model | Avg ms | FPS | Overhead |
|---|---|---|---|---|
| TFLite | Original (3.2MB) | 194ms | 5.2 | +2ms (1%) |
| TFLite | v2-1088 (11.7MB) | 329ms | 3.0 | +10ms (3%) |
| **NCNN** | **v2-1088** | **~110ms** | **~9** | **~38ms (35%)** |

### Full Pipeline with Camera (capture + preprocess + inference + draw + stream)

| Backend | Model | FPS | Source |
|---|---|---|---|
| TFLite | Original | ~4.5 | passive_watch.py |
| TFLite | v2-1088 | ~3.0 | passive_watch.py |
| **NCNN** | **v2-1088** | **~9.2** | diagnostics.py |

---

## Pipeline Comparison

### TFLite Pipeline
```
Frame → BGR2RGB → Resize 640x640 → Normalize /255 → TFLite invoke → Parse output → Draw
        ~1ms       ~2ms              ~1ms             ~320ms          ~1ms          ~1ms
Total: ~326ms per frame (3.1 FPS)
```

### NCNN Pipeline
```
Frame → Resize 640x640 → BGR2RGB → Mat.from_pixels → Normalize → NCNN extract → Parse → Draw
        ~2ms              ~1ms      ~1ms               ~1ms        ~72ms          ~1ms    ~1ms
Total: ~79ms per frame (12.7 FPS)
```

**NCNN is 4.1x faster at inference** because:
- Hand-tuned ARM NEON SIMD assembly
- Optimized memory layout for ARM cache hierarchy
- No Python overhead in core compute (C++ with Python bindings)

---

## Detection vs Altitude

Tested with synthetic frames (dummy.png on map.jpg backgrounds).

### v2-1088 Model (best)

| Altitude | Dummy size (px) | Confidence | Status |
|---|---|---|---|
| 15m | 83px | 0.91 | Excellent |
| 20m | 62px | 0.90 | Excellent |
| 25m | 50px | 0.92 | Excellent |
| 30m | 41px | 0.91 | Excellent |
| 40m | 31px | 0.89 | Good |
| 50m | 25px | 0.84 | Good |
| **60m** | **20px** | **0.84** | **Reliable limit** |
| 80m | 15px | 0.66 | Unreliable |

### Original Model

| Altitude | Confidence | vs v2-1088 |
|---|---|---|
| 30m | 0.90 | Similar |
| 40m | 0.74 | v2 +15% better |
| 50m | 0.68 | v2 +15% better |
| 60m | 0.47 | **v2 +37% better** |
| 80m | MISS | v2 still detects |

**v2-1088 is dramatically better above 40m** — the altitude that matters for SAR search.

---

## Motion Blur Analysis

### Does blur matter?

**NO.** The IMX296 global shutter camera produces negligible blur at all realistic speeds:

| Altitude | Speed | Blur (pixels) | % of dummy | Effect |
|---|---|---|---|---|
| 50m | 5 m/s | 1px | 4% | None |
| 50m | 10 m/s | 1px | 4% | None |
| 50m | 20 m/s | 2px | 8% | Negligible |
| 30m | 20 m/s | 3px | 7% | Negligible |
| 15m | 20 m/s | 7px | 8% | Negligible |

**Why:** IMX296 global shutter has ~8ms exposure outdoors. At 20 m/s the drone moves 0.16m in 8ms. At 50m altitude that's only 2 pixels of blur.

**The limiting factor is ALTITUDE (dummy pixel size), not speed/blur.**

### Laptop Prediction vs Pi Actual

Detection results matched within ±0.01 confidence — laptop predictions fully validated on Pi.

---

## Recommendations

### For Flight Day
- **Use v2-1088 model** — best at high altitude detection
- **Use NCNN backend** — 3x faster than TFLite (9 FPS vs 3 FPS)
- **Fly at 50m** — 0.84 confidence, reliable detection
- **Max altitude: 60m** — below this is reliable
- **Speed: any** — blur is not a factor

### Configuration
```bash
# Best setup on Pi
source ncnn_env/bin/activate
cp cv_models/sar_v2_1088/best.tflite best.tflite
python main.py --search-area --model cv_models/sar_v2_1088/best.tflite --backend ncnn --alt 50
```

### Test Scripts
```bash
# NCNN video test (Pi screen)
python tests/laptop/ncnn_video_player.py

# TFLite video test (Pi screen)
python tests/laptop/tflite_video_player.py

# Benchmark all models
python tests/day_1_experiments/model_compare.py --frames 30

# NCNN vs TFLite benchmark
python tests/hardware/ncnn_benchmark.py --camera

# Blur + altitude simulation
python tests/laptop/blur_altitude_test.py --model cv_models/sar_v2_1088/best.tflite
```

### Future Improvements
- FP16 XNNPACK for TFLite (~2x speedup, untested)
- Threaded pipeline (camera + inference in parallel)
- Lower confidence threshold for more detections
- Retrain with more real flight data (hard negatives from false positives)
- NCNN integration into vision.py for seamless backend switching

---

## Environment Setup

| Env | Platform | Packages | Use for |
|---|---|---|---|
| `pienv` | Pi | pymavlink, opencv, numpy, ai-edge-litert | TFLite scripts |
| `ncnn_env` | Pi | all of pienv + ncnn | NCNN scripts |
| `venv` | Laptop | TensorFlow, PyTorch, OpenCV | Simulation, main.py |
| `test_env` | Laptop | Ultralytics, TFLite, ncnn | Video analysis |

---

## Key Files

| File | What |
|---|---|
| `vision.py` | AI backend (Ultralytics / TFLite / NCNN) |
| `cv_models/sar_v2_1088/best.tflite` | Best TFLite model |
| `cv_models/sar_v2_1088/ncnn/best_ncnn_model/` | Best NCNN model |
| `pi_data/benchmark_results.txt` | All benchmark history |
| `pi_data/blur_altitude_results.txt` | All blur/altitude tests |
| `pi_data/blur_altitude_chart.png` | Comparison charts |
| `pi_data/BLUR_ALTITUDE_COMPARISON.md` | Full analysis |
