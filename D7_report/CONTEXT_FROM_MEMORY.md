# Context from Memory, Brain-Dump & Design Decisions

## How Apollo Thinks
- Engineering-first, evidence-driven mindset — every decision validated through simulation/benchmarking
- Preference for modular architecture (main.py 1411→754 in single session, 6 modules)
- Aggressive agent delegation (10-20 parallel agents per task)
- Pragmatic risk management — accepts calculated compromises (descent stall "good enough for demo")

## 17 Design Decisions with Team Input
- DD-01: MJPEG over H.264 (reliability + browser compatibility)
- DD-02: Headless SSH operation (PuTTY + browser ground control)
- DD-03: Dual-backend vision (Ultralytics/TFLite/NCNN auto-detect)
- DD-04: mavproxy UDP bridge (Python 3.13 pyserial broken)
- DD-08: Inverse-variance weighting (physics-grounded GPS estimation)
- DD-10: Three NFZ avoidance modes — chose speed-cap (smooth, no jitter)
- DD-11: Threaded inference (decouple capture from AI)
- DD-13: NCNN backend (4.5x faster, 72ms vs 327ms)
- DD-14: Zero-command passive mode (safety-first observer)
- DD-15: SMART result image composite

## Breakthrough Moments
1. Tilt compensation: R = Rz(ψ)Ry(-θ)Rx(-φ) reduced GPS error 6.2m → 0.3m, 1440 unit tests
2. NCNN discovery: 4.5x speed improvement in single session
3. Pi field day debugging: 4 critical bugs fixed in one day under pressure
4. Report scoring: 50 agents, D6 from 74→85.2, D7 from 42→82

## Things That Went Wrong
- Descent stall at 4-5m (SITL-specific, accepted)
- TFLite bbox off-screen (no documentation, empirical fix)
- GPS estimate 100m off (double-scaling bug in passive_watch)
- RC override fighting (continuous commands override pilot)
- Python 3.13 breakage (tflite + pyserial both broken)
- Geofence force inverted (sign conventions)

## Workflow Preferences
- Write everything, append never delete (brain-dump grows chronologically)
- Blueprints for large files (read BEFORE source)
- NICE_TO_HAVE with impact/effort scoring
- Memory cascade (MEMORY.md + session files)
- Agent-first investigation (parallel agents validate before commit)

## Current State
- 4,400+ lines across 11 modules, 58 test scripts, 146 pytest tests
- 3 AI model generations, mAP50 = 0.995
- Complete simulation verifying all R01-R12
- D7 ceiling at 82-84 (agent), needs HITL for 85+
