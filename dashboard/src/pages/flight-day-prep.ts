import type { PrepTask, DiagnosticCheck } from "./flight-day-types";

// ═══════════════════════════════════════════════════════════
// Pre-Flight Day Preparation
// ═══════════════════════════════════════════════════════════

export const PRE_FLIGHT_PREP: PrepTask[] = [
  {
    id: "P1", task: "Push ALL code to MainOne5", owner: "Dima", critical: true, status: "done",
    command: "cd ~/Desktop/\"AI for Robotics\"/v3 && git add -A && git commit -m \"flight day prep\" && git push origin MainOne5",
    notes: "Ensures Pi has the latest code: BGR fix, pi_flight.py, tests/ scripts, config.py updates.\n\nSteps:\n1. Open terminal in v3/ project folder\n2. Run: git status — check nothing important is unstaged\n3. Run: git add -A && git commit -m \"flight day prep\"\n4. Run: git push origin MainOne5\n5. Verify on GitHub: https://github.com/DimaChup/Group_Proj/tree/MainOne5 — check latest commit timestamp\n\nExpected output: 'MainOne5 -> MainOne5' with no errors.\n\nIf push fails:\n- 'rejected — non-fast-forward': someone else pushed. Run: git pull origin MainOne5 --rebase, then push again\n- 'Permission denied': check GitHub SSH key or use HTTPS URL\n- 'remote not found': run git remote -v to verify remote URL",
  },
  {
    id: "P2", task: "Export COCO person detector as TFLite fallback", owner: "Dima", critical: true, status: "todo",
    command: "yolo export model=yolov8n.pt format=tflite imgsz=640",
    notes: "Our custom model was trained on synthetic composites (map.jpg + dummy.png). COCO person class 0 was trained on 330k+ real images including aerial views — it is our safety net if custom model fails outdoors.\n\nSteps:\n1. Activate venv: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux)\n2. Verify ultralytics is installed: python -c \"import ultralytics; print(ultralytics.__version__)\"\n   — if missing: pip install ultralytics\n3. Run: yolo export model=yolov8n.pt format=tflite imgsz=640\n   — this downloads yolov8n.pt (~6MB) if not present, then exports to TFLite\n   — takes 1-3 minutes, lots of output is normal\n4. Find the exported file: it will be at yolov8n_saved_model/yolov8n_float32.tflite\n5. Copy it: cp yolov8n_saved_model/yolov8n_float32.tflite models/coco_yolov8n.tflite\n6. Verify size: ls -lh models/coco_yolov8n.tflite — should be ~6-12MB\n7. Quick test: python -c \"import tflite_runtime.interpreter as tflite; i=tflite.Interpreter('models/coco_yolov8n.tflite'); i.allocate_tensors(); print('OK')\"\n\nExpected output: export log ending with 'Export complete' and a .tflite file path.\n\nIf export fails:\n- 'onnx not found': pip install onnx onnxslim onnxruntime\n- 'onnx2tf not found': try on WSL/Linux instead of Windows (onnx2tf has Windows issues)\n- Alternative: download a pre-exported yolov8n TFLite from Ultralytics GitHub releases\n\nIMPORTANT: COCO model detects 80 classes. Class 0 = 'person'. Our code in vision.py filters by class — verify it accepts class 0 for COCO model. The custom model has class 0 = 'dummy'.\n\nTo swap models on flight day: cp models/coco_yolov8n.tflite best.tflite",
  },
  {
    id: "P3", task: "Test 1_passive_flight.py in SIMULATION", owner: "Dima", critical: true, status: "todo",
    command: "set DRONE_MODE=SIMULATION && python tests/flight/1_passive_flight.py --stream --save-detections --save-frames",
    notes: "1_passive_flight.py is the ZERO-RISK flight script — it sends NO commands to the drone. Pilot flies manually, Pi just watches and logs. This must work perfectly before flight day.\n\nSteps:\n1. Start SITL first (Mission Planner → Simulation → Multirotor, or mavproxy with --home=51.423412,-2.671414,50,155)\n2. Wait for SITL to show 'Ready to fly' or heartbeat messages\n3. Open a NEW terminal, activate venv\n4. Windows: set DRONE_MODE=SIMULATION\n   Linux: export DRONE_MODE=SIMULATION\n5. Run: python tests/flight/1_passive_flight.py --stream --save-detections --save-frames\n6. Open browser: http://localhost:8090/stream — you should see the camera feed with detection overlay\n7. Point webcam at a printed dummy or phone showing dummy image\n8. Watch for green bounding boxes appearing on detected objects\n\nVerify ALL of these:\n- [ ] Stream loads at http://localhost:8090/stream (MJPEG video in browser)\n- [ ] Green detection boxes appear when dummy is in view\n- [ ] Terminal shows detection logs with confidence values\n- [ ] detections/ folder is created and fills with cropped detection images\n- [ ] flight_frames/ folder is created and fills with full frames\n- [ ] A CSV log file is created with columns: timestamp, GPS, altitude, confidence, pixel_x, pixel_y\n- [ ] Ctrl+C exits cleanly without errors\n\nExpected terminal output:\n  'Connected to vehicle'\n  'Camera opened: 640x480'\n  'Model loaded: True'\n  'Serving MJPEG at http://0.0.0.0:8090/stream'\n  'Detection: conf=0.87 x=312 y=245'\n\nIf stream doesn't load:\n- Check firewall isn't blocking port 8090\n- Try http://127.0.0.1:8090/stream instead of localhost\n- Check terminal for 'Address already in use' — kill other Python processes\n\nIf no detections:\n- Verify best.tflite exists in project root\n- Try: python tests/laptop/test_cv.py --camera to test detection separately\n- Check confidence threshold in vision.py (currently 0.4 — lower to 0.25 for testing)\n\nAdditional flags for Pi:\n  --headless        (no cv2.imshow — required for SSH)\n  --save-every 4    (save every 4th frame instead of every frame — saves disk space)",
  },
  {
    id: "P4", task: "Test pi_flight.py dashboard in SIMULATION", owner: "Dima", critical: false, status: "todo",
    command: "set DRONE_MODE=SIMULATION && python pi_flight.py --fps 4",
    notes: "pi_flight.py is the full web ground station with interactive controls. Tests the operator workflow: detect → investigate → classify → land.\n\nSteps:\n1. Start SITL (same as P3)\n2. Windows: set DRONE_MODE=SIMULATION && python pi_flight.py --fps 4\n   Linux: export DRONE_MODE=SIMULATION && python pi_flight.py --fps 4\n   (--fps 4 simulates Pi-speed inference, ~250ms per frame)\n3. Open browser: http://localhost:8090\n4. You should see: video feed (left), 2D GPS grid (right), command buttons (bottom), status bar (top)\n\nTest the full operator flow:\n- [ ] Dashboard loads with video + grid + buttons\n- [ ] Status bar shows: flight mode, GPS coords, altitude, battery voltage\n- [ ] Click 'FAKE DET' button — a fake detection cluster appears on the grid\n- [ ] Click the cluster on the grid to select it (turns highlighted)\n- [ ] Press N key (or click N button) — drone should fly toward the cluster (investigate)\n- [ ] Press Y key — classify as confirmed dummy\n- [ ] Press L key — drone should fly to 7.5m offset and land\n- [ ] Press M key — resume search (if you want to cancel and keep flying)\n- [ ] Video stream shows detection overlay (green boxes) when dummy is in webcam view\n\nKeyboard shortcuts (in browser):\n  N = investigate selected cluster\n  Y = confirm as dummy\n  I = mark as item of interest\n  X = mark as false positive\n  L = land (7.5m offset from target)\n  M = resume/manual override\n\nExpected output:\n  Terminal: 'Dashboard at http://0.0.0.0:8090'\n  Browser: full dashboard with live video + interactive grid\n\nIf dashboard doesn't load:\n- Check port 8090 isn't already in use (from P3 test)\n- Kill any leftover Python processes: taskkill /F /IM python.exe (Windows)\n- Check browser console (F12) for JavaScript errors\n\nIf video is static/frozen:\n- SITL needs explicit data stream request — check terminal for 'requesting data streams'\n- Restart SITL and try again\n\nIf grid is empty:\n- Check that SITL has a GPS fix (Mission Planner should show GPS coords)\n- The grid centers on drone's GPS — if GPS is 0,0 the grid won't render correctly",
  },
  {
    id: "P5", task: "Robin: test state machine in SIMULATION", owner: "Robin", critical: true, status: "todo",
    command: "set DRONE_MODE=SIMULATION && python main.py",
    notes: "main.py is the full autonomous mission: takeoff → search pattern → detect → centre → descend → verify → land. Robin should test this independently to understand the flow.\n\nSteps:\n1. Clone the repo (if not already): git clone https://github.com/DimaChup/Group_Proj.git && cd Group_Proj && git checkout MainOne5\n2. Set up venv (if not already): python -m venv venv && venv\\Scripts\\activate && pip install -r requirements_dev.txt\n3. Start SITL: open Mission Planner → Simulation → Multirotor (use home=51.423412,-2.671414,50,155 if possible)\n4. Wait until Mission Planner shows 'Got Params' and a GPS fix\n5. In a new terminal: set DRONE_MODE=SIMULATION && python main.py\n6. A map window opens — draw a polygon (click corners, right-click to finish) for the search area\n7. Watch the state transitions in the terminal:\n   INIT → CONNECTING → ARMING → TAKEOFF → SEARCH → ...\n8. Press M key anytime to toggle manual override\n9. Press ESC or Ctrl+C to abort (drone will RTL)\n\nExpected state flow:\n  INIT: loading config\n  CONNECTING: waiting for heartbeat (should connect within 5s)\n  ARMING: switching to GUIDED, arming motors (watch Mission Planner — motors go green)\n  TAKEOFF: climbing to TARGET_ALT (30m default)\n  SEARCH: flying lawnmower pattern\n  If dummy detected: CENTERING → DESCENDING → VERIFY → APPROACH → LANDING\n\nThings to note:\n- Does it connect to SITL within 5s? (If >30s, connection string may be wrong)\n- Does ARMING succeed? (SITL should arm easily — no safety checks needed)\n- Does the search pattern look correct in Mission Planner map?\n- Any mode mapping errors? (look for 'Mode(0x...)' instead of 'GUIDED' in terminal)\n- Does it detect the simulated dummy? (SIMULATION mode overlays dummy on simulated camera)\n\nIf CONNECTING hangs:\n- Check SITL is running (Mission Planner shows live data)\n- Check config.py CONNECTION_STRING — should auto-detect SITL at tcp:127.0.0.1:5760 or udp:127.0.0.1:14550\n- Try: python -c \"from pymavlink import mavutil; m=mavutil.mavlink_connection('tcp:127.0.0.1:5760'); print(m.wait_heartbeat())\"\n\nIf ARMING fails:\n- In Mission Planner, check Messages tab for pre-arm failure reasons\n- Common SITL issue: 'RC not calibrated' — go to MP → Initial Setup → Mandatory Hardware → Radio Calibration",
  },
  {
    id: "P6", task: "Test 0b_bench_mission.py on Pi (no flying)", owner: "Robin", critical: false, status: "todo",
    command: "cd ~/dima/Group_Proj && source pienv/bin/activate && python tests/flight/0b_bench_mission.py",
    notes: "Safe bench test — walks the Cube through a mission sequence WITHOUT arming motors. Tests that Pi can send commands and Cube responds correctly.\n\nPrerequisites:\n1. Pi powered on, connected to Cube via TELEM2 wiring\n2. Cube powered (battery or USB)\n3. Mavproxy running in Terminal 1:\n   sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762\n4. Wait for mavproxy to show heartbeat messages\n\nSteps:\n1. SSH into Pi: ssh pi@192.168.1.121 (or whatever the current IP is)\n2. In Terminal 2: cd ~/dima/Group_Proj && source pienv/bin/activate\n3. Run: python tests/flight/0b_bench_mission.py\n4. Watch the output — it tests each command and shows Cube's response\n\nExpected results (bench, no GPS, no RC):\n  Mode → GUIDED: SUCCESS (system 1, mode GUIDED)\n  Mode → LAND: SUCCESS\n  Mode → STABILIZE: FAIL — 'RC not found' (expected without RC transmitter)\n  Mode → LOITER: FAIL — 'no GPS' (expected indoors)\n  ARM: REJECTED — 'RC not found' or 'pre-arm checks' (expected and SAFE)\n  Waypoint: ACK result=4 FAILED (no GPS — expected)\n  Param read: ARMING_CHECK = some number (proves param reading works)\n\nAll 'failures' above are EXPECTED and prove commands ARE reaching the Cube.\nThe key thing is: system=1 (Cube, not mavproxy) and mode names resolve correctly.\n\nIf system shows 0 instead of 1:\n- Script is talking to mavproxy, not Cube\n- Check heartbeat filtering: should filter msg.type != MAV_TYPE_GCS (type 6)\n\nIf mode shows 'Mode(0x00000004)' instead of 'GUIDED':\n- Mode name mapping issue — check COPTER_MODES dict in the script",
  },
  {
    id: "P7", task: "RC kill switch configured + tested", owner: "Pilot", critical: true, status: "todo",
    command: "Open Mission Planner → Config → Flight Modes → assign STABILIZE to a switch position",
    notes: "The RC kill switch is the MOST IMPORTANT safety feature. If anything goes wrong, flipping this switch instantly puts the drone in STABILIZE (pilot has full manual control) or can trigger LAND.\n\nSteps:\n1. Connect RC transmitter to Mission Planner (via Cube USB or telemetry)\n2. Go to: Config → Flight Modes\n3. You will see 6 flight mode slots mapped to a 3-position switch (or 2-position + 3-position combo)\n4. Assign at least one switch position to STABILIZE — this is the 'oh crap' mode\n5. Recommended setup:\n   - Position 1 (default): LOITER (GPS hold — safe default)\n   - Position 2: AUTO or GUIDED (for autonomous flight)\n   - Position 3 (kill switch): STABILIZE (full manual — instant takeover)\n6. Test: flip the switch while watching Mission Planner. The 'Flight Mode' display should change instantly.\n7. Also configure RC loss failsafe:\n   - Config → Failsafe → RC Failsafe = RTL (Return To Launch)\n   - This means if RC signal is lost, drone comes home automatically\n\nVerification:\n- [ ] Flip to kill switch position → MP shows STABILIZE within <1 second\n- [ ] Flip back → MP shows LOITER or AUTO\n- [ ] RC failsafe set to RTL (Config → Failsafe)\n- [ ] All team members know which switch is the kill switch and which direction to flip\n\nIMPORTANT:\n- STABILIZE requires pilot skill — drone won't hold position or altitude. If pilot is not confident, use LAND instead of STABILIZE as kill mode.\n- Test this on the ground with props OFF before every flight\n- The pilot must have line-of-sight to the drone AT ALL TIMES\n- If in doubt, FLIP THE SWITCH. Better to land roughly than to lose the drone.\n\nIf modes don't change when flipping switch:\n- Check RC transmitter is bound to receiver (solid green LED on receiver)\n- Check channel mapping: the flight mode switch must be on the correct RC channel (usually CH5 or CH7)\n- In MP → Radio Calibration: verify the channel changes value when you flip the switch",
  },
  {
    id: "P8", task: "Charge ALL batteries", critical: true, status: "todo",
    items: ["3x LiPo flight batteries (4.2V/cell, balance charge)", "Pi USB power bank (full)", "RC transmitter", "Laptop", "Phone (hotspot)"],
    notes: "Do this the NIGHT BEFORE flight day. LiPo batteries take 1-2 hours to balance charge.\n\nSteps:\n1. LiPo flight batteries (most important):\n   - Use a LiPo balance charger (NOT a generic USB charger)\n   - Set to 'Balance Charge' mode, NOT 'Fast Charge'\n   - Set correct cell count (e.g. 4S = 4 cells) and capacity\n   - Each cell should read 4.20V when full (check charger display)\n   - NEVER leave charging LiPos unattended — fire risk\n   - Store in LiPo-safe bag during charging\n   - Charge ALL 3 batteries — we want at least 3 flights (one per tier)\n\n2. Pi USB power bank:\n   - Standard USB charger, charge to 100%\n   - Check it can deliver enough amps for Pi 5 (needs 5V/5A ideally, 5V/3A minimum)\n   - Test: plug Pi into power bank, does it boot without low-voltage warning?\n\n3. RC transmitter:\n   - Check battery level indicator on transmitter\n   - Charge if below 50% — we need several hours of field time\n\n4. Laptop:\n   - Charge to 100%, bring charger anyway\n   - Will be used for Mission Planner + SSH to Pi\n\n5. Phone:\n   - Charge to 100% — used as WiFi hotspot for Pi-to-laptop communication\n   - Test hotspot works: turn on, connect laptop, verify internet/local network\n\nDay-of check: verify all batteries before leaving. A dead battery = a wasted trip.",
  },
  {
    id: "P9", task: "Pack equipment", critical: true, status: "todo",
    items: [
      "Drone (props OFF for transport) + prop wrench",
      "RC transmitter + spare batteries",
      "Raspberry Pi 5 + camera (IMX296) + CSI ribbon cable + tape (secure ribbon!)",
      "Pi USB power bank + USB-C cable",
      "Laptop + charger",
      "Phone (WiFi hotspot)",
      "Printed dummy (A1/A0 — BIGGER IS BETTER for altitude detection)",
      "Cones (for cone detection test if available)",
      "Measuring tape (20m+)",
      "Notebook + pen (data recording sheets)",
      "All TFLite models: best.tflite + everything in models/ (custom variants, COCO, INT8, etc.)",
      "Printed FLIGHT_DAY_CHECKLIST.md",
      "Electrical tape (camera ribbon, loose wires)",
    ],
    notes: "Pack the evening before. Use a checklist — tick off each item as it goes in the bag.\n\nCritical items (cannot fly without):\n- Drone + battery + props + prop wrench\n- RC transmitter (charged) + bound receiver\n- Pi 5 + power bank + USB-C cable\n- IMX296 camera + CSI ribbon cable + electrical tape to secure ribbon\n- best.tflite model file on Pi\n\nImportant items (flight works but data limited without):\n- Laptop (for Mission Planner monitoring + SSH)\n- Phone hotspot (Pi-laptop WiFi link)\n- Measuring tape (for landing accuracy measurement)\n- Printed dummy (A1/A0 poster — bigger = detectable from higher altitude)\n\nNice to have:\n- Cones (high-contrast ground markers, easy for CV to spot)\n- Spare USB cables\n- Sunscreen, water (field days are long)\n- Folding table/chair\n\nCamera ribbon cable warning:\nThe CSI ribbon cable connecting the IMX296 to the Pi is FRAGILE. It can work loose during transport or with vibration. Secure it with electrical tape on BOTH ends (Pi connector and camera connector). Bring spare tape.\n\nModel files:\n- best.tflite = custom dummy detector (primary)\n- models/coco_yolov8n.tflite = COCO person detector (fallback)\n- models/custom_yolov8n.tflite = copy of best.tflite (backup)\nAll three should be on the Pi. To swap: cp models/coco_yolov8n.tflite best.tflite",
  },
  {
    id: "P10", task: "Pre-measure search area GPS coords", owner: "Dima", critical: false, status: "todo",
    command: "Open Google Maps → right-click → 'What's here?' → copy coords for each corner",
    notes: "Having GPS coordinates ready saves 10+ minutes on flight day. The search area is a polygon defined by GPS corners.\n\nSteps:\n1. Open Google Maps in browser (satellite view)\n2. Navigate to Fenswood Farm / your flight location\n3. Find a flat, open area (no trees, no buildings, no power lines)\n4. Right-click on each corner of your desired search area → 'What's here?' → copy the GPS coordinates\n5. You need 4 corners minimum (rectangle). More corners = more complex polygon.\n6. Write them down in order (clockwise or counter-clockwise):\n   Corner 1: 51.XXXXX, -2.XXXXX (NW)\n   Corner 2: 51.XXXXX, -2.XXXXX (NE)\n   Corner 3: 51.XXXXX, -2.XXXXX (SE)\n   Corner 4: 51.XXXXX, -2.XXXXX (SW)\n7. Update config.py SEARCH_AREA_GPS:\n   SEARCH_AREA_GPS = [\n     (51.XXXXX, -2.XXXXX),\n     (51.XXXXX, -2.XXXXX),\n     (51.XXXXX, -2.XXXXX),\n     (51.XXXXX, -2.XXXXX),\n   ]\n8. Keep the area small for first flight — 50m × 50m is plenty\n9. Verify in Google Maps: the area should be fully within the allowed flight zone\n\nAlternative (on flight day):\n- If you have map.jpg loaded, main.py lets you draw the polygon interactively\n- On Pi headless: the polygon is read from SEARCH_AREA_GPS in config.py — so pre-measuring is important\n\nTip: also note the GPS coordinates of where you'll place the dummy. After the flight, compare the drone's estimated GPS with the actual GPS to measure accuracy.",
  },
  {
    id: "P11", task: "Recreate pienv if needed", owner: "Dima", critical: true, status: "todo",
    command: "cd ~/dima/Group_Proj && python3 -m venv --system-site-packages pienv && source pienv/bin/activate && pip install -r requirements_pi.txt && pip install ai-edge-litert",
    notes: "The Pi virtual environment may need recreating if: code was re-uploaded, Python was updated, or packages are broken. --system-site-packages is REQUIRED for picamera2 access.\n\nFull steps:\n1. SSH into Pi: ssh pi@192.168.1.121\n2. Navigate: cd ~/dima/Group_Proj\n3. Pull latest code: git checkout MainOne5 && git pull origin MainOne5\n4. Remove old venv (if recreating): rm -rf pienv\n5. Create new venv:\n   python3 -m venv --system-site-packages pienv\n   (--system-site-packages is CRITICAL — picamera2 is installed system-wide and venv must access it)\n6. Activate: source pienv/bin/activate\n7. Install dependencies:\n   pip install -r requirements_pi.txt\n   pip install ai-edge-litert\n   (ai-edge-litert replaces tflite-runtime which doesn't support Python 3.13)\n8. If numpy build takes ages (5+ min from source), that's normal on Pi — let it finish\n\nVerification (run each, all must pass):\n  python tests/laptop/test_camera.py\n    → Expected: 'Camera opened: 640x480' + live preview (or frame saved if headless)\n    → Fail: check CSI ribbon cable seated properly, run: libcamera-still -o test.jpg\n\n  python tests/laptop/test_cv.py --camera\n    → Expected: 'Model loaded: True' + detection results printed\n    → Fail: check best.tflite exists in project root, try: ls -lh best.tflite\n\n  python tests/hardware/benchmark.py\n    → Expected: '50/50 detections, ~250ms avg, ~4 FPS, confidence ~0.96'\n    → Fail: if 0/50 detections, model may be corrupted — re-copy from models/custom_yolov8n.tflite\n\nCommon issues:\n- 'No module named picamera2': forgot --system-site-packages flag. Delete venv, recreate with flag.\n- 'No module named tflite_runtime': install ai-edge-litert (not tflite-runtime) for Python 3.13\n- 'numpy >= 2 required': our code needs numpy < 2. Check: pip install 'numpy<2'\n- Camera not found: check ribbon cable, run: libcamera-hello --list-cameras",
  },
  {
    id: "P11b", task: "FOV Calibration — measure camera focal length", owner: "Dima", critical: true, status: "todo",
    command: "python tests/calibration/fov_calibrate.py --headless",
    notes: "This is the SINGLE HIGHEST-IMPACT calibration you can do. Wrong FOV = wrong pixel-to-GPS conversion = landing accuracy off by 2-3x. You can do this on a bench at home before flight day — no drone or outdoor space needed.\n\nMaterials needed:\n- Ruler or tape measure (metric, mm markings)\n- Flat surface (table or floor)\n- Something to prop the Pi camera at a known height pointing straight down (e.g., stack of books, box, clamp)\n- Pi + camera assembly powered on, pienv activated\n\nExact procedure:\n1. Mount the Pi camera pointing STRAIGHT DOWN at a ruler/tape measure lying flat on the surface\n2. Prop the camera at a known height above the ruler. Start with 300mm (30cm) — measure from the camera lens to the ruler surface\n3. Look at the camera feed (use tests/diagnostics/camera_stream.py or the calibration script). Read the total visible width of the ruler in mm\n4. Apply the formula:\n   FOCAL_LENGTH_MM = (SENSOR_WIDTH_MM × height_mm) / visible_width_mm\n   where SENSOR_WIDTH_MM = 5.02 (IMX296 sensor spec)\n\nWorked example:\n- Height = 300mm, visible width = 250mm\n- FOCAL_LENGTH_MM = (5.02 × 300) / 250 = 6.024mm\n\nRepeat at 2-3 different heights (200mm, 300mm, 500mm) to cross-check. Results should agree within ±0.2mm.\n\nExpected result range: 4-8mm. If you get a number wildly outside this range, double-check:\n- Camera is pointing STRAIGHT down (not angled)\n- Height measurement is from lens to surface (not from Pi board)\n- Ruler is in focus and you're reading the TOTAL visible width (edge to edge of frame)\n\nAfter measuring: edit config.py, find the line FOCAL_LENGTH_MM = 6.0, and replace 6.0 with your measured value.\n\nWHY this matters so much: the pixel-to-GPS conversion divides by focal length. If real focal length is 5.0 but config says 6.0, every GPS estimate is off by 20%. At 15m altitude with a 3m offset, that's 0.6m error — and it gets worse with altitude. This is a systematic error that cannot be averaged out by more observations.\n\nScripts available:\n- python tests/calibration/fov_calibrate.py --headless (multi-height, comprehensive, guided prompts)\n- python tests/calibration/fov_test_simple.py (simpler, single measurement)\n\nCan absolutely do this on a bench at home before flight day!",
  },
  {
    id: "P12", task: "Prepare data recording sheets", critical: false, status: "todo",
    notes: "Having structured data sheets ready means we actually record useful data instead of random notes. Print these or prepare in a notebook BEFORE flight day.\n\nSheet 1 — Altitude Ladder Test:\n  Columns: Altitude (m) | Detected? (Y/N) | Confidence | Notes\n  Rows: 10m, 15m, 20m, 25m, 30m\n  Purpose: find the maximum reliable detection altitude\n  How: hover at each altitude for 30s over the dummy, record if AI detects it\n\nSheet 2 — Speed Test:\n  Columns: Speed (m/s) | Detected? (Y/N) | Confidence | Motion Blur (None/Mild/Bad) | Notes\n  Rows: 3 m/s, 5 m/s, 7 m/s, 10 m/s\n  Purpose: find maximum flight speed where detection still works\n  How: fly over dummy at each speed, record detection quality\n\nSheet 3 — Waypoint Accuracy Log:\n  Columns: Waypoint # | Target GPS | Actual GPS (from MP) | Error (m) | Notes\n  Purpose: measure how accurately the Cube follows GPS waypoints\n  How: command drone to waypoints, record where it actually goes\n\nSheet 4 — Landing Measurement:\n  Columns: Run # | Dummy GPS | Estimated GPS | Landing GPS | Distance to Dummy (m) | Offset Correct? | Notes\n  Purpose: measure landing accuracy\n  How: after each landing, measure distance from drone to dummy with tape measure\n\nSheet 5 — Model Comparison:\n  Columns: Model Name | Altitude | Detected? | Confidence | FPS | Notes\n  Rows: custom_yolov8n (best.tflite), coco_yolov8n, etc.\n  Purpose: which model works best in real conditions\n\nTip: take photos of all filled sheets at end of day as backup.",
  },
  {
    id: "P13", task: "Prepare logging templates", critical: false, status: "todo",
    notes: "This overlaps with P12 but focuses on DIGITAL logging templates — CSV files and scripts that auto-record data.\n\nAutomatic logging (already built in):\n- 1_passive_flight.py --save-detections → saves cropped detection images to detections/\n- 1_passive_flight.py --save-frames --save-every 4 → saves every 4th full frame to flight_frames/\n- 1_passive_flight.py creates a CSV with: timestamp, GPS, altitude, confidence, pixel_x, pixel_y\n- pi_flight.py logs all operator commands and detection clusters\n\nManual logging template (for notebook):\nFor each flight:\n  Flight #: ___  Time: ___  Battery: ___  Weather: ___\n  Script: ___  Mode: ___  Model: ___\n  Altitude: ___m  Speed: ___m/s\n  Detections: ___  False positives: ___\n  Landing distance to dummy: ___m\n  Notes: ___________________________________\n\nPost-flight checklist:\n- [ ] Copy Pi logs to laptop: scp pi@192.168.1.121:~/dima/Group_Proj/detections/* ./flight_data/\n- [ ] Copy flight frames: scp pi@192.168.1.121:~/dima/Group_Proj/flight_frames/* ./flight_data/\n- [ ] Copy CSV logs: scp pi@192.168.1.121:~/dima/Group_Proj/*.csv ./flight_data/\n- [ ] Note config.py values used (altitude, speed, confidence threshold)\n- [ ] Photograph data recording sheets\n\nAll this data feeds into the university report — record everything, even failures.",
  },
  {
    id: "P15", task: "Prepare multiple vision models for flight day testing", owner: "Dima", critical: true, status: "todo",
    command: "yolo export model=yolov8n.pt format=tflite imgsz=640  # repeat for each variant",
    notes: "Train and export several TFLite model variants so we can swap them on Pi during flight day. Each model tests a different hypothesis about what works best in real outdoor conditions.\n\nModels to prepare:\n1. **best.tflite** (custom dummy detector) — already exists. Trained on synthetic composites (map.jpg + dummy.png). Our primary model.\n2. **models/coco_yolov8n.tflite** (COCO person detector) — export from yolov8n.pt. Detects 80 classes including 'person' (class 0). Safety net if custom model fails outdoors.\n3. **Custom retrained variants** — train on different data:\n   a. More diverse dummy images (different angles, lighting, backgrounds)\n   b. Real photos of the dummy (take photos with phone, add to training set)\n   c. Mixed dataset (synthetic composites + real photos)\n   d. Different augmentation (more blur, brightness variation for outdoor conditions)\n4. **INT8 quantized** — smaller, faster, slightly less accurate:\n   yolo export model=best.pt format=tflite int8=True imgsz=640\n5. **YOLOv8s** (larger model) — more accurate but slower (~500ms on Pi):\n   yolo export model=yolov8s.pt format=tflite imgsz=640\n\nSteps to prepare each model:\n1. Train (if custom): yolo train model=yolov8n.pt data=dataset.yaml epochs=50 imgsz=640\n2. Export: yolo export model=runs/detect/train/weights/best.pt format=tflite imgsz=640\n3. Copy to models/: cp runs/detect/train/weights/best_saved_model/best_float32.tflite models/<descriptive_name>.tflite\n4. Test locally: python test_tflite_laptop.py --model models/<name>.tflite\n5. Note the model name, training data, and expected behaviour in a models/README.md\n\nOn flight day — swapping models:\n  ssh pi@PI_IP\n  cd ~/dima/Group_Proj\n  cp models/<model_to_test>.tflite best.tflite\n  # restart the running script (Ctrl+C, re-run)\n\nTest each model at the same altitude/conditions for fair comparison. Record in Sheet 5 (Model Comparison): model name, altitude, detected?, confidence, FPS, notes.\n\nTraining tips:\n- Use generate_dataset.py to create synthetic training data (already in project)\n- Take real photos of the dummy from 2-5m height with phone for realistic training data\n- More diverse training data = better outdoor generalization\n- Don't over-train (50-100 epochs is usually enough for YOLOv8n)\n- Always keep best.tflite as backup before overwriting",
  },
  {
    id: "P14", task: "Verify 1_passive_flight.py saves all data", owner: "Dima", critical: true, status: "todo",
    command: "set DRONE_MODE=SIMULATION && python tests/flight/1_passive_flight.py --stream --save-detections --save-frames --save-every 4",
    notes: "This is our PRIMARY data collection tool for flight day. If it doesn't save data correctly, we lose all evidence for the report.\n\nSteps:\n1. Start SITL (Mission Planner or mavproxy)\n2. Windows: set DRONE_MODE=SIMULATION\n   Linux: export DRONE_MODE=SIMULATION\n3. Run: python tests/flight/1_passive_flight.py --stream --save-detections --save-frames --save-every 4\n4. Point webcam at dummy image for 30 seconds\n5. Press Ctrl+C to stop\n6. Check all outputs:\n\nVerification checklist:\n- [ ] detections/ folder exists and contains cropped detection images (.jpg files)\n      → ls detections/ → should show files like det_001.jpg, det_002.jpg, ...\n      → Open a few — they should show the detected object cropped from the frame\n- [ ] flight_frames/ folder exists and contains full frames\n      → ls flight_frames/ → should show files like frame_0004.jpg, frame_0008.jpg, ... (every 4th)\n      → Open a few — they should show the full camera view\n- [ ] CSV log file created (detection_log.csv or similar)\n      → Open in text editor or Excel\n      → Verify columns: timestamp, lat, lon, alt, confidence, pixel_x, pixel_y\n      → Verify rows are populated (not empty or all zeros)\n- [ ] Stream works: http://localhost:8090/stream shows live video with detection overlay\n- [ ] Terminal output shows detection events in real-time\n\nExpected file counts after 30s of detections:\n  detections/: ~15-30 files (one per detection at ~4 FPS)\n  flight_frames/: ~7-15 files (every 4th frame)\n  CSV: ~15-30 rows\n\nIf detections/ is empty:\n- No detections occurred — check webcam is pointed at dummy, check confidence threshold\n- Verify --save-detections flag was included\n\nIf flight_frames/ is empty:\n- Verify --save-frames flag was included\n- Check disk space: df -h\n\nIf CSV is missing or empty:\n- Check terminal for file write errors\n- Check folder permissions: touch test_write.txt && rm test_write.txt\n\nIMPORTANT: On flight day, start this script BEFORE takeoff and stop AFTER landing. Every frame and detection is valuable data for the report.",
  },
];

// ═══════════════════════════════════════════════════════════
// Preflight Diagnostics Troubleshooting Tree
// ═══════════════════════════════════════════════════════════

export const PREFLIGHT_DIAGNOSTICS: DiagnosticCheck[] = [
  {
    id: "D1", system: "Mavproxy Bridge", severity: "blocking",
    command: "sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762",
    expect: "Terminal shows 'Telemetry log', heartbeat messages appear within 5s",
    failSteps: [
      "Check TELEM2 wiring: Cube TX → Pi RX (GPIO 15), Cube RX → Pi TX (GPIO 14), GND → GND",
      "Try swapping TX and RX wires (common mistake)",
      "Verify Cube is powered (battery or USB)",
      "Try: cat /dev/ttyAMA0 — should show binary data (proves serial works)",
      "Check baud rate: must be 921600 (Cube SERIAL2_BAUD param in MP)",
      "Try sudo chmod 666 /dev/ttyAMA0 if permission denied",
    ],
  },
  {
    id: "D2", system: "Cube Heartbeat", severity: "blocking",
    command: "python tests/diagnostics/diagnostics.py --headless  (check Cube line)",
    expect: "Cube: OK (system 1, ArduCopter)",
    failSteps: [
      "Is mavproxy running? Check Terminal 1 for heartbeat messages",
      "Restart mavproxy and wait 10s",
      "Run: python tests/diagnostics/cube_monitor.py — shows all MAVLink message types + rates",
      "If system=0: you're reading mavproxy's heartbeat, not Cube. Filter type!=6 (GCS)",
      "If no messages at all: wiring issue — go back to D1",
    ],
  },
  {
    id: "D3", system: "Camera", severity: "blocking",
    command: "python tests/laptop/test_camera.py",
    expect: "Frame captured: (480, 640, 3) — shows live preview if monitor connected",
    failSteps: [
      "Reseat CSI ribbon cable — lift black clip, push ribbon in, press clip down",
      "Check correct CSI port (CAM0 on Pi 5, not CAM1)",
      "Try: libcamera-still -o test.jpg — tests camera at OS level",
      "If blue tint: camera outputs BGR, do NOT add cvtColor (this is correct)",
      "Secure ribbon with electrical tape — vibration can loosen it",
      "If 'no cameras detected': sudo raspi-config → Interface Options → Camera → Enable → reboot",
    ],
  },
  {
    id: "D4", system: "AI Model", severity: "blocking",
    command: "python tests/hardware/benchmark.py",
    expect: "50 runs, avg ~250ms, detection rate >0%, model loads without error",
    failSteps: [
      "Verify best.tflite exists in project root: ls -la best.tflite",
      "If missing: cp models/custom_yolov8n.tflite best.tflite",
      "If import error: pip install ai-edge-litert (replaces tflite-runtime on Python 3.13)",
      "If numpy error: pip install 'numpy<2' (numpy 2.x breaks tflite)",
      "If 0% detection: model may be wrong format — check with python tests/laptop/debug_tflite.py",
      "Fallback: cp models/coco_yolov8n.tflite best.tflite (COCO person detector)",
    ],
  },
  {
    id: "D5", system: "GPS Lock", severity: "blocking",
    command: "python tests/hardware/gps_test.py",
    expect: "fix_type=3 (3D fix), satellites≥8, Here 3+ LED = flashing GREEN",
    failSteps: [
      "LED flashing BLUE = searching (normal, wait 1-5 min outdoors)",
      "LED double YELLOW = pre-arm check failing (not GPS related)",
      "No LED at all = no power. Check CAN2 cable to Cube",
      "Run: python tests/hardware/gps_health.py — step-by-step CAN bus + GPS diagnosis",
      "Check GPS1_TYPE param in MP (should be 9 for DroneCAN / Here 3+)",
      "Check CAN_P2_DRIVER=1 and CAN_D2_PROTOCOL=1 in MP",
      "Move to open sky — buildings/trees block satellites",
      "Cold start can take up to 15 min. Be patient.",
    ],
  },
  {
    id: "D6", system: "RC Controller", severity: "blocking",
    command: "Mission Planner → Config → Radio Calibration",
    expect: "All 4 sticks show movement. Channel 5/6 shows mode switch positions.",
    failSteps: [
      "RC transmitter powered on?",
      "Receiver bound? Check binding procedure in RC manual",
      "Check receiver LED — solid = bound, flashing = searching",
      "Receiver wired to Cube RCIN port? (not SBUS, not GPS)",
      "Run radio calibration in MP if sticks show no movement",
      "Check battery in RC transmitter — low battery = weak signal",
    ],
  },
  {
    id: "D7", system: "Kill Switch", severity: "blocking",
    command: "Flip designated RC switch while watching MP flight mode display",
    expect: "Mode changes to STABILIZE on flip, back to previous on un-flip",
    failSteps: [
      "Configure in MP → Config → Flight Modes → assign STABILIZE to one switch position",
      "Note which channel (e.g., CH5 or CH6) and which position (low/mid/high)",
      "If mode doesn't change: wrong channel mapped, or switch not sending correct PWM",
      "Test with MP Radio Cal view: flip switch, see which channel value changes",
    ],
  },
  {
    id: "D8", system: "Mission Planner", severity: "warning",
    command: "MP → TCP → Pi IP → port 5762",
    expect: "HUD shows attitude. Map shows drone. Telemetry data flowing.",
    failSteps: [
      "Check Pi IP: hostname -I on Pi terminal",
      "Check mavproxy has tcpin:0.0.0.0:5762 output (look at startup flags)",
      "Try: sudo ufw allow 5762 on Pi (firewall)",
      "Check laptop is on same WiFi network as Pi",
      "If 'connection refused': mavproxy not running or tcpin not configured",
    ],
  },
  {
    id: "D9", system: "Battery", severity: "warning",
    command: "Check MP HUD or: python tests/diagnostics/cube_monitor.py",
    expect: "Battery voltage ≥ 14.0V (4S LiPo). Shows > 0V (0V = USB power only).",
    failSteps: [
      "0.0V = Cube on USB power, not battery. Connect flight battery.",
      "< 14.0V = battery not fully charged. Swap for fresh one.",
      "< 12.0V = critically low. DO NOT fly. Charge immediately.",
      "Check LiPo cell balance with charger if voltage seems wrong",
    ],
  },
  {
    id: "D10", system: "Live Video Stream", severity: "warning",
    command: "python tests/diagnostics/camera_stream.py --with-detection",
    expect: "Stream at http://PI_IP:8090 shows live camera with detection boxes",
    failSteps: [
      "Camera not working → fix D3 first",
      "Stream loads but no video → check port 8090 not blocked. Try different browser.",
      "No detection overlay → model not loaded. Fix D4 first.",
      "Very slow (<1 FPS) → Pi thermal throttling. Check: vcgencmd measure_temp (>80°C = throttled)",
      "Laptop can't reach → check WiFi. Try: ping PI_IP from laptop.",
    ],
  },
  {
    id: "D11", system: "Pre-Arm Checks", severity: "info",
    command: "Mission Planner → Messages tab → try to arm",
    expect: "Either arms successfully, or Messages shows specific reason for refusal",
    failSteps: [
      "'GPS not locked' → wait for fix_type=3 (D5)",
      "'RC not found' → fix RC binding (D6)",
      "'Compass variance' → run compass calibration in MP (rotate drone in all axes)",
      "'Accel calibration' → run accelerometer calibration in MP (level drone on flat surface)",
      "'Check firmware' → update ArduCopter in MP if very old version",
      "Last resort: reduce ARMING_CHECK param in MP (removes specific checks, use with caution)",
    ],
  },
  {
    id: "D12", system: "Battery Failsafe", severity: "blocking",
    command: "Mission Planner → Config → Full Parameter List → search 'FS_BATT'",
    expect: "FS_BATT_ENABLE=1, FS_BATT_VOLTAGE=14.0 (for 4S LiPo). Action = RTL.",
    failSteps: [
      "Check FS_BATT_ENABLE is 1 (not 0)",
      "Set FS_BATT_VOLTAGE to 14.0 (3.5V per cell × 4)",
      "Set FS_BATT_ACTION to 2 (RTL) — not 0 (disabled)",
      "If no battery data: Cube on USB power, not LiPo. Connect flight battery.",
      "Write params after changing",
    ],
  },
  {
    id: "D13", system: "Geofence Boundary", severity: "warning",
    command: "Mission Planner → Config → GeoFence",
    expect: "FENCE_ENABLE=1, FENCE_TYPE=7 (alt+circle+polygon), FENCE_ALT_MAX=50, FENCE_RADIUS=100, FENCE_ACTION=1 (RTL)",
    failSteps: [
      "Set FENCE_ENABLE=1",
      "Set FENCE_TYPE=7 (altitude + circular + polygon)",
      "Set FENCE_ALT_MAX=50 (metres — well under 120m CAA limit)",
      "Set FENCE_RADIUS=100 (metres from home point)",
      "Set FENCE_ACTION=1 (RTL on breach)",
      "Draw polygon on map if needed: Flight Plan → GeoFence → draw boundary",
      "Write params, verify fence shown on MP map",
    ],
  },
  {
    id: "D14", system: "Compass Calibration", severity: "warning",
    command: "Mission Planner → Initial Setup → Mandatory Hardware → Compass → Start",
    expect: "All 3 axes show green. Offsets reasonable (<200). No 'compass variance' pre-arm.",
    failSteps: [
      "Hold drone and rotate slowly through all orientations (takes 1-2 min)",
      "Keep away from metal objects, cars, power lines during cal",
      "If offsets very large (>400): external compass may be too close to electronics",
      "If cal fails repeatedly: try in a different location (magnetic interference)",
      "As last resort: relax COMPASS_OFS_MAX or disable compass check in ARMING_CHECK",
    ],
  },
];
