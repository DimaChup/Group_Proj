#!/usr/bin/env python3
"""
Follow Mode Simulation — drone searches, finds a MOVING target, then follows it.

Completely separate from the SAR mission code.
Self-contained: no imports from the main project.

Controls:
  - Click on map to place moving target (starts wandering)
  - Watch drone search → detect → switch to follow mode
  - 'r' = reset (new target placement)
  - 'q' / ESC = quit
  - '+'/'-' = speed up / slow down target
  - SPACE = pause/unpause target movement

Usage:
    python follow_mode/follow_sim.py
"""
import cv2
import numpy as np
import math
import time
import random

# ══════════════════════════════════════════════════════════════
#  CONFIG (all self-contained)
# ══════════════════════════════════════════════════════════════
MAP_W, MAP_H = 800, 600          # simulation area pixels
DRONE_ALT = 30.0                  # meters
FOV_DEG = 45.0                    # camera field of view
IMAGE_W, IMAGE_H = 640, 480      # camera resolution
DRONE_SPEED = 4.0                 # pixels per tick
TARGET_SPEED = 1.5                # pixels per tick (walking speed)
DETECT_RADIUS = 15                # target must be this close to FOV center to "detect"
FOLLOW_DISTANCE = 5               # how close drone tries to stay (pixels)
SEARCH_SPACING = 50               # lawnmower row spacing

# Colors
COL_DRONE = (255, 100, 0)        # blue
COL_FOV = (255, 200, 0)          # cyan
COL_TARGET = (0, 0, 255)         # red
COL_TARGET_TRAIL = (0, 0, 150)   # dark red
COL_SEARCH_PATH = (200, 200, 200)
COL_FOLLOW_LINE = (0, 255, 255)  # yellow
COL_DETECT = (0, 255, 0)         # green


# ══════════════════════════════════════════════════════════════
#  FOV CALCULATION
# ══════════════════════════════════════════════════════════════
def get_fov_size(alt):
    """Ground coverage in pixels at given altitude."""
    fov_rad = math.radians(FOV_DEG)
    ground_m = 2 * alt * math.tan(fov_rad / 2)
    # Assume 1 pixel = 1 meter for simplicity
    w = int(ground_m)
    h = int(ground_m * (IMAGE_H / IMAGE_W))
    return max(10, w), max(10, h)


# ══════════════════════════════════════════════════════════════
#  SEARCH PATTERN GENERATOR
# ══════════════════════════════════════════════════════════════
def generate_lawnmower(x_min, y_min, x_max, y_max, spacing):
    """Generate lawnmower search waypoints."""
    waypoints = []
    y = y_min + spacing // 2
    going_right = True
    while y < y_max:
        if going_right:
            waypoints.append([x_min + 10, y])
            waypoints.append([x_max - 10, y])
        else:
            waypoints.append([x_max - 10, y])
            waypoints.append([x_min + 10, y])
        going_right = not going_right
        y += spacing
    return waypoints


# ══════════════════════════════════════════════════════════════
#  MOVING TARGET
# ══════════════════════════════════════════════════════════════
class MovingTarget:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = TARGET_SPEED
        self.heading = random.uniform(0, 2 * math.pi)
        self.turn_timer = 0
        self.trail = []  # recent positions for trail drawing
        self.paused = False

    def update(self):
        if self.paused:
            return

        # Random wandering: occasionally change direction
        self.turn_timer -= 1
        if self.turn_timer <= 0:
            self.heading += random.gauss(0, 0.5)
            self.turn_timer = random.randint(20, 80)

        # Move
        dx = math.cos(self.heading) * self.speed
        dy = math.sin(self.heading) * self.speed
        new_x = self.x + dx
        new_y = self.y + dy

        # Bounce off walls
        margin = 30
        if new_x < margin or new_x > MAP_W - margin:
            self.heading = math.pi - self.heading
            new_x = max(margin, min(MAP_W - margin, new_x))
        if new_y < margin or new_y > MAP_H - margin:
            self.heading = -self.heading
            new_y = max(margin, min(MAP_H - margin, new_y))

        self.x = new_x
        self.y = new_y

        # Trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 200:
            self.trail.pop(0)


# ══════════════════════════════════════════════════════════════
#  DRONE STATE MACHINE
# ══════════════════════════════════════════════════════════════
class Drone:
    def __init__(self):
        self.x = MAP_W // 2
        self.y = 30.0
        self.alt = DRONE_ALT
        self.speed = DRONE_SPEED
        self.state = "SEARCH"
        self.waypoints = generate_lawnmower(20, 20, MAP_W - 20, MAP_H - 20, SEARCH_SPACING)
        self.wp_index = 0
        self.follow_target = None
        self.detect_count = 0
        self.lost_timer = 0
        self.last_known_x = 0
        self.last_known_y = 0
        self.trail = []

    def move_towards(self, tx, ty, spd=None):
        """Move towards target. Returns True if arrived."""
        if spd is None:
            spd = self.speed
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < spd:
            self.x = tx
            self.y = ty
            return True
        self.x += (dx / dist) * spd
        self.y += (dy / dist) * spd
        return False

    def get_fov_rect(self):
        """Get FOV rectangle corners."""
        fw, fh = get_fov_size(self.alt)
        x1 = int(self.x - fw // 2)
        y1 = int(self.y - fh // 2)
        x2 = x1 + fw
        y2 = y1 + fh
        return x1, y1, x2, y2

    def can_see(self, target):
        """Check if target is within FOV."""
        fx1, fy1, fx2, fy2 = self.get_fov_rect()
        return fx1 <= target.x <= fx2 and fy1 <= target.y <= fy2

    def pixel_position(self, target):
        """Where target appears in camera frame (pixel coords)."""
        fx1, fy1, fx2, fy2 = self.get_fov_rect()
        fw = fx2 - fx1
        fh = fy2 - fy1
        if fw == 0 or fh == 0:
            return IMAGE_W // 2, IMAGE_H // 2
        px = int((target.x - fx1) / fw * IMAGE_W)
        py = int((target.y - fy1) / fh * IMAGE_H)
        return px, py

    def update(self, target):
        """Main state machine tick."""
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 500:
            self.trail.pop(0)

        detected = target is not None and self.can_see(target)

        if self.state == "SEARCH":
            if detected:
                self.detect_count += 1
                self.state = "FOLLOWING"
                self.follow_target = target
                self.last_known_x = target.x
                self.last_known_y = target.y
                self.lost_timer = 0
                print(f"  [DETECTED] Switching to FOLLOW mode! (detection #{self.detect_count})")
            elif self.wp_index < len(self.waypoints):
                wp = self.waypoints[self.wp_index]
                if self.move_towards(wp[0], wp[1]):
                    self.wp_index += 1
            else:
                # Search complete, restart
                self.wp_index = 0

        elif self.state == "FOLLOWING":
            if detected:
                self.lost_timer = 0
                self.last_known_x = target.x
                self.last_known_y = target.y

                # Calculate guidance
                px, py = self.pixel_position(target)
                cx, cy = IMAGE_W // 2, IMAGE_H // 2
                off_x = (px - cx) / (IMAGE_W / 2)
                off_y = (py - cy) / (IMAGE_H / 2)

                # Move towards target (with slight lead)
                self.move_towards(target.x, target.y, self.speed)

            else:
                # Lost target — go to last known position
                self.lost_timer += 1
                arrived = self.move_towards(self.last_known_x, self.last_known_y, self.speed * 0.5)

                if self.lost_timer > 120:  # ~4 seconds at 30fps
                    print(f"  [LOST] Target lost for too long — back to SEARCH")
                    self.state = "SEARCH"
                    self.lost_timer = 0

        return detected


# ══════════════════════════════════════════════════════════════
#  MAIN SIMULATION
# ══════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 55)
    print("   FOLLOW MODE SIMULATION")
    print("   Drone searches → finds moving target → follows it")
    print("=" * 55)
    print()
    print("  Click on map to place moving target.")
    print("  Controls: +/- speed | SPACE pause | r reset | q quit")
    print()

    cv2.namedWindow("Follow Mode", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Follow Mode", MAP_W, MAP_H)

    drone = Drone()
    target = None
    frame_count = 0
    start_time = time.time()

    def mouse_callback(event, x, y, flags, param):
        nonlocal target
        if event == cv2.EVENT_LBUTTONDOWN:
            target = MovingTarget(x, y)
            print(f"  [TARGET] Placed at ({x}, {y}) — wandering started")

    cv2.setMouseCallback("Follow Mode", mouse_callback)

    while True:
        frame_count += 1

        # Update target
        if target:
            target.update()

        # Update drone
        detected = drone.update(target)

        # ── Draw ──
        canvas = np.zeros((MAP_H, MAP_W, 3), dtype=np.uint8)
        canvas[:] = (40, 40, 40)  # dark background

        # Grid
        for gx in range(0, MAP_W, 50):
            cv2.line(canvas, (gx, 0), (gx, MAP_H), (55, 55, 55), 1)
        for gy in range(0, MAP_H, 50):
            cv2.line(canvas, (0, gy), (MAP_W, gy), (55, 55, 55), 1)

        # Search path (remaining waypoints)
        if drone.state == "SEARCH" and drone.wp_index < len(drone.waypoints):
            pts = drone.waypoints[drone.wp_index:]
            for i in range(len(pts) - 1):
                cv2.line(canvas, tuple(pts[i]), tuple(pts[i + 1]), COL_SEARCH_PATH, 1)

        # Drone trail
        if len(drone.trail) > 1:
            for i in range(1, len(drone.trail)):
                alpha = i / len(drone.trail)
                col = (int(100 * alpha), int(100 * alpha), int(255 * alpha))
                cv2.line(canvas, drone.trail[i - 1], drone.trail[i], col, 1)

        # Target trail
        if target and len(target.trail) > 1:
            for i in range(1, len(target.trail)):
                cv2.line(canvas, target.trail[i - 1], target.trail[i], COL_TARGET_TRAIL, 1)

        # FOV rectangle
        fx1, fy1, fx2, fy2 = drone.get_fov_rect()
        fov_color = COL_DETECT if detected else COL_FOV
        cv2.rectangle(canvas, (fx1, fy1), (fx2, fy2), fov_color, 2 if detected else 1)

        # Follow line (drone → target)
        if drone.state == "FOLLOWING" and target:
            cv2.line(canvas, (int(drone.x), int(drone.y)),
                     (int(target.x), int(target.y)), COL_FOLLOW_LINE, 2)

        # Target
        if target:
            tx, ty = int(target.x), int(target.y)
            cv2.circle(canvas, (tx, ty), 8, COL_TARGET, -1)
            cv2.circle(canvas, (tx, ty), 12, COL_TARGET, 2)
            # Heading indicator
            hx = tx + int(math.cos(target.heading) * 20)
            hy = ty + int(math.sin(target.heading) * 20)
            cv2.arrowedLine(canvas, (tx, ty), (hx, hy), COL_TARGET, 2, tipLength=0.4)

        # Drone
        dx, dy = int(drone.x), int(drone.y)
        cv2.circle(canvas, (dx, dy), 6, COL_DRONE, -1)
        cv2.circle(canvas, (dx, dy), 10, COL_DRONE, 2)

        # ── Info panel ──
        panel_y = 10
        def info(text, color=(255, 255, 255)):
            nonlocal panel_y
            cv2.putText(canvas, text, (10, panel_y + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            panel_y += 22

        # State with color
        state_colors = {
            "SEARCH": (200, 200, 200),
            "FOLLOWING": (0, 255, 255),
        }
        state_col = state_colors.get(drone.state, (255, 255, 255))
        info(f"State: {drone.state}", state_col)

        if drone.state == "SEARCH":
            info(f"Waypoint: {drone.wp_index}/{len(drone.waypoints)}")
        elif drone.state == "FOLLOWING":
            if target:
                dist = math.sqrt((drone.x - target.x)**2 + (drone.y - target.y)**2)
                info(f"Distance: {dist:.0f}px")

                # Show guidance
                px, py = drone.pixel_position(target)
                cx, cy = IMAGE_W // 2, IMAGE_H // 2
                off_x = (px - cx) / (IMAGE_W / 2)
                off_y = (py - cy) / (IMAGE_H / 2)
                dirs = []
                if off_x < -0.15: dirs.append("LEFT")
                elif off_x > 0.15: dirs.append("RIGHT")
                if off_y < -0.15: dirs.append("FWD")
                elif off_y > 0.15: dirs.append("BACK")
                guidance = "CENTRED" if not dirs else "+".join(dirs)
                guide_col = (0, 255, 0) if guidance == "CENTRED" else (0, 255, 255)
                info(f"Guidance: {guidance}", guide_col)

            if drone.lost_timer > 0:
                info(f"LOST: {drone.lost_timer}/120", (0, 100, 255))

        if detected:
            info("** DETECTED **", COL_DETECT)

        info(f"Detections: {drone.detect_count}")

        if target:
            info(f"Target speed: {target.speed:.1f}", COL_TARGET)
            if target.paused:
                info("TARGET PAUSED", (100, 100, 255))

        # Camera view inset (bottom right)
        if target and detected:
            inset_w, inset_h = 160, 120
            inset = np.zeros((inset_h, inset_w, 3), dtype=np.uint8)
            inset[:] = (30, 30, 30)

            # Draw target in camera frame
            px, py = drone.pixel_position(target)
            # Scale to inset
            sx = int(px * inset_w / IMAGE_W)
            sy = int(py * inset_h / IMAGE_H)
            cv2.circle(inset, (sx, sy), 6, COL_TARGET, -1)
            # Center crosshair
            cv2.drawMarker(inset, (inset_w // 2, inset_h // 2),
                           (255, 255, 255), cv2.MARKER_CROSS, 15, 1)
            # Line from center to target
            cv2.line(inset, (inset_w // 2, inset_h // 2), (sx, sy), COL_FOLLOW_LINE, 1)
            cv2.rectangle(inset, (0, 0), (inset_w - 1, inset_h - 1), (100, 100, 100), 1)
            cv2.putText(inset, "CAM VIEW", (5, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1)

            # Place inset on canvas
            ix = MAP_W - inset_w - 10
            iy = MAP_H - inset_h - 10
            canvas[iy:iy + inset_h, ix:ix + inset_w] = inset

        # Instructions
        cv2.putText(canvas, "Click to place target | +/- speed | SPACE pause | r reset | q quit",
                    (10, MAP_H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (120, 120, 120), 1)

        cv2.imshow("Follow Mode", canvas)

        key = cv2.waitKey(33) & 0xFF  # ~30 FPS
        if key == ord('q') or key == 27:
            break
        elif key == ord('r'):
            drone = Drone()
            target = None
            print("  [RESET]")
        elif key == ord('+') or key == ord('='):
            if target:
                target.speed = min(10.0, target.speed + 0.5)
                print(f"  Target speed: {target.speed:.1f}")
        elif key == ord('-'):
            if target:
                target.speed = max(0.5, target.speed - 0.5)
                print(f"  Target speed: {target.speed:.1f}")
        elif key == 32:  # SPACE
            if target:
                target.paused = not target.paused
                print(f"  Target {'PAUSED' if target.paused else 'MOVING'}")

    cv2.destroyAllWindows()
    elapsed = time.time() - start_time
    print(f"\n  Ran for {elapsed:.0f}s, {drone.detect_count} detections")


if __name__ == "__main__":
    main()
