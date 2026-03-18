#!/usr/bin/env python3
"""
test_cube.py — Cube Flight Controller Connection Test

WHAT:    Connects to the Cube flight controller via serial or TCP (auto-detected
         from config.py or command-line args). Waits for MAVLink heartbeat, then
         requests data streams and listens for GPS, attitude, battery, and status
         messages for 5 seconds. Prints a summary of what telemetry was received.
WHY:     Verifies the MAVLink communication path works end-to-end before running
         flight scripts. On laptop, tests TCP to SITL/Mission Planner. On Pi,
         tests serial to Cube via mavproxy UDP bridge. Catches baud rate
         mismatches, wiring issues, and firewall blocks.
WHEN:    After wiring Cube to Pi. After starting SITL. Before any flight test.
         When MAVLink connection seems broken.
WHERE:   Laptop only (also works on Pi but primarily a dev tool).
ENV:     "venv" (needs pymavlink and config.py)
MODELS:  None (no AI inference).
RISK:    None — read-only telemetry, no commands sent.

USAGE:
    python tests/laptop/test_cube.py                          # auto from config.py
    python tests/laptop/test_cube.py tcp:127.0.0.1:5762       # explicit TCP
    python tests/laptop/test_cube.py /dev/ttyAMA0 921600      # explicit serial

FLAGS:
    [connection_string]   Optional: TCP or serial path (default: from config.py)
    [baud_rate]           Optional: baud rate for serial (default: from config.py)

OUTPUT:
    Console: connection status, heartbeat, GPS coords, attitude (roll/pitch/yaw),
    battery voltage/percentage, status text. Summary table of OK/MISSING checks.
    Exit code: 0 if all telemetry received, 1 if any missing.

BEST PRACTICES:
    - On laptop: start SITL first (Mission Planner or mavproxy)
    - On Pi: start mavproxy first, then run this test
    - If heartbeat fails, check baud rate (57600, 115200, 921600)
    - GPS missing is normal indoors (no satellite fix)

DEPENDENCIES:
    pymavlink, config.py
"""
import sys
import os
import time
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

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

    # 2. Wait for heartbeat (use recv_match loop for Python 3.13 compatibility)
    print("  Waiting for heartbeat...")
    hb = None
    start_hb = time.time()
    while time.time() - start_hb < 10:
        try:
            msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=1)
            if msg:
                hb = msg
                break
        except Exception:
            continue
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
