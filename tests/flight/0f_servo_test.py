#!/usr/bin/env python3
"""
Servo Release Test — verify payload servo responds to PWM commands.

WHAT:    Sends MAV_CMD_DO_SET_SERVO commands to the payload servo channel and
         cycles through CLOSE, PARTIAL, and FULL positions. Operator confirms
         visually/audibly that the servo moves at each step. Then runs the full
         deploy sequence (3s wait -> partial -> 3s wait -> full -> close).
WHY:     Payload release is never tested standalone before main.py. This script
         isolates the servo channel and verifies the Cube forwards PWM correctly,
         the wiring is right, and the three positions work as expected — before
         any flight code touches it.
WHEN:    After 0a_cube_commands.py (Cube link proven), before 0b_bench_mission.py.
         Run on bench with Cube powered, servo plugged into the AUX rail.
WHERE:   Pi (with Cube connected via mavproxy) or laptop (with SITL).
ENV:     pienv on Pi, or any venv with pymavlink on laptop.
MODELS:  None (no camera or AI used).
RISK:    None — no arming, no mode changes, no motor commands. Only servo PWM
         output on a single AUX channel. Safe on bench with or without props.

USAGE:
    python tests/flight/0f_servo_test.py
    python tests/flight/0f_servo_test.py --auto
    python tests/flight/0f_servo_test.py --channel 10

FLAGS:
    --auto       Skip interactive confirmations (run full sequence unattended)
    --channel N  Override servo channel (default from config.SERVO_CHANNEL)

OUTPUT:
    Terminal output with [OK]/[FAIL] for each position test and the deploy
    sequence. Summary with pass/fail count. Exit code 0 if all tests pass.

BEST PRACTICES:
    - Ensure mavproxy is running before launching this script
    - Watch the servo physically — listen for the click/whir at each position
    - If servo doesn't move, check: channel number matches SERVOx_FUNCTION in
      Mission Planner, AUX rail has power (BEC), servo wiring (signal/V+/GND)
    - Run with --auto for quick regression checks (no user input needed)

DEPENDENCIES:
    pymavlink, config.py (for CONNECTION_STR, SERVO_CHANNEL, SERVO_*_PWM)
"""
import sys
import os
import time
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

from pymavlink import mavutil
import config


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Servo release mechanism test")
    parser.add_argument("--auto", action="store_true",
                        help="Skip interactive confirmations")
    parser.add_argument("--channel", type=int, default=None,
                        help=f"Servo channel (default: config.SERVO_CHANNEL = {config.SERVO_CHANNEL})")
    return parser.parse_args()


def connect():
    """Connect to Cube via config settings."""
    conn_str = config.CONNECTION_STR
    print(f"  Connecting: {conn_str}")
    master = mavutil.mavlink_connection(conn_str)

    print("  Waiting for heartbeat...")
    autopilot_hb = None
    start = time.time()
    while time.time() - start < 10:
        hb = master.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
        if hb and hb.type != mavutil.mavlink.MAV_TYPE_GCS:
            autopilot_hb = hb
            break
    if autopilot_hb is None:
        print("  [FAIL] No heartbeat. Is mavproxy running?")
        sys.exit(1)

    master.target_system = autopilot_hb.get_srcSystem()
    master.target_component = autopilot_hb.get_srcComponent()
    print(f"  [OK] Heartbeat from system {master.target_system}")
    return master


def send_servo(master, channel, pwm):
    """Send MAV_CMD_DO_SET_SERVO and wait for ACK."""
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
        channel, pwm, 0, 0, 0, 0, 0)

    ack = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    if ack and ack.command == mavutil.mavlink.MAV_CMD_DO_SET_SERVO:
        if ack.result == 0:
            return True
        else:
            print(f"  [WARN] ACK result={ack.result} (not ACCEPTED)")
            return False
    else:
        print(f"  [WARN] No ACK received for DO_SET_SERVO")
        return False


def ask_confirmation(prompt, auto_mode):
    """Ask user for y/n confirmation. In auto mode, assume yes."""
    if auto_mode:
        print(f"  {prompt} (--auto: skipped)")
        return True
    try:
        answer = input(f"  {prompt} (y/n): ").strip().lower()
        return answer in ('y', 'yes')
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def test_servo_close(master, channel, auto_mode):
    """Test: send CLOSE PWM and confirm servo moves."""
    print(f"\n  TEST 1: CLOSE POSITION (PWM {config.SERVO_CLOSE_PWM})")
    print("  " + "-" * 40)

    print(f"  Sending: channel {channel} -> {config.SERVO_CLOSE_PWM} PWM")
    ack_ok = send_servo(master, channel, config.SERVO_CLOSE_PWM)

    if not ack_ok:
        print("  [FAIL] Servo command not acknowledged")
        return False

    time.sleep(2)
    confirmed = ask_confirmation("Did servo move to CLOSED position?", auto_mode)
    if confirmed:
        print("  [OK] Servo CLOSE confirmed")
        return True
    else:
        print("  [FAIL] Servo CLOSE not confirmed by operator")
        return False


def test_servo_partial(master, channel, auto_mode):
    """Test: send PARTIAL PWM and confirm servo moves."""
    print(f"\n  TEST 2: PARTIAL RELEASE (PWM {config.SERVO_PARTIAL_PWM})")
    print("  " + "-" * 40)

    print(f"  Sending: channel {channel} -> {config.SERVO_PARTIAL_PWM} PWM")
    ack_ok = send_servo(master, channel, config.SERVO_PARTIAL_PWM)

    if not ack_ok:
        print("  [FAIL] Servo command not acknowledged")
        return False

    time.sleep(2)
    confirmed = ask_confirmation("Did servo move to PARTIAL release?", auto_mode)
    if confirmed:
        print("  [OK] Servo PARTIAL confirmed")
        return True
    else:
        print("  [FAIL] Servo PARTIAL not confirmed by operator")
        return False


def test_servo_full(master, channel, auto_mode):
    """Test: send FULL PWM and confirm servo moves."""
    print(f"\n  TEST 3: FULL RELEASE (PWM {config.SERVO_FULL_PWM})")
    print("  " + "-" * 40)

    print(f"  Sending: channel {channel} -> {config.SERVO_FULL_PWM} PWM")
    ack_ok = send_servo(master, channel, config.SERVO_FULL_PWM)

    if not ack_ok:
        print("  [FAIL] Servo command not acknowledged")
        return False

    time.sleep(2)
    confirmed = ask_confirmation("Did servo move to FULL release?", auto_mode)
    if confirmed:
        print("  [OK] Servo FULL confirmed")
        return True
    else:
        print("  [FAIL] Servo FULL not confirmed by operator")
        return False


def test_servo_sequence(master, channel, auto_mode):
    """Test: run the full 15s deploy sequence (close -> wait -> partial -> wait -> full -> close)."""
    print(f"\n  TEST 4: FULL DEPLOY SEQUENCE")
    print("  " + "-" * 40)
    print("  Sequence: CLOSE -> 3s -> PARTIAL -> 3s -> FULL -> 3s -> CLOSE")
    print()

    steps = [
        ("CLOSE (starting position)", config.SERVO_CLOSE_PWM, 3),
        ("PARTIAL release",           config.SERVO_PARTIAL_PWM, 3),
        ("FULL release",              config.SERVO_FULL_PWM, 3),
        ("CLOSE (re-latch)",          config.SERVO_CLOSE_PWM, 0),
    ]

    all_acked = True
    for label, pwm, wait in steps:
        print(f"  -> {label} (PWM {pwm})")
        ack_ok = send_servo(master, channel, pwm)
        if not ack_ok:
            all_acked = False
        if wait > 0:
            for remaining in range(wait, 0, -1):
                print(f"     waiting {remaining}s...", end='\r')
                time.sleep(1)
            print(f"     waited {wait}s       ")

    print()
    if not all_acked:
        print("  [FAIL] One or more servo commands not acknowledged")
        return False

    confirmed = ask_confirmation("Did the full sequence work correctly?", auto_mode)
    if confirmed:
        print("  [OK] Deploy sequence confirmed")
        return True
    else:
        print("  [FAIL] Deploy sequence not confirmed by operator")
        return False


# -- Main -------------------------------------------------------
def main():
    args = parse_args()
    channel = args.channel if args.channel is not None else config.SERVO_CHANNEL

    print()
    print("=" * 55)
    print("   SERVO RELEASE TEST — payload mechanism check")
    print("=" * 55)
    print()
    print(f"  Channel:  {channel}")
    print(f"  CLOSE:    {config.SERVO_CLOSE_PWM} PWM")
    print(f"  PARTIAL:  {config.SERVO_PARTIAL_PWM} PWM")
    print(f"  FULL:     {config.SERVO_FULL_PWM} PWM")
    print(f"  Mode:     {'automatic (--auto)' if args.auto else 'interactive'}")
    print()
    print("  Safe on bench. No arming. No motors. Just servo PWM.")
    print()

    master = connect()

    results = {}
    results['close'] = test_servo_close(master, channel, args.auto)
    results['partial'] = test_servo_partial(master, channel, args.auto)
    results['full'] = test_servo_full(master, channel, args.auto)
    results['sequence'] = test_servo_sequence(master, channel, args.auto)

    # Always return servo to CLOSE at the end
    print(f"\n  Returning servo to CLOSE ({config.SERVO_CLOSE_PWM} PWM)...")
    send_servo(master, channel, config.SERVO_CLOSE_PWM)
    print("  [OK] Servo returned to CLOSE")

    master.close()

    # Summary
    print()
    print("=" * 55)
    print("  RESULTS")
    print("=" * 55)

    tests = [
        ("Servo CLOSE position",         results['close']),
        ("Servo PARTIAL release",        results['partial']),
        ("Servo FULL release",           results['full']),
        ("Full deploy sequence",         results['sequence']),
    ]

    passed = 0
    for name, ok in tests:
        symbol = "+" if ok else "X"
        print(f"  [{symbol}] {name}")
        if ok:
            passed += 1

    print()
    if passed == len(tests):
        print(f"  ALL {passed} TESTS PASSED — servo release mechanism works!")
        print("  Ready for integration in main.py deploy sequence.")
    elif passed >= 2:
        print(f"  {passed}/{len(tests)} passed — servo partially working.")
        print("  Check wiring and SERVOx_FUNCTION in Mission Planner.")
    else:
        print(f"  {passed}/{len(tests)} passed — servo NOT working.")
        print("  Troubleshooting:")
        print("    1. Check channel number matches SERVOx_FUNCTION in MP")
        print("    2. Check AUX rail has power (BEC connected)")
        print("    3. Check servo wiring: signal (orange) / V+ (red) / GND (brown)")
        print("    4. Try --channel N with a different channel number")

    print()
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
