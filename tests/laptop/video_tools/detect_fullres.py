"""
APPROACH B: FULL_RES — feed native resolution directly to YOLO without manual squashing.
Ultralytics YOLO handles letterboxing internally (adds black bars to maintain aspect ratio).
Tests whether YOLO's internal preprocessing works better than our manual resize.

Also tests: what if we resize to different sizes before feeding to YOLO?

Usage:
    python tests/laptop/video_tools/detect_fullres.py RealVideo/DJI_20260311172332_0001_V.MP4 --frame 3425
    python tests/laptop/video_tools/detect_fullres.py RealVideo/test_full_3425.jpg

This runs detection at multiple resolutions on the SAME frame and compares results.
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import cv2
import numpy as np
from vision import VisionSystem


def main():
    parser = argparse.ArgumentParser(description="Approach B: FULL_RES multi-scale detection")
    parser.add_argument("source", help="Image or video file")
    parser.add_argument("--frame", type=int, default=0, help="Frame number (video)")
    parser.add_argument("--model", default="best.tflite", help="Model path")
    parser.add_argument("--conf", type=float, default=0.2, help="Confidence threshold (low to catch everything)")
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

    # Load frame
    is_video = args.source.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
    if is_video:
        cap = cv2.VideoCapture(args.source)
        cap.set(cv2.CAP_PROP_POS_FRAMES, args.frame)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            print("Cannot read frame")
            return
    else:
        frame = cv2.imread(args.source)
        if frame is None:
            print(f"Cannot load: {args.source}")
            return

    img_h, img_w = frame.shape[:2]
    print(f"Original: {img_w}x{img_h}")
    print(f"Model: {args.model}")
    print(f"Confidence threshold: {args.conf}")
    print()
    print(f"{'Resolution':<20} {'Pixels fed':<15} {'YOLO sees':<12} {'Detected':<10} {'Conf':<8} {'Time (ms)':<10} {'Person px (est)'}")
    print("=" * 100)

    # Test at multiple resolutions
    test_sizes = [
        ("Full 4K",        img_w,  img_h),
        ("2560x1440",      2560,   1440),
        ("1920x1080",      1920,   1080),
        ("1280x720",       1280,   720),
        ("960x540",        960,    540),
        ("640x360",        640,    360),
        ("640x480 (Pi)",   640,    480),
        ("480x270",        480,    270),
        ("320x180",        320,    180),
    ]

    results = []
    panels = []

    for label, tw, th in test_sizes:
        # Resize frame
        if tw == img_w and th == img_h:
            test_frame = frame.copy()
        else:
            test_frame = cv2.resize(frame, (tw, th))

        t0 = time.perf_counter()
        found, x, y, conf = vs.detect_in_image(test_frame)
        dt = (time.perf_counter() - t0) * 1000

        # Estimate person size in pixels at this resolution
        scale = tw / img_w
        est_person_px = int(40 * scale)  # rough: person ~40px wide at 4K

        status = "YES" if found else "no"
        conf_str = f"{conf:.3f}" if found else "-"
        print(f"{label:<20} {tw}x{th:<10} {'640x640':<12} {status:<10} {conf_str:<8} {dt:<10.0f} ~{est_person_px}px")

        results.append((label, tw, th, found, conf, dt))

        # Create panel for visual comparison
        panel = cv2.resize(test_frame, (320, 180))
        if found:
            cv2.putText(panel, f"DETECTED {conf:.2f}", (5, 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            cv2.putText(panel, "NOT DETECTED", (5, 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(panel, f"{label} ({tw}x{th})", (5, 170),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        panels.append(panel)

    # Create comparison grid (3x3)
    rows = []
    for i in range(0, len(panels), 3):
        row_panels = panels[i:i+3]
        while len(row_panels) < 3:
            row_panels.append(np.zeros((180, 320, 3), dtype=np.uint8))
        rows.append(np.hstack(row_panels))
    grid = np.vstack(rows)

    print()
    print("Summary:")
    detected = [(l, tw, th, c, dt) for l, tw, th, f, c, dt in results if f]
    not_detected = [(l, tw, th, c, dt) for l, tw, th, f, c, dt in results if not f]
    print(f"  Detected at: {', '.join(l for l, *_ in detected) if detected else 'NONE'}")
    print(f"  Not detected at: {', '.join(l for l, *_ in not_detected) if not_detected else 'NONE'}")
    if detected:
        best = max(detected, key=lambda x: x[3])
        print(f"  Best: {best[0]} @ conf={best[3]:.3f} ({best[4]:.0f}ms)")

    # Show grid
    cv2.imshow("FULL_RES Comparison (Approach B)", grid)
    print("\nPress any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save grid
    out_path = "RealVideo/fullres_comparison.jpg"
    cv2.imwrite(out_path, grid)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
