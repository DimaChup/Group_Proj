"""
gen_detection_montage.py -- Generate a 2x2 detection montage at 4 altitudes

Scans the DJI 30fps flight video, finds frames with positive YOLOv8 detections
at approximately 15m, 25m, 35m, and 50m altitude, draws bounding boxes, and
arranges them in a 2x2 grid saved as PDF and PNG.

Falls back to a placeholder montage if the video or model is unavailable.

Usage (from project root, using test_env which has ultralytics):
    test_env/Scripts/python report/figs/gen_detection_montage.py
"""
import sys, os, re

PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT)

import cv2
import numpy as np

# ── Paths ──
VIDEO   = os.path.join(PROJECT, "RealVideo", "DJI_0001_1456x1088_cropped_30fps.mp4")
SRT     = os.path.join(PROJECT, "RealVideo", "DJI_20260311172332_0001_V.SRT")
PT_MODEL = os.path.join(PROJECT, "cv_models", "sar_v2_1088", "best.pt")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PNG = os.path.join(OUT_DIR, "detection_montage.png")
OUT_PDF = os.path.join(OUT_DIR, "detection_montage.pdf")

TARGET_ALTS = [15, 25, 35, 50]   # metres
ALT_TOL     = 3                   # accept if within +/- this of target
CONF_THRESH = 0.25
MAX_TRIES   = 10                  # max frames to try per altitude band


def parse_srt(srt_path):
    """Parse DJI SRT file -> dict of frame_num -> {rel_alt, ...}"""
    with open(srt_path, "r") as f:
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
            "lat": float(e[1]), "lon": float(e[2]),
            "rel_alt": float(e[3]), "abs_alt": float(e[4]),
            "yaw": float(e[5]), "pitch": float(e[6]),
        }
    return telem


def draw_detection(frame, x1, y1, x2, y2, conf, alt_label):
    """Draw green bbox, confidence, and altitude label on the frame."""
    # Green bounding box
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 220, 0), 3)

    # Confidence badge above box
    label = f"{conf:.0%}"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 8, y1), (0, 220, 0), -1)
    cv2.putText(frame, label, (x1 + 4, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    # Altitude overlay (top-left, with shadow for readability)
    cv2.putText(frame, alt_label, (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(frame, alt_label, (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 220, 0), 2, cv2.LINE_AA)

    return frame


def try_real_montage():
    """Attempt to generate montage from real video + model. Returns True on success."""
    for path, name in [(VIDEO, "Video"), (SRT, "SRT"), (PT_MODEL, "Model")]:
        if not os.path.exists(path):
            print(f"{name} not found: {path}")
            return False

    # Load model (ultralytics is much faster than TFLite on laptop)
    try:
        from ultralytics import YOLO
        model = YOLO(PT_MODEL)
        print(f"Model loaded: {PT_MODEL}")
    except Exception as e:
        print(f"YOLO load error: {e}")
        return False

    # Parse telemetry
    telem = parse_srt(SRT)
    if not telem:
        print("No SRT entries parsed")
        return False

    cap = cv2.VideoCapture(VIDEO)
    if not cap.isOpened():
        print("Cannot open video")
        return False

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video: {total} frames, SRT: {len(telem)} entries")

    # Build candidate lists per altitude, sorted by closeness to target
    candidates = {a: [] for a in TARGET_ALTS}
    for fnum, t in telem.items():
        alt = t["rel_alt"]
        for ta in TARGET_ALTS:
            if abs(alt - ta) <= ALT_TOL:
                candidates[ta].append((fnum, alt))

    for ta in TARGET_ALTS:
        candidates[ta].sort(key=lambda x: abs(x[1] - ta))
        candidates[ta] = candidates[ta][:MAX_TRIES]
        print(f"  {ta}m: {len(candidates[ta])} candidate frames")

    # Collect unique frames needed, sorted for sequential reads
    needed = {}  # fnum -> [(target_alt, actual_alt), ...]
    for ta in TARGET_ALTS:
        for fnum, actual_alt in candidates[ta]:
            if 1 <= fnum <= total:
                needed.setdefault(fnum, []).append((ta, actual_alt))

    sorted_frames = sorted(needed.keys())

    results = {}  # target_alt -> (frame, x1, y1, x2, y2, conf, actual_alt)
    done_alts = set()

    for fnum in sorted_frames:
        if len(done_alts) == len(TARGET_ALTS):
            break

        targets_here = [(ta, aa) for ta, aa in needed[fnum] if ta not in done_alts]
        if not targets_here:
            continue

        cap.set(cv2.CAP_PROP_POS_FRAMES, fnum - 1)
        ret, frame = cap.read()
        if not ret:
            continue

        # Run YOLO inference
        yolo_results = model(frame, conf=CONF_THRESH, verbose=False)
        boxes = yolo_results[0].boxes if yolo_results else None

        if boxes is not None and len(boxes) > 0:
            # Take highest-confidence detection
            best_idx = boxes.conf.argmax()
            conf = boxes.conf[best_idx].item()
            x1, y1, x2, y2 = [int(v) for v in boxes.xyxy[best_idx].tolist()]

            for ta, actual_alt in targets_here:
                if ta not in done_alts:
                    results[ta] = (frame.copy(), x1, y1, x2, y2, conf, actual_alt)
                    done_alts.add(ta)
                    print(f"  {ta}m -> frame {fnum} (alt={actual_alt:.1f}m, "
                          f"conf={conf:.2f}, box={x2-x1}x{y2-y1}px)")

    cap.release()

    for ta in TARGET_ALTS:
        if ta not in results:
            print(f"  {ta}m -> NO detection found")

    if len(results) < 2:
        print("Too few detections, falling back to placeholder")
        return False

    # Build 2x2 montage
    cell_w, cell_h = 728, 544  # half of 1456x1088
    montage = np.zeros((cell_h * 2, cell_w * 2, 3), dtype=np.uint8)
    positions = [(0, 0), (1, 0), (0, 1), (1, 1)]  # (col, row)

    for idx, ta in enumerate(TARGET_ALTS):
        col, row = positions[idx]
        x_off = col * cell_w
        y_off = row * cell_h

        if ta in results:
            frame, bx1, by1, bx2, by2, conf, actual_alt = results[ta]
            alt_label = f"{actual_alt:.0f}m altitude"
            draw_detection(frame, bx1, by1, bx2, by2, conf, alt_label)
            cell = cv2.resize(frame, (cell_w, cell_h), interpolation=cv2.INTER_AREA)
        else:
            cell = np.full((cell_h, cell_w, 3), 40, dtype=np.uint8)
            text = f"No detection at {ta}m"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
            tx = (cell_w - tw) // 2
            ty = (cell_h + th) // 2
            cv2.putText(cell, text, (tx, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (180, 180, 180), 2)

        montage[y_off:y_off + cell_h, x_off:x_off + cell_w] = cell

    # White grid lines
    cv2.line(montage, (cell_w, 0), (cell_w, cell_h * 2), (255, 255, 255), 2)
    cv2.line(montage, (0, cell_h), (cell_w * 2, cell_h), (255, 255, 255), 2)

    # Save PNG
    cv2.imwrite(OUT_PNG, montage)
    print(f"Saved: {OUT_PNG}")

    # Save PDF via matplotlib
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 1, figsize=(12, 9))
        ax.imshow(cv2.cvtColor(montage, cv2.COLOR_BGR2RGB))
        ax.axis("off")
        fig.tight_layout(pad=0.3)
        fig.savefig(OUT_PDF, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {OUT_PDF}")
    except Exception as e:
        print(f"PDF save failed: {e}")

    return True


def generate_placeholder():
    """Generate a placeholder montage with synthetic boxes."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle("Detection Montage (Placeholder)", fontsize=16, fontweight="bold")

    bbox_sizes = {15: (120, 180), 25: (70, 110), 35: (50, 75), 50: (30, 50)}

    for idx, (ax, alt) in enumerate(zip(axes.flat, TARGET_ALTS)):
        ax.set_xlim(0, 1456)
        ax.set_ylim(1088, 0)
        ax.set_facecolor("#2a2a2a")
        ax.set_xticks([])
        ax.set_yticks([])

        bw, bh = bbox_sizes[alt]
        cx, cy = 728, 544
        rect = patches.Rectangle(
            (cx - bw / 2, cy - bh / 2), bw, bh,
            linewidth=2.5, edgecolor="lime", facecolor="none"
        )
        ax.add_patch(rect)

        conf = max(0.35, 0.97 - alt * 0.012)
        ax.text(cx - bw / 2, cy - bh / 2 - 8, f"{conf:.0%}",
                color="black", fontsize=10, fontweight="bold",
                bbox=dict(boxstyle="square,pad=0.2", fc="lime", ec="none"))

        ax.set_title(f"{alt}m altitude", fontsize=13, fontweight="bold", pad=6)
        ax.text(728, 900, f"Detection at {alt}m\n(placeholder)",
                ha="center", va="center", fontsize=11, color="#999999")

    plt.tight_layout()
    fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
    fig.savefig(OUT_PDF, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved placeholder: {OUT_PNG}")
    print(f"Saved placeholder: {OUT_PDF}")


if __name__ == "__main__":
    print("=== Detection Montage Generator ===")
    if not try_real_montage():
        print("\nFalling back to placeholder montage...")
        generate_placeholder()
    print("Done.")
