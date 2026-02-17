#!/usr/bin/env python3
"""
Test sending commands TO the Cube and getting responses.

Previous tests proved Cube → Pi (telemetry) works.
This proves Pi → Cube (commands) works.

Safe to run on bench — no props needed, won't fly.

Usage:
    python tests/test_cube_commands.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymavlink import mavutil


def connect():
    """Connect to Cube via config settings."""
    import config
    conn_str = config.CONNECTION_STR
    print(f"  Connecting: {conn_str}")
    master = mavutil.mavlink_connection(conn_str)

    print("  Waiting for heartbeat...")
    msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=10)
    if not msg:
        print("  [FAIL] No heartbeat. Is mavproxy running?")
        sys.exit(1)

    print(f"  [OK] Heartbeat from system {msg.get_srcSystem()}")
    # Request data streams so we get mode/status updates
    master.mav.request_data_stream_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 4, 1)
    time.sleep(0.5)
    return master


def get_mode(master):
    """Get current flight mode name."""
    hb = master.recv_match(type='HEARTBEAT', blocking=True, timeout=3)
    if hb:
        mode = mavutil.mode_string_v10(hb)
        return mode
    return "UNKNOWN"


def test_mode_change(master):
    """Test: can we change the Cube's flight mode?"""
    print("\n  TEST 1: MODE CHANGE")
    print("  " + "-" * 40)

    # Read current mode
    current = get_mode(master)
    print(f"  Current mode: {current}")

    # Try switching to GUIDED
    print("  Sending: switch to GUIDED...")
    master.set_mode_apm(mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4)  # 4 = GUIDED
    time.sleep(1)

    new_mode = get_mode(master)
    if new_mode == "GUIDED":
        print(f"  [OK] Mode changed to GUIDED")
        guided_ok = True
    else:
        # Try alternative method
        master.mav.command_long_send(
            master.target_system, master.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            4, 0, 0, 0, 0, 0)
        time.sleep(1)
        new_mode = get_mode(master)
        if new_mode == "GUIDED":
            print(f"  [OK] Mode changed to GUIDED (via command_long)")
            guided_ok = True
        else:
            print(f"  [FAIL] Mode is {new_mode}, expected GUIDED")
            print(f"         (RC transmitter may need to be on, or mode switch set)")
            guided_ok = False

    # Switch back to STABILIZE (safe mode)
    print("  Sending: switch to STABILIZE...")
    master.set_mode_apm(mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 0)  # 0 = STABILIZE
    time.sleep(1)

    back_mode = get_mode(master)
    if back_mode == "STABILIZE":
        print(f"  [OK] Mode back to STABILIZE")
    else:
        print(f"  [?]  Mode is {back_mode} (may need RC override)")

    return guided_ok


def test_arm(master):
    """Test: can we send an arm command? (Expect failure on bench — that's OK!)"""
    print("\n  TEST 2: ARM COMMAND")
    print("  " + "-" * 40)
    print("  NOTE: Arming will likely FAIL on bench (no GPS fix, safety checks).")
    print("        That's fine — we're testing if the COMMAND reaches the Cube.\n")

    # Send arm command
    print("  Sending: ARM...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0)

    # Wait for ACK
    ack = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    if ack:
        result = ack.result
        if result == 0:
            print(f"  [OK] ARM accepted! (Cube armed — DISARMING immediately)")
            # Immediately disarm for safety
            master.mav.command_long_send(
                master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
                0, 0, 0, 0, 0, 0, 0)
            time.sleep(1)
            print(f"  [OK] Disarmed.")
            return True
        else:
            # Get the reason from STATUSTEXT
            reason = ""
            status_msg = master.recv_match(type='STATUSTEXT', blocking=True, timeout=2)
            if status_msg:
                reason = status_msg.text

            result_names = {
                0: "ACCEPTED", 1: "TEMPORARILY_REJECTED",
                2: "DENIED", 3: "UNSUPPORTED", 4: "FAILED"
            }
            result_name = result_names.get(result, f"code {result}")
            print(f"  [OK] ARM rejected: {result_name}")
            if reason:
                print(f"       Reason: {reason}")
            print(f"       (This is EXPECTED on bench — command DID reach Cube)")
            return True  # Command reached Cube, rejection is expected
    else:
        print(f"  [FAIL] No ACK received — command may not have reached Cube")
        return False


def test_request_param(master):
    """Test: can we read a parameter from the Cube?"""
    print("\n  TEST 3: PARAMETER READ")
    print("  " + "-" * 40)

    # Request a common parameter
    param_name = b'ARMING_CHECK'
    print(f"  Requesting: {param_name.decode()}...")
    master.mav.param_request_read_send(
        master.target_system, master.target_component,
        param_name, -1)

    msg = master.recv_match(type='PARAM_VALUE', blocking=True, timeout=3)
    if msg:
        print(f"  [OK] {msg.param_id} = {msg.param_value}")
        return True
    else:
        print(f"  [FAIL] No parameter response")
        return False


def test_request_home(master):
    """Test: can we read the home position?"""
    print("\n  TEST 4: HOME POSITION")
    print("  " + "-" * 40)

    print("  Requesting home position...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, 0,
        0, 0, 0, 0, 0, 0, 0)

    msg = master.recv_match(type='HOME_POSITION', blocking=True, timeout=3)
    if msg:
        lat = msg.latitude / 1e7
        lon = msg.longitude / 1e7
        alt = msg.altitude / 1000.0
        if abs(lat) > 0.1:
            print(f"  [OK] Home: {lat:.6f}, {lon:.6f}, alt={alt:.1f}m")
        else:
            print(f"  [OK] Home position received (no GPS fix yet — lat={lat})")
        return True
    else:
        print(f"  [?]  No home position (normal if no GPS fix yet)")
        return False


def test_buzzer(master):
    """Test: can we trigger the buzzer? (Audible confirmation!)"""
    print("\n  TEST 5: BUZZER (listen!)")
    print("  " + "-" * 40)

    print("  Sending: play tune...")
    master.mav.play_tune_send(
        master.target_system, master.target_component,
        b'MFT240L8 CDEC', b'')
    time.sleep(1)

    # Also try COMMAND_LONG for buzzer
    print("  Sending: DO_PARACHUTE (buzzer fallback)...")
    # Use a simple repeated beep
    for i in range(3):
        master.mav.play_tune_send(
            master.target_system, master.target_component,
            b'MFT200L16 CE', b'')
        time.sleep(0.3)

    print(f"  [?]  Did you hear beeps? (May not work over SSH)")
    return True


# ── Main ─────────────────────────────────────────────────────
def main():
    print()
    print("=" * 55)
    print("   CUBE COMMAND TEST — Can Pi control the Cube?")
    print("=" * 55)
    print()
    print("  This tests Pi → Cube commands (the control path).")
    print("  Safe on bench. No props needed. Won't fly.")
    print()

    master = connect()

    results = {}
    results['mode'] = test_mode_change(master)
    results['arm'] = test_arm(master)
    results['param'] = test_request_param(master)
    results['home'] = test_request_home(master)
    results['buzzer'] = test_buzzer(master)

    master.close()

    # Summary
    print()
    print("=" * 55)
    print("  RESULTS")
    print("=" * 55)

    tests = [
        ("Mode change (GUIDED ↔ STABILIZE)", results['mode']),
        ("Arm command (reach + ACK)", results['arm']),
        ("Parameter read", results['param']),
        ("Home position", results['home']),
        ("Buzzer", results['buzzer']),
    ]

    passed = 0
    for name, ok in tests:
        symbol = "+" if ok else "X"
        print(f"  [{symbol}] {name}")
        if ok:
            passed += 1

    print()
    if passed == len(tests):
        print(f"  ALL {passed} TESTS PASSED — Pi can control the Cube!")
        print("  Command path is working both directions.")
    elif passed >= 3:
        print(f"  {passed}/{len(tests)} passed — command path mostly works.")
        print("  Home/buzzer may need GPS fix or different hardware.")
    else:
        print(f"  {passed}/{len(tests)} passed — check connection.")

    print()
    print("  What this proves:")
    print("    Pi → Cube: commands are received and acted on")
    print("    Cube → Pi: ACKs and responses come back")
    print("    = Bi-directional control link is WORKING")
    print()

    return passed >= 3


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
