"""
Run vision model over a video file and display detections.
Usage:
    python tests/laptop/video_test.py RealVideo/DJI_20260311172721_0002_V.MP4
    python tests/laptop/video_test.py RealVideo/DJI_20260311172721_0002_V.MP4 --model models/human.tflite
    python tests/laptop/video_test.py RealVideo/DJI_20260311172721_0002_V.MP4 --save output.mp4
Controls: SPACE=pause  Q=quit  ←/→=skip 5s  +/-=speed
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import cv2
import numpy as np
from vision import VisionSystem

def main():
    parser = argparse.ArgumentParser(description="Run vision model over video")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--model", default="best.tflite", help="Model path")
    parser.add_argument("--save", default=None, help="Save output video to file")
    parser.add_argument("--conf", type=float, default=None, help="Confidence threshold override")
    parser.add_argument("--every", type=int, default=3, help="Run AI every Nth frame (default 3)")
    parser.add_argument("--infer-size", type=int, default=640, help="Resize to this width for inference (default 640)")
    parser.add_argument("--display-width", type=int, default=960, help="Display window width (default 960)")
    args = parser.parse_args()

    if not os.path.exists(args.video):
        print(f"Video not found: {args.video}")
        return

    # Override confidence if requested
    if args.conf is not None:
        try:
            import config
            config.CONFIDENCE_THRESHOLD = args.conf
            print(f"[CONFIG] Confidence threshold: {args.conf}")
        except ImportError:
            pass

    # Init vision (no camera — we'll feed frames manually)
    vs = VisionSystem(camera_index=None, model_path=args.model)
    if not vs.using_ai:
        print("Failed to load AI model")
        return

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"Cannot open video: {args.video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0

    # Compute display scale
    disp_scale = args.display_width / vid_w
    disp_w = args.display_width
    disp_h = int(vid_h * disp_scale)

    # Compute inference scale
    infer_scale = args.infer_size / vid_w
    infer_w = args.infer_size
    infer_h = int(vid_h * infer_scale)

    print(f"Video: {vid_w}x{vid_h} @ {fps:.1f}fps, {total_frames} frames ({duration:.1f}s)")
    print(f"Model: {args.model}")
    print(f"Inference at: {infer_w}x{infer_h} (every {args.every} frames)")
    print(f"Display at: {disp_w}x{disp_h}")
    print("Controls: SPACE=pause  Q=quit  A/D=skip 5s  +/-=speed")
    print()

    # Output writer
    writer = None
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(args.save, fourcc, fps, (disp_w, disp_h))
        print(f"Saving to: {args.save}")

    paused = False
    speed = 1.0
    detections = 0
    frame_num = 0
    last_result = (False, 0, 0, 0.0)  # persist detection box between AI frames
    last_bbox = None  # (x1, y1, x2, y2) in display coords
    last_dt = 0
    seeking = [False]  # mutable for trackbar callback

    # Create window with trackbar for scrubbing
    win = "Video Detection Test"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    def on_trackbar(pos):
        seeking[0] = True
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
    cv2.createTrackbar("Position", win, 0, total_frames - 1, on_trackbar)

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break
            frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            timestamp = frame_num / fps if fps > 0 else 0
            if not seeking[0]:
                try:
                    cv2.setTrackbarPos("Position", win, frame_num)
                except cv2.error:
                    pass
            seeking[0] = False

            # Run AI on every Nth frame
            if frame_num % args.every == 0:
                # Resize for inference
                infer_frame = cv2.resize(frame, (infer_w, infer_h))

                t0 = time.perf_counter()
                found, x, y, conf = vs.detect_in_image(infer_frame)
                last_dt = (time.perf_counter() - t0) * 1000
                last_result = (found, x, y, conf)

                if found:
                    detections += 1
                    # Scale bbox back to display coords
                    bw = vs.last_bbox_w * disp_scale / infer_scale
                    bh = vs.last_bbox_h * disp_scale / infer_scale
                    dx = x * disp_scale / infer_scale
                    dy = y * disp_scale / infer_scale
                    last_bbox = (int(dx - bw/2), int(dy - bh/2), int(dx + bw/2), int(dy + bh/2))
                else:
                    last_bbox = None

            # Resize for display
            disp = cv2.resize(frame, (disp_w, disp_h))

            # Draw detection box if we have one
            if last_bbox and last_result[0]:
                x1, y1, x2, y2 = last_bbox
                cv2.rectangle(disp, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(disp, f"DETECTED {last_result[3]:.2f}", (x1, y1-8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # HUD
            bar_y = disp_h - 40
            cv2.rectangle(disp, (0, bar_y), (disp_w, disp_h), (0, 0, 0), -1)
            progress = frame_num / total_frames
            cv2.rectangle(disp, (0, bar_y), (int(disp_w * progress), bar_y + 4), (0, 200, 200), -1)

            info = f"{timestamp:.1f}s / {duration:.1f}s | {last_dt:.0f}ms | Det: {detections} | Speed: {speed:.1f}x | {os.path.basename(args.model)}"
            cv2.putText(disp, info, (10, disp_h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

            if writer:
                writer.write(disp)

            cv2.imshow("Video Detection Test", disp)

        # Key handling — fast waitKey when playing
        delay = max(1, int((1000 / fps) / speed)) if not paused else 50
        key = cv2.waitKey(delay) & 0xFF

        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('d') or key == 83:  # D or right arrow
            new_pos = min(frame_num + int(fps * 5), total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
            frame_num = new_pos
        elif key == ord('a') or key == 81:  # A or left arrow
            new_pos = max(frame_num - int(fps * 5), 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
            frame_num = new_pos
        elif key == ord('+') or key == ord('='):
            speed = min(speed + 0.5, 8.0)
        elif key == ord('-'):
            speed = max(speed - 0.5, 0.5)

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()

    print(f"\n{'='*50}")
    processed = frame_num // args.every
    print(f"Frames processed by AI: {processed}")
    print(f"Detections: {detections} ({100*detections/max(1,processed):.1f}% of processed frames)")

if __name__ == "__main__":
    main()
