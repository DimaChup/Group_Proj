#!/usr/bin/env python3
"""
GPS Diagnostics — focused purely on GPS signal.

Shows:
  - GPS fix type, satellite count, HDOP
  - GPS hardware type (parameter check)
  - Whether GPS_RAW_INT messages are arriving at all
  - Live updating table until you get a fix or Ctrl+C

Usage:
    python tests2/gps_test.py
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymavlink import mavutil
import config

conn_str = config.CONNECTION_STR
print(f"[CUBE] Connecting: {conn_str}")
mav = mavutil.mavlink_connection(conn_str)
print("[CUBE] Waiting for heartbeat...")
hb = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=10)
if not hb:
    print("[FAIL] No heartbeat. Is mavproxy running?")
    sys.exit(1)
print(f"[CUBE] Connected to system {mav.target_system}")

# Request all streams at high rate
mav.mav.request_data_stream_send(
    mav.target_system, mav.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
time.sleep(0.3)

# ── Check GPS parameters ──
print(f"\n  Checking GPS parameters...")
params_to_check = [b'GPS_TYPE', b'GPS_AUTO_CONFIG', b'GPS_GNSS_MODE']
for pname in params_to_check:
    mav.mav.param_request_read_send(
        mav.target_system, mav.target_component, pname, -1)
    msg = mav.recv_match(type='PARAM_VALUE', blocking=True, timeout=2)
    if msg:
        print(f"    {msg.param_id.rstrip(chr(0)):<20} = {int(msg.param_value)}")
    else:
        print(f"    {pname.decode():<20} = (no response)")

# ── Check if GPS_RAW_INT arrives at all ──
print(f"\n  Checking if GPS data arrives...")
gps_msg = mav.recv_match(type='GPS_RAW_INT', blocking=True, timeout=5)
if gps_msg is None:
    print(f"  \033[91m[FAIL] No GPS_RAW_INT messages at all!\033[0m")
    print(f"  This means:")
    print(f"    - GPS module might not be connected")
    print(f"    - GPS_TYPE parameter might be wrong (should be 1 for u-blox/Here3+)")
    print(f"    - Try: in Mission Planner, check GPS_TYPE = 1")
    sys.exit(1)
else:
    sats = gps_msg.satellites_visible
    fix = gps_msg.fix_type
    print(f"  [OK] GPS data flowing — fix={fix}, sats={sats}")

fix_names = {0: "No GPS", 1: "No Fix", 2: "2D Fix", 3: "3D Fix",
             4: "DGPS", 5: "RTK Float", 6: "RTK Fixed"}

print(f"\n  Waiting for GPS fix... (antenna facing UP, clear sky)")
print(f"  {'Time':<8} {'Fix':<12} {'Sats':<6} {'Lat':<14} {'Lon':<14} {'Alt(m)':<8} {'HDOP':<8} {'VDOP':<8}")
print(f"  {'-'*82}")

got_fix = False
best_sats = 0
start = time.time()

try:
    while True:
        # Drain all messages
        while True:
            msg = mav.recv_msg()
            if msg is None:
                break

        gps_raw = mav.messages.get('GPS_RAW_INT')
        gps_pos = mav.messages.get('GLOBAL_POSITION_INT')

        if gps_raw:
            fix = gps_raw.fix_type
            fix_str = fix_names.get(fix, f"Type {fix}")
            sats = gps_raw.satellites_visible
            hdop = gps_raw.eph / 100.0 if gps_raw.eph < 10000 else 9999
            vdop = gps_raw.epv / 100.0 if gps_raw.epv < 10000 else 9999
            lat = gps_raw.lat / 1e7 if gps_raw.lat != 0 else 0.0
            lon = gps_raw.lon / 1e7 if gps_raw.lon != 0 else 0.0
        else:
            fix = 0
            fix_str = "No data"
            sats = 0
            hdop = 9999
            vdop = 9999
            lat = 0.0
            lon = 0.0

        best_sats = max(best_sats, sats)

        if gps_pos:
            alt = gps_pos.relative_alt / 1000.0
        else:
            alt = 0.0

        elapsed = int(time.time() - start)
        mins = elapsed // 60
        secs = elapsed % 60
        time_str = f"{mins}:{secs:02d}"

        lat_str = f"{lat:.7f}" if lat != 0 else "---"
        lon_str = f"{lon:.7f}" if lon != 0 else "---"
        hdop_str = f"{hdop:.1f}" if hdop < 9999 else "---"
        vdop_str = f"{vdop:.1f}" if vdop < 9999 else "---"

        if fix >= 3:
            marker = " << 3D FIX"
            if not got_fix:
                got_fix = True
                print(f"  {time_str:<8} {fix_str:<12} {sats:<6} {lat_str:<14} {lon_str:<14} {alt:<8.1f} {hdop_str:<8} {vdop_str:<8}{marker}")
                print(f"\n  \033[92m*** GOT 3D FIX! GPS is working. ***\033[0m\n")
            else:
                print(f"  {time_str:<8} {fix_str:<12} {sats:<6} {lat_str:<14} {lon_str:<14} {alt:<8.1f} {hdop_str:<8} {vdop_str:<8}{marker}")
        else:
            print(f"  {time_str:<8} {fix_str:<12} {sats:<6} {lat_str:<14} {lon_str:<14} {alt:<8.1f} {hdop_str:<8} {vdop_str:<8}")

        time.sleep(1)

except KeyboardInterrupt:
    elapsed = int(time.time() - start)
    mav.close()

    print(f"\n\n{'=' * 60}")
    print(f"  GPS DIAGNOSTIC RESULTS")
    print(f"{'=' * 60}")
    print(f"  Time waited:  {elapsed}s")
    print(f"  Best sats:    {best_sats}")

    if got_fix:
        print(f"  Result:       \033[92mPASS — got 3D fix\033[0m")
        print(f"  Position:     ({lat:.7f}, {lon:.7f})")
        print(f"  HDOP:         {hdop_str}")
    else:
        print(f"  Result:       \033[91mNO FIX\033[0m")
        print()
        if best_sats == 0:
            print(f"  0 satellites seen. Possible causes:")
            print(f"    1. GPS antenna not connected to Cube")
            print(f"    2. GPS antenna cable damaged")
            print(f"    3. Indoors (GPS needs sky view)")
            print(f"    4. GPS_TYPE wrong (check Mission Planner)")
        elif best_sats < 4:
            print(f"  Saw {best_sats} satellites but couldn't lock. Causes:")
            print(f"    1. Not enough sky view (need 4+ sats for 3D fix)")
            print(f"    2. Near buildings/trees blocking signals")
            print(f"    3. Cold start — wait longer (up to 5 min)")
        else:
            print(f"  Saw {best_sats} satellites but no fix. Causes:")
            print(f"    1. Interference from nearby electronics")
            print(f"    2. GPS module needs longer to converge")
            print(f"    3. Try power cycling the Cube")

    print()
