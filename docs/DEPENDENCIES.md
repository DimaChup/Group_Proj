# Script Dependency Graph

## Module Hierarchy (no circular dependencies)

```
config.py ─────────── Auto-detects platform, connection, mode
  │                   Used by ALL scripts (hub)
  │
states.py ─────────── Pure enum (State.SEARCH etc.)
  │                   Used by: main.py, simple_simulator.py
  │
utils.py ──────────── Geo math (GeoTransformer, overlay_image_alpha)
  │                   Depends on: config
  │                   Used by: main, simple_simulator, simulation, planning
  │
planning.py ───────── Lawnmower search pattern generator
  │                   Depends on: config
  │                   Used by: main.py only
  │
vision.py ─────────── Camera + AI detection (dual backend)
  │                   Depends on: config (optional)
  │                   Backend: Ultralytics (laptop) OR TFLite/ai-edge-litert (Pi)
  │                   Used by: main, simple_simulator, pi_flight, passive_watch
  │
simulation.py ─────── Map rendering + multi-target (laptop only)
                      Depends on: config, utils
                      Used by: main, simple_simulator, pi_flight (SIMULATION mode only)
```

## Script → Module Dependencies

| Script | config | states | utils | planning | vision | simulation |
|--------|--------|--------|-------|----------|--------|------------|
| main.py | Y | Y | Y | Y | Y | SIM only |
| simple_simulator.py | Y | Y | Y | - | Y | SIM only |
| pi_flight.py | Y | - | Y | - | Y | SIM only |
| passive_watch.py | Y | - | - | - | Y | - |
| capture_training.py | - | - | - | - | - | - |
| preflight.py | - | - | - | - | - | - |
| generate_dataset.py | - | - | - | - | - | - |

## Runtime Dependencies

| Resource | main | simulator | pi_flight | passive_watch | capture_training |
|----------|------|-----------|-----------|---------------|------------------|
| Cube/SITL | REQ | REQ | REQ | Optional | Optional |
| Camera | REQ | SIM=map | REQ | REQ | REQ |
| best.tflite | REQ | REQ | REQ | REQ | - |
| map.jpg | SIM only | SIM only | SIM only | - | - |
| GPS lock | REQ | - | REQ | Optional | Optional |
| Browser | Optional | - | REQ (UI) | REQ (stream) | REQ (stream) |

## Platform Compatibility

| Script | Windows | WSL | Pi | Notes |
|--------|---------|-----|------|-------|
| main.py | SIM+REAL | SIM | REAL | Headless auto-detect |
| simple_simulator.py | SIM | SIM | No | Needs cv2.imshow + map.jpg |
| pi_flight.py | SIM+REAL | SIM | REAL | Web dashboard, headless OK |
| passive_watch.py | Both | Both | REAL | Zero commands |
| capture_training.py | Both | Both | REAL | Zero commands |
| preflight.py | Both | Both | Both | Standalone |
| generate_dataset.py | Both | Both | No | Needs map.jpg + dummy.png |

## Standalone Scripts (zero project deps)

- `preflight.py` — connectivity checker
- `generate_dataset.py` — synthetic training data
- `capture_training.py` — optional mavlink only

## Critical Path for Flight

```
config.py → vision.py → main.py (or pi_flight.py)
    │                      │
    └── planning.py ───────┘  (search pattern)
    │                      │
    └── utils.py ──────────┘  (GPS math)
    │                      │
    └── states.py ─────────┘  (state machine)
```

If any module in this chain fails to import, the mission won't start.
`config.py` is the single point of failure — all other modules depend on it.
