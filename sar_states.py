#!/usr/bin/env python3
"""
Clean SAR Mission State Machine Definition
Designed for clarity, flowcharting, and real-world implementation
"""

from enum import Enum

class MissionState(Enum):
    """
    Main mission states for SAR drone operation
    Each state represents ONE clear operational mode
    """

    # ===== GROUND OPERATIONS =====
    IDLE = "IDLE"
    # System powered, on ground, motors off
    # Entry: Power on, mission reset
    # Exit: Start mission command received

    PREFLIGHT = "PREFLIGHT"
    # Pre-flight checks, GPS lock, sensor verification
    # Entry: Mission start command
    # Exit: All systems ready

    # ===== FLIGHT OPERATIONS =====
    TAKEOFF = "TAKEOFF"
    # Vertical climb to mission altitude
    # Entry: Preflight complete
    # Exit: Target altitude reached

    TRANSIT = "TRANSIT"
    # Fast horizontal flight to search area entry point
    # Entry: Takeoff complete
    # Exit: Reached search area start waypoint

    SEARCHING = "SEARCHING"
    # Follow search pattern, visual detection active
    # Can be BROAD (initial) or FOCUSED (post-PLB)
    # Entry: Reached search area OR PLB received
    # Exit: Target detected OR search complete

    # ===== TARGET ENGAGEMENT =====
    TRACKING = "TRACKING"
    # Actively following detected target, centering in view
    # Entry: Target detected with confidence
    # Exit: Target centered OR lost

    LOITER = "LOITER"
    # Hovering over target for verification/confirmation
    # Entry: Target centered
    # Exit: Target verified OR rejected

    # ===== LANDING SEQUENCE =====
    APPROACH_LANDING = "APPROACH_LANDING"
    # Fly to safe landing spot (5-10m from target)
    # Entry: Target verified, landing spot calculated
    # Exit: Reached landing spot

    LANDING = "LANDING"
    # Vertical descent to ground
    # Entry: At landing spot
    # Exit: Touchdown detected

    GROUND_OPS = "GROUND_OPS"
    # On ground, deploy payload (first aid kit)
    # Entry: Landed safely
    # Exit: Payload deployed

    # ===== RETURN HOME =====
    RETURN_HOME = "RETURN_HOME"
    # Fly back to takeoff location (TOL)
    # Entry: Payload deployed OR search aborted
    # Exit: Reached home location

    FINAL_LANDING = "FINAL_LANDING"
    # Land at home base
    # Entry: At home location
    # Exit: Touchdown at home

    # ===== TERMINAL STATES =====
    MISSION_COMPLETE = "MISSION_COMPLETE"
    # Mission successful, system shutdown
    # Entry: Landed at home
    # Exit: Manual reset only

    EMERGENCY = "EMERGENCY"
    # Emergency failsafe triggered
    # Can transition from ANY state
    # Actions: RTH or emergency land
    # Exit: Safe landing OR manual recovery


class SearchMode(Enum):
    """Sub-mode for SEARCHING state"""
    BROAD = "BROAD"      # Initial wide-area search
    FOCUSED = "FOCUSED"  # Focused search after PLB activation


class EmergencyType(Enum):
    """Types of emergency conditions"""
    LOW_BATTERY = "LOW_BATTERY"
    GPS_LOST = "GPS_LOST"
    COMM_LOST = "COMM_LOST"
    NO_FLY_VIOLATION = "NO_FLY_VIOLATION"
    MANUAL_ABORT = "MANUAL_ABORT"
    SENSOR_FAILURE = "SENSOR_FAILURE"


class StateTransitions:
    """
    Defines valid state transitions and their conditions
    Use this to generate flowcharts
    """

    TRANSITIONS = {
        MissionState.IDLE: {
            "next": [MissionState.PREFLIGHT],
            "condition": "Mission start command received",
            "action": "Initialize systems"
        },

        MissionState.PREFLIGHT: {
            "next": [MissionState.TAKEOFF, MissionState.EMERGENCY],
            "condition": "All systems GO / System failure",
            "action": "Check GPS, sensors, battery, geofence loaded"
        },

        MissionState.TAKEOFF: {
            "next": [MissionState.TRANSIT, MissionState.EMERGENCY],
            "condition": "Altitude >= target_altitude / Failure",
            "action": "Climb at 2 m/s to mission altitude"
        },

        MissionState.TRANSIT: {
            "next": [MissionState.SEARCHING, MissionState.EMERGENCY],
            "condition": "Distance to search_start < threshold / Failure",
            "action": "Fly at high speed to search area entry point"
        },

        MissionState.SEARCHING: {
            "next": [MissionState.TRACKING, MissionState.RETURN_HOME, MissionState.EMERGENCY],
            "condition": "Target detected / Search complete / Failure",
            "action": "Follow waypoints, run detection, check for PLB",
            "notes": "PLB changes search mode from BROAD to FOCUSED (same state)"
        },

        MissionState.TRACKING: {
            "next": [MissionState.LOITER, MissionState.SEARCHING, MissionState.EMERGENCY],
            "condition": "Target centered / Target lost / Failure",
            "action": "Fly toward target, keep in camera view"
        },

        MissionState.LOITER: {
            "next": [MissionState.APPROACH_LANDING, MissionState.SEARCHING, MissionState.EMERGENCY],
            "condition": "Target verified / Target rejected / Failure",
            "action": "Hover, verify target identity, wait for confirmation"
        },

        MissionState.APPROACH_LANDING: {
            "next": [MissionState.LANDING, MissionState.EMERGENCY],
            "condition": "Distance to landing_spot < threshold / Failure",
            "action": "Calculate safe landing spot 5-10m from target, fly there"
        },

        MissionState.LANDING: {
            "next": [MissionState.GROUND_OPS, MissionState.EMERGENCY],
            "condition": "Altitude < 0.1m (touchdown) / Failure",
            "action": "Descend slowly, detect ground contact"
        },

        MissionState.GROUND_OPS: {
            "next": [MissionState.RETURN_HOME],
            "condition": "Payload deployed",
            "action": "Trigger payload release mechanism, wait for confirmation"
        },

        MissionState.RETURN_HOME: {
            "next": [MissionState.FINAL_LANDING, MissionState.EMERGENCY],
            "condition": "Distance to home < threshold / Failure",
            "action": "Climb to safe altitude, fly to home location"
        },

        MissionState.FINAL_LANDING: {
            "next": [MissionState.MISSION_COMPLETE, MissionState.EMERGENCY],
            "condition": "Altitude < 0.1m at home / Failure",
            "action": "Descend at home location"
        },

        MissionState.MISSION_COMPLETE: {
            "next": [],
            "condition": "Manual reset only",
            "action": "Disarm motors, log mission data, shutdown"
        },

        MissionState.EMERGENCY: {
            "next": [MissionState.IDLE],
            "condition": "After safe landing and recovery",
            "action": "Execute RTH or emergency land depending on failure type"
        }
    }


def print_state_summary():
    """Print a text summary of all states"""
    print("=" * 70)
    print("SAR MISSION STATE MACHINE SUMMARY")
    print("=" * 70)
    print("\n[STATES]\n")

    for state in MissionState:
        trans = StateTransitions.TRANSITIONS.get(state, {})
        print(f"{state.value}")
        if trans:
            print(f"  > Next: {[s.value for s in trans.get('next', [])]}")
            print(f"  > Condition: {trans.get('condition', 'N/A')}")
            print(f"  > Action: {trans.get('action', 'N/A')}")
            if 'notes' in trans:
                print(f"  > Notes: {trans.get('notes')}")
        print()


def generate_mermaid_flowchart():
    """Generate Mermaid flowchart syntax for visualization"""
    print("\n" + "=" * 70)
    print("MERMAID FLOWCHART (paste into https://mermaid.live)")
    print("=" * 70)
    print("""
```mermaid
flowchart TD
    IDLE[IDLE<br/>On Ground, Motors Off] --> PREFLIGHT[PREFLIGHT<br/>System Checks]
    PREFLIGHT -->|All Systems GO| TAKEOFF[TAKEOFF<br/>Climb to Altitude]
    PREFLIGHT -->|Failure| EMERGENCY[EMERGENCY<br/>Failsafe]

    TAKEOFF -->|Altitude Reached| TRANSIT[TRANSIT<br/>Fly to Search Area]
    TRANSIT -->|Reached Start Point| SEARCHING[SEARCHING<br/>Follow Pattern<br/>Detect Target]

    SEARCHING -->|Target Detected| TRACKING[TRACKING<br/>Center on Target]
    SEARCHING -->|PLB Received| SEARCHING
    SEARCHING -->|Search Complete| RETURN_HOME[RETURN_HOME<br/>Fly to Base]

    TRACKING -->|Target Centered| LOITER[LOITER<br/>Hover & Verify]
    TRACKING -->|Target Lost| SEARCHING

    LOITER -->|Verified| APPROACH_LANDING[APPROACH_LANDING<br/>Fly to Landing Spot]
    LOITER -->|Rejected| SEARCHING

    APPROACH_LANDING -->|Arrived| LANDING[LANDING<br/>Descend to Ground]
    LANDING -->|Touchdown| GROUND_OPS[GROUND_OPS<br/>Deploy Payload]

    GROUND_OPS --> RETURN_HOME
    RETURN_HOME -->|At Home| FINAL_LANDING[FINAL_LANDING<br/>Land at Base]
    FINAL_LANDING -->|Touchdown| MISSION_COMPLETE[MISSION_COMPLETE<br/>Mission Done]

    TAKEOFF -.->|Emergency| EMERGENCY
    TRANSIT -.->|Emergency| EMERGENCY
    SEARCHING -.->|Emergency| EMERGENCY
    TRACKING -.->|Emergency| EMERGENCY
    LOITER -.->|Emergency| EMERGENCY
    APPROACH_LANDING -.->|Emergency| EMERGENCY
    LANDING -.->|Emergency| EMERGENCY
    RETURN_HOME -.->|Emergency| EMERGENCY

    EMERGENCY -->|After Safe Landing| IDLE

    style IDLE fill:#90EE90
    style MISSION_COMPLETE fill:#90EE90
    style EMERGENCY fill:#FF6B6B
    style SEARCHING fill:#FFD93D
    style LOITER fill:#FFD93D
```
""")


if __name__ == "__main__":
    print_state_summary()
    generate_mermaid_flowchart()

    print("\n" + "=" * 70)
    print("[STATISTICS]")
    print("=" * 70)
    print(f"Total States: {len(MissionState)}")
    print(f"Ground States: 2 (IDLE, PREFLIGHT)")
    print(f"Flight States: 2 (TAKEOFF, TRANSIT)")
    print(f"Search States: 1 (SEARCHING)")
    print(f"Engagement States: 2 (TRACKING, LOITER)")
    print(f"Landing States: 4 (APPROACH_LANDING, LANDING, GROUND_OPS, RETURN_HOME)")
    print(f"Terminal States: 3 (FINAL_LANDING, MISSION_COMPLETE, EMERGENCY)")
    print("=" * 70)
