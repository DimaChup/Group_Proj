# Pi Data — Hardware-Specific Files

This directory is pushed FROM the Pi and pulled TO the laptop.
It keeps both sides in sync with Pi-specific data.

## What goes here

| File | How to generate | When to update |
|---|---|---|
| `calibration_data.npz` | `python tests/calibration/lens_calibrate.py` on Pi | After camera/lens change |
| `readiness_report.txt` | `python field_tools/system_readiness.py > pi_data/readiness_report.txt` | Each flight day |
| `benchmark_results.txt` | `python tests/day_1_experiments/model_compare.py --frames 50 > pi_data/benchmark_results.txt` | After model swap or Pi change |
| `ncnn_benchmark.txt` | `python tests/hardware/ncnn_benchmark.py > pi_data/ncnn_benchmark.txt` | When testing NCNN |
| `detections_sample/` | Copy best detections: `cp detections/*.jpg pi_data/detections_sample/` | After flights with good data |

## How to update (on Pi)

```bash
cd ~/dima/Group_Proj
# Run benchmarks
python field_tools/system_readiness.py > pi_data/readiness_report.txt
python tests/day_1_experiments/model_compare.py --frames 50 > pi_data/benchmark_results.txt

# Copy calibration if it exists
cp calibration_data.npz pi_data/ 2>/dev/null

# Push to GitHub
git add pi_data/
git commit -m "Update Pi data: benchmarks + calibration"
git push
```

## How to get on laptop

```bash
git pull
```

## Staleness check

If `benchmark_results.txt` is older than the latest model or code change,
re-run benchmarks on Pi. Check dates with `ls -la pi_data/`.
