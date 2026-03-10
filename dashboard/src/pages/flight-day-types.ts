/**
 * Flight Day 1 — Type definitions.
 * Shared by flight-day-prep.ts and flight-day-tiers.ts.
 */

// ═══════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════

export interface FlightStep {
  id: string;
  task: string;
  how?: string;
  command?: string;
  verify?: string;
  contingency?: string;
  owner?: string;
  data?: string[];
  notes?: string;
  /** Numbered sub-steps — the detailed "recipe" for beginners */
  detailedSteps?: string[];
  /** What the terminal/screen should show if everything works */
  expectedOutput?: string;
  /** Approximate time for this step */
  duration?: string;
}

export interface FlightPhase {
  id: string;
  title: string;
  subtitle?: string;
  steps: FlightStep[];
}

export interface GoNoGo {
  question: string;
  go: string;
  noGo: string;
  partialGo?: string;
}

export interface FlightTier {
  id: string;
  title: string;
  subtitle: string;
  color: string;
  time: string;
  batteries: string;
  entryRequirements: string[];
  phases: FlightPhase[];
  gate?: GoNoGo;
  contingencies: Record<string, string>;
  dataCollected: string[];
}

export interface PrepTask {
  id: string;
  task: string;
  owner?: string;
  command?: string;
  items?: string[];
  notes?: string;
  critical: boolean;
  status: "done" | "todo";
}

export interface DiagnosticCheck {
  id: string;
  system: string;
  command: string;
  expect: string;
  failSteps: string[];
  severity: "blocking" | "warning" | "info";
}

export interface Measurement {
  id: string;
  category: "calibration" | "performance" | "accuracy" | "detection";
  metric: string;
  how: string;
  unit: string;
  currentValue?: string;
  notes?: string;
}

export interface LogRequirement {
  id: string;
  what: string;
  source: string;
  format: string;
  analysis: string;
}
