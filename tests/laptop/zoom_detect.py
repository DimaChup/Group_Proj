"""
Interactive zoom + detect + tiling tool.
Load a high-res image/video, zoom in/out, test detection at any crop level,
or run tiling across the full frame.

Usage:
    python tests/laptop/zoom_detect.py RealVideo/DJI_20260311172332_0001_V.MP4 --frame 3425
    python tests/laptop/zoom_detect.py RealVideo/DJI_20260311172332_0001_V.MP4 --frame 2033
    python tests/laptop/zoom_detect.py RealVideo/test_full_3425.jpg

Controls:
    W / +       = zoom in
    S / -       = zoom out
    Click+drag  = pan
    SPACE       = detect on current view (ZOOM mode)
    T           = run TILING on full frame (shows all tile detections)
    1 / 2 / 3   = tile size: 640 / 960 / 1280
    A / D       = prev/next frame (video, jumps 30 frames)
    F / G       = prev/next frame (video, jumps 150 frames — fast skip)
    E           = save current view (filename includes resolution)
    R           = reset zoom
    Q           = quit
"""
import sys, os, time, argparse, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import cv2
import numpy as np
from vision import VisionSystem


# ─── Tiling helpers ───

def tile_detect(vs, frame, tile_size=640, overlap=0.25, conf_thresh=0.3):
    """Split frame into overlapping tiles, detect in each, merge with NMS.
    Returns (detections, tile_count, grid) where grid is list of (x1,y1,x2,y2)."""
    h, w = frame.shape[:2]
    stride = int(tile_size * (1 - overlap))
    detections = []
    grid = []
    tile_count = 0

    for y0 in range(0, h - tile_size // 2, stride):
        for x0 in range(0, w - tile_size // 2, stride):
            x1 = min(x0, w - tile_size)
            y1 = min(y0, h - tile_size)
            x2 = min(x1 + tile_size, w)
            y2 = min(y1 + tile_size, h)
            x1, y1 = max(0, x1), max(0, y1)

            grid.append((x1, y1, x2, y2))
            tile = frame[y1:y2, x1:x2].copy()
            tile_count += 1

            found, tx, ty, conf = vs.detect_in_image(tile)
            if found and conf >= conf_thresh:
                orig_x = x1 + tx
                orig_y = y1 + ty
                bw = vs.last_bbox_w
                bh = vs.last_bbox_h
                detections.append((orig_x, orig_y, bw, bh, conf))

    if len(detections) > 1:
        detections = nms(detections, iou_thresh=0.3)

    return detections, tile_count, grid


def nms(dets, iou_thresh=0.3):
    """Non-maximum suppression on (cx, cy, w, h, conf) detections."""
    boxes = [(cx-w//2, cy-h//2, cx+w//2, cy+h//2, conf) for cx, cy, w, h, conf in dets]
    boxes.sort(key=lambda b: b[4], reverse=True)
    keep = []
    while boxes:
        best = boxes.pop(0)
        keep.append(best)
        boxes = [b for b in boxes if iou_calc(best, b) < iou_thresh]
    return [((x1+x2)//2, (y1+y2)//2, x2-x1, y2-y1, conf) for x1, y1, x2, y2, conf in keep]


def iou_calc(a, b):
    xi1, yi1 = max(a[0], b[0]), max(a[1], b[1])
    xi2, yi2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, xi2-xi1) * max(0, yi2-yi1)
    area_a = (a[2]-a[0]) * (a[3]-a[1])
    area_b = (b[2]-b[0]) * (b[3]-b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0


def main():
    parser = argparse.ArgumentParser(description="Interactive zoom + detect + tiling")
    parser.add_argument("source", help="Image or video file")
    parser.add_argument("--frame", type=int, default=0, help="Frame number (video only)")
    parser.add_argument("--model", default="best.tflite", help="Model path")
    parser.add_argument("--conf", type=float, default=None, help="Confidence threshold")
    args = parser.parse_args()

    if args.conf is not None:
        try:
            import config
            config.CONFIDENCE_THRESHOLD = args.conf
        except ImportError:
            pass

    # Load image
    is_video = args.source.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
    cap = None
    frame_num = args.frame

    if is_video:
        cap = cv2.VideoCapture(args.source)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, full_img = cap.read()
        if not ret:
            print("Cannot read frame")
            return
    else:
        full_img = cv2.imread(args.source)
        if full_img is None:
            print(f"Cannot load: {args.source}")
            return
        total_frames = 1
        fps = 30

    img_h, img_w = full_img.shape[:2]
    print(f"Image: {img_w}x{img_h}")
    if is_video:
        print(f"Frame: {frame_num}/{total_frames} ({frame_num/fps:.1f}s)")

    # Show window immediately with loading message
    win = "Zoom + Detect + Tiling"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    splash = np.zeros((200, 500, 3), dtype=np.uint8)
    cv2.putText(splash, f"Loading {os.path.basename(args.model)}...", (30, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
    cv2.imshow(win, splash)
    cv2.waitKey(1)

    # Init vision
    vs = VisionSystem(camera_index=None, model_path=args.model)
    if not vs.using_ai:
        print("Failed to load AI model")
        return

    # State
    zoom = 1.0
    cx, cy = img_w / 2, img_h / 2
    # Auto-detect screen size, use 60% of screen height for main view
    try:
        import ctypes
        user32 = ctypes.windll.user32
        screen_w, screen_h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    except Exception:
        screen_w, screen_h = 1920, 1080
    # Main view takes ~55% of screen height (leave room for YOLO panel + taskbar)
    disp_h = int(screen_h * 0.50)
    disp_w = int(disp_h * img_w / img_h)
    # Cap width to 90% of screen
    if disp_w > screen_w * 0.9:
        disp_w = int(screen_w * 0.9)
        disp_h = int(disp_w * img_h / img_w)
    dragging = False
    drag_start = None
    drag_cx, drag_cy = cx, cy
    last_detection = None       # (found, dx, dy, conf, region) for zoom mode
    tile_detections = None      # list of (cx, cy, w, h, conf) for tiling mode
    tile_grid = None            # list of (x1, y1, x2, y2) tile rectangles
    tile_info = ""              # tiling stats string
    tile_size = 640
    save_count = 0
    yolo_view_mode = 0          # V cycles: 0=off, 1=1x, 2=2x, 3=4x, 4=8x
    yolo_cx, yolo_cy = 320, 320  # center of YOLO zoom view (in 640x640 coords)
    yolo_dragging = False
    yolo_drag_start = None
    yolo_drag_cx, yolo_drag_cy = 320, 320

    # Video scrub slider
    seeking = [False]
    if is_video:
        def on_trackbar(pos):
            nonlocal frame_num, full_img, img_h, img_w, last_detection, tile_detections, tile_info
            seeking[0] = True
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ret, new_frame = cap.read()
            if ret:
                full_img = new_frame
                frame_num = pos
                img_h, img_w = full_img.shape[:2]
                last_detection = None
                tile_detections = None
                tile_grid = None
                tile_info = ""
        cv2.createTrackbar("Frame", win, frame_num, total_frames - 1, on_trackbar)

    def get_crop():
        view_w = img_w / zoom
        view_h = img_h / zoom
        x1 = int(max(0, cx - view_w / 2))
        y1 = int(max(0, cy - view_h / 2))
        x2 = int(min(img_w, cx + view_w / 2))
        y2 = int(min(img_h, cy + view_h / 2))
        return x1, y1, x2, y2

    def on_mouse(event, mx, my, flags, param):
        nonlocal zoom, cx, cy, dragging, drag_start, drag_cx, drag_cy, last_detection, tile_detections
        nonlocal yolo_cx, yolo_cy, yolo_dragging, yolo_drag_start, yolo_drag_cx, yolo_drag_cy

        # Check if mouse is in YOLO panel (below main view)
        yolo_panel_size = min(disp_h, screen_h - disp_h - 80) if yolo_view_mode > 0 else 0
        in_yolo = yolo_view_mode > 0 and my > disp_h and mx < yolo_panel_size

        if event == cv2.EVENT_MOUSEWHEEL:
            if in_yolo:
                # Scroll zooms YOLO view
                pass  # use V key instead for clarity
            else:
                if flags > 0:
                    zoom = min(zoom * 1.3, 20.0)
                else:
                    zoom = max(zoom / 1.3, 1.0)
                cx = np.clip(cx, img_w / zoom / 2, img_w - img_w / zoom / 2)
                cy = np.clip(cy, img_h / zoom / 2, img_h - img_h / zoom / 2)
                last_detection = None

        elif event == cv2.EVENT_LBUTTONDOWN:
            if in_yolo:
                yolo_dragging = True
                yolo_drag_start = (mx, my)
                yolo_drag_cx, yolo_drag_cy = yolo_cx, yolo_cy
            else:
                dragging = True
                drag_start = (mx, my)
                drag_cx, drag_cy = cx, cy

        elif event == cv2.EVENT_MOUSEMOVE:
            if yolo_dragging:
                yolo_zoom = [1, 1, 2, 4, 8][yolo_view_mode]
                view_size = 640 / yolo_zoom
                dx = (mx - yolo_drag_start[0]) * (640 / 640) / yolo_zoom
                dy = (my - yolo_drag_start[1]) * (640 / 640) / yolo_zoom
                half = view_size / 2
                yolo_cx = np.clip(yolo_drag_cx - dx, half, 640 - half)
                yolo_cy = np.clip(yolo_drag_cy - dy, half, 640 - half)
            elif dragging:
                dx = (mx - drag_start[0]) / disp_w * (img_w / zoom)
                dy = (my - drag_start[1]) / disp_h * (img_h / zoom)
                cx = np.clip(drag_cx - dx, img_w / zoom / 2, img_w - img_w / zoom / 2)
                cy = np.clip(drag_cy - dy, img_h / zoom / 2, img_h - img_h / zoom / 2)

        elif event == cv2.EVENT_LBUTTONUP:
            dragging = False
            yolo_dragging = False

    cv2.setMouseCallback(win, on_mouse)

    print("\nControls:")
    print("  W/+ = zoom in    S/- = zoom out    Drag = pan")
    print("  SPACE = detect current view    T = tiling on full frame")
    print("  1/2/3 = tile size (640/960/1280)")
    print("  V = toggle YOLO view (what the model actually sees)")
    print("  A/D = skip 30 frames    F/G = skip 150 frames")
    print("  E = save    R = reset    Q = quit")

    while True:
        x1, y1, x2, y2 = get_crop()
        crop = full_img[y1:y2, x1:x2].copy()
        crop_h, crop_w = crop.shape[:2]

        # Normal view (always)
        disp = cv2.resize(crop, (disp_w, disp_h))
        sx = disp_w / crop_w
        sy = disp_h / crop_h

        # YOLO view: show the actual 640x640 below the main view
        if yolo_view_mode > 0:
            yolo_input = cv2.resize(crop, (640, 640))
            yolo_zoom_level = [1, 1, 2, 4, 8][yolo_view_mode]
            yolo_label = f"YOLO INPUT 640x640"

            if yolo_zoom_level == 1:
                yolo_show = yolo_input.copy()
                # Draw crosshair at center
                cv2.drawMarker(yolo_show, (int(yolo_cx), int(yolo_cy)), (0, 200, 255),
                              cv2.MARKER_CROSS, 20, 1)
            else:
                # Zoom into yolo_cx, yolo_cy
                half = 640 // (2 * yolo_zoom_level)
                yx1 = int(max(0, yolo_cy - half))
                yx2 = int(min(640, yolo_cy + half))
                yx1_x = int(max(0, yolo_cx - half))
                yx2_x = int(min(640, yolo_cx + half))
                yolo_crop_region = yolo_input[yx1:yx2, yx1_x:yx2_x]
                yolo_show = cv2.resize(yolo_crop_region, (640, 640), interpolation=cv2.INTER_NEAREST)
                actual_w = yx2_x - yx1_x
                actual_h = yx2 - yx1
                yolo_label = f"YOLO {yolo_zoom_level}x ZOOM ({actual_w}x{actual_h}px region) — drag to pan"

            # Draw highlight box on main view showing where YOLO zoom is looking
            if yolo_zoom_level > 1:
                half = 640 // (2 * yolo_zoom_level)
                # Map YOLO coords back to main display coords
                # yolo_cx/yolo_cy are in 640x640 space, map to crop space then display space
                box_x1 = int((yolo_cx - half) / 640 * crop_w * sx)
                box_y1 = int((yolo_cy - half) / 640 * crop_h * sy)
                box_x2 = int((yolo_cx + half) / 640 * crop_w * sx)
                box_y2 = int((yolo_cy + half) / 640 * crop_h * sy)
                cv2.rectangle(disp, (box_x1, box_y1), (box_x2, box_y2), (0, 100, 255), 2)
                cv2.putText(disp, f"YOLO {yolo_zoom_level}x", (box_x1, box_y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 100, 255), 1)

            # Build panel: scale YOLO view to fit remaining screen space
            yolo_disp_h = min(disp_h, screen_h - disp_h - 80)  # fit below main view
            yolo_disp_size = yolo_disp_h  # square
            yolo_show_resized = cv2.resize(yolo_show, (yolo_disp_size, yolo_disp_size))

            panel_h = yolo_disp_h
            yolo_panel = np.zeros((panel_h, disp_w, 3), dtype=np.uint8)
            yolo_panel[:yolo_disp_size, :yolo_disp_size] = yolo_show_resized
            cv2.rectangle(yolo_panel, (0, 0), (yolo_disp_size-1, yolo_disp_size-1), (0, 100, 255), 2)
            cv2.putText(yolo_panel, yolo_label, (8, 22),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 100, 255), 2)

            # Info on right side
            ratio = max(crop_w, crop_h) / 640
            info_x = yolo_disp_size + 15
            fs = 0.42
            cv2.putText(yolo_panel, f"Main zoom: {zoom:.1f}x", (info_x, 30), cv2.FONT_HERSHEY_SIMPLEX, fs, (200, 200, 200), 1)
            cv2.putText(yolo_panel, f"View: {crop_w}x{crop_h}", (info_x, 55), cv2.FONT_HERSHEY_SIMPLEX, fs, (200, 200, 200), 1)
            cv2.putText(yolo_panel, f"Squeeze: {ratio:.1f}x", (info_x, 80), cv2.FONT_HERSHEY_SIMPLEX, fs, (0, 100, 255), 1)
            cv2.putText(yolo_panel, f"Person ~{max(1,int(40/ratio))}px in YOLO", (info_x, 105), cv2.FONT_HERSHEY_SIMPLEX, fs, (0, 200, 255), 1)
            cv2.putText(yolo_panel, f"YOLO zoom: {yolo_zoom_level}x", (info_x, 130), cv2.FONT_HERSHEY_SIMPLEX, fs, (0, 200, 255), 1)
            cv2.putText(yolo_panel, "V=cycle  Drag=pan", (info_x, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)

            disp = np.vstack([disp, yolo_panel])

        # Draw tile grid overlay
        if tile_grid:
            for i, (gx1, gy1, gx2, gy2) in enumerate(tile_grid):
                # Map from full image coords to current view
                dx1 = int((gx1 - x1) * sx)
                dy1 = int((gy1 - y1) * sy)
                dx2 = int((gx2 - x1) * sx)
                dy2 = int((gy2 - y1) * sy)
                # Only draw if visible
                if dx2 > 0 and dy2 > 0 and dx1 < disp_w and dy1 < disp_h:
                    # Cyan grid lines, semi-transparent feel
                    cv2.rectangle(disp, (dx1, dy1), (dx2, dy2), (255, 200, 0), 1)
                    # Tile number in corner
                    cv2.putText(disp, str(i+1), (max(0, dx1+3), max(12, dy1+14)),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 200, 0), 1)

        # Draw zoom detection
        if last_detection is not None:
            found, dx, dy, conf, det_region = last_detection
            if det_region == (x1, y1, x2, y2) and found:
                bw = vs.last_bbox_w * sx
                bh = vs.last_bbox_h * sy
                ddx, ddy = dx * sx, dy * sy
                rx1, ry1 = int(ddx - bw/2), int(ddy - bh/2)
                rx2, ry2 = int(ddx + bw/2), int(ddy + bh/2)
                cv2.rectangle(disp, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)
                cv2.putText(disp, f"ZOOM {conf:.2f}", (rx1, ry1-8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw tiling detections (mapped to current view)
        if tile_detections:
            for tcx, tcy, tw, th, tconf in tile_detections:
                # Map from full image coords to current crop coords
                dcx = (tcx - x1) * sx
                dcy = (tcy - y1) * sy
                dw = tw * sx
                dh = th * sy
                # Only draw if visible in current view
                if 0 < dcx < disp_w and 0 < dcy < disp_h:
                    rx1 = int(dcx - dw/2)
                    ry1 = int(dcy - dh/2)
                    rx2 = int(dcx + dw/2)
                    ry2 = int(dcy + dh/2)
                    cv2.rectangle(disp, (rx1, ry1), (rx2, ry2), (0, 200, 255), 2)
                    cv2.putText(disp, f"TILE {tconf:.2f}", (rx1, ry1-8),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

        # HUD — 3 lines
        hud_h = 50
        actual_w = disp.shape[1]  # wider in split view
        cv2.rectangle(disp, (0, disp_h - hud_h), (actual_w, disp_h), (0, 0, 0), -1)

        line1 = f"Zoom: {zoom:.1f}x | View: {crop_w}x{crop_h} | YOLO: 640x640 | Tile: {tile_size}px"
        if is_video:
            ts = frame_num / fps
            line1 += f" | Frame: {frame_num} ({ts:.1f}s)"
        cv2.putText(disp, line1, (10, disp_h - 32), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)

        if tile_info:
            cv2.putText(disp, tile_info, (10, disp_h - 19), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 200, 255), 1)
        else:
            # Estimate tiles for current full frame
            stride = int(tile_size * 0.75)
            est_tiles = max(1, (img_w - tile_size//2) // stride + 1) * max(1, (img_h - tile_size//2) // stride + 1)
            cv2.putText(disp, f"T=tile full frame ({est_tiles} tiles, ~{est_tiles*206}ms on Pi)",
                       (10, disp_h - 19), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)

        cv2.putText(disp, "SPACE=detect  T=tile  V=yolo view  W/S=zoom  1/2/3=tilesize  A/D/F/G=skip  E=save  Q=quit",
                   (10, disp_h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (120, 120, 120), 1)

        cv2.imshow(win, disp)
        key = cv2.waitKey(30) & 0xFF

        if key == ord('q'):
            break

        elif key == ord('w') or key == ord('+') or key == ord('='):
            zoom = min(zoom * 1.4, 20.0)
            cx = np.clip(cx, img_w / zoom / 2, img_w - img_w / zoom / 2)
            cy = np.clip(cy, img_h / zoom / 2, img_h - img_h / zoom / 2)
            last_detection = None

        elif key == ord('s') or key == ord('-'):
            zoom = max(zoom / 1.4, 1.0)
            last_detection = None

        elif key == ord(' '):
            # Zoom detection on current crop (threaded to avoid freeze)
            det_region = (x1, y1, x2, y2)
            det_frame = crop.copy()
            det_cw, det_ch = crop_w, crop_h
            det_zoom = zoom
            tile_detections = None
            tile_info = ""
            # Show "detecting" immediately
            tmp = disp.copy()
            cv2.putText(tmp, "DETECTING...", (disp_w//2 - 80, disp_h//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imshow(win, tmp)
            cv2.waitKey(1)
            t0 = time.perf_counter()
            found, dx, dy, conf = vs.detect_in_image(det_frame)
            dt = (time.perf_counter() - t0) * 1000
            last_detection = (found, dx, dy, conf, det_region)
            if found:
                print(f"  ZOOM DETECT: conf={conf:.2f} at ({dx},{dy}) in {det_cw}x{det_ch} ({dt:.0f}ms, zoom {det_zoom:.1f}x)")
            else:
                print(f"  ZOOM DETECT: nothing in {det_cw}x{det_ch} ({dt:.0f}ms, zoom {det_zoom:.1f}x)")

        elif key == ord('t'):
            # Tiling on full frame
            print(f"  TILING {tile_size}px on {img_w}x{img_h}...")
            tmp = disp.copy()
            cv2.putText(tmp, "TILING...", (disp_w//2 - 60, disp_h//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
            cv2.imshow(win, tmp)
            cv2.waitKey(1)
            t0 = time.perf_counter()
            tile_detections, n_tiles, tile_grid = tile_detect(vs, full_img, tile_size, overlap=0.25, conf_thresh=0.3)
            dt = (time.perf_counter() - t0) * 1000
            last_detection = None
            tile_info = f"TILING: {len(tile_detections)} found | {n_tiles} tiles | {tile_size}px | {dt:.0f}ms | Pi est: {n_tiles*206}ms"
            print(f"  {tile_info}")
            for i, (tcx, tcy, tw, th, tconf) in enumerate(tile_detections):
                print(f"    [{i+1}] conf={tconf:.2f} at ({tcx},{tcy}) size={tw}x{th}")

        elif key == ord('1'):
            tile_size = 640
            tile_detections = None
            tile_grid = None
            tile_info = ""
            print(f"  Tile size: {tile_size}px")
        elif key == ord('2'):
            tile_size = 960
            tile_detections = None
            tile_grid = None
            tile_info = ""
            print(f"  Tile size: {tile_size}px")
        elif key == ord('3'):
            tile_size = 1280
            tile_detections = None
            tile_grid = None
            tile_info = ""
            print(f"  Tile size: {tile_size}px")

        elif key == ord('e'):
            save_count += 1
            has_det = (last_detection and last_detection[0]) or bool(tile_detections)
            status = "det" if has_det else "nodet"
            fname = f"RealVideo/zoom_{save_count}_{crop_w}x{crop_h}_{status}.jpg"
            cv2.imwrite(fname, crop)
            print(f"  Saved: {fname}")

        elif key == ord('v'):
            yolo_view_mode = (yolo_view_mode + 1) % 5
            labels = ["OFF", "1x", "2x", "4x", "8x"]
            print(f"  YOLO view: {labels[yolo_view_mode]}")

        elif key == ord('r'):
            zoom = 1.0
            cx, cy = img_w / 2, img_h / 2
            last_detection = None
            tile_detections = None
            tile_grid = None
            tile_info = ""

        # Frame navigation
        elif is_video and key == ord('d'):
            frame_num = min(frame_num + 30, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, full_img = cap.read()
            if not ret: break
            img_h, img_w = full_img.shape[:2]
            last_detection = None
            tile_detections = None
            tile_grid = None
            tile_info = ""
            print(f"  Frame: {frame_num} ({frame_num/fps:.1f}s)")
            try: cv2.setTrackbarPos("Frame", win, frame_num)
            except cv2.error: pass

        elif is_video and key == ord('a'):
            frame_num = max(frame_num - 30, 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, full_img = cap.read()
            if not ret: break
            img_h, img_w = full_img.shape[:2]
            last_detection = None
            tile_detections = None
            tile_grid = None
            tile_info = ""
            print(f"  Frame: {frame_num} ({frame_num/fps:.1f}s)")
            try: cv2.setTrackbarPos("Frame", win, frame_num)
            except cv2.error: pass

        elif is_video and key == ord('g'):
            frame_num = min(frame_num + 150, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, full_img = cap.read()
            if not ret: break
            img_h, img_w = full_img.shape[:2]
            last_detection = None
            tile_detections = None
            tile_grid = None
            tile_info = ""
            print(f"  Frame: {frame_num} ({frame_num/fps:.1f}s) [fast skip]")
            try: cv2.setTrackbarPos("Frame", win, frame_num)
            except cv2.error: pass

        elif is_video and key == ord('f'):
            frame_num = max(frame_num - 150, 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, full_img = cap.read()
            if not ret: break
            img_h, img_w = full_img.shape[:2]
            last_detection = None
            tile_detections = None
            tile_grid = None
            tile_info = ""
            print(f"  Frame: {frame_num} ({frame_num/fps:.1f}s) [fast skip]")
            try: cv2.setTrackbarPos("Frame", win, frame_num)
            except cv2.error: pass

    if cap:
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
