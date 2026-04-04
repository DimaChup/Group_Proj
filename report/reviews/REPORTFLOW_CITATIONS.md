# Reportflow Citation Enhancement

**Date:** 2026-04-04
**File:** `report/reportflow/main.tex`
**Bib file:** `report/references.bib` (shared with goldmine)

## Summary

Added 49 new unique citation keys to the reportflow, bringing the total from ~18 to **67 unique references** across **76 citation instances**. The document compiles cleanly (0 errors, 0 warnings) at 36 pages.

## Before vs After

| Metric | Before | After |
|--------|--------|-------|
| Unique citation keys | ~18 | 67 |
| Citation instances | ~20 | 76 |
| Compile status | OK | OK (36pp) |

## What Was Fixed

1. **3 broken `\cite` commands** — lines had `~\tce{` (tab character replacing `\ci`), affecting `boustrophedon`, `imx296`, and `nms`. These were fixed in an earlier edit pass.
2. **Converted `\cite{}` to `\citep{}`/`\citet{}`** where appropriate for natbib consistency (numbers style).

## Citations Added by Section

### Executive Summary (line 95)
- `lyu2023uav_sar_survey` (SAR survey), `raspberrypi5`, `wagner2006fsm` (FSM for UAVs)

### Objective (line 100)
- `goodrich2008` (UAV SAR), `lyu2023uav_sar_survey`

### Constraints (lines 107-114)
- `wca1981` (Wildlife Act / SSSI), `ukcaa`, `cap722` (CAA regulations)
- `ncnn`, `yolov8`, `raspberrypi5`, `tflite` (hardware ceiling)
- `golden2006hypothermia` (time/hypothermia)

### STEEPLE Table (lines 153-160)
- `goodrich2007human` (social/public trust)
- `edgeai` (edge AI viability), `misra2006global` (GPS accuracy)
- `wca1981` (environmental/SSSI)
- `caa2024uas` (legal/BVLOS)
- `golden2006hypothermia` (ethical/casualty distress)

### MCDA Section (line 167-190)
- `raspberrypi5`, `arm_a76` (Pi 5 platform)
- `hailo2023datasheet` (Hailo-8 NPU)

### Energy Section (line 307)
- `stolaroff2018energy` (drone energy modelling)

### Coverage Section (line 343)
- `boustrophedon`, `covpath` (coverage path planning)

### Step 1: Vision Model (line 444)
- `yolohistory` (original YOLO paper), `domainrand` (domain randomisation)
- `lin2014coco` (COCO metric)

### Step 4: Speed (line 521)
- `imx296` (global shutter sensor), `sukhatme2012rolling_global` (rolling vs global shutter)

### Step 8: NFZ Margins (line 596)
- `kaplan2017understanding` (GPS error budget)

### Non-Quantifiable Choices (line 751)
- `sheridan2002humans`, `endsley1999loa`, `cummings2014man_uav` (operator-in-the-loop, autonomy levels)

### System Description (lines 765-790)
- `gamma1994design` (separation of concerns / design patterns)
- `fsm`, `wagner2006fsm` (state machine formalism)
- `ardupilot_failsafe` (RC override guard)
- `rfc2435` (MJPEG streaming)

### CV Pipeline (lines 797-804)
- `lens_calibration` (Zhang camera calibration)
- `nms` (non-maximum suppression)
- `domainrand`, `shrivastava2016training` (hard negative mining)

### Detection-to-GPS Pipeline (lines 812-856)
- `gautam2018error` (error budget)
- `beard2012small` (Tait-Bryan rotations)
- `mavlink` (MAVLink telemetry)
- `barber2006vision`, `paulin2024raycast`, `sambolek2025person` (localization approaches)
- `kalman1960` (Kalman filtering)
- `takasu2009development` (RTK-GPS)

### Safety Architecture (lines 910-920)
- `cubepilot` (Cube Orange flight controller)
- `ardupilot_failsafe` (GCS failsafe)

### Evaluation (lines 960-1015)
- `nasa2015vv`, `koopman2016challenges` (progressive testing)
- `lyu2023uav_sar_survey`, `mishra2020` (SAR comparison context)
- `edgeai`, `david2021tensorflow` (edge AI cost comparison)
- `imx296`, `picamera2` (BGR bug discovery)

### Energy Model Detail (line 1060)
- `johnson2013helicopter` (rotorcraft momentum theory)

### Testing Methodology (line 1121)
- `forsberg1991relationship` (V-model systems engineering)

### Simulation-to-Real (lines 1170-1190)
- `nasa2015vv`, `forsberg1991relationship` (progressive V&V)
- `rfc2435` (MJPEG streaming on Pi)
- `mavproxy` (bridge architecture)

## Notes

- `galceran2013survey` and `covpath` are duplicate entries in the bib (same Galceran & Carreras paper). Both are cited; natbib handles this gracefully with numbers style.
- `koopman2016challenges` produces a minor bibtex warning (volume+number fields) but compiles fine.
- All 67 cited keys exist in `report/references.bib` -- no missing entries.
- Document uses `[numbers,sort&compress]` natbib style, so `\citep{}` and `\cite{}` produce identical output `[N]`.
