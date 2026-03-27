# Path Optimization Analysis

SAR drone lawnmower search pattern optimization for the AENGM0074 survey area near Bristol.

## What it does

Finds the optimal **altitude** and **scan angle** for the lawnmower search pattern by evaluating every combination of:
- 6 altitudes: 20m, 25m, 30m, 35m, 40m, 50m
- 36 scan angles: 0 to 175 degrees in 5-degree steps

For each combination it computes:
- Camera ground footprint and swath spacing (20% overlap)
- Number of scan lines needed to cover the 5-corner survey polygon
- Total path length (scan lines + U-turn transits)
- Search time at altitude-dependent speed (6 m/s at 20m up to 10 m/s at 50m)
- Time penalty from SSSI no-fly zone slowdown (speed ramps from 3.0 to 0.3 m/s within 20m of boundary)
- Energy cost using a simplified quadcopter model (150W hover + speed-squared drag)
- U-turn penalty (2 seconds deceleration/reacceleration per turn)

## How to run

From the project root (`v3/`):

```bash
python analysis/path_optimization/optimize_path.py
```

Requirements: `numpy`, `matplotlib` (both included in `requirements_dev.txt`).

No connection to the drone or SITL is needed. The script reads polygon geometry from `flight_plans/AENGM0074.kml` and camera parameters from `config.py`.

## Outputs

**Console:** Results table, detailed breakdown per altitude, and optimal configuration recommendation.

**Plots (saved to this directory):**

| File | Description |
|------|-------------|
| `plot1_energy_vs_altitude.png` | Total energy with and without NFZ slowdown |
| `plot2_time_vs_altitude.png` | Total search time with and without NFZ slowdown |
| `plot3_scan_angle_vs_altitude.png` | Optimal scan angle for each altitude |
| `plot4_scan_lines_vs_altitude.png` | Number of scan lines and swath width vs altitude |
| `plot5_energy_heatmap.png` | 2D heatmap of energy across all altitude x angle combinations |
| `plot6_survey_and_pattern.png` | Map of survey area + SSSI + optimal lawnmower pattern |

## Energy model

Simplified quadcopter power model:

- **Hover power**: 150W (constant, always consumed while airborne)
- **Movement power**: 50W * (speed / 5 m/s)^2 (aerodynamic drag scales with speed squared)
- **U-turn**: 2 seconds of hover-only power per turn (deceleration + reacceleration)
- **Total energy** = hover_power * total_time + movement_power * flight_time

## Key parameters

All sourced from `config.py`:

| Parameter | Value | Source |
|-----------|-------|--------|
| Sensor width | 5.02 mm | IMX296 spec |
| Focal length | 5.46 mm | Calibrated 2026-03-11 |
| Image size | 1456 x 1088 px | Pi camera native |
| Overlap | 20% | Standard practice |
| Speed at 20m | 6.0 m/s | Motion blur limit |
| Speed at 50m | 10.0 m/s | Coverage speed |
| NFZ slow zone | 20 m | Safety buffer |
| NFZ min speed | 0.3 m/s | Near-boundary crawl |
