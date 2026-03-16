"""
Interactive zoom + detect tool.
Load a high-res image, zoom in/out with scroll wheel, click to pan, SPACE to detect.

Usage:
    python tests/laptop/zoom_detect.py RealVideo/test_full_3425.jpg
    python tests/laptop/zoom_detect.py RealVideo/DJI_20260311172332_0001_V.MP4 --frame 3425
    python tests/laptop/zoom_detect.py RealVideo/DJI_20260311172332_0001_V.MP4 --frame 2033

Controls:
    Scroll wheel  = zoom in/out
    Click + drag  = pan
    SPACE         = run detection on current view
    S             = save current view + detection result
    R             = reset zoom
    Left/Right    = prev/next frame (video mode)
    Q             = quit
"""
import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import cv2
import numpy as np
from vision import VisionSystem

def main():
    parser = argparse.ArgumentParser(description="Interactive zoom + detect")
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

    img_h, img_w = full_img.shape[:2]
    print(f"Image: {img_w}x{img_h}")
    if is_video:
        print(f"Frame: {frame_num}/{total_frames}")

    # Init vision
    vs = VisionSystem(camera_index=None, model_path=args.model)
    if not vs.using_ai:
        print("Failed to load AI model")
        return

    # Zoom state
    zoom = 1.0
    cx, cy = img_w / 2, img_h / 2  # center of view
    disp_w, disp_h = 960, 540
    dragging = False
    drag_start = None
    drag_cx, drag_cy = cx, cy
    last_detection = None
    save_count = 0

    win = "Zoom + Detect"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    def get_crop():
        """Get the visible crop region at current zoom."""
        view_w = img_w / zoom
        view_h = img_h / zoom
        x1 = int(max(0, cx - view_w / 2))
        y1 = int(max(0, cy - view_h / 2))
        x2 = int(min(img_w, cx + view_w / 2))
        y2 = int(min(img_h, cy + view_h / 2))
        return x1, y1, x2, y2

    def on_mouse(event, mx, my, flags, param):
        nonlocal zoom, cx, cy, dragging, drag_start, drag_cx, drag_cy

        if event == cv2.EVENT_MOUSEWHEEL:
            # Zoom in/out
            if flags > 0:
                zoom = min(zoom * 1.3, 20.0)
            else:
                zoom = max(zoom / 1.3, 1.0)
            # Clamp center
            cx = np.clip(cx, img_w / zoom / 2, img_w - img_w / zoom / 2)
            cy = np.clip(cy, img_h / zoom / 2, img_h - img_h / zoom / 2)

        elif event == cv2.EVENT_LBUTTONDOWN:
            dragging = True
            drag_start = (mx, my)
            drag_cx, drag_cy = cx, cy

        elif event == cv2.EVENT_MOUSEMOVE and dragging:
            dx = (mx - drag_start[0]) / disp_w * (img_w / zoom)
            dy = (my - drag_start[1]) / disp_h * (img_h / zoom)
            cx = np.clip(drag_cx - dx, img_w / zoom / 2, img_w - img_w / zoom / 2)
            cy = np.clip(drag_cy - dy, img_h / zoom / 2, img_h - img_h / zoom / 2)

        elif event == cv2.EVENT_LBUTTONUP:
            dragging = False

    cv2.setMouseCallback(win, on_mouse)

    print("\nControls:")
    print("  W/S or +/- = zoom in/out    Click+drag = pan")
    print("  SPACE = detect    E = save    R = reset    Q = quit")
    if is_video:
        print("  A/D = prev/next frame")

    while True:
        x1, y1, x2, y2 = get_crop()
        crop = full_img[y1:y2, x1:x2].copy()
        crop_h, crop_w = crop.shape[:2]

        # Resize crop for display
        disp = cv2.resize(crop, (disp_w, disp_h))

        # Draw detection if exists
        if last_detection is not None:
            found, dx, dy, conf, det_region = last_detection
            if det_region == (x1, y1, x2, y2):  # same view
                if found:
                    # Scale detection coords to display
                    sx = disp_w / crop_w
                    sy = disp_h / crop_h
                    bw = vs.last_bbox_w * sx
                    bh = vs.last_bbox_h * sy
                    ddx = dx * sx
                    ddy = dy * sy
                    rx1 = int(ddx - bw/2)
                    ry1 = int(ddy - bh/2)
                    rx2 = int(ddx + bw/2)
                    ry2 = int(ddy + bh/2)
                    cv2.rectangle(disp, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)
                    cv2.putText(disp, f"DETECTED {conf:.2f}", (rx1, ry1-8),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # HUD
        cv2.rectangle(disp, (0, disp_h - 35), (disp_w, disp_h), (0, 0, 0), -1)
        crop_info = f"Zoom: {zoom:.1f}x | View: {crop_w}x{crop_h} | YOLO sees: 640x640"
        if is_video:
            crop_info += f" | Frame: {frame_num}"
        cv2.putText(disp, crop_info, (10, disp_h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        cv2.putText(disp, "SPACE=detect  W/S=zoom  Drag=pan  E=save  Q=quit",
                   (10, disp_h - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1)

        cv2.imshow(win, disp)
        key = cv2.waitKey(30) & 0xFF

        if key == ord('q'):
            break

        elif key == ord('w') or key == ord('+') or key == ord('='):
            zoom = min(zoom * 1.4, 20.0)
            cx = np.clip(cx, img_w / zoom / 2, img_w - img_w / zoom / 2)
            cy = np.clip(cy, img_h / zoom / 2, img_h - img_h / zoom / 2)
            last_detection = None

        elif key == ord('s') and not is_video:
            zoom = max(zoom / 1.4, 1.0)
            last_detection = None

        elif key == ord('s') and is_video and zoom > 1.0:
            zoom = max(zoom / 1.4, 1.0)
            last_detection = None

        elif key == ord('-'):
            zoom = max(zoom / 1.4, 1.0)
            last_detection = None

        elif key == ord(' '):
            # Run detection on current crop
            test_frame = crop.copy()
            found, dx, dy, conf = vs.detect_in_image(test_frame)
            last_detection = (found, dx, dy, conf, (x1, y1, x2, y2))
            if found:
                print(f"  DETECTED! conf={conf:.2f} at ({dx},{dy}) in {crop_w}x{crop_h} crop (zoom {zoom:.1f}x)")
            else:
                print(f"  Nothing detected in {crop_w}x{crop_h} crop (zoom {zoom:.1f}x)")

        elif key == ord('e'):
            save_count += 1
            status = "det" if (last_detection and last_detection[0]) else "nodet"
            fname = f"RealVideo/zoom_{save_count}_{crop_w}x{crop_h}_{status}.jpg"
            cv2.imwrite(fname, crop)
            print(f"  Saved: {fname}")

        elif key == ord('r'):
            zoom = 1.0
            cx, cy = img_w / 2, img_h / 2
            last_detection = None

        elif is_video and (key == 83 or key == ord('d')):  # right
            frame_num = min(frame_num + 30, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, full_img = cap.read()
            if not ret: break
            img_h, img_w = full_img.shape[:2]
            last_detection = None
            print(f"  Frame: {frame_num}")

        elif is_video and (key == 81 or key == ord('a')):  # left
            frame_num = max(frame_num - 30, 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, full_img = cap.read()
            if not ret: break
            img_h, img_w = full_img.shape[:2]
            last_detection = None
            print(f"  Frame: {frame_num}")

    if cap:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
