#!/usr/bin/env python3
"""Servo Release — Side View Demo.

Visual proof-of-concept showing a two-stage servo release mechanism.
Uses OpenCV drawing only. Auto-plays and loops.

Controls: SPACE = pause/resume, R = restart, Q = quit
"""

import cv2
import numpy as np
import time

W, H = 800, 600
GROUND_Y = 480
DRONE_Y = 160          # drone hover altitude (3m ~ pixel 160)
FPS = 60
CYCLE = 12.0           # total loop duration in seconds

# Colors (BGR)
SKY_TOP = (235, 200, 140)
SKY_BOT = (230, 180, 120)
GROUND  = (55, 120, 75)
GROUND2 = (45, 100, 65)
DRONE_C = (60, 60, 60)
ROTOR_C = (40, 40, 40)
ROPE_C  = (70, 70, 180)
PKG_C   = (40, 40, 200)
BAR_BG  = (50, 50, 50)
BAR_FG  = (200, 160, 50)
WHITE   = (255, 255, 255)
GREEN   = (80, 200, 80)
ORANGE  = (50, 160, 240)
RED     = (60, 60, 220)


def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


def draw_sky(img):
    for y in range(GROUND_Y):
        t = y / GROUND_Y
        c = tuple(int(lerp(SKY_TOP[i], SKY_BOT[i], t)) for i in range(3))
        img[y, :] = c
    img[GROUND_Y:GROUND_Y+5, :] = GROUND2
    img[GROUND_Y+5:, :] = GROUND


def draw_drone(img, cx, cy):
    # Body
    bw, bh = 70, 18
    cv2.rectangle(img, (cx - bw//2, cy - bh//2), (cx + bw//2, cy + bh//2), DRONE_C, -1)
    cv2.rectangle(img, (cx - 12, cy - bh//2 - 10), (cx + 12, cy - bh//2), (80, 80, 80), -1)
    # Landing skids
    for dx in [-25, 25]:
        cv2.line(img, (cx + dx, cy + bh//2), (cx + dx, cy + bh//2 + 14), DRONE_C, 2)
        cv2.line(img, (cx + dx - 10, cy + bh//2 + 14), (cx + dx + 10, cy + bh//2 + 14), DRONE_C, 3)
    # Rotor arms + rotors
    for dx in [-38, 38]:
        cv2.line(img, (cx, cy - 4), (cx + dx, cy - 20), DRONE_C, 3)
        cv2.ellipse(img, (cx + dx, cy - 22), (22, 4), 0, 0, 360, ROTOR_C, 2)


def draw_package(img, cx, cy, w=30, h=22):
    cv2.rectangle(img, (cx - w//2, cy - h//2), (cx + w//2, cy + h//2), PKG_C, -1)
    cv2.rectangle(img, (cx - w//2, cy - h//2), (cx + w//2, cy + h//2), (30, 30, 150), 2)
    cv2.line(img, (cx - w//2, cy - h//2), (cx + w//2, cy + h//2), (30, 30, 150), 1)
    cv2.line(img, (cx + w//2, cy - h//2), (cx - w//2, cy + h//2), (30, 30, 150), 1)


def draw_rope(img, x1, y1, x2, y2):
    cv2.line(img, (x1, y1), (x2, y2), ROPE_C, 2)


def draw_checkmark(img, cx, cy):
    pts = np.array([[cx-12, cy], [cx-4, cy+10], [cx+14, cy-10]], np.int32)
    cv2.polylines(img, [pts], False, GREEN, 3, cv2.LINE_AA)


def draw_timeline(img, t, phase_name):
    bar_x, bar_y, bar_w, bar_h = 50, H - 30, W - 100, 12
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), BAR_BG, -1)
    fill = int(bar_w * (t / CYCLE))
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + fill, bar_y + bar_h), BAR_FG, -1)
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), WHITE, 1)
    # Phase markers
    for s in [3, 6, 9]:
        mx = bar_x + int(bar_w * s / CYCLE)
        cv2.line(img, (mx, bar_y - 3), (mx, bar_y + bar_h + 3), WHITE, 1)
    cv2.putText(img, f"{t:.1f}s", (bar_x + bar_w + 8, bar_y + bar_h), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE, 1, cv2.LINE_AA)


def render(t):
    img = np.zeros((H, W, 3), np.uint8)
    draw_sky(img)

    cx = 400  # drone center x
    drone_x, drone_y = cx, DRONE_Y
    pkg_x, pkg_y = cx, DRONE_Y + 120
    rope_top_y = DRONE_Y + 27
    rope_bot_y = pkg_y - 11
    show_rope = True
    show_pkg_on_drone = True
    show_check = False
    text, text_color = "", WHITE

    if t < 3.0:
        # Phase 0: hovering
        text, text_color = "HOVERING  -  waiting...", WHITE
        # Gentle bob
        drone_y = DRONE_Y + int(3 * np.sin(t * 2.5))
        rope_top_y = drone_y + 27
        pkg_y = drone_y + 120
        rope_bot_y = pkg_y - 11

    elif t < 6.0:
        # Phase 1: rope extends, package lowers to ground
        p = (t - 3.0) / 3.0
        text, text_color = "PHASE 1  -  rope deploying", ORANGE
        target_pkg_y = GROUND_Y - 14
        pkg_y = int(lerp(DRONE_Y + 120, target_pkg_y, p))
        rope_top_y = drone_y + 27
        rope_bot_y = pkg_y - 11

    elif t < 9.0:
        # Phase 2: rope detaches & retracts, package stays
        p = (t - 6.0) / 3.0
        text, text_color = "PHASE 2  -  package released", RED
        pkg_y = GROUND_Y - 14
        show_pkg_on_drone = False
        rope_end_y = int(lerp(GROUND_Y - 25, drone_y + 40, p))
        rope_top_y = drone_y + 27
        rope_bot_y = rope_end_y
        if p > 0.7:
            show_rope = False

    else:
        # Phase 3: drone departs up-right
        p = (t - 9.0) / 3.0
        text, text_color = "COMPLETE  -  departing", GREEN
        drone_x = int(lerp(cx, cx + 180, p))
        drone_y = int(lerp(DRONE_Y, DRONE_Y - 200, p))
        pkg_y = GROUND_Y - 14
        show_rope = False
        show_pkg_on_drone = False
        show_check = True

    # Draw rope
    if show_rope:
        draw_rope(img, drone_x, rope_top_y, drone_x if show_pkg_on_drone else cx, rope_bot_y)

    # Draw package
    draw_package(img, cx if not show_pkg_on_drone else drone_x, pkg_y)

    # Draw checkmark next to grounded package
    if show_check:
        draw_checkmark(img, cx + 30, pkg_y)

    # Draw drone on top
    draw_drone(img, drone_x, drone_y)

    # Altitude reference lines
    cv2.putText(img, "3m", (15, DRONE_Y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(img, "0m", (15, GROUND_Y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.line(img, (40, DRONE_Y), (55, DRONE_Y), (150, 150, 150), 1)
    cv2.line(img, (40, GROUND_Y), (55, GROUND_Y), (150, 150, 150), 1)

    # Status text
    cv2.putText(img, text, (W//2 - len(text)*7, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2, cv2.LINE_AA)

    # Timeline
    draw_timeline(img, t, text)

    # Title
    cv2.putText(img, "Servo Release - Side View Demo", (W//2 - 180, H - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)

    return img


def main():
    cv2.namedWindow("Servo Release - Side View Demo", cv2.WINDOW_AUTOSIZE)
    paused = False
    t = 0.0
    last = time.time()

    while True:
        now = time.time()
        if not paused:
            t += now - last
            if t >= CYCLE:
                t -= CYCLE
        last = now

        img = render(t)
        if paused:
            cv2.putText(img, "PAUSED", (W//2 - 50, H//2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2, cv2.LINE_AA)

        cv2.imshow("Servo Release - Side View Demo", img)
        key = cv2.waitKey(max(1, int(1000 / FPS))) & 0xFF

        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('r'):
            t = 0.0

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
