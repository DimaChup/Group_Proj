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
            import tensorflow as tf
            TFLiteInterpreter = tf.lite.Interpreter
        except ImportError:
            pass

class VisionSystem:
    def __init__(self, camera_index=0, model_path="best.tflite"):
        self.cap = None
        if camera_index is not None:
            print(f"[VISION] Opening Camera Index {camera_index}...")
            self.cap = cv2.VideoCapture(camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

        # --- AI MODEL SETUP ---
        self.model = None
        self.using_ai = False
        self._use_tflite_direct = False

        if not os.path.exists(model_path):
            print(f"[VISION] Model file not found: {model_path}")
            return

        # Option 1: Ultralytics YOLO (preferred - handles all output parsing)
        if YOLO is not None:
            try:
                print(f"[VISION] Loading Model via Ultralytics: {model_path}...")
                self.model = YOLO(model_path, task='detect')
                self.model(np.zeros((100, 100, 3), dtype=np.uint8), verbose=False)
                self.using_ai = True
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
                print(f"[VISION] TFLite Loaded! Input: {self._input_shape} dtype={self._input_dtype}")
            except Exception as e:
                print(f"[VISION] TFLite Load Failed: {e}")
        else:
            print("[VISION] No AI backend available (install ultralytics or tflite-runtime)")

    def detect_in_image(self, frame):
        """ Returns: found (bool), x, y, confidence (float) """
        if frame is None: return False, 0, 0, 0.0
        if not self.using_ai: return False, 0, 0, 0.0

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
            for det in preds:
                conf = float(np.max(det[4:]))  # best class confidence
                if conf > 0.4 and conf > best_conf:
                    best_conf = conf
                    best_det = det

            if best_det is not None:
                cx = int(best_det[0] * w)
                cy = int(best_det[1] * h)
                bw = int(best_det[2] * w)
                bh = int(best_det[3] * h)
                x1 = cx - bw // 2
                y1 = cy - bh // 2
                x2 = cx + bw // 2
                y2 = cy + bh // 2
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"AI {best_conf:.2f}", (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                return True, cx, cy, float(best_conf)

            return False, 0, 0, 0.0

        # --- Ultralytics YOLO inference (primary) ---
        results = self.model(frame, conf=0.4, verbose=False)
        if results[0].boxes:
            best_box = max(results[0].boxes, key=lambda x: x.conf[0])
            x, y, w, h = best_box.xywh[0].cpu().numpy()
            conf = float(best_box.conf[0])
            x1, y1, x2, y2 = best_box.xyxy[0].cpu().numpy()
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f"AI {conf:.2f}", (int(x1), int(y1)-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            return True, int(x), int(y), conf

        return False, 0, 0, 0.0

    def get_frame(self):
        if not self.cap: return None
        ret, frame = self.cap.read()
        return frame if ret else None

    def process_frame_manually(self, frame):
        return self.detect_in_image(frame)

    def release(self):
        if self.cap: self.cap.release()
