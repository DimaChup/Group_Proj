/**
 * ReadmeTab — Comprehensive project overview for the team.
 * First tab in dashboard. Explains everything: what we built, how to use it,
 * testing scripts, calibration, flight day plan, architecture.
 */

import { useState } from "react";
import {
  PROJECT_OVERVIEW,
  ARCHITECTURE,
  HARDWARE_SUMMARY,
  COMPLETED,
  TODO,
  TEST_CATEGORIES,
  CALIBRATIONS,
  FLIGHT_STEPS,
  GPS_ESTIMATION,
  CONNECTIONS,
  KEY_CONFIG,
  MODELS,
  MY_CHECKLIST,
} from "./readme-data";

type SectionId =
  | "my-checklist" | "overview" | "architecture" | "hardware" | "status"
  | "tests" | "calibration" | "flight-plan" | "gps"
  | "connections" | "config" | "models" | "howto";

const STATUS_COLOR: Record<string, { bg: string; text: string }> = {
  done: { bg: "bg-green-500/15", text: "text-green-400" },
  ready: { bg: "bg-blue-500/15", text: "text-blue-400" },
  "needs-testing": { bg: "bg-amber-500/15", text: "text-amber-400" },
  todo: { bg: "bg-zinc-500/15", text: "text-zinc-400" },
};

const RISK_COLOR: Record<string, string> = {
  none: "text-green-500",
  low: "text-blue-400",
  medium: "text-amber-400",
  high: "text-red-400",
};

export default function ReadmeTab() {
  const [expanded, setExpanded] = useState<Set<SectionId>>(
    new Set(["my-checklist", "overview", "status", "tests", "flight-plan"])
  );
  const [checked, setChecked] = useState<Set<string>>(new Set());

  const toggle = (id: SectionId) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const Section = ({
    id,
    title,
    subtitle,
    children,
  }: {
    id: SectionId;
    title: string;
    subtitle?: string;
    children: React.ReactNode;
  }) => (
    <div className="border border-zinc-800/50 rounded-lg overflow-hidden">
      <button
        onClick={() => toggle(id)}
        className="w-full flex items-center gap-3 px-4 py-2.5 bg-zinc-900/50 hover:bg-zinc-800/30 transition-colors cursor-pointer"
      >
        <span className="text-[10px] text-zinc-500 w-4">
          {expanded.has(id) ? "▼" : "▶"}
        </span>
        <span className="text-[12px] font-bold text-zinc-200">{title}</span>
        {subtitle && (
          <span className="text-[9px] text-zinc-500 ml-auto">{subtitle}</span>
        )}
      </button>
      {expanded.has(id) && (
        <div className="px-4 pb-4 pt-2 space-y-3">{children}</div>
      )}
    </div>
  );

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-3 min-w-0">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-lg font-bold text-zinc-100">
          {PROJECT_OVERVIEW.title}
        </h1>
        <p className="text-[10px] text-zinc-500 mt-0.5">
          {PROJECT_OVERVIEW.course} — {PROJECT_OVERVIEW.team} — Share this with
          your team to understand the full system
        </p>
      </div>

      {/* ── My Pre-Flight Checklist ─────────────────────────────── */}
      <div className="border-2 border-amber-500/30 rounded-lg overflow-hidden">
        <button
          onClick={() => toggle("my-checklist")}
          className="w-full flex items-center gap-3 px-4 py-3 bg-amber-500/10 hover:bg-amber-500/15 transition-colors cursor-pointer"
        >
          <span className="text-[10px] text-amber-400 w-4">
            {expanded.has("my-checklist") ? "▼" : "▶"}
          </span>
          <span className="text-[13px] font-bold text-amber-300">
            MY PRE-FLIGHT CHECKLIST (CV Person)
          </span>
          <span className="text-[10px] text-amber-500/70 ml-auto">
            {checked.size}/{MY_CHECKLIST.length} done
          </span>
        </button>
        {expanded.has("my-checklist") && (
          <div className="px-4 pb-4 pt-2 space-y-1">
            <div className="flex gap-6 mb-3">
              <p className="text-[10px] text-zinc-500">
                <span className="inline-block w-2 h-2 rounded-full bg-blue-500 mr-1" />
                At home (laptop)
              </p>
              <p className="text-[10px] text-zinc-500">
                <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-1" />
                At field (Pi)
              </p>
            </div>
            {MY_CHECKLIST.map((item) => {
              const isDone = checked.has(item.id);
              const isField = item.location === "field";
              return (
                <div
                  key={item.id}
                  className={`flex items-start gap-3 p-2.5 rounded border transition-colors cursor-pointer ${
                    isDone
                      ? "bg-green-500/5 border-green-500/20 opacity-60"
                      : "bg-zinc-800/20 border-zinc-800/30 hover:border-zinc-700/50"
                  }`}
                  onClick={() =>
                    setChecked((prev) => {
                      const next = new Set(prev);
                      next.has(item.id) ? next.delete(item.id) : next.add(item.id);
                      return next;
                    })
                  }
                >
                  <div className="mt-0.5 shrink-0">
                    <div
                      className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                        isDone
                          ? "border-green-500 bg-green-500"
                          : "border-zinc-600"
                      }`}
                    >
                      {isDone && (
                        <span className="text-[10px] text-black font-bold">
                          ✓
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span
                        className={`inline-block w-2 h-2 rounded-full shrink-0 ${
                          isField ? "bg-green-500" : "bg-blue-500"
                        }`}
                      />
                      <span
                        className={`text-[11px] font-bold ${
                          isDone ? "text-zinc-500 line-through" : "text-zinc-200"
                        }`}
                      >
                        {item.id}. {item.task}
                      </span>
                      <span className="text-[8px] text-zinc-600 ml-auto shrink-0">
                        ~{item.time}
                      </span>
                    </div>
                    <p className="text-[9px] text-cyan-400/80 font-mono mb-0.5 break-all">
                      {item.command}
                    </p>
                    <p className="text-[9px] text-zinc-500">{item.detail}</p>
                  </div>
                </div>
              );
            })}
            <p className="text-[9px] text-zinc-600 mt-2 pt-2 border-t border-zinc-800/30">
              Order: 1→2→3→4→5→6 at home. Items 7-10 at the field on flight day.
            </p>
          </div>
        )}
      </div>

      {/* ── Overview ──────────────────────────────────────────────── */}
      <Section id="overview" title="What This Project Does" subtitle="The mission">
        <div className="space-y-2">
          {PROJECT_OVERVIEW.summary.map((s, i) => (
            <div key={i} className="flex gap-2 text-[10px] text-zinc-300">
              <span className="text-zinc-500 shrink-0">{i + 1}.</span>
              <span>{s}</span>
            </div>
          ))}
          <div className="mt-3 p-2 bg-zinc-800/30 rounded text-[9px] text-zinc-400 font-mono overflow-x-auto">
            {PROJECT_OVERVIEW.stateFlow}
          </div>
        </div>
      </Section>

      {/* ── Status ────────────────────────────────────────────────── */}
      <Section
        id="status"
        title="What's Done & What's Left"
        subtitle={`${COMPLETED.filter((d) => d.status === "done").length} done, ${TODO.length} remaining`}
      >
        <div className="space-y-1">
          <p className="text-[10px] font-bold text-green-400 mb-2">
            Completed / Ready
          </p>
          {COMPLETED.map((d) => {
            const c = STATUS_COLOR[d.status];
            return (
              <div
                key={d.id}
                className="flex items-start gap-2 text-[10px] py-1"
              >
                <span
                  className={`${c.bg} ${c.text} px-1.5 py-0.5 rounded text-[8px] font-bold shrink-0 uppercase`}
                >
                  {d.status}
                </span>
                <div>
                  <span className="text-zinc-200 font-medium">{d.name}</span>
                  <span className="text-zinc-500 ml-1">— {d.description}</span>
                </div>
              </div>
            );
          })}

          <p className="text-[10px] font-bold text-amber-400 mt-4 mb-2">
            Still To Do
          </p>
          {TODO.map((d) => {
            const c = STATUS_COLOR[d.status];
            return (
              <div
                key={d.id}
                className="flex items-start gap-2 text-[10px] py-1"
              >
                <span
                  className={`${c.bg} ${c.text} px-1.5 py-0.5 rounded text-[8px] font-bold shrink-0 uppercase`}
                >
                  {d.status}
                </span>
                <div>
                  <span className="text-zinc-200 font-medium">{d.name}</span>
                  <span className="text-zinc-500 ml-1">— {d.description}</span>
                </div>
              </div>
            );
          })}
        </div>
      </Section>

      {/* ── Test Scripts ──────────────────────────────────────────── */}
      <Section
        id="tests"
        title="All Test Scripts — What Each Does & When to Use"
        subtitle={`${TEST_CATEGORIES.reduce((n, c) => n + c.scripts.length, 0)} scripts in ${TEST_CATEGORIES.length} categories`}
      >
        <div className="space-y-5">
          {TEST_CATEGORIES.map((cat) => (
            <div key={cat.category}>
              <div className="mb-2">
                <p className="text-[11px] font-bold text-zinc-200">
                  {cat.category}
                </p>
                <p className="text-[9px] text-zinc-500">
                  <span className="text-zinc-400 font-mono">
                    {cat.folder}
                  </span>{" "}
                  — {cat.purpose}
                </p>
              </div>
              <div className="space-y-1.5">
                {cat.scripts.map((s) => (
                  <div
                    key={s.name}
                    className="bg-zinc-800/20 rounded p-2.5 border border-zinc-800/30"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-mono text-cyan-400 font-bold">
                        {s.name}
                      </span>
                      <span
                        className={`text-[8px] font-bold uppercase ${RISK_COLOR[s.risk]}`}
                      >
                        {s.risk === "none"
                          ? "SAFE"
                          : s.risk === "low"
                            ? "PASSIVE"
                            : s.risk === "medium"
                              ? "SENDS CMDS"
                              : "AUTONOMOUS"}
                      </span>
                    </div>
                    <p className="text-[10px] text-zinc-300">{s.purpose}</p>
                    <p className="text-[9px] text-zinc-500 mt-1">
                      <span className="text-zinc-400">When:</span> {s.when}
                    </p>
                    {s.output && (
                      <p className="text-[9px] text-zinc-500">
                        <span className="text-zinc-400">Output:</span>{" "}
                        {s.output}
                      </p>
                    )}
                    {s.flags && s.flags.length > 0 && (
                      <div className="flex gap-1 mt-1 flex-wrap">
                        {s.flags.map((f) => (
                          <span
                            key={f}
                            className="text-[8px] font-mono bg-zinc-700/30 text-zinc-400 px-1.5 py-0.5 rounded"
                          >
                            {f}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* ── Calibration ───────────────────────────────────────────── */}
      <Section
        id="calibration"
        title="Calibration — Getting the Numbers Right"
        subtitle="FOV calibration is the most important step"
      >
        <div className="space-y-2">
          <p className="text-[10px] text-zinc-400">
            Wrong calibration = wrong GPS estimates from pixel positions. FOV
            calibration is the ONE systematic error you can eliminate before
            flying.
          </p>
          {CALIBRATIONS.map((cal) => (
            <div
              key={cal.id}
              className="bg-zinc-800/20 rounded p-2.5 border border-zinc-800/30"
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-bold text-zinc-200">
                  {cal.name}
                </span>
                <span className="text-[8px] bg-zinc-700/30 text-zinc-400 px-1.5 py-0.5 rounded">
                  {cal.location === "both"
                    ? "bench + field"
                    : cal.location}
                </span>
              </div>
              <p className="text-[10px] text-zinc-300">{cal.what}</p>
              <p className="text-[9px] text-zinc-500 mt-1 font-mono">
                python {cal.script}
              </p>
              {cal.configUpdate && (
                <p className="text-[9px] text-amber-400/70 mt-0.5">
                  → {cal.configUpdate}
                </p>
              )}
            </div>
          ))}
        </div>
      </Section>

      {/* ── Flight Day Plan ───────────────────────────────────────── */}
      <Section
        id="flight-plan"
        title="Flight Day Plan — Step by Step"
        subtitle="Follow in order, never skip"
      >
        <div className="space-y-2">
          {FLIGHT_STEPS.map((step) => (
            <div
              key={step.id}
              className="bg-zinc-800/20 rounded p-3 border border-zinc-800/30"
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[12px] font-bold text-zinc-300">
                  Step {step.id}
                </span>
                <span className="text-[10px] font-bold text-zinc-200">
                  {step.name}
                </span>
                <span
                  className={`text-[8px] font-bold ml-auto ${
                    step.risk.includes("None")
                      ? "text-green-500"
                      : step.risk.includes("Low")
                        ? "text-blue-400"
                        : step.risk.includes("Medium")
                          ? "text-amber-400"
                          : "text-red-400"
                  }`}
                >
                  Risk: {step.risk}
                </span>
              </div>
              <p className="text-[10px] text-zinc-300 mb-1.5">
                {step.purpose}
              </p>
              <p className="text-[9px] text-zinc-500 font-mono mb-1.5">
                {step.script}
              </p>
              <div className="space-y-0.5">
                {step.details.map((d, i) => (
                  <p key={i} className="text-[9px] text-zinc-500">
                    • {d}
                  </p>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* ── GPS Estimation ────────────────────────────────────────── */}
      <Section
        id="gps"
        title="How GPS Estimation Works"
        subtitle="Pixel → GPS conversion pipeline"
      >
        <div className="space-y-2">
          {GPS_ESTIMATION.steps.map((s, i) => (
            <div key={i} className="flex gap-2 text-[10px] text-zinc-300">
              <span className="text-cyan-500/60 shrink-0 font-mono w-4 text-right">
                {i + 1}
              </span>
              <span>{s}</span>
            </div>
          ))}
          <div className="mt-2 p-2 bg-amber-500/5 border border-amber-500/20 rounded">
            <p className="text-[9px] text-amber-400">
              {GPS_ESTIMATION.whyCalibrationMatters}
            </p>
          </div>
        </div>
      </Section>

      {/* ── Architecture ──────────────────────────────────────────── */}
      <Section
        id="architecture"
        title="Architecture — Core Files"
        subtitle={`${ARCHITECTURE.coreFiles.length} core files`}
      >
        <div className="space-y-1.5">
          {ARCHITECTURE.coreFiles.map((f) => (
            <div key={f.file} className="flex gap-2 text-[10px]">
              <span className="text-cyan-400 font-mono shrink-0 w-40 text-right">
                {f.file}
              </span>
              <span className="text-zinc-400">{f.desc}</span>
            </div>
          ))}
          <div className="mt-3 pt-3 border-t border-zinc-800/30">
            <p className="text-[10px] font-bold text-zinc-300 mb-1.5">
              Key Design Decisions
            </p>
            {ARCHITECTURE.designDecisions.map((d, i) => (
              <p key={i} className="text-[9px] text-zinc-500 py-0.5">
                • {d}
              </p>
            ))}
          </div>
        </div>
      </Section>

      {/* ── Hardware ──────────────────────────────────────────────── */}
      <Section
        id="hardware"
        title="Hardware Summary"
        subtitle={`${HARDWARE_SUMMARY.length} components`}
      >
        <div className="overflow-x-auto">
          <table className="w-full text-[10px]">
            <thead>
              <tr className="text-zinc-500 text-left border-b border-zinc-800/50">
                <th className="py-1 pr-3">Component</th>
                <th className="py-1 pr-3">Model</th>
                <th className="py-1">Detail</th>
              </tr>
            </thead>
            <tbody>
              {HARDWARE_SUMMARY.map((h) => (
                <tr
                  key={h.component}
                  className="border-b border-zinc-800/20"
                >
                  <td className="py-1.5 pr-3 text-zinc-300 font-medium">
                    {h.component}
                  </td>
                  <td className="py-1.5 pr-3 text-cyan-400 font-mono">
                    {h.model}
                  </td>
                  <td className="py-1.5 text-zinc-500">{h.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* ── Connections ───────────────────────────────────────────── */}
      <Section
        id="connections"
        title="Connection Architecture"
        subtitle="How everything talks to everything"
      >
        <div className="space-y-1.5">
          {CONNECTIONS.diagram.map((line, i) => (
            <p key={i} className="text-[10px] text-zinc-300 font-mono">
              {line}
            </p>
          ))}
          <div className="mt-3 p-2 bg-zinc-800/30 rounded">
            <p className="text-[9px] text-zinc-400 mb-1">
              mavproxy command (Pi Terminal 1 — always running first):
            </p>
            <p className="text-[8px] text-zinc-500 font-mono break-all">
              {CONNECTIONS.mavproxy}
            </p>
          </div>
          <p className="text-[9px] text-zinc-500 mt-1">
            <span className="text-zinc-400">Why mavproxy?</span>{" "}
            {CONNECTIONS.whyMavproxy}
          </p>
        </div>
      </Section>

      {/* ── Config Values ─────────────────────────────────────────── */}
      <Section
        id="config"
        title="Key Config Values (config.py)"
        subtitle="Tune these after real testing"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-[10px]">
            <thead>
              <tr className="text-zinc-500 text-left border-b border-zinc-800/50">
                <th className="py-1 pr-3">Parameter</th>
                <th className="py-1 pr-3">Default</th>
                <th className="py-1 pr-3">Description</th>
                <th className="py-1">Tune With</th>
              </tr>
            </thead>
            <tbody>
              {KEY_CONFIG.map((c) => (
                <tr key={c.param} className="border-b border-zinc-800/20">
                  <td className="py-1.5 pr-3 text-cyan-400 font-mono">
                    {c.param}
                  </td>
                  <td className="py-1.5 pr-3 text-zinc-300">{c.value}</td>
                  <td className="py-1.5 pr-3 text-zinc-500">{c.desc}</td>
                  <td className="py-1.5 text-amber-400/70 font-mono text-[9px]">
                    {c.tuneWith || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* ── Models ────────────────────────────────────────────────── */}
      <Section
        id="models"
        title="AI Models — What We Have & How to Swap"
        subtitle="--model flag or cp to best.tflite"
      >
        <div className="space-y-3">
          <div>
            <p className="text-[10px] font-bold text-zinc-300 mb-1.5">
              Available Models
            </p>
            {MODELS.current.map((m) => (
              <div
                key={m.name}
                className="flex gap-2 text-[10px] py-0.5"
              >
                <span className="text-cyan-400 font-mono shrink-0 w-56">
                  {m.name}
                </span>
                <span className="text-zinc-500">
                  {m.desc} ({m.size})
                </span>
              </div>
            ))}
          </div>
          <div>
            <p className="text-[10px] font-bold text-zinc-300 mb-1.5">
              How to Swap
            </p>
            {MODELS.howToSwap.map((h, i) => (
              <p
                key={i}
                className="text-[9px] text-zinc-400 font-mono py-0.5"
              >
                {h}
              </p>
            ))}
          </div>
          <div>
            <p className="text-[10px] font-bold text-zinc-300 mb-1.5">
              Models to Prepare (TODO)
            </p>
            {MODELS.toPrepare.map((t, i) => (
              <p key={i} className="text-[9px] text-zinc-500 py-0.5">
                • {t}
              </p>
            ))}
          </div>
        </div>
      </Section>

      {/* ── How to Run ────────────────────────────────────────────── */}
      <Section
        id="howto"
        title="How to Run — Quick Commands"
        subtitle="Laptop simulation, Pi real flight, dry-run"
      >
        <div className="space-y-3 text-[10px]">
          <div>
            <p className="font-bold text-zinc-300 mb-1">
              Dry-run (no GPS, no Cube needed)
            </p>
            <div className="bg-zinc-800/30 rounded p-2 font-mono text-[9px] text-zinc-400 space-y-0.5">
              <p>python main.py --dry-run</p>
              <p>python main.py --dry-run --model models/best2.tflite</p>
            </div>
          </div>
          <div>
            <p className="font-bold text-zinc-300 mb-1">
              Simulation (laptop + SITL)
            </p>
            <div className="bg-zinc-800/30 rounded p-2 font-mono text-[9px] text-zinc-400 space-y-0.5">
              <p>set DRONE_MODE=SIMULATION</p>
              <p>python main.py</p>
              <p>python simple_simulator.py --fps 4 --tflite --gps-drift 3</p>
            </div>
          </div>
          <div>
            <p className="font-bold text-zinc-300 mb-1">
              Real flight (Pi + Cube)
            </p>
            <div className="bg-zinc-800/30 rounded p-2 font-mono text-[9px] text-zinc-400 space-y-0.5">
              <p className="text-zinc-500">
                # Terminal 1: start mavproxy (always first)
              </p>
              <p className="break-all">{CONNECTIONS.mavproxy}</p>
              <p className="text-zinc-500 mt-1">
                # Terminal 2: run script
              </p>
              <p>cd ~/dima/Group_Proj && source pienv/bin/activate</p>
              <p>
                python tests/flight/1_passive_flight.py --headless --stream
              </p>
              <p className="text-zinc-500 mt-1"># or full dashboard:</p>
              <p>python pi_flight.py --fps 4</p>
              <p className="text-zinc-500 mt-1"># Laptop browser:</p>
              <p>{"http://<PI_IP>:8090"}</p>
            </div>
          </div>
          <div>
            <p className="font-bold text-zinc-300 mb-1">
              Kill switch (always works)
            </p>
            <p className="text-zinc-400">
              RC mode switch → STABILIZE. Hardware-level override. Works
              regardless of what Python script is running.
            </p>
          </div>
        </div>
      </Section>

      {/* Footer */}
      <div className="text-[9px] text-zinc-600 pt-4 pb-8 text-center">
        SAR Drone — University of Bristol — AENGM0074 — Generated from project
        codebase
      </div>
    </div>
  );
}
