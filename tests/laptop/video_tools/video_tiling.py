"""
Play video with TILING detection — runs detection on overlapping tiles per frame.

Usage:
    python tests/laptop/video_tools/video_tiling.py RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4
    python tests/laptop/video_tools/video_tiling.py RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4 --tile-size 640
    python tests/laptop/video_tools/video_tiling.py RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4 --save output.mp4

Controls:
    SPACE     = pause/resume
    Q         = quit
    A/D       = skip 5s back/forward
    F/G       = skip 30s back/forward
    +/-       = speed up/slow down
    1/2/3     = tile size 640/960/1280
    T         = toggle tiling on/off (single-frame detection when off)
    Slider    = scrub through video
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import cv2
import numpy as np
from vision import VisionSystem


def tile_detect(vs, frame, tile_size=640, overlap=0.25, conf_thresh=0.3):
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
                detections.append((x1 + tx, y1 + ty, vs.last_bbox_w, vs.last_bbox_h, conf))

    if len(detections) > 1:
        detections = nms(detections)
    return detections, tile_count, grid


def nms(dets, iou_thresh=0.3):
    boxes = [(cx-w//2, cy-h//2, cx+w//2, cy+h//2, conf) for cx, cy, w, h, conf in dets]
    boxes.sort(key=lambda b: b[4], reverse=True)
    keep = []
    while boxes:
        best = boxes.pop(0)
        keep.append(best)
        boxes = [b for b in boxes if iou(best, b) < iou_thresh]
    return [((x1+x2)//2, (y1+y2)//2, x2-x1, y2-y1, c) for x1, y1, x2, y2, c in keep]


def iou(a, b):
    xi1, yi1 = max(a[0], b[0]), max(a[1], b[1])
    xi2, yi2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, xi2-xi1) * max(0, yi2-yi1)
    ua = (a[2]-a[0])*(a[3]-a[1])
    ub = (b[2]-b[0])*(b[3]-b[1])
    return inter / (ua + ub - inter) if (ua + ub - inter) > 0 else 0


def main():
    parser = argparse.ArgumentParser(description="Video playback with tiling detection")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--model", default="best.tflite", help="Model path")
    parser.add_argument("--tile-size", type=int, default=960, help="Tile size (default 960)")
    parser.add_argument("--conf", type=float, default=0.3, help="Confidence threshold")
    parser.add_argument("--display-width", type=int, default=1280, help="Display width")
    parser.add_argument("--save", default=None, help="Save output video")
    args = parser.parse_args()

    if args.conf:
        try:
            import config
            config.CONFIDENCE_THRESHOLD = args.conf
        except ImportError:
            pass

    vs = VisionSystem(camera_index=None, model_path=args.model)
    if not vs.using_ai:
        print("Failed to load AI model")
        return

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"Cannot open: {args.video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps

    disp_scale = args.display_width / vid_w
    disp_w = args.display_width
    disp_h = int(vid_h * disp_scale)

    print(f"Video: {vid_w}x{vid_h} @ {fps:.0f}fps, {total_frames} frames ({duration:.1f}s)")
    print(f"Display: {disp_w}x{disp_h}")
    print(f"Tile size: {args.tile_size}px")
    print()
    print("Controls: SPACE=pause  +/-=speed  A/D=5s  F/G=30s  1/2/3=tilesize  T=toggle tiling  Q=quit")

    win = "Video Tiling Detection"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    seeking = [False]
    def on_trackbar(pos):
        seeking[0] = True
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
    cv2.createTrackbar("Frame", win, 0, total_frames - 1, on_trackbar)

    writer = None
    if args.save:
        writer = cv2.VideoWriter(args.save, cv2.VideoWriter_fourcc(*'mp4v'), fps, (disp_w, disp_h))
        print(f"Saving to: {args.save}")

    paused = False
    speed = 1.0
    tile_size = args.tile_size
    use_tiling = True
    total_dets = 0
    frame_num = 0
    last_grid = None

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break
            frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            if not seeking[0]:
                try:
                    cv2.setTrackbarPos("Frame", win, frame_num)
                except cv2.error:
                    pass
            seeking[0] = False

            timestamp = frame_num / fps

            # Run detection
            t0 = time.perf_counter()
            if use_tiling:
                dets, n_tiles, last_grid = tile_detect(vs, frame, tile_size, overlap=0.25, conf_thresh=args.conf)
            else:
                found, x, y, conf = vs.detect_in_image(frame.copy())
                n_tiles = 1
                last_grid = None
                dets = [(x, y, vs.last_bbox_w, vs.last_bbox_h, conf)] if found else []
            dt = (time.perf_counter() - t0) * 1000
            total_dets += len(dets)

            # Draw on display frame
            disp = cv2.resize(frame, (disp_w, disp_h))

            # Draw tile grid
            if last_grid:
                for gx1, gy1, gx2, gy2 in last_grid:
                    dx1 = int(gx1 * disp_scale)
                    dy1 = int(gy1 * disp_scale)
                    dx2 = int(gx2 * disp_scale)
                    dy2 = int(gy2 * disp_scale)
                    cv2.rectangle(disp, (dx1, dy1), (dx2, dy2), (255, 200, 0), 1)

            # Draw detections
            for cx, cy, bw, bh, conf in dets:
                rx1 = int((cx - bw/2) * disp_scale)
                ry1 = int((cy - bh/2) * disp_scale)
                rx2 = int((cx + bw/2) * disp_scale)
                ry2 = int((cy + bh/2) * disp_scale)
                cv2.rectangle(disp, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)
                label = f"{'TILE' if use_tiling else 'DET'} {conf:.2f}"
                cv2.putText(disp, label, (rx1, ry1-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # HUD
            hud_h = 45
            cv2.rectangle(disp, (0, disp_h - hud_h), (disp_w, disp_h), (0, 0, 0), -1)
            # Progress bar
            progress = frame_num / total_frames
            cv2.rectangle(disp, (0, disp_h - hud_h), (int(disp_w * progress), disp_h - hud_h + 3), (0, 200, 200), -1)

            mode_str = f"TILING {tile_size}px ({n_tiles} tiles)" if use_tiling else "SINGLE FRAME"
            pi_est = n_tiles * 206
            line1 = f"{timestamp:.1f}s / {duration:.1f}s | {dt:.0f}ms | {mode_str} | Pi est: {pi_est}ms | Speed: {speed:.1f}x"
            line2 = f"Dets this frame: {len(dets)} | Total: {total_dets} | {os.path.basename(args.model)}"
            cv2.putText(disp, line1, (10, disp_h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)
            cv2.putText(disp, line2, (10, disp_h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)

            if writer:
                writer.write(disp)

            cv2.imshow(win, disp)

        # Key handling
        delay = max(1, int((1000 / fps) / speed)) if not paused else 50
        key = cv2.waitKey(delay) & 0xFF

        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
            print("PAUSED" if paused else "PLAYING")
        elif key == ord('+') or key == ord('='):
            speed = min(speed + 0.5, 16.0)
            print(f"Speed: {speed}x")
        elif key == ord('-'):
            speed = max(speed - 0.5, 0.25)
            print(f"Speed: {speed}x")
        elif key == ord('d'):
            new = min(frame_num + int(fps * 5), total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new)
            frame_num = new
        elif key == ord('a'):
            new = max(frame_num - int(fps * 5), 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new)
            frame_num = new
        elif key == ord('g'):
            new = min(frame_num + int(fps * 30), total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new)
            frame_num = new
        elif key == ord('f'):
            new = max(frame_num - int(fps * 30), 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new)
            frame_num = new
        elif key == ord('t'):
            use_tiling = not use_tiling
            print(f"Tiling: {'ON' if use_tiling else 'OFF (single frame)'}")
        elif key == ord('1'):
            tile_size = 640
            print(f"Tile size: {tile_size}px")
        elif key == ord('2'):
            tile_size = 960
            print(f"Tile size: {tile_size}px")
        elif key == ord('3'):
            tile_size = 1280
            print(f"Tile size: {tile_size}px")

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()

    print(f"\nTotal detections: {total_dets}")


if __name__ == "__main__":
    main()
