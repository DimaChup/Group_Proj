# System Description Review

Deep review of `report/sections/system_description.tex` (214 lines).

---

## 1. Architecture Diagram -- PASS

- `architecture.pdf` exists in `figs/`, referenced as `Figure~\ref{fig:architecture}` (line 52).
- Caption describes module dependency graph. Good.
- Also has `pi_system.pdf` (Figure 3, line 58) showing hardware data flow. Excellent -- two architectural views.
- **Minor:** Consider whether the caption for fig:architecture should mention the four layers explicitly (config, independent, domain, orchestration) so the figure is self-contained.

## 2. Hardware BOM -- MOSTLY COMPLETE, one concern

- Table `tab:hw-bom` (lines 22-39) lists 6 rows: Cube Orange+ FC, Here3 GPS, Pi 5, IMX296 camera, frame+motors+ESCs, battery+RC+misc. Total ~565 GBP.
- **Missing from BOM:** Telemetry radio (SiK/RFD900 or Wi-Fi link -- how does the ground station laptop receive MAVLink over Wi-Fi? Line 41 says "via Wi-Fi" but no Wi-Fi hardware is listed). If using the Pi's built-in Wi-Fi, state that explicitly.
- **Missing from BOM:** Any mention of cabling/connectors for Pi-to-Cube UART (JST-GH cable, logic level converter if needed).
- **Brief equipment list match:** The BOM covers the Hexsoon EDU-450, Cube Orange+, Pi 5, and camera as expected from the course-provided kit. The frame was "provided" per other review docs -- consider noting which items were provided vs purchased to be transparent with the examiner.
- **Cost discrepancy flagged elsewhere:** Exec summary says "airframe cost under 400 GBP" but BOM says 565 GBP total. Already flagged in SCORING_D6_v2.md -- ensure consistency.

## 3. CV Pipeline -- PASS, well done

- Section 2.3 (lines 100-119) covers preprocessing, inference, backends, and performance.
- **Timing present:** "206.5 ms per frame (4.8 FPS)" (line 119), "208 ms" in figure caption (line 113).
- `cv_pipeline.pdf` exists and is referenced (Figure~\ref{fig:cv_pipeline}, line 114).
- Three backends described (NCNN, Ultralytics, TFLite) with auto-selection.
- Smart detection mode documented (k consecutive frames).
- Overlap calculation present (91%, 11-17 opportunities per target).
- **Suggestion:** Add a 1-line note about the confidence threshold value (0.2 is mentioned on line 106, but the operational threshold used for triggering investigation vs the filtering threshold should be distinguished -- 0.2 is the raw filter, 0.4 is used in practice per config).

## 4. State Machine Diagram -- PASS with coverage gap

- `state_machine.pdf` exists in `figs/`, referenced as Figure~\ref{fig:state_machine} (line 133).
- States enumerated in the four-phase list (lines 138-143).
- **Cross-check against states.py (20 states):**

| State in states.py | Mentioned in tex? | Where |
|---|---|---|
| INIT | Yes | line 139 |
| CONNECTING | Yes | line 139 |
| ARMING | Yes | line 139 |
| TAKEOFF | Yes | line 139 |
| PRE_WAYPOINTS | Yes | line 140 |
| TRANSIT_TO_SEARCH | Yes | line 140 |
| SEARCH | Yes | line 140 |
| CENTERING | Yes | line 141 |
| DESCENDING | **NO** | Missing from body text |
| VERIFY | Yes | line 141 |
| HOVER | **NO** | Missing from body text |
| APPROACH | Yes | line 141 |
| RETURN_TO_SEARCH | **NO** | Missing from body text |
| RETURN_FROM_MANUAL | **NO** | Missing from body text |
| HOVER_TARGET | Yes | line 141 |
| RETURN_TRANSIT | Yes | line 142 |
| RETURN_HOME | Yes | line 142 |
| LANDING | Yes | line 142 |
| MANUAL | **Implied** | line 145 mentions "manual override" but MANUAL state not named |
| DONE | Yes | line 142 |

- **5 states not explicitly named:** DESCENDING, HOVER, RETURN_TO_SEARCH, RETURN_FROM_MANUAL, MANUAL. The text says "20-state FSM" and references Appendix A1 for the full table, so this is defensible -- but DESCENDING is a core mission phase (between CENTERING and VERIFY) and its omission from the engagement sequence is a factual gap. The engagement sequence reads "CENTERING -> VERIFY -> APPROACH -> HOVER_TARGET" but should read "CENTERING -> DESCENDING -> VERIFY -> APPROACH -> HOVER_TARGET".
- **Recommendation:** Fix the engagement bullet to include DESCENDING between CENTERING and VERIFY. Optionally add RETURN_TO_SEARCH (what happens on N at VERIFY?) and MANUAL.

### Suggested fix (line 141):

```latex
\item \textbf{Engagement:} CENTERING (fly to GPS estimate) $\to$ DESCENDING (reduce altitude for close-up view) $\to$ VERIFY (operator Y/N/I with 120\,s timeout) $\to$ APPROACH (7.5\,m offset) $\to$ HOVER\_TARGET (servo payload release).
```

## 5. GPS Estimation Math -- PASS, excellent

- Section 2.6 (lines 148-196) is strong: pinhole camera model, GSD formula, heading rotation, WGS 84 conversion.
- Three fusion methods documented: spatial clustering, inverse-variance weighting, Kalman filter.
- Quantitative results: CEP50 = 2.3 m, max error = 16.5 m.
- Four subfigures (bullseye, directional error, convergence, estimator comparison) -- all PDFs exist in `figs/`.
- GPS timing lag attribution is a nice touch (100-200 ms latency).
- **No issues.**

## 6. Ground Station -- THIN (reviewer flagged)

- Section 2.7 (lines 199-201) is exactly **3 sentences / 4 lines**. This is the weakest subsection.
- Content present: MJPEG, 2D GPS grid, 9 buttons, latency, headless mode, passive mode.
- **What's missing:**
  - No figure of the ground station UI (screenshot or diagram).
  - No description of the operator workflow (what does the operator actually see and do?).
  - No mention of the web architecture (Flask/ThreadingHTTPServer, streaming endpoint, /cmd endpoint).
  - No discussion of why browser-based (vs native app, vs Mission Planner overlay).
  - No mention of the dual-output architecture (UDP for scripts + TCP for Mission Planner).

### Suggested expanded text:

```latex
\subsection{Ground Station}\label{sec:groundstation}

The ground station is a browser-based dashboard served by a threaded HTTP server
on the Pi at port~8090, accessible from any device on the local Wi-Fi network.
Figure~\ref{fig:ground_station} shows the interface layout.

The dashboard provides three primary panels: (1)~a live MJPEG video stream with
detection bounding boxes, confidence scores, and target ID overlays; (2)~a 2D GPS
grid centred on the search area showing numbered detection clusters, the drone's
current position, and the planned search path; and (3)~a command panel with nine
buttons: arm, takeoff, investigate (N), confirm target (Y), mark as interest (I),
reject as false positive (X), land, RTL, and manual override (M).

MJPEG was selected over H.264/WebRTC for three reasons: minimal client-side
complexity (a single \texttt{<img>} tag), no transcoding latency on the Pi's CPU,
and graceful degradation on dropped frames (each frame is independently decodable).
Measured end-to-end latency is approximately \SI{300}{\milli\second}.

Headless operation is auto-detected when no \texttt{DISPLAY} environment variable
is set, enabling deployment over SSH without X11 forwarding. In this mode, all
\texttt{cv2.imshow} calls are skipped and operator interaction occurs exclusively
through the browser interface or terminal keypresses. A passive monitoring mode
(\texttt{passive\_watch.py}) provides the same video stream and detection overlays
but issues zero flight commands, enabling safe observation during manual RC flights.

\begin{figure}[ht]
\centering
\includegraphics[width=0.85\textwidth]{ground_station}
\caption{Browser-based ground station interface showing MJPEG video with detection
overlay (left), GPS cluster map (centre), and operator command buttons (right).}
\label{fig:ground_station}
\end{figure}
```

**Action needed:** Generate `ground_station.pdf` -- either a screenshot from simulation or a diagram. This subsection desperately needs a figure.

## 7. Search Pattern -- ADEQUATE but missing depth

- Section 2.4 (lines 122-124) is a single paragraph. It covers the algorithm steps, strip spacing, overlap, and mentions Bezier smoothing and PLB redirect.
- **The orphaned `05_path_planning.tex` (182 lines) contains far stronger content:**
  - Coverage path planning literature comparison (3 algorithms evaluated)
  - Formal coverage guarantee proof (via Choset's boustrophedon decomposition)
  - Lane width equations with worked numerical example
  - 216-configuration parametric sweep for scan angle optimisation
  - Energy analysis model (power equation, transit vs search split)
  - Bezier smoothing equations
  - Focus area (PLB redirect) description
  - Spiral pattern alternative
  - Comparison table (5 algorithms)
  - Flight parameters table
  - `coverage_vs_time.pdf` figure (exists in figs/)

- **This is the report's biggest missed opportunity.** The orphaned file has 4 pages of the report's best technical content that is invisible in the compiled PDF.

### Recommendation (choose one):

**(A) Include as body section (if page budget allows):**
Add `\input{sections/05_path_planning}` to `main.tex` between system_description and requirements_verification. This adds ~3-4 pages. Check against the 15-page limit.

**(B) Include as appendix + pull key content into body:**
Add as an appendix and expand the body subsection to ~1 page with: the coverage guarantee equation, the lane width derivation, and a reference to the appendix for the full parametric sweep.

**(C) Merge key content into system_description.tex:**
Replace the 3-line subsection with ~1 page covering: algorithm steps (already there), coverage guarantee equation (Eq 1-2 from the orphaned file), the `coverage_vs_time` figure, and the comparison table. Reference the 216-config sweep results in one sentence. This is the safest option for page budget.

### Suggested replacement for Section 2.4 (option C, ~30 lines):

```latex
\subsection{Search Pattern Generation}\label{sec:search-pattern}

The lawnmower (boustrophedon) pattern was selected from three candidates---boustrophedon, spiral, and probabilistic---for its formal coverage guarantee~\cite{choset2001coverage}, predictable path length, and alignment with JSAR search protocols. Both lawnmower and spiral generators are implemented; all field missions use the lawnmower pattern for wide-area search.

\paragraph{Rotated-mask algorithm.}
The waypoint generator (\texttt{planning.py}) uses a rotate--rasterise--zigzag--rotate-back approach: (1)~rasterise the GPS polygon into a binary mask; (2)~rotate to align with the longest edge via the minimum-area bounding rectangle (rotating calipers), minimising U-turn count; (3)~compute strip spacing from the camera footprint; (4)~cast horizontal scan lines with $\tfrac{1}{3}$-strip inset to prevent boundary overshoot; (5)~optimise start corner for minimal transit; (6)~inverse-rotate to GPS coordinates. B\'{e}zier-smoothed U-turns maintain momentum through turns.

\paragraph{Coverage guarantee.}
The strip spacing is derived from the thin-lens ground footprint:
\begin{equation}\label{eq:footprint}
  W_g = \frac{w_s \cdot h}{f}, \qquad
  L = W_g\,(1 - \alpha)
\end{equation}
where $w_s = \SI{5.02}{\milli\metre}$ (IMX296 sensor width), $f = \SI{5.46}{\milli\metre}$ (calibrated focal length), $h$ is altitude, and $\alpha = 0.20$ is the overlap fraction. At $h = \SI{35}{\metre}$: $W_g \approx \SI{32.2}{\metre}$, $L \approx \SI{25.7}{\metre}$. Since $L < W_g$, consecutive swaths overlap by at least $\alpha \cdot W_g \approx \SI{6.4}{\metre}$, guaranteeing every ground point falls within at least one swath under \SIrange{2}{3}{\metre} GPS drift.

\paragraph{Scan angle optimisation.}
A 216-configuration parametric sweep (6~altitudes $\times$ 36~angles) confirmed the optimal scan angle at \SIrange{65}{75}{\degree}, consistent with the polygon's elongation. Deviating by \SI{30}{\degree} increases scan-line count by ${\sim}$\SI{40}{\percent}. The automatic angle from \texttt{cv2.minAreaRect} matches the optimum. Figure~\ref{fig:coverage_vs_time} shows the resulting near-linear coverage progression.

\begin{figure}[ht]
  \centering
  \includegraphics[width=0.8\linewidth]{coverage_vs_time}
  \caption{Area coverage progression over time for the boustrophedon search pattern at \SI{35}{\metre} altitude. The near-linear increase confirms systematic, gap-free coverage.}
  \label{fig:coverage_vs_time}
\end{figure}

A PLB-triggered focus area redirect generates a tighter search pattern around the beacon signal, with reduced speed (\SI{5}{\metre\per\second}) and fresh waypoints from the drone's current position.
```

## 8. Simulation -- PASS

- Section 2.8 (lines 204-213) describes four simulation levels with progressive fidelity.
- Lists specific bugs caught in simulation (MAVLink race, lat scaling, auto-disarm, GPS lag).
- `mission_timeline.pdf` figure exists and is referenced (Figure~\ref{fig:mission_timeline}).
- **Suggestion:** Could mention that the same code runs at all levels (only config changes), which is a strong engineering claim.

## 9. Figure Audit -- all exist

| Figure ref | File needed | Exists? | Caption quality |
|---|---|---|---|
| fig:mission_overview | mission_overview.pdf | YES | Good, detailed |
| fig:architecture | architecture.pdf | YES | Good |
| fig:pi_system | pi_system.pdf | YES | Good |
| fig:geofence_diagram | geofence_diagram.pdf | YES | Good, describes 4 panels |
| fig:cv_pipeline | cv_pipeline.pdf | YES | Good, includes timing |
| fig:state_machine | state_machine.pdf | YES | Good |
| fig:gps_bullseye | gps_bullseye.pdf | YES | Good |
| fig:gps_error_direction | gps_error_direction.pdf | YES | Good |
| fig:gps_convergence | gps_convergence.pdf | YES | Good |
| fig:estimator_comparison | estimator_comparison.pdf | YES | Good |
| fig:mission_timeline | mission_timeline.pdf | YES | Good |

- **All 11 figures exist.** No broken references.
- **Missing figure:** No ground station UI screenshot/diagram (Section 2.7).
- **Missing figure:** `coverage_vs_time.pdf` exists in `figs/` but is NOT referenced from system_description.tex (only from the orphaned 05_path_planning.tex). Pull it into the expanded search pattern subsection.
- All captions are descriptive and self-contained. Good practice.

## 10. Orphaned `05_path_planning.tex` -- CRITICAL

Status: 182 lines of strong technical content. **NOT included in main.tex.** Not referenced from anywhere in the compiled PDF.

Content worth salvaging (ranked by value):

| Content | Lines | Value | Recommendation |
|---|---|---|---|
| Coverage guarantee equations (Eq 1-2) | 63-82 | HIGH | Pull into body (Section 2.4) |
| 216-config parametric sweep results | 85-111 | HIGH | Summarise in 2-3 sentences in body |
| Algorithm comparison table (5 methods) | 135-153 | MEDIUM | Pull into body or appendix |
| Coverage vs time figure reference | 53-58 | HIGH | Pull into body -- figure exists |
| Energy analysis model | 94-111 | MEDIUM | Appendix material |
| Bezier smoothing equation | 114-122 | LOW | Already mentioned in body (without equation) |
| Focus area / PLB redirect | 125-128 | LOW | Already in body (1 sentence) |
| Spiral pattern alternative | 130-133 | LOW | Already mentioned in body |
| Flight parameters table | 158-181 | MEDIUM | Useful appendix or body table |
| Search area definition (3 input methods) | 19-29 | LOW | Nice-to-have |

**Minimum action:** Pull coverage guarantee equations, coverage_vs_time figure, and 216-config sweep summary into body Section 2.4. This adds ~0.5 pages and dramatically strengthens the search pattern subsection.

---

## Summary of Issues

| # | Issue | Severity | Action |
|---|---|---|---|
| 1 | DESCENDING state missing from engagement sequence | HIGH | Fix line 141 |
| 2 | Ground station subsection is 3 sentences / no figure | HIGH | Expand to ~15 lines + add figure |
| 3 | 05_path_planning.tex orphaned (best technical content invisible) | CRITICAL | Merge key content into Section 2.4 |
| 4 | coverage_vs_time.pdf exists but unreferenced from body | MEDIUM | Reference in expanded Section 2.4 |
| 5 | 5 states not named in body text (DESCENDING, HOVER, RETURN_TO_SEARCH, RETURN_FROM_MANUAL, MANUAL) | MEDIUM | Add DESCENDING + MANUAL minimum |
| 6 | BOM missing Wi-Fi/telemetry link hardware | LOW | Add note about Pi built-in Wi-Fi |
| 7 | Confidence threshold ambiguity (0.2 filter vs 0.4 operational) | LOW | Clarify in one parenthetical |
| 8 | No ground_station figure exists in figs/ | MEDIUM | Generate screenshot or diagram |

## Estimated Page Impact

- Current section: ~5.5 pages (estimated from 214 lines + 11 figures)
- Expanded ground station (+12 lines + 1 figure): +0.4 pages
- Expanded search pattern (+25 lines + 1 figure): +0.5 pages
- State machine fix: no page change (same line count)
- **Total after fixes: ~6.4 pages** -- check against 15-page body limit with other sections.
