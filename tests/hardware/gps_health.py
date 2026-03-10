#!/usr/bin/env python3
"""
GPS Health Check — step-by-step verification of Here 3+ GPS.

Goes through each layer in order:
  Step 1: Cube connected? (heartbeat)
  Step 2: CAN bus enabled? (parameters)
  Step 3: GPS type configured? (GPS_TYPE = 9 for DroneCAN)
  Step 4: GPS hardware talking? (GPS_RAW_INT messages arriving)
  Step 5: Satellites visible? (fix_type, sat count)
  Step 6: 3D fix? (live tracking until fix or Ctrl+C)

Each step must pass before the next makes sense.
If a step fails, it tells you exactly what to check.

LED Reference (Here 3+):
  Flashing BLUE   = no GPS lock (searching)
  Flashing GREEN  = GPS lock acquired (ready to arm!)
  Double YELLOW   = pre-arm checks failing
  Flashing YELLOW = RC failsafe active

Usage:
    python tests2/gps_health.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymavlink import mavutil
import config


def read_param(mav, name, fallback_name=None, timeout=2):
    """Read a parameter from the Cube. Try name first, then fallback."""
    for pname in [name] + ([fallback_name] if fallback_name else []):
        mav.mav.param_request_read_send(
            mav.target_system, mav.target_component,
            pname.encode() if isinstance(pname, str) else pname, -1)
        msg = mav.recv_match(type='PARAM_VALUE', blocking=True, timeout=timeout)
        if msg:
            return msg.param_id.rstrip(chr(0)), int(msg.param_value)
    return None, None


def main():
    print()
    print("=" * 60)
    print("   GPS HEALTH CHECK — Here 3+ Step-by-Step")
    print("=" * 60)
    print()

    step = 0
    all_pass = True

    # ── Step 1: Connect to Cube ──
    step += 1
    print(f"  STEP {step}: CUBE CONNECTION")
    print(f"  {'-'*50}")

    conn_str = config.CONNECTION_STR
    print(f"  Connecting: {conn_str}")
    mav = mavutil.mavlink_connection(conn_str)
    msg = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=10)
    if not msg:
        print(f"  [FAIL] No heartbeat from Cube")
        print(f"         Is mavproxy running?")
        print(f"         Is Cube powered?")
        sys.exit(1)

    print(f"  [PASS] Cube connected (system {mav.target_system})")

    # Request data streams
    mav.mav.request_data_stream_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
    time.sleep(0.5)

    # ── Step 2: CAN bus enabled ──
    step += 1
    print(f"\n  STEP {step}: CAN BUS (Here 3+ connects via CAN)")
    print(f"  {'-'*50}")

    can_params = [
        ("CAN_P1_DRIVER",   "CAN port 1 driver",   1, "1 = enabled"),
        ("CAN_D1_PROTOCOL", "CAN1 protocol",        1, "1 = DroneCAN"),
        ("CAN_P2_DRIVER",   "CAN port 2 driver",    1, "1 = enabled"),
        ("CAN_D2_PROTOCOL", "CAN2 protocol",        1, "1 = DroneCAN"),
    ]

    can_ok = False
    for pname, desc, expected, expected_desc in can_params:
        name, val = read_param(mav, pname)
        if name is not None:
            ok = (val == expected)
            status = "OK" if ok else "!!"
            print(f"  [{status}] {name:<20} = {val}  ({desc}, want {expected_desc})")
            if ok and "DRIVER" in pname:
                can_ok = True
        else:
            print(f"  [??] {pname:<20} = not found")

    if can_ok:
        print(f"  [PASS] At least one CAN port enabled")
    else:
        print(f"  [WARN] No CAN port enabled — Here 3+ needs CAN")
        print(f"         In Mission Planner: Config > Full Parameter Tree")
        print(f"         Set CAN_P1_DRIVER=1, CAN_D1_PROTOCOL=1")
        print(f"         (or P2 if GPS is on CAN2 port)")
        print(f"         Reboot Cube after changing")
        all_pass = False

    # ── Step 3: GPS type configured ──
    step += 1
    print(f"\n  STEP {step}: GPS TYPE PARAMETER")
    print(f"  {'-'*50}")

    # ArduCopter 4.6+ renamed GPS_TYPE → GPS1_TYPE
    name, gps_type = read_param(mav, "GPS1_TYPE", "GPS_TYPE")
    if name is not None:
        print(f"  {name} = {gps_type}")
        if gps_type == 9:
            print(f"  [PASS] GPS type = DroneCAN (correct for Here 3+)")
        elif gps_type == 1:
            print(f"  [WARN] GPS type = Serial (Here 3+ uses CAN, not serial)")
            print(f"         Change to 9 in Mission Planner, then reboot")
            all_pass = False
        elif gps_type == 0:
            print(f"  [FAIL] GPS type = DISABLED")
            print(f"         Set GPS_TYPE=9 in Mission Planner, then reboot")
            all_pass = False
        else:
            print(f"  [??]   GPS type = {gps_type} (expected 9 for DroneCAN)")
    else:
        print(f"  [FAIL] Could not read GPS_TYPE parameter")
        all_pass = False

    # Also check GPS auto-config
    name, auto_cfg = read_param(mav, "GPS_AUTO_CONFIG")
    if name and auto_cfg is not None:
        print(f"  {name} = {auto_cfg} ({'enabled' if auto_cfg else 'disabled'})")

    # ── Step 4: GPS hardware talking ──
    step += 1
    print(f"\n  STEP {step}: GPS HARDWARE DATA")
    print(f"  {'-'*50}")
    print(f"  Listening for GPS_RAW_INT messages (5 sec)...")

    # Drain old messages first
    while mav.recv_msg() is not None:
        pass

    gps_msg = mav.recv_match(type='GPS_RAW_INT', blocking=True, timeout=5)
    if gps_msg is None:
        print(f"  [FAIL] No GPS data arriving from Cube")
        print(f"")
        print(f"  The Cube is NOT receiving GPS data. Check:")
        print(f"    1. Is Here 3+ cable plugged into CAN1 or CAN2 on Cube?")
        print(f"    2. Is the cable fully seated on BOTH ends?")
        print(f"    3. Does the Here 3+ LED light up at all?")
        print(f"       - No light = no power = bad cable or wrong port")
        print(f"       - Any light = getting power, software issue")
        print(f"    4. Try the OTHER CAN port on the Cube")
        print(f"    5. After changing ports, reboot Cube")
        all_pass = False

        # Check for any GPS-related STATUSTEXT messages
        print(f"\n  Checking Cube status messages...")
        for _ in range(20):
            stxt = mav.recv_match(type='STATUSTEXT', blocking=True, timeout=0.5)
            if stxt:
                text = stxt.text
                if 'gps' in text.lower() or 'can' in text.lower():
                    print(f"    Cube says: \"{text}\"")
            else:
                break
    else:
        fix = gps_msg.fix_type
        sats = gps_msg.satellites_visible
        print(f"  [PASS] GPS hardware is connected and sending data!")
        print(f"         fix_type = {fix}, satellites = {sats}")

        if sats == 0:
            print(f"         (0 satellites — normal indoors, need sky view)")

    # ── Step 5: Satellite status ──
    step += 1
    print(f"\n  STEP {step}: SATELLITE STATUS")
    print(f"  {'-'*50}")

    if gps_msg is None:
        print(f"  [SKIP] No GPS data — fix Step 4 first")
    else:
        fix_names = {
            0: "No GPS",
            1: "No Fix (searching)",
            2: "2D Fix (no altitude)",
            3: "3D Fix (GOOD)",
            4: "DGPS (better)",
            5: "RTK Float (precise)",
            6: "RTK Fixed (best)",
        }

        fix = gps_msg.fix_type
        sats = gps_msg.satellites_visible
        hdop = gps_msg.eph / 100.0 if gps_msg.eph < 10000 else 9999

        print(f"  Fix type:   {fix} — {fix_names.get(fix, f'Unknown ({fix})')}")
        print(f"  Satellites: {sats}")
        if hdop < 9999:
            print(f"  HDOP:       {hdop:.1f} ({'good' if hdop < 2 else 'poor' if hdop < 5 else 'very poor'})")

        if fix >= 3:
            lat = gps_msg.lat / 1e7
            lon = gps_msg.lon / 1e7
            print(f"  Position:   ({lat:.7f}, {lon:.7f})")
            print(f"  [PASS] GPS has 3D fix — ready to fly!")
        elif sats > 0:
            print(f"  [WAIT] Seeing {sats} satellites but no fix yet")
            print(f"         Need 4+ satellites for 3D fix")
            print(f"         Go outside, wait 1-3 minutes")
        else:
            print(f"  [WAIT] No satellites yet")
            print(f"         Are you indoors? GPS needs clear sky view")
            print(f"         Take outside, wait 2-4 minutes (cold start)")

    # ── Step 6: Live tracking ──
    step += 1
    print(f"\n  STEP {step}: LIVE GPS TRACKING")
    print(f"  {'-'*50}")

    if gps_msg is None:
        print(f"  [SKIP] No GPS data")
        mav.close()
        return

    if gps_msg.fix_type >= 3:
        print(f"  Already have 3D fix! Monitoring for 10 seconds...")
        track_seconds = 10
    else:
        print(f"  Waiting for fix... (Ctrl+C to stop)")
        print(f"  Take GPS outside with clear sky view if indoors")
        track_seconds = 999999

    print()
    print(f"  {'Time':<7} {'Fix':<14} {'Sats':<6} {'HDOP':<7} {'Lat':<14} {'Lon':<14} {'LED':<15}")
    print(f"  {'-'*80}")

    fix_names_short = {0: "No GPS", 1: "No Fix", 2: "2D Fix", 3: "3D Fix",
                       4: "DGPS", 5: "RTK Float", 6: "RTK Fixed"}

    got_fix = False
    best_sats = 0
    start = time.time()

    try:
        while time.time() - start < track_seconds:
            # Drain all messages
            while mav.recv_msg() is not None:
                pass

            gps_raw = mav.messages.get('GPS_RAW_INT')
            if not gps_raw:
                time.sleep(1)
                continue

            fix = gps_raw.fix_type
            sats = gps_raw.satellites_visible
            hdop = gps_raw.eph / 100.0 if gps_raw.eph < 10000 else 9999
            lat = gps_raw.lat / 1e7 if gps_raw.lat != 0 else 0.0
            lon = gps_raw.lon / 1e7 if gps_raw.lon != 0 else 0.0

            best_sats = max(best_sats, sats)

            elapsed = int(time.time() - start)
            time_str = f"{elapsed // 60}:{elapsed % 60:02d}"
            fix_str = fix_names_short.get(fix, f"Type {fix}")
            lat_str = f"{lat:.7f}" if lat != 0 else "---"
            lon_str = f"{lon:.7f}" if lon != 0 else "---"
            hdop_str = f"{hdop:.1f}" if hdop < 9999 else "---"

            # LED prediction based on ArduPilot state
            if fix >= 3:
                led = "GREEN (lock!)"
            else:
                led = "BLUE (no lock)"

            marker = ""
            if fix >= 3 and not got_fix:
                got_fix = True
                marker = " << FIX!"

            print(f"  {time_str:<7} {fix_str:<14} {sats:<6} {hdop_str:<7} {lat_str:<14} {lon_str:<14} {led}{marker}")

            time.sleep(1)

    except KeyboardInterrupt:
        pass

    mav.close()

    # ── Summary ──
    print(f"\n  {'='*60}")
    print(f"  GPS HEALTH SUMMARY")
    print(f"  {'='*60}")

    elapsed = int(time.time() - start)
    print(f"  Time tracked: {elapsed}s")
    print(f"  Best sats:    {best_sats}")

    if got_fix:
        print(f"  Result:       PASS — got 3D fix")
        print(f"  GPS is healthy and ready for flight.")
    elif gps_msg is not None and best_sats > 0:
        print(f"  Result:       PARTIAL — GPS talking, saw {best_sats} sats, no fix")
        print(f"  Go outside with clear sky and wait longer.")
    elif gps_msg is not None:
        print(f"  Result:       PARTIAL — GPS connected, 0 satellites")
        print(f"  Hardware OK but needs sky view (go outside).")
    else:
        print(f"  Result:       FAIL — GPS not communicating")
        print(f"  Check wiring and CAN parameters.")

    print()
    print(f"  LED Quick Reference:")
    print(f"    Flashing BLUE    = disarmed, no GPS lock (normal indoors)")
    print(f"    Flashing GREEN   = disarmed, GPS lock acquired (ready!)")
    print(f"    Double YELLOW    = pre-arm check failing")
    print(f"    Flashing YELLOW  = failsafe (RC off)")
    print()


if __name__ == "__main__":
    main()
