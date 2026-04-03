python field_tools/passive_watch.py --fake --no-mavlink --model cv_models/human.tflite --conf 0.4 --smart-estimate --smart-radius 2.0 --smart-min 7 --save-dir dima_images --class-filter "person,bird"

python field_tools/passive_watch.py --fake --no-mavlink --model cv_models/human.tflite --conf 0.4 --smart-estimate --smart-radius 2.0 --smart-min 7 --smart-dir alex_22 --class-filter "person,bird"


python main.py --speed 5 --lock-yaw --clean









========================================================

python field_tools/passive_watch.py --conf 0.5 --model cv_models/human.tflite --save-dir /home/flightlab-user/detections --class-filter person --simple-names




python field_tools/passive_watch.py --conf 0.3 --model cv_models/human.tflite --save-dir detections_laptop --simple-names --no-mavlink



================================================================================================

python field_tools/passive_watch.py --conf 0.5 --model cv_models/human.tflite --save-dir /home/flightlab-user/detections --class-filter person --simple-names --smart-estimate


http://192.168.1.121:8090/


================================================================================================
CALIBRATION STEPS (do on Pi before mission)
================================================================================================

STEP 1: Lens calibration (defisheye — needs checkerboard)
--------
python tests/calibration/lens_calibrate.py --board 13x8
- Hold checkerboard at 10+ different angles
- SPACE to capture each, Q when done
- Creates calibration_data.npz (used by UNDISTORT_ENABLED in config.py)
- Only needed once per camera (unless lens changes)

STEP 2: FOV / Focal length calibration (most important for GPS accuracy)
--------
Option A: On Pi with screen
  python tests/calibration/gps_calibrate_gui.py --model cv_models/human.tflite
  - Hold camera at known height pointing DOWN at target
  - Enter height (H key) + distance from below camera (D key)
  - SPACE to capture 10 frames
  - Repeat 3-4 times at different distances
  - Prints corrected FOCAL_LENGTH_MM → update config.py

Option B: From recorded Pi video (on laptop)
  python tests/laptop/video_test_compare.py <pi_video.mp4> --smart-estimate
  - Press B for calibration mode
  - Scroll to zoom, right-click HEAD then FEET of dummy
  - Auto-calculates focal length from altitude + pixel distance + known height (1.8m)
  - Auto-updates config.py

STEP 3: Verify config.py has correct values
--------
FOCAL_LENGTH_MM = ???   ← from calibration (currently 5.46, rough estimate)
SENSOR_WIDTH_MM = 5.02  ← hardware constant, don't change
IMAGE_W = 1456          ← Pi camera native, don't change
IMAGE_H = 1088          ← Pi camera native, don't change
UNDISTORT_ENABLED = True ← needs calibration_data.npz from step 1
CAMERA_FLIP_180 = True   ← camera mounted inverted on drone

STEP 4: Verify GPS estimation works
--------
python field_tools/passive_watch.py --conf 0.5 --model cv_models/human.tflite --class-filter person --simple-names --no-save
- Fly over known target, check stream at http://PI_IP:8090/
- DUMMY EST should show estimated GPS close to true position
- If >3m off → recalibrate FOCAL_LENGTH_MM

================================================================================================
MISSION COMMAND (after calibration)
================================================================================================

Terminal 1 (mavproxy):
sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762

Terminal 2 (smart detection):
python field_tools/passive_watch.py --conf 0.5 --model cv_models/human.tflite --save-dir /home/flightlab-user/detections --class-filter person --simple-names --smart-estimate

Stream: http://192.168.1.121:8090/

Output: SMART_51.42340_-2.67147_10samp.png
  - Image: most central frame from tightest cluster of 10
  - Coordinate: median of 10 estimates (all within 0.5m of each other)
  - Accuracy: ~0.2-0.5m from true position (with good calibration)

================================================================================================
HOW GPS ESTIMATION WORKS
================================================================================================

1. Camera captures 1456x1088 frame
2. Undistort (if enabled) → clean straight-line image
3. AI detects person → pixel position (px, py)
4. Read from Cube: drone GPS, altitude, yaw
5. Calculate:
   GSD = (5.02mm × altitude) / (FOCAL_LENGTH_MM × 1456)
   offset_right = (px - 728) × GSD meters
   offset_forward = -(py - 544) × GSD meters
6. Rotate by yaw → north/east offset
7. Add to drone GPS → estimated dummy GPS

Smart estimate: greedy tightest 10 detections → median = final position