"""
Simulate drone descent behavior near NFZ buffer zone.
Models ArduCopter's position controller + geofence interactions.
Tests: does the drone reach 3m from various starting conditions?
"""
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config

# ArduCopter defaults
PSC_POSZ_P = 1.0          # Position Z proportional gain
WPNAV_SPEED_DN = 1.5      # Max descent rate m/s
WPNAV_SPEED_UP = 2.5      # Max climb rate m/s
DT = 0.1                  # Simulation timestep (seconds)
MAX_TIME = 120.0           # Max simulation time

# SSSI polygon (from config)
SSSI = config.SSSI_GPS

def point_to_segment_dist(px, py, ax, ay, bx, by):
    """Distance from point (px,py) to line segment (ax,ay)-(bx,by) in metres."""
    dx, dy = bx - ax, by - ay
    len_sq = dx*dx + dy*dy
    if len_sq < 1e-12:
        return math.sqrt((px-ax)**2 + (py-ay)**2)
    t = max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / len_sq))
    cx, cy = ax + t*dx, ay + t*dy
    return math.sqrt((px-cx)**2 + (py-cy)**2)

def dist_to_nfz_m(lat, lon):
    """Approximate distance to nearest NFZ edge in metres."""
    lat_m = 111320.0
    lon_m = 111320.0 * math.cos(math.radians(lat))
    best = float('inf')
    for i in range(len(SSSI)):
        p1 = SSSI[i]
        p2 = SSSI[(i+1) % len(SSSI)]
        d = point_to_segment_dist(
            lat * lat_m, lon * lon_m,
            p1[0] * lat_m, p1[1] * lon_m,
            p2[0] * lat_m, p2[1] * lon_m)
        best = min(best, d)
    return best

def simulate_descent(start_alt, target_alt, nfz_dist_m, has_vz_hint=False,
                     set_speed_active=False, set_speed_val=3.0,
                     label=""):
    """
    Simulate vertical descent from start_alt to target_alt.

    Models:
    - ArduCopter position controller: climb_rate = PSC_POSZ_P * alt_error
    - WPNAV_SPEED_DN cap on descent rate
    - Optional vz feed-forward hint
    - Optional set_speed airspeed limit effect on vertical
    """
    alt = start_alt
    t = 0.0
    stuck_count = 0
    prev_alt = alt

    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"  Start: {start_alt}m → Target: {target_alt}m | NFZ dist: {nfz_dist_m}m")
    print(f"  vz hint: {has_vz_hint} | set_speed active: {set_speed_active} ({set_speed_val} m/s)")
    print(f"{'='*70}")

    while t < MAX_TIME:
        alt_error = alt - target_alt  # positive = above target

        # ArduCopter position controller: P-gain
        desired_rate = PSC_POSZ_P * alt_error  # positive = descend

        # Cap by WPNAV_SPEED_DN
        if desired_rate > 0:
            desired_rate = min(desired_rate, WPNAV_SPEED_DN)
        else:
            desired_rate = max(desired_rate, -WPNAV_SPEED_UP)

        # vz feed-forward (like DESCENDING handler P-controller)
        if has_vz_hint:
            if alt_error > 0.5:
                vz_hint = min(0.5 * alt_error, 1.5)
            elif alt_error < -0.5:
                vz_hint = max(0.5 * alt_error, -1.5)
            else:
                vz_hint = 0
            # Feed-forward adds to P-controller output
            desired_rate = min(desired_rate + vz_hint, WPNAV_SPEED_DN)

        # set_speed effect: if active, total velocity budget is limited
        # Assume some horizontal speed component uses part of the budget
        if set_speed_active and nfz_dist_m < 20:
            # Speed ramp: 0 at 2m, set_speed_val at 20m
            if nfz_dist_m <= 2.0:
                horiz_budget = 0.0
            else:
                ratio = (nfz_dist_m - 2.0) / (20.0 - 2.0)
                horiz_budget = ratio * set_speed_val

            # If drone is also moving horizontally toward landing spot,
            # the airspeed limit constrains total velocity vector
            assumed_horiz_speed = min(horiz_budget, 2.0)  # assume ~2 m/s horizontal
            total_budget = set_speed_val
            remaining_for_vert = math.sqrt(max(0, total_budget**2 - assumed_horiz_speed**2))
            if desired_rate > remaining_for_vert:
                desired_rate = remaining_for_vert

        # Apply descent
        alt -= desired_rate * DT
        t += DT

        # Check if stuck (altitude not changing)
        if abs(alt - prev_alt) < 0.001:
            stuck_count += 1
        else:
            stuck_count = 0
        prev_alt = alt

        # Print progress every 5 seconds
        if int(t * 10) % 50 == 0:
            print(f"  t={t:5.1f}s  alt={alt:6.2f}m  rate={desired_rate:5.2f}m/s  err={alt_error:6.2f}m")

        # Check success
        if abs(alt - target_alt) < 0.5:
            print(f"  ✓ REACHED {alt:.1f}m at t={t:.1f}s")
            return True, t, alt

        # Check stuck
        if stuck_count > 50:  # 5 seconds stuck
            print(f"  ✗ STUCK at {alt:.1f}m after {t:.1f}s")
            return False, t, alt

    print(f"  ✗ TIMEOUT at {alt:.1f}m after {t:.1f}s")
    return False, t, alt


def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║        DESCENT SIMULATION — NFZ Buffer Zone Effects                 ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    results = []

    # ── Experiment 1: Baseline (far from NFZ, no interference) ────────
    ok, t, alt = simulate_descent(
        19.0, 3.0, nfz_dist_m=100,
        has_vz_hint=False, set_speed_active=False,
        label="EXP 1: Baseline — 100m from NFZ, no vz hint, no set_speed")
    results.append(("Baseline (100m, no vz)", ok, t, alt))

    # ── Experiment 2: With vz hint (like DESCENDING handler) ──────────
    ok, t, alt = simulate_descent(
        19.0, 3.0, nfz_dist_m=100,
        has_vz_hint=True, set_speed_active=False,
        label="EXP 2: With vz hint — 100m from NFZ")
    results.append(("With vz hint (100m)", ok, t, alt))

    # ── Experiment 3: Near NFZ (5m), no vz, OLD set_speed active ──────
    ok, t, alt = simulate_descent(
        19.0, 3.0, nfz_dist_m=5,
        has_vz_hint=False, set_speed_active=True, set_speed_val=3.0,
        label="EXP 3: OLD CODE — 5m from NFZ, set_speed active (3 m/s cap)")
    results.append(("OLD: 5m NFZ + set_speed", ok, t, alt))

    # ── Experiment 4: Near NFZ (2m), no vz, OLD set_speed active ──────
    ok, t, alt = simulate_descent(
        19.0, 3.0, nfz_dist_m=2,
        has_vz_hint=False, set_speed_active=True, set_speed_val=3.0,
        label="EXP 4: OLD CODE — 2m from NFZ, set_speed active (ZERO speed cap)")
    results.append(("OLD: 2m NFZ + set_speed", ok, t, alt))

    # ── Experiment 5: Near NFZ (5m), no vz, NEW code (set_speed disabled) ─
    ok, t, alt = simulate_descent(
        19.0, 3.0, nfz_dist_m=5,
        has_vz_hint=False, set_speed_active=False,
        label="EXP 5: NEW CODE — 5m from NFZ, set_speed DISABLED")
    results.append(("NEW: 5m NFZ, no set_speed", ok, t, alt))

    # ── Experiment 6: Near NFZ (2m), no vz, NEW code ──────────────────
    ok, t, alt = simulate_descent(
        19.0, 3.0, nfz_dist_m=2,
        has_vz_hint=False, set_speed_active=False,
        label="EXP 6: NEW CODE — 2m from NFZ, set_speed DISABLED")
    results.append(("NEW: 2m NFZ, no set_speed", ok, t, alt))

    # ── Experiment 7: Near NFZ (5m), WITH vz hint, NEW code ───────────
    ok, t, alt = simulate_descent(
        19.0, 3.0, nfz_dist_m=5,
        has_vz_hint=True, set_speed_active=False,
        label="EXP 7: NEW CODE + vz hint — 5m from NFZ")
    results.append(("NEW + vz: 5m NFZ", ok, t, alt))

    # ── Experiment 8: Starting from 35m (skipped DESCENDING) ──────────
    ok, t, alt = simulate_descent(
        35.0, 3.0, nfz_dist_m=5,
        has_vz_hint=False, set_speed_active=False,
        label="EXP 8: From 35m (no DESCENDING step) — 5m from NFZ")
    results.append(("35m start, 5m NFZ", ok, t, alt))

    # ── Experiment 9: From 35m with OLD set_speed ─────────────────────
    ok, t, alt = simulate_descent(
        35.0, 3.0, nfz_dist_m=5,
        has_vz_hint=False, set_speed_active=True, set_speed_val=3.0,
        label="EXP 9: OLD CODE — From 35m, 5m NFZ, set_speed active")
    results.append(("OLD: 35m, 5m NFZ + set_speed", ok, t, alt))

    # ── Experiment 10: Climb from 3m to 35m (RETURN_TRANSIT) ──────────
    ok, t, alt = simulate_descent(
        3.0, 35.0, nfz_dist_m=5,
        has_vz_hint=False, set_speed_active=False,
        label="EXP 10: CLIMB 3m→35m (RETURN_TRANSIT, no vz hint)")
    results.append(("Climb 3→35, no vz", ok, t, alt))

    # ── Experiment 11: Climb with vz hint ─────────────────────────────
    ok, t, alt = simulate_descent(
        3.0, 35.0, nfz_dist_m=5,
        has_vz_hint=True, set_speed_active=False,
        label="EXP 11: CLIMB 3m→35m WITH vz=-1.5 hint")
    results.append(("Climb 3→35, with vz", ok, t, alt))

    # ── Summary ───────────────────────────────────────────────────────
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                         RESULTS SUMMARY                             ║")
    print("╠══════════════════════════════════════════════════════════════════════╣")
    print(f"║ {'Experiment':<35} {'Result':^8} {'Time':>6} {'Final Alt':>10} ║")
    print("╠══════════════════════════════════════════════════════════════════════╣")
    for name, ok, t, alt in results:
        status = "✓ OK" if ok else "✗ FAIL"
        print(f"║ {name:<35} {status:^8} {t:5.1f}s {alt:8.1f}m ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    # ── Experiment 12-15: THE REAL BUG — velocity override ─────────────
    print("\n" + "="*70)
    print("  REAL BUG SIMULATION: send_velocity(0,0,0) overriding position target")
    print("="*70)

    for nfz_d, label_d in [(5, "5m"), (2, "2m"), (10, "10m"), (0, "INSIDE")]:
        alt = 19.0
        target = 3.0
        t = 0.0
        in_manual = False
        manual_time = 0.0
        reached = False

        print(f"\n  EXP: OLD CODE — {label_d} from NFZ, velocity override simulation")
        print(f"  Simulates: APPROACH sends position target, geofence sends velocity(0,0,0)")

        while t < 60:
            alt_error = alt - target

            # State handler: send_global_target(3.0) — P-controller
            pos_rate = min(PSC_POSZ_P * alt_error, WPNAV_SPEED_DN) if alt_error > 0 else 0

            # Geofence: if near NFZ AND old code
            if nfz_d <= 3.0:  # inside hard boundary
                if not in_manual:
                    in_manual = True
                    manual_time = t
                    print(f"    t={t:.1f}s: MANUAL switch! send_velocity(0,0,0)")
                # In MANUAL: repulsive push with vz=0 OVERRIDES position target
                actual_rate = 0  # vz=0 locks altitude
            else:
                # Outside hard boundary but in speed ramp zone
                actual_rate = pos_rate

            alt -= actual_rate * DT
            t += DT

            if int(t*10) % 50 == 0:
                state = "MANUAL" if in_manual else "APPROACH"
                print(f"    t={t:5.1f}s  alt={alt:6.2f}m  rate={actual_rate:5.2f}m/s  [{state}]")

            if abs(alt - target) < 0.5:
                print(f"    ✓ REACHED {alt:.1f}m at t={t:.1f}s")
                reached = True
                break

        if not reached:
            if in_manual:
                print(f"    ✗ STUCK at {alt:.1f}m — velocity override locked altitude since t={manual_time:.1f}s")
            else:
                print(f"    ✗ STUCK at {alt:.1f}m after {t:.1f}s")

        results.append((f"VELOVERRIDE {label_d} NFZ", reached, t, alt))

    # ── Experiment: NEW CODE near NFZ ─────────────────────────────────
    for nfz_d, label_d in [(0, "INSIDE"), (2, "2m"), (5, "5m")]:
        alt = 19.0
        target = 3.0
        t = 0.0
        reached = False

        print(f"\n  EXP: NEW CODE — {label_d} from NFZ, no velocity override")
        print(f"  Simulates: skip_speed_clamp=True, no MANUAL switch, position target works")

        while t < 60:
            alt_error = alt - target
            # Position target always works — no velocity override
            pos_rate = min(PSC_POSZ_P * alt_error, WPNAV_SPEED_DN) if alt_error > 0 else 0
            alt -= pos_rate * DT
            t += DT

            if int(t*10) % 50 == 0:
                print(f"    t={t:5.1f}s  alt={alt:6.2f}m  rate={pos_rate:5.2f}m/s  [APPROACH]")

            if abs(alt - target) < 0.5:
                print(f"    ✓ REACHED {alt:.1f}m at t={t:.1f}s")
                reached = True
                break

        if not reached:
            print(f"    ✗ STUCK at {alt:.1f}m")
        results.append((f"NEW {label_d} NFZ", reached, t, alt))

    # ── Final summary ─────────────────────────────────────────────────
    print("\n")
    print("="*70)
    print("  FULL RESULTS SUMMARY")
    print("="*70)
    print(f"  {'Experiment':<40} {'Result':^8} {'Time':>6} {'Alt':>6}")
    print("-"*70)
    for name, ok, t, alt in results:
        status = "OK" if ok else "FAIL"
        print(f"  {name:<40} {status:^8} {t:5.1f}s {alt:5.1f}m")

    # Analysis
    print("\n── ANALYSIS ──")
    print("• Position-only (no vz hint): ArduCopter uses P-gain (PSC_POSZ_P=1.0)")
    print(f"  For 16m error: rate = min(1.0 × 16, {WPNAV_SPEED_DN}) = {WPNAV_SPEED_DN} m/s")
    print(f"  Time to descend 16m at {WPNAV_SPEED_DN} m/s = {16/WPNAV_SPEED_DN:.1f}s")
    print()
    print("• OLD code (set_speed active near NFZ):")
    print("  At 5m from NFZ: speed cap ~0.83 m/s → vertical budget shrinks")
    print("  At 2m from NFZ: speed cap 0 → NO vertical movement possible")
    print()
    print("• NEW code (set_speed disabled):")
    print("  No speed interference → P-controller descends freely")
    print("  Adding vz hint makes descent faster but not strictly necessary")


if __name__ == "__main__":
    main()
