"""Standalone servo release test — simple interactive keyboard control.

Connects to the Cube via mavproxy's UDP bridge (already running on port 14550),
then lets you open/close the payload servo with keyboard keys. Also lets you
scan through channels if you're not sure which one is wired to the payload.

Usage:
    # Default: test channel 14 (current hardware)
    python tests/hardware/servo_test.py

    # Override channel
    python tests/hardware/servo_test.py --channel 9
    python tests/hardware/servo_test.py --channel 8

    # Sweep through candidate channels (6, 8, 9, 14)
    python tests/hardware/servo_test.py --sweep

Keys:
    o     = OPEN / release (PWM 1100)
    c     = CLOSE / hold (PWM 1500)
    p     = PARTIAL release (PWM 1300)
    1..9  = set custom PWM 1100..1900 in 100-step increments
    +/-   = raise/lower current channel number
    s     = sweep: open/close on channels 6, 8, 9, 10, 14 one at a time
    q     = quit (sets close PWM first)

Pre-requisites:
    - mavproxy running and bridging Cube to udpin on 127.0.0.1:14550
      (same as the terminal 1 setup used by passive_watch)
    - No propellers attached (safety!)
"""
import argparse
import sys
import time

from pymavlink import mavutil

# PWM levels (match config.py defaults)
PWM_CLOSE = 1500    # hold / re-latch
PWM_PARTIAL = 1300  # stage 1 partial release
PWM_OPEN = 1100     # stage 2 full release

# Channels to try when sweeping
SWEEP_CHANNELS = [6, 8, 9, 10, 14]


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--channel", type=int, default=14,
                    help="Servo channel to control (default: 14)")
    ap.add_argument("--conn", type=str, default="udpin:0.0.0.0:14550",
                    help="MAVLink connection string (default mavproxy UDP in)")
    ap.add_argument("--sweep", action="store_true",
                    help="Run a channel sweep automatically and exit")
    ap.add_argument("--dwell", type=float, default=1.5,
                    help="Seconds to dwell at each PWM during sweep (default 1.5)")
    return ap.parse_args()


def send_servo(mav, channel, pwm):
    """Send MAV_CMD_DO_SET_SERVO for one channel."""
    mav.mav.command_long_send(
        mav.target_system,
        mav.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0,            # confirmation
        channel,      # param1: servo channel (1-16)
        pwm,          # param2: PWM (1000-2000)
        0, 0, 0, 0, 0
    )
    print(f"  -> SERVO ch{channel} = {pwm} us")


def sweep(mav, dwell):
    print(f"\n== SWEEP: testing channels {SWEEP_CHANNELS} ==")
    for ch in SWEEP_CHANNELS:
        print(f"\n[Channel {ch}] CLOSE (1500)")
        send_servo(mav, ch, PWM_CLOSE)
        time.sleep(dwell)
        print(f"[Channel {ch}] OPEN (1100)")
        send_servo(mav, ch, PWM_OPEN)
        time.sleep(dwell)
        print(f"[Channel {ch}] CLOSE (1500) — returning to hold")
        send_servo(mav, ch, PWM_CLOSE)
        time.sleep(0.5)
        ans = input(f"  Did the servo move on channel {ch}? (y/n/q): ").strip().lower()
        if ans == "q":
            return
        if ans == "y":
            print(f"\n✓ CONFIRMED: payload servo is on CHANNEL {ch}")
            return


def interactive_loop(mav, channel):
    print(f"""
== Interactive servo control ==
Current channel: {channel}

Keys:
  o       open (PWM {PWM_OPEN})
  c       close (PWM {PWM_CLOSE})
  p       partial (PWM {PWM_PARTIAL})
  +/-     change channel
  s       sweep 6/8/9/10/14
  q       quit

""")
    while True:
        try:
            cmd = input(f"[ch{channel}]> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting, closing servo first...")
            send_servo(mav, channel, PWM_CLOSE)
            return

        if cmd == "q":
            print("Closing servo and exiting...")
            send_servo(mav, channel, PWM_CLOSE)
            return
        elif cmd == "o":
            send_servo(mav, channel, PWM_OPEN)
        elif cmd == "c":
            send_servo(mav, channel, PWM_CLOSE)
        elif cmd == "p":
            send_servo(mav, channel, PWM_PARTIAL)
        elif cmd == "+":
            channel = min(16, channel + 1)
            print(f"  channel -> {channel}")
        elif cmd == "-":
            channel = max(1, channel - 1)
            print(f"  channel -> {channel}")
        elif cmd == "s":
            sweep(mav, dwell=1.5)
        elif cmd.isdigit():
            ch_try = int(cmd)
            if 1 <= ch_try <= 16:
                channel = ch_try
                print(f"  channel -> {channel}")
            else:
                print("  channel must be 1-16")
        elif cmd == "":
            continue
        else:
            print("  Unknown. Keys: o/c/p/+/-/s/q or 1-16")


def main():
    args = parse_args()

    print(f"Connecting to {args.conn} ...")
    mav = mavutil.mavlink_connection(args.conn)
    mav.wait_heartbeat()
    print(f"Heartbeat OK from system {mav.target_system}, component {mav.target_component}")

    if args.sweep:
        sweep(mav, args.dwell)
    else:
        interactive_loop(mav, args.channel)


if __name__ == "__main__":
    main()
