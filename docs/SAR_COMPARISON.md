# SAR Drone — Comparison with Industry & Academic Practice

> For report writing: how our approach compares, what to cite, what to highlight.

## Our Strengths (highlight in report)

1. **Progressive testing (bench→passive→active→autonomous)** — explicitly recommended in aerospace V&V but rarely done in academic drone projects. Our numbered test scripts (0a-4) are a genuine contribution.
2. **Operator-in-the-loop verification** — industry standard for real SAR. Frame as deliberate design, not limitation. Reference CAA/FAA BVLOS regulations.
3. **7.5m offset landing** — addresses propwash/crash risk to casualty. Rarely mentioned in academic papers but critical for real SAR.
4. **GPS estimation with inverse variance weighting + spatial clustering** — more sophisticated than most academic SAR projects (which report single GPS coordinate).
5. **Simulation-first development** — full mission validated in SITL before hardware. Standard in aerospace, rare in academic drone projects.
6. **Edge AI deployment pipeline** — train Colab → export TFLite → deploy Pi 5 at ~4 FPS. Practical and documented.
7. **Browser-based headless ground station** — works over SSH, no monitor needed. Aligned with real field operations.

## Known Gaps (document as limitations/future work)

| Gap | Notes |
|-----|-------|
| Thermal camera | Most real SAR use thermal + RGB dual sensors (hardware cost) |
| Geofence enforcement | We have SSSI_GPS data but no runtime enforcement in Python |
| Multi-drone coordination | Out of scope for MSc, mention as future work |
| Battery-aware path planning | We rely on ArduPilot failsafe, don't adapt search pattern |
| Confidence calibration | Threshold 0.4 is a guess — need altitude_sweep data |
| Formal telemetry recording | CSV logging exists but no rosbag-equivalent structured data |

## Key References to Cite

### Search Patterns & Coverage Planning
- Survey on Coverage Path Planning with UAVs — MDPI Drones 2019 — https://www.mdpi.com/2504-446X/3/1/4
- Coverage Path Planning for UAVs in SAR — Wiley 2025 — https://onlinelibrary.wiley.com/doi/10.1155/int/4700518
- Deep RL for Time-Critical Wilderness SAR — PMC 2025 — https://pmc.ncbi.nlm.nih.gov/articles/PMC11831046/

### Target Detection & CV
- Camera-Based Target Detection UAV for SAR — MDPI Sensors 2016 — https://www.mdpi.com/1424-8220/16/11/1778
- Real-Time SAR with YOLO — MDPI Drones 2025 — https://www.mdpi.com/2504-446X/9/8/514
- Aerial Person Detection Survey — J. Remote Sensing 2025 — https://spj.science.org/doi/10.34133/remotesensing.0474
- YOLOv8 on Embedded Platforms — MDPI J. Imaging 2025 — https://www.mdpi.com/2313-433X/11/12/436

### Frameworks & Architecture
- AUSPEX Open-Source SAR Framework — Frontiers 2025 — https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2025.1583479/full
- SearchWing SAR Mission Tools — ArduPilot Discourse — https://discuss.ardupilot.org/t/searchwing-sar-missiontools/115139
- Autonomous SAR Drone Design to Implementation — arXiv 2022 — https://arxiv.org/pdf/2211.15866

### Edge Deployment
- Benchmarking DL Models on Edge — arXiv 2024 — https://arxiv.org/html/2409.16808v1

## How to Use This in Report

### Framing Our Approach
- Lawnmower = "Parallel Track Search" in SAR terminology (standard baseline)
- State machine = standard detect→verify→land workflow
- ArduPilot + MAVLink + Python = most common academic SAR architecture
- YOLOv8n TFLite = current edge AI standard for detection

### Unique Contributions to Highlight
1. Progressive V&V testing methodology with numbered scripts
2. Statistical GPS estimation (inverse variance weighting, not just single-point)
3. Offset landing for casualty safety
4. Zero-command passive testing scripts for calibration
5. Headless browser-based ground station for field operation
