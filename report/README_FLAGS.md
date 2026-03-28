# main.py Command-Line Flags (v5.8)

All flags are optional. With no flags, `main.py` runs a live mission using the default
model, search altitude, and streaming server.

---

## Mission Mode

| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--dry-run` | Print waypoints, distances, timing, and state walkthrough without arming, flying, or connecting to a Cube. Saves `dry_run_pattern.jpg` if `map.jpg` is present. | off | `python main.py --dry-run` |
| `--headless` | Disable all `cv2.imshow` windows. Input via terminal keys or browser buttons at `http://localhost:8090/`. Auto-enabled on Linux when `$DISPLAY` is empty (e.g. PuTTY/SSH to Pi). | auto-detect | `python main.py --headless` |

## Flight Parameters

| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--alt <meters>` | Override search/cruise altitude (`config.TARGET_ALT`). | `35.0` | `python main.py --alt 25` |
| `--speed <factor>` | SITL simulation speedup factor (sets `SIM_SPEEDUP` param). Only meaningful in SIMULATION mode. `1` = real-time, `5` = 5x faster. | `1` | `python main.py --speed 5` |
| `--transit <file>` | Path to a JSON file of GPS waypoints the drone flies before starting the search pattern. If the file is missing and this flag was given explicitly, the script exits with an error. | `flight_plans/transit.json` | `python main.py --transit flight_plans/custom.json` |
| `--beacon-delay <seconds>` | Seconds after search begins before a simulated PLB (Personal Locator Beacon) signal fires, redirecting the drone from the main search area to the Focus Area polygon. `0` = never auto-trigger (beacon can still be triggered manually with the B key). | `0` | `python main.py --beacon-delay 600` |

## Detection Options

| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--model <path>` | Path to a `.tflite` model file. Swap models without copying files. | `best.tflite` | `python main.py --model cv_models/sar_v2_1088/best.tflite` |
| `--smart-detect` | Require `DETECT_CONFIRM_FRAMES` consecutive detections of the same target before queueing it for investigation. Reduces false positives at the cost of slower reaction. | off | `python main.py --smart-detect` |
| `--center-verify` | After centering on a target, start GPS averaging to refine the target position before entering VERIFY. Without this flag, the drone enters VERIFY immediately. | off | `python main.py --center-verify` |

## Geofence

| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--no-nfz` | Disable the SSSI no-fly-zone geofence entirely. Useful for bench testing or sites without restricted areas. | geofence on (if KML defines SSSI) | `python main.py --no-nfz` |

## Streaming and Display

| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--no-stream` | Disable the MJPEG/HTTP streaming server on port 8090. Saves CPU if no browser ground station is needed. | stream on | `python main.py --no-stream` |

Stream settings (port 8090, 320x240, 5 FPS, quality 50) are hardcoded constants and
cannot be changed via CLI flags.

---

## Examples

```bash
# Basic simulation run (default model, 35m altitude, stream on)
python main.py

# Dry run -- check pattern, distances, timing (no Cube needed)
python main.py --dry-run

# Dry run at a lower altitude to see how waypoint count changes
python main.py --dry-run --alt 20

# Real flight with custom altitude and smart detection
python main.py --alt 25 --smart-detect

# Simulation at 5x speed with beacon auto-trigger after 10 minutes
python main.py --speed 5 --beacon-delay 600

# Use retrained model, disable geofence for bench test
python main.py --model cv_models/sar_v2_1088/best.tflite --no-nfz

# Headless on Pi over SSH, no cv2 windows
python main.py --headless

# Full mission with all options
python main.py --alt 30 --speed 3 --transit flight_plans/transit.json \
    --beacon-delay 600 --smart-detect --center-verify --model cv_models/sar_v2_1088/best.tflite

# Dry run with alternate model (verify it loads correctly)
python main.py --dry-run --model models/human.tflite
```

## Notes

- **`DRONE_MODE` environment variable** controls SIMULATION vs REAL mode. It is not a
  CLI flag -- set it before running: `set DRONE_MODE=SIMULATION` (Windows) or
  `export DRONE_MODE=SIMULATION` (Linux). If unset, `config.py` auto-detects based on
  available serial ports.
- The `--transit` file defaults to `flight_plans/transit.json`. If that file does not
  exist and the flag was **not** given explicitly, the drone simply flies direct to the
  search area (no error). If you explicitly pass `--transit` and the file is missing,
  the script exits immediately.
- All flags can be combined freely.
