#!/usr/bin/env python3
"""
GPS Ground Truth — Calibrate CV position estimates against real GPS ground truth.

WHAT:    Reads live GPS from the Cube via mavproxy and lets you mark the drone's
         position when directly over the dummy (press T). Compares these ground truth
         marks against a CV-estimated position to quantify estimation error in metres.
         Also measures GPS spread/drift by recording multiple marks from a hover.
WHY:     The full pipeline (camera detection -> pixel position -> FOV math -> GPS estimate)
         accumulates errors from FOV calibration, GPS latency, camera tilt, and altitude
         inaccuracy. This script measures the END-TO-END error so you know how close the
         drone will actually land to the target. Essential for validating that FOV
         calibration, lens correction, and GPS timing lag compensation are working.
WHEN:    During flight testing, after passive_watch.py has built a CV estimate of the
         dummy position. Fly directly over the dummy and mark ground truth.
WHERE:   Pi (with mavproxy running). Also works on laptop with SITL.
ENV:     Requires pymavlink. No camera or AI needed.
MODELS:  None (GPS only, no AI inference).
RISK:    None. ZERO commands sent. Read-only GPS monitoring.

USAGE:
    python tests/calibration/gps_ground_truth.py
    python tests/calibration/gps_ground_truth.py --connect udpin:0.0.0.0:14550
    python tests/calibration/gps_ground_truth.py --cv-estimate 51.4234 -2.6714

FLAGS:
    --connect STR           MAVLink connection string (default: udpin:0.0.0.0:14550)
    --cv-estimate LAT LON   CV-estimated dummy position to compare against

OUTPUT:
    - Live GPS display (lat, lon, alt, satellites, fix type)
    - Ground truth marks with spread analysis (max/mean distance from average)
    - CV estimate vs ground truth error in metres
    - ground_truth_YYYYMMDD_HHMMSS.txt summary file

BEST PRACTICES:
    - Use the stream crosshair (passive_watch.py) to centre the dummy before marking
    - Take 3-5 marks from different passes for a robust ground truth average
    - A GPS spread > 3m means conditions are poor — wait or take more samples
    - Hover for 5+ seconds before marking (let GPS settle)
    - Run alongside passive_watch.py: it estimates, this script validates
    - On Windows (os.name == 'nt'), keyboard input is not supported — use Pi/Linux

DEPENDENCIES:
    pymavlink, select (Unix), termios/tty (Unix)
    Note: Non-blocking keyboard input requires Unix terminal (Pi or WSL)
"""
import sys
import os
import time
import math
import signal
import argparse
from datetime import datetime

signal.signal(signal.SIGINT, signal.SIG_DFL)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pymavlink import mavutil

COPTER_MODES = {
    0: "STABILIZE", 2: "ALT_HOLD", 3: "AUTO", 4: "GUIDED",
    5: "LOITER", 6: "RTL", 9: "LAND", 16: "POSHOLD",
}


def haversine_m(lat1, lon1, lat2, lon2):
    """Distance in metres between two GPS coordinates."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def main():
    parser = argparse.ArgumentParser(description="GPS ground truth calibration")
    parser.add_argument('--connect', default='udpin:0.0.0.0:14550',
                        help='MAVLink connection (default: udpin:0.0.0.0:14550)')
    parser.add_argument('--cv-estimate', nargs=2, type=float, metavar=('LAT', 'LON'),
                        help='CV estimated dummy position (lat lon) to compare against')
    args = parser.parse_args()

    print("=" * 55)
    print("  GPS GROUND TRUTH CALIBRATION")
    print("  Fly directly over dummy, press T to mark position")
    print("  ZERO commands sent. Read-only.")
    print("=" * 55)

    # Connect to mavproxy
    print(f"\n[MAV] Connecting to {args.connect}...")
    mav = mavutil.mavlink_connection(args.connect)

    # Wait for heartbeat
    print("[MAV] Waiting for heartbeat...")
    while True:
        msg = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
        if msg and msg.type != 6:  # skip GCS heartbeats
            print(f"[MAV] Connected! System {msg.get_srcSystem()}")
            break

    # Ground truth marks
    marks = []
    cv_estimate = None
    if args.cv_estimate:
        cv_estimate = (args.cv_estimate[0], args.cv_estimate[1])
        print(f"\n[CV EST] {cv_estimate[0]:.7f}, {cv_estimate[1]:.7f}")

    print("\nControls:")
    print("  T = Mark current drone GPS as ground truth")
    print("  E = Enter CV estimate manually (lat lon)")
    print("  R = Reset all marks")
    print("  Q = Quit and show summary")
    print("\nLive GPS (updating...):\n")

    # Non-blocking keyboard input
    import select
    if os.name != 'nt':
        import tty
        import termios
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    try:
        last_print = 0
        lat, lon, alt, sats, fix = 0, 0, 0, 0, 0

        while True:
            # Read MAVLink
            msg = mav.recv_match(blocking=False)
            if msg:
                mtype = msg.get_type()
                if mtype == 'GLOBAL_POSITION_INT':
                    lat = msg.lat / 1e7
                    lon = msg.lon / 1e7
                    alt = msg.relative_alt / 1000.0
                elif mtype == 'GPS_RAW_INT':
                    sats = msg.satellites_visible
                    fix = msg.fix_type

            # Print status every 0.5s
            now = time.time()
            if now - last_print > 0.5:
                last_print = now
                fix_str = ["NO GPS", "NO FIX", "2D", "3D", "DGPS", "RTK Float", "RTK Fix"]
                fix_name = fix_str[fix] if fix < len(fix_str) else f"Type{fix}"

                status = (f"\r  GPS: {lat:.7f}, {lon:.7f} | Alt: {alt:.1f}m | "
                          f"Sats: {sats} | Fix: {fix_name} | Marks: {len(marks)}  ")
                print(status, end='', flush=True)

            # Check keyboard
            if os.name != 'nt':
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1).lower()

                    if key == 't':
                        if lat == 0 and lon == 0:
                            print("\n  [!] No GPS fix — cannot mark")
                        else:
                            mark = {
                                "lat": lat, "lon": lon, "alt": alt,
                                "sats": sats, "time": datetime.now().strftime("%H:%M:%S")
                            }
                            marks.append(mark)
                            print(f"\n  [MARK {len(marks)}] {lat:.7f}, {lon:.7f} "
                                  f"@{alt:.1f}m ({sats} sats)")

                            # Compare with CV estimate if available
                            if cv_estimate:
                                err = haversine_m(lat, lon, cv_estimate[0], cv_estimate[1])
                                print(f"  [ERROR] CV estimate vs ground truth: {err:.1f}m")

                            # If multiple marks, show spread
                            if len(marks) >= 2:
                                avg_lat = sum(m["lat"] for m in marks) / len(marks)
                                avg_lon = sum(m["lon"] for m in marks) / len(marks)
                                dists = [haversine_m(m["lat"], m["lon"], avg_lat, avg_lon)
                                         for m in marks]
                                print(f"  [SPREAD] Avg: {avg_lat:.7f}, {avg_lon:.7f} | "
                                      f"Max spread: {max(dists):.1f}m | "
                                      f"Mean spread: {sum(dists)/len(dists):.1f}m")
                        print()

                    elif key == 'e':
                        # Restore terminal for input
                        if os.name != 'nt':
                            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                        try:
                            inp = input("\n  Enter CV estimate (lat lon): ")
                            parts = inp.strip().split()
                            cv_estimate = (float(parts[0]), float(parts[1]))
                            print(f"  [CV EST] Set to {cv_estimate[0]:.7f}, {cv_estimate[1]:.7f}")
                        except (ValueError, IndexError):
                            print("  [!] Invalid input. Use: lat lon")
                        if os.name != 'nt':
                            tty.setcbreak(sys.stdin.fileno())
                        print()

                    elif key == 'r':
                        marks.clear()
                        print("\n  [RESET] All marks cleared\n")

                    elif key == 'q':
                        break

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        if os.name != 'nt':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    # Summary
    print("\n\n" + "=" * 55)
    print("  CALIBRATION SUMMARY")
    print("=" * 55)

    if not marks:
        print("  No marks recorded.")
        return

    avg_lat = sum(m["lat"] for m in marks) / len(marks)
    avg_lon = sum(m["lon"] for m in marks) / len(marks)

    print(f"\n  Ground truth marks: {len(marks)}")
    print(f"  Average position:   {avg_lat:.7f}, {avg_lon:.7f}")

    for i, m in enumerate(marks):
        d = haversine_m(m["lat"], m["lon"], avg_lat, avg_lon)
        print(f"    Mark {i+1}: {m['lat']:.7f}, {m['lon']:.7f} "
              f"@{m['alt']:.1f}m ({m['sats']}sats) [{m['time']}] "
              f"spread: {d:.1f}m")

    dists = [haversine_m(m["lat"], m["lon"], avg_lat, avg_lon) for m in marks]
    print(f"\n  GPS spread: max {max(dists):.1f}m, mean {sum(dists)/len(dists):.1f}m")

    if cv_estimate:
        err = haversine_m(avg_lat, avg_lon, cv_estimate[0], cv_estimate[1])
        print(f"\n  CV estimate:    {cv_estimate[0]:.7f}, {cv_estimate[1]:.7f}")
        print(f"  Ground truth:   {avg_lat:.7f}, {avg_lon:.7f}")
        print(f"  ESTIMATION ERROR: {err:.1f}m")

    # Save to file
    fname = f"ground_truth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(fname, 'w') as f:
        f.write(f"Ground Truth Calibration {datetime.now().isoformat()}\n")
        f.write(f"Marks: {len(marks)}\n")
        f.write(f"Average: {avg_lat:.7f}, {avg_lon:.7f}\n")
        for i, m in enumerate(marks):
            f.write(f"  {i+1}: {m['lat']:.7f},{m['lon']:.7f} @{m['alt']:.1f}m {m['sats']}sats\n")
        if cv_estimate:
            f.write(f"CV estimate: {cv_estimate[0]:.7f}, {cv_estimate[1]:.7f}\n")
            f.write(f"Error: {err:.1f}m\n")
    print(f"\n  Saved to {fname}")


if __name__ == "__main__":
    main()
