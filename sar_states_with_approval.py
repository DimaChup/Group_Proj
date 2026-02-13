#!/usr/bin/env python3
"""
SAR Mission State Machine with Human-in-the-Loop (HITL) Approval Requirements
Defines which transitions require human approval for safety and mission success
"""

from enum import Enum

class MissionState(Enum):
    """Main mission states"""
    IDLE = "IDLE"
    PREFLIGHT = "PREFLIGHT"
    TAKEOFF = "TAKEOFF"
    TRANSIT = "TRANSIT"
    SEARCHING = "SEARCHING"
    TRACKING = "TRACKING"
    LOITER = "LOITER"
    APPROACH_LANDING = "APPROACH_LANDING"
    LANDING = "LANDING"
    GROUND_OPS = "GROUND_OPS"
    RETURN_HOME = "RETURN_HOME"
    FINAL_LANDING = "FINAL_LANDING"
    MISSION_COMPLETE = "MISSION_COMPLETE"
    EMERGENCY = "EMERGENCY"


class ApprovalLevel(Enum):
    """Types of state transitions"""
    AUTOMATIC = "AUTO"                    # Happens automatically
    APPROVAL_REQUIRED = "APPROVAL"        # Requires human approval
    MANUAL_TRIGGER = "MANUAL"             # Human must initiate
    INFORMATIONAL = "INFO"                # Notify pilot, no action needed


class ApprovalPrompt(Enum):
    """Standard approval prompts for GCS interface"""
    MISSION_START = "Ready to begin preflight checks?"
    TAKEOFF_CLEARANCE = "Preflight complete. Arm motors and takeoff?"
    TARGET_VERIFY = "Target detected. Is this the casualty?"
    LANDING_APPROVE = "Landing spot calculated. Approve landing?"
    PAYLOAD_DEPLOY = "On ground. Deploy first aid kit?"
    ABORT_SEARCH = "Search pattern complete, no target found. Return home?"


class StateTransitionConfig:
    """
    Configuration for each state transition
    Includes approval requirements, timeouts, and prompts
    """

    TRANSITIONS = {
        # ===== MISSION START =====
        (MissionState.IDLE, MissionState.PREFLIGHT): {
            "approval": ApprovalLevel.MANUAL_TRIGGER,
            "prompt": ApprovalPrompt.MISSION_START,
            "description": "Pilot initiates mission start",
            "can_abort": True,
            "timeout": None  # Wait indefinitely
        },

        # ===== PREFLIGHT TO TAKEOFF =====
        (MissionState.PREFLIGHT, MissionState.TAKEOFF): {
            "approval": ApprovalLevel.APPROVAL_REQUIRED,
            "prompt": ApprovalPrompt.TAKEOFF_CLEARANCE,
            "description": "Confirm all systems ready, airspace clear",
            "can_abort": True,
            "timeout": None,  # Wait for pilot decision
            "checklist": [
                "GPS lock obtained (>10 satellites)",
                "Battery >80%",
                "Geofence loaded",
                "Camera operational",
                "Airspace clear"
            ]
        },

        (MissionState.PREFLIGHT, MissionState.EMERGENCY): {
            "approval": ApprovalLevel.AUTOMATIC,
            "description": "Preflight check failed",
            "can_abort": False
        },

        # ===== TAKEOFF TO TRANSIT =====
        (MissionState.TAKEOFF, MissionState.TRANSIT): {
            "approval": ApprovalLevel.AUTOMATIC,
            "description": "Target altitude reached",
            "condition": "altitude >= target_altitude",
            "notify_pilot": True,
            "can_abort": True
        },

        # ===== TRANSIT TO SEARCHING =====
        (MissionState.TRANSIT, MissionState.SEARCHING): {
            "approval": ApprovalLevel.AUTOMATIC,
            "description": "Reached search area entry point",
            "condition": "distance_to_search_start < 5m",
            "notify_pilot": True,
            "can_abort": True
        },

        # ===== SEARCHING TO TRACKING =====
        (MissionState.SEARCHING, MissionState.TRACKING): {
            "approval": ApprovalLevel.AUTOMATIC,
            "description": "Target detected, beginning tracking",
            "condition": "target_confidence > 0.7",
            "notify_pilot": True,  # Important: Tell pilot we found something
            "can_abort": True,
            "pilot_can_reject": True  # Pilot can say "false positive, keep searching"
        },

        (MissionState.SEARCHING, MissionState.RETURN_HOME): {
            "approval": ApprovalLevel.APPROVAL_REQUIRED,
            "prompt": ApprovalPrompt.ABORT_SEARCH,
            "description": "Search pattern complete, no target found",
            "condition": "search_complete AND NOT target_found",
            "can_abort": False,
            "options": [
                "Return Home (mission abort)",
                "Extend Search (add more waypoints)",
                "Manual Search (pilot control)"
            ]
        },

        # ===== TRACKING TO LOITER =====
        (MissionState.TRACKING, MissionState.LOITER): {
            "approval": ApprovalLevel.AUTOMATIC,
            "description": "Target centered, entering verification hover",
            "condition": "target_centered AND distance < 10m",
            "notify_pilot": True,
            "can_abort": True
        },

        (MissionState.TRACKING, MissionState.SEARCHING): {
            "approval": ApprovalLevel.AUTOMATIC,
            "description": "Target lost, resuming search",
            "condition": "target_lost_for > 5_seconds",
            "notify_pilot": True
        },

        # ===== LOITER TO APPROACH_LANDING ===== ⭐ CRITICAL
        (MissionState.LOITER, MissionState.APPROACH_LANDING): {
            "approval": ApprovalLevel.APPROVAL_REQUIRED,
            "prompt": ApprovalPrompt.TARGET_VERIFY,
            "description": "Human verification that target is correct casualty",
            "timeout": 60,  # If no response in 60s, return to SEARCHING
            "can_abort": True,
            "options": [
                "Confirm - This is the casualty (proceed to landing)",
                "Reject - False positive (resume search)",
                "Hold - Need more time to observe (stay in LOITER)"
            ],
            "display_info": [
                "Live camera feed",
                "GPS coordinates",
                "Detection confidence",
                "Time hovering"
            ],
            "importance": "CRITICAL",
            "rationale": "Prevent landing at wrong target, wasting resources"
        },

        (MissionState.LOITER, MissionState.SEARCHING): {
            "approval": ApprovalLevel.AUTOMATIC,
            "description": "Target rejected or verification timeout",
            "condition": "pilot_rejected OR timeout_exceeded"
        },

        # ===== APPROACH_LANDING TO LANDING =====
        (MissionState.APPROACH_LANDING, MissionState.LANDING): {
            "approval": ApprovalLevel.AUTOMATIC,  # Can make this APPROVAL_REQUIRED if desired
            "description": "Arrived at landing spot (5-10m from target)",
            "condition": "distance_to_landing_spot < 2m",
            "notify_pilot": True,
            "can_abort": True,
            "optional_approval": True,  # Can enable for extra safety
            "optional_prompt": ApprovalPrompt.LANDING_APPROVE
        },

        # ===== LANDING TO GROUND_OPS =====
        (MissionState.LANDING, MissionState.GROUND_OPS): {
            "approval": ApprovalLevel.AUTOMATIC,
            "description": "Touchdown detected",
            "condition": "altitude < 0.1m AND ground_contact",
            "notify_pilot": True
        },

        # ===== GROUND_OPS TO RETURN_HOME =====
        (MissionState.GROUND_OPS, MissionState.RETURN_HOME): {
            "approval": ApprovalLevel.APPROVAL_REQUIRED,
            "prompt": ApprovalPrompt.PAYLOAD_DEPLOY,
            "description": "Deploy first aid kit payload",
            "timeout": 30,
            "can_abort": False,  # Must either deploy or manual override
            "action": "Trigger payload release mechanism"
        },

        # ===== RETURN_HOME TO FINAL_LANDING =====
        (MissionState.RETURN_HOME, MissionState.FINAL_LANDING): {
            "approval": ApprovalLevel.AUTOMATIC,
            "description": "Reached home location",
            "condition": "distance_to_home < 5m",
            "notify_pilot": True
        },

        # ===== FINAL_LANDING TO MISSION_COMPLETE =====
        (MissionState.FINAL_LANDING, MissionState.MISSION_COMPLETE): {
            "approval": ApprovalLevel.AUTOMATIC,
            "description": "Landed at home, mission complete",
            "condition": "altitude < 0.1m AND at_home",
            "notify_pilot": True
        },

        # ===== EMERGENCY TRANSITIONS =====
        # Any state can go to EMERGENCY (triggered by pilot or system)
    }


class PilotOverride(Enum):
    """Commands pilot can issue at ANY time from ANY state"""
    EMERGENCY_RTH = "EMERGENCY_RTH"                # Return to home immediately
    EMERGENCY_LAND = "EMERGENCY_LAND"              # Land at current position NOW
    MANUAL_CONTROL = "MANUAL_CONTROL"              # Switch to manual RC control
    PAUSE_MISSION = "PAUSE_MISSION"                # Hold position, await instructions
    ABORT_MISSION = "ABORT_MISSION"                # Cancel mission, RTH
    REJECT_CURRENT = "REJECT_CURRENT"              # Reject current action (e.g., false detection)


def print_approval_summary():
    """Print which transitions require approval"""
    print("=" * 80)
    print("SAR MISSION - HUMAN APPROVAL REQUIREMENTS")
    print("=" * 80)
    print("\n[CRITICAL - APPROVAL REQUIRED]\n")

    critical = []
    recommended = []
    automatic = []

    for (from_state, to_state), config in StateTransitionConfig.TRANSITIONS.items():
        approval = config.get("approval")
        if approval in [ApprovalLevel.APPROVAL_REQUIRED, ApprovalLevel.MANUAL_TRIGGER]:
            importance = config.get("importance", "HIGH")
            if importance == "CRITICAL":
                critical.append((from_state, to_state, config))
            else:
                recommended.append((from_state, to_state, config))
        else:
            automatic.append((from_state, to_state, config))

    # Print critical approvals
    for from_state, to_state, config in critical:
        print(f"[!] {from_state.value} -> {to_state.value}")
        print(f"   Prompt: {config.get('prompt', 'N/A')}")
        print(f"   Why: {config.get('rationale', config.get('description'))}")
        if 'options' in config:
            print(f"   Options: {config['options']}")
        print()

    print("\n[HIGH PRIORITY - APPROVAL REQUIRED]\n")
    for from_state, to_state, config in recommended:
        print(f"> {from_state.value} -> {to_state.value}")
        print(f"  Prompt: {config.get('prompt', 'N/A')}")
        print(f"  Why: {config.get('description')}")
        print()

    print("\n[AUTOMATIC TRANSITIONS (No Approval)]\n")
    print(f"Total: {len(automatic)} transitions happen automatically")
    print("Pilot is notified but doesn't need to approve")
    print()
    for from_state, to_state, config in automatic[:5]:  # Show first 5
        print(f"  - {from_state.value} -> {to_state.value}")
    print(f"  ... and {len(automatic) - 5} more")

    print("\n" + "=" * 80)
    print("[PILOT OVERRIDE CAPABILITIES - AVAILABLE ANYTIME]")
    print("=" * 80)
    for override in PilotOverride:
        print(f"  [{override.value}]")
    print()


def generate_gcs_interface_spec():
    """Generate specification for Ground Control Station interface"""
    print("=" * 80)
    print("GROUND CONTROL STATION (GCS) INTERFACE SPECIFICATION")
    print("=" * 80)
    print("""
## Required Display Elements:

1. **Status Panel** (always visible)
   - Current state (large, clear font)
   - Mission timer
   - Battery percentage
   - GPS position
   - Altitude
   - Distance to target/home
   - Number of waypoints completed

2. **Video Feed** (always visible)
   - Live camera feed from drone
   - Target detection overlay (bounding box, confidence)
   - Crosshair/center indicator

3. **Map View** (always visible)
   - Drone position
   - Search area boundary
   - No-fly zones
   - Waypoints (completed vs remaining)
   - Detected targets
   - Home location

4. **Approval Dialog** (appears when needed)
   - Large, clear prompt
   - Simple YES/NO or multiple choice buttons
   - Relevant information for decision
   - Timeout indicator if applicable

5. **Emergency Controls** (always visible, RED)
   - Big red "EMERGENCY RTH" button
   - "EMERGENCY LAND" button
   - "MANUAL CONTROL" button
   - "PAUSE MISSION" button

## Critical Design Principles:

- [OK] **Clarity** - Pilot should know state in 1 second
- [OK] **Simplicity** - One-click decisions when possible
- [OK] **Safety** - Emergency controls always accessible
- [OK] **Context** - Provide info needed for decision
- [OK] **Feedback** - Confirm actions immediately
- [NO] **NO hidden menus** - Everything critical is visible
- [NO] **NO small buttons** - Touch-friendly (min 44x44px)
- [NO] **NO jargon** - Use plain language

## Example Approval Dialog for LOITER -> APPROACH_LANDING:

    +------------------------------------------+
    |  [!] TARGET VERIFICATION REQUIRED        |
    +------------------------------------------+
    |                                          |
    |  [Live Video Feed]                       |
    |  Confidence: 87%                         |
    |  Position: 51.4545N, -2.5879W            |
    |  Hovering time: 0:15                     |
    |                                          |
    |  Is this the casualty?                   |
    |                                          |
    |  [YES] CONFIRM - Proceed to Landing      |
    |  [NO]  REJECT - Resume Search            |
    |  [HOLD] Continue Observing               |
    |                                          |
    |  Timeout in: 45s                         |
    +------------------------------------------+
""")


if __name__ == "__main__":
    print_approval_summary()
    generate_gcs_interface_spec()

    print("\n" + "=" * 80)
    print("BEST PRACTICES SUMMARY")
    print("=" * 80)
    print("""
1. [OK] Semi-Autonomous Operation (Level 2)
   - Drone executes search and navigation autonomously
   - Human approves critical decisions
   - Human can override anytime

2. [!] MOST CRITICAL Approval: Target Verification (LOITER)
   - Don't land at wrong target
   - Human visual confirmation required
   - Options: Confirm, Reject, or Hold for more observation

3. [EMERGENCY] Emergency Overrides Always Available
   - Big red buttons for RTH, Emergency Land, Manual Control
   - Accessible from ANY state
   - No confirmation dialog (immediate action)

4. [INFO] Clear Communication
   - Always show current state
   - Notify pilot of autonomous transitions
   - Provide context for approval decisions

5. [TIME] Timeouts for Safety
   - Approval requests have timeouts (30-60 seconds)
   - If no response: safe default action (usually RTH or hold)
   - Prevents mission from getting stuck

6. [LOG] Log Everything
   - All approvals/rejections logged
   - Pilot actions timestamped
   - Required for post-mission analysis and regulatory compliance
""")
    print("=" * 80)
