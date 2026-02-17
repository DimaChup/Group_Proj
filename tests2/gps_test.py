#!/usr/bin/env python3
"""
GPS Lock Test — wait for satellite fix and show live GPS status.

Take the drone outside or near a window and run this.
It will keep printing GPS status until you get a fix or press Ctrl+C.

Requires mavproxy running in another terminal.

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
mav.wait_heartbeat(timeout=10)
print(f"[CUBE] Connected to system {mav.target_system}")

# Request streams
try:
    mav.mav.request_data_stream_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1
    )
except Exception:
    pass

fix_names = {0: "No GPS", 1: "No Fix", 2: "2D Fix", 3: "3D Fix",
             4: "DGPS", 5: "RTK Float", 6: "RTK Fixed"}

print(f"\nWaiting for GPS fix... (take drone outside, antenna facing UP)")
print(f"{'Time':<10} {'Fix':<12} {'Sats':<6} {'Lat':<14} {'Lon':<14} {'Alt(m)':<10} {'HDOP':<8}")
print("-" * 74)

got_fix = False
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
            lat_raw = gps_raw.lat / 1e7 if gps_raw.lat != 0 else 0.0
            lon_raw = gps_raw.lon / 1e7 if gps_raw.lon != 0 else 0.0
        else:
            fix = 0
            fix_str = "No data"
            sats = 0
            hdop = 9999
            lat_raw = 0.0
            lon_raw = 0.0

        # Use GLOBAL_POSITION_INT for altitude (more reliable)
        if gps_pos:
            alt = gps_pos.relative_alt / 1000.0
        else:
            alt = 0.0

        elapsed = int(time.time() - start)
        mins = elapsed // 60
        secs = elapsed % 60
        time_str = f"{mins}:{secs:02d}"

        lat_str = f"{lat_raw:.7f}" if lat_raw != 0 else "---"
        lon_str = f"{lon_raw:.7f}" if lon_raw != 0 else "---"
        hdop_str = f"{hdop:.1f}" if hdop < 9999 else "---"

        # Color-code the status in terminal
        if fix >= 3:
            status = f"  {time_str:<10} {fix_str:<12} {sats:<6} {lat_str:<14} {lon_str:<14} {alt:<10.1f} {hdop_str:<8} <<"
            if not got_fix:
                got_fix = True
                print(status)
                print(f"\n  *** GOT 3D FIX! GPS is working. ***\n")
            else:
                print(status)
        else:
            print(f"  {time_str:<10} {fix_str:<12} {sats:<6} {lat_str:<14} {lon_str:<14} {alt:<10.1f} {hdop_str:<8}")

        time.sleep(1)

except KeyboardInterrupt:
    elapsed = int(time.time() - start)
    print(f"\n\n{'=' * 50}")
    print(f"  GPS TEST RESULTS")
    print(f"{'=' * 50}")
    if got_fix:
        print(f"  Result:   PASS — got 3D fix")
        print(f"  Sats:     {sats}")
        print(f"  Position: ({lat_raw:.7f}, {lon_raw:.7f})")
        print(f"  HDOP:     {hdop_str}")
    else:
        print(f"  Result:   NO FIX after {elapsed}s")
        print(f"  Sats:     {sats}")
        print(f"  Check:")
        print(f"    - Is the GPS antenna connected to the Cube?")
        print(f"    - Is the antenna facing UP with clear sky?")
        print(f"    - First fix can take 1-3 minutes (cold start)")
        print(f"    - Try again outside, away from buildings")
    print()
