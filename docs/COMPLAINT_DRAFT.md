# Draft Complaint Letter — Drone Hardware Issues

**To:** Steve [surname], Module Lead AENGM0074
**From:** [Your name], Blue Team
**Date:** 2026-03-19
**Re:** Inability to test custom software due to non-functional drone hardware

---

## Context

As part of AENGM0074, our team has developed a complete autonomous SAR (Search and Rescue) drone system including:
- Autonomous search pattern flight (lawnmower/spiral)
- AI-based casualty detection (YOLOv8n, TFLite + NCNN backends)
- GPS estimation of target position
- Web-based ground station for real-time monitoring
- Comprehensive test suite (146 automated tests)
- Progressive flight test methodology (bench → passive → autonomous)

The software is simulation-proven and has been running successfully in SITL for months. We are ready and have been ready to test on real hardware.

## Issue

**We have been unable to deploy and test our code on the actual drone across two flight days because the provided hardware has not been functional.**

### Flight Day 1 (2026-03-11)
- Weather cancelled outdoor flight
- Bench testing conducted: camera, Cube connection, benchmarks all working on Pi
- Lens calibration completed
- Discovery: GPS 2 "still configuring" — prevents arming

### Flight Day 2 (2026-03-18)
- Arrived prepared with all software ready
- Mavproxy connected, diagnostics passed, benchmarks completed
- **Could not arm:** "GPS 2 still configuring this GPS"
- GPS 1 had full 3D fix (13 satellites, 0.8 HDOP) — excellent
- GPS 2 appears to either not be connected or be faulty
- Attempted flight but drone did not take off
- **Drone had additional issues:** [add details about power/motor problems]
- Spent entire session diagnosing hardware, not testing software

## Impact

- Two flight days used with zero flight testing achieved
- Software development is complete but cannot be validated in real conditions
- Team has invested significant effort in simulation, testing infrastructure, and preparation
- Every flight day without a working drone is a day we cannot demonstrate our system
- Assessment deadline is approaching with no real-world flight data

## What We've Done

Despite hardware issues, we have:
- Full simulation testing (end-to-end mission runs perfectly)
- Pi integration tested (camera, AI model, Cube telemetry all verified)
- Benchmarked 3 inference backends (Ultralytics, TFLite, NCNN)
- Proven NCNN gives 4.5x speedup (13.8 FPS vs 3.1 FPS)
- Built comprehensive test and diagnostic tools
- Documented everything thoroughly

## What We Need

1. **A working drone** that can arm and fly with our Pi + Cube setup
2. **Acknowledgement** that the delays are due to hardware provision, not our team's readiness
3. **Additional flight day(s)** to compensate for the two lost sessions
4. **Confirmation** of the GPS 2 configuration — should `GPS_TYPE2` be set to 0 if only one GPS is connected?

## Evidence

All diagnostic data, benchmarks, and logs from both flight days are saved in our repository:
- `pi_data/benchmark_results.txt` — model performance on Pi
- `pi_data/final_readiness.txt` — system readiness check (all pass except hardware)
- `pi_data/blur_altitude_results.txt` — detection capability proven
- Flight logs from Cube (log50.bin, log51.bin, log52.bin)

---

*[Add more specific details about what Steve said, what broke, timeline, etc.]*
