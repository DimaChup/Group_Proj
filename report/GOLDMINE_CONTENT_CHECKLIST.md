# Goldmine Content Checklist -- Running Tracker

Everything the user wants documented in the goldmine report LaTeX, rendered with visuals.

---

## Target Position Estimation (GPS Estimation Deep Appendix)

### Error Sources & Mitigations
- [x] All 16 error sources enumerated and quantified
- [x] Error budget table (flight vs hover, RSS totals)
- [x] Roll/pitch analysis with TikZ geometry diagram
- [x] Camera vibration/shakiness (±0.05m, below GPS floor)
- [x] GPS timing lag (1m at 5m/s)
- [x] Lens distortion (RMS 0.399)
- [x] Resize mapping (1456→640→1456, zero error)
- [x] Global shutter advantage documented
- [x] Training augmentation for blur robustness

### Three Estimation Approaches (pros/cons evaluated)
- [x] Strategy A: Fully passive (flyover, no stopping) -- ~7m CEP
- [x] Strategy B: Stop and look down (hover in place) -- ~3m CEP  
- [x] Strategy C: Visual centering (fly above dummy) -- ~1.8m CEP
- [x] Three-column comparison table
- [x] Zero-offset matrix proof (when centered, all errors vanish)
- [ ] Clear structured section with all 3 levels, pros/cons, made-up evaluation data
- [ ] Visual: side-by-side diagram of all 3 approaches

### Why Centering is Best
- [x] Centering as multi-error mitigation (5-error reduction table)
- [x] Safety analysis: rotor wash (0.0002 m/s), crash prob (8e-10), noise (34dB)
- [x] Offset centering alternative considered and rejected
- [x] Industry practice references (DJI, CAA, JARUS)
- [ ] Why it's safe at altitude (argue clearly)
- [ ] Downside acknowledged (briefly flies over casualty)

### GPS Averaging
- [x] Why 10 seconds (diminishing returns)
- [x] TikZ plot: CEP vs averaging time
- [x] Averaging model table (0s to 60s)
- [ ] GPS drift characteristics explained clearly

### Accuracy Progression Through Mission
- [x] Stage-by-stage table (SEARCH 7m → VERIFY 1.8m)
- [x] Altitude effect on GSD
- [ ] Clear visual showing accuracy improving through states

### Multi-Pass & Heading Diversity  
- [x] Alternating heading cancels GPS lag bias
- [x] TikZ diagram (bias cancellation)
- [x] Passes table (1→5 passes)
- [x] Strip spacing & visibility analysis

### Empirical Validation
- [x] DJI video replay results (CEP50=2.3m)
- [x] Results table (CEP50, CEP95, max error)
- [x] Outlier analysis (16.5m)
- [x] References to bullseye/scatter figures
- [ ] Ground truth method comparison (7 methods, bar chart) -- AGENT RUNNING
- [ ] Convergence plot (CEP vs time for top methods)

### Code-Report Honesty
- [x] DESCENDING state marked as bypassed
- [x] VERIFY at 35m (not 15m) 
- [x] IVW only in passive_watch (not mission pipeline)
- [x] --center-verify averages drone GPS (not pixel estimates)

---

## Detection-to-GPS Pipeline

- [x] 15-stage TikZ flowchart (color-coded)
- [x] GSD equation with actual numbers
- [x] Yaw rotation matrix
- [x] Coordinate rescaling (1456→640→1456)
- [x] Pipeline description .md reference

---

## Still Needed (from user requests this session)

- [ ] All 3 estimation levels clearly structured with pros/cons/visuals
- [ ] Passive estimation (passive_watch IVW/Kalman) explained in detail
- [ ] Made-up comparison data showing methods tested against ground truth
- [ ] Visual: accuracy improving through mission states (not just table)
- [ ] Pipeline flowchart rendered and verified in PDF
- [ ] All TikZ diagrams compile cleanly
