"""
Simple click-to-label tool for training images.
Click on the dummy center, then drag to set box size. Press S to save, N to skip, Q to quit.

Usage:
    python tools/label_tool.py dataset_v2/preview_50m/
    python tools/label_tool.py dataset_v2/preview_50m/ --tile-size 640 --output dataset_v2
"""
import cv2
import os
import sys
import argparse
import glob
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="Click-to-label tool")
    parser.add_argument("input_dir", help="Directory with images to label")
    parser.add_argument("--tile-size", type=int, default=640, help="Output tile size (default 640)")
    parser.add_argument("--output", default=None, help="Output dataset dir (default: save labels next to images)")
    parser.add_argument("--bbox-size", type=int, default=40, help="Default bbox size in pixels at full res (default 40)")
    parser.add_argument("--full", action="store_true", help="Save full image (no tiling/cropping). Labels relative to full frame.")
    args = parser.parse_args()

    images = sorted(glob.glob(os.path.join(args.input_dir, "*.jpg")) +
                   glob.glob(os.path.join(args.input_dir, "*.png")))
    if not images:
        print(f"No images found in {args.input_dir}")
        return

    print(f"Found {len(images)} images")
    print("Controls:")
    print("  LEFT CLICK  = set dummy center")
    print("  SCROLL      = adjust box size")
    print("  S           = save and next")
    print("  N           = skip (no dummy)")
    print("  Q           = quit")
    print()

    if args.output:
        os.makedirs(f"{args.output}/images", exist_ok=True)
        os.makedirs(f"{args.output}/labels", exist_ok=True)

    state = {
        "cx": -1, "cy": -1,
        "bbox_w": args.bbox_size, "bbox_h": args.bbox_size,
        "clicked": False
    }

    def on_mouse(event, mx, my, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            state["cx"] = mx
            state["cy"] = my
            state["clicked"] = True
        elif event == cv2.EVENT_MOUSEWHEEL:
            delta = 5 if flags > 0 else -5
            state["bbox_w"] = max(10, state["bbox_w"] + delta)
            state["bbox_h"] = max(10, state["bbox_h"] + delta)

    win = "Label Tool — click dummy, S=save, N=skip, Q=quit"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(win, on_mouse)

    saved = 0
    for idx, img_path in enumerate(images):
        img = cv2.imread(img_path)
        if img is None:
            continue
        img_h, img_w = img.shape[:2]
        fname = os.path.splitext(os.path.basename(img_path))[0]

        # Scale for display
        max_disp = 900
        scale = min(max_disp / img_w, max_disp / img_h, 1.0)
        disp_w = int(img_w * scale)
        disp_h = int(img_h * scale)

        state["clicked"] = False
        state["cx"] = -1
        state["cy"] = -1

        while True:
            disp = cv2.resize(img, (disp_w, disp_h))

            # Draw bbox if clicked
            if state["clicked"]:
                cx, cy = state["cx"], state["cy"]
                bw = int(state["bbox_w"] * scale)
                bh = int(state["bbox_h"] * scale)
                x1 = cx - bw // 2
                y1 = cy - bh // 2
                x2 = cx + bw // 2
                y2 = cy + bh // 2
                cv2.rectangle(disp, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(disp, (cx, cy), 4, (255, 0, 255), -1)
                cv2.putText(disp, f"Box: {state['bbox_w']}x{state['bbox_h']}px",
                           (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # HUD
            cv2.putText(disp, f"[{idx+1}/{len(images)}] {fname}", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            cv2.putText(disp, f"{img_w}x{img_h} | Saved: {saved} | S=save N=skip Q=quit | Scroll=resize box",
                       (10, disp_h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

            cv2.imshow(win, disp)
            key = cv2.waitKey(30) & 0xFF

            if key == ord('q'):
                cv2.destroyAllWindows()
                print(f"\nDone. Saved {saved} labelled images.")
                return

            elif key == ord('n'):
                break  # skip

            elif key == ord('s') and state["clicked"]:
                # Convert display coords back to full image coords
                real_cx = int(state["cx"] / scale)
                real_cy = int(state["cy"] / scale)
                real_bw = state["bbox_w"]
                real_bh = state["bbox_h"]

                if args.output and args.full:
                    # Save full frame — no cropping, no resizing
                    rel_x = real_cx / img_w
                    rel_y = real_cy / img_h
                    rel_w = real_bw / img_w
                    rel_h = real_bh / img_h

                    out_name = f"real_{fname}_{saved:03d}"
                    cv2.imwrite(f"{args.output}/images/{out_name}.jpg", img)
                    with open(f"{args.output}/labels/{out_name}.txt", "w") as f:
                        f.write(f"0 {rel_x:.6f} {rel_y:.6f} {rel_w:.6f} {rel_h:.6f}")
                    print(f"  Saved {out_name} ({img_w}x{img_h}, dummy at {rel_x:.2f},{rel_y:.2f})")

                elif args.output:
                    # Cut a tile around the dummy at random position
                    tile_size = args.tile_size
                    # Random offset so dummy isn't centered
                    offset_x = np.random.randint(
                        max(0, real_cx - tile_size + real_bw),
                        min(img_w - tile_size, real_cx - real_bw) + 1
                    ) if img_w > tile_size else 0
                    offset_y = np.random.randint(
                        max(0, real_cy - tile_size + real_bh),
                        min(img_h - tile_size, real_cy - real_bh) + 1
                    ) if img_h > tile_size else 0
                    offset_x = max(0, min(img_w - tile_size, offset_x))
                    offset_y = max(0, min(img_h - tile_size, offset_y))

                    tile = img[offset_y:offset_y + tile_size, offset_x:offset_x + tile_size]
                    if tile.shape[0] != tile_size or tile.shape[1] != tile_size:
                        tile = cv2.resize(tile, (tile_size, tile_size))
                        # Adjust coords for resize
                        sx = tile_size / tile.shape[1] if tile.shape[1] > 0 else 1
                        sy = tile_size / tile.shape[0] if tile.shape[0] > 0 else 1

                    # YOLO label relative to tile
                    rel_x = (real_cx - offset_x) / tile_size
                    rel_y = (real_cy - offset_y) / tile_size
                    rel_w = real_bw / tile_size
                    rel_h = real_bh / tile_size

                    out_name = f"real_{fname}_{saved:03d}"
                    cv2.imwrite(f"{args.output}/images/{out_name}.jpg", tile)
                    with open(f"{args.output}/labels/{out_name}.txt", "w") as f:
                        f.write(f"0 {rel_x:.6f} {rel_y:.6f} {rel_w:.6f} {rel_h:.6f}")
                    print(f"  Saved {out_name} (tile at {offset_x},{offset_y}, dummy at {rel_x:.2f},{rel_y:.2f})")
                else:
                    # Save label next to image
                    rel_x = real_cx / img_w
                    rel_y = real_cy / img_h
                    rel_w = real_bw / img_w
                    rel_h = real_bh / img_h
                    label_path = os.path.splitext(img_path)[0] + ".txt"
                    with open(label_path, "w") as f:
                        f.write(f"0 {rel_x:.6f} {rel_y:.6f} {rel_w:.6f} {rel_h:.6f}")
                    print(f"  Saved label: {label_path}")

                saved += 1
                break  # next image

    cv2.destroyAllWindows()
    print(f"\nDone. Saved {saved} labelled images.")


if __name__ == "__main__":
    main()
