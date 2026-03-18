"""
Enhanced dataset generator for SAR dummy detection.
Combines:
  1. Synthetic composites (map.jpg + dummy.png) at ALL scales (close + far)
  2. Real frames extracted from DJI video with known detection locations
  3. Hard negatives (field with no dummy)

Usage:
    python generate_dataset_v2.py
    python generate_dataset_v2.py --output dataset_v2 --size 640
    python generate_dataset_v2.py --output dataset_v2 --size 728   # for 728 model
"""
import cv2
import numpy as np
import os
import csv
import random
import argparse
import math


def generate_synthetic(bg_full, fg_full, output_dir, img_size, num_images=300):
    """Generate synthetic composites with dummy at various scales (altitudes)."""
    print(f"\n--- Generating {num_images} synthetic images ---")
    h_bg, w_bg = bg_full.shape[:2]
    h_fg, w_fg = fg_full.shape[:2]
    count = 0

    for i in range(num_images):
        # Random background crop
        x_rnd = random.randint(0, w_bg - img_size)
        y_rnd = random.randint(0, h_bg - img_size)
        background = bg_full[y_rnd:y_rnd + img_size, x_rnd:x_rnd + img_size].copy()

        # Scale distribution: mix of close, medium, and far
        # 30% close (0.2-0.4), 40% medium (0.08-0.2), 30% far (0.03-0.08)
        r = random.random()
        if r < 0.3:
            scale = random.uniform(0.2, 0.4)    # close (~15-20m)
            tag = "close"
        elif r < 0.7:
            scale = random.uniform(0.08, 0.2)   # medium (~20-35m)
            tag = "mid"
        else:
            scale = random.uniform(0.03, 0.08)   # far (~35-60m)
            tag = "far"

        new_w = max(8, int(w_fg * scale))
        new_h = max(8, int(h_fg * scale))

        # Skip if too small to see
        if new_w < 6 or new_h < 6:
            continue

        # Resize dummy
        fg_resized = cv2.resize(fg_full, (new_w, new_h))

        # Rotate
        angle = random.randint(0, 360)
        M = cv2.getRotationMatrix2D((new_w // 2, new_h // 2), angle, 1.0)
        # Expand canvas for rotation
        cos_a = abs(M[0, 0])
        sin_a = abs(M[0, 1])
        rot_w = int(new_h * sin_a + new_w * cos_a)
        rot_h = int(new_h * cos_a + new_w * sin_a)
        M[0, 2] += (rot_w - new_w) / 2
        M[1, 2] += (rot_h - new_h) / 2
        fg_rotated = cv2.warpAffine(fg_resized, M, (rot_w, rot_h))

        # Ensure it fits
        if rot_w >= img_size or rot_h >= img_size:
            continue

        # Random position
        paste_x = random.randint(0, img_size - rot_w)
        paste_y = random.randint(0, img_size - rot_h)

        # Alpha blend
        if fg_rotated.shape[2] == 4:
            alpha_s = fg_rotated[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s
            for c in range(3):
                background[paste_y:paste_y + rot_h, paste_x:paste_x + rot_w, c] = (
                    alpha_s * fg_rotated[:, :, c] +
                    alpha_l * background[paste_y:paste_y + rot_h, paste_x:paste_x + rot_w, c]
                )
        else:
            background[paste_y:paste_y + rot_h, paste_x:paste_x + rot_w] = fg_rotated[:, :, :3]

        # Augment: random brightness/contrast
        if random.random() < 0.5:
            alpha_aug = random.uniform(0.7, 1.3)  # contrast
            beta_aug = random.randint(-30, 30)     # brightness
            background = np.clip(alpha_aug * background + beta_aug, 0, 255).astype(np.uint8)

        # Augment: random blur (motion blur simulation)
        if random.random() < 0.3:
            k = random.choice([3, 5])
            background = cv2.GaussianBlur(background, (k, k), 0)

        # YOLO label (normalized)
        x_center = (paste_x + rot_w / 2) / img_size
        y_center = (paste_y + rot_h / 2) / img_size
        bbox_w = rot_w / img_size
        bbox_h = rot_h / img_size

        fname = f"syn_{tag}_{count:04d}"
        cv2.imwrite(f"{output_dir}/images/{fname}.jpg", background)
        with open(f"{output_dir}/labels/{fname}.txt", "w") as f:
            f.write(f"0 {x_center:.6f} {y_center:.6f} {bbox_w:.6f} {bbox_h:.6f}")
        count += 1

    print(f"  Generated {count} synthetic images")
    return count


def extract_real_frames(video_path, csv_path, output_dir, img_size, max_frames=100):
    """Extract detected frames from DJI video as training tiles."""
    print(f"\n--- Extracting real frames from {video_path} ---")
    if not os.path.exists(csv_path):
        print(f"  No CSV found at {csv_path}, skipping real frames")
        return 0

    # Read detection CSV
    rows = []
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            rows.append(r)

    if not rows:
        print("  No detections in CSV, skipping")
        return 0

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  Cannot open video")
        return 0

    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Sample evenly from detections
    step = max(1, len(rows) // max_frames)
    selected = rows[::step][:max_frames]
    count = 0

    for r in selected:
        frame_num = int(r['frame'])
        det_x = int(r['det_px_x'])
        det_y = int(r['det_px_y'])
        det_w = int(r['det_w'])
        det_h = int(r['det_h'])

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if not ret:
            continue

        # Extract a tile centered on detection
        half = img_size // 2
        cx = max(half, min(vid_w - half, det_x))
        cy = max(half, min(vid_h - half, det_y))
        tile = frame[cy - half:cy + half, cx - half:cx + half].copy()

        if tile.shape[0] != img_size or tile.shape[1] != img_size:
            tile = cv2.resize(tile, (img_size, img_size))

        # YOLO label — detection center relative to tile
        rel_x = (det_x - (cx - half)) / img_size
        rel_y = (det_y - (cy - half)) / img_size
        bbox_w = det_w / img_size
        bbox_h = det_h / img_size

        # Clamp
        rel_x = max(0.01, min(0.99, rel_x))
        rel_y = max(0.01, min(0.99, rel_y))
        bbox_w = min(bbox_w, 0.95)
        bbox_h = min(bbox_h, 0.95)

        fname = f"real_{count:04d}_f{frame_num}"
        cv2.imwrite(f"{output_dir}/images/{fname}.jpg", tile)
        with open(f"{output_dir}/labels/{fname}.txt", "w") as f:
            f.write(f"0 {rel_x:.6f} {rel_y:.6f} {bbox_w:.6f} {bbox_h:.6f}")
        count += 1

    cap.release()
    print(f"  Extracted {count} real frames")
    return count


def generate_negatives(bg_full, output_dir, img_size, num_images=50):
    """Generate negative samples (no dummy) for reducing false positives."""
    print(f"\n--- Generating {num_images} negative images ---")
    h_bg, w_bg = bg_full.shape[:2]
    count = 0

    for i in range(num_images):
        x_rnd = random.randint(0, w_bg - img_size)
        y_rnd = random.randint(0, h_bg - img_size)
        crop = bg_full[y_rnd:y_rnd + img_size, x_rnd:x_rnd + img_size].copy()

        # Random augmentation
        if random.random() < 0.5:
            alpha = random.uniform(0.7, 1.3)
            beta = random.randint(-30, 30)
            crop = np.clip(alpha * crop + beta, 0, 255).astype(np.uint8)

        fname = f"neg_{count:04d}"
        cv2.imwrite(f"{output_dir}/images/{fname}.jpg", crop)
        # Empty label file = no detections
        with open(f"{output_dir}/labels/{fname}.txt", "w") as f:
            pass
        count += 1

    print(f"  Generated {count} negative images")
    return count


def create_yaml(output_dir, img_size):
    """Create dataset.yaml for YOLO training."""
    abs_path = os.path.abspath(output_dir).replace("\\", "/")
    yaml_content = f"""path: {abs_path}
train: images
val: images

names:
  0: dummy
"""
    yaml_path = f"{output_dir}/dataset.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    print(f"\nDataset YAML: {yaml_path}")
    return yaml_path


def main():
    parser = argparse.ArgumentParser(description="Generate enhanced SAR training dataset")
    parser.add_argument("--output", default="dataset_v2", help="Output directory")
    parser.add_argument("--size", type=int, default=640, help="Image size (640 or 728)")
    parser.add_argument("--synthetic", type=int, default=300, help="Number of synthetic images")
    parser.add_argument("--negatives", type=int, default=50, help="Number of negative images")
    parser.add_argument("--real-max", type=int, default=100, help="Max real frames to extract")
    parser.add_argument("--video", default="RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4")
    parser.add_argument("--csv", default="RealVideo/DJI_0001_1456x1088_cropped_30fps_detections.csv")
    args = parser.parse_args()

    os.makedirs(f"{args.output}/images", exist_ok=True)
    os.makedirs(f"{args.output}/labels", exist_ok=True)

    total = 0

    # 1. Synthetic composites (only far/small — originals already have close/medium)
    bg = cv2.imread("assets/map.jpg")
    fg = cv2.imread("assets/dummy.png", cv2.IMREAD_UNCHANGED)
    if bg is not None and fg is not None:
        total += generate_synthetic(bg, fg, args.output, args.size, args.synthetic)
    else:
        print("WARNING: map.jpg or dummy.png not found, skipping synthetic")

    # 2. Real frames from DJI video
    if os.path.exists(args.video):
        total += extract_real_frames(args.video, args.csv, args.output, args.size, args.real_max)
    else:
        print(f"WARNING: {args.video} not found, skipping real frames")

    # 3. Negatives
    if bg is not None:
        total += generate_negatives(bg, args.output, args.size, args.negatives)

    # 4. Create YAML
    create_yaml(args.output, args.size)

    print(f"\n{'='*50}")
    print(f"Total images: {total}")
    print(f"Output: {args.output}/")
    print(f"Image size: {args.size}x{args.size}")
    print(f"\nTo train on Colab:")
    print(f"  yolo train data={args.output}/dataset.yaml model=yolov8n.pt imgsz={args.size} epochs=100")
    print(f"\nTo export for Pi:")
    print(f"  yolo export model=best.pt format=tflite imgsz={args.size}")


if __name__ == "__main__":
    main()
