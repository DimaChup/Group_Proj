# vision.py
import cv2
import numpy as np
import os

# --- Backend Detection ---
# Priority 1: Ultralytics YOLO (accurate, for dev machines)
YOLO = None
try:
    from ultralytics import YOLO as _YOLO
    YOLO = _YOLO
except ImportError:
    pass

# Priority 2: TFLite direct (lightweight, for Pi)
TFLiteInterpreter = None
if YOLO is None:
    try:
        from tflite_runtime.interpreter import Interpreter
        TFLiteInterpreter = Interpreter
    except ImportError:
        try:
            from ai_edge_litert.interpreter import Interpreter
            TFLiteInterpreter = Interpreter
        except ImportError:
            try:
                import tensorflow as tf
                TFLiteInterpreter = tf.lite.Interpreter
            except ImportError:
                pass

# Priority 3: NCNN (ARM-optimized, fastest on Pi 5)
ncnn_available = False
try:
    import ncnn as _ncnn
    ncnn_available = True
except ImportError:
    pass

class VisionSystem:
    def __init__(self, camera_index=0, model_path="best.tflite"):
        self.cap = None
        self._picam = None
        cam_w, cam_h = 640, 480
        if camera_index is not None:
            try:
                import config as _cfg
                cam_w, cam_h = _cfg.IMAGE_W, _cfg.IMAGE_H
            except Exception:
                cam_w, cam_h = 640, 480
            print(f"[VISION] Opening Camera Index {camera_index} ({cam_w}x{cam_h})...")
            self.cap = cv2.VideoCapture(camera_index)
            if self.cap.isOpened():
                ret, _ = self.cap.read()
                if ret:
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)
                    self.cap.set(cv2.CAP_PROP_FPS, 30)
                    print("[VISION] Camera opened via OpenCV")
                else:
                    self.cap.release()
                    self.cap = None
            else:
                self.cap = None
            # Fallback: picamera2 (Raspberry Pi)
            if self.cap is None:
                try:
                    from picamera2 import Picamera2
                    self._picam = Picamera2()
                    self._picam.configure(self._picam.create_preview_configuration(
                        main={"size": (cam_w, cam_h), "format": "RGB888"}
                    ))
                    self._picam.start()
                    import time; time.sleep(1)
                    # Discard first 10 frames (AWB/exposure convergence)
                    for _ in range(10):
                        self._picam.capture_array()
                    print("[VISION] Warmup: discarded 10 frames")

                    # Apply white balance to fix blue tint
                    try:
                        import config as _cfg
                        awb_mode = getattr(_cfg, "CAMERA_AWB_MODE", "daylight")
                        if awb_mode == "manual":
                            gains = getattr(_cfg, "CAMERA_COLOUR_GAINS", (1.5, 1.2))
                            self._picam.set_controls({
                                "AwbEnable": False,
                                "ColourGains": gains
                            })
                            print(f"[VISION] AWB: manual gains R={gains[0]} B={gains[1]}")
                        elif awb_mode != "auto":
                            from libcamera import controls
                            awb_map = {
                                "daylight": controls.AwbModeEnum.Daylight,
                                "cloudy": controls.AwbModeEnum.Cloudy,
                                "indoor": controls.AwbModeEnum.Indoor,
                                "tungsten": controls.AwbModeEnum.Tungsten,
                                "fluorescent": controls.AwbModeEnum.Fluorescent,
                            }
                            mode = awb_map.get(awb_mode, controls.AwbModeEnum.Daylight)
                            self._picam.set_controls({"AwbMode": mode})
                            print(f"[VISION] AWB: {awb_mode}")
                        else:
                            print("[VISION] AWB: auto")
                        time.sleep(0.5)  # let AWB settle
                    except Exception as e:
                        print(f"[VISION] AWB setup skipped: {e}")

                    print("[VISION] Camera opened via picamera2")
                except Exception as e:
                    print(f"[VISION] No camera available: {e}")

        # --- LENS UNDISTORTION (precompute maps once) ---
        self._undistort_map1 = None
        self._undistort_map2 = None
        calib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration_data.npz")
        if os.path.exists(calib_path):
            try:
                calib = np.load(calib_path)
                mtx = calib["camera_matrix"]
                dist = calib["dist_coeffs"]
                img_w, img_h = cam_w, cam_h
                new_mtx, _ = cv2.getOptimalNewCameraMatrix(mtx, dist, (img_w, img_h), 0, (img_w, img_h))
                self._undistort_map1, self._undistort_map2 = cv2.initUndistortRectifyMap(
                    mtx, dist, None, new_mtx, (img_w, img_h), cv2.CV_16SC2)
                print(f"[VISION] Lens undistortion loaded (RMS={float(calib['rms_error']):.3f})")
            except Exception as e:
                print(f"[VISION] Lens calibration skipped: {e}")

        # --- AI MODEL SETUP ---
        self.model = None
        self.using_ai = False
        self._use_tflite_direct = False
        self._use_ncnn = False
        self._ncnn_net = None
        self.last_bbox_w = 0  # last detection bounding box width (pixels)
        self.last_class_name = ""  # last detected class name (e.g. "person", "dummy")
        self.last_bbox_h = 0  # last detection bounding box height (pixels)
        self.backend_name = "none"  # "ultralytics", "tflite", "ncnn"
        try:
            import config as _cfg
            self._conf_thresh = getattr(_cfg, "CONFIDENCE_THRESHOLD", 0.4)
        except Exception:
            self._conf_thresh = 0.4

        if not os.path.exists(model_path):
            print(f"[VISION] Model file not found: {model_path}")
            return

        # Option 0: NCNN (if model path points to ncnn directory or --backend ncnn)
        ncnn_requested = "--backend" in " ".join(os.sys.argv) and "ncnn" in " ".join(os.sys.argv)
        ncnn_model_dir = None
        if model_path.endswith('.tflite'):
            # Check if matching NCNN model exists alongside
            base_dir = os.path.dirname(model_path)
            ncnn_dir = os.path.join(base_dir, "ncnn", "best_ncnn_model")
            if os.path.exists(ncnn_dir):
                ncnn_model_dir = ncnn_dir
        elif os.path.isdir(model_path):
            ncnn_model_dir = model_path

        if ncnn_available and ncnn_requested and ncnn_model_dir:
            try:
                param_path = os.path.join(ncnn_model_dir, "model.ncnn.param")
                bin_path = os.path.join(ncnn_model_dir, "model.ncnn.bin")
                if os.path.exists(param_path) and os.path.exists(bin_path):
                    print(f"[VISION] Loading NCNN model from {ncnn_model_dir}...")
                    self._ncnn_net = _ncnn.Net()
                    self._ncnn_net.opt.num_threads = 4
                    self._ncnn_net.opt.use_vulkan_compute = False
                    self._ncnn_net.load_param(param_path)
                    self._ncnn_net.load_model(bin_path)
                    self._use_ncnn = True
                    self.using_ai = True
                    self.model = True
                    self.backend_name = "ncnn"
                    # Warmup
                    mat_in = _ncnn.Mat(640, 640, 3)
                    ex = self._ncnn_net.create_extractor()
                    ex.input("in0", mat_in)
                    ex.extract("out0")
                    print("[VISION] NCNN loaded! Warmup complete.")
                else:
                    print(f"[VISION] NCNN model files not found in {ncnn_model_dir}")
            except Exception as e:
                print(f"[VISION] NCNN Load Failed: {e}")

        # Option 1: Ultralytics YOLO (preferred - handles all output parsing)
        if not self.using_ai and YOLO is not None:
            try:
                print(f"[VISION] Loading Model via Ultralytics: {model_path}...")
                self.model = YOLO(model_path, task='detect')
                self.model(np.zeros((100, 100, 3), dtype=np.uint8), verbose=False)
                self.using_ai = True
                self.backend_name = "ultralytics"
                print("[VISION] AI Engine Loaded Successfully (Ultralytics)!")
            except Exception as e:
                print(f"[VISION] Ultralytics Load Failed: {e}")
                self.model = None

        # Option 2: Direct TFLite (lightweight fallback for Pi)
        elif TFLiteInterpreter is not None and model_path.endswith('.tflite'):
            try:
                print(f"[VISION] Loading TFLite Model: {model_path}...")
                self.interpreter = TFLiteInterpreter(model_path=model_path)
                self.interpreter.allocate_tensors()
                self._input_details = self.interpreter.get_input_details()
                self._output_details = self.interpreter.get_output_details()
                self._input_shape = self._input_details[0]['shape']
                self._input_dtype = self._input_details[0]['dtype']
                self._use_tflite_direct = True
                self.using_ai = True
                self.model = True  # flag so model-is-not-None checks pass
                self.backend_name = "tflite"
                print(f"[VISION] TFLite Loaded! Input: {self._input_shape} dtype={self._input_dtype}")
            except Exception as e:
                print(f"[VISION] TFLite Load Failed: {e}")
        else:
            print("[VISION] No AI backend available (install ultralytics or tflite-runtime)")

    def undistort(self, frame):
        """Apply lens undistortion if calibration is loaded. ~1-2ms at 640x480."""
        if self._undistort_map1 is not None and frame is not None:
            return cv2.remap(frame, self._undistort_map1, self._undistort_map2, cv2.INTER_LINEAR)
        return frame

    def detect_in_image(self, frame):
        """ Returns: found (bool), x, y, confidence (float) """
        if frame is None: return False, 0, 0, 0.0
        if not self.using_ai: return False, 0, 0, 0.0
        frame = self.undistort(frame)

        _conf_thresh = self._conf_thresh

        # --- NCNN inference (fastest on Pi 5) ---
        if self._use_ncnn:
            h, w = frame.shape[:2]
            # Preprocess: resize to 640x640, BGR→RGB, normalize
            img = cv2.resize(frame, (640, 640))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            mat_in = _ncnn.Mat.from_pixels(img_rgb, _ncnn.Mat.PixelType.PIXEL_RGB, 640, 640)
            mean_vals = [0.0, 0.0, 0.0]
            norm_vals = [1/255.0, 1/255.0, 1/255.0]
            mat_in.substract_mean_normalize(mean_vals, norm_vals)

            ex = self._ncnn_net.create_extractor()
            ex.input("in0", mat_in)
            ret, mat_out = ex.extract("out0")

            # Parse YOLOv8 output: same format as TFLite [1, 5+nclass, num_detections]
            output = np.array(mat_out)
            if output.ndim == 2:
                preds = output
            else:
                preds = output.reshape(-1, output.shape[-1]) if output.ndim == 3 else output

            if preds.shape[0] < preds.shape[-1]:
                preds = preds.T  # -> [num_detections, 5+nclass]

            best_conf = 0.0
            best_det = None
            for det in preds:
                cls_id = int(np.argmax(det[4:]))
                conf = float(det[4 + cls_id])
                if conf > _conf_thresh and conf > best_conf:
                    best_conf = conf
                    best_det = det

            if best_det is not None:
                raw_cx, raw_cy = best_det[0], best_det[1]
                raw_bw, raw_bh = best_det[2], best_det[3]
                # NCNN output may be in pixel coords (0-640) or normalized (0-1)
                # If values > 1.5, they're pixel coords relative to 640x640 input
                if raw_cx > 1.5:
                    # Pixel coords — scale from 640x640 to actual frame size
                    cx = int(raw_cx * w / 640)
                    cy = int(raw_cy * h / 640)
                    bw = int(raw_bw * w / 640)
                    bh = int(raw_bh * h / 640)
                else:
                    # Normalized coords (0-1) — scale to frame size
                    cx = int(raw_cx * w)
                    cy = int(raw_cy * h)
                    bw = int(raw_bw * w)
                    bh = int(raw_bh * h)
                self.last_bbox_w = bw
                self.last_bbox_h = bh
                num_classes = len(best_det) - 4
                self.last_class_name = "dummy" if num_classes == 1 else f"cls{int(np.argmax(best_det[4:]))}"
                x1, y1 = max(0, cx - bw // 2), max(0, cy - bh // 2)
                x2, y2 = min(w, cx + bw // 2), min(h, cy + bh // 2)
                label = f"AI {best_conf:.2f} [{self.last_class_name}]"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                return True, cx, cy, float(best_conf)

            return False, 0, 0, 0.0

        # --- Direct TFLite inference (Pi fallback) ---
        if self._use_tflite_direct:
            h, w = frame.shape[:2]
            input_h, input_w = self._input_shape[1], self._input_shape[2]

            # Preprocess: BGR->RGB, resize, normalize
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (input_w, input_h))
            if self._input_dtype == np.float32:
                img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=0)

            # Run inference
            self.interpreter.set_tensor(self._input_details[0]['index'], img)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self._output_details[0]['index'])

            # Parse YOLOv8 output: [1, 5+nclass, num_detections]
            preds = output[0]
            if preds.shape[0] < preds.shape[-1]:
                preds = preds.T  # -> [num_detections, 5+nclass]

            # Columns: cx, cy, w, h, class_conf...
            best_conf = 0.0
            best_det = None
            best_cls_id = 0
            for det in preds:
                cls_id = int(np.argmax(det[4:]))
                conf = float(det[4 + cls_id])
                if conf > _conf_thresh and conf > best_conf:
                    best_conf = conf
                    best_det = det
                    best_cls_id = cls_id

            # COCO class names for TFLite multi-class models
            COCO_NAMES = {0:"person",1:"bicycle",2:"car",3:"motorcycle",4:"airplane",5:"bus",
                6:"train",7:"truck",8:"boat",9:"traffic light",10:"fire hydrant",11:"stop sign",
                12:"parking meter",13:"bench",14:"bird",15:"cat",16:"dog",17:"horse",18:"sheep",
                19:"cow",20:"elephant",24:"backpack",25:"umbrella",26:"handbag",27:"tie",
                28:"suitcase",39:"bottle",56:"chair",57:"couch",58:"potted plant",59:"bed",
                60:"dining table",62:"tv",63:"laptop",64:"mouse",67:"cell phone"}

            if best_det is not None:
                cx = int(best_det[0] * w)
                cy = int(best_det[1] * h)
                bw = int(best_det[2] * w)
                bh = int(best_det[3] * h)
                self.last_bbox_w = bw
                self.last_bbox_h = bh
                num_classes = len(best_det) - 4
                self.last_class_name = COCO_NAMES.get(best_cls_id, f"cls{best_cls_id}") if num_classes > 1 else "dummy"
                x1 = max(0, cx - bw // 2)
                y1 = max(0, cy - bh // 2)
                x2 = min(w, cx + bw // 2)
                y2 = min(h, cy + bh // 2)
                label = f"AI {best_conf:.2f} [{self.last_class_name}]"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                return True, cx, cy, float(best_conf)

            return False, 0, 0, 0.0

        # --- Ultralytics YOLO inference (primary) ---
        results = self.model(frame, conf=_conf_thresh, verbose=False)
        if results[0].boxes:
            best_box = max(results[0].boxes, key=lambda x: x.conf[0])
            x, y, w, h = best_box.xywh[0].cpu().numpy()
            conf = float(best_box.conf[0])
            self.last_bbox_w = int(w)
            self.last_bbox_h = int(h)
            # Store class name for display
            cls_id = int(best_box.cls[0])
            names = self.model.names if hasattr(self.model, 'names') else {}
            self.last_class_name = names.get(cls_id, f"cls{cls_id}")
            x1, y1, x2, y2 = best_box.xyxy[0].cpu().numpy()
            label = f"AI {conf:.2f} [{self.last_class_name}]"
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, label, (int(x1), int(y1)-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            return True, int(x), int(y), conf

        return False, 0, 0, 0.0

    @staticmethod
    def _gray_world(frame):
        """Gray world auto white balance — neutralises color cast."""
        f = frame.astype(np.float32)
        avg_b, avg_g, avg_r = f[:,:,0].mean(), f[:,:,1].mean(), f[:,:,2].mean()
        avg_all = (avg_b + avg_g + avg_r) / 3.0
        if avg_b > 0: f[:,:,0] = np.clip(f[:,:,0] * (avg_all / avg_b), 0, 255)
        if avg_g > 0: f[:,:,1] = np.clip(f[:,:,1] * (avg_all / avg_g), 0, 255)
        if avg_r > 0: f[:,:,2] = np.clip(f[:,:,2] * (avg_all / avg_r), 0, 255)
        return f.astype(np.uint8)

    def get_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if not ret:
                return None
        elif self._picam:
            frame = self._picam.capture_array()
            # IMX296 Global Shutter: sensor outputs BGR despite RGB888 label
            # No conversion needed — data is already in OpenCV's BGR format
        else:
            return None

        # Apply color correction if enabled
        try:
            import config as _cfg
            if getattr(_cfg, "CAMERA_COLOR_CORRECTION", False):
                frame = self._gray_world(frame)
            # Flip 180° if camera is mounted inverted
            if getattr(_cfg, "CAMERA_FLIP_180", False):
                frame = cv2.flip(frame, -1)
        except Exception:
            pass

        return frame

    def process_frame_manually(self, frame):
        return self.detect_in_image(frame)

    def release(self):
        if self.cap: self.cap.release()
        if self._picam:
            try: self._picam.stop()
            except Exception: pass
