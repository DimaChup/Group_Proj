# Final Charts Visual Inspection

Reviewed: 2026-03-27. All 8 figures in `report/figs/`.

---

## 1. gps_bullseye.png -- Score: 8/10

**What it shows:** Scatter plot of GPS target estimates around true position, with CEP50 (2.3 m) and CEP95 (5.1 m) ellipses on a bullseye grid (5 m, 10 m, 15 m rings).

**Strengths:**
- Axes labeled clearly (East offset / North offset in metres).
- Legend is complete: CEP50, CEP95, GPS estimates, true position, centroid with coordinates.
- Concentric rings give immediate sense of scale.
- Centroid offset (+0.6, -0.2 m) shown -- useful detail.

**Issues:**
- The chart is rendered at a small resolution; some text (e.g. "Bearing 155" annotation, ring labels) is hard to read at print size.
- The dashed CEP ellipses are thin and may not reproduce well in black-and-white printing.
- A few outlier points at ~15 m east are visually dominant but not discussed in the legend.

**Recommendation:** Increase render resolution or font size. Consider annotating the outlier cluster or mentioning N=XX in the legend.

---

## 2. estimator_comparison.png -- Score: 9/10

**What it shows:** Bar chart comparing 4 GPS estimation methods by CEP50 error (metres): Rolling Average (4.5 m), Cumulative Average (3.2 m), Kalman Filter (2.8 m), Inverse Variance Weighted (2.3 m, highlighted as "Selected").

**Strengths:**
- Very clean, publication-quality layout.
- Error bars present on all four bars.
- Values annotated directly above each bar -- no guessing.
- "Selected" badge on the chosen method is effective and immediately clear.
- Y-axis starts at 0 (no truncation tricks).

**Issues:**
- No x-axis label (though bar labels substitute adequately).
- Error bar meaning not stated (standard deviation? confidence interval? min-max?).

**Recommendation:** Add a footnote or caption clarifying what the error bars represent.

---

## 3. gps_error_direction.png -- Score: 7/10

**What it shows:** Two-panel figure. Left: polar scatter of error distribution at heading 155 degrees, 10 m/s. Right: grouped bar chart of along-track vs cross-track median absolute error at 5, 7.5, and 10 m/s.

**Strengths:**
- Dual-panel layout is informative -- directional bias on the left, speed dependence on the right.
- Along-track vs cross-track decomposition is the right analysis for GPS timing lag.
- Annotation box on the right panel explains the GPS timing lag mechanism.
- Color coding (orange = along-track, blue = cross-track) is consistent across panels.

**Issues:**
- Left polar plot is quite small and dense; individual points overlap heavily.
- The "5m" and "10m" rings on the polar plot are faint and hard to read.
- Right panel bar labels (1.9, 1.1, 2.0, 1.1, 2.1, 1.0) are small.
- Overall figure is low resolution for a two-panel layout -- would benefit from being wider.

**Recommendation:** Render at higher resolution or make the figure wider in the report. Increase font sizes on the polar plot rings.

---

## 4. detection_heatmap.png -- Score: 7/10

**What it shows:** Spatial heatmap of detections over the search area polygon, with detection confidence as color, search area boundary, estimated position, true target, CEP50 circle, and take-off location.

**Strengths:**
- Search area polygon and take-off location give spatial context.
- Color bar (Detection Confidence 0.0-1.0) is labeled.
- CEP50 circle around the target cluster is useful.
- Legend includes all relevant markers.

**Issues:**
- The heatmap gradient is subtle and hard to distinguish at the cluster center -- most points appear to be high confidence (green/yellow) but the gradient is not very visible.
- "start" and "Take-off" labels overlap or are placed in low-contrast areas.
- Axes are in "m from take-off" which is good, but the figure is small and labels are cramped.
- The search area polygon lines are very light grey and may disappear in print.

**Recommendation:** Increase figure size. Make the search area boundary darker or dashed. Consider a discrete color scale (e.g. 3-4 bins) if the continuous gradient is not adding information.

---

## 5. training_curves.png -- Score: 9/10

**What it shows:** Dual-axis line chart of training loss (left y-axis, orange) and mAP50 (right y-axis, blue) over 150 epochs, with phase annotations ("Rapid Adaptation", "Refinement", "Plateau") and best epoch marker (epoch 127).

**Strengths:**
- Dual-axis is executed well -- colors match the axis labels.
- Phase annotations add interpretive value beyond raw curves.
- "Best (epoch 127)" vertical dashed line is clear.
- Loss converges smoothly; mAP50 rises and plateaus as expected -- data is plausible.
- Epoch axis labeled, both y-axes labeled with units.

**Issues:**
- The mAP50 curve has some noise/jitter in the 20-60 epoch range that is not discussed (normal for small datasets but could be noted).
- Phase boundary labels are slightly hard to read at small print size.

**Recommendation:** Minor -- could add a note that mAP50 jitter is expected with a 366-image dataset. Otherwise excellent.

---

## 6. altitude_detection_table.png -- Score: 8/10

**What it shows:** Three-panel horizontal bar chart: target pixel size (px in 640 input), detection confidence, and detection rate (%) across altitudes from 10 m to 50 m.

**Strengths:**
- Three-panel layout gives a complete operational picture at a glance.
- Color coding on detection rate panel (green >90%, yellow 70-90%, orange/red <70%) is effective.
- Values annotated on each bar.
- Altitude range (10-50 m) is practical and relevant.
- Data is physically plausible: pixel size decreases with altitude, confidence and detection rate follow.

**Issues:**
- The "Target Pixel Size" panel x-axis label says "px in 640 input" -- this is technically correct but may confuse readers who don't know about the 640x640 model input resize.
- At 50 m, detection rate is 20% and confidence is 0.30 -- this is right at the 0.4 threshold boundary, so the 20% rate makes sense, but worth noting the threshold in the caption.

**Recommendation:** Add a brief note about the confidence threshold (0.4) either in the figure or caption. Clarify "640 input" for non-technical readers.

---

## 7. detection_envelope.png -- Score: 9/10

**What it shows:** Dual-axis plot of detection confidence (left) and target pixel size (right) vs altitude, with multiple curves for different blur conditions: no blur (ideal), 10 m/s at 1/100 s, 15 m/s at 1/100 s, and 10 m/s with global shutter (1/500 s). Shaded operational envelope (15-40 m) and confidence threshold (0.2) marked.

**Strengths:**
- This is the most informative figure in the set -- combines altitude, blur, confidence, and pixel size in one view.
- Line styles are distinct (solid, dashed, dash-dot, dotted) and colors are distinguishable.
- Operational envelope shading is immediately clear.
- "Blur significant below 15 m only" annotation is valuable.
- Confidence threshold line at 0.2 is marked.
- Right y-axis (target size in pixels) adds context for why confidence drops.
- "~10 px min" annotation at the bottom right explains the detection floor.

**Issues:**
- The confidence threshold is marked at 0.2, but the project uses 0.4 (per config/vision.py). This is either a different threshold for this analysis or an error -- needs verification.
- Legend is slightly crowded in the upper right.

**Recommendation:** Verify that the 0.2 threshold is intentional for this figure (vs the operational 0.4). If 0.4 is correct, update. Otherwise add a caption note explaining why 0.2 is shown here.

---

## 8. blur_vs_altitude.png -- Score: 8/10

**What it shows:** Two-panel figure comparing pixel displacement from motion blur at 1/100 s exposure (left) and 1/500 s exposure (right), across altitudes 5-50 m, for ground speeds 5, 10, and 15 m/s. Operational envelope (15-40 m) shaded. Blur threshold at 3 px marked.

**Strengths:**
- Side-by-side exposure comparison is the right layout for this analysis.
- Three speed curves in distinct colors (green, blue, red) are easy to distinguish.
- Operational envelope shading is consistent with the detection envelope figure.
- Blur threshold (3 px) dashed line provides a clear pass/fail boundary.
- Y-axis scales are different between panels (0-50 px vs 0-10 px), which is appropriate given the magnitude difference.
- "Blur threshold (3 px)" annotation on the right panel.

**Issues:**
- The different y-axis scales between panels could mislead a quick reader into thinking 1/500 s has comparable blur to 1/100 s. A note or shared scale option would help.
- At 1/100 s exposure (left panel), 15 m/s at 5 m altitude gives ~50 px blur -- this is extreme and probably unrealistic (drone would not fly that fast at 5 m), but the curve is mathematically correct.
- Legend is slightly small.

**Recommendation:** Consider noting in the caption that y-axis scales differ between panels. The mathematical model is clean and plausible.

---

## Summary Table

| Figure | Score | Key Strength | Top Issue |
|--------|-------|-------------|-----------|
| gps_bullseye | 8/10 | Clear CEP metrics with spatial context | Small render size, thin ellipse lines |
| estimator_comparison | 9/10 | Clean, annotated, highlights selection | Error bar meaning not stated |
| gps_error_direction | 7/10 | Along/cross-track decomposition | Small and dense, needs higher resolution |
| detection_heatmap | 7/10 | Spatial context with search polygon | Subtle gradient, light polygon lines |
| training_curves | 9/10 | Dual-axis done right, phase annotations | Minor jitter not discussed |
| altitude_detection_table | 8/10 | Three-panel operational picture | "640 input" may confuse readers |
| detection_envelope | 9/10 | Most informative figure, combines 4 variables | Confidence threshold 0.2 vs operational 0.4 |
| blur_vs_altitude | 8/10 | Clear exposure comparison, threshold line | Different y-axis scales between panels |

**Overall average: 8.1/10**

**Top 3 action items:**
1. **detection_envelope.png** -- Verify the 0.2 confidence threshold (project uses 0.4). Fix or explain in caption.
2. **gps_error_direction.png** and **detection_heatmap.png** -- Render at higher resolution or increase figure width in the report layout.
3. All figures -- Ensure captions in the LaTeX report explain any non-obvious details (error bar meaning, threshold values, "640 input" preprocessing).
