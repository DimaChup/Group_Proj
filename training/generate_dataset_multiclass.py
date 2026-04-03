"""
Multi-class synthetic dataset generator for YOLOv8 SAR drone detection.

5 classes (matching simulation assets):
  0: dummy     (1.8m rescue mannequin)
  1: cone      (0.5m traffic cone / marker)
  2: pants     (0.9m clothing item on ground)
  3: tshirt    (0.8m clothing item on ground)
  4: backpack  (0.7m equipment on ground)

Features:
  - Train/val split (80/20) in YOLO directory structure
  - Multiple asset types per image (1-3 objects)
  - Altitude-based scaling (15-50m, physical model)
  - 10 augmentations: color jitter, gamma, brightness/contrast, noise,
    motion blur, gaussian blur, shadows, haze, barrel distortion, perspective
  - Brightness matching (foreground matches local background patch)
  - Edge-blended alpha compositing
  - DJI video frame backgrounds (if available)
  - Negative images with empty labels
  - Auto-generates dataset.yaml
  - Auto-zips for Colab upload

Output structure:
  dataset_multiclass/
    dataset.yaml
    images/train/   (80%)
    images/val/     (20%)
    labels/train/
    labels/val/

Usage:
    python training/generate_dataset_multiclass.py
    python training/generate_dataset_multiclass.py --count 500 --negatives 50 --size 1088
    python training/generate_dataset_multiclass.py --count 800 --negatives 100 --seed 42
"""

import cv2
import numpy as np
import os
import random
import argparse
import math
import shutil
import zipfile

# ---------------------------------------------------------------------------
#  Asset paths (relative to project root v3/)
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
MAP_PATH = os.path.join(ASSETS_DIR, "map.jpg")

ASSET_DEFS = {
    "dummy":    {"path": os.path.join(ASSETS_DIR, "dummy.png"),    "class_id": 0, "height_m": 1.8,
                 "placeholder_color": (0, 0, 200)},    # red
    "cone":     {"path": os.path.join(ASSETS_DIR, "cone.png"),     "class_id": 1, "height_m": 0.5,
                 "placeholder_color": (0, 140, 255)},   # orange
    "pants":    {"path": os.path.join(ASSETS_DIR, "pants.png"),    "class_id": 2, "height_m": 0.9,
                 "placeholder_color": (200, 50, 0)},    # blue
    "tshirt":   {"path": os.path.join(ASSETS_DIR, "tshirt.png"),   "class_id": 3, "height_m": 0.8,
                 "placeholder_color": (0, 200, 0)},     # green
    "backpack": {"path": os.path.join(ASSETS_DIR, "backpack.png"), "class_id": 4, "height_m": 0.7,
                 "placeholder_color": (100, 50, 50)},   # dark teal
}

VIDEO_PATH_DEFAULT = os.path.join(
    PROJECT_ROOT, "RealVideo", "DJI_0001_1456x1088_cropped_30fps.mp4"
)

# Camera model (IMX296)
SENSOR_W_MM = 5.02
FOCAL_MM = 5.46


# ---------------------------------------------------------------------------
#  Physical model: object pixel size vs altitude
# ---------------------------------------------------------------------------
def object_pixel_height(alt_m, img_w, real_h_m):
    """Pixel height of an object at a given altitude."""
    gsd = (SENSOR_W_MM * alt_m) / (FOCAL_MM * img_w)
    return real_h_m / gsd


# ---------------------------------------------------------------------------
#  Placeholder generation (if asset PNG missing)
# ---------------------------------------------------------------------------
def create_placeholder(name, color_bgr, width=80, height=120):
    """Create a simple colored rectangle with alpha as placeholder asset."""
    img = np.zeros((height, width, 4), dtype=np.uint8)
    img[:, :, :3] = color_bgr
    img[:, :, 3] = 255  # fully opaque
    # Add a border
    cv2.rectangle(img, (2, 2), (width - 3, height - 3), (255, 255, 255, 255), 1)
    # Add text label
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(name[:4], font, 0.3, 1)[0]
    tx = (width - text_size[0]) // 2
    ty = height // 2 + text_size[1] // 2
    cv2.putText(img, name[:4], (tx, ty), font, 0.3, (255, 255, 255, 255), 1)
    return img


# ---------------------------------------------------------------------------
#  Augmentation helpers
# ---------------------------------------------------------------------------
def add_gaussian_noise(img, sigma_range=(5, 25)):
    sigma = random.uniform(*sigma_range)
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def add_motion_blur(img, ksize_range=(3, 15)):
    ksize = random.randrange(ksize_range[0], ksize_range[1] + 1, 2)
    if ksize < 3:
        ksize = 3
    angle = random.uniform(0, 360)
    kernel = np.zeros((ksize, ksize), dtype=np.float32)
    cx, cy = ksize // 2, ksize // 2
    dx = math.cos(math.radians(angle))
    dy = math.sin(math.radians(angle))
    for i in range(ksize):
        t = i - cx
        x = int(round(cx + t * dx))
        y = int(round(cy + t * dy))
        if 0 <= x < ksize and 0 <= y < ksize:
            kernel[y, x] = 1.0
    kernel /= max(kernel.sum(), 1.0)
    return cv2.filter2D(img, -1, kernel)


def add_barrel_distortion(img, k1_range=(0.1, 0.4)):
    h, w = img.shape[:2]
    k1 = random.uniform(*k1_range)
    fx = fy = w
    cx_c, cy_c = w / 2, h / 2
    cam = np.array([[fx, 0, cx_c], [0, fy, cy_c], [0, 0, 1]], dtype=np.float64)
    dist = np.array([k1, 0, 0, 0, 0], dtype=np.float64)
    new_cam, _ = cv2.getOptimalNewCameraMatrix(cam, dist, (w, h), 0, (w, h))
    map1, map2 = cv2.initUndistortRectifyMap(cam, dist, None, new_cam, (w, h), cv2.CV_32FC1)
    return cv2.remap(img, map1, map2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def add_random_shadows(img, num_shadows_range=(1, 3)):
    out = img.copy().astype(np.float32)
    h, w = img.shape[:2]
    n = random.randint(*num_shadows_range)
    for _ in range(n):
        pts = np.array([
            [random.randint(0, w), random.randint(0, h)]
            for _ in range(random.randint(3, 5))
        ], dtype=np.int32)
        hull = cv2.convexHull(pts)
        mask = np.zeros((h, w), dtype=np.float32)
        cv2.fillConvexPoly(mask, hull, 1.0)
        darkness = random.uniform(0.4, 0.7)
        for c in range(3):
            out[:, :, c] = out[:, :, c] * (1 - mask * (1 - darkness))
    return np.clip(out, 0, 255).astype(np.uint8)


def add_haze(img, alpha_range=(0.1, 0.4)):
    alpha = random.uniform(*alpha_range)
    white = np.full_like(img, 220, dtype=np.uint8)
    return cv2.addWeighted(img, 1 - alpha, white, alpha, 0)


def apply_perspective(img, strength=0.05):
    h, w = img.shape[:2]
    s = strength
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32([
        [random.uniform(0, w * s), random.uniform(0, h * s)],
        [w - random.uniform(0, w * s), random.uniform(0, h * s)],
        [w - random.uniform(0, w * s), h - random.uniform(0, h * s)],
        [random.uniform(0, w * s), h - random.uniform(0, h * s)],
    ])
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def color_jitter_hsv(img, h_range=(-15, 15), s_range=(0.7, 1.3), v_range=(0.7, 1.3)):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 0] = (hsv[:, :, 0] + random.uniform(*h_range)) % 180
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * random.uniform(*s_range), 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * random.uniform(*v_range), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def gamma_correction(img, gamma_range=(0.6, 1.6)):
    gamma = random.uniform(*gamma_range)
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
    return cv2.LUT(img, table)


def apply_augmentation_pipeline(img):
    """Apply random subset of augmentations."""
    if random.random() < 0.5:
        img = color_jitter_hsv(img)
    if random.random() < 0.4:
        img = gamma_correction(img)
    if random.random() < 0.4:
        alpha = random.uniform(0.6, 1.4)
        beta = random.randint(-40, 40)
        img = np.clip(alpha * img.astype(np.float32) + beta, 0, 255).astype(np.uint8)
    if random.random() < 0.3:
        img = add_gaussian_noise(img)
    if random.random() < 0.2:
        img = add_motion_blur(img)
    if random.random() < 0.2:
        k = random.choice([3, 5, 7])
        img = cv2.GaussianBlur(img, (k, k), 0)
    if random.random() < 0.25:
        img = add_random_shadows(img)
    if random.random() < 0.15:
        img = add_haze(img)
    if random.random() < 0.10:
        img = add_barrel_distortion(img)
    if random.random() < 0.15:
        img = apply_perspective(img, strength=0.03)
    return img


# ---------------------------------------------------------------------------
#  Background extraction
# ---------------------------------------------------------------------------
def extract_video_backgrounds(video_path, img_size, max_frames=50):
    """Extract random frame crops from DJI video as backgrounds."""
    if not os.path.exists(video_path):
        print(f"  Video not found: {video_path} (skipping)")
        return []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  Cannot open video: {video_path}")
        return []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if vid_w < img_size or vid_h < img_size:
        print(f"  Video {vid_w}x{vid_h} too small for {img_size} crops")
        cap.release()
        return []
    indices = sorted(random.sample(range(total), min(max_frames, total)))
    backgrounds = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        x = random.randint(0, vid_w - img_size)
        y = random.randint(0, vid_h - img_size)
        backgrounds.append(frame[y:y + img_size, x:x + img_size].copy())
    cap.release()
    print(f"  Extracted {len(backgrounds)} video background crops")
    return backgrounds


def get_map_crop(bg_full, img_size):
    """Random crop from map.jpg."""
    h, w = bg_full.shape[:2]
    if w < img_size or h < img_size:
        return cv2.resize(bg_full, (img_size, img_size))
    x = random.randint(0, w - img_size)
    y = random.randint(0, h - img_size)
    return bg_full[y:y + img_size, x:x + img_size].copy()


# ---------------------------------------------------------------------------
#  Foreground compositing
# ---------------------------------------------------------------------------
def resize_foreground(fg, target_h):
    """Resize foreground maintaining aspect ratio to target pixel height."""
    h, w = fg.shape[:2]
    scale = target_h / h
    new_w = max(4, int(w * scale))
    new_h = max(4, int(h * scale))
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    return cv2.resize(fg, (new_w, new_h), interpolation=interp)


def rotate_foreground(fg, angle):
    """Rotate foreground with expanded canvas."""
    h, w = fg.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    cos_a = abs(M[0, 0])
    sin_a = abs(M[0, 1])
    rot_w = int(h * sin_a + w * cos_a)
    rot_h = int(h * cos_a + w * sin_a)
    M[0, 2] += (rot_w - w) / 2
    M[1, 2] += (rot_h - h) / 2
    border = (0, 0, 0, 0) if fg.shape[2] == 4 else (0, 0, 0)
    rotated = cv2.warpAffine(fg, M, (rot_w, rot_h),
                              flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT,
                              borderValue=border)
    return rotated, rot_w, rot_h


def alpha_blend(bg, fg, px, py):
    """Alpha-blend fg onto bg at position (px, py). Handles 4-channel fg."""
    fh, fw = fg.shape[:2]
    bh, bw = bg.shape[:2]
    x1 = max(0, px)
    y1 = max(0, py)
    x2 = min(bw, px + fw)
    y2 = min(bh, py + fh)
    if x2 <= x1 or y2 <= y1:
        return bg
    fx1 = x1 - px
    fy1 = y1 - py
    fx2 = fx1 + (x2 - x1)
    fy2 = fy1 + (y2 - y1)
    if fg.shape[2] == 4:
        alpha = fg[fy1:fy2, fx1:fx2, 3:4].astype(np.float32) / 255.0
        alpha_2d = alpha[:, :, 0]
        alpha_2d = cv2.GaussianBlur(alpha_2d, (7, 7), 2)
        alpha = alpha_2d[:, :, np.newaxis]
        fg_rgb = fg[fy1:fy2, fx1:fx2, :3].astype(np.float32)
        bg_region = bg[y1:y2, x1:x2].astype(np.float32)
        blended = alpha * fg_rgb + (1 - alpha) * bg_region
        bg[y1:y2, x1:x2] = blended.astype(np.uint8)
    else:
        bg[y1:y2, x1:x2] = fg[fy1:fy2, fx1:fx2, :3]
    return bg


def brightness_match(fg_rot, bg_patch):
    """Scale foreground brightness to match local background patch."""
    if bg_patch.size == 0 or fg_rot.shape[2] != 4:
        return fg_rot
    bg_mean = np.mean(cv2.cvtColor(bg_patch, cv2.COLOR_BGR2GRAY).astype(np.float32))
    fg_gray = cv2.cvtColor(fg_rot[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.float32)
    fg_alpha = fg_rot[:, :, 3].astype(np.float32) / 255.0
    alpha_sum = fg_alpha.sum()
    if alpha_sum > 0:
        fg_mean = (fg_gray * fg_alpha).sum() / alpha_sum
        if fg_mean > 1.0:
            scale = np.clip(bg_mean / fg_mean, 0.5, 2.0)
            fg_rot_f = fg_rot.astype(np.float32)
            fg_rot_f[:, :, :3] *= scale
            fg_rot = np.clip(fg_rot_f, 0, 255).astype(np.uint8)
    return fg_rot


def paste_object(bg, fg_img, class_id, real_h_m, img_size, alt_m,
                 near_pos=None, angle=None):
    """Paste a single object onto background.

    Args:
        bg: background image (modified in place)
        fg_img: foreground BGRA image
        class_id: YOLO class ID
        real_h_m: physical height in metres
        img_size: square image dimension
        alt_m: simulated altitude
        near_pos: (cx, cy) normalized — if provided, 50% chance to place nearby
        angle: rotation angle (random if None)

    Returns:
        (bg, bbox_dict) or (bg, None) if placement failed.
        bbox_dict: {class_id, x_center, y_center, w, h} (normalized 0-1)
    """
    pix_h = object_pixel_height(alt_m, img_size, real_h_m)
    fg_resized = resize_foreground(fg_img, pix_h)

    if angle is None:
        angle = random.randint(0, 360)
    fg_rot, rot_w, rot_h = rotate_foreground(fg_resized, angle)

    if rot_w >= img_size or rot_h >= img_size:
        return bg, None

    margin = 2
    max_x = img_size - rot_w - margin
    max_y = img_size - rot_h - margin
    if max_x < margin or max_y < margin:
        return bg, None

    # Decide position
    place_near = near_pos is not None and random.random() < 0.5
    if place_near:
        # Place within 1-3 object-heights of the reference position
        cx_ref = int(near_pos[0] * img_size)
        cy_ref = int(near_pos[1] * img_size)
        offset_range = max(1, int(pix_h * random.uniform(1.0, 3.0)))
        px = cx_ref + random.randint(-offset_range, offset_range) - rot_w // 2
        py = cy_ref + random.randint(-offset_range, offset_range) - rot_h // 2
        px = max(margin, min(max_x, px))
        py = max(margin, min(max_y, py))
    else:
        px = random.randint(margin, max_x)
        py = random.randint(margin, max_y)

    # Brightness matching
    patch = bg[py:py + rot_h, px:px + rot_w]
    fg_rot = brightness_match(fg_rot, patch)

    bg = alpha_blend(bg, fg_rot, px, py)

    bbox = {
        "class_id": class_id,
        "x_center": (px + rot_w / 2) / img_size,
        "y_center": (py + rot_h / 2) / img_size,
        "w": rot_w / img_size,
        "h": rot_h / img_size,
    }
    return bg, bbox


# ---------------------------------------------------------------------------
#  Dataset generation
# ---------------------------------------------------------------------------
def generate_images(backgrounds, assets, output_dir, img_size,
                    num_images, split, class_stats):
    """Generate composite images for one split (train or val).

    Image composition distribution:
      ~35%: dummy + 1-2 accessories
      ~25%: dummy alone
      ~15%: accessories only (no dummy)
      ~10%: mixed (2+ different non-dummy objects)
      ~15%: negatives (inline, no objects)
    """
    img_dir = os.path.join(output_dir, "images", split)
    lbl_dir = os.path.join(output_dir, "labels", split)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)

    asset_names = list(assets.keys())
    non_dummy_names = [n for n in asset_names if n != "dummy"]

    for i in range(num_images):
        bg = backgrounds[random.randint(0, len(backgrounds) - 1)].copy()
        if bg.shape[0] != img_size or bg.shape[1] != img_size:
            bg = cv2.resize(bg, (img_size, img_size))

        # Altitude distribution: 25% low (15-20m), 40% mid (20-35m), 35% high (35-50m)
        r_alt = random.random()
        if r_alt < 0.25:
            alt = random.uniform(15, 20)
        elif r_alt < 0.65:
            alt = random.uniform(20, 35)
        else:
            alt = random.uniform(35, 50)

        labels = []
        r_type = random.random()

        if r_type < 0.35 and non_dummy_names:
            # --- 35%: dummy + 1-2 accessories ---
            d = assets["dummy"]
            bg, dummy_bbox = paste_object(bg, d["img"], d["class_id"], d["height_m"],
                                          img_size, alt)
            if dummy_bbox:
                labels.append(dummy_bbox)
                class_stats["dummy"] = class_stats.get("dummy", 0) + 1
                near = (dummy_bbox["x_center"], dummy_bbox["y_center"])
                num_acc = random.choice([1, 2])
                for _ in range(num_acc):
                    acc_name = random.choice(non_dummy_names)
                    a = assets[acc_name]
                    a_alt = max(10, alt + random.uniform(-3, 3))
                    bg, acc_bbox = paste_object(bg, a["img"], a["class_id"],
                                                a["height_m"], img_size, a_alt,
                                                near_pos=near)
                    if acc_bbox:
                        labels.append(acc_bbox)
                        class_stats[acc_name] = class_stats.get(acc_name, 0) + 1
            tag = "da"

        elif r_type < 0.60 or not non_dummy_names:
            # --- 25%: dummy alone (15% chance of multi-dummy) ---
            num_targets = 1
            if random.random() < 0.15:
                num_targets = random.choice([2, 3])
            d = assets["dummy"]
            for t in range(num_targets):
                t_alt = max(10, alt + random.uniform(-3, 3)) if t > 0 else alt
                bg, bbox = paste_object(bg, d["img"], d["class_id"], d["height_m"],
                                        img_size, t_alt)
                if bbox:
                    labels.append(bbox)
                    class_stats["dummy"] = class_stats.get("dummy", 0) + 1
            tag = "d"

        elif r_type < 0.75:
            # --- 15%: accessories only (no dummy) ---
            num_acc = random.randint(1, 3)
            for _ in range(num_acc):
                acc_name = random.choice(non_dummy_names)
                a = assets[acc_name]
                a_alt = max(10, alt + random.uniform(-3, 3))
                bg, acc_bbox = paste_object(bg, a["img"], a["class_id"],
                                            a["height_m"], img_size, a_alt)
                if acc_bbox:
                    labels.append(acc_bbox)
                    class_stats[acc_name] = class_stats.get(acc_name, 0) + 1
            tag = "a"

        elif r_type < 0.85:
            # --- 10%: mixed (2-3 different objects from all classes) ---
            num_obj = random.randint(2, 3)
            chosen = random.sample(asset_names, min(num_obj, len(asset_names)))
            ref_pos = None
            for obj_name in chosen:
                a = assets[obj_name]
                a_alt = max(10, alt + random.uniform(-3, 3))
                bg, bbox = paste_object(bg, a["img"], a["class_id"],
                                        a["height_m"], img_size, a_alt,
                                        near_pos=ref_pos)
                if bbox:
                    labels.append(bbox)
                    class_stats[obj_name] = class_stats.get(obj_name, 0) + 1
                    if ref_pos is None:
                        ref_pos = (bbox["x_center"], bbox["y_center"])
            tag = "mx"

        else:
            # --- 15%: inline negatives ---
            tag = "neg"

        # Apply augmentation pipeline
        bg = apply_augmentation_pipeline(bg)

        # Write image and label
        fname = f"syn_{tag}_{i:05d}"
        cv2.imwrite(os.path.join(img_dir, f"{fname}.jpg"), bg,
                    [cv2.IMWRITE_JPEG_QUALITY, 92])

        with open(os.path.join(lbl_dir, f"{fname}.txt"), "w") as f:
            for bbox in labels:
                f.write(f"{bbox['class_id']} {bbox['x_center']:.6f} "
                        f"{bbox['y_center']:.6f} {bbox['w']:.6f} {bbox['h']:.6f}\n")

        if (i + 1) % 100 == 0:
            print(f"  [{split}] {i + 1}/{num_images}")

    print(f"  [{split}] Generated {num_images} images")


def generate_negatives(backgrounds, output_dir, img_size, num_images, split):
    """Generate negative images (no objects, empty labels)."""
    img_dir = os.path.join(output_dir, "images", split)
    lbl_dir = os.path.join(output_dir, "labels", split)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)

    for i in range(num_images):
        bg = backgrounds[random.randint(0, len(backgrounds) - 1)].copy()
        if bg.shape[0] != img_size or bg.shape[1] != img_size:
            bg = cv2.resize(bg, (img_size, img_size))
        bg = apply_augmentation_pipeline(bg)

        fname = f"neg_{i:04d}"
        cv2.imwrite(os.path.join(img_dir, f"{fname}.jpg"), bg,
                    [cv2.IMWRITE_JPEG_QUALITY, 92])
        with open(os.path.join(lbl_dir, f"{fname}.txt"), "w") as f:
            pass  # empty label
    print(f"  [{split}] Generated {num_images} negative images")


def create_yaml(output_dir):
    """Create dataset.yaml for YOLO training."""
    abs_path = os.path.abspath(output_dir).replace("\\", "/")
    yaml_content = f"""path: {abs_path}
train: images/train
val: images/val

names:
  0: dummy
  1: cone
  2: pants
  3: tshirt
  4: backpack
"""
    yaml_path = os.path.join(output_dir, "dataset.yaml")
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    print(f"\nDataset YAML: {yaml_path}")
    return yaml_path


def zip_dataset(output_dir, zip_path):
    """Zip the dataset directory for Colab upload."""
    print(f"\nZipping dataset to {zip_path}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                filepath = os.path.join(root, f)
                arcname = os.path.relpath(filepath, os.path.dirname(output_dir))
                zf.write(filepath, arcname)
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"  Zip created: {zip_path} ({size_mb:.1f} MB)")


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Generate multi-class SAR training dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python training/generate_dataset_multiclass.py
  python training/generate_dataset_multiclass.py --count 500 --negatives 50 --size 1088
  python training/generate_dataset_multiclass.py --count 800 --negatives 100 --seed 42 --no-zip
        """,
    )
    parser.add_argument("--output", default="training/dataset_multiclass",
                        help="Output directory (default: training/dataset_multiclass)")
    parser.add_argument("--size", type=int, default=640,
                        help="Image size in pixels (default: 640)")
    parser.add_argument("--count", type=int, default=600,
                        help="Total synthetic images (split 80/20 train/val, default: 600)")
    parser.add_argument("--negatives", type=int, default=50,
                        help="Negative images (split 80/20 train/val, default: 50)")
    parser.add_argument("--video-bgs", type=int, default=50,
                        help="Number of background crops from DJI video (default: 50)")
    parser.add_argument("--video", default=VIDEO_PATH_DEFAULT,
                        help="DJI video path for background extraction")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--no-zip", action="store_true",
                        help="Skip zip creation")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    out = args.output

    # Clean output if exists
    if os.path.exists(out):
        print(f"Removing existing {out}/...")
        shutil.rmtree(out)

    os.makedirs(os.path.join(out, "images", "train"), exist_ok=True)
    os.makedirs(os.path.join(out, "images", "val"), exist_ok=True)
    os.makedirs(os.path.join(out, "labels", "train"), exist_ok=True)
    os.makedirs(os.path.join(out, "labels", "val"), exist_ok=True)

    # -------------------------------------------------------------------
    #  Load assets
    # -------------------------------------------------------------------
    print("Loading assets...")

    bg_map = cv2.imread(MAP_PATH)
    if bg_map is None:
        print(f"ERROR: map.jpg not found at {MAP_PATH}")
        return

    print(f"  Map: {bg_map.shape[1]}x{bg_map.shape[0]}")

    assets = {}
    for name, defn in ASSET_DEFS.items():
        path = defn["path"]
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                assets[name] = {
                    "img": img,
                    "class_id": defn["class_id"],
                    "height_m": defn["height_m"],
                }
                ch = "BGRA" if img.shape[2] == 4 else "BGR"
                print(f"  {name}: {img.shape[1]}x{img.shape[0]} ({ch})")
                continue
        # Create placeholder
        print(f"  {name}: NOT FOUND at {path} -- creating placeholder")
        placeholder = create_placeholder(name, defn["placeholder_color"])
        assets[name] = {
            "img": placeholder,
            "class_id": defn["class_id"],
            "height_m": defn["height_m"],
        }

    # -------------------------------------------------------------------
    #  Build background pool
    # -------------------------------------------------------------------
    print("\nBuilding background pool...")
    map_bgs = [get_map_crop(bg_map, args.size) for _ in range(100)]
    print(f"  Map crops: {len(map_bgs)}")

    video_bgs = extract_video_backgrounds(args.video, args.size, args.video_bgs)
    all_backgrounds = map_bgs + video_bgs
    print(f"  Total backgrounds: {len(all_backgrounds)}")

    # -------------------------------------------------------------------
    #  Generate train/val split
    # -------------------------------------------------------------------
    num_train = int(args.count * 0.8)
    num_val = args.count - num_train
    neg_train = int(args.negatives * 0.8)
    neg_val = args.negatives - neg_train

    print(f"\n--- Generating dataset ({args.count} synthetic + {args.negatives} negatives) ---")
    print(f"  Train: {num_train} synthetic + {neg_train} negatives = {num_train + neg_train}")
    print(f"  Val:   {num_val} synthetic + {neg_val} negatives = {num_val + neg_val}")

    class_stats = {}

    print(f"\n--- Training split ---")
    generate_images(all_backgrounds, assets, out, args.size, num_train, "train", class_stats)
    generate_negatives(all_backgrounds, out, args.size, neg_train, "train")

    print(f"\n--- Validation split ---")
    generate_images(all_backgrounds, assets, out, args.size, num_val, "val", class_stats)
    generate_negatives(all_backgrounds, out, args.size, neg_val, "val")

    # Dataset YAML
    create_yaml(out)

    # Zip
    if not args.no_zip:
        zip_path = out.rstrip("/\\") + ".zip"
        zip_dataset(out, zip_path)

    # -------------------------------------------------------------------
    #  Summary
    # -------------------------------------------------------------------
    total = args.count + args.negatives
    print(f"\n{'=' * 60}")
    print(f"Multi-class dataset generated!")
    print(f"  Total images:    {total}")
    print(f"  Train:           {num_train + neg_train}")
    print(f"  Val:             {num_val + neg_val}")
    print(f"  Image size:      {args.size}x{args.size}")
    print(f"  Output:          {out}/")
    print(f"  Classes:         5")
    print(f"\n  Class instance counts (across train+val):")
    for name in ASSET_DEFS:
        count = class_stats.get(name, 0)
        print(f"    {ASSET_DEFS[name]['class_id']}: {name:10s}  {count} instances")
    print(f"\n  Assets used:")
    for name in assets:
        print(f"    {name}: class {assets[name]['class_id']}, "
              f"height {assets[name]['height_m']}m")
    print(f"\n  Augmentations: color jitter, gamma, brightness/contrast,")
    print(f"    noise, motion blur, gaussian blur, shadows, haze,")
    print(f"    barrel distortion, perspective warp")
    print(f"\nTo train on Colab:")
    print(f"  yolo train data={out}/dataset.yaml model=yolov8n.pt "
          f"imgsz={args.size} epochs=150 batch=8")
    print(f"\nTo export for Pi:")
    print(f"  yolo export model=best.pt format=tflite imgsz={args.size}")


if __name__ == "__main__":
    main()
