"""
APPROACH A: TILING — split high-res frame into overlapping 640x640 crops.
Run detection on each tile, merge results with NMS.

Usage:
    python tests/laptop/video_tools/detect_tiling.py RealVideo/DJI_20260311172332_0001_V.MP4 --frame 3425
    python tests/laptop/video_tools/detect_tiling.py RealVideo/test_full_3425.jpg
    python tests/laptop/video_tools/detect_tiling.py RealVideo/DJI_20260311172332_0001_V.MP4 --frame 3425 --tile-size 960
    python tests/laptop/video_tools/detect_tiling.py RealVideo/DJI_20260311172332_0001_V.MP4 --video  (run over whole video)

Controls (image mode): A/D=prev/next frame  Q=quit
Controls (video mode): SPACE=pause  A/D=skip 5s  +/-=speed  Q=quit
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import cv2
import numpy as np
from vision import VisionSystem


def tile_detect(vs, frame, tile_size=640, overlap=0.25, conf_thresh=0.4):
    """
    Split frame into overlapping tiles, run detection on each.
    Returns list of (x, y, w, h, conf) in original frame coords.
    """
    h, w = frame.shape[:2]
    stride = int(tile_size * (1 - overlap))
    detections = []

    for y0 in range(0, h - tile_size // 2, stride):
        for x0 in range(0, w - tile_size // 2, stride):
            x1 = min(x0, w - tile_size)
            y1 = min(y0, h - tile_size)
            x2 = x1 + tile_size
            y2 = y1 + tile_size

            # Clamp
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            tile = frame[y1:y2, x1:x2].copy()

            found, tx, ty, conf = vs.detect_in_image(tile)
            if found and conf >= conf_thresh:
                # Map back to original coords
                orig_x = x1 + tx
                orig_y = y1 + ty
                bw = vs.last_bbox_w
                bh = vs.last_bbox_h
                detections.append((orig_x, orig_y, bw, bh, conf))

    # Simple NMS: merge overlapping detections (keep highest conf)
    if len(detections) > 1:
        detections = nms(detections, iou_thresh=0.3)

    return detections


def nms(dets, iou_thresh=0.3):
    """Non-maximum suppression on (cx, cy, w, h, conf) detections."""
    if not dets:
        return []

    # Convert to x1y1x2y2
    boxes = []
    for cx, cy, bw, bh, conf in dets:
        boxes.append((cx - bw//2, cy - bh//2, cx + bw//2, cy + bh//2, conf))

    # Sort by confidence descending
    boxes.sort(key=lambda b: b[4], reverse=True)
    keep = []

    while boxes:
        best = boxes.pop(0)
        keep.append(best)
        remaining = []
        for b in boxes:
            if iou(best, b) < iou_thresh:
                remaining.append(b)
        boxes = remaining

    # Convert back to cx, cy, w, h, conf
    result = []
    for x1, y1, x2, y2, conf in keep:
        result.append(((x1+x2)//2, (y1+y2)//2, x2-x1, y2-y1, conf))
    return result


def iou(a, b):
    """IoU between two (x1,y1,x2,y2,conf) boxes."""
    xi1 = max(a[0], b[0])
    yi1 = max(a[1], b[1])
    xi2 = min(a[2], b[2])
    yi2 = min(a[3], b[3])
    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    area_a = (a[2]-a[0]) * (a[3]-a[1])
    area_b = (b[2]-b[0]) * (b[3]-b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0


def draw_detections(frame, detections, scale=1.0):
    """Draw all detections on frame."""
    for cx, cy, bw, bh, conf in detections:
        x1 = int((cx - bw//2) * scale)
        y1 = int((cy - bh//2) * scale)
        x2 = int((cx + bw//2) * scale)
        y2 = int((cy + bh//2) * scale)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"TILING {conf:.2f}", (x1, y1-8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)


def main():
    parser = argparse.ArgumentParser(description="Approach A: TILING detection")
    parser.add_argument("source", help="Image or video file")
    parser.add_argument("--frame", type=int, default=0, help="Start frame (video)")
    parser.add_argument("--model", default="best.tflite", help="Model path")
    parser.add_argument("--tile-size", type=int, default=640, help="Tile size in pixels")
    parser.add_argument("--overlap", type=float, default=0.25, help="Tile overlap (0-0.5)")
    parser.add_argument("--conf", type=float, default=0.3, help="Confidence threshold")
    parser.add_argument("--display-width", type=int, default=960, help="Display width")
    parser.add_argument("--video", action="store_true", help="Play as video (not frame-by-frame)")
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

    is_video = args.source.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
    cap = None

    if is_video:
        cap = cv2.VideoCapture(args.source)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_FRAMES, args.frame)
        ret, frame = cap.read()
        if not ret:
            print("Cannot read frame")
            return
        frame_num = args.frame
    else:
        frame = cv2.imread(args.source)
        if frame is None:
            print(f"Cannot load: {args.source}")
            return
        total_frames = 1
        fps = 1
        frame_num = 0

    img_h, img_w = frame.shape[:2]
    disp_scale = args.display_width / img_w
    disp_w = args.display_width
    disp_h = int(img_h * disp_scale)

    # Calculate tile grid
    stride = int(args.tile_size * (1 - args.overlap))
    n_tiles_x = max(1, (img_w - args.tile_size) // stride + 2)
    n_tiles_y = max(1, (img_h - args.tile_size) // stride + 2)
    total_tiles = n_tiles_x * n_tiles_y

    print(f"Image: {img_w}x{img_h}")
    print(f"Tile size: {args.tile_size}x{args.tile_size}, overlap: {args.overlap}")
    print(f"Grid: {n_tiles_x}x{n_tiles_y} = {total_tiles} tiles per frame")
    print(f"Estimated time per frame: {total_tiles * 50:.0f}ms (laptop) / {total_tiles * 206:.0f}ms (Pi)")
    print()

    win = "TILING Detection (Approach A)"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    if args.video and is_video:
        # Video playback mode
        speed = 1.0
        paused = False
        total_dets = 0

        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_num += 1

                t0 = time.perf_counter()
                dets = tile_detect(vs, frame, args.tile_size, args.overlap, args.conf)
                dt = (time.perf_counter() - t0) * 1000
                total_dets += len(dets)

                disp = cv2.resize(frame, (disp_w, disp_h))
                draw_detections(disp, dets, disp_scale)

                # HUD
                ts = frame_num / fps
                cv2.rectangle(disp, (0, disp_h-35), (disp_w, disp_h), (0,0,0), -1)
                info = f"TILING {args.tile_size}px | {total_tiles} tiles | {dt:.0f}ms | {ts:.1f}s | Dets: {len(dets)} (total: {total_dets})"
                cv2.putText(disp, info, (10, disp_h-12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200,200,200), 1)
                cv2.imshow(win, disp)

            delay = max(1, int((1000/fps)/speed)) if not paused else 50
            key = cv2.waitKey(delay) & 0xFF
            if key == ord('q'): break
            elif key == ord(' '): paused = not paused
            elif key == ord('+'): speed = min(speed+0.5, 8)
            elif key == ord('-'): speed = max(speed-0.5, 0.5)
            elif key == ord('d'):
                frame_num = min(frame_num + int(fps*5), total_frames-1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            elif key == ord('a'):
                frame_num = max(frame_num - int(fps*5), 0)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    else:
        # Frame-by-frame mode (image or video)
        while True:
            print(f"Running tiling on frame {frame_num} ({img_w}x{img_h})...")
            t0 = time.perf_counter()
            dets = tile_detect(vs, frame, args.tile_size, args.overlap, args.conf)
            dt = (time.perf_counter() - t0) * 1000

            print(f"  {len(dets)} detections in {dt:.0f}ms ({total_tiles} tiles)")
            for i, (cx, cy, bw, bh, conf) in enumerate(dets):
                print(f"  [{i+1}] conf={conf:.2f} at ({cx},{cy}) size={bw}x{bh}")

            disp = cv2.resize(frame, (disp_w, disp_h))
            draw_detections(disp, dets, disp_scale)

            # HUD
            cv2.rectangle(disp, (0, disp_h-35), (disp_w, disp_h), (0,0,0), -1)
            info = f"TILING {args.tile_size}px | {total_tiles} tiles | {dt:.0f}ms | Frame: {frame_num} | Detections: {len(dets)}"
            cv2.putText(disp, info, (10, disp_h-12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200,200,200), 1)

            cv2.imshow(win, disp)
            key = cv2.waitKey(0) & 0xFF

            if key == ord('q'):
                break
            elif is_video and (key == ord('d') or key == 83):
                frame_num = min(frame_num + 30, total_frames - 1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                if not ret: break
            elif is_video and (key == ord('a') or key == 81):
                frame_num = max(frame_num - 30, 0)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                if not ret: break

    if cap:
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
