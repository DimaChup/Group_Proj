// D6: Company Report — 50% of final grade
// Data structure for the Group Report writing guide

export const REPORT_META = {
  code: "D6",
  title: "Company Report",
  weight: "50% of final grade",
  format: "Single PDF + GitHub link (MIT license)",
  pageLimit: "15 pages (excl. cover, exec summary, intro, references, appendices)",
  due: "Thursday Week 23",
  submission: "Blackboard (one per group)",
  aiPolicy: "Software dev: Category 3 (Selective). Reporting: Category 2 (Minimal).",
};

export type SectionStatus = "done" | "draft" | "outline" | "todo" | "blocked";

export const STATUS_COLORS: Record<SectionStatus, { bg: string; text: string; label: string }> = {
  done:    { bg: "bg-emerald-900/40", text: "text-emerald-400", label: "Done" },
  draft:   { bg: "bg-amber-900/40",   text: "text-amber-400",   label: "Draft" },
  outline: { bg: "bg-blue-900/40",    text: "text-blue-400",    label: "Outline" },
  todo:    { bg: "bg-zinc-800/40",    text: "text-zinc-500",    label: "To Do" },
  blocked: { bg: "bg-red-900/40",     text: "text-red-400",     label: "Blocked" },
};

export interface RubricBand {
  range: string;
  descriptor: string;
}

export interface Criterion {
  name: string;
  weight: string;
  bands: RubricBand[];
  topMarkTips: string[];
}

export const RUBRIC: Criterion[] = [
  {
    name: "Specialist Skills & Problem-Solving",
    weight: "40%",
    bands: [
      { range: "0-35", descriptor: "Does not show ability to identify key aspects of complex problems" },
      { range: "42-48", descriptor: "Little evidence of awareness of key aspects; weak deployment of tools" },
      { range: "52-58", descriptor: "Limited ability to identify key aspects; some understanding shown" },
      { range: "62-68", descriptor: "Key aspects identified; appropriate technologies selected and implemented effectively" },
      { range: "72-78", descriptor: "Key aspects identified and implemented effectively, showing initiative and autonomy" },
      { range: "83-100", descriptor: "Confident and comprehensive identification; highly effective implementation showing initiative, autonomy, and creativity" },
    ],
    topMarkTips: [
      "Show INITIATIVE — go beyond minimum requirements (e.g., FOV calibration, model retraining, tiling comparison)",
      "Show AUTONOMY — independent problem-solving (e.g., debugging SRT sync, discovering BGR colour issue)",
      "Show CREATIVITY — novel approaches (e.g., GPS estimation from CV, inverse variance weighting, spatial clustering)",
      "Demonstrate comprehensive understanding of the entire system, not just your subsystem",
    ],
  },
  {
    name: "Decision Making",
    weight: "40%",
    bands: [
      { range: "0-35", descriptor: "No evidence of ability to make decisions in complex/unpredictable circumstances" },
      { range: "42-48", descriptor: "Little evidence of decision-making in complex circumstances" },
      { range: "52-58", descriptor: "Limited ability to make decisions in complex/unpredictable circumstances" },
      { range: "62-68", descriptor: "Confident in adapting; making evidence-based decisions" },
      { range: "72-78", descriptor: "Confident in adapting; making effective, evidence-based decisions" },
      { range: "83-100", descriptor: "Shows confidence and creativity in adapting to changing/unfamiliar/challenging circumstances" },
    ],
    topMarkTips: [
      "Every decision must be EVIDENCE-BASED — show data, benchmarks, comparisons",
      "Document decisions that CHANGED — show you adapted when things didn't work (e.g., TFLite vs Ultralytics, FOV discovery)",
      "Show trade-off analysis — why this approach over alternatives? (e.g., YOLOv8n vs YOLOv8s, tiling vs full-frame)",
      "Include failed experiments — they show real engineering judgment (e.g., 6fps SRT sync failure)",
      "STEEPLE considerations — environmental (battery disposal), ethical (SAR privacy), safety (kill switch, RTL)",
    ],
  },
  {
    name: "Communication",
    weight: "20%",
    bands: [
      { range: "0-35", descriptor: "Very limited awareness of effective communication" },
      { range: "42-48", descriptor: "Limited awareness of effective communication" },
      { range: "52-58", descriptor: "Some awareness of effective communication" },
      { range: "62-68", descriptor: "Effective, making use of appropriate techniques/resources" },
      { range: "72-78", descriptor: "Effective, making use of appropriate techniques/resources" },
      { range: "83-100", descriptor: "Effective, engaging, and professional, making use of innovative techniques and resources" },
    ],
    topMarkTips: [
      "Professional formatting — clear headings, consistent style, no orphan paragraphs",
      "Figures with captions and cross-references — architecture diagrams, flowcharts, benchmark plots",
      "Use the dashboard/website as 'innovative technique' — reference it as a project management tool",
      "Tables for comparisons — model benchmarks, requirement verification matrix",
      "Concise writing — 15 pages is tight, every sentence must earn its place",
    ],
  },
];

export interface ReportSection {
  id: string;
  title: string;
  required: boolean;
  countsTowardLimit: boolean;
  suggestedPages: string;
  status: SectionStatus;
  guidance: string;
  outline: string[];
  evidence: string[];  // what we already have from our work
}

export const REPORT_SECTIONS: ReportSection[] = [
  {
    id: "exec",
    title: "Executive Summary",
    required: true,
    countsTowardLimit: false,
    suggestedPages: "1 page",
    status: "todo",
    guidance: "Single page, self-contained. Reader should understand the project without reading anything else.",
    outline: [
      "Project objective: autonomous SAR drone with AI-based casualty detection",
      "System overview: DJI Mini 3 Pro + Raspberry Pi 5 + Cube Orange + YOLOv8n",
      "Key achievement: end-to-end simulation working, real hardware tested, model retrained on real data",
      "Quantitative results: mAP50=0.995, detection at 15-50m altitude, GPS estimation CEP50=2.3m",
      "Flight day outcome summary (TBD)",
    ],
    evidence: [
      "Benchmark results (Pi 5: 206ms inference, 4.8 FPS)",
      "Model training metrics (mAP50=0.995)",
      "GPS estimation accuracy from video analysis (CEP50=2.3m)",
    ],
  },
  {
    id: "intro",
    title: "Introduction",
    required: true,
    countsTowardLimit: false,
    suggestedPages: "1 page",
    status: "todo",
    guidance: "Context, background, company description (member bios, roles), brief description of member contributions.",
    outline: [
      "SAR context: search and rescue using UAVs, real-world motivation",
      "Project brief: AENGM0074, University of Bristol, team of 5",
      "Team member bios and roles (HW, CV/Optics, Flight Dynamics, GCS, PM)",
      "Brief contribution summary per member",
    ],
    evidence: [
      "Team roles defined in dashboard Team tab",
      "WBS shows 90 tasks across 7 subsystems",
    ],
  },
  {
    id: "design",
    title: "Design Rationale",
    required: true,
    countsTowardLimit: true,
    suggestedPages: "3-4 pages",
    status: "outline",
    guidance: "Justification of design decisions including STEEPLE considerations. This is where 'Decision Making' (40%) is assessed.",
    outline: [
      "Platform selection: DJI Mini 3 Pro — why? (sub-250g, GPS, stable, camera)",
      "Companion computer: Raspberry Pi 5 — why? (GPIO, Python, community, power)",
      "AI model: YOLOv8n — why? (speed vs accuracy trade-off, TFLite export, Pi-compatible)",
      "Detection approach: single-frame vs tiling — benchmarks showing tiling finds small targets",
      "GPS estimation: pixel-to-GPS conversion — FOV calibration, inverse variance weighting",
      "Communication: MAVLink via mavproxy — why bridge? (Python 3.13 pyserial bug)",
      "Search pattern: lawnmower — coverage vs efficiency analysis",
      "Safety: RC kill switch, RTL on link loss, operator confirmation before landing",
      "STEEPLE: environmental (battery, noise), ethical (privacy, SAR data), legal (UK drone regs <250g), safety (kill switch)",
    ],
    evidence: [
      "Pipeline tab in dashboard: 10 mission stages with all design alternatives documented",
      "docs/DESIGN_DECISIONS.md: DD-01 format rationale for each major decision",
      "Benchmark data: inference speed, detection rate vs altitude",
      "FOV calibration results: 54.4 deg, validated across 15-50m",
      "Model comparison: original vs retrained (real data improved detection at altitude)",
    ],
  },
  {
    id: "system",
    title: "System Description",
    required: true,
    countsTowardLimit: true,
    suggestedPages: "3-4 pages",
    status: "outline",
    guidance: "Architecture of final system with flow charts, schematics, images. This is where 'Specialist Skills' (40%) is shown.",
    outline: [
      "System architecture diagram: Camera → Pi 5 → vision.py → planning.py → MAVLink → Cube → Motors",
      "State machine: INIT → CONNECTING → ARMING → TAKEOFF → SEARCH → CENTERING → DESCENDING → VERIFY → APPROACH → LANDING → DONE",
      "Software architecture: config.py (settings), vision.py (AI), planning.py (search), main.py (state machine), utils.py (geo math)",
      "Hardware connections: Pi → Cube (UART 921600), Camera (CSI), Buzzer (MAVLink)",
      "AI pipeline: camera frame → lens undistortion → resize 640x640 → YOLOv8n TFLite → NMS → (found, x, y, conf)",
      "GPS estimation pipeline: pixel detection → FOV geometry → drone GPS + altitude + yaw → target GPS estimate",
      "Ground station: pi_flight.py web dashboard, MJPEG stream, command buttons, 2D GPS grid",
      "Simulation: simple_simulator.py (keyboard flight + CV), simulation.py (map + virtual camera)",
    ],
    evidence: [
      "ARCHITECTURE.md: system diagrams, hardware checklist",
      "vision.py: dual-backend (Ultralytics laptop, TFLite Pi)",
      "simple_simulator.py: full interactive simulation with GPS estimation",
      "pi_flight.py: web-based ground station with MJPEG stream",
    ],
  },
  {
    id: "verification",
    title: "Requirements Verification",
    required: true,
    countsTowardLimit: true,
    suggestedPages: "3-4 pages",
    status: "outline",
    guidance: "Process and evidence of satisfying requirements. Descriptions, images, technical details.",
    outline: [
      "Requirement traceability matrix: each requirement → how verified → evidence",
      "Detection verification: video analysis showing detection at 15-50m altitude (screenshots, confidence plots)",
      "GPS accuracy: CEP50=2.3m from DJI video analysis, scatter plots",
      "Inference speed: Pi 5 benchmark 206ms (4.8 FPS), laptop benchmark data",
      "Communication: MAVLink heartbeat verified, command latency measured",
      "Safety: RC override tested, RTL on link loss verified in simulation",
      "Search coverage: lawnmower pattern generates full coverage of search polygon",
      "Landing accuracy: simulation shows 7.5m offset landing (within safety margin)",
      "Model performance: mAP50=0.995 on validation set, confusion matrix",
    ],
    evidence: [
      "video_test.py: GPS scatter plots, detection frame captures, CEP50 measurements",
      "benchmark results: Pi inference timing, model comparison",
      "Simulation screenshots: state machine transitions, landing sequence",
      "FOV calibration: dummy measures 1.8m consistently across altitudes",
      "Detection CSV logs from video analysis runs",
      "confusion_matrix.png from training (in cv_models/)",
    ],
  },
  {
    id: "evaluation",
    title: "Evaluation",
    required: true,
    countsTowardLimit: true,
    suggestedPages: "2-3 pages",
    status: "todo",
    guidance: "Plus/delta review of TECHNICAL performance. Focus on what worked, what didn't, what we'd change. NOT team working or self-development (that goes in D7).",
    outline: [
      "PLUS: What worked well technically",
      "  - Simulation-first approach: caught bugs before hardware existed",
      "  - Dual-backend vision.py: same code on laptop and Pi",
      "  - Model retraining with real data: significant detection improvement",
      "  - Progressive testing methodology: bench → passive → active → autonomous",
      "DELTA: What we'd change / didn't work",
      "  - BGR colour issue discovered late (should have tested earlier)",
      "  - 6fps video SRT sync issue wasted calibration time",
      "  - GPS timing lag (100-200ms) limits accuracy at speed",
      "  - Single-class detector: can't distinguish dummy from false positives visually",
      "FUTURE: Next steps if project continued",
      "  - NCNN inference (~15 FPS on Pi)",
      "  - Multi-class training (person vs object)",
      "  - Hailo-8L accelerator (80+ FPS)",
      "  - Real outdoor GPS calibration with ground truth",
    ],
    evidence: [
      "Session logs documenting discovery and resolution of issues",
      "Benchmark comparisons across model versions",
      "GPS timing lag analysis from memory/gps-timing-lag.md",
      "CV speed research from memory/cv-speed-research.md",
    ],
  },
  {
    id: "references",
    title: "References",
    required: true,
    countsTowardLimit: false,
    suggestedPages: "1-2 pages",
    status: "todo",
    guidance: "Cite research, design, and code sources. Justify design decisions with academic/industry references.",
    outline: [
      "YOLOv8 paper and Ultralytics documentation",
      "MAVLink protocol specification",
      "ArduPilot documentation (GUIDED mode, MAV_CMD)",
      "Raspberry Pi 5 specifications",
      "DJI Mini 3 Pro specifications",
      "TFLite / ai-edge-litert documentation",
      "UK CAA drone regulations (sub-250g category)",
      "SAR drone literature: comparison papers (docs/SAR_COMPARISON.md has references)",
      "OpenCV documentation",
      "FSRS spaced repetition (if used in methodology discussion)",
    ],
    evidence: [
      "docs/SAR_COMPARISON.md: industry/academic comparison with citations",
    ],
  },
  {
    id: "appendices",
    title: "Appendices",
    required: false,
    countsTowardLimit: false,
    suggestedPages: "As needed",
    status: "todo",
    guidance: "Further detail only — NOT assessed. Include summaries in main sections. Schematics, trade-off studies, extended benchmarks.",
    outline: [
      "A: Hardware wiring diagram (Pi → Cube connections)",
      "B: Full benchmark results table (all models, all resolutions)",
      "C: Detection log sample (CSV format explanation)",
      "D: Search pattern geometry (lawnmower algorithm visualization)",
      "E: State machine diagram (full transition table)",
      "F: GitHub repository link and structure",
    ],
    evidence: [],
  },
];

export const PAGE_BUDGET = {
  total: 15,
  sections: [
    { id: "design", pages: 4, label: "Design Rationale" },
    { id: "system", pages: 4, label: "System Description" },
    { id: "verification", pages: 4, label: "Requirements Verification" },
    { id: "evaluation", pages: 3, label: "Evaluation" },
  ],
};

export const TOP_MARK_STRATEGIES = [
  {
    criterion: "Specialist Skills (40%)",
    target: "72-78+",
    strategies: [
      "Show the FULL technical pipeline end-to-end: camera → AI → GPS → landing",
      "Demonstrate initiative: we retrained the model on real data (not just synthetic)",
      "Show autonomy: independent debugging of SRT sync, BGR colour, FOV calibration",
      "Quantify everything: mAP50, CEP50, FPS, confidence thresholds, detection altitude range",
      "Include benchmark comparisons: before vs after retraining, tiled vs single-frame",
    ],
  },
  {
    criterion: "Decision Making (40%)",
    target: "72-78+",
    strategies: [
      "Every design choice backed by evidence (benchmarks, comparisons, failure analysis)",
      "Show ADAPTATION: initial plan → what changed → why → outcome",
      "Document the SRT sync discovery as evidence of rigorous testing revealing issues",
      "Include trade-off tables: YOLOv8n vs 8s, 640 vs 1088, TFLite vs NCNN",
      "STEEPLE analysis shows awareness of real-world constraints beyond pure engineering",
    ],
  },
  {
    criterion: "Communication (20%)",
    target: "83-100",
    strategies: [
      "Professional figures: architecture diagram, state machine, benchmark plots, scatter plots",
      "Requirement verification matrix: clean table mapping each requirement to evidence",
      "Reference the dashboard/website as innovative project management tool",
      "Consistent formatting, numbered figures, cross-references",
      "Executive summary that stands alone — reader gets the full picture in 1 page",
    ],
  },
];
