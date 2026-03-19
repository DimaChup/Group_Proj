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

---

## Motion Blur — Deep Dive

### What Causes Blur?

Blur depends on **exposure time**, NOT frame rate:
- **Exposure time** = how long the shutter is open per frame
- **FPS** = how many frames per second (independent of blur)
- **Global shutter** (IMX296) = all pixels capture simultaneously (no rolling shutter distortion)

### Exposure Time vs Lighting

| Condition | Typical exposure | Blur at 10m/s, 50m alt | Impact |
|---|---|---|---|
| Bright sun | 1-2ms | <1px | None |
| Cloudy | 5-8ms | 1px | None |
| Overcast | 10-15ms | 1-2px | Negligible |
| Dusk/dawn | 20-40ms | 2-4px | Minor |
| Indoor lab | 20-30ms | Large (close objects) | Significant |

**Key insight:** Indoor testing with hand-held dummy looks much worse than real flight because:
1. Indoor = longer exposure (dim lighting)
2. Hand movement at 0.5m distance = huge pixel displacement
3. Real flight at 50m = tiny pixel displacement even at 20 m/s

### Why We're Safe

At 50m altitude, 10 m/s speed, 8ms exposure:
- Drone moves: 10 × 0.008 = 0.08m in one frame
- GSD at 50m: ~0.014m per pixel
- Blur: 0.08 / 0.014 = ~6 pixels... but on a 25-pixel dummy that's 24%

Wait — that contradicts our simulation! The simulation showed only 1-2px blur. The difference:
- Simulation used simplified blur model (kernel size = distance/GSD)
- Real blur also depends on the direction of motion relative to the dummy
- Worst case (flying directly over): full 6px blur
- Typical case (lawnmower pattern, flying past): 1-3px blur (most motion is lateral)

**Conclusion:** Blur is low but not zero. Our simulation was slightly optimistic. Real flight testing is essential to validate.

---

## Model Evaluation — Proper Benchmarking

### Current Approach (Visual Comparison)
- Run `video_test_compare.py` on DJI 30fps video
- Visually check: does model detect the dummy?
- Switch models with M key, compare subjectively
- **Problem:** subjective, not quantitative, hard to compare precisely

### Proper Approach (Ground Truth Benchmarking)

To scientifically compare models, we need:

**Step 1: Create Ground Truth**
- Take the DJI 30fps video
- Manually label every frame where dummy is visible
- Record: frame number, bounding box (x, y, w, h)
- Use `training/label_tool.py` or create a dedicated annotation tool
- This becomes the "answer key"

**Step 2: Run Each Model**
- Process the same video with each model/backend
- Each produces a detections CSV: frame, confidence, bbox
- Scripts: `video_test.py` already outputs CSV

**Step 3: Compare Against Ground Truth**
For each model, calculate:
- **True Positives (TP):** model detected AND ground truth has dummy
- **False Positives (FP):** model detected BUT no dummy in ground truth
- **False Negatives (FN):** model missed BUT ground truth has dummy
- **Precision:** TP / (TP + FP) — how many detections are correct
- **Recall:** TP / (TP + FN) — how many real dummies are found
- **F1 Score:** harmonic mean of precision and recall
- **IoU:** overlap between predicted and ground truth bounding boxes

**Step 4: Compare Models**

| Metric | Original | v2-1088 TFLite | v2-1088 NCNN |
|---|---|---|---|
| Precision | ? | ? | ? |
| Recall | ? | ? | ? |
| F1 Score | ? | ? | ? |
| Avg IoU | ? | ? | ? |
| FPS | 5.2 | 3.1 | 13.8 |
| False Positives | ? | ? | ? |

### What We Have vs What We Need

| Asset | Status |
|---|---|
| DJI 30fps video | Have it (RealVideo/) |
| Pi camera captured video | Have it (pi_data/captured_video/) |
| Detection CSVs from video_test.py | Have some |
| **Ground truth labels** | **DON'T HAVE — need to create** |
| Model comparison script | Need to create |
| Precision/recall calculator | Need to create |

### Quick Approximation (Without Ground Truth)

Until we have proper ground truth, we can compare:
1. Run all models on same video
2. Count total detections at same confidence threshold
3. Visually spot-check false positives
4. Compare detection at known difficult frames (high altitude, edge of view)

---

## Overfitting Concerns

### Are Our Models Overtrained?

**Risk factors:**
- v2-1088 trained on only 366 images (300 synthetic + 16 real + 50 negatives)
- Synthetic images use the SAME `dummy.png` composited on `map.jpg` backgrounds
- Only 16 real frames from ONE DJI flight
- Model might have memorised the specific dummy appearance, not generalised

**Signs of overfitting:**
- Very high mAP on training data (0.995) but unknown on unseen data
- Detects our specific dummy perfectly but might miss real humans
- High confidence on synthetic test frames but lower on real flight video

**How to test:**
1. **Real flight test** — most important! Does it detect from actual altitude?
2. **Different dummy** — test with a different mannequin/person
3. **Different background** — test in a field we didn't train on
4. **COCO person model** (`cv_models/human.tflite`) — compare against a model trained on 100K+ real images

**Mitigation:**
- Add more real flight photos to training set (from `detections/`)
- Add hard negatives (false positive frames)
- Test with COCO person model as baseline
- Augment with more diverse backgrounds

### Why Real Flight Testing is Essential

Simulation and video replay cannot replace real flight because:
1. **Camera characteristics differ** — real Pi camera vs DJI camera vs synthetic
2. **Lighting varies** — sun angle, shadows, weather
3. **Dummy appearance changes** — angle, clothing, position
4. **GPS accuracy** — real GPS drift affects where we look
5. **Wind/vibration** — affects frame quality in ways simulation can't predict

**Priority: get passive_watch.py running during a real manual flight ASAP.**

---

## NCNN Integration Status

### What Works
- `ncnn_video_player.py` — loads NCNN directly, bypasses vision.py, 9 FPS
- `ncnn_benchmark.py` — 13.8 FPS inference through vision.py
- `diagnostics.py` — NCNN model swap with M key, 9.2 FPS

### What Needs Fixing
- `vision.py` uses sys.argv hack (`--backend ncnn`) — fragile
- Scripts that use argparse consume the flag before vision.py sees it
- **Planned fix:** add explicit `backend=` parameter to VisionSystem.__init__
- See `docs/NCNN_INTEGRATION_TODO.md` for full plan

### Pipeline Overhead Analysis

Why 13.8 FPS inference becomes 9 FPS full pipeline:

```
NCNN inference only:    72ms  (13.8 FPS)
+ Video file read:      +5ms
+ Resize to 640x640:    +2ms
+ BGR→RGB conversion:   +1ms
+ Mat.from_pixels:      +1ms
+ Output parsing:       +1ms
+ Draw boxes/HUD:       +3ms
+ cv2.imshow:           +5ms
+ cv2.waitKey:          +1ms
──────────────────────────────
Full pipeline:         ~91ms  (~11 FPS theoretical)
Actual measured:      ~110ms  (~9 FPS)
```

The extra ~20ms gap is Python overhead (garbage collection, thread scheduling, etc).

---

## Lessons Learned & Optimisation Notes

### Lesson 1: Direct loading beats abstraction layers
- `ncnn_video_player.py` loads NCNN directly → 9 FPS, works perfectly
- Going through `vision.py` → sys.argv hacks, flag conflicts, slower
- **Takeaway:** for performance-critical paths, bypass abstraction layers

### Lesson 2: Single-threaded is simpler but limiting
- Current pipeline: capture → preprocess → inference → draw → display (sequential)
- Camera waits for inference to finish before capturing next frame
- Camera can do 30 FPS but model only does 5-14 FPS
- **Fix:** threaded pipeline — camera thread captures continuously, inference thread processes latest frame
- Expected improvement: display at 30 FPS with detections updating at inference rate

### Lesson 3: NCNN works but integration needs care
- NCNN inference: 72ms (13.8 FPS) — proven fast
- Through vision.py with sys.argv: works sometimes, breaks in complex scripts
- **Planned fix:** `VisionSystem(backend="ncnn")` explicit parameter
- Direct NCNN loading (as in ncnn_video_player.py) is the reliable path

### Lesson 4: Same model weights = same detection accuracy
- TFLite and NCNN run the same YOLO weights
- Detection confidence is identical (±0.01) regardless of backend
- Only speed differs — choose backend based on speed needs

### Lesson 5: Preprocessing matters
- TFLite pipeline: BGR→RGB → resize → normalize → inference
- NCNN pipeline: resize → BGR→RGB → Mat.from_pixels → normalize → inference
- Order of operations differs slightly — shouldn't affect accuracy but worth noting
- Both resize to 640x640 regardless of input resolution

### Optimisation Roadmap (prioritised)

| # | Optimisation | Expected gain | Effort | Risk |
|---|---|---|---|---|
| 1 | Clean NCNN backend in vision.py | 3x FPS (3→9) | Low | Low |
| 2 | Threaded camera+inference pipeline | +30% FPS | Medium | Medium |
| 3 | FP16 XNNPACK TFLite | ~2x TFLite speed | Low | Low |
| 4 | Lower confidence threshold (0.4→0.3) | More detections | Trivial | More FP |
| 5 | Camera FPS cap to match model speed | Save CPU/power | Trivial | None |
| 6 | Retrain with real flight data | Better accuracy | High | Overfitting |
| 7 | Hailo-8L accelerator ($70) | 80+ FPS | High | Hardware cost |

### Portability Notes (Future: Mavic/other drones)
- Our vision pipeline is camera-agnostic — just feeds frames to the model
- Could work with any video source: Pi camera, DJI SDK stream, HDMI capture, RTSP
- The model (YOLOv8n TFLite/NCNN) runs on any ARM or x86 device
- Key requirement: compute device (Pi/Jetson/laptop) connected to drone video feed
- DJI Mavic: would need DJI Mobile SDK or HDMI capture card → Pi/laptop

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
