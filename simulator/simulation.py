# simulation.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
import math
import config
from utils import overlay_image_alpha

class SimulationEnvironment:
    def __init__(self, geo_transformer):
        self.geo = geo_transformer
        
        # Load Map
        self.full_map = cv2.imread(config.MAP_FILE)
        if self.full_map is None:
            print(f"Error: '{config.MAP_FILE}' not found. Creating a fake green map.")
            self.full_map = np.zeros((1000, 1000, 3), dtype=np.uint8)
            self.full_map[:] = (34, 139, 34)
            cv2.line(self.full_map, (0,0), (1000,1000), (255,255,255), 2)
        
        self.map_h, self.map_w = self.full_map.shape[:2]
        self.coverage_overlay = np.zeros_like(self.full_map)

        # Pre-scaled map for god view rendering (avoids 63MB copy every frame)
        # The god view is always resized to IMAGE_H height, so we can work at
        # a reduced resolution and save ~90% of memory ops per frame.
        _god_target_h = config.IMAGE_H
        self._god_scale = _god_target_h / self.map_h
        self._god_w = int(self.map_w * self._god_scale)
        self._god_h = _god_target_h
        self._god_map = cv2.resize(self.full_map, (self._god_w, self._god_h))
        self._god_coverage = np.zeros_like(self._god_map)
        print(f"God view: {self.map_w}x{self.map_h} -> {self._god_w}x{self._god_h} "
              f"({self._god_map.nbytes/1e6:.1f}MB vs {self.full_map.nbytes/1e6:.1f}MB)")
        
        # Load Dummy + Cone Assets
        self.dummy_img = cv2.imread(config.DUMMY_FILE, cv2.IMREAD_UNCHANGED)
        if self.dummy_img is None:
            print(f"Warning: '{config.DUMMY_FILE}' not found. Stickman mode only.")
        self.cone_img = cv2.imread(config.CONE_FILE, cv2.IMREAD_UNCHANGED)
        if self.cone_img is None:
            print(f"Warning: '{config.CONE_FILE}' not found. Cone placement disabled.")
        self.pants_img = cv2.imread(config.PANTS_FILE, cv2.IMREAD_UNCHANGED)
        if self.pants_img is None:
            print(f"Warning: '{config.PANTS_FILE}' not found.")
        self.tshirt_img = cv2.imread(config.TSHIRT_FILE, cv2.IMREAD_UNCHANGED)
        if self.tshirt_img is None:
            print(f"Warning: '{config.TSHIRT_FILE}' not found.")
        self.backpack_img = cv2.imread(config.BACKPACK_FILE, cv2.IMREAD_UNCHANGED)
        if self.backpack_img is None:
            print(f"Warning: '{config.BACKPACK_FILE}' not found.")

        # Calc Sizes
        raw_radius = config.TARGET_REAL_RADIUS_M * self.geo.pix_per_m
        self.target_radius_px = max(2, int(raw_radius))
        print(f"Map Scale: 1m = {self.geo.pix_per_m:.2f} px")

        # Sim State — multi-target support
        self.sim_targets = []          # list of (x, y) pixel positions
        self.sim_target_types = []     # list of "dummy"/"cone"/"pants"/"tshirt"/"backpack"
        self.sim_target_type = "dummy"
        self.ALL_TARGET_TYPES = ["dummy", "cone", "pants", "tshirt", "backpack"]
        # Backwards compat aliases
        self.sim_target_px = None

    def setup_on_map(self, preload_polygon_gps=None, preload_transit_gps=None):
        """Interactive map setup. Preload polygon and/or transit path from GPS coords."""
        h, w = self.full_map.shape[:2]
        MAX_DISPLAY_H = 800
        scale_factor = 1.0
        if h > MAX_DISPLAY_H:
            scale_factor = MAX_DISPLAY_H / h
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            display_map = cv2.resize(self.full_map, (new_w, new_h))
        else:
            display_map = self.full_map.copy()

        targets = []           # list of (x, y) — first = real dummy
        target_types = []      # list of "dummy" or "cone" per target
        place_type = ["dummy"] # current placement type (mutable for closure)
        transit_wps = []       # list of (x, y) — pre-search transit waypoints
        search_polygon = []
        polygon_closed = False
        # Phases: "targets" → "transit" → "polygon" (or skip polygon if preloaded)
        phase = "targets"

        # Pre-load search polygon from GPS coords (skip drawing step)
        if preload_polygon_gps:
            for lat, lon in preload_polygon_gps:
                px = self.geo.gps_to_pixels(lat, lon)
                search_polygon.append((int(px[0]), int(px[1])))
            polygon_closed = True
            print(f"  Search polygon pre-loaded: {len(search_polygon)} points from KML")

        # Pre-load transit path from GPS coords (skip drawing step)
        if preload_transit_gps:
            for lat, lon in preload_transit_gps:
                px = self.geo.gps_to_pixels(lat, lon)
                transit_wps.append((int(px[0]), int(px[1])))
            print(f"  Transit path pre-loaded: {len(transit_wps)} waypoints")

        window_name = "Select Target"

        focus_polygon = []  # optional Focus Area for PLB beacon redirect
        focus_closed = False

        def _redraw(temp_vis):
            """Draw all elements on the display."""
            # Pre-compute heights for all asset types
            asset_h = {
                "dummy": max(20, int(config.DUMMY_HEIGHT_M * self.geo.pix_per_m * scale_factor)),
                "cone": max(10, int(config.CONE_HEIGHT_M * self.geo.pix_per_m * scale_factor)),
                "pants": max(10, int(config.PANTS_HEIGHT_M * self.geo.pix_per_m * scale_factor)),
                "tshirt": max(10, int(config.TSHIRT_HEIGHT_M * self.geo.pix_per_m * scale_factor)),
                "backpack": max(10, int(config.BACKPACK_HEIGHT_M * self.geo.pix_per_m * scale_factor)),
            }
            asset_img = {
                "dummy": self.dummy_img, "cone": self.cone_img,
                "pants": self.pants_img, "tshirt": self.tshirt_img, "backpack": self.backpack_img,
            }
            # Targets
            for i, tgt in enumerate(targets):
                sx, sy = int(tgt[0]*scale_factor), int(tgt[1]*scale_factor)
                ttype = target_types[i] if i < len(target_types) else "dummy"
                img = asset_img.get(ttype)
                if img is not None:
                    overlay_image_alpha(temp_vis, img, sx, sy, 0, asset_h.get(ttype, 20))
                else:
                    vis_radius = max(2, int(self.target_radius_px * scale_factor))
                    cv2.circle(temp_vis, (sx, sy), vis_radius, (0, 0, 255), -1)
                color = (0, 128, 255) if i == 0 else (255, 255, 0)
                label = f"{i+1}{ttype[0].upper()}"
                cv2.putText(temp_vis, label, (sx + 10, sy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            # Show current placement mode
            mode_text = f"Placing: {place_type[0].upper()} (C=cycle)"
            type_colors = {"dummy": (0,200,0), "cone": (0,255,255), "pants": (255,150,0), "tshirt": (200,0,200), "backpack": (0,150,255)}
            cv2.putText(temp_vis, mode_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       type_colors.get(place_type[0], (255,255,255)), 2)
            # Transit waypoints (cyan line + numbered circles)
            if len(transit_wps) > 0:
                for i, wp in enumerate(transit_wps):
                    sx, sy = int(wp[0]*scale_factor), int(wp[1]*scale_factor)
                    cv2.circle(temp_vis, (sx, sy), 5, (255, 255, 0), -1)
                    cv2.putText(temp_vis, f"T{i+1}", (sx + 8, sy - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                if len(transit_wps) > 1:
                    line_pts = [(int(w[0]*scale_factor), int(w[1]*scale_factor)) for w in transit_wps]
                    for j in range(len(line_pts)-1):
                        cv2.line(temp_vis, line_pts[j], line_pts[j+1], (255, 255, 0), 2)
            # Flight Area boundary (yellow, 6px)
            if hasattr(config, 'FLIGHT_AREA_GPS') and len(config.FLIGHT_AREA_GPS) >= 3:
                fa_pts = np.array([[int(self.geo.gps_to_pixels(lat, lon)[0]*scale_factor),
                                    int(self.geo.gps_to_pixels(lat, lon)[1]*scale_factor)]
                                   for lat, lon in config.FLIGHT_AREA_GPS], dtype=np.int32)
                cv2.polylines(temp_vis, [fa_pts], True, (0, 200, 255), 6)
            # SSSI no-fly zone (red fill 30% + red outline)
            if hasattr(config, 'SSSI_GPS') and len(config.SSSI_GPS) >= 3:
                sssi_pts = np.array([[int(self.geo.gps_to_pixels(lat, lon)[0]*scale_factor),
                                      int(self.geo.gps_to_pixels(lat, lon)[1]*scale_factor)]
                                     for lat, lon in config.SSSI_GPS], dtype=np.int32)
                overlay = temp_vis.copy()
                cv2.fillPoly(overlay, [sssi_pts], (0, 0, 180))
                cv2.addWeighted(overlay, 0.3, temp_vis, 0.7, 0, temp_vis)
                cv2.polylines(temp_vis, [sssi_pts], True, (0, 0, 255), 3)
                cx_s = int(np.mean(sssi_pts[:, 0]))
                cy_s = int(np.mean(sssi_pts[:, 1]))
                cv2.putText(temp_vis, "SSSI NFZ", (cx_s - 30, cy_s),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # TOL marker (cyan star)
            if hasattr(config, 'TAKEOFF_GPS') and config.TAKEOFF_GPS[0] != 0:
                tol_px = self.geo.gps_to_pixels(*config.TAKEOFF_GPS)
                tol_pt = (int(tol_px[0]*scale_factor), int(tol_px[1]*scale_factor))
                cv2.drawMarker(temp_vis, tol_pt, (255, 255, 0), cv2.MARKER_STAR, 20, 2)
                cv2.putText(temp_vis, "TOL", (tol_pt[0]+12, tol_pt[1]-8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            # Search polygon (green)
            if len(search_polygon) > 0:
                pts = [np.array([[int(p[0]*scale_factor), int(p[1]*scale_factor)] for p in search_polygon], dtype=np.int32)]
                cv2.polylines(temp_vis, pts, polygon_closed, (0, 255, 0), 2)
                for p in pts[0]: cv2.circle(temp_vis, tuple(p), 3, (0, 255, 0), -1)
            # Focus polygon (magenta — PLB beacon area)
            if len(focus_polygon) > 0:
                fpts = [np.array([[int(p[0]*scale_factor), int(p[1]*scale_factor)] for p in focus_polygon], dtype=np.int32)]
                cv2.polylines(temp_vis, fpts, focus_closed, (255, 0, 255), 2)
                for p in fpts[0]: cv2.circle(temp_vis, tuple(p), 4, (255, 0, 255), -1)
                if focus_closed:
                    cv2.putText(temp_vis, "FOCUS", (fpts[0][0][0]+5, fpts[0][0][1]-8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)

        def mouse_callback(event, x, y, flags, param):
            nonlocal phase, polygon_closed, focus_closed
            real_x = int(x / scale_factor)
            real_y = int(y / scale_factor)
            update = False

            if event == cv2.EVENT_LBUTTONDOWN:
                if phase == "targets":
                    targets.append((real_x, real_y))
                    target_types.append(place_type[0])
                    n = len(targets)
                    tname = place_type[0].upper()
                    label = f"REAL {tname}" if n == 1 else f"{tname} #{n}"
                    print(f"  Placed {label} at ({real_x}, {real_y})")
                    if n == 1:
                        print("  Left-click more targets, or Right-click to finish. C=toggle dummy/cone.")
                elif phase == "transit":
                    transit_wps.append((real_x, real_y))
                    print(f"  Transit WP {len(transit_wps)} at ({real_x}, {real_y})")
                elif phase == "focus" and not focus_closed:
                    focus_polygon.append((real_x, real_y))
                    print(f"  Focus point {len(focus_polygon)} at ({real_x}, {real_y})")
                elif phase == "polygon" and not polygon_closed:
                    search_polygon.append((real_x, real_y))
                update = True

            elif event == cv2.EVENT_RBUTTONDOWN:
                if phase == "targets" and len(targets) >= 1:
                    transit_preloaded = preload_transit_gps and len(transit_wps) > 0
                    if transit_preloaded and polygon_closed:
                        # Both preloaded — offer focus area drawing
                        phase = "focus"
                        print(f"  {len(targets)} target(s) placed.")
                        print("  Draw Focus Area (magenta) for PLB beacon. Left-click points, Right-click to close (or skip).")
                    elif transit_preloaded:
                        # Transit preloaded but need polygon
                        phase = "polygon"
                        print(f"  {len(targets)} target(s) placed. Transit pre-loaded ({len(transit_wps)} pts).")
                        print("Step 2: Left-click search polygon points, Right-click to close.")
                    else:
                        phase = "transit"
                        print(f"  {len(targets)} target(s) placed.")
                        print("Step 2: Left-click transit waypoints (cyan). Right-click when done (or skip).")
                elif phase == "transit":
                    if polygon_closed:
                        phase = "focus"
                        n = len(transit_wps)
                        print(f"  {n} transit waypoint(s).")
                        print("  Draw Focus Area (magenta) for PLB beacon. Left-click points, Right-click to close (or skip).")
                    else:
                        phase = "polygon"
                        n = len(transit_wps)
                        print(f"  {n} transit waypoint(s).")
                        print("Step 3: Left-click search polygon points, Right-click to close.")
                elif phase == "focus" and not focus_closed:
                    if len(focus_polygon) >= 3:
                        focus_closed = True
                        phase = "done"
                        print(f"  Focus Area closed ({len(focus_polygon)} points). Press KEY to Launch.")
                    else:
                        # Skip focus — no points or not enough
                        phase = "done"
                        print("  No Focus Area drawn. Press KEY to Launch.")
                elif phase == "polygon" and not polygon_closed and len(search_polygon) >= 3:
                    polygon_closed = True
                    phase = "focus"
                    print("Polygon Closed.")
                    print("  Draw Focus Area (magenta) for PLB beacon. Left-click points, Right-click to close (or skip).")
                update = True

            if update:
                temp_vis = display_map.copy()
                _redraw(temp_vis)
                cv2.imshow(window_name, temp_vis)

        cv2.namedWindow(window_name)
        # Draw preloaded elements on initial display
        temp = display_map.copy()
        if search_polygon:
            pts = [np.array([[int(p[0]*scale_factor), int(p[1]*scale_factor)] for p in search_polygon], dtype=np.int32)]
            cv2.polylines(temp, pts, True, (0, 255, 0), 2)
            for p in pts[0]:
                cv2.circle(temp, tuple(p), 3, (0, 255, 0), -1)
        if transit_wps:
            for i, wp in enumerate(transit_wps):
                sx, sy = int(wp[0]*scale_factor), int(wp[1]*scale_factor)
                cv2.circle(temp, (sx, sy), 6, (255, 255, 0), -1)
                cv2.putText(temp, f"T{i+1}", (sx + 10, sy - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
            if len(transit_wps) > 1:
                for j in range(len(transit_wps)-1):
                    p1 = (int(transit_wps[j][0]*scale_factor), int(transit_wps[j][1]*scale_factor))
                    p2 = (int(transit_wps[j+1][0]*scale_factor), int(transit_wps[j+1][1]*scale_factor))
                    cv2.line(temp, p1, p2, (255, 255, 0), 2)
        cv2.imshow(window_name, temp)
        cv2.setMouseCallback(window_name, mouse_callback)
        print("--- MISSION SETUP ---")
        transit_preloaded = preload_transit_gps and len(transit_wps) > 0
        if preload_polygon_gps and transit_preloaded:
            print("  Search polygon + transit path loaded.")
            print("1. Left-click to place targets (first = REAL). C=toggle dummy/cone. Right-click when done.")
            print("2. Press any KEY to start.")
        elif preload_polygon_gps:
            print("  Search polygon loaded from KML.")
            print("1. Left-click to place targets. C=cycle type (dummy/cone/pants/tshirt/backpack). Right-click when done.")
            print("2. Left-click transit waypoints (cyan path before search). Right-click when done/skip.")
            print("3. Press any KEY to start.")
        else:
            print("1. Left-click to place targets. C=cycle type (dummy/cone/pants/tshirt/backpack). Right-click when done.")
            print("2. Left-click transit waypoints (cyan). Right-click when done/skip.")
            print("3. Left-click search polygon points, Right-click to close.")
            print("4. Press any KEY to start.")
        # Wait for key — C toggles placement type during target phase
        while True:
            key = cv2.waitKey(100) & 0xFF
            if key == ord('c') and phase == "targets":
                idx = self.ALL_TARGET_TYPES.index(place_type[0])
                place_type[0] = self.ALL_TARGET_TYPES[(idx + 1) % len(self.ALL_TARGET_TYPES)]
                print(f"  Placement mode: {place_type[0].upper()}")
                temp_k = display_map.copy()
                _redraw(temp_k)
                cv2.imshow(window_name, temp_k)
            elif key == 255 or key == 0:
                continue  # no key pressed
            elif phase == "done":
                break
        try:
            cv2.destroyWindow(window_name)
        except cv2.error:
            pass

        self.sim_targets = targets
        self.sim_target_types = target_types
        self.sim_target_type = "dummy"
        # Backwards compat: first target as sim_target_px
        self.sim_target_px = targets[0] if targets else None
        return targets, "dummy", search_polygon, transit_wps, focus_polygon

    def get_drone_view(self, cx, cy, alt, yaw):
        fov = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
        safe_alt = max(1.0, alt)
        ground_w = 2 * safe_alt * math.tan(fov / 2)
        view_w_px = int(ground_w * self.geo.pix_per_m)
        view_h_px = int(view_w_px * (config.IMAGE_H / config.IMAGE_W))
        
        diag = int(math.sqrt(view_w_px**2 + view_h_px**2))
        x1 = cx - diag // 2; y1 = cy - diag // 2
        x2 = x1 + diag; y2 = y1 + diag
        
        pad_l = max(0, -x1); pad_t = max(0, -y1)
        pad_r = max(0, x2 - self.map_w); pad_b = max(0, y2 - self.map_h)
        
        sx1 = x1 + pad_l; sy1 = y1 + pad_t
        sx2 = x2 - pad_r; sy2 = y2 - pad_b
        
        if sx2 > sx1 and sy2 > sy1:
            raw_crop = self.full_map[sy1:sy2, sx1:sx2]
            if pad_l > 0 or pad_t > 0 or pad_r > 0 or pad_b > 0:
                raw_crop = cv2.copyMakeBorder(raw_crop, pad_t, pad_b, pad_l, pad_r, cv2.BORDER_CONSTANT, value=(0,0,0))
        else:
            raw_crop = np.zeros((diag, diag, 3), dtype=np.uint8)
            
        center = (diag // 2, diag // 2)
        M = cv2.getRotationMatrix2D(center, math.degrees(yaw), 1.0)
        rotated_patch = cv2.warpAffine(raw_crop, M, (diag, diag))
        
        start_x = (diag - view_w_px) // 2
        start_y = (diag - view_h_px) // 2
        crop = rotated_patch[start_y:start_y+view_h_px, start_x:start_x+view_w_px]
        
        final_view = cv2.resize(crop, (config.IMAGE_W, config.IMAGE_H))
            
        # Render ALL targets in camera view
        angle_rad = -yaw
        scale = config.IMAGE_W / max(1, view_w_px)
        px_per_m_screen = config.IMAGE_W / ground_w
        for ti, tgt in enumerate(self.sim_targets):
            dx = tgt[0] - cx
            dy = tgt[1] - cy
            dx_rot = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
            dy_rot = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
            screen_x = int((config.IMAGE_W / 2) + (dx_rot * scale))
            screen_y = int((config.IMAGE_H / 2) + (dy_rot * scale))
            ttype = self.sim_target_types[ti] if ti < len(self.sim_target_types) else "dummy"
            height_map = {"dummy": config.DUMMY_HEIGHT_M, "cone": config.CONE_HEIGHT_M,
                          "pants": config.PANTS_HEIGHT_M, "tshirt": config.TSHIRT_HEIGHT_M,
                          "backpack": config.BACKPACK_HEIGHT_M}
            img_map = {"dummy": self.dummy_img, "cone": self.cone_img,
                       "pants": self.pants_img, "tshirt": self.tshirt_img, "backpack": self.backpack_img}
            t_img = img_map.get(ttype)
            if t_img is not None:
                t_h = int(height_map.get(ttype, 1.0) * px_per_m_screen)
                overlay_image_alpha(final_view, t_img, screen_x, screen_y, 0, t_h, rotation_deg=math.degrees(yaw))
            else:
                dot_rad_screen = int(config.TARGET_REAL_RADIUS_M * px_per_m_screen)
                cv2.circle(final_view, (screen_x, screen_y), max(3, dot_rad_screen), (0, 0, 255), -1)

        return final_view, view_w_px, view_h_px

    def get_god_view(self, cx, cy, yaw, view_w_px, view_h_px, zoom_level, virtual_poly, search_poly, target_gps, landing_gps, geo_tool, logged_items=None, detection_clusters=None, active_cluster_idx=None, search_wps=None, search_wp_index=0, transit_wps_gps=None, transit_wp_index=0, current_state=None, rescan_pass=0, items_of_interest=None, rejected_targets=None, nfz_buffer_m=0, nfz_repulsion_vec=None, nfz_arrows=False):
        display_map = self.full_map.copy()
        
        # Render ALL targets on god view
        god_height_map = {"dummy": config.DUMMY_HEIGHT_M, "cone": config.CONE_HEIGHT_M,
                          "pants": config.PANTS_HEIGHT_M, "tshirt": config.TSHIRT_HEIGHT_M,
                          "backpack": config.BACKPACK_HEIGHT_M}
        god_img_map = {"dummy": self.dummy_img, "cone": self.cone_img,
                       "pants": self.pants_img, "tshirt": self.tshirt_img, "backpack": self.backpack_img}
        for ti, tgt in enumerate(self.sim_targets):
            ttype = self.sim_target_types[ti] if ti < len(self.sim_target_types) else "dummy"
            t_img = god_img_map.get(ttype)
            if t_img is not None:
                t_h = max(5, int(god_height_map.get(ttype, 1.0) * self.geo.pix_per_m))
                overlay_image_alpha(display_map, t_img, tgt[0], tgt[1], 0, t_h)
            else:
                cv2.circle(display_map, tgt, self.target_radius_px, (0, 0, 255), -1)

        # Draw Polygons
        if len(search_poly) > 1:
              cv2.polylines(display_map, [np.array(search_poly, np.int32)], True, (0, 255, 0), 2)
        if len(virtual_poly) > 0:
              cv2.drawContours(display_map, [virtual_poly], -1, (255, 0, 255), 2)
        # Draw SSSI no-fly zone (red with faint fill)
        if config.SSSI_GPS:
            sssi_pts = np.array([geo_tool.gps_to_pixels(lat, lon) for lat, lon in config.SSSI_GPS], np.int32)
            # Faint red fill
            overlay = display_map.copy()
            cv2.fillPoly(overlay, [sssi_pts], (0, 0, 180))
            cv2.addWeighted(overlay, 0.15, display_map, 0.85, 0, display_map)
            # Red border
            cv2.polylines(display_map, [sssi_pts], True, (0, 0, 255), 2)
            cx_s, cy_s = sssi_pts.mean(axis=0).astype(int)
            cv2.putText(display_map, "SSSI NFZ", (cx_s - 30, cy_s), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            # Inner NFZ polygon (20m inside boundary) — bright pink, bold
            if nfz_buffer_m > 0:
                if not hasattr(self, '_nfz_inner_contours'):
                    inner_px = int(config.NFZ_INNER_OFFSET_M * geo_tool.pix_per_m)
                    h_map, w_map = self.full_map.shape[:2]
                    # Work at 1/4 resolution for fast morphological ops
                    S = 4
                    sh, sw = h_map // S, w_map // S
                    small_pts = (sssi_pts // S).astype(np.int32)
                    mask_s = np.zeros((sh, sw), dtype=np.uint8)
                    cv2.fillPoly(mask_s, [small_pts], 255)
                    k = max(3, (inner_px // S) * 2 + 1)
                    eroded = cv2.erode(mask_s, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
                    contours_s, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    self._nfz_inner_contours = [c * S for c in contours_s]  # scale back up
                if self._nfz_inner_contours:
                    cv2.drawContours(display_map, self._nfz_inner_contours, -1, (255, 0, 255), 3)
            # Repulsion buffer (orange outline)
            if nfz_buffer_m > 0:
                if not hasattr(self, '_nfz_buffer_contours'):
                    buf_px = int(nfz_buffer_m * geo_tool.pix_per_m)
                    h_map, w_map = self.full_map.shape[:2]
                    S = 4
                    sh, sw = h_map // S, w_map // S
                    small_pts = (sssi_pts // S).astype(np.int32)
                    mask_s = np.zeros((sh, sw), dtype=np.uint8)
                    cv2.fillPoly(mask_s, [small_pts], 255)
                    k = max(3, (buf_px // S) * 2 + 1)
                    dilated = cv2.dilate(mask_s, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
                    contours_s, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    self._nfz_buffer_contours = [c * S for c in contours_s]
                if self._nfz_buffer_contours:
                    cv2.drawContours(display_map, self._nfz_buffer_contours, -1, (0, 140, 255), 2)
            # Vector field around SSSI (only with --arrows flag)
            if nfz_buffer_m > 0 and nfz_arrows:
                if not hasattr(self, '_nfz_vector_field'):
                    from geofence import NFZGeofence
                    _fence = NFZGeofence(geo_tool)
                    self._nfz_vector_field = []
                    step = 25
                    h_map, w_map = self.full_map.shape[:2]
                    for gy in range(step, h_map, step):
                        for gx in range(step, w_map, step):
                            lat, lon = geo_tool.pixels_to_gps(gx, gy)
                            dist, inside = _fence.distance_to_boundary(lat, lon)
                            if dist > nfz_buffer_m or inside:
                                continue
                            off_lat, off_lon = _fence.repulsive_offset(lat, lon)
                            if abs(off_lat) < 1e-9 and abs(off_lon) < 1e-9:
                                continue
                            # Negate for display (repulsive_offset returns inverted signs)
                            dy_m = -off_lat * 111320
                            dx_m = -off_lon * 111320 * math.cos(math.radians(lat))
                            mag = math.sqrt(dx_m**2 + dy_m**2)
                            if mag < 0.01:
                                continue
                            adx = int(dx_m / mag * 18)
                            ady = int(-dy_m / mag * 18)  # pixel y inverted
                            col = (0, 0, 200) if dist < 4 else (0, 100, 200) if dist < 7 else (0, 180, 180)
                            self._nfz_vector_field.append((gx, gy, gx+adx, gy+ady, col))
                for vf in self._nfz_vector_field:
                    cv2.arrowedLine(display_map, (vf[0], vf[1]), (vf[2], vf[3]), vf[4], 1, tipLength=0.4)

        # Drone repulsion arrow (bold, on drone position)
        if nfz_repulsion_vec and (abs(nfz_repulsion_vec[0]) > 1e-8 or abs(nfz_repulsion_vec[1]) > 1e-8):
            off_lat, off_lon = nfz_repulsion_vec
            # Negate for display (repulsive_offset returns inverted signs)
            dy_m = -off_lat * 111320
            dx_m = -off_lon * 111320 * math.cos(math.radians(51.42))
            arrow_len = math.sqrt(dx_m**2 + dy_m**2)
            if arrow_len > 0.01:
                vis_len = 80
                dx_px = int(dx_m / arrow_len * vis_len)
                dy_px = int(-dy_m / arrow_len * vis_len)
                end_x, end_y = cx + dx_px, cy + dy_px
                strength = min(1.0, arrow_len * 200)
                color = (0, 0, 255) if strength > 0.6 else (0, 140, 255) if strength > 0.3 else (0, 255, 0)
                cv2.arrowedLine(display_map, (cx, cy), (end_x, end_y), (0, 0, 0), 7, tipLength=0.35)
                cv2.arrowedLine(display_map, (cx, cy), (end_x, end_y), color, 4, tipLength=0.35)
                cv2.putText(display_map, f"REPEL {arrow_len:.1f}m", (end_x+8, end_y-8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
                cv2.putText(display_map, f"REPEL {arrow_len:.1f}m", (end_x+8, end_y-8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Draw flight boundary (yellow)
        if config.FLIGHT_AREA_GPS:
            flight_pts = np.array([geo_tool.gps_to_pixels(lat, lon) for lat, lon in config.FLIGHT_AREA_GPS], np.int32)
            cv2.polylines(display_map, [flight_pts], True, (0, 200, 255), 6)
            # Label (use local vars to avoid overwriting drone cx,cy)
            fa_cx = int(np.mean(flight_pts[:, 0]))
            fa_cy = int(np.min(flight_pts[:, 1])) - 10
            cv2.putText(display_map, "FLIGHT AREA", (fa_cx - 60, fa_cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

        # Draw Coverage (only during SEARCH — transit doesn't count as swept)
        # Pass 0 = cyan/yellow, pass 1+ = orange (different color per rescan)
        coverage_colors = [(255, 255, 0), (0, 140, 255), (0, 255, 128)]  # yellow, orange, green
        cov_color = coverage_colors[min(rescan_pass, len(coverage_colors) - 1)]
        rect = ((cx, cy), (view_w_px, view_h_px), math.degrees(yaw))
        box = np.int32(cv2.boxPoints(rect))
        if current_state == "SEARCH":
            cv2.fillPoly(self.coverage_overlay, [box], cov_color)
        cv2.addWeighted(self.coverage_overlay, 0.2, display_map, 1.0, 0, display_map)
        
        cv2.circle(display_map, (cx, cy), 8, (255, 0, 0), -1)
        cv2.drawContours(display_map, [box], 0, (0, 255, 255), 2)
        
        # Draw numbered cluster estimates (replaces single green EST)
        cluster_colors = [
            (0, 255, 0), (0, 200, 255), (255, 200, 0), (255, 0, 255),
            (0, 255, 255), (200, 100, 255), (100, 255, 200), (255, 150, 100),
        ]
        if detection_clusters:
            for ci, cl in enumerate(detection_clusters):
                if cl.get("best_gps"):
                    clx, cly = geo_tool.gps_to_pixels(cl["best_gps"][0], cl["best_gps"][1])
                    color = cluster_colors[ci % len(cluster_colors)]
                    # Active cluster: filled + ring; others: ring only
                    if ci == active_cluster_idx:
                        cv2.circle(display_map, (clx, cly), 10, color, -1)
                        cv2.circle(display_map, (clx, cly), 16, color, 2)
                    else:
                        cv2.circle(display_map, (clx, cly), 10, color, 2)
                    cid = cl.get("id", ci+1)
                    label = f"#{cid} ({cl['detection_count']})"
                    cv2.putText(display_map, label, (clx + 18, cly + 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    # Total average marker (small square, same color)
                    if cl.get("total_gps"):
                        tx, ty = geo_tool.gps_to_pixels(cl["total_gps"][0], cl["total_gps"][1])
                        cv2.rectangle(display_map, (tx-5, ty-5), (tx+5, ty+5), color, 2)
                    # Kalman filter marker (triangle, same color)
                    if cl.get("kalman_gps"):
                        kx, ky = geo_tool.gps_to_pixels(cl["kalman_gps"][0], cl["kalman_gps"][1])
                        tri = np.array([(kx, ky-7), (kx+6, ky+5), (kx-6, ky+5)], np.int32)
                        cv2.fillPoly(display_map, [tri], color)
        elif target_gps[0] != 0:
            # Fallback: single green EST if no clusters provided
            tx, ty = geo_tool.gps_to_pixels(target_gps[0], target_gps[1])
            cv2.circle(display_map, (tx, ty), 8, (0, 255, 0), -1)
            cv2.circle(display_map, (tx, ty), 14, (0, 255, 0), 2)
            cv2.putText(display_map, "EST", (tx + 16, ty + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if landing_gps[0] != 0:
            lx, ly = geo_tool.gps_to_pixels(landing_gps[0], landing_gps[1])
            cv2.circle(display_map, (lx, ly), 8, (255, 0, 255), -1)  # filled pink = landing
            cv2.circle(display_map, (lx, ly), 20, (255, 255, 255), 2)
            cv2.putText(display_map, "LAND", (lx + 22, ly + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

        # Draw logged items (IOI = cyan, FP = red X)
        if logged_items:
            for item in logged_items:
                gps = item.get("gps")
                if gps:
                    ix, iy = geo_tool.gps_to_pixels(gps[0], gps[1])
                    if item["type"] == "interest":
                        # Cyan diamond
                        pts = np.array([(ix, iy-10), (ix+8, iy), (ix, iy+10), (ix-8, iy)], np.int32)
                        cv2.fillPoly(display_map, [pts], (255, 255, 0))
                        cv2.putText(display_map, "IOI", (ix + 12, iy + 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                    else:
                        # Red X for false positive
                        cv2.line(display_map, (ix-6, iy-6), (ix+6, iy+6), (0, 0, 255), 2)
                        cv2.line(display_map, (ix-6, iy+6), (ix+6, iy-6), (0, 0, 255), 2)
                        cv2.putText(display_map, "FP", (ix + 10, iy + 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        # Draw search waypoint path (zigzag inside polygon)
        if search_wps:
            wp_pts = [geo_tool.gps_to_pixels(lat, lon) for lat, lon in search_wps]
            for j in range(len(wp_pts)-1):
                p1 = (int(wp_pts[j][0]), int(wp_pts[j][1]))
                p2 = (int(wp_pts[j+1][0]), int(wp_pts[j+1][1]))
                if j < search_wp_index:
                    cv2.line(display_map, p1, p2, (0, 200, 0), 3)
                else:
                    cv2.line(display_map, p1, p2, (255, 255, 255), 2)
            if wp_pts:
                sp = (int(wp_pts[0][0]), int(wp_pts[0][1]))
                ep = (int(wp_pts[-1][0]), int(wp_pts[-1][1]))
                cv2.circle(display_map, sp, 8, (0, 255, 0), -1)
                cv2.putText(display_map, "S", (sp[0]+10, sp[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.circle(display_map, ep, 8, (0, 0, 255), -1)
                cv2.putText(display_map, "E", (ep[0]+10, ep[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            if current_state == "SEARCH" and search_wp_index < len(wp_pts):
                cur = wp_pts[search_wp_index]
                cv2.circle(display_map, (int(cur[0]), int(cur[1])), 10, (0, 255, 255), 3)

        # Draw transit path (cyan line + dots)
        if transit_wps_gps:
            tw_pts = [geo_tool.gps_to_pixels(lat, lon) for lat, lon in transit_wps_gps]
            for i, pt in enumerate(tw_pts):
                cv2.circle(display_map, (int(pt[0]), int(pt[1])), 8, (0, 255, 255), -1)
                cv2.putText(display_map, f"T{i+1}", (int(pt[0])+12, int(pt[1])-8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            if len(tw_pts) > 1:
                for j in range(len(tw_pts)-1):
                    p1 = (int(tw_pts[j][0]), int(tw_pts[j][1]))
                    p2 = (int(tw_pts[j+1][0]), int(tw_pts[j+1][1]))
                    cv2.line(display_map, p1, p2, (0, 255, 255), 3)
            if current_state == "PRE_WAYPOINTS" and transit_wp_index < len(tw_pts):
                cur = tw_pts[transit_wp_index]
                cv2.circle(display_map, (int(cur[0]), int(cur[1])), 14, (0, 0, 255), 3)

        # Draw rejected targets (red X) — false positives
        if rejected_targets:
            for idx, (rlat, rlon) in enumerate(rejected_targets):
                rx, ry = geo_tool.gps_to_pixels(rlat, rlon)
                cv2.circle(display_map, (rx, ry), 10, (0, 0, 255), -1)  # red dot
                cv2.circle(display_map, (rx, ry), 10, (255, 255, 255), 2)  # white border
                # X mark
                cv2.line(display_map, (rx-7, ry-7), (rx+7, ry+7), (255, 255, 255), 2)
                cv2.line(display_map, (rx+7, ry-7), (rx-7, ry+7), (255, 255, 255), 2)
                cv2.putText(display_map, f"FP", (rx + 15, ry + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Draw items of interest (blue markers)
        if items_of_interest:
            for idx, item in enumerate(items_of_interest):
                ix, iy = geo_tool.gps_to_pixels(item['lat'], item['lon'])
                radius_px = max(15, int(3.0 * geo_tool.pix_per_m))
                cv2.circle(display_map, (ix, iy), radius_px, (255, 50, 50), 2)
                cv2.circle(display_map, (ix, iy), 12, (255, 50, 50), -1)
                cv2.circle(display_map, (ix, iy), 12, (255, 255, 255), 2)
                cv2.putText(display_map, f"I{idx+1}", (ix + 18, iy + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 50, 50), 2)

        # Apply Zoom
        if zoom_level > 1.0:
            h, w = display_map.shape[:2]
            crop_h = int(h / zoom_level)
            crop_w = int(w / zoom_level)
            x1 = max(0, min(w - crop_w, cx - crop_w // 2))
            y1 = max(0, min(h - crop_h, cy - crop_h // 2))
            x2 = x1 + crop_w; y2 = y1 + crop_h
            display_map = display_map[y1:y2, x1:x2]

        target_h = config.IMAGE_H
        base_scale = target_h / self.map_h
        target_w = int(self.map_w * base_scale)
        if zoom_level > 1.0: return cv2.resize(display_map, (config.IMAGE_H, config.IMAGE_H))
        return cv2.resize(display_map, (target_w, target_h))