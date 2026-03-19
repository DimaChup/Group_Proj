# Blur + Altitude Detection Comparison

## Laptop Predictions (to be validated on Pi)

### Model 1: Original (3.2MB, best.tflite)
```
         0m/s   2m/s   5m/s   8m/s  10m/s  15m/s  20m/s
  15m   0.94   0.94   0.94   0.95   0.94   0.93   0.91    ← all good
  20m   0.96   0.96   0.96   0.97   0.96   0.96   0.96    ← all good
  25m   0.94   0.94   0.93   0.94   0.94   0.92   0.92    ← all good
  30m   0.89   0.87   0.90   0.87   0.85   0.89   0.86    ← starts dropping
  40m   0.76   0.74   0.75   0.66   0.72   0.75   0.75    ← mediocre
  50m   0.63   0.61   0.62   0.58   0.66   0.56   0.57    ← borderline
  60m   0.48   0.58   0.45   MISS   MISS   0.41   0.51    ← unreliable
  80m   MISS   MISS   MISS   MISS   MISS   MISS   MISS    ← no detection
```
**Max reliable altitude: ~50m** (conf > 0.5 at all speeds)
**Blur effect: NEGLIGIBLE** (global shutter, max 2px blur at 50m/20m/s)

### Model 2: v2-1088 Retrained (11.7MB, sar_v2_1088)
```
         0m/s   2m/s   5m/s   8m/s  10m/s  15m/s  20m/s
  15m   0.91   0.91   0.91   0.91   0.91   0.91   0.90    ← all good
  20m   0.90   0.90   0.91   0.91   0.91   0.90   0.89    ← all good
  25m   0.92   0.92   0.93   0.92   0.92   0.91   0.92    ← all good
  30m   0.91   0.91   0.92   0.91   0.93   0.92   0.88    ← still strong
  40m   0.86   0.87   0.88   0.87   0.89   0.86   0.86    ← good
  50m   0.84   0.84   0.84   0.82   0.84   0.81   0.84    ← good!
  60m   0.84   0.80   0.83   0.85   0.82   0.81   0.84    ← still detecting!
  80m   0.66   0.66   0.69   0.56   MISS   0.73   0.45    ← borderline
```
**Max reliable altitude: ~60m** (conf > 0.8 at all speeds!)
**Blur effect: NEGLIGIBLE** (same camera, same physics)

## Comparison: Original vs v2-1088

| Altitude | Original conf | v2-1088 conf | Winner |
|----------|---------------|--------------|--------|
| 15m | 0.94 | 0.91 | Original (slightly) |
| 20m | 0.96 | 0.90 | Original |
| 25m | 0.94 | 0.92 | Similar |
| 30m | 0.89 | 0.91 | **v2-1088** |
| 40m | 0.76 | 0.86 | **v2-1088** (+10%) |
| 50m | 0.63 | 0.84 | **v2-1088** (+21%) |
| 60m | 0.48 | 0.84 | **v2-1088** (+36%!) |
| 80m | MISS | 0.66 | **v2-1088** (detects!) |

**v2-1088 is dramatically better at high altitude** because it was trained on real aerial data at 1088px resolution.

## When Does Blur Start Mattering?

**Short answer: IT DOESN'T** (for our setup)

| Altitude | Dummy size | Max blur at 20m/s | Blur % of dummy |
|----------|-----------|-------------------|-----------------|
| 15m | 83px | 7px | 8% |
| 20m | 62px | 5px | 8% |
| 30m | 41px | 3px | 7% |
| 50m | 25px | 2px | 8% |
| 60m | 20px | 1px | 5% |
| 80m | 15px | 1px | 7% |

Blur is always <10% of dummy size because:
1. **Global shutter** (IMX296) — 8ms exposure, no rolling shutter
2. **High altitude** — ground moves slowly in pixels
3. **Low GSD** — at 50m each pixel covers ~1.4m

**The real limit is ALTITUDE (dummy pixel size), not speed/blur.**

## Predictions for Pi

Since the model weights are identical, Pi should produce the SAME detection results.
The only difference is speed:

| Backend | Inference FPS | Full pipeline FPS |
|---------|---------------|-------------------|
| TFLite original (3.2MB) | 5.2 | ~4.5 |
| TFLite v2-1088 (11.7MB) | 3.1 | ~3.0 |
| NCNN v2-1088 (11.7MB) | 13.8 | ~9.5 |

**Prediction: Detection confidence on Pi will match laptop exactly.**
**Prediction: NCNN on Pi will have same detection as TFLite, just faster.**

## Pi Actual Results

*(Run on Pi and paste results here)*

```
TBD — run: python tests/laptop/blur_altitude_test.py --model best.tflite
TBD — run: python tests/laptop/blur_altitude_test.py --model cv_models/sar_v2_1088/best.tflite
TBD — run: python tests/laptop/blur_altitude_test.py --model cv_models/sar_v2_1088/best.tflite --backend ncnn
```

## Recommendation

**Use v2-1088 model with NCNN backend:**
- Detects reliably up to 60m (vs 50m with original)
- 84% confidence at 50m (vs 63% with original)
- 13.8 FPS inference (vs 3.1 FPS TFLite)
- Motion blur is not a concern at any realistic flight speed
