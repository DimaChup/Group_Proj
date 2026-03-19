# planning.py
import math
import cv2
import numpy as np
import config

class PathPlanner:
    def __init__(self, geo_transformer, search_poly):
        self.geo = geo_transformer
        self.search_polygon = search_poly
        self.pix_per_m = self.geo.pix_per_m
        self.virtual_polygon = [] 

    # --- MAIN GENERATOR (OPTIMIZED) ---
    def generate_search_pattern(self, map_w, map_h, drone_gps=None, alt_override=None):
        if len(self.search_polygon) < 3: return []
        search_alt = alt_override or config.TARGET_ALT
        print(f"[PLANNER] Calculating Optimum Path (alt={search_alt:.0f}m)")

        # 1. GENERATE SEARCH MASK
        mask = np.zeros((map_h, map_w), dtype=np.uint8)
        poly_pts = np.array([self.search_polygon], dtype=np.int32)
        cv2.fillPoly(mask, poly_pts, 255)
        
        # Update Virtual Polygon for Visualization (It is now exactly the Search Poly)
        self.virtual_polygon = poly_pts.reshape(-1, 1, 2)

        # 2. ROTATED SWEEP LOGIC
        
        # Determine Angle (Principal Component Analysis or MinAreaRect)
        rect = cv2.minAreaRect(poly_pts[0])
        (center, size, angle) = rect
        scan_angle = angle + 90 if size[0] < size[1] else angle
        
        # Rotate Mask to align with longest edge
        M = cv2.getRotationMatrix2D(center, scan_angle, 1.0)
        M_inv = cv2.invertAffineTransform(M)
        rotated_mask = cv2.warpAffine(mask, M, (map_w, map_h))

        # Scan Lines
        ground_width_m = (config.SENSOR_WIDTH_MM * search_alt) / config.FOCAL_LENGTH_MM
        overlap = 0.2
        SWATH_M = ground_width_m * (1.0 - overlap)
        step_px = int(SWATH_M * self.pix_per_m)
        if step_px < 1: step_px = 1
        
        points = cv2.findNonZero(rotated_mask)
        if points is None: return []
        x, y, w, h = cv2.boundingRect(points)
        
        # Generate ALL possible lines (Strips)
        all_strips = []
        
        margin = step_px // 2
        bottom_limit = y + h - margin
        last_scan_y = -999

        scan_lines = list(range(y + margin, y + h, step_px))
        # Ensure the last edge line is included (clamped to margin from border)
        if not scan_lines or scan_lines[-1] < bottom_limit:
            scan_lines.append(bottom_limit)

        for scan_y in scan_lines:
            scan_y = min(scan_y, bottom_limit)
            if scan_y == last_scan_y:
                continue  # skip duplicate
            last_scan_y = scan_y
            row = rotated_mask[scan_y, :]
            pixels = np.where(row == 255)[0]
            if len(pixels) > 0:
                # Inset by margin to keep buffer from polygon edge on turns
                x_start = pixels[0] + margin
                x_end = pixels[-1] - margin
                if x_end > x_start:
                    # Store as rotated points (x, y)
                    all_strips.append( [ (x_start, scan_y), (x_end, scan_y) ] )

        # 3. GLOBAL OPTIMIZATION: CLOSEST START CORNER
        direction = 1 # Default (Left to Right)
        
        if drone_gps and all_strips:
            drone_px = self.geo.gps_to_pixels(drone_gps[0], drone_gps[1])
            
            def get_dist_to_rotated_point(p_rot):
                p_arr = np.array([[p_rot]], dtype=np.float32)
                p_orig = cv2.transform(p_arr, M_inv)[0][0]
                return (p_orig[0]-drone_px[0])**2 + (p_orig[1]-drone_px[1])**2

            first_strip = all_strips[0]
            last_strip = all_strips[-1]
            
            # Check 4 Corners
            d_top_left = get_dist_to_rotated_point(first_strip[0])
            d_top_right = get_dist_to_rotated_point(first_strip[1])
            d_bot_left = get_dist_to_rotated_point(last_strip[0])
            d_bot_right = get_dist_to_rotated_point(last_strip[1])
            
            min_dist = min(d_top_left, d_top_right, d_bot_left, d_bot_right)
            
            # Decide Top vs Bottom
            if min_dist == d_bot_left or min_dist == d_bot_right:
                all_strips.reverse()
                # If we swapped, the "first strip" is now the bottom one
                # Re-eval left/right for the NEW first strip
                d_left = get_dist_to_rotated_point(all_strips[0][0])
                d_right = get_dist_to_rotated_point(all_strips[0][1])
            else:
                d_left = d_top_left
                d_right = d_top_right
                
            # Decide Left vs Right
            if d_right < d_left:
                direction = -1

        # 4. CONVERT TO GPS WAYPOINTS
        wps = []
        for strip in all_strips:
            # strip is [(x1, y), (x2, y)]
            if direction == -1:
                pt_start, pt_end = strip[1], strip[0]
            else:
                pt_start, pt_end = strip[0], strip[1]
            
            pts_rot = np.array([[pt_start, pt_end]], dtype=np.float32)
            pts_orig = cv2.transform(pts_rot, M_inv)[0]
            
            p1_gps = self.geo.pixels_to_gps(pts_orig[0][0], pts_orig[0][1])
            p2_gps = self.geo.pixels_to_gps(pts_orig[1][0], pts_orig[1][1])
            
            wps.append(p1_gps)
            wps.append(p2_gps)
            
            # ZigZag
            direction *= -1

        return wps

    @staticmethod
    def smooth_waypoints(wps, num_arc_points=3):
        """Add Bezier curve points at sharp turns to smooth the path.

        Takes a lawnmower pattern (alternating strip endpoints) and inserts
        arc waypoints at each U-turn so the drone follows a smooth curve
        instead of stopping at each corner.

        Args:
            wps: list of (lat, lon) waypoints from generate_search_pattern
            num_arc_points: number of interpolation points per turn (3-5)

        Returns:
            smoothed list of (lat, lon) waypoints
        """
        if len(wps) < 4:
            return wps

        smoothed = [wps[0]]  # keep first point

        for i in range(1, len(wps) - 1):
            prev = wps[i - 1]
            curr = wps[i]
            nxt = wps[i + 1]

            # Check if this is a turn point (end of strip → start of next strip)
            # In lawnmower: even indices are strip starts, odd are strip ends
            # Turn happens at odd→even transitions (end of strip → start of next)
            if i % 2 == 1:  # end of a strip — this is a turn
                # Quadratic Bezier: P0=curr, P1=control point, P2=next
                # Control point is at the corner (curr) pushed outward
                # For smooth turn, use curr as control point between prev-end and next-start
                for t_val in range(1, num_arc_points + 1):
                    t = t_val / (num_arc_points + 1)
                    # Quadratic Bezier: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
                    lat = (1 - t) ** 2 * prev[0] + 2 * (1 - t) * t * curr[0] + t ** 2 * nxt[0]
                    lon = (1 - t) ** 2 * prev[1] + 2 * (1 - t) * t * curr[1] + t ** 2 * nxt[1]
                    smoothed.append((float(lat), float(lon)))
            else:
                smoothed.append(curr)

        smoothed.append(wps[-1])  # keep last point
        return smoothed

    # --- SPIRAL PATTERN ---
    def generate_spiral_pattern(self, map_w, map_h, drone_gps=None, alt_override=None):
        """Simple rectangular inward spiral using same rotated-mask approach as lawnmower."""
        if len(self.search_polygon) < 3:
            return []

        print("[PLANNER] Calculating Spiral Path")

        # 1. MASK + ROTATION (same as lawnmower)
        mask = np.zeros((map_h, map_w), dtype=np.uint8)
        poly_pts = np.array([self.search_polygon], dtype=np.int32)
        cv2.fillPoly(mask, poly_pts, 255)
        self.virtual_polygon = poly_pts.reshape(-1, 1, 2)

        rect = cv2.minAreaRect(poly_pts[0])
        (center, size, angle) = rect
        scan_angle = angle + 90 if size[0] < size[1] else angle

        M = cv2.getRotationMatrix2D(center, scan_angle, 1.0)
        M_inv = cv2.invertAffineTransform(M)
        rotated_mask = cv2.warpAffine(mask, M, (map_w, map_h))

        # 2. SWATH
        search_alt = alt_override or config.TARGET_ALT
        ground_width_m = (config.SENSOR_WIDTH_MM * search_alt) / config.FOCAL_LENGTH_MM
        overlap = 0.2
        SWATH_M = ground_width_m * (1.0 - overlap)
        step_px = max(1, int(SWATH_M * self.pix_per_m))

        points = cv2.findNonZero(rotated_mask)
        if points is None:
            return []
        x, y, w, h = cv2.boundingRect(points)

        # 3. RECTANGULAR SPIRAL (inward)
        # Walk the edges of the bounding rect, shrinking inward each ring
        spiral_pts = []
        top, bottom, left, right = y, y + h, x, x + w

        while top < bottom and left < right:
            # Top edge: left -> right
            for sx in range(left + step_px // 2, right, step_px):
                if rotated_mask[min(top + step_px // 2, map_h - 1), sx] == 255:
                    spiral_pts.append((sx, top + step_px // 2))
            top += step_px

            # Right edge: top -> bottom
            for sy in range(top + step_px // 2, bottom, step_px):
                if rotated_mask[sy, min(right - step_px // 2, map_w - 1)] == 255:
                    spiral_pts.append((right - step_px // 2, sy))
            right -= step_px

            # Bottom edge: right -> left
            if top < bottom:
                for sx in range(right - step_px // 2, left, -step_px):
                    if rotated_mask[min(bottom - step_px // 2, map_h - 1), sx] == 255:
                        spiral_pts.append((sx, bottom - step_px // 2))
                bottom -= step_px

            # Left edge: bottom -> top
            if left < right:
                for sy in range(bottom - step_px // 2, top, -step_px):
                    if rotated_mask[sy, max(left + step_px // 2, 0)] == 255:
                        spiral_pts.append((left + step_px // 2, sy))
                left += step_px

        # 4. UNROTATE + CONVERT TO GPS
        if not spiral_pts:
            return []

        pts_arr = np.array([spiral_pts], dtype=np.float32)
        pts_orig = cv2.transform(pts_arr, M_inv)[0]

        wps = []
        for p in pts_orig:
            gps = self.geo.pixels_to_gps(p[0], p[1])
            wps.append(gps)

        # 5. START FROM CLOSEST CORNER TO DRONE
        if drone_gps and wps:
            drone_px = self.geo.gps_to_pixels(drone_gps[0], drone_gps[1])
            dists = []
            for p in pts_orig:
                dists.append((p[0] - drone_px[0])**2 + (p[1] - drone_px[1])**2)
            start_idx = dists.index(min(dists))
            wps = wps[start_idx:] + wps[:start_idx]

        print(f"  Spiral: {len(wps)} waypoints")
        return wps