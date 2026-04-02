"""CV Pipeline Visualization — self-contained HTML/CSS/JS diagram.

Embeddable in any browser dashboard. Shows the full image processing
pipeline from camera sensor to GPS estimation with live geometry.

Usage:
    from field_tools.cv_pipeline_visual import get_cv_pipeline_html
    # Inject into an HTTP response or embed in a larger page.
    # Call updatePipelineData({alt: 30, yaw: 155, lat: 51.42, lon: -2.67, fps: 4.8})
    # from JavaScript to update dynamic values.
"""


def get_cv_pipeline_html():
    """Return HTML string for CV pipeline visualization."""
    return '''
<div id="cv-pipeline-root">
<style>
/* ── CV Pipeline Scoped Styles ─────────────────────────────── */
#cv-pipeline-root {
  background: #111;
  color: #ccc;
  font-family: 'Courier New', monospace;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #333;
  overflow-x: auto;
}
#cv-pipeline-root * { box-sizing: border-box; }

/* Title */
.cvp-title {
  text-align: center;
  font-size: 14px;
  font-weight: bold;
  color: #0f0;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 14px;
  border-bottom: 1px solid #333;
  padding-bottom: 8px;
}

/* Pipeline row */
.cvp-row {
  display: flex;
  align-items: stretch;
  gap: 0;
  min-width: 1050px;
}

/* Arrow between stages */
.cvp-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  min-width: 28px;
  color: #555;
  font-size: 18px;
  user-select: none;
}
.cvp-arrow::after {
  content: '';
  display: block;
  width: 20px;
  height: 2px;
  background: linear-gradient(90deg, #333, #0a0);
  position: relative;
}
.cvp-arrow span {
  display: none;
}

/* Stage card */
.cvp-stage {
  flex: 1;
  min-width: 140px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 5px;
  padding: 10px 11px 9px;
  position: relative;
  transition: border-color 0.3s;
}
.cvp-stage:hover {
  border-color: #0a0;
}

/* Stage number badge */
.cvp-badge {
  position: absolute;
  top: -8px;
  left: 10px;
  background: #0a0;
  color: #000;
  font-size: 9px;
  font-weight: bold;
  padding: 1px 6px;
  border-radius: 8px;
  letter-spacing: 0.5px;
}

/* Stage icon + title row */
.cvp-head {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 7px;
  margin-top: 4px;
}
.cvp-icon {
  font-size: 18px;
  line-height: 1;
  filter: grayscale(0.3);
}
.cvp-name {
  font-size: 11px;
  font-weight: bold;
  color: #eee;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Key-value lines */
.cvp-kv {
  font-size: 10px;
  line-height: 1.55;
  color: #999;
}
.cvp-kv .k { color: #777; }
.cvp-kv .v { color: #bbb; }
.cvp-kv .hi { color: #0f0; }  /* highlighted dynamic value */
.cvp-kv .warn { color: #fa0; }
.cvp-kv .dim { color: #555; }
.cvp-kv .sep {
  border-top: 1px solid #2a2a2a;
  margin: 4px 0 3px;
}

/* ── FOV Geometry Canvas ───────────────────────────────────── */
.cvp-geom-wrap {
  margin-top: 12px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
}
.cvp-geom-canvas-wrap {
  position: relative;
  flex-shrink: 0;
}
#cvp-fov-canvas {
  background: #0a0a0a;
  border: 1px solid #333;
  border-radius: 4px;
  display: block;
}
.cvp-geom-info {
  font-size: 10px;
  line-height: 1.6;
  color: #999;
  min-width: 180px;
}
.cvp-geom-info .hi { color: #0f0; }
.cvp-geom-info .label { color: #666; font-size: 9px; }

/* ── Bottom summary bar ────────────────────────────────────── */
.cvp-summary {
  margin-top: 12px;
  padding: 8px 12px;
  background: #0d0d0d;
  border: 1px solid #282828;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 6px 20px;
  font-size: 10px;
}
.cvp-summary .item {
  color: #777;
}
.cvp-summary .item .val {
  color: #0f0;
  font-weight: bold;
}
</style>

<div class="cvp-title">CV Detection Pipeline</div>

<!-- ── Pipeline Stages ──────────────────────────────────── -->
<div class="cvp-row">

  <!-- Stage 1: Camera -->
  <div class="cvp-stage">
    <div class="cvp-badge">1</div>
    <div class="cvp-head">
      <span class="cvp-icon">&#x1F4F7;</span>
      <span class="cvp-name">Camera</span>
    </div>
    <div class="cvp-kv">
      <span class="k">Sensor</span> <span class="v">IMX296 global shutter</span><br>
      <span class="k">Size</span> <span class="v">5.02 mm &times; 3.76 mm</span><br>
      <span class="k">Focal</span> <span class="v">f = 5.46 mm</span><br>
      <span class="k">Output</span> <span class="v">1456&times;1088 px</span><br>
      <span class="k">Ratio</span> <span class="v">4:3, BGR order</span><br>
      <div class="sep"></div>
      <span class="dim">Inverted mount (180&deg; flip)</span><br>
      <span class="dim">No color conversion needed</span>
    </div>
  </div>

  <div class="cvp-arrow"><span>&rarr;</span></div>

  <!-- Stage 2: Preprocess -->
  <div class="cvp-stage">
    <div class="cvp-badge">2</div>
    <div class="cvp-head">
      <span class="cvp-icon">&#x2699;</span>
      <span class="cvp-name">Preprocess</span>
    </div>
    <div class="cvp-kv">
      <span class="k">Color</span> <span class="v">BGR pass-through</span><br>
      <span class="k">Undistort</span> <span class="v">cv2.remap (optional)</span><br>
      <span class="k">Cost</span> <span class="v">+1.5 ms</span><br>
      <span class="k">Resize</span> <span class="v">None (full res to AI)</span><br>
      <div class="sep"></div>
      <span class="dim">IMX296 distortion is minimal</span><br>
      <span class="dim">Undistort via calibration_data.npz</span>
    </div>
  </div>

  <div class="cvp-arrow"><span>&rarr;</span></div>

  <!-- Stage 3: Model Input -->
  <div class="cvp-stage">
    <div class="cvp-badge">3</div>
    <div class="cvp-head">
      <span class="cvp-icon">&#x1F5BC;</span>
      <span class="cvp-name">Model Input</span>
    </div>
    <div class="cvp-kv">
      <span class="k">Model</span> <span class="v">YOLOv8n TFLite</span><br>
      <span class="k">Tensor</span> <span class="v">[1, 640, 640, 3] f32</span><br>
      <div class="sep"></div>
      <span class="k">Letterbox</span><br>
      <span class="v">1456&times;1088</span>
      <span class="dim">&rarr; pad to 1456&times;1456</span><br>
      <span class="dim">&rarr; resize to 640&times;640</span><br>
      <div class="sep"></div>
      <span class="dim">Top/bottom black bars from pad</span><br>
      <span class="dim">Scale: 0.44 px/px</span>
    </div>
  </div>

  <div class="cvp-arrow"><span>&rarr;</span></div>

  <!-- Stage 4: Inference -->
  <div class="cvp-stage">
    <div class="cvp-badge">4</div>
    <div class="cvp-head">
      <span class="cvp-icon">&#x1F9E0;</span>
      <span class="cvp-name">Inference</span>
    </div>
    <div class="cvp-kv">
      <span class="k">Pi TFLite</span> <span class="hi" id="cvp-inf-ms">206 ms</span> <span class="dim">(<span id="cvp-inf-fps">4.8</span> FPS)</span><br>
      <span class="k">Pi NCNN</span> <span class="v">~100 ms (10 FPS)</span><br>
      <span class="k">Laptop</span> <span class="v">~30 ms</span><br>
      <div class="sep"></div>
      <span class="k">Output</span> <span class="v">[1, 5, 8400]</span><br>
      <span class="dim">8400 candidates &times; 5:</span><br>
      <span class="dim">(cx, cy, w, h, conf)</span><br>
      <span class="k">NMS</span> <span class="v">&rarr; best detection</span>
    </div>
  </div>

  <div class="cvp-arrow"><span>&rarr;</span></div>

  <!-- Stage 5: Detection -->
  <div class="cvp-stage">
    <div class="cvp-badge">5</div>
    <div class="cvp-head">
      <span class="cvp-icon">&#x1F3AF;</span>
      <span class="cvp-name">Detection</span>
    </div>
    <div class="cvp-kv">
      <span class="k">Output</span> <span class="v">(found, cx, cy, conf)</span><br>
      <span class="k">Coords</span> <span class="v">pixel, 1456&times;1088</span><br>
      <span class="k">Threshold</span> <span class="v">conf &ge; 0.4</span><br>
      <span class="k">Class</span> <span class="v">"dummy" (1-class)</span><br>
      <div class="sep"></div>
      <span class="k">Last conf</span> <span class="hi" id="cvp-det-conf">--</span><br>
      <span class="k">Position</span> <span class="hi" id="cvp-det-pos">--</span>
    </div>
  </div>

  <div class="cvp-arrow"><span>&rarr;</span></div>

  <!-- Stage 6: GPS -->
  <div class="cvp-stage" style="min-width:190px; flex:1.4;">
    <div class="cvp-badge">6</div>
    <div class="cvp-head">
      <span class="cvp-icon">&#x1F4CD;</span>
      <span class="cvp-name">GPS Estimation</span>
    </div>
    <div class="cvp-kv">
      <span class="k">f<sub>px</sub></span> <span class="v">= 5.46 &times; 1456 / 5.02 = <span class="hi">1584 px</span></span><br>
      <div class="sep"></div>
      <span class="dim">1. dx = cx &minus; 728, dy = cy &minus; 544</span><br>
      <span class="dim">2. m = px &times; alt / f<sub>px</sub></span><br>
      <span class="dim">3. Rotate by yaw</span><br>
      <span class="dim">4. &Delta;lat = N / 111320</span><br>
      <span class="dim">&nbsp;&nbsp; &Delta;lon = E / (111320 cos &phi;)</span><br>
      <div class="sep"></div>
      <span class="k">Weight</span> <span class="v">1/alt&sup2; &times; centrality</span><br>
      <span class="k">Alt</span> <span class="hi" id="cvp-gps-alt">-- m</span>
    </div>
  </div>

</div><!-- /cvp-row -->

<!-- ── FOV Geometry + Summary ───────────────────────────── -->
<div class="cvp-geom-wrap">
  <div class="cvp-geom-canvas-wrap">
    <canvas id="cvp-fov-canvas" width="320" height="180"></canvas>
  </div>
  <div class="cvp-geom-info">
    <span class="label">GROUND COVERAGE AT ALTITUDE</span><br><br>
    <span class="k">Altitude</span> <span class="hi" id="cvp-gc-alt">30 m</span><br>
    <span class="k">Width</span> <span class="hi" id="cvp-gc-w">27.6 m</span><br>
    <span class="k">Height</span> <span class="hi" id="cvp-gc-h">20.6 m</span><br>
    <span class="k">HFOV</span> <span class="v" id="cvp-gc-hfov">49.4&deg;</span><br>
    <span class="k">GSD</span> <span class="hi" id="cvp-gc-gsd">19.0 mm/px</span><br>
    <br>
    <span class="label">DETECTION RANGE</span><br><br>
    <span class="k">Dummy ~1.8m tall</span><br>
    <span class="k">At 30m</span> <span class="v">~52 px tall</span><br>
    <span class="k">At 50m</span> <span class="v">~31 px tall</span><br>
    <span class="k">At 10m</span> <span class="v">~156 px tall</span><br>
    <br>
    <span class="label">GPS ACCURACY</span><br><br>
    <span class="k">CEP50</span> <span class="v">~2.3 m</span><br>
    <span class="k">GPS lag</span> <span class="warn">100-200 ms</span><br>
    <span class="k">At 5 m/s</span> <span class="warn">~1 m error</span>
  </div>
</div>

<!-- ── Summary Bar ──────────────────────────────────────── -->
<div class="cvp-summary">
  <div class="item">Latency: <span class="val" id="cvp-sum-lat">~210 ms</span></div>
  <div class="item">FPS: <span class="val" id="cvp-sum-fps">4.8</span></div>
  <div class="item">Model: <span class="val">YOLOv8n</span></div>
  <div class="item">Input: <span class="val">640&times;640</span></div>
  <div class="item">Sensor: <span class="val">1456&times;1088</span></div>
  <div class="item">f<sub>px</sub>: <span class="val">1584</span></div>
</div>

<!-- ── JavaScript ───────────────────────────────────────── -->
<script>
(function() {
  // Constants
  const SENSOR_W = 5.02, FOCAL_MM = 5.46, IMG_W = 1456, IMG_H = 1088;
  const F_PX = FOCAL_MM * IMG_W / SENSOR_W; // 1584
  const SENSOR_H = SENSOR_W * IMG_H / IMG_W; // ~3.76

  // State
  let pipeState = { alt: 30, yaw: 0, lat: 51.423, lon: -2.671, fps: 4.8,
                    det_conf: null, det_cx: null, det_cy: null };

  // ── FOV canvas drawing ──────────────────────────────────
  function drawFOV() {
    const canvas = document.getElementById('cvp-fov-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const alt = pipeState.alt || 30;

    ctx.clearRect(0, 0, W, H);

    // Background gradient (sky to ground)
    const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
    bgGrad.addColorStop(0, '#0a0a14');
    bgGrad.addColorStop(0.35, '#0a0a14');
    bgGrad.addColorStop(0.4, '#0d1a0d');
    bgGrad.addColorStop(1, '#0d1a0d');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);

    // Ground line
    const groundY = H * 0.78;
    ctx.strokeStyle = '#2a4a2a';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 3]);
    ctx.beginPath();
    ctx.moveTo(0, groundY);
    ctx.lineTo(W, groundY);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#2a4a2a';
    ctx.font = '9px monospace';
    ctx.fillText('GROUND', 6, groundY - 4);

    // Drone position
    const droneX = W / 2;
    const droneY = groundY - Math.min(alt * 2.2, H * 0.6);

    // Ground coverage
    const gndW = alt * SENSOR_W / FOCAL_MM;
    const gndH = alt * SENSOR_H / FOCAL_MM;

    // Scale: fit ground width into canvas
    const maxGndPx = W * 0.85;
    const scale = maxGndPx / Math.max(gndW, 5);
    const gndWpx = gndW * scale;
    const gndHpx = gndH * scale; // not used directly, shown as text

    // FOV cone
    const leftX = droneX - gndWpx / 2;
    const rightX = droneX + gndWpx / 2;

    // Cone fill
    ctx.beginPath();
    ctx.moveTo(droneX, droneY);
    ctx.lineTo(leftX, groundY);
    ctx.lineTo(rightX, groundY);
    ctx.closePath();
    const coneGrad = ctx.createLinearGradient(droneX, droneY, droneX, groundY);
    coneGrad.addColorStop(0, 'rgba(0,255,0,0.08)');
    coneGrad.addColorStop(1, 'rgba(0,255,0,0.03)');
    ctx.fillStyle = coneGrad;
    ctx.fill();

    // Cone edges
    ctx.beginPath();
    ctx.moveTo(droneX, droneY);
    ctx.lineTo(leftX, groundY);
    ctx.moveTo(droneX, droneY);
    ctx.lineTo(rightX, groundY);
    ctx.strokeStyle = 'rgba(0,200,0,0.5)';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Ground coverage bracket
    ctx.strokeStyle = '#0f0';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(leftX, groundY + 2);
    ctx.lineTo(leftX, groundY + 10);
    ctx.lineTo(rightX, groundY + 10);
    ctx.lineTo(rightX, groundY + 2);
    ctx.stroke();

    // Ground width label
    ctx.fillStyle = '#0f0';
    ctx.font = 'bold 10px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(gndW.toFixed(1) + ' m', droneX, groundY + 22);

    // Ground height label (smaller, to the side)
    ctx.fillStyle = '#0a0';
    ctx.font = '9px monospace';
    ctx.fillText('(' + gndH.toFixed(1) + ' m tall)', droneX, groundY + 33);

    // Drone icon
    ctx.fillStyle = '#0f0';
    ctx.font = 'bold 11px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('[ DRONE ]', droneX, droneY - 6);

    // Altitude line
    ctx.setLineDash([2, 3]);
    ctx.strokeStyle = '#555';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(droneX, droneY + 4);
    ctx.lineTo(droneX, groundY - 2);
    ctx.stroke();
    ctx.setLineDash([]);

    // Altitude label
    ctx.fillStyle = '#aaa';
    ctx.font = '9px monospace';
    ctx.textAlign = 'left';
    const midAltY = (droneY + groundY) / 2;
    ctx.fillText(alt.toFixed(0) + ' m', droneX + 6, midAltY);

    // HFOV angle arc
    const arcR = 25;
    const halfAngle = Math.atan2(gndWpx / 2, groundY - droneY);
    ctx.beginPath();
    ctx.arc(droneX, droneY, arcR, Math.PI/2 - halfAngle, Math.PI/2 + halfAngle);
    ctx.strokeStyle = 'rgba(0,200,0,0.5)';
    ctx.lineWidth = 1;
    ctx.stroke();

    const hfov = 2 * Math.atan(SENSOR_W / (2 * FOCAL_MM)) * 180 / Math.PI;
    ctx.fillStyle = '#888';
    ctx.font = '8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(hfov.toFixed(1) + '\\u00b0', droneX, droneY + arcR + 10);

    // Detection marker (if active)
    if (pipeState.det_cx != null && pipeState.det_cy != null && pipeState.det_conf) {
      // Map pixel position to ground position
      const normX = (pipeState.det_cx - IMG_W/2) / (IMG_W/2); // -1 to 1
      const markerX = droneX + normX * (gndWpx / 2);
      ctx.fillStyle = '#f44';
      ctx.beginPath();
      ctx.arc(markerX, groundY - 3, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#f66';
      ctx.font = '8px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('DET ' + (pipeState.det_conf * 100).toFixed(0) + '%', markerX, groundY - 10);
    }

    // GSD label (top-left)
    const gsd = (gndW / IMG_W * 1000).toFixed(1); // mm/px
    ctx.fillStyle = '#555';
    ctx.font = '8px monospace';
    ctx.textAlign = 'left';
    ctx.fillText('GSD: ' + gsd + ' mm/px', 6, 12);

    // Dummy height in pixels (top-right)
    const dummyPx = (1.8 / gndW * IMG_W).toFixed(0);
    ctx.textAlign = 'right';
    ctx.fillText('Dummy: ~' + dummyPx + ' px tall', W - 6, 12);

    ctx.textAlign = 'start'; // reset
  }

  // ── Update info text ────────────────────────────────────
  function updateInfo() {
    const alt = pipeState.alt || 30;
    const gndW = alt * SENSOR_W / FOCAL_MM;
    const gndH = alt * SENSOR_H / FOCAL_MM;
    const gsd = gndW / IMG_W * 1000; // mm/px
    const hfov = 2 * Math.atan(SENSOR_W / (2 * FOCAL_MM)) * 180 / Math.PI;

    setText('cvp-gc-alt', alt.toFixed(0) + ' m');
    setText('cvp-gc-w', gndW.toFixed(1) + ' m');
    setText('cvp-gc-h', gndH.toFixed(1) + ' m');
    setText('cvp-gc-gsd', gsd.toFixed(1) + ' mm/px');
    setText('cvp-gps-alt', alt.toFixed(0) + ' m');

    if (pipeState.fps) {
      const ms = (1000 / pipeState.fps).toFixed(0);
      setText('cvp-inf-ms', ms + ' ms');
      setText('cvp-inf-fps', pipeState.fps.toFixed(1));
      setText('cvp-sum-fps', pipeState.fps.toFixed(1));
      setText('cvp-sum-lat', '~' + ms + ' ms');
    }

    if (pipeState.det_conf != null) {
      setText('cvp-det-conf', (pipeState.det_conf * 100).toFixed(1) + '%');
    }
    if (pipeState.det_cx != null && pipeState.det_cy != null) {
      setText('cvp-det-pos', pipeState.det_cx.toFixed(0) + ', ' + pipeState.det_cy.toFixed(0));
    }
  }

  function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  }

  // ── Public API ──────────────────────────────────────────
  window.updatePipelineData = function(data) {
    if (data.alt != null) pipeState.alt = data.alt;
    if (data.yaw != null) pipeState.yaw = data.yaw;
    if (data.lat != null) pipeState.lat = data.lat;
    if (data.lon != null) pipeState.lon = data.lon;
    if (data.fps != null) pipeState.fps = data.fps;
    if (data.det_conf !== undefined) pipeState.det_conf = data.det_conf;
    if (data.det_cx !== undefined) pipeState.det_cx = data.det_cx;
    if (data.det_cy !== undefined) pipeState.det_cy = data.det_cy;
    updateInfo();
    drawFOV();
  };

  // Initial draw
  drawFOV();
  updateInfo();

  // Altitude slider demo (standalone testing)
  // Uncomment to add an interactive slider:
  // const slider = document.createElement('input');
  // slider.type = 'range'; slider.min = 5; slider.max = 60; slider.value = 30;
  // slider.style.cssText = 'width:200px;margin:10px;';
  // slider.oninput = function() { updatePipelineData({alt: +this.value}); };
  // document.getElementById('cv-pipeline-root').appendChild(slider);

})();
</script>
</div>
'''


def get_cv_pipeline_test_page():
    """Return a full standalone HTML page for testing the pipeline visual."""
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>CV Pipeline — SAR Drone</title>
<style>
  html, body {{ margin: 0; padding: 0; background: #0a0a0a; }}
  .test-wrap {{ max-width: 1200px; margin: 20px auto; padding: 0 16px; }}
  .test-controls {{
    background: #1a1a1a; border: 1px solid #333; border-radius: 5px;
    padding: 12px 16px; margin-bottom: 12px;
    font: 11px monospace; color: #aaa;
    display: flex; gap: 24px; flex-wrap: wrap; align-items: center;
  }}
  .test-controls label {{ display: flex; align-items: center; gap: 8px; }}
  .test-controls input[type=range] {{ width: 140px; }}
  .test-controls .val {{ color: #0f0; min-width: 50px; }}
</style>
</head>
<body>
<div class="test-wrap">
  <div class="test-controls">
    <label>Altitude:
      <input type="range" id="tc-alt" min="5" max="60" value="30">
      <span class="val" id="tc-alt-val">30 m</span>
    </label>
    <label>FPS:
      <input type="range" id="tc-fps" min="1" max="30" value="5" step="0.5">
      <span class="val" id="tc-fps-val">5.0</span>
    </label>
    <label>
      <button onclick="simulateDetection()" style="font:11px monospace;padding:4px 10px;background:#222;color:#0f0;border:1px solid #444;border-radius:3px;cursor:pointer;">
        Simulate Detection
      </button>
    </label>
  </div>
  {get_cv_pipeline_html()}
</div>
<script>
  document.getElementById('tc-alt').oninput = function() {{
    document.getElementById('tc-alt-val').textContent = this.value + ' m';
    updatePipelineData({{alt: +this.value}});
  }};
  document.getElementById('tc-fps').oninput = function() {{
    document.getElementById('tc-fps-val').textContent = (+this.value).toFixed(1);
    updatePipelineData({{fps: +this.value}});
  }};
  function simulateDetection() {{
    // Random detection near center
    const cx = 728 + (Math.random() - 0.5) * 600;
    const cy = 544 + (Math.random() - 0.5) * 400;
    const conf = 0.6 + Math.random() * 0.35;
    updatePipelineData({{det_cx: cx, det_cy: cy, det_conf: conf}});
  }}
</script>
</body>
</html>'''


if __name__ == '__main__':
    """Write test page to disk and open in browser."""
    import os
    import webbrowser

    path = os.path.join(os.path.dirname(__file__), '_cv_pipeline_test.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(get_cv_pipeline_test_page())
    print(f'Written to {path}')
    webbrowser.open(path)
