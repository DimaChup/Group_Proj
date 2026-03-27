# D7 Individual Reflective Report -- Scoring Guide

> 50% of unit mark. 5 pages max (excl. cover + appendices). Individual submission.

---

## What Gets 75+ (First Class)

### Teamwork (Rubric criterion)

**Top band:** "Outstanding ability to work and lead a team with creativity and flexibility responsive to group members' interests and the obligations and goals of the team. Able to manage conflict."

**HOW TO HIT THIS:**
- Show specific examples of leadership: took initiative on entire software stack (state machine, CV pipeline, ground station, testing framework), set the 10-phase development roadmap, created the progressive testing methodology (bench -> passive -> waypoint -> full autonomous)
- Flexibility: adapted when team members had different skill levels -- built web-based ground station (pi_flight.py) so non-coders could participate in flight testing through a browser, created FIELD_QUICK_REF.md so anyone could run scripts without understanding the codebase
- Responsiveness to group interests: structured work so hardware/wiring team and software team could progress in parallel, created clear interfaces (vision.py API, config.py auto-detect) so changes in one area didn't break another
- Conflict management: give specific examples -- disagreements on approach, timeline pressure, differing priorities. Show HOW you resolved them (compromise, data-driven decisions, deferring to expertise)

### Self-management (Rubric criterion)

**Top band:** "Works autonomously demonstrating outstanding self-organisational skills and behaviours. Has a professional attitude to completing all tasks."

**HOW TO HIT THIS:**
- Self-organisation: managed multiple concurrent workstreams (CV model training, state machine development, ground station UI, hardware integration, documentation, testing). Show the 10-phase roadmap and how you tracked progress
- Professional attitude: comprehensive documentation (CLAUDE.md as ground truth, 16+ doc files, blueprints for complex files), version control discipline (feature branches, progressive commits, never breaking main), requirements traceability
- Autonomous working: simulation-first development -- built and tested entire system on laptop before touching hardware. Docker Pi environment test. Identified and resolved blockers independently (BGR/RGB camera issue, Python 3.13 TFLite incompatibility, mavproxy serial workaround)
- Completing all tasks: show follow-through from initial design through implementation, testing, field deployment, and documentation. Note any setbacks and how you recovered (weather cancelling flight day, pivoting to bench testing)

### Insight (Rubric criterion)

**Top band:** "Shows confidence in working autonomously and setting own goals. Can assess own strengths and weaknesses. Able to identify and implement an effective programme of self-development. Can provide effective feedback to others."

**HOW TO HIT THIS:**
- **Strengths (honest):** rapid prototyping, simulation-first methodology, modular architecture design, systematic testing approach, strong documentation habits
- **Weaknesses (honest):** tendency to build solo rather than delegate (could have involved team earlier in software), over-engineering (2500-line simulator when simpler would suffice), needed to learn when "good enough" beats perfect, initial underestimation of hardware integration challenges
- **Self-development programme:** learned MAVLink protocol from scratch, edge AI deployment (TFLite, NCNN, model quantisation), safety-critical software design (geofencing, kill switches, progressive testing), web-based ground control station development, lens calibration and FOV estimation
- **Feedback to others:** how you helped team members learn ArduPilot/Mission Planner, created documentation that enabled others to run tests, code review practices, structured the GitHub workflow for the team

### AHEP4 Standards (must explicitly address all four)

**M5 -- Design solutions with originality + STEEPLE:**
- Originality: simulation-first development, dual-backend CV (Ultralytics on laptop / TFLite on Pi with identical API), auto-detecting config, headless ground station, progressive testing methodology
- STEEPLE: safety (geofencing R01/R02, kill switch R09, progressive testing), environmental (SSSI no-fly zone, battery lifecycle, noise impact on wildlife), legal (CAA regulations, operator licensing), ethical (SAR context -- false negatives have life-or-death consequences, privacy of bystanders)

**M7 -- Environmental and societal impact (full lifecycle):**
- Positive: SAR drones reduce search time, cover terrain humans can't, operate in poor visibility
- Negative: battery production/disposal, electronic waste, noise disturbance to wildlife, energy consumption of AI training (300+ synthetic images, GPU hours on Colab)
- Mitigation: efficient YOLOv8n model (3.2MB), edge inference (no cloud dependency), geofencing to protect SSSI, mission abort capabilities
- Lifecycle: manufacturing -> deployment -> maintenance -> disposal of drone + Pi + batteries

**M16 -- Evaluate own AND team effectiveness:**
- Own: what went well (simulation-first saved weeks of debugging, modular design enabled rapid iteration), what didn't (solo development bottleneck, could have pair-programmed more)
- Team: honest assessment of team dynamics, workload distribution, communication effectiveness, how the team adapted to setbacks. Use plus/delta format

**M17 -- Communication methods + evaluate effectiveness:**
- Methods used: GitHub (code + issues), documentation suite (16+ docs), web ground station (real-time browser dashboard), presentations (PDR, FDR), live demos
- Evaluate: which methods worked (web GCS was excellent for non-technical stakeholders, documentation prevented context loss between sessions), which didn't (too much documentation can overwhelm, verbal updates sometimes faster than written)

---

## Page Budget (5 pages max)

| Section | Pages | Content |
|---------|-------|---------|
| Intro + role description | 0.5 | Your role, team context, project summary |
| Design and originality (M5) | 1.0 | Key design decisions, originality, STEEPLE analysis |
| Impact and ethics (M7) | 0.5 | Environmental/societal impact, lifecycle, mitigation |
| Teamwork and leadership (M16) | 1.0 | Leadership examples, flexibility, conflict, team evaluation |
| Communication (M17) | 0.5 | Methods used, what worked, what didn't |
| Self-development and insight | 1.5 | Strengths/weaknesses, learning programme, autonomy, feedback to others |

---

## Common Mistakes to Avoid

1. **Describing the project instead of reflecting.** The marker knows what SAR drones are. Focus on YOUR experience, decisions, growth, and honest evaluation
2. **Being uncritical.** "Everything went great" scores low. Show genuine weaknesses and what you learned from them
3. **Ignoring AHEP4 codes.** Explicitly reference M5, M7, M16, M17 -- the marker is looking for these
4. **Treating teamwork superficially.** "We worked well together" is not enough. Give concrete examples with outcomes
5. **Forgetting lifecycle in M7.** Environmental impact is not just "drones help people" -- discuss manufacturing, energy, disposal
6. **Not evaluating communication methods (M17).** Don't just list them -- assess which were effective and why

---

## Evidence to Reference (from project)

- 10-phase development roadmap (docs/ROADMAP.md)
- Progressive testing methodology (5 flight test stages)
- Simulation-first approach (same code on laptop and Pi)
- Web ground station (pi_flight.py -- browser dashboard for non-technical operators)
- Documentation suite (16+ docs, blueprints, session logs)
- Model retraining pipeline (dataset_v2, Colab, 3 model variants)
- Hardware debugging (BGR/RGB fix, Python 3.13 workarounds, lens calibration)
- Geofencing implementation (R01/R02 compliance)
- Field day bench testing (adapted when weather cancelled flight)
- Benchmark results (206.5ms inference, 4.8 FPS on Pi 5)
