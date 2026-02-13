#!/usr/bin/env python3
"""
Simple SAR Mission Simulator
Tests the state machine logic without heavy simulation overhead
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from enum import Enum
import math
import random


def random_point_in_polygon(polygon):
    """Generate a random point inside a polygon using rejection sampling"""
    # Get bounding box
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    while True:
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        if point_in_polygon(x, y, polygon):
            return (x, y)


def point_in_polygon(x, y, polygon):
    """Ray casting algorithm to check if point is inside polygon"""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

class MissionState(Enum):
    """All possible states for the SAR mission"""
    INIT = "INIT"
    TAKEOFF = "TAKEOFF"
    TRANSIT_TO_SEARCH = "TRANSIT_TO_SEARCH"
    SEARCH = "SEARCH"
    SEARCH_FOCUSED = "SEARCH_FOCUSED"
    TARGET_DETECTED = "TARGET_DETECTED"
    CENTERING = "CENTERING"  # Fly above target to refine position estimate
    DESCEND = "DESCEND"  # Descend to verify altitude for better look
    VERIFY_TARGET = "VERIFY_TARGET"  # Hover and wait for pilot Y/N
    SELECT_LANDING_SIDE = "SELECT_LANDING_SIDE"  # Pilot picks N/S/E/W
    APPROACH_LANDING = "APPROACH_LANDING"
    LAND = "LAND"
    DEPLOY_PAYLOAD = "DEPLOY_PAYLOAD"
    ASCEND = "ASCEND"
    RETURN_TO_HOME = "RETURN_TO_HOME"
    LAND_AT_HOME = "LAND_AT_HOME"
    MISSION_COMPLETE = "MISSION_COMPLETE"
    MANUAL = "MANUAL"
    EMERGENCY = "EMERGENCY"

class SimpleDrone:
    def __init__(self, start_pos, altitude=0):
        self.x = start_pos[0]
        self.y = start_pos[1]
        self.altitude = altitude
        self.target_altitude = 30.0  # Default flight altitude
        self.speed = 5.0  # pixels per time step
        # FOV at reference altitude (30m) = 36x36  (60% of original 60)
        # Scales proportionally with altitude: fov = 36 * (alt / 30) = 1.2 * alt
        self.fov_ref = 36.0  # FOV side length at target_altitude
        self.fov_width = self.fov_ref   # current FOV (updated each frame)
        self.fov_height = self.fov_ref

    def update_fov(self):
        """Update FOV size based on current altitude (higher = sees more ground)"""
        if self.altitude > 0:
            scale = self.altitude / self.target_altitude
            self.fov_width = self.fov_ref * scale
            self.fov_height = self.fov_ref * scale
        else:
            self.fov_width = 1.0  # minimal FOV on ground
            self.fov_height = 1.0

class MissionSimulator:
    def __init__(self, config_file='mission_config.json'):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)

        # Extract map elements
        self.width = self.config['map_size']['width']
        self.height = self.config['map_size']['height']
        self.search_area = self.config['search_area']
        self.no_fly_zone = self.config['no_fly_zone']
        self.start_point = tuple(self.config['start_point'])
        self.transit_waypoints = self.config['transit_waypoints']
        self.search_waypoints = self.config['search_waypoints']
        # Dummy location - set by user click before simulation starts
        self.dummy_location = None

        # Initialize drone
        self.drone = SimpleDrone(self.start_point)

        # Mission state
        self.state = MissionState.INIT
        self.current_waypoint_index = 0
        self.target_detected = False
        self.time_step = 0

        # Search pass tracking (1 = forward, 2 = reverse)
        self.search_pass = 1

        # PLB focused search
        self.plb_received = False
        self.plb_focus_area = None
        self.focused_waypoints = []
        self.focused_waypoint_index = 0
        self.focused_wp_line = None
        self.focused_search_pass = 1  # 1 = forward, 2 = reverse sweep of focus area
        self.waiting_for_focused_retry = False  # pilot prompt after 2 sweeps
        self.focused_retry_result = None

        # After rejection, suppress detection until dummy leaves FOV
        self.detection_suppressed = False

        # Where the drone was when it detected the target
        self.detected_position = None

        # Estimated target position (rough at first, refined during centering/descend)
        self.estimated_target_pos = None

        # Landing spot (calculated later)
        self.landing_spot = None

        # Verify altitude (lower altitude for better look before Y/N)
        self.verify_altitude = 15.0

        # Human-in-the-loop verification
        self.waiting_for_verification = False
        self.verification_result = None

        # Landing side selection (N/S/E/W after Y confirmation)
        self.selecting_landing_side = False
        self.landing_side_result = None

        # Deploy payload: 0=waiting for R (release), 1=released, waiting for H (go home)
        self.deploy_phase = 0

        # Emergency landing flag (skip payload deploy)
        self.emergency_landing = False

        # Manual mode: stores the state to resume to
        self.pre_manual_state = None

        # Logging
        self.state_log = []
        self.violations = []

        # Visualization
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.setup_plot()

        # Connect keyboard events for human-in-the-loop
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def setup_plot(self):
        # Dark theme matching the map setup tool
        self.fig.set_facecolor('#1a1a2e')
        self.ax.set_facecolor('#16213e')
        self.ax.set_xlim(-10, self.width + 10)
        self.ax.set_ylim(-10, self.height + 10)
        self.ax.invert_yaxis()  # Flip Y-axis so (0,0) is top-left
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.15, color='#4a4a6a')
        self.ax.set_title('SAR Mission Simulator', fontsize=16, fontweight='bold', color='white')
        self.ax.tick_params(colors='#8888aa')
        for spine in self.ax.spines.values():
            spine.set_color('#4a4a6a')

        # Search area - bright blue
        if len(self.search_area) > 2:
            poly = patches.Polygon(self.search_area, closed=True,
                                  edgecolor='#4dabf7', facecolor='#4dabf7',
                                  alpha=0.15, linewidth=2, label='Search Area')
            self.ax.add_patch(poly)

        # No-fly zone - dark red
        if len(self.no_fly_zone) > 2:
            poly = patches.Polygon(self.no_fly_zone, closed=True,
                                  edgecolor='#e03131', facecolor='#c92a2a',
                                  alpha=0.25, linewidth=2, label='No-Fly Zone')
            self.ax.add_patch(poly)

        # Transit waypoints - orange/yellow dashed
        if self.transit_waypoints:
            transit_x = [p[0] for p in self.transit_waypoints]
            transit_y = [p[1] for p in self.transit_waypoints]
            self.ax.plot(transit_x, transit_y, '^--', color='#ffa94d', markersize=9,
                        linewidth=1.5, label='Transit Waypoints', alpha=0.8,
                        markeredgecolor='#e8590c', markeredgewidth=1)
            for i, (x, y) in enumerate(self.transit_waypoints):
                self.ax.text(x + 5, y - 5, str(i+1), fontsize=7, color='#ffa94d', fontweight='bold')

        # Search waypoints - cyan with numbers
        if self.search_waypoints:
            search_x = [p[0] for p in self.search_waypoints]
            search_y = [p[1] for p in self.search_waypoints]
            self.ax.plot(search_x, search_y, 'o--', color='#22b8cf', markersize=6,
                        linewidth=1, label='Search Waypoints', alpha=0.7,
                        markeredgecolor='#15aabf', markeredgewidth=1)
            for i, (x, y) in enumerate(self.search_waypoints):
                self.ax.text(x + 4, y - 4, str(i+1), fontsize=6, color='#22b8cf')

        # Start point - bright green
        self.ax.plot(self.start_point[0], self.start_point[1], 'o',
                    color='#51cf66', markersize=15, label='Start/Home',
                    markeredgecolor='#2f9e44', markeredgewidth=2)

        # Dummy marker - will be created after user clicks to place
        self.dummy_marker = None

        # Drone marker - white with cyan glow
        self.drone_marker = self.ax.plot(self.drone.x, self.drone.y, 'o',
                                        color='white', markersize=12,
                                        markeredgecolor='#22b8cf',
                                        markeredgewidth=3, label='Drone')[0]

        # FOV rectangle - cyan tint
        self.fov_rect = patches.Rectangle(
            (self.drone.x - self.drone.fov_ref/2, self.drone.y - self.drone.fov_ref/2),
            self.drone.fov_ref, self.drone.fov_ref,
            edgecolor='#22b8cf', facecolor='#22b8cf', alpha=0.2,
            linewidth=1.5, linestyle='-', label='FOV')
        self.ax.add_patch(self.fov_rect)

        # Trail - light blue
        self.trail_x = [self.drone.x]
        self.trail_y = [self.drone.y]
        self.trail_line, = self.ax.plot(self.trail_x, self.trail_y, '-',
                                       color='#74c0fc', linewidth=1, alpha=0.5,
                                       label='Drone Path')

        # Info text - dark panel with light text
        self.info_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes,
                                     verticalalignment='top', fontsize=10,
                                     family='monospace', color='#e0e0e0',
                                     bbox=dict(boxstyle='round', facecolor='#0f3460',
                                               edgecolor='#4a4a6a', alpha=0.92))

        self.ax.legend(loc='upper right', fontsize=9, facecolor='#0f3460',
                      edgecolor='#4a4a6a', labelcolor='#e0e0e0')

    def point_in_polygon(self, point, polygon):
        """Check if point is inside polygon using ray casting"""
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def check_no_fly_violation(self):
        """Check if drone is in no-fly zone"""
        if len(self.no_fly_zone) > 2:
            if self.point_in_polygon((self.drone.x, self.drone.y), self.no_fly_zone):
                violation = f"NO-FLY ZONE VIOLATION at ({self.drone.x:.1f}, {self.drone.y:.1f})"
                if violation not in self.violations:
                    self.violations.append(violation)
                    print(f"⚠️  {violation}")
                return True
        return False

    def distance_to(self, target):
        """Calculate distance to target point"""
        return math.sqrt((self.drone.x - target[0])**2 + (self.drone.y - target[1])**2)

    def move_towards(self, target, speed=None):
        """Move drone towards target at given speed"""
        if speed is None:
            speed = self.drone.speed

        dx = target[0] - self.drone.x
        dy = target[1] - self.drone.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist < speed:
            self.drone.x = target[0]
            self.drone.y = target[1]
            return True  # Reached
        else:
            self.drone.x += (dx / dist) * speed
            self.drone.y += (dy / dist) * speed
            return False  # Still moving

    def place_dummy(self):
        """Let user click on the map to place the dummy before simulation starts"""
        self.ax.set_title('CLICK to place the dummy (casualty) on the map', fontsize=16,
                         fontweight='bold', color='#ff6b6b')
        plt.draw()
        plt.pause(0.1)

        print("Click on the map to place the dummy...")
        point = plt.ginput(1, timeout=0)  # Wait for 1 click, no timeout

        if point:
            self.dummy_location = (point[0][0], point[0][1])
            print(f"Dummy placed at: ({self.dummy_location[0]:.1f}, {self.dummy_location[1]:.1f})")

            # Draw dummy as a warm red circle
            self.dummy_marker = plt.Circle(self.dummy_location, radius=5,
                                          color='#ff6b6b', alpha=0.3,
                                          edgecolor='#e03131', linewidth=1.5,
                                          label='Dummy (Casualty)')
            self.ax.add_patch(self.dummy_marker)
        else:
            print("No dummy placed!")
            return False

        self.ax.set_title('SAR Mission Simulator', fontsize=16, fontweight='bold', color='white')
        self.ax.legend(loc='upper right', fontsize=9, facecolor='#0f3460',
                      edgecolor='#4a4a6a', labelcolor='#e0e0e0')
        plt.draw()
        return True

    def on_key_press(self, event):
        """Handle keyboard input for human-in-the-loop verification"""
        if not event.key:
            return
        key = event.key.lower()

        # --- Manual mode toggle (M) - available from any active state ---
        if key == 'm' and self.state != MissionState.MANUAL and self.state != MissionState.MISSION_COMPLETE:
            self.pre_manual_state = self.state
            self.state = MissionState.MANUAL
            self.ax.set_title('MANUAL MODE - Press A to resume auto, L to emergency land',
                             fontsize=14, fontweight='bold', color='#ffd43b')
            print("\n" + "="*50)
            print("  MANUAL MODE ACTIVATED - Drone holding position")
            print("  Press A = Resume automatic mode")
            print("  Press L = Emergency land here")
            print("="*50 + "\n")
            plt.draw()
            return

        # --- Manual mode actions (A = resume, L = emergency land) ---
        if self.state == MissionState.MANUAL:
            if key == 'a':
                # Resume previous state
                print(f">> Resuming automatic mode -> {self.pre_manual_state.value}")
                self.state = self.pre_manual_state
                self.pre_manual_state = None
                self.ax.set_title('SAR Mission Simulator', fontsize=16, fontweight='bold', color='white')
                plt.draw()
            elif key == 'l':
                # Emergency land at current position
                print(">> EMERGENCY LANDING initiated at current position")
                self.landing_spot = (self.drone.x, self.drone.y)
                self.pre_manual_state = None
                self.emergency_landing = True
                self.ax.set_title('EMERGENCY LANDING', fontsize=16, fontweight='bold', color='#ff6b6b')
                self.state = MissionState.LAND
                plt.draw()
            return

        # Landing side selection (after Y confirmation)
        if self.selecting_landing_side:
            if key in ['n', 's', 'e', 'w']:
                self.landing_side_result = key
                self.selecting_landing_side = False
                print(f">> Landing side selected: {key.upper()}")
            return

        # Focused search retry prompt (Y = search again, N = RTH)
        if self.waiting_for_focused_retry:
            if key == 'y':
                self.focused_retry_result = True
                self.waiting_for_focused_retry = False
                print(">> Pilot chose to SEARCH AGAIN")
            elif key == 'n':
                self.focused_retry_result = False
                self.waiting_for_focused_retry = False
                print(">> Pilot chose to RETURN HOME")
            return

        # Deploy: R = release kit, H = go home
        if self.state == MissionState.DEPLOY_PAYLOAD:
            if key == 'r' and self.deploy_phase == 0:
                self.deploy_phase = 1
                print(">> FIRST AID KIT RELEASED!")
                self.ax.set_title('Kit released! Press H to return home',
                                 fontsize=14, fontweight='bold', color='#51cf66')
                plt.draw()
            elif key == 'h' and self.deploy_phase == 1:
                print(">> RTH command received - ascending")
                self.ax.set_title('SAR Mission Simulator', fontsize=16, fontweight='bold', color='white')
                self.state = MissionState.ASCEND
                plt.draw()
            return

        # Target verification (Y/N)
        if self.waiting_for_verification:
            if key == 'y':
                self.verification_result = True
                self.waiting_for_verification = False
                print(">> Key Y received - CONFIRMED")
            elif key == 'n':
                self.verification_result = False
                self.waiting_for_verification = False
                print(">> Key N received - REJECTED")

    def check_detection(self):
        """Check if dummy is within the drone's FOV rectangle"""
        if self.dummy_location is None:
            return False
        dx = abs(self.dummy_location[0] - self.drone.x)
        dy = abs(self.dummy_location[1] - self.drone.y)
        in_fov = dx < self.drone.fov_width / 2 and dy < self.drone.fov_height / 2

        if self.detection_suppressed:
            if not in_fov:
                # Dummy has left the FOV - re-enable detection
                self.detection_suppressed = False
            return False

        return in_fov

    def generate_plb_focus_area(self):
        """Generate PLB focus area as random polygon (5-7 sides) around dummy, clamped to search area"""
        error_radius = 30
        plb_x = self.dummy_location[0] + np.random.uniform(-error_radius, error_radius)
        plb_y = self.dummy_location[1] + np.random.uniform(-error_radius, error_radius)

        # Random polygon: 5-7 sides, ~75% of old 120x120 area
        num_sides = random.randint(5, 7)
        base_radius = 48  # avg vertex distance from center

        # Clamp center so polygon stays inside search area
        sa_xs = [p[0] for p in self.search_area]
        sa_ys = [p[1] for p in self.search_area]
        sa_min_x, sa_max_x = min(sa_xs), max(sa_xs)
        sa_min_y, sa_max_y = min(sa_ys), max(sa_ys)
        max_r = base_radius + 15
        plb_x = max(sa_min_x + max_r, min(sa_max_x - max_r, plb_x))
        plb_y = max(sa_min_y + max_r, min(sa_max_y - max_r, plb_y))

        # Generate sorted random angles with perturbation
        base_angles = np.linspace(0, 2 * np.pi, num_sides, endpoint=False)
        angles = base_angles + np.random.uniform(-0.3, 0.3, num_sides)
        angles = np.sort(angles)

        # Random radii per vertex
        radii = np.random.uniform(base_radius - 15, base_radius + 15, num_sides)

        # Build polygon vertices
        self.plb_focus_area = []
        for angle, radius in zip(angles, radii):
            vx = plb_x + radius * np.cos(angle)
            vy = plb_y + radius * np.sin(angle)
            self.plb_focus_area.append((vx, vy))

        # Draw PLB focus area
        poly = patches.Polygon(self.plb_focus_area, closed=True,
                              edgecolor='orange', facecolor='orange',
                              alpha=0.15, linewidth=3, linestyle='--',
                              label='PLB Focus Area')
        self.ax.add_patch(poly)
        print(f"PLB ACTIVATED! Focus area at ({plb_x:.1f}, {plb_y:.1f}), {num_sides} sides")

    def _scanline_intersections(self, y_val):
        """Find x-intersections of horizontal line y_val with the focus area polygon edges"""
        intersections = []
        n = len(self.plb_focus_area)
        for i in range(n):
            x1, y1 = self.plb_focus_area[i]
            x2, y2 = self.plb_focus_area[(i + 1) % n]
            if (y1 <= y_val < y2) or (y2 <= y_val < y1):
                if y2 != y1:
                    x_int = x1 + (y_val - y1) * (x2 - x1) / (y2 - y1)
                    intersections.append(x_int)
        intersections.sort()
        return intersections

    def generate_focused_waypoints(self):
        """Generate lawnmower sweep that follows the polygon shape using scan-line clipping"""
        ys = [p[1] for p in self.plb_focus_area]
        min_y, max_y = min(ys), max(ys)

        # Row spacing = half FOV at search altitude for good overlap
        spacing = self.drone.fov_ref * 0.5
        margin = 3

        waypoints = []
        y = min_y + margin
        going_right = True

        while y <= max_y - margin:
            # Find where this row intersects the polygon
            intersections = self._scanline_intersections(y)

            # Pair intersections (enter/exit polygon) and create waypoints
            for j in range(0, len(intersections) - 1, 2):
                left = intersections[j] + margin
                right = intersections[j + 1] - margin
                if right > left:
                    if going_right:
                        waypoints.append([left, y])
                        waypoints.append([right, y])
                    else:
                        waypoints.append([right, y])
                        waypoints.append([left, y])
            if intersections:
                going_right = not going_right
            y += spacing

        self.focused_waypoints = waypoints
        self.focused_waypoint_index = 0

        # Plot the focused search path on the map
        if waypoints:
            wp_x = [p[0] for p in waypoints]
            wp_y = [p[1] for p in waypoints]
            self.focused_wp_line, = self.ax.plot(wp_x, wp_y, '*--',
                                                 markersize=8, linewidth=1.5,
                                                 color='lime', alpha=0.8,
                                                 label='Focused Search Path')
            self.ax.legend(loc='upper right', fontsize=9, facecolor='#0f3460',
                          edgecolor='#4a4a6a', labelcolor='#e0e0e0')
            plt.draw()

        print(f"Generated {len(waypoints)} focused search waypoints (polygon sweep)")

    def refine_target_estimate(self):
        """Refine estimated target position when dummy is in FOV (simulates camera GPS refinement)"""
        if self.dummy_location is None or self.estimated_target_pos is None:
            return
        # Check if dummy is currently in FOV
        dx = abs(self.dummy_location[0] - self.drone.x)
        dy = abs(self.dummy_location[1] - self.drone.y)
        if dx < self.drone.fov_width / 2 and dy < self.drone.fov_height / 2:
            # Move estimate 20% closer to actual position each step
            ex, ey = self.estimated_target_pos
            ax, ay = self.dummy_location
            self.estimated_target_pos = (ex + 0.2 * (ax - ex), ey + 0.2 * (ay - ey))

    def calculate_safe_landing_spot(self, direction):
        """Calculate landing spot 7.5m from estimated target in chosen direction (N/S/E/W)"""
        distance = 7.5
        tx, ty = self.estimated_target_pos

        if direction == 'n':
            landing_x, landing_y = tx, ty - distance  # North = up (y inverted)
        elif direction == 's':
            landing_x, landing_y = tx, ty + distance  # South = down
        elif direction == 'e':
            landing_x, landing_y = tx + distance, ty  # East = right
        elif direction == 'w':
            landing_x, landing_y = tx - distance, ty  # West = left
        else:
            landing_x, landing_y = tx, ty - distance  # Default north

        self.landing_spot = (landing_x, landing_y)
        print(f"Landing spot: {direction.upper()} of target at ({landing_x:.1f}, {landing_y:.1f})")

    def update_state_machine(self):
        """Main state machine logic"""
        prev_state = self.state

        # ===== STATE MACHINE =====
        if self.state == MissionState.INIT:
            self.state = MissionState.TAKEOFF

        elif self.state == MissionState.TAKEOFF:
            # Simulate altitude gain
            if self.drone.altitude < self.drone.target_altitude:
                self.drone.altitude += 1.0
            else:
                self.state = MissionState.TRANSIT_TO_SEARCH
                self.current_waypoint_index = 0

        elif self.state == MissionState.TRANSIT_TO_SEARCH:
            # Follow transit waypoints
            if self.transit_waypoints and self.current_waypoint_index < len(self.transit_waypoints):
                target = self.transit_waypoints[self.current_waypoint_index]
                if self.move_towards(target, speed=8.0):  # Fast transit
                    self.current_waypoint_index += 1
            else:
                # Reached search area
                self.state = MissionState.SEARCH
                self.current_waypoint_index = 0

        elif self.state == MissionState.SEARCH:
            # Check for target detection via FOV
            if self.check_detection():
                self.target_detected = True
                self.detected_position = (self.drone.x, self.drone.y)
                self.state = MissionState.TARGET_DETECTED
                print(f"TARGET DETECTED during broad search!")
            else:
                # Follow search waypoints
                if self.current_waypoint_index < len(self.search_waypoints):
                    target = self.search_waypoints[self.current_waypoint_index]
                    if self.move_towards(target, speed=3.0):
                        self.current_waypoint_index += 1

                    # Check if 40% of waypoints done -> trigger PLB
                    total_wps = len(self.search_waypoints)
                    if not self.plb_received and self.current_waypoint_index >= int(total_wps * 0.4):
                        self.plb_received = True
                        self.generate_plb_focus_area()
                        self.generate_focused_waypoints()
                        self.state = MissionState.SEARCH_FOCUSED
                else:
                    # Completed current pass
                    if self.search_pass == 1:
                        # First pass done - reverse waypoints for second pass
                        self.search_pass = 2
                        self.search_waypoints = list(reversed(self.search_waypoints))
                        self.current_waypoint_index = 0
                        print("Search pass 1 complete - starting reverse pass")
                    else:
                        # Both passes done, nothing found - return home
                        print("Search complete - target not found. Returning home.")
                        self.return_waypoints = list(reversed(self.transit_waypoints)) + [list(self.start_point)]
                        self.return_waypoint_index = 0
                        self.state = MissionState.RETURN_TO_HOME

        elif self.state == MissionState.SEARCH_FOCUSED:
            # Handle pilot retry decision (after 2 sweeps with no find)
            if self.focused_retry_result is not None:
                if self.focused_retry_result:
                    # Pilot wants to search focus area again - reverse and go
                    self.focused_waypoints = list(reversed(self.focused_waypoints))
                    self.focused_waypoint_index = 0
                    self.focused_search_pass += 1
                    self.focused_retry_result = None
                    self.ax.set_title('SAR Mission Simulator', fontsize=16, fontweight='bold', color='white')
                    print(f"Searching focus area again (pass {self.focused_search_pass})")
                else:
                    # Pilot wants to RTH
                    self.ax.set_title('SAR Mission Simulator', fontsize=16, fontweight='bold', color='white')
                    print("Pilot chose RTH - returning home")
                    self.return_waypoints = list(reversed(self.transit_waypoints)) + [list(self.start_point)]
                    self.return_waypoint_index = 0
                    self.state = MissionState.RETURN_TO_HOME
            elif self.waiting_for_focused_retry:
                pass  # Waiting for pilot input
            elif self.check_detection():
                # Target found
                self.target_detected = True
                self.detected_position = (self.drone.x, self.drone.y)
                self.state = MissionState.TARGET_DETECTED
                print("TARGET DETECTED during focused search!")
            else:
                # Follow generated lawnmower waypoints
                if self.focused_waypoint_index < len(self.focused_waypoints):
                    target = self.focused_waypoints[self.focused_waypoint_index]
                    if self.move_towards(target, speed=3.0):
                        self.focused_waypoint_index += 1
                else:
                    # Focused sweep exhausted
                    if self.focused_search_pass == 1:
                        # First sweep done - reverse for second sweep
                        self.focused_search_pass = 2
                        self.focused_waypoints = list(reversed(self.focused_waypoints))
                        self.focused_waypoint_index = 0
                        print("Focus area sweep 1 complete - starting reverse sweep")
                    else:
                        # Two sweeps done, not found - ask pilot
                        self.waiting_for_focused_retry = True
                        self.focused_retry_result = None
                        self.ax.set_title('TARGET NOT FOUND - Press Y to search again, N to RTH',
                                         fontsize=14, fontweight='bold', color='#ffa94d')
                        print("\n" + "="*50)
                        print("  TARGET NOT FOUND IN FOCUS AREA (2 sweeps)")
                        print("  Press Y = Search focus area again")
                        print("  Press N = Return to home")
                        print("="*50 + "\n")

        elif self.state == MissionState.TARGET_DETECTED:
            # Simulate camera GPS calculation: camera sees the target in FOV
            # and estimates its ground position (like calculate_target_gps in real code)
            # Result is near the actual dummy with measurement noise
            noise = 8
            est_x = self.dummy_location[0] + np.random.uniform(-noise, noise)
            est_y = self.dummy_location[1] + np.random.uniform(-noise, noise)
            self.estimated_target_pos = (est_x, est_y)
            self.verification_result = None
            self.landing_side_result = None
            print(f"Camera GPS estimate: ({est_x:.1f}, {est_y:.1f}) [actual: ({self.dummy_location[0]:.1f}, {self.dummy_location[1]:.1f})]")
            self.state = MissionState.CENTERING

        elif self.state == MissionState.CENTERING:
            # Fly above estimated target at search altitude to refine position
            self.refine_target_estimate()
            if self.move_towards(self.estimated_target_pos, speed=4.0):
                # Arrived above estimated target - descend for better look
                print(f"Centered above target. Estimate: ({self.estimated_target_pos[0]:.1f}, {self.estimated_target_pos[1]:.1f})")
                self.state = MissionState.DESCEND

        elif self.state == MissionState.DESCEND:
            # Descend to verify altitude while tracking + refining position
            self.refine_target_estimate()
            # Stay centered above the refining estimate while descending
            self.move_towards(self.estimated_target_pos, speed=2.0)
            if self.drone.altitude > self.verify_altitude:
                self.drone.altitude -= 0.5
            else:
                print(f"At verify altitude ({self.verify_altitude}m). Final estimate: ({self.estimated_target_pos[0]:.1f}, {self.estimated_target_pos[1]:.1f})")
                self.state = MissionState.VERIFY_TARGET

        elif self.state == MissionState.VERIFY_TARGET:
            # Human-in-the-loop: wait for pilot Y/N (like main.py VERIFY state)
            if not self.waiting_for_verification and self.verification_result is None:
                self.waiting_for_verification = True
                self.ax.set_title('TARGET DETECTED - Press Y to confirm, N to reject',
                                 fontsize=14, fontweight='bold', color='#ff6b6b')
                print("\n" + "="*50)
                print("  TARGET DETECTED! PILOT VERIFICATION REQUIRED")
                print("  Press Y to CONFIRM or N to REJECT")
                print("="*50 + "\n")
                plt.draw()
            elif self.verification_result is not None:
                if self.verification_result:
                    # Confirmed - ask pilot which side to land
                    print("CONFIRMED by pilot - select landing side")
                    self.state = MissionState.SELECT_LANDING_SIDE
                else:
                    # Rejected - resume search, suppress until dummy leaves FOV
                    print("REJECTED by pilot - resuming search")
                    self.target_detected = False
                    self.detected_position = None
                    self.estimated_target_pos = None
                    self.verification_result = None
                    self.detection_suppressed = True
                    self.drone.altitude = self.drone.target_altitude
                    if self.dummy_marker:
                        self.dummy_marker.set_alpha(0.3)
                    self.ax.set_title('SAR Mission Simulator', fontsize=16, fontweight='bold', color='white')
                    if self.focused_waypoints and self.focused_waypoint_index < len(self.focused_waypoints):
                        self.state = MissionState.SEARCH_FOCUSED
                    else:
                        self.state = MissionState.SEARCH

        elif self.state == MissionState.SELECT_LANDING_SIDE:
            # Wait for pilot to choose landing side (N/S/E/W)
            if not self.selecting_landing_side and self.landing_side_result is None:
                self.selecting_landing_side = True
                self.ax.set_title('SELECT LANDING SIDE - Press N / S / E / W',
                                 fontsize=14, fontweight='bold', color='#51cf66')
                print("\n" + "="*50)
                print("  SELECT LANDING SIDE")
                print("  Press N (North) / S (South) / E (East) / W (West)")
                print("="*50 + "\n")
                plt.draw()
            elif self.landing_side_result is not None:
                self.calculate_safe_landing_spot(self.landing_side_result)
                self.ax.set_title('SAR Mission Simulator', fontsize=16, fontweight='bold', color='white')
                self.state = MissionState.APPROACH_LANDING

        elif self.state == MissionState.APPROACH_LANDING:
            if self.move_towards(self.landing_spot, speed=2.0):
                self.state = MissionState.LAND

        elif self.state == MissionState.LAND:
            if self.drone.altitude > 0:
                self.drone.altitude -= 0.5
            else:
                if self.emergency_landing:
                    print("Emergency landing complete.")
                    self.state = MissionState.MISSION_COMPLETE
                else:
                    self.state = MissionState.DEPLOY_PAYLOAD

        elif self.state == MissionState.DEPLOY_PAYLOAD:
            # Phase 0: waiting for pilot to press R (release kit)
            # Phase 1: kit released, waiting for pilot to press H (go home)
            # Transitions handled in on_key_press
            if prev_state != MissionState.DEPLOY_PAYLOAD and self.deploy_phase == 0:
                self.ax.set_title('LANDED - Press R to release first aid kit',
                                 fontsize=14, fontweight='bold', color='#ffd43b')
                print("\n" + "="*50)
                print("  LANDED next to target")
                print("  Press R = Release first aid kit")
                print("="*50 + "\n")

        elif self.state == MissionState.ASCEND:
            # Climb back to cruise altitude before transit home
            if self.drone.altitude < self.drone.target_altitude:
                self.drone.altitude += 1.0
            else:
                print(f"Reached {self.drone.target_altitude}m - heading home")
                self.return_waypoints = list(reversed(self.transit_waypoints)) + [list(self.start_point)]
                self.return_waypoint_index = 0
                self.state = MissionState.RETURN_TO_HOME

        elif self.state == MissionState.RETURN_TO_HOME:
            # Follow reverse transit waypoints back home
            if self.return_waypoint_index < len(self.return_waypoints):
                target = self.return_waypoints[self.return_waypoint_index]
                if self.move_towards(target, speed=8.0):
                    self.return_waypoint_index += 1
            else:
                self.state = MissionState.LAND_AT_HOME

        elif self.state == MissionState.LAND_AT_HOME:
            if self.drone.altitude > 0:
                self.drone.altitude -= 1.0
            else:
                self.state = MissionState.MISSION_COMPLETE
                print("✓ MISSION COMPLETE!")

        elif self.state == MissionState.MANUAL:
            # Drone holds position - all movement handled by key press (A or L)
            pass

        # Log state changes
        if prev_state != self.state:
            log_entry = f"[T={self.time_step}] {prev_state.value} → {self.state.value}"
            self.state_log.append(log_entry)
            print(log_entry)

        # Check violations
        self.check_no_fly_violation()

    def update_visualization(self):
        """Update the plot"""
        # Update drone position
        self.drone_marker.set_data([self.drone.x], [self.drone.y])

        # Update FOV size based on altitude, then reposition and resize
        self.drone.update_fov()
        self.fov_rect.set_xy((self.drone.x - self.drone.fov_width/2,
                              self.drone.y - self.drone.fov_height/2))
        self.fov_rect.set_width(self.drone.fov_width)
        self.fov_rect.set_height(self.drone.fov_height)

        # Update trail
        self.trail_x.append(self.drone.x)
        self.trail_y.append(self.drone.y)
        self.trail_line.set_data(self.trail_x, self.trail_y)

        # Show dummy when detected
        if self.target_detected and self.dummy_marker:
            self.dummy_marker.set_alpha(1.0)

        # Draw landing spot
        if self.landing_spot:
            self.ax.plot(self.landing_spot[0], self.landing_spot[1], '^',
                        color='#51cf66', markersize=15,
                        markeredgecolor='#2f9e44', markeredgewidth=2)

        # Update info text
        info = f"Time: {self.time_step}\n"
        info += f"State: {self.state.value}\n"
        info += f"Position: ({self.drone.x:.1f}, {self.drone.y:.1f})\n"
        info += f"Altitude: {self.drone.altitude:.1f}m\n"
        info += f"Target Detected: {self.target_detected}\n"
        if self.state == MissionState.SEARCH_FOCUSED:
            info += f"Search Mode: FOCUSED (sweep {self.focused_search_pass})\n"
        elif self.state == MissionState.SEARCH:
            info += f"Search Mode: BROAD (pass {self.search_pass}/2)\n"
        if self.estimated_target_pos:
            info += f"Target Est: ({self.estimated_target_pos[0]:.1f}, {self.estimated_target_pos[1]:.1f})\n"
        if self.state == MissionState.ASCEND:
            info += f"Ascending to {self.drone.target_altitude:.0f}m\n"
        info += f"PLB Received: {self.plb_received}\n"
        info += f"Violations: {len(self.violations)}"
        if self.state == MissionState.MANUAL:
            info += "\n\n>>> MANUAL MODE <<<\n"
            info += "Press A = Resume auto\n"
            info += "Press L = Emergency land"
        elif self.state == MissionState.DEPLOY_PAYLOAD:
            if self.deploy_phase == 0:
                info += "\n\n>>> LANDED <<<\n"
                info += "Press R = Release first aid kit"
            else:
                info += "\n\n>>> KIT RELEASED <<<\n"
                info += "Press H = Return home"
        elif self.waiting_for_verification:
            info += "\n\n>>> CONFIRM TARGET? <<<\n"
            info += "Press Y = Confirm\n"
            info += "Press N = Reject"
        elif self.selecting_landing_side:
            info += "\n\n>>> SELECT LANDING SIDE <<<\n"
            info += "Press N/S/E/W"
        elif self.waiting_for_focused_retry:
            info += "\n\n>>> NOT FOUND IN FOCUS AREA <<<\n"
            info += "Press Y = Search again\n"
            info += "Press N = Return home"
        else:
            info += "\n\nPress M = Manual mode"
        self.info_text.set_text(info)

    def step(self):
        """Single simulation step"""
        if self.state != MissionState.MISSION_COMPLETE:
            self.update_state_machine()
            self.update_visualization()
            self.time_step += 1

    def run_auto(self, max_steps=2000):
        """Run simulation automatically until complete"""
        # Let user place the dummy first
        if not self.place_dummy():
            print("Simulation cancelled - no dummy placed.")
            return

        print("\n=== Starting Automatic Simulation ===\n")

        for _ in range(max_steps):
            self.step()

            # Longer pause when waiting for human input so key events register
            if self.state in (MissionState.MANUAL, MissionState.DEPLOY_PAYLOAD) or self.waiting_for_verification or self.selecting_landing_side or self.waiting_for_focused_retry:
                plt.pause(0.15)
            else:
                plt.pause(0.01)

            if self.state == MissionState.MISSION_COMPLETE:
                break

        self.print_summary()
        plt.show()

    def print_summary(self):
        """Print mission summary"""
        print("\n" + "="*50)
        print("MISSION SUMMARY")
        print("="*50)
        print(f"Total Time Steps: {self.time_step}")
        print(f"Target Found: {self.target_detected}")
        print(f"Search Passes Completed: {self.search_pass}")
        print(f"Final State: {self.state.value}")
        print(f"\nViolations: {len(self.violations)}")
        for v in self.violations:
            print(f"  - {v}")

        if self.landing_spot and self.target_detected:
            final_dist = self.distance_to(self.dummy_location)
            print(f"\nFinal Distance to Target: {final_dist:.2f} units")

        print("\nState Transitions:")
        for log in self.state_log[-10:]:  # Last 10 transitions
            print(f"  {log}")

        print("="*50)

if __name__ == "__main__":
    print("=== SAR Mission Simple Simulator ===")
    print("Loading configuration from mission_config.json...\n")

    try:
        sim = MissionSimulator('mission_config.json')
        sim.run_auto()
    except FileNotFoundError:
        print("❌ Error: mission_config.json not found!")
        print("Please run map_setup_tool.py first to create your mission map.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
