#!/usr/bin/env python3
"""
Live Cube Monitor — see EVERYTHING the Cube is sending in real-time.

Shows:
  - GPS status (fix type, satellites, HDOP, position)
  - Attitude (roll, pitch, yaw)
  - Battery (voltage, current, remaining)
  - RC channels (is transmitter talking?)
  - System status + mode
  - Vibration levels
  - EKF status
  - All message rates

Updates continuously. Great for diagnosing GPS issues.

Usage:
    python tests2/cube_monitor.py
    python tests2/cube_monitor.py --raw     (show ALL raw messages)
"""
import sys
import os
import time
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymavlink import mavutil
import config

RAW_MODE = "--raw" in sys.argv


def connect():
    conn_str = config.CONNECTION_STR
    print(f"[CUBE] Connecting: {conn_str}")
    mav = mavutil.mavlink_connection(conn_str)
    print("[CUBE] Waiting for heartbeat...")
    hb = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=10)
    if not hb:
        print("[FAIL] No heartbeat. Is mavproxy running?")
        sys.exit(1)
    print(f"[CUBE] Connected — system {mav.target_system}")

    # Request ALL streams at high rate for diagnostics
    mav.mav.request_data_stream_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
    time.sleep(0.5)
    return mav


def main():
    print()
    print("=" * 65)
    print("   LIVE CUBE MONITOR — All readings in real-time")
    print("   Press Ctrl+C to stop")
    print("=" * 65)
    print()

    mav = connect()

    # Data storage
    gps_raw = None
    gps_pos = None
    attitude = None
    battery = None
    vfr_hud = None
    rc_channels = None
    heartbeat = None
    vibration = None
    ekf = None
    power = None
    meminfo = None

    # Message rate tracking
    msg_counts = {}
    rate_start = time.time()
    msg_rates = {}

    fix_names = {0: "No GPS", 1: "No Fix", 2: "2D Fix", 3: "3D Fix",
                 4: "DGPS", 5: "RTK Float", 6: "RTK Fixed"}

    mode_map = {0: "STABILIZE", 2: "ALT_HOLD", 3: "AUTO", 4: "GUIDED",
                5: "LOITER", 6: "RTL", 9: "LAND", 16: "POSHOLD"}

    update_count = 0
    start_time = time.time()

    try:
        while True:
            # Drain all available messages
            while True:
                msg = mav.recv_match(blocking=False)
                if msg is None:
                    break

                mtype = msg.get_type()
                msg_counts[mtype] = msg_counts.get(mtype, 0) + 1

                if mtype == "GPS_RAW_INT":
                    gps_raw = msg
                elif mtype == "GLOBAL_POSITION_INT":
                    gps_pos = msg
                elif mtype == "ATTITUDE":
                    attitude = msg
                elif mtype == "SYS_STATUS":
                    battery = msg
                elif mtype == "VFR_HUD":
                    vfr_hud = msg
                elif mtype == "RC_CHANNELS":
                    rc_channels = msg
                elif mtype == "HEARTBEAT":
                    heartbeat = msg
                elif mtype == "VIBRATION":
                    vibration = msg
                elif mtype == "EKF_STATUS_REPORT":
                    ekf = msg
                elif mtype == "POWER_STATUS":
                    power = msg
                elif mtype == "MEMINFO":
                    meminfo = msg

            # Calculate rates every 2 seconds
            now = time.time()
            if now - rate_start >= 2.0:
                elapsed = now - rate_start
                msg_rates = {k: v / elapsed for k, v in msg_counts.items()}
                msg_counts = {}
                rate_start = now

            # Update display every 0.5 seconds
            update_count += 1
            if update_count % 10 != 0:
                time.sleep(0.05)
                continue

            elapsed = int(now - start_time)
            mins = elapsed // 60
            secs = elapsed % 60

            # Clear screen (works on Pi terminal)
            print("\033[2J\033[H", end="")

            print(f"  LIVE CUBE MONITOR  |  {mins}:{secs:02d}  |  Ctrl+C to stop")
            print("=" * 65)

            # ── GPS ──
            print(f"\n  GPS:")
            if gps_raw:
                fix = gps_raw.fix_type
                fix_str = fix_names.get(fix, f"Type {fix}")
                sats = gps_raw.satellites_visible
                hdop = gps_raw.eph / 100.0 if gps_raw.eph < 10000 else 9999
                vdop = gps_raw.epv / 100.0 if gps_raw.epv < 10000 else 9999
                lat = gps_raw.lat / 1e7
                lon = gps_raw.lon / 1e7
                alt_msl = gps_raw.alt / 1000.0

                fix_color = "\033[92m" if fix >= 3 else "\033[91m" if fix <= 1 else "\033[93m"
                reset = "\033[0m"

                print(f"    Fix:        {fix_color}{fix_str}{reset}")
                print(f"    Satellites: {fix_color}{sats}{reset}")
                print(f"    HDOP:       {hdop:.1f}  (< 2.0 = good)")
                print(f"    VDOP:       {vdop:.1f}")
                if lat != 0:
                    print(f"    Lat:        {lat:.7f}")
                    print(f"    Lon:        {lon:.7f}")
                    print(f"    Alt (MSL):  {alt_msl:.1f}m")
                else:
                    print(f"    Position:   waiting for fix...")
            else:
                print(f"    \033[91mNo GPS data received\033[0m")

            if gps_pos:
                rel_alt = gps_pos.relative_alt / 1000.0
                print(f"    Alt (rel):  {rel_alt:.1f}m")

            # ── ATTITUDE ──
            print(f"\n  ATTITUDE:")
            if attitude:
                roll = math.degrees(attitude.roll)
                pitch = math.degrees(attitude.pitch)
                yaw = math.degrees(attitude.yaw)
                print(f"    Roll:  {roll:>7.1f}°")
                print(f"    Pitch: {pitch:>7.1f}°")
                print(f"    Yaw:   {yaw:>7.1f}°")
            else:
                print(f"    No attitude data")

            # ── BATTERY ──
            print(f"\n  BATTERY:")
            if battery:
                voltage = battery.voltage_battery / 1000.0
                current = battery.current_battery / 100.0 if battery.current_battery >= 0 else 0
                remaining = battery.battery_remaining
                if voltage > 0:
                    print(f"    Voltage:    {voltage:.2f}V")
                    print(f"    Current:    {current:.1f}A")
                    if remaining >= 0:
                        print(f"    Remaining:  {remaining}%")
                else:
                    print(f"    No battery (USB powered?)")
            else:
                print(f"    No battery data")

            # ── VFR HUD ──
            print(f"\n  FLIGHT DATA:")
            if vfr_hud:
                print(f"    Airspeed:   {vfr_hud.airspeed:.1f} m/s")
                print(f"    Groundspd:  {vfr_hud.groundspeed:.1f} m/s")
                print(f"    Heading:    {vfr_hud.heading}°")
                print(f"    Throttle:   {vfr_hud.throttle}%")
                print(f"    Climb:      {vfr_hud.climb:.1f} m/s")
            else:
                print(f"    No flight data")

            # ── RC ──
            print(f"\n  RC TRANSMITTER:")
            if rc_channels:
                ch_count = rc_channels.chancount
                ch1 = rc_channels.chan1_raw  # roll
                ch2 = rc_channels.chan2_raw  # pitch
                ch3 = rc_channels.chan3_raw  # throttle
                ch4 = rc_channels.chan4_raw  # yaw
                ch5 = rc_channels.chan5_raw  # mode switch
                rssi = rc_channels.rssi

                if ch3 > 900:
                    print(f"    Channels:   {ch_count}")
                    print(f"    Roll:       {ch1}  Pitch: {ch2}  Thr: {ch3}  Yaw: {ch4}")
                    print(f"    Ch5 (mode): {ch5}")
                    print(f"    RSSI:       {rssi}")
                else:
                    print(f"    \033[91m{ch_count}ch but throttle={ch3} — RC off?\033[0m")
            else:
                print(f"    No RC data")

            # ── MODE ──
            print(f"\n  SYSTEM:")
            if heartbeat:
                custom_mode = heartbeat.custom_mode
                mode_name = mode_map.get(custom_mode, f"MODE_{custom_mode}")
                armed = "ARMED" if heartbeat.base_mode & 128 else "DISARMED"
                armed_color = "\033[91m" if armed == "ARMED" else "\033[92m"
                print(f"    Mode:       {mode_name}")
                print(f"    Status:     {armed_color}{armed}\033[0m")
            else:
                print(f"    No heartbeat")

            # ── VIBRATION ──
            if vibration:
                print(f"\n  VIBRATION:")
                print(f"    X: {vibration.vibration_x:.1f}  Y: {vibration.vibration_y:.1f}  Z: {vibration.vibration_z:.1f}")
                clip0 = vibration.clipping_0
                clip1 = vibration.clipping_1
                clip2 = vibration.clipping_2
                if clip0 > 0 or clip1 > 0 or clip2 > 0:
                    print(f"    \033[91mCLIPPING: {clip0}/{clip1}/{clip2}\033[0m")

            # ── EKF ──
            if ekf:
                print(f"\n  EKF STATUS:")
                print(f"    Vel:   {ekf.velocity_variance:.3f}  Pos(h): {ekf.pos_horiz_variance:.3f}  "
                      f"Pos(v): {ekf.pos_vert_variance:.3f}")
                print(f"    Compass: {ekf.compass_variance:.3f}  Terrain: {ekf.terrain_alt_variance:.3f}")

            # ── MESSAGE RATES ──
            print(f"\n  MESSAGE RATES (msg/sec):")
            if msg_rates:
                # Show top messages by rate
                sorted_rates = sorted(msg_rates.items(), key=lambda x: -x[1])
                for mtype, rate in sorted_rates[:12]:
                    bar = "█" * min(40, int(rate * 2))
                    print(f"    {mtype:<30} {rate:>5.1f}  {bar}")
                total = sum(msg_rates.values())
                print(f"    {'TOTAL':<30} {total:>5.1f}")
            else:
                print(f"    Calculating...")

            # ── RAW MODE ──
            if RAW_MODE:
                print(f"\n  ALL KNOWN MESSAGES:")
                for key in sorted(mav.messages.keys()):
                    if key.startswith("MAV") or key == "BAD_DATA":
                        continue
                    msg = mav.messages[key]
                    fields = msg.get_fieldnames()
                    vals = ", ".join(f"{f}={getattr(msg, f)}" for f in fields[:6])
                    print(f"    {key}: {vals}")

            print(f"\n  Tip: --raw flag shows all message fields")

    except KeyboardInterrupt:
        print("\n\nStopped.")
        mav.close()

        # Final GPS summary
        print()
        if gps_raw:
            fix = gps_raw.fix_type
            sats = gps_raw.satellites_visible
            if fix >= 3:
                print(f"  GPS: GOT FIX ({fix_names[fix]}, {sats} sats)")
            else:
                print(f"  GPS: NO FIX ({fix_names.get(fix, '?')}, {sats} sats)")
                print(f"  Troubleshooting:")
                print(f"    - Is GPS antenna connected to Cube? (Here 3+)")
                print(f"    - Is antenna facing UP with clear sky view?")
                print(f"    - Cold start can take 1-3 minutes")
                print(f"    - Try outside, away from buildings/trees")
                print(f"    - Check GPS_TYPE param (should be 1 for u-blox)")
        else:
            print(f"  GPS: NO DATA AT ALL")
            print(f"    - Check GPS module wiring")
            print(f"    - Check GPS_TYPE param in Mission Planner")
        print()


if __name__ == "__main__":
    main()
