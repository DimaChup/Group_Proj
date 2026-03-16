// D7: Individual Reflective Report — 50% of final grade
// Data structure for the Individual Report writing guide

export const REPORT_META = {
  code: "D7",
  title: "Individual Reflective Report",
  weight: "50% of final grade",
  format: "Individual PDF",
  pageLimit: "5 pages (excl. cover and appendices)",
  due: "Thursday Week 23",
  submission: "Blackboard (individual)",
  standards: "AHEP4: M5, M7, M16, M17",
  aiPolicy: "Reporting: Category 2 (Minimal).",
};

export type SectionStatus = "done" | "draft" | "outline" | "todo";

export const STATUS_COLORS: Record<SectionStatus, { bg: string; text: string; label: string }> = {
  done:    { bg: "bg-emerald-900/40", text: "text-emerald-400", label: "Done" },
  draft:   { bg: "bg-amber-900/40",   text: "text-amber-400",   label: "Draft" },
  outline: { bg: "bg-blue-900/40",    text: "text-blue-400",    label: "Outline" },
  todo:    { bg: "bg-zinc-800/40",    text: "text-zinc-500",    label: "To Do" },
};

export interface RubricBand {
  range: string;
  descriptor: string;
}

export interface Criterion {
  name: string;
  ahep: string;
  bands: RubricBand[];
  topMarkTips: string[];
  reflectionPrompts: string[];
}

export const RUBRIC: Criterion[] = [
  {
    name: "Teamwork",
    ahep: "M16 — Function as individual and team member/leader",
    bands: [
      { range: "0-35", descriptor: "Little/no demonstration of ability to work in team" },
      { range: "42-48", descriptor: "Shows limited ability to work within team" },
      { range: "52-58", descriptor: "Shows ability to work with others; contribute productively" },
      { range: "62-68", descriptor: "Works effectively within team, recognising contributions of others; manages conflict" },
      { range: "72-78", descriptor: "Consistently demonstrates effective teamworking and leadership skills; ensures teams meet goals; manages conflict" },
      { range: "83-100", descriptor: "Outstanding ability to work and lead team with creativity/flexibility responsive to members' interests and team goals" },
    ],
    topMarkTips: [
      "Show LEADERSHIP — you drove the technical direction (simulation-first, progressive testing)",
      "Show CONFLICT MANAGEMENT — how you handled disagreements or blockers constructively",
      "Recognise OTHERS' contributions genuinely — what did each team member bring that you couldn't?",
      "Demonstrate FLEXIBILITY — how you adapted when a team member was stuck or priorities changed",
    ],
    reflectionPrompts: [
      "Describe a specific situation where you led a technical decision. What was at stake?",
      "How did you divide work? Was it effective? What would you change?",
      "Was there conflict? How did you handle it? What was the outcome?",
      "How did you support team members who were struggling?",
      "What was your biggest contribution that others couldn't have done?",
    ],
  },
  {
    name: "Self-Management",
    ahep: "M17 — Communicate complex engineering matters effectively",
    bands: [
      { range: "0-35", descriptor: "Very limited self-organisational skills; inability to meet deadlines" },
      { range: "42-48", descriptor: "Limited self-organisational skills; ability to meet deadlines" },
      { range: "52-58", descriptor: "Some self-organisational skills; able to complete most tasks" },
      { range: "62-68", descriptor: "Good self-organisational skills; professional attitude" },
      { range: "72-78", descriptor: "Works autonomously demonstrating very good self-organisational skills; professional attitude" },
      { range: "83-100", descriptor: "Works autonomously demonstrating outstanding self-organisational skills; professional attitude" },
    ],
    topMarkTips: [
      "Show AUTONOMY — you set up CI/testing/documentation without being asked",
      "Show PROFESSIONALISM — meeting deadlines, managing scope, communicating blockers early",
      "Demonstrate systematic approach: brain-dump → plan → implement → test → document",
      "Show time management: parallel streams, not waiting for others to unblock you",
    ],
    reflectionPrompts: [
      "How did you organise your work across the project timeline?",
      "What tools/systems did you use to stay on track? (GitHub, dashboard, CLAUDE.md, etc.)",
      "When were you most productive and why? When were you least productive?",
      "How did you handle the pressure of multiple deadlines (flight day prep + code + reports)?",
      "What would you do differently in terms of time management?",
    ],
  },
  {
    name: "Insight",
    ahep: "M5/M7 — Design solutions, evaluate environmental/societal impact",
    bands: [
      { range: "0-35", descriptor: "Very limited awareness of own strengths/weaknesses" },
      { range: "42-48", descriptor: "Limited awareness of own strengths/weaknesses" },
      { range: "52-58", descriptor: "Some ability to identify strengths/weaknesses; some evidence of self-development" },
      { range: "62-68", descriptor: "Confident self-reflection; proactive approach to self-development" },
      { range: "72-78", descriptor: "Demonstrates ability to assess strengths/weaknesses; identifies and implements effective self-development programme" },
      { range: "83-100", descriptor: "Confidence in working autonomously and setting own goals; effective self-development; can provide effective feedback to others" },
    ],
    topMarkTips: [
      "Be HONEST about weaknesses — generic 'I could improve communication' scores low",
      "Show SPECIFIC self-development — what skill did you identify as weak, what did you DO about it?",
      "Demonstrate GROWTH — compare start-of-project you vs end-of-project you with concrete examples",
      "For 80%+: show you can MENTOR others — did you teach a team member something?",
      "Connect to future career: how does this project feed into your goals for Ukraine/robotics?",
    ],
    reflectionPrompts: [
      "What was your biggest technical weakness at the start? How did you address it?",
      "What surprised you about yourself during this project?",
      "What skill improved the most? Provide a before/after example.",
      "If you mentored someone on this project, what would you teach them first?",
      "How does this project connect to your career goals?",
    ],
  },
];

export interface ReportSection {
  id: string;
  title: string;
  suggestedPages: string;
  status: SectionStatus;
  guidance: string;
  outline: string[];
  evidence: string[];
}

export const REPORT_SECTIONS: ReportSection[] = [
  {
    id: "context",
    title: "Context & Role",
    suggestedPages: "0.5 pages",
    status: "outline",
    guidance: "Brief context: what was the project, what was your specific role and responsibilities?",
    outline: [
      "Project: autonomous SAR drone for casualty detection (AENGM0074, team of 5)",
      "My role: CV/AI lead + overall system integrator",
      "Responsibilities: vision system, AI training, simulation, GPS estimation, system architecture",
      "Why this role: background in [your context], passion for robotics + AI for real-world impact",
    ],
    evidence: [],
  },
  {
    id: "teamwork",
    title: "Teamwork & Leadership (M16)",
    suggestedPages: "1.5 pages",
    status: "todo",
    guidance: "Reflect on your role in the team. Show leadership, conflict management, supporting others. Use specific incidents.",
    outline: [
      "Leadership examples:",
      "  - Drove simulation-first methodology: convinced team to test in sim before hardware",
      "  - Created progressive testing framework: bench → passive → active → autonomous",
      "  - Built the dashboard to keep everyone aligned on progress and priorities",
      "Team dynamics:",
      "  - How work was divided (HW, CV, FD, GCS, PM)",
      "  - Communication: GitHub, WhatsApp, in-person sessions",
      "  - A specific challenge/conflict and how it was resolved",
      "Supporting others:",
      "  - Taught team members about the codebase / testing approach",
      "  - Created comprehensive documentation (CLAUDE.md, FLIGHT_DAY_CHECKLIST, etc.)",
    ],
    evidence: [
      "Dashboard with WBS, team roles, progress tracking",
      "90 WBS tasks showing clear division of work",
      "CLAUDE.md session logs showing continuous documentation",
      "docs/ folder: 15+ documentation files for knowledge transfer",
    ],
  },
  {
    id: "selfmanagement",
    title: "Self-Management & Autonomy (M17)",
    suggestedPages: "1 page",
    status: "todo",
    guidance: "Show how you organised yourself, managed deadlines, worked autonomously. Professional attitude.",
    outline: [
      "Tools and systems:",
      "  - CLAUDE.md as living document: project state always current for any session",
      "  - brain-dump.md: captured every idea, nothing lost",
      "  - NICE_TO_HAVE.md: prioritised backlog with impact/effort scoring",
      "  - Git strategy: feature branches, never break main",
      "Autonomous work:",
      "  - Set up entire Python environment, CI workflow, testing infrastructure",
      "  - Self-directed model retraining pipeline (label → train → export → validate)",
      "  - Built video analysis tools to validate detection without needing flight time",
      "Deadline management:",
      "  - Flight day prep completed systematically (FLIGHT_DAY_CHECKLIST.md)",
      "  - Parallel workstreams: hardware testing didn't block software development",
    ],
    evidence: [
      "Git history: 50+ commits showing systematic progress",
      "CLAUDE.md: 10+ session logs with clear progression",
      "FLIGHT_DAY_CHECKLIST.md: printable, follow-top-to-bottom",
    ],
  },
  {
    id: "insight",
    title: "Insight & Self-Development (M5/M7)",
    suggestedPages: "1.5 pages",
    status: "todo",
    guidance: "Honest self-reflection. Strengths, weaknesses, what you learned, how you grew. Connect to future development.",
    outline: [
      "Strengths discovered:",
      "  - Systems thinking: connecting camera → AI → GPS → flight control into coherent whole",
      "  - Rapid prototyping: simulation → real hardware pipeline",
      "  - Documentation discipline: every session documented, nothing lost between sessions",
      "Weaknesses addressed:",
      "  - [Be specific and honest — e.g., initially over-engineered solutions, learned to simplify]",
      "  - [e.g., Initially didn't test with real data — learned that synthetic-only training has limits]",
      "  - [e.g., Underestimated calibration importance — FOV was wrong until properly measured]",
      "Growth areas:",
      "  - TFLite/edge AI deployment — new skill gained through this project",
      "  - Hardware-software integration — moved from pure software to physical systems",
      "  - Working under uncertainty — real drones don't behave like simulations",
      "Future development:",
      "  - How this connects to career goals (robotics for Ukraine, SAR applications)",
      "  - Skills to develop further: embedded systems, real-time control, outdoor testing",
      "Environmental/societal impact (M7):",
      "  - SAR drones save lives — faster search coverage than ground teams",
      "  - Sub-250g platform: minimal environmental/regulatory impact",
      "  - Privacy considerations: camera pointing down, not at people's homes",
      "  - Battery lifecycle: proper disposal, minimal flights for testing",
    ],
    evidence: [
      "Before/after: original synthetic-only model vs retrained model with real data",
      "FOV calibration journey: wrong FOV → discovered via inconsistent measurements → calibrated properly",
      "SRT sync discovery: debugging revealed frame mismatch → documented for future users",
    ],
  },
  {
    id: "conclusion",
    title: "Conclusion",
    suggestedPages: "0.5 pages",
    status: "todo",
    guidance: "Brief summary: what you're most proud of, what you'd do differently, what you'll take forward.",
    outline: [
      "Most proud of: [the complete pipeline from simulation to real detection]",
      "Would change: [specific thing, e.g., start real-data training earlier]",
      "Taking forward: [skills and mindset for career]",
    ],
    evidence: [],
  },
];

export const PAGE_BUDGET = {
  total: 5,
  sections: [
    { id: "context", pages: 0.5, label: "Context & Role" },
    { id: "teamwork", pages: 1.5, label: "Teamwork & Leadership" },
    { id: "selfmanagement", pages: 1.0, label: "Self-Management" },
    { id: "insight", pages: 1.5, label: "Insight & Self-Development" },
    { id: "conclusion", pages: 0.5, label: "Conclusion" },
  ],
};

export const TOP_MARK_STRATEGIES = [
  {
    criterion: "Teamwork (M16)",
    target: "72-78+",
    strategies: [
      "Show consistent leadership AND followership — you adapted your role based on team needs",
      "Include a specific conflict resolution example with clear outcome",
      "Genuinely acknowledge what others brought that you couldn't",
      "For 83+: show creativity/flexibility in responding to team members' interests",
    ],
  },
  {
    criterion: "Self-Management (M17)",
    target: "72-78+",
    strategies: [
      "Demonstrate AUTONOMY — you set your own goals and met them without being chased",
      "Show professional attitude: deadlines met, quality maintained, scope managed",
      "Reference specific tools/systems you built to stay organised",
      "For 83+: show outstanding organisational skills with evidence",
    ],
  },
  {
    criterion: "Insight (M5/M7)",
    target: "72-78+",
    strategies: [
      "Be vulnerably honest about a real weakness — then show what you DID about it",
      "Show a clear before/after growth arc with concrete example",
      "Include a self-development plan: what will you learn next and how?",
      "For 83+: show you can mentor others and provide effective feedback",
      "Environmental/societal awareness: SAR saves lives, sub-250g minimises impact",
    ],
  },
];
