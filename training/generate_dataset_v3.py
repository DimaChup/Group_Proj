"""
Enhanced dataset generator v3 for SAR dummy detection.

Improvements over v2:
  1. Gaussian noise (sensor noise simulation)
  2. Motion blur (drone movement, directional kernel)
  3. Lens barrel distortion (fisheye simulation)
  4. Random shadow polygons
  5. Haze/fog (additive white alpha blend)
  6. Perspective transform (viewing angle variation)
  7. Multiple targets per image (2-3 dummies with separate labels)
  8. Varied target appearance (pants, tshirt, backpack near dummy)
  9. Aggressive color jitter (HSV shifts, gamma correction)
  10. Higher negative ratio (20% default)
  11. DJI video frame backgrounds (in addition to map.jpg crops)
  12. Altitude-based dummy scaling (15-50m physical model)

Output format: YOLO (images/ + labels/ + dataset.yaml), same as v2.

Usage:
    python generate_dataset_v3.py
    python generate_dataset_v3.py --count 500 --negatives 100 --output dataset_v3
    python generate_dataset_v3.py --count 500 --negatives 100 --size 1088
"""
import cv2
import numpy as np
import os
import csv
import random
import argparse
import math


# ---------------------------------------------------------------------------
#  Asset paths (relative to project root v3/)
# ---------------------------------------------------------------------------
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
MAP_PATH = os.path.join(ASSETS_DIR, "map.jpg")
DUMMY_PATH = os.path.join(ASSETS_DIR, "dummy.png")
CONE_PATH = os.path.join(ASSETS_DIR, "cone.png")
PANTS_PATH = os.path.join(ASSETS_DIR, "pants.png")
TSHIRT_PATH = os.path.join(ASSETS_DIR, "tshirt.png")
BACKPACK_PATH = os.path.join(ASSETS_DIR, "backpack.png")

VIDEO_PATH_DEFAULT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "RealVideo", "DJI_0001_1456x1088_cropped_30fps.mp4",
)
CSV_PATH_DEFAULT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "RealVideo", "DJI_0001_1456x1088_cropped_30fps_detections.csv",
)


# ---------------------------------------------------------------------------
#  Physical model: dummy pixel size vs altitude
# ---------------------------------------------------------------------------
# IMX296 sensor: focal_length_mm=5.46, sensor_width_mm=5.02
# At altitude h (m), GSD = (sensor_w * h) / (focal * image_w)
# Dummy height ~1.8m.  Pixel height = 1.8 / GSD
SENSOR_W_MM = 5.02
FOCAL_MM = 5.46
DUMMY_REAL_H_M = 1.8


def dummy_pixel_height(alt_m, img_w):
    """Pixel height of the dummy at a given altitude for a given image width."""
    gsd = (SENSOR_W_MM * alt_m) / (FOCAL_MM * img_w)
    return DUMMY_REAL_H_M / gsd


# ---------------------------------------------------------------------------
#  Augmentation helpers
# ---------------------------------------------------------------------------

def add_gaussian_noise(img, sigma_range=(5, 25)):
    """Add Gaussian noise with random sigma."""
    sigma = random.uniform(*sigma_range)
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    noisy = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return noisy


def add_motion_blur(img, ksize_range=(3, 15)):
    """Directional motion blur with random angle and kernel size."""
    ksize = random.randrange(ksize_range[0], ksize_range[1] + 1, 2)  # odd
    if ksize < 3:
        ksize = 3
    angle = random.uniform(0, 360)
    kernel = np.zeros((ksize, ksize), dtype=np.float32)
    cx, cy = ksize // 2, ksize // 2
    # Draw a line through center at the chosen angle
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
    """Simulate lens barrel distortion (fisheye effect)."""
    h, w = img.shape[:2]
    k1 = random.uniform(*k1_range)
    # Camera matrix centered
    fx = fy = w
    cx_c, cy_c = w / 2, h / 2
    cam = np.array([[fx, 0, cx_c], [0, fy, cy_c], [0, 0, 1]], dtype=np.float64)
    dist = np.array([k1, 0, 0, 0, 0], dtype=np.float64)
    new_cam, _ = cv2.getOptimalNewCameraMatrix(cam, dist, (w, h), 0, (w, h))
    map1, map2 = cv2.initUndistortRectifyMap(cam, dist, None, new_cam, (w, h), cv2.CV_32FC1)
    return cv2.remap(img, map1, map2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def add_random_shadows(img, num_shadows_range=(1, 3)):
    """Overlay dark polygonal shadow regions."""
    out = img.copy().astype(np.float32)
    h, w = img.shape[:2]
    n = random.randint(*num_shadows_range)
    for _ in range(n):
        # Random quadrilateral
        pts = np.array([
            [random.randint(0, w), random.randint(0, h)]
            for _ in range(random.randint(3, 5))
        ], dtype=np.int32)
        hull = cv2.convexHull(pts)
        mask = np.zeros((h, w), dtype=np.float32)
        cv2.fillConvexPoly(mask, hull, 1.0)
        # Darken by 30-60%
        darkness = random.uniform(0.4, 0.7)
        for c in range(3):
            out[:, :, c] = out[:, :, c] * (1 - mask * (1 - darkness))
    return np.clip(out, 0, 255).astype(np.uint8)


def add_haze(img, alpha_range=(0.1, 0.4)):
    """Simulate haze/fog by blending with white."""
    alpha = random.uniform(*alpha_range)
    white = np.full_like(img, 220, dtype=np.uint8)  # slightly off-white
    return cv2.addWeighted(img, 1 - alpha, white, alpha, 0)


def apply_perspective(img, strength=0.05):
    """Apply slight perspective warp (viewing angle variation).

    Returns warped image and the 3x3 perspective matrix (for transforming bbox points).
    """
    h, w = img.shape[:2]
    s = strength
    # Source corners
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    # Perturb each corner randomly
    dst = np.float32([
        [random.uniform(0, w * s), random.uniform(0, h * s)],
        [w - random.uniform(0, w * s), random.uniform(0, h * s)],
        [w - random.uniform(0, w * s), h - random.uniform(0, h * s)],
        [random.uniform(0, w * s), h - random.uniform(0, h * s)],
    ])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    return warped, M


def color_jitter_hsv(img, h_range=(-15, 15), s_range=(0.7, 1.3), v_range=(0.7, 1.3)):
    """HSV-space color jitter: hue shift, saturation scale, value scale."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    # Hue shift (0-180 in OpenCV)
    hsv[:, :, 0] = (hsv[:, :, 0] + random.uniform(*h_range)) % 180
    # Saturation scale
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * random.uniform(*s_range), 0, 255)
    # Value scale
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * random.uniform(*v_range), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def gamma_correction(img, gamma_range=(0.6, 1.6)):
    """Apply random gamma correction."""
    gamma = random.uniform(*gamma_range)
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                       for i in range(256)]).astype(np.uint8)
    return cv2.LUT(img, table)


# ---------------------------------------------------------------------------
#  Background extraction
# ---------------------------------------------------------------------------

def extract_video_backgrounds(video_path, img_size, max_frames=50):
    """Extract random frames from DJI video as background crops."""
    if not os.path.exists(video_path):
        print(f"  Video not found: {video_path}")
        return []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  Cannot open video: {video_path}")
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if vid_w < img_size or vid_h < img_size:
        print(f"  Video {vid_w}x{vid_h} too small for {img_size} crops")
        cap.release()
        return []

    # Sample random frame indices
    indices = sorted(random.sample(range(total_frames), min(max_frames, total_frames)))
    backgrounds = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        # Random crop to img_size
        x = random.randint(0, vid_w - img_size)
        y = random.randint(0, vid_h - img_size)
        crop = frame[y:y + img_size, x:x + img_size].copy()
        backgrounds.append(crop)

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

def load_accessory_assets():
    """Load accessory PNGs (pants, tshirt, backpack) if they exist."""
    accessories = {}
    for name, path in [("pants", PANTS_PATH), ("tshirt", TSHIRT_PATH),
                        ("backpack", BACKPACK_PATH), ("cone", CONE_PATH)]:
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                accessories[name] = img
                print(f"  Loaded accessory: {name} ({img.shape[1]}x{img.shape[0]})")
    return accessories


def resize_foreground(fg, target_h):
    """Resize foreground maintaining aspect ratio to target pixel height."""
    h, w = fg.shape[:2]
    scale = target_h / h
    new_w = max(4, int(w * scale))
    new_h = max(4, int(h * scale))
    return cv2.resize(fg, (new_w, new_h), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)


def rotate_foreground(fg, angle):
    """Rotate foreground with expanded canvas.  Returns (rotated_img, rot_w, rot_h)."""
    h, w = fg.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    cos_a = abs(M[0, 0])
    sin_a = abs(M[0, 1])
    rot_w = int(h * sin_a + w * cos_a)
    rot_h = int(h * cos_a + w * sin_a)
    M[0, 2] += (rot_w - w) / 2
    M[1, 2] += (rot_h - h) / 2
    rotated = cv2.warpAffine(fg, M, (rot_w, rot_h),
                              flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT,
                              borderValue=(0, 0, 0, 0) if fg.shape[2] == 4 else (0, 0, 0))
    return rotated, rot_w, rot_h


def alpha_blend(bg, fg, px, py):
    """Alpha-blend fg onto bg at position (px, py).  Handles 4-channel fg."""
    fh, fw = fg.shape[:2]
    bh, bw = bg.shape[:2]

    # Clip to bounds
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
        # Edge blending: soften alpha mask to remove hard cut-out edges
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


def paste_target(bg, fg_full, img_size, alt_m, angle=None):
    """Paste a single target (dummy) onto the background.

    Returns (bg, bbox_dict) where bbox_dict has keys: x_center, y_center, w, h
    (all normalised 0-1), or None if placement failed.
    """
    # Altitude-based pixel height
    pix_h = dummy_pixel_height(alt_m, img_size)
    fg_resized = resize_foreground(fg_full, pix_h)

    if angle is None:
        angle = random.randint(0, 360)
    fg_rot, rot_w, rot_h = rotate_foreground(fg_resized, angle)

    if rot_w >= img_size or rot_h >= img_size:
        return bg, None

    # Random position with margin
    margin = 2
    max_x = img_size - rot_w - margin
    max_y = img_size - rot_h - margin
    if max_x < margin or max_y < margin:
        return bg, None

    px = random.randint(margin, max_x)
    py = random.randint(margin, max_y)

    # Brightness matching: scale dummy brightness to match local background patch
    patch = bg[py:py + rot_h, px:px + rot_w]
    if patch.size > 0 and fg_rot.shape[2] == 4:
        # Compute mean brightness of background patch and dummy (alpha-weighted)
        bg_mean = np.mean(cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY).astype(np.float32))
        fg_gray = cv2.cvtColor(fg_rot[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.float32)
        fg_alpha = fg_rot[:, :, 3].astype(np.float32) / 255.0
        alpha_sum = fg_alpha.sum()
        if alpha_sum > 0:
            fg_mean = (fg_gray * fg_alpha).sum() / alpha_sum
            if fg_mean > 1.0:
                scale = bg_mean / fg_mean
                # Clamp scale to avoid extreme shifts
                scale = np.clip(scale, 0.5, 2.0)
                fg_rot_f = fg_rot.astype(np.float32)
                fg_rot_f[:, :, :3] *= scale
                fg_rot = np.clip(fg_rot_f, 0, 255).astype(np.uint8)

    bg = alpha_blend(bg, fg_rot, px, py)

    bbox = {
        "x_center": (px + rot_w / 2) / img_size,
        "y_center": (py + rot_h / 2) / img_size,
        "w": rot_w / img_size,
        "h": rot_h / img_size,
    }
    return bg, bbox


def paste_accessory_near(bg, accessory_img, bbox, img_size, alt_m):
    """Paste an accessory image near the dummy (within ~2m real-world radius).

    Does not create a new label -- accessories are clutter, not targets.
    """
    pix_h = dummy_pixel_height(alt_m, img_size)
    # Accessories are roughly 40-60% the dummy height
    acc_h = pix_h * random.uniform(0.3, 0.6)
    acc_resized = resize_foreground(accessory_img, acc_h)

    angle = random.randint(0, 360)
    acc_rot, rw, rh = rotate_foreground(acc_resized, angle)

    # Place within ~1-3 dummy-heights of the dummy center
    cx = int(bbox["x_center"] * img_size)
    cy = int(bbox["y_center"] * img_size)
    offset_range = int(pix_h * random.uniform(1.0, 3.0))
    ox = random.randint(-offset_range, offset_range)
    oy = random.randint(-offset_range, offset_range)
    px = cx + ox - rw // 2
    py = cy + oy - rh // 2

    # Clamp
    px = max(0, min(img_size - rw, px))
    py = max(0, min(img_size - rh, py))

    return alpha_blend(bg, acc_rot, px, py)


# ---------------------------------------------------------------------------
#  Augmentation pipeline
# ---------------------------------------------------------------------------

def apply_augmentation_pipeline(img):
    """Apply a random subset of augmentations to a composited image."""
    # 1. Color jitter (50%)
    if random.random() < 0.5:
        img = color_jitter_hsv(img)

    # 2. Gamma correction (40%)
    if random.random() < 0.4:
        img = gamma_correction(img)

    # 3. Brightness/contrast (40%)
    if random.random() < 0.4:
        alpha = random.uniform(0.6, 1.4)
        beta = random.randint(-40, 40)
        img = np.clip(alpha * img.astype(np.float32) + beta, 0, 255).astype(np.uint8)

    # 4. Gaussian noise (30%)
    if random.random() < 0.3:
        img = add_gaussian_noise(img)

    # 5. Motion blur (20%)
    if random.random() < 0.2:
        img = add_motion_blur(img)

    # 6. Gaussian blur (20%)
    if random.random() < 0.2:
        k = random.choice([3, 5, 7])
        img = cv2.GaussianBlur(img, (k, k), 0)

    # 7. Random shadows (25%)
    if random.random() < 0.25:
        img = add_random_shadows(img)

    # 8. Haze/fog (15%)
    if random.random() < 0.15:
        img = add_haze(img)

    # 9. Barrel distortion (10%)
    if random.random() < 0.10:
        img = add_barrel_distortion(img)

    # 10. Perspective warp (15%) -- applied without updating labels
    #     (small warp, bbox shift is negligible at <5% strength)
    if random.random() < 0.15:
        img, _ = apply_perspective(img, strength=0.03)

    return img


# ---------------------------------------------------------------------------
#  Main generators
# ---------------------------------------------------------------------------

def generate_synthetic(backgrounds, fg_full, accessories, output_dir, img_size,
                       num_images=500, multi_target_ratio=0.15):
    """Generate synthetic composites with augmentation pipeline.

    Args:
        backgrounds: list of background images (map crops + video crops)
        fg_full: dummy foreground image (BGRA)
        accessories: dict of accessory images
        output_dir: output directory path
        img_size: square image dimension
        num_images: how many to generate
        multi_target_ratio: fraction of images with 2-3 targets
    """
    print(f"\n--- Generating {num_images} synthetic images ---")
    count = 0
    acc_list = list(accessories.values()) if accessories else []

    for i in range(num_images):
        # Pick a random background
        bg = backgrounds[random.randint(0, len(backgrounds) - 1)].copy()
        if bg.shape[0] != img_size or bg.shape[1] != img_size:
            bg = cv2.resize(bg, (img_size, img_size))

        # Decide altitude for this image
        # Distribution: 25% low (15-20m), 40% mid (20-35m), 35% high (35-50m)
        r = random.random()
        if r < 0.25:
            alt = random.uniform(15, 20)
            tag = "close"
        elif r < 0.65:
            alt = random.uniform(20, 35)
            tag = "mid"
        else:
            alt = random.uniform(35, 50)
            tag = "far"

        # How many targets?
        if random.random() < multi_target_ratio:
            num_targets = random.choice([2, 3])
        else:
            num_targets = 1

        labels = []
        placed = 0
        for t in range(num_targets):
            # Vary altitude slightly for multi-target (different positions)
            t_alt = alt + random.uniform(-3, 3) if t > 0 else alt
            t_alt = max(10, t_alt)

            bg, bbox = paste_target(bg, fg_full, img_size, t_alt)
            if bbox is None:
                continue

            labels.append(bbox)
            placed += 1

            # Sometimes add accessories near the dummy (40% chance per target)
            if acc_list and random.random() < 0.4:
                acc = random.choice(acc_list)
                bg = paste_accessory_near(bg, acc, bbox, img_size, t_alt)

        if placed == 0:
            continue

        # Apply augmentation pipeline
        bg = apply_augmentation_pipeline(bg)

        # Write
        n_str = "multi" if placed > 1 else tag
        fname = f"syn_{n_str}_{count:05d}"
        cv2.imwrite(f"{output_dir}/images/{fname}.jpg", bg,
                    [cv2.IMWRITE_JPEG_QUALITY, 92])

        with open(f"{output_dir}/labels/{fname}.txt", "w") as f:
            for bbox in labels:
                f.write(f"0 {bbox['x_center']:.6f} {bbox['y_center']:.6f} "
                        f"{bbox['w']:.6f} {bbox['h']:.6f}\n")
        count += 1

        if (count % 100) == 0:
            print(f"  ... {count}/{num_images}")

    print(f"  Generated {count} synthetic images ({sum(1 for _ in os.listdir(f'{output_dir}/labels') if 'multi' in _)} multi-target)")
    return count


def extract_real_frames(video_path, csv_path, output_dir, img_size, max_frames=100):
    """Extract detected frames from DJI video as training tiles (same as v2)."""
    print(f"\n--- Extracting real frames from {os.path.basename(video_path)} ---")
    if not os.path.exists(csv_path):
        print(f"  No CSV found at {csv_path}, skipping real frames")
        return 0

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

    if max_frames <= 0:
        cap.release()
        print("  max_frames=0, skipping")
        return 0
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

        half = img_size // 2
        cx = max(half, min(vid_w - half, det_x))
        cy = max(half, min(vid_h - half, det_y))
        tile = frame[cy - half:cy + half, cx - half:cx + half].copy()

        if tile.shape[0] != img_size or tile.shape[1] != img_size:
            tile = cv2.resize(tile, (img_size, img_size))

        rel_x = max(0.01, min(0.99, (det_x - (cx - half)) / img_size))
        rel_y = max(0.01, min(0.99, (det_y - (cy - half)) / img_size))
        bbox_w = min(det_w / img_size, 0.95)
        bbox_h = min(det_h / img_size, 0.95)

        fname = f"real_{count:04d}_f{frame_num}"
        cv2.imwrite(f"{output_dir}/images/{fname}.jpg", tile,
                    [cv2.IMWRITE_JPEG_QUALITY, 95])
        with open(f"{output_dir}/labels/{fname}.txt", "w") as f:
            f.write(f"0 {rel_x:.6f} {rel_y:.6f} {bbox_w:.6f} {bbox_h:.6f}")
        count += 1

    cap.release()
    print(f"  Extracted {count} real frames")
    return count


def generate_negatives(backgrounds, output_dir, img_size, num_images=100):
    """Generate negative samples (no dummy) with augmentations."""
    print(f"\n--- Generating {num_images} negative images ---")
    count = 0

    for i in range(num_images):
        bg = backgrounds[random.randint(0, len(backgrounds) - 1)].copy()
        if bg.shape[0] != img_size or bg.shape[1] != img_size:
            bg = cv2.resize(bg, (img_size, img_size))

        # Apply augmentation pipeline (same as positives)
        bg = apply_augmentation_pipeline(bg)

        fname = f"neg_{count:04d}"
        cv2.imwrite(f"{output_dir}/images/{fname}.jpg", bg,
                    [cv2.IMWRITE_JPEG_QUALITY, 92])
        with open(f"{output_dir}/labels/{fname}.txt", "w") as f:
            pass  # Empty label = no detections
        count += 1

    print(f"  Generated {count} negative images")
    return count


def create_yaml(output_dir):
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


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate enhanced SAR training dataset v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_dataset_v3.py
  python generate_dataset_v3.py --count 500 --negatives 100 --output dataset_v3
  python generate_dataset_v3.py --count 800 --negatives 200 --size 1088 --video-bgs 80
        """,
    )
    parser.add_argument("--output", default="dataset_v3", help="Output directory (default: dataset_v3)")
    parser.add_argument("--size", type=int, default=640, help="Image size in pixels (default: 640)")
    parser.add_argument("--count", type=int, default=500, help="Number of synthetic images (default: 500)")
    parser.add_argument("--negatives", type=int, default=100, help="Number of negative images (default: 100)")
    parser.add_argument("--real-max", type=int, default=100, help="Max real frames to extract (default: 100)")
    parser.add_argument("--video", default=VIDEO_PATH_DEFAULT,
                        help="DJI video path for real frame extraction")
    parser.add_argument("--csv", default=CSV_PATH_DEFAULT,
                        help="Detection CSV for real frame extraction")
    parser.add_argument("--video-bgs", type=int, default=50,
                        help="Number of background crops from DJI video (default: 50)")
    parser.add_argument("--multi-target", type=float, default=0.15,
                        help="Fraction of images with 2-3 targets (default: 0.15)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    # Output directories
    out = args.output
    os.makedirs(f"{out}/images", exist_ok=True)
    os.makedirs(f"{out}/labels", exist_ok=True)

    # ---------------------------------------------------------------
    #  Load assets
    # ---------------------------------------------------------------
    print("Loading assets...")

    bg_map = cv2.imread(MAP_PATH)
    if bg_map is None:
        print(f"ERROR: map.jpg not found at {MAP_PATH}")
        return

    fg = cv2.imread(DUMMY_PATH, cv2.IMREAD_UNCHANGED)
    if fg is None:
        print(f"ERROR: dummy.png not found at {DUMMY_PATH}")
        return

    print(f"  Map: {bg_map.shape[1]}x{bg_map.shape[0]}")
    print(f"  Dummy: {fg.shape[1]}x{fg.shape[0]} ({'BGRA' if fg.shape[2] == 4 else 'BGR'})")

    accessories = load_accessory_assets()

    # ---------------------------------------------------------------
    #  Build background pool (map crops + video frames)
    # ---------------------------------------------------------------
    print("\nBuilding background pool...")

    # Map crops (always available)
    map_bgs = [get_map_crop(bg_map, args.size) for _ in range(100)]
    print(f"  Map crops: {len(map_bgs)}")

    # Video frame crops (if video exists)
    video_bgs = extract_video_backgrounds(args.video, args.size, args.video_bgs)

    all_backgrounds = map_bgs + video_bgs
    print(f"  Total backgrounds: {len(all_backgrounds)}")

    # ---------------------------------------------------------------
    #  Generate dataset
    # ---------------------------------------------------------------
    total = 0

    # 1. Synthetic composites
    total += generate_synthetic(
        all_backgrounds, fg, accessories, out, args.size,
        num_images=args.count,
        multi_target_ratio=args.multi_target,
    )

    # 2. Real frames from DJI video
    if os.path.exists(args.video):
        total += extract_real_frames(args.video, args.csv, out, args.size, args.real_max)
    else:
        print(f"\nWARNING: Video not found ({args.video}), skipping real frames")

    # 3. Negatives (20% ratio by default)
    total += generate_negatives(all_backgrounds, out, args.size, args.negatives)

    # 4. Dataset YAML
    create_yaml(out)

    # ---------------------------------------------------------------
    #  Summary
    # ---------------------------------------------------------------
    neg_pct = args.negatives / max(1, total) * 100
    print(f"\n{'=' * 60}")
    print(f"Dataset v3 generated!")
    print(f"  Total images:    {total}")
    print(f"  Synthetic:       {args.count}")
    print(f"  Real frames:     (up to {args.real_max})")
    print(f"  Negatives:       {args.negatives} ({neg_pct:.0f}%)")
    print(f"  Image size:      {args.size}x{args.size}")
    print(f"  Output:          {out}/")
    print(f"  Multi-target:    {args.multi_target * 100:.0f}% of synthetic")
    print(f"\n  Assets used:")
    print(f"    Map background:   {MAP_PATH}")
    print(f"    Dummy foreground: {DUMMY_PATH}")
    for name in accessories:
        print(f"    Accessory:        {name}")
    if not accessories:
        print(f"    (no accessories found -- add pants.png, tshirt.png, backpack.png to assets/)")
    print(f"\n  Augmentations applied:")
    print(f"    Color jitter (HSV)     50%")
    print(f"    Gamma correction       40%")
    print(f"    Brightness/contrast    40%")
    print(f"    Gaussian noise         30%")
    print(f"    Random shadows         25%")
    print(f"    Motion blur            20%")
    print(f"    Gaussian blur          20%")
    print(f"    Haze/fog               15%")
    print(f"    Perspective warp       15%")
    print(f"    Barrel distortion      10%")
    print(f"\nTo train on Colab:")
    print(f"  yolo train data={out}/dataset.yaml model=yolov8n.pt imgsz={args.size} epochs=150 batch=8")
    print(f"\nTo export for Pi:")
    print(f"  yolo export model=best.pt format=tflite imgsz={args.size}")


if __name__ == "__main__":
    main()
