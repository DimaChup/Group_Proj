# NCNN Integration into vision.py — TODO for Next Session

## What Works Now
- `ncnn_video_player.py` — loads NCNN directly, bypasses vision.py, works perfectly
- `ncnn_benchmark.py` — loads through vision.py with `--backend ncnn`, worked on Pi
- `diagnostics.py` — loaded NCNN through vision.py, showed 9.2 FPS on Pi

## What Doesn't Work
- `video_test_compare_v2.py` — argparse ate the `--backend ncnn` flag before vision.py saw it
- Detection quality seemed different through vision.py vs direct — needs investigation

## Root Cause
- vision.py checks `"--backend" in " ".join(os.sys.argv)` — fragile
- Scripts that use argparse consume `--backend` before vision.py reads sys.argv
- Multiple VisionSystem instances in same script (model switching) — sys.argv state gets confused

## Fix Plan
1. **Backup vision.py** first
2. **Change NCNN detection from sys.argv to explicit parameter:**
   ```python
   # BEFORE (fragile):
   ncnn_requested = "--backend" in " ".join(os.sys.argv) and "ncnn" in " ".join(os.sys.argv)

   # AFTER (explicit):
   class VisionSystem:
       def __init__(self, camera_index=0, model_path="best.tflite", backend="auto"):
           # backend: "auto" | "tflite" | "ncnn" | "ultralytics"
   ```
3. **Backend selection logic:**
   - `"auto"` — try Ultralytics → TFLite → NCNN (current behaviour)
   - `"ncnn"` — force NCNN, fail if not available
   - `"tflite"` — force TFLite
   - `"ultralytics"` — force Ultralytics
4. **All scripts pass backend explicitly:**
   ```python
   vis = VisionSystem(camera_index=None, model_path=path, backend="ncnn")
   ```
5. **No more sys.argv hacking**

## Testing Checklist
- [ ] vision.py compiles
- [ ] 146 pytest tests pass
- [ ] main.py simulation works (default backend)
- [ ] main.py with `--backend ncnn` works
- [ ] diagnostics.py model switching works
- [ ] ncnn_video_player.py still works
- [ ] tflite_video_player.py still works
- [ ] video_test_compare.py still works
- [ ] Detection quality identical between backends

## Reference: How ncnn_video_player.py Does It (correctly)
```python
import ncnn
net = ncnn.Net()
net.opt.num_threads = 4
net.load_param("model.ncnn.param")
net.load_model("model.ncnn.bin")

mat_in = ncnn.Mat.from_pixels(img_rgb, ncnn.Mat.PixelType.PIXEL_RGB, 640, 640)
mat_in.substract_mean_normalize([0,0,0], [1/255, 1/255, 1/255])
ex = net.create_extractor()
ex.input("in0", mat_in)
ret, mat_out = ex.extract("out0")
```
