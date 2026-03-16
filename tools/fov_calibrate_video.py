"""
FOV Calibration from Video — click on a known-size object at different altitudes.

Usage:
    python tools/fov_calibrate_video.py RealVideo/DJI_0001_1456x1088_6fps.mp4
    python tools/fov_calibrate_video.py RealVideo/DJI_0001_1456x1088_6fps.mp4 --known-height 1.8

Instructions:
    1. Scrub to a frame where you can see the dummy clearly
    2. RIGHT-CLICK the TOP of the dummy, then RIGHT-CLICK the BOTTOM
    3. It records the pixel height + altitude, calculates FOV
    4. Repeat at 3-5 different altitudes for best accuracy
    5. Press Q to quit — shows the calibrated FOV

The tool uses SRT telemetry for altitude. Same SRT auto-detection as video_test.py.
"""
import sys, os, math, argparse, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cv2
import numpy as np


def parse_srt(srt_path):
    with open(srt_path, 'r') as f:
        text = f.read()
    entries = re.findall(
        r'FrameCnt:\s*(\d+)[\s\S]*?'
        r'latitude:\s*([\d.-]+)\][\s\S]*?'
        r'longitude:\s*([\d.-]+)\][\s\S]*?'
        r'rel_alt:\s*([\d.-]+)\s+abs_alt:\s*([\d.-]+)\][\s\S]*?'
        r'gb_yaw:\s*([\d.-]+)\s+gb_pitch:\s*([\d.-]+)',
        text
    )
    telem = {}
    for e in entries:
        telem[int(e[0])] = {
            'lat': float(e[1]), 'lon': float(e[2]),
            'rel_alt': float(e[3]), 'abs_alt': float(e[4]),
            'yaw': float(e[5]), 'pitch': float(e[6])
        }
    return telem


def find_srt(video_path):
    base = os.path.splitext(video_path)[0]
    for ext in ['.SRT', '.srt']:
        if os.path.exists(base + ext):
            return base + ext
    vdir = os.path.dirname(video_path)
    for f in os.listdir(vdir):
        if f.upper().endswith('.SRT'):
            return os.path.join(vdir, f)
    return None


def main():
    parser = argparse.ArgumentParser(description="FOV calibration from video")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--known-height", type=float, default=1.8, help="Known object height in meters (default 1.8)")
    parser.add_argument("--srt", default=None, help="SRT telemetry file")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"Cannot open: {args.video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    srt_path = args.srt or find_srt(args.video)
    telem = {}
    if srt_path:
        telem = parse_srt(srt_path)
        print(f"SRT loaded: {len(telem)} entries")
    else:
        print("WARNING: No SRT file — you'll need to enter altitude manually")

    # Display
    max_disp = 960
    scale = min(max_disp / vid_w, max_disp / vid_h, 1.0)
    disp_w = int(vid_w * scale)
    disp_h = int(vid_h * scale)

    win = "FOV Calibration — right-click top & bottom of dummy"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    print(f"\nVideo: {vid_w}x{vid_h} @ {fps:.0f}fps, {total} frames")
    print(f"Known object height: {args.known_height}m")
    print(f"\nInstructions:")
    print(f"  1. Scrub to frame with dummy visible")
    print(f"  2. RIGHT-CLICK top of dummy, then RIGHT-CLICK bottom")
    print(f"  3. It calculates FOV from pixel height + altitude")
    print(f"  4. Repeat at different altitudes (3-5 samples)")
    print(f"  5. Press Q to finish and see calibrated FOV")
    print(f"  Middle-click to clear current points")
    print()

    # State
    click_pts = []
    measurements = []  # list of (alt, px_dist, fov_calculated)
    frame_num = [0]
    frame = [None]
    paused = [True]
    zoom_level = [1.0]  # 1.0 = no zoom, 2.0 = 2x, etc.
    zoom_center = [disp_w // 2, disp_h // 2]  # zoom follows mouse

    def get_alt(fnum):
        """Get altitude for frame, searching nearby if needed."""
        t = telem.get(fnum)
        if t:
            return t['rel_alt']
        for off in range(1, 60):
            t = telem.get(fnum - off) or telem.get(fnum + off)
            if t:
                return t['rel_alt']
        return None

    def screen_to_image(sx, sy):
        """Convert screen (zoomed display) coords to original display coords."""
        z = zoom_level[0]
        cx, cy = zoom_center
        # Visible region in display coords
        half_w = disp_w / (2 * z)
        half_h = disp_h / (2 * z)
        left = cx - half_w
        top = cy - half_h
        # Screen pixel to display pixel
        ix = left + sx / z
        iy = top + sy / z
        return ix, iy

    def on_mouse(event, mx, my, flags, param):
        if event == cv2.EVENT_MOUSEWHEEL:
            # Zoom in/out centered on mouse position
            old_z = zoom_level[0]
            if flags > 0:
                zoom_level[0] = min(zoom_level[0] * 1.3, 10.0)
            else:
                zoom_level[0] = max(zoom_level[0] / 1.3, 1.0)
            # Update zoom center to mouse position (in image coords)
            ix, iy = screen_to_image(mx, my)
            zoom_center[0] = max(0, min(disp_w, int(ix)))
            zoom_center[1] = max(0, min(disp_h, int(iy)))
            return

        if event == cv2.EVENT_RBUTTONDOWN:
            # Convert screen click to display image coords
            ix, iy = screen_to_image(mx, my)
            click_pts.append((ix, iy))
            if len(click_pts) == 2:
                p1, p2 = click_pts
                # Distance in display pixels
                px_dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                # Convert display pixels to original video pixels
                vid_px_dist = px_dist / scale

                alt = get_alt(frame_num[0])
                if alt is None or alt < 1:
                    print("  No altitude data for this frame! Scrub to a frame with telemetry.")
                    click_pts.clear()
                    return

                # ground_w = known_height * vid_w / vid_px_dist
                # FOV_h = 2 * atan(ground_w / (2 * alt))
                # focal_length_px = (pixel_height * altitude) / known_height
                f_px = (vid_px_dist * alt) / args.known_height
                fov_h = 2 * math.degrees(math.atan(vid_w / (2 * f_px)))

                measurements.append((alt, vid_px_dist, f_px, fov_h))
                # Check consistency with previous samples
                if len(measurements) > 1:
                    f_vals = [m[2] for m in measurements]
                    f_avg = sum(f_vals) / len(f_vals)
                    spread = max(f_vals) - min(f_vals)
                    pct = 100 * spread / f_avg if f_avg > 0 else 0
                    print(f"  Sample {len(measurements)}: Alt={alt:.1f}m, {vid_px_dist:.0f}px, f={f_px:.0f}px, FOV={fov_h:.1f} deg  (spread: {pct:.1f}%)")
                else:
                    print(f"  Sample {len(measurements)}: Alt={alt:.1f}m, {vid_px_dist:.0f}px, f={f_px:.0f}px, FOV={fov_h:.1f} deg")

                click_pts.clear()
            elif len(click_pts) > 2:
                click_pts.clear()
        elif event == cv2.EVENT_MBUTTONDOWN:
            click_pts.clear()
        elif event == cv2.EVENT_MOUSEMOVE and zoom_level[0] > 1.0:
            # Pan zoom center slightly towards mouse on drag
            pass

    cv2.setMouseCallback(win, on_mouse)

    def on_trackbar(pos):
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ret, f = cap.read()
        if ret:
            frame[0] = f
            frame_num[0] = pos
    cv2.createTrackbar("Frame", win, 0, total - 1, on_trackbar)

    # Read first frame
    ret, f = cap.read()
    if ret:
        frame[0] = f
    paused[0] = True

    while True:
        if not paused[0]:
            ret, f = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                paused[0] = True
                continue
            frame[0] = f
            frame_num[0] = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            try:
                cv2.setTrackbarPos("Frame", win, frame_num[0])
            except cv2.error:
                pass

        if frame[0] is not None:
            disp = cv2.resize(frame[0], (disp_w, disp_h))

            # Apply zoom — crop and scale up
            z = zoom_level[0]
            if z > 1.01:
                cx, cy = zoom_center
                half_w = int(disp_w / (2 * z))
                half_h = int(disp_h / (2 * z))
                # Clamp zoom center
                cx = max(half_w, min(disp_w - half_w, cx))
                cy = max(half_h, min(disp_h - half_h, cy))
                zoom_center[0], zoom_center[1] = cx, cy
                crop = disp[cy - half_h:cy + half_h, cx - half_w:cx + half_w]
                disp = cv2.resize(crop, (disp_w, disp_h), interpolation=cv2.INTER_LINEAR)

            # Draw click points (convert from image coords to screen coords)
            def image_to_screen(ix, iy):
                cx, cy = zoom_center
                half_w = disp_w / (2 * z)
                half_h = disp_h / (2 * z)
                sx = (ix - (cx - half_w)) * z
                sy = (iy - (cy - half_h)) * z
                return int(sx), int(sy)

            for pt in click_pts:
                sp = image_to_screen(pt[0], pt[1])
                cv2.circle(disp, sp, 5, (0, 255, 255), -1)
            if len(click_pts) == 1:
                sp = image_to_screen(click_pts[0][0], click_pts[0][1])
                cv2.putText(disp, "Now click BOTTOM of dummy", (sp[0]+10, sp[1]),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            # Altitude + info
            alt = get_alt(frame_num[0])
            alt_str = f"Alt: {alt:.1f}m" if alt else "Alt: ???"
            zoom_str = f"  |  Zoom: {zoom_level[0]:.1f}x" if zoom_level[0] > 1.01 else ""
            cv2.rectangle(disp, (0, 0), (500, 90), (0, 0, 0), -1)
            cv2.putText(disp, f"{alt_str}  |  Frame {frame_num[0]}  |  SPACE=play/pause{zoom_str}", (8, 22),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            cv2.putText(disp, f"Samples: {len(measurements)}  |  Right-click top & bottom  |  Scroll=zoom", (8, 44),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1)

            # Show current calibration estimate
            if measurements:
                f_vals = [m[2] for m in measurements]
                f_avg = sum(f_vals) / len(f_vals)
                f_std = (sum((f - f_avg)**2 for f in f_vals) / len(f_vals))**0.5
                avg_fov = 2 * math.degrees(math.atan(vid_w / (2 * f_avg)))
                consistent = f_std / f_avg * 100 if f_avg > 0 else 999
                if consistent < 5:
                    color = (0, 255, 0)  # green = good
                    status = "GOOD"
                elif consistent < 15:
                    color = (0, 200, 255)  # yellow = ok
                    status = "OK"
                else:
                    color = (0, 0, 255)  # red = bad
                    status = "CHECK"
                cv2.putText(disp, f"f={f_avg:.0f}px  FOV={avg_fov:.1f} deg  spread={consistent:.1f}% [{status}]", (8, 66),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
                cv2.putText(disp, f"pixel*alt/1.8 should be constant across altitudes", (8, 84),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.35, (120, 120, 120), 1)

                # Show scale bar with calibrated FOV
                if alt and alt > 1:
                    ground_w = 2 * alt * math.tan(math.radians(avg_fov / 2))
                    px_1m = int(disp_w / ground_w)
                    if px_1m > 5:
                        sx1 = disp_w - px_1m - 15
                        sy1 = disp_h - 40
                        cv2.line(disp, (sx1, sy1), (disp_w - 15, sy1), (255, 255, 255), 2)
                        cv2.line(disp, (sx1, sy1-5), (sx1, sy1+5), (255, 255, 255), 2)
                        cv2.line(disp, (disp_w-15, sy1-5), (disp_w-15, sy1+5), (255, 255, 255), 2)
                        cv2.putText(disp, f"1m (FOV {avg_fov:.1f})", (sx1, sy1-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

            # Draw previous measurement lines faded
            for i, (m_alt, m_px, m_fpx, m_fov) in enumerate(measurements):
                cv2.putText(disp, f"  #{i+1}: alt={m_alt:.0f}m  px={m_px:.0f}  f={m_fpx:.0f}  FOV={m_fov:.1f}",
                           (8, disp_h - 15 - (len(measurements) - 1 - i) * 18),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.38, (150, 150, 150), 1)

            cv2.imshow(win, disp)

        key = cv2.waitKey(30 if not paused[0] else 50) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            paused[0] = not paused[0]

    cap.release()
    cv2.destroyAllWindows()

    # Final results
    if measurements:
        f_vals = [m[2] for m in measurements]
        f_avg = sum(f_vals) / len(f_vals)
        f_std = (sum((f - f_avg)**2 for f in f_vals) / len(f_vals))**0.5
        avg_fov = 2 * math.degrees(math.atan(vid_w / (2 * f_avg)))

        print(f"\n{'='*50}")
        print(f"FOV CALIBRATION RESULTS")
        print(f"{'='*50}")
        print(f"Known object height: {args.known_height}m")
        print(f"Video: {vid_w}x{vid_h}")
        print(f"Samples: {len(measurements)}")
        print()
        print(f"  {'#':>3}  {'Alt':>6}  {'Pixels':>7}  {'f_px':>7}  {'FOV':>7}  {'px*alt':>8}")
        print(f"  {'---':>3}  {'---':>6}  {'---':>7}  {'---':>7}  {'---':>7}  {'---':>8}")
        for i, (m_alt, m_px, m_fpx, m_fov) in enumerate(measurements):
            product = m_px * m_alt  # should be constant = known_height * f_px
            print(f"  {i+1:>3}  {m_alt:>5.1f}m  {m_px:>6.0f}px  {m_fpx:>6.0f}px  {m_fov:>5.1f} deg  {product:>7.0f}")
        print()
        print(f"  Focal length: {f_avg:.0f} px (+/- {f_std:.0f})")
        print(f"  CALIBRATED HFOV: {avg_fov:.1f} deg")
        print(f"  Consistency: {100*f_std/f_avg:.1f}% spread")
        print()

        # Check for altitude-dependent trend
        if len(measurements) >= 3:
            alts = [m[0] for m in measurements]
            fpxs = [m[2] for m in measurements]
            # Simple correlation check
            mean_a = sum(alts) / len(alts)
            mean_f = sum(fpxs) / len(fpxs)
            num = sum((a - mean_a) * (f - mean_f) for a, f in zip(alts, fpxs))
            den_a = sum((a - mean_a)**2 for a in alts)**0.5
            den_f = sum((f - mean_f)**2 for f in fpxs)**0.5
            corr = num / (den_a * den_f) if den_a > 0 and den_f > 0 else 0
            if abs(corr) > 0.5:
                trend = "INCREASES" if corr > 0 else "DECREASES"
                print(f"  WARNING: focal length {trend} with altitude (r={corr:.2f})")
                print(f"  This suggests altitude data may be inaccurate or camera isn't perfectly nadir")
            else:
                print(f"  No altitude-dependent trend detected (r={corr:.2f}) - good!")

        print()
        print(f"To apply in video_test.py:")
        print(f"  Replace all 'radians(36.5)' with 'radians({avg_fov:.1f})'")
        print(f"  Replace 'fov_h=36.5' with 'fov_h={avg_fov:.1f}'")
    else:
        print("\nNo measurements taken.")


if __name__ == "__main__":
    main()
