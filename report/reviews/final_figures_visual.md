# Final Figures Visual Inspection

Date: 2026-03-27
Reviewer: Claude Opus 4.6 (visual inspection of all PNGs)

---

## 1. architecture.png -- System Architecture Diagram

**Score: 7/10**

- **Text readability**: Good. All labels (Cube Orange+, Raspberry Pi 5, IMX296, etc.) are legible. Protocol labels (UART/MAVProxy, CSI-2, PWM, WiFi) are readable but the italic "433 MHz RC link" text is slightly small.
- **Colors**: Clean three-color legend (blue=hardware, green=software, white=ground). Effective use of the dashed box for "Airborne Platform".
- **Layout**: Logical left-to-right flow from flight controller to companion computer. Ground segment clearly separated at top.
- **Issues**:
  - The orange WiFi line from Ground Station clips through the "Airborne Platform" title text -- looks slightly messy.
  - The software bar (main.py | vision.py | planning.py | utils.py) is green but could be more prominent -- it blends into the background.
  - The Buzzer box hangs below IMX296 without a labeled connection type.
  - Missing: no power distribution shown (battery, BEC). Acceptable for a software-focused report.
- **Examiner impression**: Solid, professional. Shows the key hardware and communication links clearly. Minor visual polish needed on the WiFi line overlap.

**Verdict: PASS -- minor polish recommended but not blocking.**

---

## 2. state_machine.png -- Mission State Machine

**Score: 9/10**

- **Text readability**: Excellent. All state names (INIT, TAKEOFF, SEARCH, CENTERING, VERIFY, APPROACH, LANDING, DONE) are large, bold, and white-on-colored backgrounds.
- **Colors**: Excellent four-color scheme with clear legend: green=start/end, blue=autonomous, orange=operator decision, red=safety override. Very intuitive.
- **Layout**: Clean top-to-bottom flow showing the main mission progression. MANUAL override is clearly shown to the right with bidirectional dashed arrows. Rejection loop (N) on the left returns to SEARCH.
- **Transition labels**: "Detection", "M key (override)", "M key (resume)", "Confirmed [Y]", "Rejected [N]", "Link loss / RC kill / RTL (firmware)" -- all readable and well-placed.
- **Issues**:
  - The "Rejected [N]" arrow going from VERIFY back up to SEARCH is slightly cramped on the left edge -- the label overlaps the figure boundary marginally.
  - Missing states: CONNECTING and DESCENDING (mentioned in CLAUDE.md) are not shown. This may be intentional simplification for the report.
- **Examiner impression**: One of the best figures in the set. Clean, professional, immediately understandable. The color coding is a strong design choice.

**Verdict: PASS -- excellent quality.**

---

## 3. cv_pipeline.png -- Computer Vision Detection Pipeline

**Score: 7/10**

- **Text readability**: Good. All stage labels are clear. Timing annotations (1.5 ms, 0.3 ms, 196 ms) and resolution labels (1456x1088, 640x640) are readable.
- **Colors**: Consistent light blue boxes with orange summary text at the bottom. Clean.
- **Layout**: Linear left-to-right pipeline: Camera Frame -> Lens Undistort -> Resize to 640x640 -> YOLOv8n TFLite -> NMS Filter -> Detection (x, y, conf). Logical and easy to follow.
- **Issues**:
  - The figure is very short/flat -- significant white space above and below. When inserted in a LaTeX document this will waste vertical space or look undersized.
  - The total "~198 ms per frame (5.1 FPS)" does not match the sum: 1.5 + 0.3 + 196 = 197.8 ms, which rounds to ~198 ms. The FPS should be 1000/198 = 5.05 FPS. Stated as 5.1 FPS -- minor rounding discrepancy but acceptable.
  - The "conf > 0.2" label under NMS Filter contradicts the config which says confidence threshold is 0.4. This could confuse a careful examiner. NMS pre-filter at 0.2 vs final threshold at 0.4 may be intentional, but should be clarified.
  - No mention of the BGR color handling (a key design point from the project).
- **Examiner impression**: Informative and clean, but very thin. Would benefit from slightly more vertical content (e.g., add input/output tensor shapes, or a note about the TFLite backend).

**Verdict: PASS -- consider making it taller or adding detail to avoid looking sparse.**

---

## 4. mission_overview.png -- Mission Overview Map

**Score: 9/10**

- **Text readability**: Excellent. Title, axis labels (East/North in meters), legend entries, and annotations all legible.
- **Colors**: Excellent color choices: blue dashed = flight area, dark green solid = search area, red hatched = SSSI no-fly zone, orange dashed = focus area (PLB), grey = search pattern, green diamond = landing point. High contrast and distinct.
- **Data content**: Rich and informative. Shows take-off location (star), lawnmower search pattern, target with GPS estimate scatter, 7.5m offset landing point, RTL path, scale bar (50 m).
- **Layout**: Professional cartographic feel with north arrow, scale bar, and comprehensive legend.
- **Issues**:
  - The GPS estimate cluster (small green dots near target) is slightly hard to distinguish at this resolution -- could use a larger marker or a callout.
  - The "RTL" label near the return path is small.
  - The search pattern lines within the SSSI zone are visible -- this might prompt a question about whether the drone actually flies into the SSSI. If the geofence prevents this, the pattern lines should ideally be clipped. However, this may be intentional to show the "unprotected" scenario.
- **Examiner impression**: Outstanding figure. Looks publication-quality. Communicates the entire mission concept in one image.

**Verdict: PASS -- excellent, one of the strongest figures.**

---

## 5. geofence_diagram.png -- Geofence/NFZ Protection System

**Score: 8/10**

- **Text readability**: Good overall. Panel titles (a-d) are clear. The protection layer summary table (panel d) is readable. Speed reduction profile (panel c) has clear axis labels.
- **Colors**: Consistent with mission_overview.png. Good use of red for NFZ, orange for warning zones, green for safe areas. The "before/after" comparison (panels a vs b) is very effective.
- **Layout**: Four-panel layout is well organized: (a) without geofence, (b) with protection, (c) speed profile, (d) summary table. The 2x2 grid is logical.
- **Data content**: Shows the three-layer protection clearly: speed ramp, repulsive force, hard boundary. The deflected trajectory in panel (b) is a strong visual.
- **Issues**:
  - Panel (a) and (b) text annotations are quite small -- "7 path segments enter SSSI", "Lawnmower path crosses SSSI boundary", "Deflected trajectory" are readable but at the limit.
  - The speed reduction profile (panel c) labels "MANUAL" and "Speed Ramp" are small.
  - Panel (d) table text is on the edge of readability -- may not survive LaTeX scaling well.
  - The "X" markers in panel (a) showing violations are effective.
- **Examiner impression**: Very strong conceptual figure. The before/after comparison is compelling and the four-panel layout communicates a complex system well. The table in (d) is a nice touch.

**Verdict: PASS -- strong figure, ensure LaTeX scaling preserves table readability.**

---

## 6. optimization_network.png -- Optimisation Variable Dependency Network

**Score: 6/10**

- **Text readability**: Mostly readable but several labels are quite small, especially the mathematical notation inside boxes (e.g., subscript variables like "W(1-a)", "n_lines", "f_blur"). The three column headers (Decision Variables, Derived Quantities, Performance Metrics) are clear.
- **Colors**: Good three-color scheme: blue = decision variables, white = derived quantities, red/green = performance metrics (with "minimise"/"maximise" implied). Effective.
- **Layout**: Left-to-right dependency flow is logical. Lines show how inputs propagate through derived quantities to performance metrics.
- **Issues**:
  - **Line crossings are messy.** Multiple edges cross each other, especially in the center. This makes it hard to trace individual dependencies. A graph layout algorithm or manual rearrangement could reduce crossings significantly.
  - The line thickness legend (strong/medium/weak) at the bottom is good but the actual line differences are hard to distinguish in the figure -- they all look similar weight.
  - "NFZ margin d_nfz" at the bottom left connects only to "Time near NFZ" -- this isolated pair looks orphaned from the rest of the network.
  - Some boxes have very small subscript text that will be illegible at typical figure widths in a two-column or A4 report.
- **Examiner impression**: The concept is excellent and this kind of dependency network is exactly what an examiner wants to see for path planning optimization. However, the visual execution is cluttered. The crossing lines reduce clarity.

**Verdict: NEEDS IMPROVEMENT -- the concept is strong but the visual clutter from crossing lines hurts readability. Consider rearranging nodes to reduce crossings, or use curved/colored lines to distinguish paths.**

---

## 7. sensitivity_matrix.png -- Sensitivity Heatmap

**Score: 9/10**

- **Text readability**: Excellent. Row labels (Altitude, Ground speed, Scan angle, Overlap fraction, NFZ margin), column labels (Coverage %, Detection P, Mission Time, Energy Wh, NFZ Risk), and cell annotations are all clearly readable. The brief explanatory text in each cell (e.g., "+0.6 wider lines", "-0.3 smaller target") is a great touch.
- **Colors**: Red-green diverging colormap is intuitive: green = increasing the input improves the metric, red = worsens it. The colorbar on the right is clear. The footnote explains the convention.
- **Data content**: 5x5 matrix with quantitative sensitivity values and qualitative descriptions. Rich and informative.
- **Issues**:
  - The green-red colormap may not be accessible to color-blind readers. A blue-red or purple-orange diverging scheme would be more inclusive. However, this is a minor concern for a university report.
  - Some cells have text that is slightly dense (two lines of text + number).
- **Examiner impression**: Outstanding analytical figure. Shows deep understanding of parameter interactions. The combination of numerical values with brief explanations is very effective.

**Verdict: PASS -- excellent, publication-quality analytical figure.**

---

## 8. sensitivity_spider.png -- Spider/Radar Chart

**Score: 8/10**

- **Text readability**: Good. Title includes the configuration parameters (35 m, 8 m/s, 70 deg, 20%, 30 m margin). Each axis has dual labels showing both the achieved value and theoretical best (e.g., "Detection 92% / 99%", "Coverage 96% / 100%").
- **Colors**: Blue filled polygon for selected configuration, grey dashed for theoretical best. Clean and effective. The blue fill with transparency works well.
- **Data points**: 0.93 Detection, 0.96 Coverage, 1.00 NFZ Safety, 0.40 Energy, 0.38 Time. The data point labels are readable.
- **Layout**: Five-axis radar chart, well proportioned.
- **Issues**:
  - The "Time" and "Energy" axes show low scores (0.38 and 0.40) which correctly shows these as weaknesses. However, it might prompt an examiner to ask why these are so low -- ensure the report text explains the trade-off.
  - The legend is small and positioned in the upper right -- adequate but could be slightly larger.
  - The grey "Theoretical best" line is very faint -- could be slightly darker for visibility.
- **Examiner impression**: Clean and informative radar chart that effectively communicates the trade-off space. The dual-value axis labels are a nice design decision.

**Verdict: PASS -- strong figure showing good engineering judgment.**

---

## 9. benchmark_comparison.png -- Inference Benchmark Bar Chart

**Score: 8/10**

- **Text readability**: Good. Title clear. X-axis labels identify each configuration (TFLite FP32 best.tflite 3.2 MB, TFLite FP32 sar_v2_1088 11.7 MB, etc.). Y-axis (Inference Time ms) is clear. FPS annotations above each bar are very helpful.
- **Colors**: Blue solid = measured, orange hatched = projected. Clean distinction.
- **Data content**: Six configurations compared: three measured TFLite variants (~208ms each), two projected alternatives (NCNN ~92ms, TFLite FP16 ~112ms), and Ultralytics PyTorch on laptop (~1250ms). The contrast between Pi inference and laptop PyTorch is dramatic and informative.
- **Issues**:
  - The x-axis labels are quite dense and slightly rotated -- at smaller figure sizes these could become hard to read. The model file sizes in the labels are useful but add to the density.
  - The Ultralytics bar (1250ms) dominates the chart, compressing the other bars visually. A broken y-axis or log scale might show the Pi-side differences more clearly. As-is, the three TFLite bars look nearly identical and their differences are invisible.
  - "projected" label could be more prominently explained (e.g., a footnote saying these are estimated from documentation, not measured).
- **Examiner impression**: Informative comparison. The measured vs projected distinction is honest and good engineering practice. The laptop comparison contextualizes the Pi performance well.

**Verdict: PASS -- good figure, consider whether the y-axis scale compresses the Pi-side bars too much.**

---

## 10. confusion_matrix.png -- YOLOv8n Confusion Matrix

**Score: 8/10**

- **Text readability**: Excellent. All labels (True Class: Dummy/Background, Predicted Class: Dummy/Background) are clear. The cell values (TP=989, FP=6, FN=11, TN=50) are large and bold. The summary metrics at the bottom (Precision=0.994, Recall=0.989, F1=0.991) are clearly readable.
- **Colors**: Green for correct predictions (TP, TN), pink/red for errors (FP, FN). Standard and intuitive.
- **Data content**: Strong results. 989 true positives with only 6 false positives and 11 false negatives. The class imbalance (995 dummy samples vs 61 background) is visible and could be discussed in the report.
- **Issues**:
  - The matrix is labeled TP/FP/FN/TN explicitly inside the cells, which is helpful for clarity but slightly unusual for a standard confusion matrix figure (most just show the counts). This is actually a positive -- makes it very accessible.
  - The class imbalance (995 positives vs 61 negatives) should be acknowledged in the report text. The TN=50 with only 61 total negatives means 11 negatives were misclassified as dummy (FP=6 seems inconsistent -- FP should be background predicted as dummy). Actually: FP=6 means 6 background images were predicted as dummy, FN=11 means 11 dummy images were missed. This checks out: 989+11=1000 dummy, 6+50=56 background. Wait -- that gives 1056 total, not a round number. The numbers seem plausible but the dataset composition should be stated.
  - The "Validation Set" in the title is good -- makes clear this is not training performance.
- **Examiner impression**: Clean, standard confusion matrix with strong results. The explicit TP/FP/FN/TN labels add clarity.

**Verdict: PASS -- clean and informative.**

---

## Summary Table

| # | Figure | Score | Verdict |
|---|--------|-------|---------|
| 1 | architecture.png | 7/10 | PASS -- minor WiFi line overlap, software bar blends in |
| 2 | state_machine.png | 9/10 | PASS -- excellent, clean color-coded flow |
| 3 | cv_pipeline.png | 7/10 | PASS -- too flat/thin, conf threshold discrepancy |
| 4 | mission_overview.png | 9/10 | PASS -- publication quality, strong cartographic design |
| 5 | geofence_diagram.png | 8/10 | PASS -- strong 4-panel layout, small text in table |
| 6 | optimization_network.png | 6/10 | NEEDS IMPROVEMENT -- crossing lines create visual clutter |
| 7 | sensitivity_matrix.png | 9/10 | PASS -- outstanding analytical heatmap |
| 8 | sensitivity_spider.png | 8/10 | PASS -- effective trade-off visualization |
| 9 | benchmark_comparison.png | 8/10 | PASS -- good, y-axis scale compresses Pi bars |
| 10 | confusion_matrix.png | 8/10 | PASS -- clean standard matrix with strong results |

**Overall average: 7.9/10**

### Figures Needing Regeneration

1. **optimization_network.png (6/10)** -- PRIORITY. The crossing lines make the dependency network hard to follow. Rearrange node positions to minimize edge crossings, or use colored/curved edges to distinguish paths. The concept is excellent but the execution needs a cleaner layout.

### Figures Worth Minor Touch-ups (optional)

2. **cv_pipeline.png (7/10)** -- Make the figure taller (add tensor shape annotations or backend details) so it does not look sparse in the report. Clarify the conf > 0.2 vs 0.4 threshold.
3. **architecture.png (7/10)** -- Fix the WiFi line clipping through the title text. Minor 5-minute fix.
4. **benchmark_comparison.png (8/10)** -- Consider a broken y-axis or inset zoom to show the differences between the three TFLite variants more clearly.

### No Action Needed

- state_machine.png, mission_overview.png, geofence_diagram.png, sensitivity_matrix.png, sensitivity_spider.png, confusion_matrix.png -- all strong as-is.
