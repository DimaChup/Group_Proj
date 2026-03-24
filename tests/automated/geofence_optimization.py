#!/usr/bin/env python3
"""
Geofence Repulsion Parameter Optimization
==========================================
2D physics simulation: drone approaches SSSI boundary and gets repelled.
Sweeps parameter combinations to find optimal geofence repulsion settings.

Physics model:
- ArduCopter ~0.5s first-order lag on velocity commands
- Repulsive force: nudge_speed = MAX_SPEED * urgency (linear or quadratic)
- Optional damping when drone already moving away
- 50Hz simulation loop (dt=0.02s)

Usage:
    python tests/automated/geofence_optimization.py
"""

import math
import itertools
import sys
from dataclasses import dataclass, field
from typing import List, Tuple

# ─── Parameters to sweep ───────────────────────────────────────────────
MAX_REPULSION_SPEEDS = [3, 5, 6, 8, 10, 12, 15]       # m/s
BUFFER_DISTANCES     = [8, 10, 12, 15]                  # metres
DAMPING_THRESHOLDS   = [0, 1.0, 1.5, 2.0, 3.0]         # m/s (0 = no damping)
SCALING_MODES        = ["linear", "quadratic"]

# ─── Simulation constants ──────────────────────────────────────────────
DT = 0.02                   # 50 Hz
DRONE_RESPONSE_LAG = 0.5    # seconds — ArduCopter PID lag
SIM_DURATION = 15.0         # seconds per scenario
SETTLE_VEL_THRESH = 0.15    # m/s — consider settled when |v| < this
BOUNDARY_X = 0.0            # SSSI boundary at x=0; drone starts at positive x

# ─── Test scenarios ────────────────────────────────────────────────────
@dataclass
class Scenario:
    name: str
    approach_speed: float   # m/s (positive = toward boundary)
    start_x: float          # metres from boundary
    angle_deg: float        # 0 = head-on, 45 = grazing

SCENARIOS = [
    Scenario("3 m/s head-on",    3,  20, 0),
    Scenario("5 m/s head-on",    5,  20, 0),
    Scenario("8 m/s head-on",    8,  20, 0),
    Scenario("12 m/s head-on",  12,  20, 0),
    Scenario("15 m/s head-on",  15,  20, 0),
    Scenario("5 m/s 45-deg",     5,  20, 45),
    Scenario("8 m/s 30-deg",     8,  20, 30),
]

# ─── Result containers ─────────────────────────────────────────────────
@dataclass
class ScenarioResult:
    scenario_name: str
    min_distance: float       # closest approach to boundary (negative = breach)
    overshoot: float          # how far past buffer edge (0 if never entered buffer.. wait,
                              # overshoot = buffer - min_distance if min_distance < buffer)
    settle_time: float        # time until velocity < threshold
    oscillation_count: int    # direction reversals in x-velocity
    breached: bool            # crossed x=0?

@dataclass
class ParamResult:
    max_speed: float
    buffer: float
    damping: float
    scaling: str
    scenario_results: List[ScenarioResult] = field(default_factory=list)
    score: float = 0.0
    failed: bool = False
    fail_reason: str = ""


def run_scenario(scenario: Scenario, max_speed: float, buffer: float,
                 damping: float, scaling: str) -> ScenarioResult:
    """Run one 2D physics simulation of drone approaching boundary."""
    angle_rad = math.radians(scenario.angle_deg)

    # Initial conditions
    x = scenario.start_x
    y = 0.0
    # Velocity components (negative vx = toward boundary at x=0)
    vx = -scenario.approach_speed * math.cos(angle_rad)
    vy = -scenario.approach_speed * math.sin(angle_rad)

    steps = int(SIM_DURATION / DT)
    min_dist = x
    breached = False
    oscillations = 0
    prev_vx_sign = -1  # starts moving toward boundary
    settle_time = SIM_DURATION  # default: never settled
    settled = False

    for step in range(steps):
        t = step * DT
        dist = x  # distance to boundary (boundary at x=0)

        if dist < min_dist:
            min_dist = dist
        if dist <= 0:
            breached = True

        # ── Compute repulsive velocity command ──
        if dist < buffer and dist >= 0:
            urgency = 1.0 - dist / buffer
            if scaling == "quadratic":
                urgency = urgency ** 2
            push_speed = max_speed * urgency

            # Damping: if drone already moving away (vx > 0), reduce push
            if damping > 0 and vx > 0:
                damping_factor = max(0.0, 1.0 - vx / damping)
                push_speed *= damping_factor

            target_vx = push_speed  # push away from boundary (positive x)
            # Y component: no repulsion in y (boundary is a line along y-axis)
            target_vy = vy * 0.95  # slight friction to slow lateral drift
        elif dist < 0:
            # Inside SSSI — maximum push out
            target_vx = max_speed
            target_vy = 0.0
        else:
            # Outside buffer — keep approaching
            target_vx = -scenario.approach_speed * math.cos(angle_rad)
            target_vy = -scenario.approach_speed * math.sin(angle_rad)

        # ── ArduCopter first-order lag ──
        alpha = DT / DRONE_RESPONSE_LAG
        vx += (target_vx - vx) * alpha
        vy += (target_vy - vy) * alpha

        # ── Update position ──
        x += vx * DT
        y += vy * DT

        # ── Track oscillations (sign changes in vx) ──
        current_sign = 1 if vx > 0.05 else (-1 if vx < -0.05 else 0)
        if current_sign != 0 and prev_vx_sign != 0 and current_sign != prev_vx_sign:
            oscillations += 1
        if current_sign != 0:
            prev_vx_sign = current_sign

        # ── Check settle (velocity magnitude below threshold while in buffer) ──
        speed = math.sqrt(vx**2 + vy**2)
        if not settled and dist > 0 and dist < buffer and speed < SETTLE_VEL_THRESH:
            settle_time = t
            settled = True
        # Un-settle if it speeds up again
        if settled and speed > SETTLE_VEL_THRESH * 3:
            settled = False
            settle_time = SIM_DURATION

    # Final settle check — if drone moved out of buffer and stopped, that counts
    if not settled:
        speed = math.sqrt(vx**2 + vy**2)
        if speed < SETTLE_VEL_THRESH:
            settle_time = SIM_DURATION * 0.9  # late settle

    overshoot = max(0, buffer - min_dist) if min_dist < buffer else 0.0

    return ScenarioResult(
        scenario_name=scenario.name,
        min_distance=min_dist,
        overshoot=overshoot,
        settle_time=settle_time,
        oscillation_count=oscillations,
        breached=breached,
    )


def score_results(param: ParamResult) -> float:
    """Score a parameter set across all scenarios. Higher = better."""
    total = 0.0

    for r in param.scenario_results:
        if r.breached:
            param.failed = True
            param.fail_reason = f"Breach in '{r.scenario_name}'"
            return -1000.0
        if r.oscillation_count > 5:
            param.failed = True
            param.fail_reason = f"{r.oscillation_count} oscillations in '{r.scenario_name}'"
            return -500.0

    for r in param.scenario_results:
        # min_distance_score: ideal is ~2m from boundary (not too close, not too far)
        # Peak at 2m, drops off either side
        dist_err = abs(r.min_distance - 2.0)
        if r.min_distance < 0.5:
            dist_score = -20.0  # very bad, almost breached
        elif r.min_distance < 1.0:
            dist_score = 2.0
        else:
            dist_score = max(0, 10.0 - dist_err * 2.0)

        # overshoot_score: less is better (0 overshoot into buffer is fine,
        # but deep penetration toward boundary is bad)
        overshoot_score = max(0, 10.0 - r.overshoot * 1.5)

        # settle_score: faster settle = better
        settle_score = max(0, 10.0 - r.settle_time * 1.0)

        # oscillation penalty
        osc_penalty = r.oscillation_count * 2.0

        scenario_score = dist_score + overshoot_score + settle_score - osc_penalty
        total += scenario_score

    return total


def main():
    print("=" * 80)
    print("GEOFENCE REPULSION PARAMETER OPTIMIZATION")
    print("=" * 80)
    print(f"Scenarios: {len(SCENARIOS)}")
    combos = (len(MAX_REPULSION_SPEEDS) * len(BUFFER_DISTANCES) *
              len(DAMPING_THRESHOLDS) * len(SCALING_MODES))
    print(f"Parameter combinations: {combos}")
    print(f"Total simulations: {combos * len(SCENARIOS)}")
    print()

    all_results: List[ParamResult] = []

    for max_spd, buf, damp, scl in itertools.product(
        MAX_REPULSION_SPEEDS, BUFFER_DISTANCES, DAMPING_THRESHOLDS, SCALING_MODES
    ):
        pr = ParamResult(max_speed=max_spd, buffer=buf, damping=damp, scaling=scl)

        for scenario in SCENARIOS:
            result = run_scenario(scenario, max_spd, buf, damp, scl)
            pr.scenario_results.append(result)

        pr.score = score_results(pr)
        all_results.append(pr)

    # Sort by score descending
    all_results.sort(key=lambda p: p.score, reverse=True)

    # ── Summary statistics ──
    passed = [r for r in all_results if not r.failed]
    failed = [r for r in all_results if r.failed]
    breached = [r for r in all_results if r.fail_reason.startswith("Breach")]

    print(f"Results: {len(passed)} PASSED, {len(failed)} FAILED "
          f"({len(breached)} breaches, {len(failed)-len(breached)} oscillation failures)")
    print()

    # ── TOP 10 table ──
    print("=" * 80)
    print("TOP 10 PARAMETER SETS (ranked by score)")
    print("=" * 80)
    print(f"{'Rank':<5} {'MaxSpd':<7} {'Buffer':<7} {'Damp':<6} {'Scale':<10} "
          f"{'Score':<8} {'MinDist':<9} {'MaxOvr':<9} {'MaxSettle':<10} {'MaxOsc':<7}")
    print("-" * 80)

    for i, pr in enumerate(all_results[:10]):
        min_d = min(r.min_distance for r in pr.scenario_results)
        max_o = max(r.overshoot for r in pr.scenario_results)
        max_s = max(r.settle_time for r in pr.scenario_results)
        max_osc = max(r.oscillation_count for r in pr.scenario_results)
        print(f"{i+1:<5} {pr.max_speed:<7.0f} {pr.buffer:<7.0f} {pr.damping:<6.1f} "
              f"{pr.scaling:<10} {pr.score:<8.1f} {min_d:<9.2f} {max_o:<9.2f} "
              f"{max_s:<10.1f} {max_osc:<7}")

    print()

    # ── TOP 5 detailed ──
    print("=" * 80)
    print("TOP 5 — DETAILED BREAKDOWN")
    print("=" * 80)

    for i, pr in enumerate(all_results[:5]):
        print(f"\n--- #{i+1}: MAX_SPEED={pr.max_speed}, BUFFER={pr.buffer}, "
              f"DAMPING={pr.damping}, SCALING={pr.scaling} | Score={pr.score:.1f} ---")
        print(f"  {'Scenario':<25} {'MinDist':>8} {'Overshoot':>10} "
              f"{'Settle':>8} {'Osc':>5} {'Status':>8}")
        for r in pr.scenario_results:
            status = "FAIL" if r.breached else "PASS"
            print(f"  {r.scenario_name:<25} {r.min_distance:>8.2f} {r.overshoot:>10.2f} "
                  f"{r.settle_time:>8.1f} {r.oscillation_count:>5} {status:>8}")

    print()

    # ── Best pick scenario check ──
    best = all_results[0]
    print("=" * 80)
    print("RECOMMENDED PARAMETERS")
    print("=" * 80)
    print(f"  MAX_REPULSION_SPEED = {best.max_speed} m/s")
    print(f"  BUFFER_DISTANCE     = {best.buffer} m")
    print(f"  DAMPING_THRESHOLD   = {best.damping} m/s" +
          (" (no damping)" if best.damping == 0 else ""))
    print(f"  SCALING             = {best.scaling}")
    print(f"  SCORE               = {best.score:.1f}")
    print()

    # Scenario pass/fail for the winner
    print("Scenario results for recommended parameters:")
    all_pass = True
    for r in best.scenario_results:
        status = "PASS" if not r.breached else "FAIL"
        if r.breached:
            all_pass = False
        margin = f"margin={r.min_distance:.2f}m"
        print(f"  [{status}] {r.scenario_name:<25} {margin}, "
              f"settle={r.settle_time:.1f}s, osc={r.oscillation_count}")

    print()
    if all_pass:
        print("ALL SCENARIOS PASSED with recommended parameters.")
    else:
        print("WARNING: Some scenarios FAILED. Review parameters.")

    # ── Worst-case analysis ──
    print()
    print("=" * 80)
    print("WORST-CASE ANALYSIS (recommended params)")
    print("=" * 80)
    worst_dist = min(r.min_distance for r in best.scenario_results)
    worst_scenario = min(best.scenario_results, key=lambda r: r.min_distance)
    print(f"  Closest approach:   {worst_dist:.2f}m (in '{worst_scenario.scenario_name}')")
    print(f"  Max overshoot:      {max(r.overshoot for r in best.scenario_results):.2f}m")
    print(f"  Max settle time:    {max(r.settle_time for r in best.scenario_results):.1f}s")
    print(f"  Max oscillations:   {max(r.oscillation_count for r in best.scenario_results)}")

    # ── Parameter sensitivity ──
    print()
    print("=" * 80)
    print("PARAMETER SENSITIVITY (how each parameter affects score)")
    print("=" * 80)

    # Group by each parameter and show average score
    for param_name, values in [
        ("MAX_SPEED", MAX_REPULSION_SPEEDS),
        ("BUFFER", BUFFER_DISTANCES),
        ("DAMPING", DAMPING_THRESHOLDS),
        ("SCALING", SCALING_MODES),
    ]:
        print(f"\n  {param_name}:")
        for val in values:
            if param_name == "MAX_SPEED":
                subset = [r for r in passed if r.max_speed == val]
            elif param_name == "BUFFER":
                subset = [r for r in passed if r.buffer == val]
            elif param_name == "DAMPING":
                subset = [r for r in passed if r.damping == val]
            else:
                subset = [r for r in passed if r.scaling == val]

            if subset:
                avg = sum(r.score for r in subset) / len(subset)
                best_in = max(subset, key=lambda r: r.score)
                print(f"    {str(val):<12} avg_score={avg:>6.1f}  "
                      f"best={best_in.score:>6.1f}  n={len(subset)}")
            else:
                print(f"    {str(val):<12} ALL FAILED")

    # ── Failure analysis ──
    if breached:
        print()
        print("=" * 80)
        print(f"BREACH ANALYSIS ({len(breached)} parameter sets caused SSSI breach)")
        print("=" * 80)
        # Show which parameter values most commonly cause breaches
        from collections import Counter
        spd_counts = Counter(r.max_speed for r in breached)
        buf_counts = Counter(r.buffer for r in breached)
        print("  Breaches by MAX_SPEED:", dict(sorted(spd_counts.items())))
        print("  Breaches by BUFFER:   ", dict(sorted(buf_counts.items())))


if __name__ == "__main__":
    main()
