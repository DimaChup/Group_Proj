# Blur + Altitude Detection Comparison — LAPTOP vs PI VALIDATED

Date: 2026-03-19

---

## 1. Confidence vs Altitude (at 0 m/s — no blur)

```
Conf
1.0 ┬─────────────────────────────────────────────────────
    │
0.9 ┤  ●━━━━━━●━━━━━━●━━━━━━●                              ← v2-1088 Pi (TFLite)
    │  ○------○------○------○╲                              ← v2-1088 Laptop
    │  ■━━━━━━■━━━━━━■        ╲  ●━━━━●━━━━●
0.8 ┤  □------□------□         ╲ ○----○----○
    │                  ■         ╲            ╲  ●
    │                  □╲         ●             ╲ ○
0.7 ┤                    ■        ○
    │                    □╲
    │                      ■
0.6 ┤                      □╲                         ●
    │                        ■                        ○
    │                        □
0.5 ┤                          ■
    │                          □
    │                            ■
0.4 ┤                            □
    │
    │
0.0 ┤                              ■ □                  ● ○
    ┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────
   15m    20m    25m    30m    40m    50m    60m    80m

   ● v2-1088 Pi TFLite    ○ v2-1088 Laptop
   ■ Original Pi TFLite   □ Original Laptop
```

---

## 2. Detection Confidence Table — ALL RESULTS

### Original Model (3.2MB) — Laptop vs Pi

```
         0m/s   2m/s   5m/s   8m/s  10m/s  15m/s  20m/s
        L / P  L / P  L / P  L / P  L / P  L / P  L / P
  15m  .94/.95 .94/.95 .94/.94 .95/.95 .94/.94 .93/.93 .91/.92
  20m  .96/.96 .96/.96 .96/.96 .97/.97 .96/.97 .96/.96 .96/.96
  25m  .94/.94 .94/.94 .93/.94 .94/.94 .94/.94 .92/.93 .92/.93
  30m  .89/.90 .87/.88 .90/.88 .87/.87 .85/.89 .89/.86 .86/.84
  40m  .76/.74 .74/.73 .75/.76 .66/.77 .72/.75 .75/.80 .75/.74
  50m  .63/.68 .61/.63 .62/.56 .58/.61 .66/.67 .56/.46 .57/.63
  60m  .48/.47 .58/.50 .45/.47 MISS/-- MISS/-- .41/.52 .51/.44
  80m  MISS    MISS    MISS    MISS    MISS    MISS    MISS
```

### v2-1088 Model (11.7MB) — Laptop vs Pi

```
         0m/s   2m/s   5m/s   8m/s  10m/s  15m/s  20m/s
        L / P  L / P  L / P  L / P  L / P  L / P  L / P
  15m  .91/.91 .91/.91 .91/.91 .91/.91 .91/.90 .91/.91 .90/.91
  20m  .90/.90 .90/.90 .91/.90 .91/.91 .91/.91 .90/.90 .89/.90
  25m  .92/.91 .92/.92 .93/.92 .92/.91 .92/.92 .91/.92 .92/.92
  30m  .91/.91 .91/.91 .92/.91 .91/.91 .93/.91 .92/.91 .88/.90
  40m  .86/.89 .87/.86 .88/.87 .87/.89 .89/.86 .86/.87 .86/.87
  50m  .84/.83 .84/.84 .84/.87 .82/.85 .84/.83 .81/.84 .84/.84
  60m  .84/.84 .80/.84 .83/.83 .85/.86 .82/.83 .81/.85 .84/.84
  80m  .66/--  .66/.54 .69/.62 .56/.72 MISS/-- .73/.59 .45/--
```

---

## 3. Prediction Accuracy — Did Laptop Match Pi?

| Altitude | Original (L vs P) | v2-1088 (L vs P) | Verdict |
|----------|-------------------|-------------------|---------|
| 15m | 0.94 vs 0.95 | 0.91 vs 0.91 | MATCH |
| 20m | 0.96 vs 0.96 | 0.90 vs 0.90 | MATCH |
| 25m | 0.94 vs 0.94 | 0.92 vs 0.91 | MATCH |
| 30m | 0.89 vs 0.90 | 0.91 vs 0.91 | MATCH |
| 40m | 0.76 vs 0.74 | 0.86 vs 0.89 | MATCH |
| 50m | 0.63 vs 0.68 | 0.84 vs 0.83 | MATCH |
| 60m | 0.48 vs 0.47 | 0.84 vs 0.80 | MATCH |
| 80m | MISS vs MISS | 0.66 vs MISS* | CLOSE |

**Average error: ±0.03 confidence** — Laptop predictions validated on Pi!

*v2-1088 at 80m: laptop detected (0.66), Pi missed in some runs — borderline altitude.

---

## 4. v2-1088 vs Original — Side by Side

| Altitude | Dummy px | Original | v2-1088 | v2 advantage |
|----------|----------|----------|---------|-------------|
| 15m | 83px | 0.95 | 0.91 | Original +4% |
| 20m | 62px | 0.96 | 0.90 | Original +6% |
| 25m | 50px | 0.94 | 0.92 | Similar |
| 30m | 41px | 0.90 | 0.91 | Similar |
| 40m | 31px | 0.74 | 0.89 | **v2 +15%** |
| 50m | 25px | 0.68 | 0.83 | **v2 +15%** |
| 60m | 20px | 0.47 | 0.84 | **v2 +37%!!** |
| 80m | 15px | MISS | MISS* | Both fail |

**v2-1088 is dramatically better above 40m** — the altitude that matters for SAR search.

---

## 5. When Does Blur Start Mattering?

**Answer: IT DOESN'T** (for our hardware)

```
Blur (pixels) at different speed × altitude:

         0m/s  5m/s  10m/s  15m/s  20m/s
  15m     1     1      3      5      7    ← worst case: 7px on 83px dummy = 8%
  30m     1     1      1      2      3    ← 3px on 41px dummy = 7%
  50m     1     1      1      1      2    ← 2px on 25px dummy = 8%
  80m     1     1      1      1      1    ← negligible
```

Blur is always <10% of dummy size because:
- **IMX296 global shutter** — 8ms exposure (no rolling shutter smear)
- **High altitude** — ground moves slowly relative to camera
- **Blur < 8px** even at worst case (15m altitude, 20 m/s)

**The limiting factor is ALTITUDE (dummy pixel size), not speed.**

---

## 6. Speed Comparison

| Backend | Model | Inference FPS | Full Pipeline FPS |
|---------|-------|---------------|-------------------|
| TFLite | Original (3.2MB) | 5.2 | ~4.5 |
| TFLite | v2-1088 (11.7MB) | 3.1 | ~3.0 |
| **NCNN** | **v2-1088 (11.7MB)** | **13.8** | **~9.5** |

---

## 7. RECOMMENDATION

**Use v2-1088 model with NCNN backend:**

| Metric | Value |
|--------|-------|
| Max reliable altitude | **60m** (0.84 confidence) |
| Reliable at search altitude (50m) | **0.83 confidence** |
| Speed (full pipeline) | **~9.5 FPS** |
| Blur impact | **None** (global shutter) |
| Improvement over original at 60m | **+37% confidence** |
| Speed improvement over TFLite | **4.5x faster** |

**Configuration:**
```bash
python main.py --search-area --model cv_models/sar_v2_1088/best.tflite --backend ncnn --alt 50
```
