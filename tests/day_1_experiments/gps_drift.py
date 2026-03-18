#!/usr/bin/env python3
"""
GPS Drift — GPS noise floor measurement while hovering

WHAT:    Records the drone's GPS position at 4 Hz while the pilot hovers in
         place. After recording, computes horizontal drift statistics (standard
         deviation, max drift, CEP50, CEP95) and altitude stability. No camera
         or AI model is used — this is pure GPS telemetry logging.
WHY:     Establishes the GPS noise floor: the minimum possible error in any
         GPS-based estimation. If the GPS drifts 3m while stationary, target
         position estimates can never be better than 3m. Critical for sizing
         the offset landing distance.
WHEN:    Run during a manual RC hover on Day 1. Pilot holds position at
         10-15m altitude for 60+ seconds (longer is better).
WHERE:   Pi (primary) or laptop (with SITL)
ENV:     Pi: pienv venv (pymavlink). Laptop: dev venv (pymavlink).
         No camera or AI model required.
MODELS:  none — this script does not use the camera or AI.
RISK:    none — sends ZERO commands to the Cube. Purely observational.

USAGE:
    python tests/day_1_experiments/gps_drift.py --headless
    python tests/day_1_experiments/gps_drift.py --headless --duration 120

FLAGS:
    --duration N  Recording duration in seconds (default 60). Recording starts
                  automatically when GPS fix is available and altitude > 2m.

OUTPUT:
    - exp_drift_YYYYMMDD_HHMMSS.csv in project root
      Columns: timestamp, elapsed_s, lat, lon, alt, groundspeed, gps_sats,
      gps_fix
    - Terminal summary: mean distance from centre, std dev, max drift,
      CEP50, CEP95, altitude range, and interpretation

BEST PRACTICES:
    - Hover in place with minimal stick input for cleanest data
    - Run for 120+ seconds if battery allows (more samples = better stats)
    - CEP95 < 2m is good; 2-4m is acceptable; > 4m is poor
    - Compare results with and without RTK if available
    - Run early in the flight session while satellite geometry is fresh

DEPENDENCIES:
    pymavlink, config.py
"""

import sys, os, csv, time, math

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import config

# ── CLI ──────────────────────────────────────────────────────────────────
DURATION = 60  # seconds to record

for _i, _a in enumerate(sys.argv):
    if _a == "--duration" and _i + 1 < len(sys.argv):
        DURATION = int(sys.argv[_i + 1])

# ── Geo math ─────────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# ── Cube connection ─────────────────────────────────────────────────────
def connect_cube():
    try:
        from pymavlink import mavutil
    except ImportError:
        print("[CUBE] pymavlink not installed")
        return None
    conn_str = config.CONNECTION_STR
    print(f"[CUBE] Connecting: {conn_str}")
    try:
        if conn_str.startswith("/dev/"):
            mav = mavutil.mavlink_connection(conn_str, baud=config.BAUD_RATE)
        else:
            mav = mavutil.mavlink_connection(conn_str)
        mav.wait_heartbeat(timeout=10)
        print(f"[CUBE] Connected (system {mav.target_system})")
        mav.mav.request_data_stream_send(
            mav.target_system, mav.target_component, 0, 10, 1)  # 10 Hz for drift
        return mav
    except Exception as e:
        print(f"[CUBE] Failed: {e}")
        return None

# ── Main ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  EXPERIMENT: GPS Drift While Hovering")
    print("  PASSIVE — sends ZERO commands.")
    print("=" * 60)
    print()
    print(f"  Duration: {DURATION}s")
    print("  Protocol: pilot hovers in place, script logs GPS jitter")
    print()

    mav = connect_cube()
    if mav is None:
        print("Cannot run without Cube connection.")
        return

    ts_start = time.strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(project_root, f"exp_drift_{ts_start}.csv")
    log_file = open(log_path, "w", newline="")
    writer = csv.writer(log_file)
    writer.writerow(["timestamp", "elapsed_s", "lat", "lon", "alt", "groundspeed",
                      "gps_sats", "gps_fix"])

    positions = []  # (lat, lon, alt, time)
    t_start = None
    sample_interval = 0.25  # 4 Hz

    print(f"\n[READY] Waiting for GPS fix and altitude > 2m...")
    print("[READY] Pilot: hover in place and hold steady.\n")

    # Wait for GPS + altitude
    recording = False
    try:
        while True:
            msg = mav.recv_match(blocking=True, timeout=1)
            if msg is None:
                continue
            mt = msg.get_type()

            if mt == "GLOBAL_POSITION_INT":
                lat = msg.lat / 1e7
                lon = msg.lon / 1e7
                alt = msg.relative_alt / 1000.0

                if not recording:
                    if lat != 0 and alt > 2:
                        recording = True
                        t_start = time.time()
                        print(f"  RECORDING STARTED at alt={alt:.1f}m  GPS=({lat:.6f},{lon:.6f})")
                        print(f"  Hold position for {DURATION}s...")
                    continue

                elapsed = time.time() - t_start
                if elapsed > DURATION:
                    print(f"\n  {DURATION}s complete!")
                    break

                positions.append((lat, lon, alt, elapsed))
                writer.writerow([
                    time.strftime("%H:%M:%S"), f"{elapsed:.2f}",
                    f"{lat:.7f}", f"{lon:.7f}", f"{alt:.1f}", "",
                    "", ""
                ])
                log_file.flush()

                # Progress
                if len(positions) % 20 == 0:
                    print(f"  {elapsed:.0f}s / {DURATION}s  "
                          f"({len(positions)} samples)  "
                          f"alt={alt:.1f}m")

                time.sleep(sample_interval)

            elif mt == "GPS_RAW_INT" and recording:
                # Update last CSV row with satellite data
                pass

    except KeyboardInterrupt:
        print("\nStopped early.")

    log_file.close()

    # ── Analysis ─────────────────────────────────────────────────────────
    if len(positions) < 10:
        print("  Not enough data for analysis.")
        return

    lats = [p[0] for p in positions]
    lons = [p[1] for p in positions]
    alts = [p[2] for p in positions]

    mean_lat = sum(lats) / len(lats)
    mean_lon = sum(lons) / len(lons)
    mean_alt = sum(alts) / len(alts)

    # Distance of each sample from mean position
    distances = [haversine(mean_lat, mean_lon, lat, lon)
                 for lat, lon in zip(lats, lons)]

    std_dist = (sum((d - sum(distances)/len(distances))**2
                    for d in distances) / len(distances)) ** 0.5
    max_drift = max(distances)
    alt_range = max(alts) - min(alts)

    # CEP (Circular Error Probable) — radius containing 50% of points
    sorted_dist = sorted(distances)
    cep50 = sorted_dist[len(sorted_dist) // 2]
    cep95 = sorted_dist[int(len(sorted_dist) * 0.95)]

    print()
    print("=" * 60)
    print("  GPS DRIFT RESULTS")
    print("=" * 60)
    print(f"  Duration:      {positions[-1][3]:.0f}s")
    print(f"  Samples:       {len(positions)}")
    print(f"  Mean position: {mean_lat:.7f}, {mean_lon:.7f}")
    print(f"  Mean altitude: {mean_alt:.1f}m")
    print()
    print(f"  Horizontal drift:")
    print(f"    Mean distance from centre: {sum(distances)/len(distances):.2f}m")
    print(f"    Std dev:        {std_dist:.2f}m")
    print(f"    Max drift:      {max_drift:.2f}m")
    print(f"    CEP50 (50%):    {cep50:.2f}m")
    print(f"    CEP95 (95%):    {cep95:.2f}m")
    print()
    print(f"  Altitude stability:")
    print(f"    Range:    {alt_range:.2f}m")
    print(f"    Min:      {min(alts):.1f}m")
    print(f"    Max:      {max(alts):.1f}m")
    print()
    print(f"  CSV saved: {log_path}")
    print()
    print("  INTERPRETATION:")
    print(f"    GPS noise floor = ~{cep95:.1f}m (95% of readings within this radius)")
    print(f"    Your GPS estimates cannot be more accurate than this.")
    if cep95 < 2:
        print("    GOOD — GPS is tight enough for offset landing.")
    elif cep95 < 4:
        print("    OK — expect 5-8m landing accuracy with 7.5m offset.")
    else:
        print("    POOR — GPS very noisy. Consider more satellites or RTK.")
    print("=" * 60)


if __name__ == "__main__":
    main()
