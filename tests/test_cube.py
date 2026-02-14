#!/usr/bin/env python3
"""
Test connection to Cube flight controller.
Checks serial/TCP link, heartbeat, GPS, attitude, and battery.

Usage: python tests/test_cube.py
       python tests/test_cube.py /dev/ttyAMA0 921600
       python tests/test_cube.py tcp:127.0.0.1:5762
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymavlink import mavutil

def test_cube(conn_str=None, baud=None):
    print("=" * 45)
    print("       CUBE CONNECTION TEST")
    print("=" * 45)

    # Get connection from config if not provided
    if conn_str is None:
        import config
        conn_str = config.CONNECTION_STR
        baud = config.BAUD_RATE
    if baud is None:
        baud = 57600

    is_serial = conn_str.startswith("/dev/")
    baud_str = f" (baud={baud})" if is_serial else ""
    print(f"\n  Connecting: {conn_str}{baud_str}")

    # 1. Establish connection
    try:
        if is_serial:
            master = mavutil.mavlink_connection(conn_str, baud=baud)
        else:
            master = mavutil.mavlink_connection(conn_str)
    except Exception as e:
        print(f"  [FAIL] Could not open connection: {e}")
        if is_serial:
            print("\n  Troubleshooting:")
            print(f"    - Does {conn_str} exist? Check wiring.")
            print(f"    - Try: ls -la {conn_str}")
            print(f"    - Wrong baud? Try 57600, 115200, or 921600")
        else:
            print("\n  Troubleshooting:")
            print("    - Is Mission Planner / SITL running?")
            print("    - Check firewall settings")
        return False

    # 2. Wait for heartbeat
    print("  Waiting for heartbeat...")
    hb = master.wait_heartbeat(timeout=10)
    if not hb:
        print(f"  [FAIL] No heartbeat received after 10 seconds.")
        if is_serial:
            print(f"         Wrong baud rate? (tried {baud})")
        master.close()
        return False

    sys_id = hb.get_srcSystem()
    autopilot = hb.autopilot
    mav_type = hb.type
    print(f"  [OK]   Heartbeat from system {sys_id}")

    # 3. Request data streams
    print("  Requesting data streams...")
    master.mav.request_data_stream_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 4, 1)

    # 4. Listen for telemetry (5 seconds)
    print("  Listening for telemetry (5 sec)...\n")
    got_gps = False
    got_attitude = False
    got_battery = False
    got_status = False

    start = time.time()
    while time.time() - start < 5:
        msg = master.recv_match(blocking=True, timeout=1)
        if msg is None:
            continue

        msg_type = msg.get_type()

        if msg_type == 'GLOBAL_POSITION_INT' and not got_gps:
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            alt = msg.relative_alt / 1000.0
            print(f"  [OK]   GPS:      lat={lat:.6f}  lon={lon:.6f}  alt={alt:.1f}m")
            got_gps = True

        elif msg_type == 'ATTITUDE' and not got_attitude:
            roll = msg.roll * 57.2958  # rad to deg
            pitch = msg.pitch * 57.2958
            yaw = msg.yaw * 57.2958
            print(f"  [OK]   ATTITUDE: roll={roll:.1f}  pitch={pitch:.1f}  yaw={yaw:.1f}")
            got_attitude = True

        elif msg_type == 'SYS_STATUS' and not got_battery:
            voltage = msg.voltage_battery / 1000.0 if msg.voltage_battery > 0 else 0
            remaining = msg.battery_remaining
            if voltage > 0:
                print(f"  [OK]   BATTERY:  {voltage:.1f}V  ({remaining}% remaining)")
            else:
                print(f"  [OK]   BATTERY:  (no battery data - normal in SITL)")
            got_battery = True

        elif msg_type == 'STATUSTEXT' and not got_status:
            print(f"  [OK]   STATUS:   {msg.text}")
            got_status = True

        if got_gps and got_attitude and got_battery:
            break

    # 5. Summary
    master.close()
    print(f"\n  {'─' * 40}")
    checks = [("Heartbeat", True), ("GPS", got_gps), ("Attitude", got_attitude), ("Battery", got_battery)]
    all_ok = True
    for name, ok in checks:
        status = "OK" if ok else "MISSING"
        if not ok:
            all_ok = False
        print(f"  [{status:7s}] {name}")

    if not got_gps:
        print("\n  GPS missing: wait for satellite fix or check GPS module")
    if not got_attitude:
        print("\n  Attitude missing: IMU may not be calibrated")

    print()
    return all_ok

if __name__ == "__main__":
    conn = None
    baud = None
    if len(sys.argv) >= 2:
        conn = sys.argv[1]
    if len(sys.argv) >= 3:
        baud = int(sys.argv[2])
    success = test_cube(conn, baud)
    sys.exit(0 if success else 1)
