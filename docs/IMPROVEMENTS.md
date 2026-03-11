# Improvements Roadmap

Ranked potential improvements with stepping stones, test scripts, and research sources.
Updated after each session. Items move from Backlog → In Progress → Done.

---

## Quick Reference: What To Do When

| When | Do This | Section |
|------|---------|---------|
| **Right now (zero effort)** | Lower confidence threshold to 0.3 | CV Quick Wins |
| **Before flight day** | Active cooler, vibration mounts, cable security, BEC power | Hardware Prep |
| **First flight opportunity** | Capture real training photos with capture_training.py | Training Data |
| **After first flight** | Retrain model on real data, try NCNN export | Model & Inference |
| **If budget allows ($70)** | Hailo-8L AI HAT+ for 60 FPS inference | Hardware Accelerator |
| **Between flights** | Improve ground station UX (thumbnails, alerts, coverage viz) | Ground Station UX |

---

## 1. CV Quick Wins (Zero/Low Effort)

### 1.1 Lower Confidence Threshold
- **Current:** 0.4 in vision.py (lines 174, 197)
- **Change to:** 0.25-0.3
- **Why:** For SAR, missing the target (false negative) is worse than investigating a bush (false positive). Your clustering system filters noise anyway.
- **Effort:** Change one number
- **Test:** Run altitude_sweep experiment, compare detection rates

### 1.2 Lock Camera Exposure for Flight
- **Current:** Auto-exposure (default picamera2)
- **Change to:** `ExposureTime: 2500` (1/400s) in picamera2 config
- **Why:** At 5 m/s from 15m, auto-exposure may choose long exposure → motion blur → missed detections
- **Where:** vision.py, picamera2 `set_controls()` call
- **Effort:** One line change
- **Risk:** May be too dark in shadow — test outdoors first

### 1.3 Camera Warmup Frames
- **Issue:** First 5-10 frames have unconverged AWB/exposure → garbage detections
- **Fix:** Discard first 10 frames in vision.py `__init__`
- **Effort:** 3 lines of code

### 1.4 Lower Detection Altitude
- **Current:** TARGET_ALT = 30m in config.py
- **Research says:** MobileNet SSD studies found max reliable detection altitude is ~20m for person detection. YOLOv8n should be similar.
- **Action:** Test at 30m first, have 15-20m as fallback
- **Change in:** config.py TARGET_ALT

---

## 2. Hardware Preparation (Before Flight Day)

### 2.1 Thermal Management (Critical)
- [ ] **Active cooler on Pi 5** — Pi throttles at 80C, hard-throttles at 85C. CV inference pushes it there without cooling. Official active cooler weighs ~15g.
- [ ] **Monitor temperature in scripts** — Add `vcgencmd measure_temp` logging. If >75C, you're near throttling.
- [ ] In-flight prop wash helps cool, but bench tests are worst case for heat.

### 2.2 Vibration Isolation
- [ ] **Rubber grommets or gel pads** under Pi mounting — motor vibration causes SD card read errors and camera shake
- [ ] **Secure camera ribbon cable** with zip ties / kapton tape — #1 field failure mode
- [ ] **Balance propellers** — imbalanced props create low-frequency vibration affecting IMU and camera
- [ ] **Hot glue SD card** in place — vibration can partially eject it

### 2.3 Power
- [ ] **Dedicated BEC/buck converter** from LiPo to Pi (5V/5A) — do NOT power from Cube's 5V rail (brownout risk under CV load)
- [ ] **Separate ground planes** for Pi and GPS/magnetometer — CV processing creates EMI that can affect compass
- [ ] **1000uF capacitor** on Pi power input to absorb motor startup transients
- [ ] **A2/V30 rated SD card** — slow cards cause I/O bottlenecks when writing detection logs + images during inference

### 2.4 Assembly
- [ ] **Solder, not breadboard** — vibration loosens push-fit connections within minutes
- [ ] **Conformal coat** exposed solder joints (Bristol weather = damp)
- [ ] **Zip tie all cables** — every loose connector is a flight failure waiting to happen

---

## 3. Inference Speed (Current: 250ms / 4 FPS)

### 3.1 NCNN Export (Best Free Option)
| Metric | TFLite (current) | NCNN |
|--------|:-:|:-:|
| Speed | 250ms | **~83ms** |
| FPS | 4 | **12** |
| Accuracy | Same | Same |
| Cost | - | Free |

- **How:** `yolo export model=best.pt format=ncnn` → produces `best_ncnn_model/` folder
- **Catch:** Requires `ultralytics` on Pi (pulls PyTorch, ~2GB). Python 3.13 untested.
- **Alternative:** Standalone `pip install ncnn` bindings (lighter, but write own postprocessing)
- **Branch:** `ncnn-experiment` created, ready for when we have `best.pt`
- **Status:** BLOCKED — need original .pt weights (lost/not in git). Retrain on Colab → export both TFLite + NCNN.

### 3.2 Model Upgrade (YOLO11n / YOLO26n)
| Model | NCNN Speed | mAP (COCO) |
|-------|:-:|:-:|
| YOLOv8n (current) | ~83ms | 37.3 |
| YOLO11n | ~80ms | 39.5 |
| **YOLO26n** | **~68ms** | **40.1** |

- Same Ultralytics export pipeline, same training workflow
- Do this when retraining anyway — zero extra effort

### 3.3 Input Resolution
- Current: 640x640. Reducing to 480x480 could give ~1.5-2x speedup
- **Risk:** At 30m altitude, dummy is ~20-30px at 640. At 480, it's ~15px — may be below detection threshold
- **Test:** Export model at 480, benchmark detection rate vs speed

### 3.4 Hailo-8L AI HAT+ ($70 Upgrade)
| Metric | TFLite (current) | Hailo-8L |
|--------|:-:|:-:|
| Speed | 250ms | **~16ms** |
| FPS | 4 | **60** |
| Cost | - | $70 |

- Official Raspberry Pi product — plugs into Pi 5 PCIe slot
- Could run YOLOv8s (more accurate) and still get 80 FPS
- Needs model conversion to HEF format (Hailo Dataflow Compiler on x86 Linux)
- **Recommendation:** Fly first with current setup. Hailo is "next iteration" upgrade.
- Source: [Raspberry Pi AI HAT+](https://www.raspberrypi.com/products/ai-hat/)

### 3.5 What Does NOT Work
- **INT8 TFLite:** Zero speedup on Pi 5 ARM CPU (known issue, GitHub #7445)
- **Coral USB TPU:** Dead product, 1-2 FPS on YOLO (worse than current!), Python 3.13 incompatible, discontinued by Google
- **Vulkan GPU on Pi 5:** VideoCore VII doesn't benefit DL workloads. CPU + NEON is faster.
- **RT-DETR (transformers):** Need GPU, too slow on Pi 5 CPU

---

## 4. Training Data & Model Quality

### 4.1 Capture Real Training Photos (Highest Impact)
- **Current model** trained on synthetic composites (map.jpg + dummy.png pasted on top)
- **The gap** between synthetic and real aerial photos is large — lighting, shadows, grass texture, camera noise
- **Action:** On first flight, run `capture_training.py` and photograph dummy from 5m, 10m, 15m, 20m, 25m, 30m
- Different poses (lying flat, curled, arms out, face down)
- Different lighting (sunny, overcast)
- **Then:** Label with Roboflow, retrain on Colab (free GPU), export to TFLite + NCNN

### 4.2 Retrain on Colab
```python
# Colab notebook (one-time setup):
!pip install ultralytics
!yolo detect train model=yolov8n.pt data=dataset.yaml epochs=100 imgsz=640
!yolo export model=runs/detect/train/weights/best.pt format=tflite
!yolo export model=runs/detect/train/weights/best.pt format=ncnn
# Download both: best.tflite (fallback) + best_ncnn_model/ (fast)
```

### 4.3 COCO Person Detector as Backup
- `models/human.tflite` already exists (YOLOv8n trained on 80 COCO classes including "person")
- Swap on flight day if custom model fails: `cp models/human.tflite best.tflite`
- May detect bystanders too (false positives) — but better than missing the dummy

---

## 5. Ground Station UX (pi_flight.py)

### 5.1 High Priority
- [ ] **Battery voltage bar** — colour-coded (green >14V, yellow 13-14V, red <13V for 4S). Single most important safety indicator.
- [ ] **Estimated flight time remaining** — more useful than raw voltage. Approximate from battery % + elapsed time.
- [ ] **Heartbeat watchdog** — if no Cube heartbeat for 5s, show "LINK LOST" red banner.
- [ ] **Confidence as colour** — green/yellow/red bounding box border instead of numeric "0.62". Faster to parse.
- [ ] **Minimal HUD overlay on video** — altitude + battery icon + mode overlaid semi-transparently on video itself, so operator never looks away from feed.

### 5.2 Medium Priority
- [ ] **Detection thumbnail strip** — save cropped detection images, show recent ones in scrollable strip below video. Lets operator review without pausing feed.
- [ ] **Search coverage visualization** — shade already-searched area on 2D grid. Operator needs "how much is left" at a glance.
- [ ] **Adaptive information density** — show less during SEARCH (coverage + alert-on-detection), show more during INVESTIGATE (confidence, cluster info, classify buttons). Reduces cognitive load (SafeSpect, CHI 2025).
- [ ] **Time since last detection** timer — if 60+ seconds pass with no detection, operator knows to check camera/model.
- [ ] **One-click RTL button** — always visible, never hidden behind a menu.

### 5.3 Nice To Have
- [ ] **Geofence visualization** — draw flight boundary and SSSI no-fly zone on map
- [ ] **Predictive path** — show remaining search waypoints on map
- [ ] **Detection rate** (detections/minute) — spike in rate is more informative than raw count
- [ ] **Alert hierarchy** — red banner (critical: battery/link), orange (warning: detection), green status bar (normal)
- [ ] **Command acknowledgement** — after sending MAV_CMD, show success/failure from COMMAND_ACK

### 5.4 UX Principles (from SAR research)
1. **Three things always visible:** video feed, drone position on map, battery/status
2. **Collapsible panels** — hideable instrument panels for unobstructed video view
3. **Don't show raw numbers operator can't act on.** "Heading: toward target" > "Yaw: 153°"
4. **Context-dependent display.** SEARCH → coverage progress. INVESTIGATE → detection info. LAND → distance + descent rate.
5. **Keyboard shortcuts are correct** — in high-stress flight ops, keyboard > mouse

---

## 6. Development Workflow

### 6.1 LLM Context Management (Prevent Forgetting + Avoid Overload)

**Problem:** CLAUDE.md is ~700 lines with session log eating most of it. Each new session loads it all.

**Solution: Three-tier system**

| Tier | What | When Loaded | Max Size |
|------|------|-------------|----------|
| **Tier 0** | CLAUDE.md — rules, architecture, current state, next steps | Every session | ~200 lines |
| **Tier 1** | docs/*.md — blueprints, guides, this file | On demand (when task needs it) | No limit |
| **Tier 2** | Source code, session logs, brain dumps | Searched when needed | No limit |

**Key changes needed:**
- [ ] Extract session log from CLAUDE.md → `docs/SESSION_ARCHIVE.md` (append-only history)
- [ ] Replace with 5-10 line "Current State" block that gets overwritten each session
- [ ] Add "Next Steps" as FIRST section in CLAUDE.md (every session starts knowing what to do)
- [ ] Create `.claudeignore` — exclude `_archive/`, `*.csv`, large data files
- [ ] Keep MEMORY.md under 200 lines (currently fine)

**Three memory systems work together:**
| System | Purpose | Who writes | When loaded |
|--------|---------|-----------|-------------|
| CLAUDE.md | Rules & architecture | You (human) | Every session |
| MEMORY.md | Learned facts & patterns | Claude (auto) | Every session |
| docs/*.md | Detailed guides | Both | On demand |

### 6.2 Progressive Testing (Already Good, Add Exit Criteria)

Your numbered flight tests (0a through 4) are textbook. Add **exit criteria** for each:

| Step | Test | Exit Criteria (proceed when...) |
|------|------|------|
| 0a | Cube commands (bench) | All mode changes ACK'd, commands reach Cube |
| 0b | Bench mission (no props) | Full sequence completes without errors |
| 0c | Feedback test | Vision→GPS pipeline produces reasonable coordinates |
| 1 | MP AUTO waypoints | Drone completes pattern, RTLs, no deviations >5m |
| 2 | Waypoint test (your code) | 4 waypoints flown, landing within 3m of target |
| 3 | Passive CV (manual RC) | 50+ detections in 5min flight, FP rate <20% |
| 4 | Detect & center | Drone centres on target within 3m, holds position |
| 5 | Full autonomous | Complete mission: search → detect → verify → land |

### 6.3 Record & Replay
- During manual flights, record raw frames + telemetry to disk
- Replay on laptop to test model changes without flying again
- `capture_training.py` captures frames but not synchronized telemetry
- **TODO:** Add GPS/attitude metadata per frame (JSON sidecar files)

### 6.4 Automated Smoke Test on Pi
- After `git pull`, run single script: camera check, model load, single inference, Cube heartbeat
- Pass/fail in 10 seconds. `preflight.py` partially does this but could be streamlined.

---

## 7. Pi + CV Best Practices Checklist

### Camera
- [x] Global shutter camera (IMX296) — eliminates jello effect from vibration
- [x] BGR output confirmed — no cvtColor needed
- [x] 180° flip for inverted mounting
- [ ] Lock exposure to 1/400s for flight (reduce motion blur)
- [ ] Warmup: discard first 10 frames (AWB/exposure convergence)
- [ ] Lock AWB after convergence (prevent colour shifts between frames)

### Reliability
- [ ] Active cooler on Pi 5 (throttles at 80C)
- [ ] Temperature monitoring in scripts (`vcgencmd measure_temp`)
- [ ] Vibration-damped Pi mounting
- [ ] Secured camera ribbon cable (zip ties)
- [ ] Dedicated 5V/5A BEC power (not from Cube)
- [ ] Hot-glued SD card
- [ ] A2/V30 SD card for I/O performance
- [ ] Balanced propellers

### Software
- [x] Dual backend vision.py (Ultralytics / TFLite)
- [x] Config auto-detection (Pi / laptop)
- [x] Same code on all platforms
- [ ] NCNN backend (3x faster, pending .pt weights)
- [ ] Camera threaded capture (separate from inference loop)
- [ ] Undervoltage monitoring (`vcgencmd get_throttled`)

### Operations
- [x] Progressive test scripts (numbered 0a-5)
- [x] Operator-in-the-loop verification (Y/N at VERIFY stage)
- [x] RC always has priority (kill switch to STABILIZE)
- [x] Spatial clustering (temporal consistency filtering)
- [ ] Search coverage visualization in ground station
- [ ] Battery-based estimated flight time

---

## 8. Professional SAR Reference

What professional SAR drone teams do (for context / dissertation discussion):

| Feature | Professional SAR | Our Project | Gap |
|---------|:---:|:---:|-----|
| Thermal + RGB cameras | Yes | RGB only | Expected limitation (budget) |
| Hardware accelerator | Jetson Orin / Hailo | CPU TFLite | Hailo-8L would close this |
| Multi-drone coordination | Yes | Single drone | Out of scope |
| Temporal consistency filtering | Yes | Yes (clustering) | Implemented |
| Multi-pass confirmation | Yes | Yes (SEARCH→VERIFY) | Implemented |
| Operator confirmation | Yes | Yes (Y/N verify) | Implemented |
| Search coverage logging | Yes | Partial | Need visualization |
| Crew handover / logs | Yes | JSON + photos | Implemented |
| Auto search pattern | Yes | Yes (lawnmower) | Implemented |
| Real-time detection | Yes (~30 FPS) | Yes (~4 FPS) | NCNN/Hailo would close this |

---

## Sources

### Inference Optimization
- [Ultralytics Raspberry Pi Guide](https://docs.ultralytics.com/guides/raspberry-pi/)
- [NCNN on Pi 5 Benchmarks](https://community.ultralytics.com/t/ultralytics-yolo-raspberry-pi-5-benchmarks/70)
- [TFLite INT8 no speedup (GitHub #7445)](https://github.com/ultralytics/ultralytics/issues/7445)
- [Hailo RPi5 Examples](https://github.com/hailo-ai/hailo-rpi5-examples)
- [Raspberry Pi AI HAT+](https://www.raspberrypi.com/products/ai-hat/)
- [Coral vs Hailo Comparison](https://www.seeedstudio.com/blog/2024/07/16/raspberry-pi-ai-kit-vs-coral-usb-accelerator/)
- [YOLO11 on Pi (LearnOpenCV)](https://learnopencv.com/yolo11-on-raspberry-pi/)

### Ground Station UX
- [SafeSpect: AR HUD for Drone Inspections (CHI 2025)](https://arxiv.org/html/2504.16533)
- [Multi-Drone SAR Trust Study (ACM 2024)](https://dl.acm.org/doi/fullHtml/10.1145/3686038.3686052)
- [FlightAR: AR Flight with YOLOv8n](https://arxiv.org/html/2410.16943v1)
- [DroneSAR App](https://www.dji.com/newsroom/news/dji-and-dronesar-bring-search-and-rescue-app-to-first-responders)
- [Mavelous GCS](https://github.com/wiseman/mavelous)

### Pi + CV Best Practices
- [OpenCV Pi Camera & Cooling](https://opencv.org/configuring-raspberry-pi-for-opencv-camera-cooling/)
- [Roboflow Pi Deployment Guide](https://blog.roboflow.com/raspberry-pi-computer-vision/)
- [Pi Thermal Management](https://www.raspberrypi.com/news/heating-and-cooling-raspberry-pi-5/)
- [picamera2 Manual](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)

### Context Management
- [CLAUDE.md Best Practices (UX Planet)](https://uxplanet.org/claude-md-best-practices-1ef4f861ce7c)
- [Claude Code Best Practices (Official)](https://code.claude.com/docs/en/best-practices)
- [7 Ways to Cut Token Usage](https://dev.to/boucle2026/7-ways-to-cut-your-claude-code-token-usage-elb)
