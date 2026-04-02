"""
gps_charts.py — Client-side Interactive GPS Scatter Charts for Browser Dashboard

Replaces server-rendered OpenCV JPEG bullseye plots with smooth, live,
Canvas-based charts that run entirely in the browser.

Provides get_gps_charts_html() which returns a self-contained HTML/CSS/JS string
(no external dependencies) rendering:
  1. Main scatter plot (bullseye rings, color modes, zoom/pan, map background)
  2. Error convergence line chart (running mean/weighted/median)
  3. Smart cluster mini-chart (tightest 10, lock status)

Usage in passive_watch.py or pi_flight.py:
    from field_tools.gps_charts import get_gps_charts_html

    # Insert into your HTML page:
    html = get_gps_charts_html()

    # Requires API endpoint:
    #   /api/estimates-full → JSON with:
    #     {
    #       "estimates": [[lat, lon, pdist, alt, conf], ...],
    #       "smart": {"locked": bool, "cluster": [[lat,lon,pdist], ...],
    #                 "spread": float, "median": [lat,lon]},
    #       "drone": {"lat": float, "lon": float}
    #     }
"""

import json
import config


def get_gps_charts_html():
    """Return HTML/CSS/JS string for interactive GPS scatter charts."""
    cfg = {
        "REF_LAT": config.REF_LAT,
        "REF_LON": config.REF_LON,
        "MAP_WIDTH_METERS": config.MAP_WIDTH_METERS,
    }
    cfg_json = json.dumps(cfg)

    return f'''
<style>
#gps-charts-root {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  background: #1a1a1a;
  padding: 8px;
  border-radius: 6px;
  font-family: "Consolas", "Courier New", monospace;
  color: #ccc;
  user-select: none;
}}
#gps-charts-root * {{ box-sizing: border-box; }}
.gps-chart-col {{ display: flex; flex-direction: column; gap: 8px; }}
.gps-chart-panel {{
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}}
.gps-chart-panel canvas {{ display: block; }}
.gps-chart-toolbar {{
  display: flex;
  gap: 4px;
  padding: 4px 6px;
  background: #222;
  border-bottom: 1px solid #333;
  flex-wrap: wrap;
  align-items: center;
}}
.gps-chart-toolbar button {{
  background: #333;
  color: #ccc;
  border: 1px solid #444;
  border-radius: 3px;
  padding: 2px 8px;
  font: 11px monospace;
  cursor: pointer;
}}
.gps-chart-toolbar button:hover {{ background: #444; }}
.gps-chart-toolbar button.active {{ background: #555; color: #0f0; border-color: #0f0; }}
.gps-chart-toolbar .sep {{ width: 1px; height: 16px; background: #444; margin: 0 4px; }}
.gps-filter-row {{
  padding: 3px 6px;
  background: #222;
  border-bottom: 1px solid #333;
  font: 10px monospace;
  color: #888;
}}
.gps-filter-row label {{ color: #0f0; margin-right: 4px; }}
.gps-filter-row input[type=range] {{
  width: 100%;
  height: 10px;
  accent-color: #0f0;
  vertical-align: middle;
}}
.gps-filter-row .fval {{ color: #0f0; min-width: 36px; display: inline-block; text-align: right; }}
.gps-filter-group {{ display: block; }}
.gps-slider-line {{ display: flex; align-items: center; gap: 4px; margin: 1px 0; }}
.gps-slider-line span.slbl {{ color: #888; min-width: 28px; }}
.gps-chart-stats {{
  padding: 4px 8px;
  background: #222;
  border-top: 1px solid #333;
  font: 11px monospace;
  color: #aaa;
  line-height: 1.6;
}}
.gps-chart-stats .val {{ color: #0f0; }}
.gps-chart-stats .lbl {{ color: #888; }}
#gps-tooltip {{
  position: fixed;
  background: rgba(0,0,0,0.9);
  color: #0f0;
  font: 11px monospace;
  padding: 6px 10px;
  border: 1px solid #0f0;
  border-radius: 4px;
  pointer-events: none;
  z-index: 9999;
  display: none;
  white-space: pre;
}}
</style>

<div id="gps-charts-root">
  <!-- Left column: main scatter + convergence -->
  <div class="gps-chart-col">
    <div class="gps-chart-panel" style="width:500px;">
      <div class="gps-chart-toolbar" id="scatter-toolbar">
        <span style="color:#888;font-size:10px;">Color:</span>
        <button id="btn-color-pcent" class="active" data-mode="pixel_centrality">Pixel Centrality</button>
        <button id="btn-color-dcent" data-mode="distance_centrality">Distance Centrality</button>
        <button id="btn-color-alt" data-mode="altitude">Altitude</button>
        <button id="btn-color-conf" data-mode="confidence">Confidence</button>
        <div class="sep"></div>
        <button id="btn-map-bg">Map BG: off</button>
        <button id="btn-toggle-dots">Dots: ON</button>
        <div class="sep"></div>
        <button id="btn-reset-view">Reset View</button>
        <div class="sep"></div>
        <label style="color:#888;font-size:10px;">Ground Truth:</label>
        <input type="text" id="gt-input" placeholder="lat,lon" style="width:140px;background:#222;color:#0f0;border:1px solid #444;border-radius:3px;padding:2px 4px;font:11px monospace;">
        <button id="gt-btn">Set</button>
        <button id="gt-clear-btn" style="display:none;">Clear</button>
      </div>
      <div class="gps-filter-row" id="scatter-filters">
        <div id="filter-pdist" class="gps-filter-group">
          <label>Pdist (px):</label>
          <div class="gps-slider-line"><span class="slbl">Min:</span> <span class="fval" id="fv-pdist-min">0</span> <input type="range" id="f-pdist-min" min="0" max="1000" value="0" step="1"></div>
          <div class="gps-slider-line"><span class="slbl">Max:</span> <span class="fval" id="fv-pdist-max">1000</span> <input type="range" id="f-pdist-max" min="0" max="1000" value="1000" step="1"></div>
        </div>
        <div id="filter-dist" class="gps-filter-group" style="display:none;">
          <label>Distance (m):</label>
          <div class="gps-slider-line"><span class="slbl">Min:</span> <span class="fval" id="fv-dist-min">0</span> <input type="range" id="f-dist-min" min="0" max="50" value="0" step="0.1"></div>
          <div class="gps-slider-line"><span class="slbl">Max:</span> <span class="fval" id="fv-dist-max">50</span> <input type="range" id="f-dist-max" min="0" max="50" value="50" step="0.1"></div>
        </div>
        <div id="filter-alt" class="gps-filter-group" style="display:none;">
          <label>Alt (m):</label>
          <div class="gps-slider-line"><span class="slbl">Min:</span> <span class="fval" id="fv-alt-min">0</span> <input type="range" id="f-alt-min" min="0" max="100" value="0" step="0.5"></div>
          <div class="gps-slider-line"><span class="slbl">Max:</span> <span class="fval" id="fv-alt-max">100</span> <input type="range" id="f-alt-max" min="0" max="100" value="100" step="0.5"></div>
        </div>
        <div id="filter-conf" class="gps-filter-group" style="display:none;">
          <label>Conf:</label>
          <div class="gps-slider-line"><span class="slbl">Min:</span> <span class="fval" id="fv-conf-min">0</span> <input type="range" id="f-conf-min" min="0" max="1" value="0" step="0.01"></div>
          <div class="gps-slider-line"><span class="slbl">Max:</span> <span class="fval" id="fv-conf-max">1.00</span> <input type="range" id="f-conf-max" min="0" max="1" value="1" step="0.01"></div>
        </div>
      </div>
      <canvas id="scatter-canvas" width="500" height="400" style="cursor:grab;"></canvas>
      <div class="gps-chart-stats" id="scatter-stats">
        <span class="lbl">Waiting for detections...</span>
      </div>
    </div>
    <div class="gps-chart-panel" style="width:500px;">
      <canvas id="convergence-canvas" width="500" height="200"></canvas>
    </div>
  </div>

  <!-- Right column: smart cluster + central 4m side by side -->
  <div class="gps-chart-col">
    <div style="display:flex; gap:8px;">
      <div class="gps-chart-panel" style="width:250px;">
        <canvas id="cluster-canvas" width="250" height="300"></canvas>
      </div>
      <div class="gps-chart-panel" style="width:250px;">
        <canvas id="central-canvas" width="250" height="300"></canvas>
      </div>
    </div>
  </div>
</div>

<div id="gps-tooltip"></div>

<script>
(function() {{
  "use strict";

  // ── Config from Python ──
  const CFG = {cfg_json};
  const REF_LAT = CFG.REF_LAT;
  const REF_LON = CFG.REF_LON;
  const MAP_W_M = CFG.MAP_WIDTH_METERS;
  const COS_REF = Math.cos(REF_LAT * Math.PI / 180);

  // ── State ──
  let estimates = [];       // [[lat, lon, pdist, alt, conf], ...]
  let smartData = null;     // {{locked, cluster, spread, median}}
  let dronePos = null;      // {{lat, lon}}
  let bestData = null;      // {{est_lat, est_lon, drone_lat, drone_lon, center_dist}} or null
  let groundTruth = null;   // {{lat, lon}} or null
  let prevDataHash = "";
  let colorMode = "pixel_centrality";   // pixel_centrality | distance_centrality | altitude | confidence
  const F_PX = 1584;  // focal length in pixels for distance centrality
  let mapBgOn = true;  // default ON
  let mapImg = null;
  let mapLoading = false;
  let showDots = true;

  // Scatter view state (zoom/pan in meters)
  let viewCenterE = 0, viewCenterN = 0;  // meters offset from mean
  let viewScale = 1;   // px per meter (computed from data)
  let baseScale = 1;   // auto-fit scale
  let zoomLevel = 1;   // user zoom multiplier
  let isDragging = false;
  let dragStartX = 0, dragStartY = 0;
  let dragStartCE = 0, dragStartCN = 0;

  // ── Canvas refs ──
  const scatterCvs = document.getElementById("scatter-canvas");
  const scatterCtx = scatterCvs.getContext("2d");
  const convergeCvs = document.getElementById("convergence-canvas");
  const convergeCtx = convergeCvs.getContext("2d");
  const clusterCvs = document.getElementById("cluster-canvas");
  const clusterCtx = clusterCvs.getContext("2d");
  const centralCvs = document.getElementById("central-canvas");
  const centralCtx = centralCvs.getContext("2d");
  const statsEl = document.getElementById("scatter-stats");
  const tooltip = document.getElementById("gps-tooltip");

  // High-DPI support
  function setupHiDPI(canvas, ctx, w, h) {{
    const dpr = window.devicePixelRatio || 1;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }}
  setupHiDPI(scatterCvs, scatterCtx, 500, 400);
  setupHiDPI(convergeCvs, convergeCtx, 500, 200);
  setupHiDPI(clusterCvs, clusterCtx, 250, 300);
  setupHiDPI(centralCvs, centralCtx, 250, 300);

  // ── Color mode buttons + dynamic filter visibility ──
  function updateFilterVisibility() {{
    document.getElementById("filter-pdist").style.display = colorMode === "pixel_centrality" ? "block" : "none";
    document.getElementById("filter-dist").style.display = colorMode === "distance_centrality" ? "block" : "none";
    document.getElementById("filter-alt").style.display = colorMode === "altitude" ? "block" : "none";
    document.getElementById("filter-conf").style.display = colorMode === "confidence" ? "block" : "none";
  }}
  // Set initial visibility
  updateFilterVisibility();

  document.querySelectorAll("#scatter-toolbar button[data-mode]").forEach(btn => {{
    btn.addEventListener("click", () => {{
      colorMode = btn.dataset.mode;
      document.querySelectorAll("#scatter-toolbar button[data-mode]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      updateFilterVisibility();
      drawScatter();
    }});
  }});

  document.getElementById("btn-map-bg").addEventListener("click", () => {{
    mapBgOn = !mapBgOn;
    document.getElementById("btn-map-bg").textContent = "Map BG: " + (mapBgOn ? "ON" : "off");
    if (mapBgOn && !mapImg && !mapLoading) {{
      mapLoading = true;
      const img = new Image();
      img.onload = () => {{ mapImg = img; mapLoading = false; drawScatter(); }};
      img.onerror = () => {{ mapLoading = false; }};
      img.src = "/map";
    }}
    drawScatter();
  }});

  document.getElementById("btn-toggle-dots").addEventListener("click", () => {{
    showDots = !showDots;
    document.getElementById("btn-toggle-dots").textContent = "Dots: " + (showDots ? "ON" : "OFF");
    drawScatter();
  }});

  // Load map image on startup since mapBgOn defaults to true
  if (mapBgOn && !mapImg && !mapLoading) {{
    mapLoading = true;
    const img = new Image();
    img.onload = () => {{ mapImg = img; mapLoading = false; drawScatter(); }};
    img.onerror = () => {{ mapLoading = false; }};
    img.src = "/map";
  }}

  document.getElementById("btn-reset-view").addEventListener("click", () => {{
    viewCenterE = 0;
    viewCenterN = 0;
    zoomLevel = 1;
    drawScatter();
  }});

  document.getElementById("gt-btn").addEventListener("click", () => {{
    const val = document.getElementById("gt-input").value.trim();
    const parts = val.split(",").map(s => parseFloat(s.trim()));
    if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {{
      groundTruth = {{ lat: parts[0], lon: parts[1] }};
      // Also send to server so interactive_map.py can use it
      fetch("/api/set-ground-truth?lat=" + parts[0] + "&lon=" + parts[1]).catch(() => {{}});
      document.getElementById("gt-clear-btn").style.display = "inline";
      document.getElementById("gt-input").style.borderColor = "#0f0";
      needsRedraw = true;
    }} else {{
      document.getElementById("gt-input").style.borderColor = "#f00";
    }}
  }});

  document.getElementById("gt-clear-btn").addEventListener("click", () => {{
    groundTruth = null;
    document.getElementById("gt-input").value = "";
    document.getElementById("gt-input").style.borderColor = "#444";
    document.getElementById("gt-clear-btn").style.display = "none";
    fetch("/api/clear-ground-truth").catch(() => {{}});
    needsRedraw = true;
  }});

  // ── Filter state ──
  let filterPdistMin = 0, filterPdistMax = 1000;
  let filterDistMin = 0, filterDistMax = 50;
  let filterAltMin = 0, filterAltMax = 100;
  let filterConfMin = 0, filterConfMax = 1;

  // ── Global color range (computed from ALL estimates, not filtered subset) ──
  let globalMaxPd = 1, globalMinAlt = 0, globalMaxAlt = 100;
  let globalMaxDistM = 1, globalMinConf = 0, globalMaxConf = 1;

  function updateGlobalColorRange() {{
    if (estimates.length === 0) return;
    globalMaxPd = 0; globalMinAlt = Infinity; globalMaxAlt = -Infinity;
    globalMaxDistM = 0; globalMinConf = 1; globalMaxConf = 0;
    for (const e of estimates) {{
      const pdist = e[2], alt = e[3], conf = e[4];
      if (pdist > globalMaxPd) globalMaxPd = pdist;
      if (alt < globalMinAlt) globalMinAlt = alt;
      if (alt > globalMaxAlt) globalMaxAlt = alt;
      if (conf < globalMinConf) globalMinConf = conf;
      if (conf > globalMaxConf) globalMaxConf = conf;
      const dm = pdist * alt / F_PX;
      if (dm > globalMaxDistM) globalMaxDistM = dm;
    }}
    globalMaxPd = Math.max(globalMaxPd, 1);
    globalMaxDistM = Math.max(globalMaxDistM, 0.1);
  }}

  function updateFilterRanges() {{
    // Adjust slider max values based on actual data
    if (estimates.length > 0) {{
      let maxPd = 0, maxA = 0, maxDist = 0;
      for (const e of estimates) {{
        if (e[2] > maxPd) maxPd = e[2];
        if (e[3] > maxA) maxA = e[3];
        const dm = e[2] * e[3] / F_PX;
        if (dm > maxDist) maxDist = dm;
      }}
      maxPd = Math.ceil(maxPd) || 1000;
      maxA = Math.ceil(maxA) || 100;
      maxDist = Math.ceil(maxDist * 10) / 10 || 50;
      const pdMinEl = document.getElementById("f-pdist-min");
      const pdMaxEl = document.getElementById("f-pdist-max");
      const altMinEl = document.getElementById("f-alt-min");
      const altMaxEl = document.getElementById("f-alt-max");
      const distMinEl = document.getElementById("f-dist-min");
      const distMaxEl = document.getElementById("f-dist-max");
      pdMinEl.max = maxPd; pdMaxEl.max = maxPd;
      altMinEl.max = maxA; altMaxEl.max = maxA;
      distMinEl.max = maxDist; distMaxEl.max = maxDist;
      // If max slider is at old max, snap to new max
      if (parseFloat(pdMaxEl.value) >= parseFloat(pdMaxEl.max) - 1 || filterPdistMax >= maxPd) {{
        pdMaxEl.value = maxPd; filterPdistMax = maxPd;
        document.getElementById("fv-pdist-max").textContent = maxPd;
      }}
      if (parseFloat(altMaxEl.value) >= parseFloat(altMaxEl.max) - 0.5 || filterAltMax >= maxA) {{
        altMaxEl.value = maxA; filterAltMax = maxA;
        document.getElementById("fv-alt-max").textContent = maxA;
      }}
      if (parseFloat(distMaxEl.value) >= parseFloat(distMaxEl.max) - 0.1 || filterDistMax >= maxDist) {{
        distMaxEl.value = maxDist; filterDistMax = maxDist;
        document.getElementById("fv-dist-max").textContent = maxDist.toFixed(1);
      }}
    }}
  }}

  function onFilterChange() {{
    filterPdistMin = parseFloat(document.getElementById("f-pdist-min").value);
    filterPdistMax = parseFloat(document.getElementById("f-pdist-max").value);
    filterDistMin = parseFloat(document.getElementById("f-dist-min").value);
    filterDistMax = parseFloat(document.getElementById("f-dist-max").value);
    filterAltMin = parseFloat(document.getElementById("f-alt-min").value);
    filterAltMax = parseFloat(document.getElementById("f-alt-max").value);
    filterConfMin = parseFloat(document.getElementById("f-conf-min").value);
    filterConfMax = parseFloat(document.getElementById("f-conf-max").value);
    // Clamp min <= max
    if (filterPdistMin > filterPdistMax) filterPdistMin = filterPdistMax;
    if (filterDistMin > filterDistMax) filterDistMin = filterDistMax;
    if (filterAltMin > filterAltMax) filterAltMin = filterAltMax;
    if (filterConfMin > filterConfMax) filterConfMin = filterConfMax;
    // Update display values
    document.getElementById("fv-pdist-min").textContent = filterPdistMin.toFixed(0);
    document.getElementById("fv-pdist-max").textContent = filterPdistMax.toFixed(0);
    document.getElementById("fv-dist-min").textContent = filterDistMin.toFixed(1);
    document.getElementById("fv-dist-max").textContent = filterDistMax.toFixed(1);
    document.getElementById("fv-alt-min").textContent = filterAltMin.toFixed(1);
    document.getElementById("fv-alt-max").textContent = filterAltMax.toFixed(1);
    document.getElementById("fv-conf-min").textContent = filterConfMin.toFixed(2);
    document.getElementById("fv-conf-max").textContent = filterConfMax.toFixed(2);
    drawScatter();
  }}

  document.querySelectorAll("#scatter-filters input[type=range]").forEach(el => {{
    el.addEventListener("input", onFilterChange);
  }});

  // ── GPS helpers ──
  function gpsToMeters(lat, lon, refLat, refLon) {{
    const n = (lat - refLat) * 111320;
    const e = (lon - refLon) * 111320 * Math.cos(refLat * Math.PI / 180);
    return [e, n];
  }}

  function heatColor(val) {{
    // 0 = green, 1 = red
    const v = Math.max(0, Math.min(1, val));
    const r = Math.round(255 * v);
    const g = Math.round(255 * (1 - v));
    return `rgb(${{r}},${{g}},0)`;
  }}

  // ── Data hash for change detection ──
  function dataHash() {{
    // Include length so every new detection triggers redraw
    const base = estimates.length;
    const smart = smartData ? (smartData.locked ? "L" : "S") + (smartData.cluster ? smartData.cluster.length : 0) : "X";
    const central = estimates.filter(e => e[2] < 200).length;
    const gtKey = groundTruth ? "GT" + groundTruth.lat.toFixed(5) : "noGT";
    const bestKey = bestData ? "B" + bestData.est_lat.toFixed(5) : "noB";
    return base + ":" + smart + ":" + central + ":" + (smartLocked ? "SL" : "SU") + ":" + gtKey + ":" + bestKey;
  }}

  // ── Scatter plot ──
  function drawScatter() {{
    const W = 500, H = 400;
    const ctx = scatterCtx;
    ctx.clearRect(0, 0, W, H);

    // Background
    ctx.fillStyle = "#1a1a1a";
    ctx.fillRect(0, 0, W, H);

    if (estimates.length === 0) {{
      ctx.fillStyle = "#555";
      ctx.font = "14px monospace";
      ctx.textAlign = "center";
      ctx.fillText("Waiting for detections...", W / 2, H / 2);
      ctx.textAlign = "start";
      statsEl.innerHTML = '<span class="lbl">Waiting for detections...</span>';
      return;
    }}

    // Apply filter based on active color mode
    const filtered = estimates.filter(e => {{
      const pdist = e[2], alt = e[3], conf = e[4];
      if (colorMode === "pixel_centrality") {{
        return pdist >= filterPdistMin && pdist <= filterPdistMax;
      }} else if (colorMode === "distance_centrality") {{
        const dist_m = pdist * alt / F_PX;
        return dist_m >= filterDistMin && dist_m <= filterDistMax;
      }} else if (colorMode === "altitude") {{
        return alt >= filterAltMin && alt <= filterAltMax;
      }} else if (colorMode === "confidence") {{
        return conf >= filterConfMin && conf <= filterConfMax;
      }}
      return true;
    }});

    if (filtered.length === 0) {{
      ctx.fillStyle = "#555";
      ctx.font = "13px monospace";
      ctx.textAlign = "center";
      ctx.fillText("All " + estimates.length + " points filtered out", W / 2, H / 2);
      ctx.textAlign = "start";
      statsEl.innerHTML = '<span class="lbl">Filtered:</span> <span class="val">0 / ' + estimates.length + '</span>';
      return;
    }}

    // Compute mean
    let sumLat = 0, sumLon = 0;
    for (const e of filtered) {{ sumLat += e[0]; sumLon += e[1]; }}
    const meanLat = sumLat / filtered.length;
    const meanLon = sumLon / filtered.length;

    // Origin: ground truth if set, else mean
    const originLat = groundTruth ? groundTruth.lat : meanLat;
    const originLon = groundTruth ? groundTruth.lon : meanLon;

    // Convert all to meters relative to origin
    const pts = filtered.map((e, i) => {{
      const [em, nm] = gpsToMeters(e[0], e[1], originLat, originLon);
      return {{ e: em, n: nm, pdist: e[2], alt: e[3], conf: e[4], idx: i, lat: e[0], lon: e[1] }};
    }});

    // Auto-scale: fit 95th percentile distance
    const dists = pts.map(p => Math.sqrt(p.e * p.e + p.n * p.n)).sort((a, b) => a - b);
    const p95 = dists[Math.floor(dists.length * 0.95)] || 5;
    const maxRange = Math.max(p95 * 2.2, 4);
    const margin = 40;
    const usable = Math.min(W, H) - 2 * margin;
    baseScale = usable / maxRange;
    viewScale = baseScale * zoomLevel;

    const cx = W / 2;
    const cy = H / 2;

    // Map background
    if (mapBgOn && mapImg) {{
      drawMapBackground(ctx, W, H, cx, cy, originLat, originLon);
    }}

    // Grid lines
    ctx.strokeStyle = "#333";
    ctx.lineWidth = 0.5;
    const gridStep = autoGridStep(maxRange / zoomLevel);
    const viewLeft = -cx / viewScale + viewCenterE;
    const viewRight = (W - cx) / viewScale + viewCenterE;
    const viewTop = -cy / viewScale + viewCenterN;
    const viewBot = (H - cy) / viewScale + viewCenterN;
    const gStart = Math.floor(viewLeft / gridStep) * gridStep;
    const gEnd = Math.ceil(viewRight / gridStep) * gridStep;
    ctx.font = "9px monospace";
    ctx.fillStyle = "#555";
    for (let g = gStart; g <= gEnd; g += gridStep) {{
      const sx = cx + (g - viewCenterE) * viewScale;
      ctx.beginPath(); ctx.moveTo(sx, 0); ctx.lineTo(sx, H); ctx.stroke();
      if (Math.abs(g) > 0.01) {{
        ctx.fillText(g.toFixed(g === Math.round(g) ? 0 : 1) + "m", sx + 2, H - 4);
      }}
    }}
    const gStartN = Math.floor(viewTop / gridStep) * gridStep;
    const gEndN = Math.ceil(viewBot / gridStep) * gridStep;
    for (let g = gStartN; g <= gEndN; g += gridStep) {{
      const sy = cy - (g - viewCenterN) * viewScale;
      ctx.beginPath(); ctx.moveTo(0, sy); ctx.lineTo(W, sy); ctx.stroke();
      if (Math.abs(g) > 0.01) {{
        ctx.fillText(g.toFixed(g === Math.round(g) ? 0 : 1) + "m", 2, sy - 2);
      }}
    }}

    // Bullseye rings
    const rings = [1, 2, 3, 5, 10, 20, 50];
    ctx.strokeStyle = "#444";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    for (const r of rings) {{
      const rpx = r * viewScale;
      if (rpx > 5 && rpx < Math.max(W, H) * 2) {{
        const rx = cx + (0 - viewCenterE) * viewScale;
        const ry = cy - (0 - viewCenterN) * viewScale;
        ctx.beginPath();
        ctx.arc(rx, ry, rpx, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = "#666";
        ctx.font = "10px monospace";
        ctx.fillText(r + "m", rx + rpx + 3, ry - 3);
      }}
    }}
    ctx.setLineDash([]);

    // Compass labels
    ctx.fillStyle = "#888";
    ctx.font = "bold 12px monospace";
    ctx.textAlign = "center";
    const originX = cx + (0 - viewCenterE) * viewScale;
    const originY = cy - (0 - viewCenterN) * viewScale;
    ctx.fillText("N", originX, Math.max(14, originY - Math.min(H / 2 - 10, 5 * viewScale) - 5));
    ctx.fillText("E", Math.min(W - 10, originX + Math.min(W / 2 - 10, 5 * viewScale) + 12), originY + 4);
    ctx.textAlign = "start";

    // Color values — use GLOBAL range (full dataset) so colors are absolute, not relative to filter
    const altRange = Math.max(globalMaxAlt - globalMinAlt, 0.1);
    const confRange = Math.max(globalMaxConf - globalMinConf, 0.01);

    // Draw dots (skip when toggled off)
    if (showDots) {{
      for (const p of pts) {{
        const sx = cx + (p.e - viewCenterE) * viewScale;
        const sy = cy - (p.n - viewCenterN) * viewScale;
        if (sx < -10 || sx > W + 10 || sy < -10 || sy > H + 10) continue;

        let val = 0;
        if (colorMode === "pixel_centrality") val = Math.min(1, p.pdist / globalMaxPd);
        else if (colorMode === "distance_centrality") val = Math.min(1, (p.pdist * p.alt / F_PX) / globalMaxDistM);
        else if (colorMode === "altitude") val = (p.alt - globalMinAlt) / altRange;
        else if (colorMode === "confidence") val = 1 - (p.conf - globalMinConf) / confRange;

        ctx.fillStyle = heatColor(val);
        ctx.beginPath();
        ctx.arc(sx, sy, 3.5, 0, Math.PI * 2);
        ctx.fill();
      }}
    }}

    // Compute mean position in meters (relative to origin)
    const meanME = pts.reduce((s, p) => s + p.e, 0) / pts.length;
    const meanMN = pts.reduce((s, p) => s + p.n, 0) / pts.length;

    // Compute weighted mean (weight = 1/cdist^2)
    let wE = 0, wN = 0, wTotal = 0;
    for (const p of pts) {{
      const cd = Math.max(p.pdist, 1);
      const w = 1 / (cd * cd);
      wE += p.e * w;
      wN += p.n * w;
      wTotal += w;
    }}
    if (wTotal > 0) {{ wE /= wTotal; wN /= wTotal; }}

    // Compute median
    const sortedE = pts.map(p => p.e).sort((a, b) => a - b);
    const sortedN = pts.map(p => p.n).sort((a, b) => a - b);
    const medE = sortedE[Math.floor(sortedE.length / 2)];
    const medN = sortedN[Math.floor(sortedN.length / 2)];

    // Ground truth star marker (bright yellow) — at origin when GT is set
    if (groundTruth) {{
      const gtsx = cx + (0 - viewCenterE) * viewScale;
      const gtsy = cy - (0 - viewCenterN) * viewScale;
      // 5-pointed star
      ctx.fillStyle = "#ffff00";
      ctx.strokeStyle = "#ffff00";
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let i = 0; i < 10; i++) {{
        const r = (i % 2 === 0) ? 9 : 4;
        const a = -Math.PI / 2 + (i * Math.PI / 5);
        const sx2 = gtsx + r * Math.cos(a);
        const sy2 = gtsy + r * Math.sin(a);
        if (i === 0) ctx.moveTo(sx2, sy2); else ctx.lineTo(sx2, sy2);
      }}
      ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#ffff00";
      ctx.font = "bold 10px monospace";
      ctx.textAlign = "center";
      ctx.fillText("TRUE", gtsx, gtsy - 13);
      ctx.textAlign = "start";
    }}

    // Mean marker (yellow cross)
    const msx = cx + (meanME - viewCenterE) * viewScale;
    const msy = cy - (meanMN - viewCenterN) * viewScale;
    ctx.strokeStyle = "#ffdc00";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(msx - 8, msy); ctx.lineTo(msx + 8, msy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(msx, msy - 8); ctx.lineTo(msx, msy + 8); ctx.stroke();

    // Weighted mean marker (cyan SQUARE)
    const wsx = cx + (wE - viewCenterE) * viewScale;
    const wsy = cy - (wN - viewCenterN) * viewScale;
    ctx.strokeStyle = "#00ffff";
    ctx.lineWidth = 2;
    ctx.strokeRect(wsx - 6, wsy - 6, 12, 12);

    // Median marker (pink/magenta triangle — distinct from SMART star)
    const medsx = cx + (medE - viewCenterE) * viewScale;
    const medsy = cy - (medN - viewCenterN) * viewScale;
    ctx.strokeStyle = "#ff66ff";
    ctx.fillStyle = "rgba(255,102,255,0.4)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(medsx, medsy - 8);
    ctx.lineTo(medsx + 7, medsy + 5);
    ctx.lineTo(medsx - 7, medsy + 5);
    ctx.closePath(); ctx.fill(); ctx.stroke();

    // Best Detection markers (red circle = estimate, red X = drone, dashed line between)
    if (bestData && bestData.est_lat !== undefined) {{
      const [bestEstE, bestEstN] = gpsToMeters(bestData.est_lat, bestData.est_lon, originLat, originLon);
      const bestEstSx = cx + (bestEstE - viewCenterE) * viewScale;
      const bestEstSy = cy - (bestEstN - viewCenterN) * viewScale;

      // Red filled circle at estimate position
      ctx.fillStyle = "#ff2020";
      ctx.strokeStyle = "#ff2020";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(bestEstSx, bestEstSy, 6, 0, Math.PI * 2);
      ctx.fill();

      // Label "BEST" near the circle
      ctx.font = "bold 10px monospace";
      ctx.textAlign = "center";
      ctx.fillText("BEST", bestEstSx, bestEstSy - 10);
      ctx.textAlign = "start";

      if (bestData.drone_lat !== undefined) {{
        const [bestDrnE, bestDrnN] = gpsToMeters(bestData.drone_lat, bestData.drone_lon, originLat, originLon);
        const bestDrnSx = cx + (bestDrnE - viewCenterE) * viewScale;
        const bestDrnSy = cy - (bestDrnN - viewCenterN) * viewScale;

        // Red X at drone position
        ctx.strokeStyle = "#ff2020";
        ctx.lineWidth = 2;
        const xSz = 8;
        ctx.beginPath(); ctx.moveTo(bestDrnSx - xSz, bestDrnSy - xSz); ctx.lineTo(bestDrnSx + xSz, bestDrnSy + xSz); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(bestDrnSx + xSz, bestDrnSy - xSz); ctx.lineTo(bestDrnSx - xSz, bestDrnSy + xSz); ctx.stroke();

        // Red dashed line connecting drone and estimate
        ctx.setLineDash([5, 4]);
        ctx.strokeStyle = "#ff2020";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(bestDrnSx, bestDrnSy);
        ctx.lineTo(bestEstSx, bestEstSy);
        ctx.stroke();
        ctx.setLineDash([]);
      }}
    }}

    // Smart cluster median marker (magenta 5-pointed star) — when locked
    let smartMedE = null, smartMedN = null;
    if (smartData && smartData.locked && smartData.median) {{
      [smartMedE, smartMedN] = gpsToMeters(smartData.median[0], smartData.median[1], originLat, originLon);
      const smsx = cx + (smartMedE - viewCenterE) * viewScale;
      const smsy = cy - (smartMedN - viewCenterN) * viewScale;
      // 5-pointed star in magenta
      ctx.fillStyle = "#ff00ff";
      ctx.strokeStyle = "#ff00ff";
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let i = 0; i < 10; i++) {{
        const r = (i % 2 === 0) ? 9 : 4;
        const a = -Math.PI / 2 + (i * Math.PI / 5);
        const sx2 = smsx + r * Math.cos(a);
        const sy2 = smsy + r * Math.sin(a);
        if (i === 0) ctx.moveTo(sx2, sy2); else ctx.lineTo(sx2, sy2);
      }}
      ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#ff00ff";
      ctx.font = "bold 10px monospace";
      ctx.textAlign = "center";
      ctx.fillText("SMART", smsx, smsy - 13);
      // Show lat/lon coordinates below the star
      ctx.font = "9px monospace";
      ctx.fillText(smartData.median[0].toFixed(7) + ", " + smartData.median[1].toFixed(7), smsx, smsy + 18);
      ctx.textAlign = "start";
    }}

    // Central-10 median marker (orange diamond) — first 10 with pdist < 200
    let c10MedE = null, c10MedN = null;
    const central10 = filtered.filter(e => e[2] < 200).slice(0, 10);
    if (central10.length >= 3) {{
      const c10pts = central10.map(e => {{
        const [em2, nm2] = gpsToMeters(e[0], e[1], originLat, originLon);
        return {{ e: em2, n: nm2 }};
      }});
      const c10sortE = c10pts.map(p => p.e).sort((a, b) => a - b);
      const c10sortN = c10pts.map(p => p.n).sort((a, b) => a - b);
      c10MedE = c10sortE[Math.floor(c10sortE.length / 2)];
      c10MedN = c10sortN[Math.floor(c10sortN.length / 2)];
      const c10sx = cx + (c10MedE - viewCenterE) * viewScale;
      const c10sy = cy - (c10MedN - viewCenterN) * viewScale;
      // Orange diamond
      ctx.fillStyle = "#ff8c00";
      ctx.strokeStyle = "#ff8c00";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(c10sx, c10sy - 8); ctx.lineTo(c10sx + 6, c10sy);
      ctx.lineTo(c10sx, c10sy + 8); ctx.lineTo(c10sx - 6, c10sy);
      ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.font = "bold 10px monospace";
      ctx.textAlign = "center";
      ctx.fillText("4m", c10sx, c10sy - 12);
      ctx.textAlign = "start";
    }}

    // Stats — error is distance from origin (ground truth if set, else mean)
    const cep50 = dists[Math.floor(dists.length / 2)] || 0;
    const maxSpread = dists[dists.length - 1] || 0;
    const meanErr = Math.sqrt(meanME * meanME + meanMN * meanMN);
    const wErr = Math.sqrt(wE * wE + wN * wN);
    const medErr = Math.sqrt(medE * medE + medN * medN);

    // Best detection error from origin
    let bestErrStr = "";
    if (bestData && bestData.est_lat !== undefined) {{
      const [bestEstE2, bestEstN2] = gpsToMeters(bestData.est_lat, bestData.est_lon, originLat, originLon);
      const bestErr = Math.sqrt(bestEstE2 * bestEstE2 + bestEstN2 * bestEstN2);
      bestErrStr = ` &nbsp; <span class="lbl" style="color:#ff2020;">Best:</span> <span class="val">${{bestErr.toFixed(2)}}m</span>`;
    }}

    // Smart cluster median error from origin
    let smartErrStr = "";
    if (smartMedE !== null && smartMedN !== null) {{
      const smartErr = Math.sqrt(smartMedE * smartMedE + smartMedN * smartMedN);
      smartErrStr = ` &nbsp; <span class="lbl" style="color:#ff00ff;">Smart:</span> <span class="val">${{smartErr.toFixed(2)}}m</span>`;
    }} else {{
      smartErrStr = ` &nbsp; <span class="lbl" style="color:#666;">SMART: searching...</span>`;
    }}

    // Central-10 median error from origin
    let c10ErrStr = "";
    if (c10MedE !== null && c10MedN !== null) {{
      const c10Err = Math.sqrt(c10MedE * c10MedE + c10MedN * c10MedN);
      c10ErrStr = ` &nbsp; <span class="lbl" style="color:#ff8c00;">4m:</span> <span class="val">${{c10Err.toFixed(2)}}m</span>`;
    }}

    const filtLabel = filtered.length < estimates.length
      ? `${{filtered.length}}/${{estimates.length}}`
      : `${{estimates.length}}`;
    const gtLabel = groundTruth
      ? ` &nbsp; <span class="lbl" style="color:#ff0;">GT:</span> <span class="val">${{groundTruth.lat.toFixed(7)}}, ${{groundTruth.lon.toFixed(7)}}</span>`
      : ` &nbsp; <span class="lbl">GPS:</span> <span class="val">${{meanLat.toFixed(7)}}, ${{meanLon.toFixed(7)}}</span>`;
    const errRefLabel = groundTruth ? " (from GT)" : " (from mean)";
    statsEl.innerHTML =
      `<span class="lbl">N:</span> <span class="val">${{filtLabel}}</span>` +
      ` &nbsp; <span class="lbl">CEP50:</span> <span class="val">${{cep50.toFixed(2)}}m</span>` +
      ` &nbsp; <span class="lbl">Max:</span> <span class="val">${{maxSpread.toFixed(2)}}m</span>` +
      gtLabel +
      `<br><span class="lbl" style="color:#ffdc00;">Mean (simple avg):</span> <span class="val">${{meanErr.toFixed(2)}}m</span>` +
      ` &nbsp; <span class="lbl" style="color:#0ff;">Weighted (centrality):</span> <span class="val">${{wErr.toFixed(2)}}m</span>` +
      ` &nbsp; <span class="lbl" style="color:#f0f;">Median:</span> <span class="val">${{medErr.toFixed(2)}}m</span>` +
      bestErrStr + smartErrStr + c10ErrStr +
      `<span class="lbl">${{errRefLabel}}</span>`;
  }}

  function drawMapBackground(ctx, W, H, cx, cy, meanLat, meanLon) {{
    if (!mapImg) return;
    // Map pixel (0,0) = (REF_LAT, REF_LON)
    // GPS->map pixel: px = (lon - REF_LON) * 111320 * cos(REF_LAT) / MAP_W_M * mapImgW
    //                 py = (REF_LAT - lat) * 111320 / MAP_W_M * mapImgW
    const mW = mapImg.naturalWidth;
    const mH = mapImg.naturalHeight;
    const pxPerMeter = mW / MAP_W_M;

    // Mean GPS -> map pixel
    const meanMapX = (meanLon - REF_LON) * 111320 * COS_REF * pxPerMeter / 1;  // but pxPerMeter is already mW/MAP_W_M
    const meanMapXc = (meanLon - REF_LON) * 111320 * COS_REF / MAP_W_M * mW;
    const meanMapYc = (REF_LAT - meanLat) * 111320 / MAP_W_M * mW;

    // View extent in meters
    const viewHalfW = (W / 2) / viewScale;
    const viewHalfH = (H / 2) / viewScale;

    // Source rect on map image (in map pixels)
    const srcCx = meanMapXc + viewCenterE * pxPerMeter;
    const srcCy = meanMapYc - viewCenterN * pxPerMeter;
    const srcHalfW = viewHalfW * pxPerMeter;
    const srcHalfH = viewHalfH * pxPerMeter;

    ctx.save();
    ctx.drawImage(mapImg,
      srcCx - srcHalfW, srcCy - srcHalfH, srcHalfW * 2, srcHalfH * 2,
      0, 0, W, H);
    // Dark overlay for readability
    ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
    ctx.fillRect(0, 0, W, H);
    ctx.restore();
  }}

  function autoGridStep(range) {{
    // Choose nice grid step for given visible range
    const candidates = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100];
    for (const c of candidates) {{
      if (range / c <= 12) return c;
    }}
    return 100;
  }}

  // ── Scatter interaction: zoom/pan ──
  scatterCvs.addEventListener("wheel", (e) => {{
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    zoomLevel = Math.max(0.1, Math.min(200, zoomLevel * factor));

    // Zoom towards mouse position
    const rect = scatterCvs.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const W = 500, H = 400;
    const cx = W / 2;
    const cy = H / 2;

    // Meters at mouse before zoom
    const oldScale = viewScale;
    const newScale = baseScale * zoomLevel;
    const meterE = (mx - cx) / oldScale + viewCenterE;
    const meterN = -(my - cy) / oldScale + viewCenterN;

    // Adjust center so mouse points to same meter coord
    viewCenterE = meterE - (mx - cx) / newScale;
    viewCenterN = meterN + (my - cy) / newScale;

    drawScatter();
  }}, {{ passive: false }});

  scatterCvs.addEventListener("mousedown", (e) => {{
    isDragging = true;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    dragStartCE = viewCenterE;
    dragStartCN = viewCenterN;
    scatterCvs.style.cursor = "grabbing";
  }});

  window.addEventListener("mousemove", (e) => {{
    if (!isDragging) return;
    const dx = e.clientX - dragStartX;
    const dy = e.clientY - dragStartY;
    viewCenterE = dragStartCE - dx / viewScale;
    viewCenterN = dragStartCN + dy / viewScale;
    drawScatter();
  }});

  window.addEventListener("mouseup", () => {{
    if (isDragging) {{
      isDragging = false;
      scatterCvs.style.cursor = "grab";
    }}
  }});

  // Click to inspect a dot
  scatterCvs.addEventListener("click", (e) => {{
    if (estimates.length === 0) return;
    const rect = scatterCvs.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const W = 500, H = 400;
    const cx = W / 2;

    let sumLat = 0, sumLon = 0;
    for (const est of estimates) {{ sumLat += est[0]; sumLon += est[1]; }}
    const clickMeanLat = sumLat / estimates.length;
    const clickMeanLon = sumLon / estimates.length;
    const clickOriginLat = groundTruth ? groundTruth.lat : clickMeanLat;
    const clickOriginLon = groundTruth ? groundTruth.lon : clickMeanLon;

    let closest = null, closestDist = Infinity;
    for (let i = 0; i < estimates.length; i++) {{
      const [em, nm] = gpsToMeters(estimates[i][0], estimates[i][1], clickOriginLat, clickOriginLon);
      const sx = cx + (em - viewCenterE) * viewScale;
      const sy = H / 2 - (nm - viewCenterN) * viewScale;
      const d = Math.sqrt((mx - sx) ** 2 + (my - sy) ** 2);
      if (d < closestDist) {{ closestDist = d; closest = i; }}
    }}

    if (closest !== null && closestDist < 15) {{
      const est = estimates[closest];
      tooltip.style.display = "block";
      tooltip.style.left = (e.clientX + 12) + "px";
      tooltip.style.top = (e.clientY - 10) + "px";
      const distM = (est[2] * est[3] / F_PX).toFixed(2);
      tooltip.textContent =
        `#${{closest + 1}}\\n` +
        `Lat: ${{est[0].toFixed(7)}}\\n` +
        `Lon: ${{est[1].toFixed(7)}}\\n` +
        `Alt: ${{est[3].toFixed(1)}}m\\n` +
        `Conf: ${{est[4].toFixed(3)}}\\n` +
        `CenterDist: ${{est[2].toFixed(0)}}px (${{distM}}m)`;
      // Auto-hide after 3 seconds
      setTimeout(() => {{ tooltip.style.display = "none"; }}, 3000);
    }} else {{
      tooltip.style.display = "none";
    }}
  }});

  // ── Error convergence chart ──
  function drawConvergence() {{
    const W = 500, H = 200;
    const ctx = convergeCtx;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#1a1a1a";
    ctx.fillRect(0, 0, W, H);

    const nPts = estimates.length;
    if (nPts < 2) {{
      ctx.fillStyle = "#555";
      ctx.font = "13px monospace";
      ctx.textAlign = "center";
      ctx.fillText("Error Convergence — need 2+ detections", W / 2, H / 2);
      ctx.textAlign = "start";
      return;
    }}

    // Title
    ctx.fillStyle = "#ccc";
    ctx.font = "11px monospace";
    ctx.fillText("ERROR CONVERGENCE", 50, 14);

    // Compute mean in meters
    let sumLat = 0, sumLon = 0;
    for (const e of estimates) {{ sumLat += e[0]; sumLon += e[1]; }}
    const cMeanLat = sumLat / nPts;
    const cMeanLon = sumLon / nPts;

    // Reference for convergence: ground truth if set, else final mean
    const refLat = groundTruth ? groundTruth.lat : cMeanLat;
    const refLon = groundTruth ? groundTruth.lon : cMeanLon;

    const pts = estimates.map(e => {{
      const [em, nm] = gpsToMeters(e[0], e[1], refLat, refLon);
      return {{ e: em, n: nm, pdist: e[2] }};
    }});

    // Final reference point (0,0 when using GT, final mean when not)
    const fmE = groundTruth ? 0 : pts.reduce((s, p) => s + p.e, 0) / nPts;
    const fmN = groundTruth ? 0 : pts.reduce((s, p) => s + p.n, 0) / nPts;

    const meanErrs = [], wErrs = [], medErrs = [];

    for (let k = 1; k <= nPts; k++) {{
      const sub = pts.slice(0, k);
      // Running mean
      const rmE = sub.reduce((s, p) => s + p.e, 0) / k;
      const rmN = sub.reduce((s, p) => s + p.n, 0) / k;
      meanErrs.push(Math.sqrt((rmE - fmE) ** 2 + (rmN - fmN) ** 2));

      // Running weighted (1/cdist^2)
      let wTot = 0, weE = 0, weN = 0;
      for (const p of sub) {{
        const cd = Math.max(p.pdist, 1);
        const w = 1 / (cd * cd);
        weE += p.e * w; weN += p.n * w; wTot += w;
      }}
      if (wTot > 0) {{ weE /= wTot; weN /= wTot; }}
      wErrs.push(Math.sqrt((weE - fmE) ** 2 + (weN - fmN) ** 2));

      // Running median
      const sE = sub.map(p => p.e).sort((a, b) => a - b);
      const sN = sub.map(p => p.n).sort((a, b) => a - b);
      const mE = sE[Math.floor(sE.length / 2)];
      const mN = sN[Math.floor(sN.length / 2)];
      medErrs.push(Math.sqrt((mE - fmE) ** 2 + (mN - fmN) ** 2));
    }}

    // Chart area
    const cl = 50, cr = W - 10, ct = 24, cb = H - 28;
    const cw = cr - cl, ch = cb - ct;

    const allErrs = meanErrs.concat(wErrs, medErrs);
    let yMax = Math.max(...allErrs, 0.5);

    // Grid
    ctx.strokeStyle = "#333";
    ctx.lineWidth = 0.5;
    ctx.fillStyle = "#666";
    ctx.font = "9px monospace";
    const ySteps = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50];
    for (const ym of ySteps) {{
      if (ym <= yMax) {{
        const gy = cb - (ym / yMax) * ch;
        ctx.beginPath(); ctx.moveTo(cl, gy); ctx.lineTo(cr, gy); ctx.stroke();
        ctx.fillText(ym.toFixed(ym < 1 ? 1 : 0) + "m", 4, gy + 3);
      }}
    }}

    // Axes
    ctx.strokeStyle = "#555";
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(cl, ct); ctx.lineTo(cl, cb); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cl, cb); ctx.lineTo(cr, cb); ctx.stroke();

    // Plot lines
    function plotLine(errs, color) {{
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      for (let i = 0; i < errs.length; i++) {{
        const x = cl + (i / Math.max(nPts - 1, 1)) * cw;
        const y = cb - (Math.min(errs[i], yMax) / yMax) * ch;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }}
      ctx.stroke();
    }}

    plotLine(meanErrs, "#ffdc00");
    plotLine(wErrs, "#00ffff");
    plotLine(medErrs, "#ff00ff");

    // Legend
    ctx.font = "10px monospace";
    const ly = H - 6;
    ctx.fillStyle = "#ffdc00"; ctx.fillText("+mean", cl, ly);
    ctx.fillStyle = "#00ffff"; ctx.fillText("\u25A0weighted", cl + 55, ly);
    ctx.fillStyle = "#ff00ff"; ctx.fillText("\u25C6median", cl + 135, ly);

    // X axis
    ctx.fillStyle = "#888";
    ctx.fillText("N=" + nPts, cr - 35, cb + 14);
    ctx.fillText("detection count", cl + cw / 2 - 40, cb + 14);
  }}

  // ── Tightest cluster algorithm (from video_test_compare.py) ──
  function findTightestCluster(ests, k) {{
    // For each seed point, find k nearest, return cluster with smallest max pairwise spread
    // If fewer than k points, return ALL points as the cluster
    if (ests.length <= k) {{
      const allIndices = ests.map((_, i) => i);
      if (ests.length < 2) return {{ indices: allIndices, spread: 0 }};
      let spread = 0;
      for (let i = 0; i < ests.length; i++) {{
        for (let j = i + 1; j < ests.length; j++) {{
          const dn = (ests[i][0] - ests[j][0]) * 111320;
          const de = (ests[i][1] - ests[j][1]) * 111320 * Math.cos(ests[i][0] * Math.PI / 180);
          const d = Math.sqrt(dn * dn + de * de);
          if (d > spread) spread = d;
        }}
      }}
      return {{ indices: allIndices, spread: spread }};
    }}
    let bestSpread = Infinity, bestIndices = [];
    for (let seed = 0; seed < ests.length; seed++) {{
      // Sort all points by distance from seed
      const dArr = ests.map((e, i) => {{
        const dn = (e[0] - ests[seed][0]) * 111320;
        const de = (e[1] - ests[seed][1]) * 111320 * Math.cos(ests[seed][0] * Math.PI / 180);
        return {{ i: i, d: Math.sqrt(dn * dn + de * de) }};
      }});
      dArr.sort((a, b) => a.d - b.d);
      const cluster = dArr.slice(0, k).map(x => x.i);
      // Compute spread (max pairwise distance)
      let spread = 0;
      for (let i = 0; i < cluster.length; i++) {{
        for (let j = i + 1; j < cluster.length; j++) {{
          const ci = ests[cluster[i]], cj = ests[cluster[j]];
          const dn = (ci[0] - cj[0]) * 111320;
          const de = (ci[1] - cj[1]) * 111320 * Math.cos(ci[0] * Math.PI / 180);
          const d = Math.sqrt(dn * dn + de * de);
          if (d > spread) spread = d;
        }}
      }}
      if (spread < bestSpread) {{ bestSpread = spread; bestIndices = cluster.slice(); }}
    }}
    return {{ indices: bestIndices, spread: bestSpread }};
  }}

  // ── Smart cluster mini-chart (continuously updated tightest-10) ──
  let smartLocked = false;
  let smartLockedIndices = null;
  let smartLockedSpread = Infinity;
  let SMART_LOCK_SPREAD = 0.75;  // meters — updated from server via /api/estimates-full
  let SMART_LOCK_COUNT = 10;     // min samples — updated from server

  function drawCluster() {{
    const W = 250, H = 300;
    const ctx = clusterCtx;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#1a1a1a";
    ctx.fillRect(0, 0, W, H);

    const margin = 30;
    const cx = W / 2, cy = H / 2 + 10;
    const nTotal = estimates.length;

    // Phase 1: fewer than 10 detections — show ALL dots numbered as they arrive
    if (nTotal < 10) {{
      ctx.fillStyle = "#ff8800";
      ctx.font = "bold 12px monospace";
      ctx.fillText("SMART CLUSTER", 8, 18);
      ctx.fillStyle = "#888";
      ctx.font = "11px monospace";
      const spreadInfo = nTotal >= 2 ? findTightestCluster(estimates, nTotal) : null;
      const spreadStr = spreadInfo ? "  spread: " + spreadInfo.spread.toFixed(1) + "m" : "";
      ctx.fillText("Gathering " + nTotal + "/10..." + spreadStr, 8, 33);

      // Show arriving dots with numbers
      if (nTotal > 0) {{
        let sLat = 0, sLon = 0;
        for (const e of estimates) {{ sLat += e[0]; sLon += e[1]; }}
        const mLat = sLat / nTotal, mLon = sLon / nTotal;
        const usable = Math.min(W, H) - 2 * margin;
        // Estimate scale from data
        let maxD = 0.5;
        for (const e of estimates) {{
          const [em, nm] = gpsToMeters(e[0], e[1], mLat, mLon);
          const d = Math.sqrt(em * em + nm * nm);
          if (d > maxD) maxD = d;
        }}
        const cScale = usable / (2 * Math.max(maxD * 1.5, 0.3));
        // Faint rings
        ctx.setLineDash([3, 3]);
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 0.5;
        for (const r of [0.2, 0.5, 1.0]) {{
          const rpx = r * cScale;
          if (rpx > 3 && rpx < usable) {{
            ctx.beginPath(); ctx.arc(cx, cy, rpx, 0, Math.PI * 2); ctx.stroke();
          }}
        }}
        ctx.setLineDash([]);
        // Numbered dots (cyan, same style as cluster phase)
        for (let i = 0; i < estimates.length; i++) {{
          const e = estimates[i];
          const [em, nm] = gpsToMeters(e[0], e[1], mLat, mLon);
          const sx = cx + em * cScale, sy = cy - nm * cScale;
          // Radial line from center
          ctx.strokeStyle = "#333";
          ctx.lineWidth = 0.5;
          ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(sx, sy); ctx.stroke();
          // Dot
          ctx.fillStyle = "#00ffff";
          ctx.beginPath(); ctx.arc(sx, sy, 5, 0, Math.PI * 2); ctx.fill();
          ctx.strokeStyle = "#fff";
          ctx.lineWidth = 1;
          ctx.beginPath(); ctx.arc(sx, sy, 5, 0, Math.PI * 2); ctx.stroke();
          // Number
          ctx.fillStyle = "#ccc";
          ctx.font = "9px monospace";
          ctx.fillText(String(i + 1), sx + 7, sy + 3);
        }}
      }}
      // Center cross
      ctx.strokeStyle = "#444";
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(cx - 8, cy); ctx.lineTo(cx + 8, cy); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx, cy - 8); ctx.lineTo(cx, cy + 8); ctx.stroke();
      ctx.fillStyle = "#888";
      ctx.font = "9px monospace";
      ctx.fillText("N=" + nTotal + "/" + SMART_LOCK_COUNT, 5, H - 5);
      return;
    }}

    // Sync lock state from server (reset when params change via /api/set-smart)
    if (smartData && !smartData.locked && smartLocked) {{
      smartLocked = false;
      smartLockedIndices = null;
      smartLockedSpread = Infinity;
    }}

    // Phase 2 & 3: use SERVER's locked cluster when available, else find locally
    let clusterIndices, clusterSpread;
    if (smartData && smartData.locked && smartData.cluster && smartData.cluster.length > 0) {{
      // Server has locked — use its cluster (authoritative, matches bullseye + SMART grid)
      smartLocked = true;
      smartLockedSpread = smartData.spread || 0;
      clusterSpread = smartLockedSpread;
      // Map server cluster to local estimate indices by matching lat/lon
      clusterIndices = [];
      for (const sc of smartData.cluster) {{
        let bestIdx = -1, bestDist = Infinity;
        for (let i = 0; i < estimates.length; i++) {{
          const d = Math.abs(estimates[i][0] - sc[0]) + Math.abs(estimates[i][1] - sc[1]);
          if (d < bestDist) {{ bestDist = d; bestIdx = i; }}
        }}
        if (bestIdx >= 0 && bestDist < 0.0001) clusterIndices.push(bestIdx);
      }}
      smartLockedIndices = clusterIndices.slice();
    }} else if (smartLocked && smartLockedIndices) {{
      clusterIndices = smartLockedIndices;
      clusterSpread = smartLockedSpread;
    }} else {{
      const result = findTightestCluster(estimates, SMART_LOCK_COUNT);
      clusterIndices = result.indices;
      clusterSpread = result.spread;
      // Local lock check (before server confirms)
      if (clusterSpread < SMART_LOCK_SPREAD && clusterIndices.length >= SMART_LOCK_COUNT) {{
        smartLocked = true;
        smartLockedIndices = clusterIndices.slice();
        smartLockedSpread = clusterSpread;
      }}
    }}

    const clusterSet = new Set(clusterIndices);
    const clusterEsts = clusterIndices.map(i => estimates[i]);
    const outlierEsts = estimates.filter((_, i) => !clusterSet.has(i));

    // Compute cluster mean
    let cSumLat = 0, cSumLon = 0;
    for (const c of clusterEsts) {{ cSumLat += c[0]; cSumLon += c[1]; }}
    const cMeanLat = cSumLat / clusterEsts.length;
    const cMeanLon = cSumLon / clusterEsts.length;

    // Convert to meters
    const cPts = clusterEsts.map(c => {{
      const [em, nm] = gpsToMeters(c[0], c[1], cMeanLat, cMeanLon);
      return {{ e: em, n: nm, pdist: c[2] || 0 }};
    }});
    const oPts = outlierEsts.map(c => {{
      const [em, nm] = gpsToMeters(c[0], c[1], cMeanLat, cMeanLon);
      return {{ e: em, n: nm }};
    }});

    // Scale to fit cluster with margin
    const cDists = cPts.map(p => Math.sqrt(p.e * p.e + p.n * p.n));
    const cMax = Math.max(...cDists) * 1.5 || 0.5;
    const usable = Math.min(W, H) - 2 * margin;
    const cScale = usable / (2 * Math.max(cMax, 0.3));

    // Header
    if (smartLocked) {{
      ctx.fillStyle = "#00ff00";
      ctx.font = "bold 12px monospace";
      ctx.fillText("LOCKED", 8, 18);
      ctx.fillStyle = "#0f0";
      ctx.font = "10px monospace";
      ctx.fillText("spread: " + clusterSpread.toFixed(2) + "m", 70, 18);
    }} else {{
      ctx.fillStyle = "#ff8800";
      ctx.font = "bold 12px monospace";
      ctx.fillText("FINDING CLUSTER...", 8, 18);
      ctx.fillStyle = "#888";
      ctx.font = "10px monospace";
      ctx.fillText("spread: " + clusterSpread.toFixed(2) + "m (need <" + SMART_LOCK_SPREAD.toFixed(1) + "m)", 8, 33);
      ctx.fillText(nTotal + " det, best " + SMART_LOCK_COUNT + " highlighted", 8, 46);
    }}

    // Fine rings: 0.1, 0.2, 0.5, 1.0m
    ctx.setLineDash([3, 3]);
    ctx.strokeStyle = "#444";
    ctx.lineWidth = 0.8;
    ctx.font = "8px monospace";
    ctx.fillStyle = "#555";
    for (const r of [0.1, 0.2, 0.5, 1.0]) {{
      const rpx = r * cScale;
      if (rpx > 3 && rpx < usable) {{
        ctx.beginPath();
        ctx.arc(cx, cy, rpx, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillText(r + "m", cx + rpx + 2, cy - 2);
      }}
    }}
    ctx.setLineDash([]);

    // Outlier X marks (dim, rejected from cluster)
    for (const p of oPts) {{
      const sx = cx + p.e * cScale, sy = cy - p.n * cScale;
      if (sx > 0 && sx < W && sy > 0 && sy < H) {{
        ctx.strokeStyle = "rgba(100,100,100,0.5)";
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(sx - 3, sy - 3); ctx.lineTo(sx + 3, sy + 3); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(sx + 3, sy - 3); ctx.lineTo(sx - 3, sy + 3); ctx.stroke();
      }}
    }}

    // Cluster dots with numbers and radial lines
    for (let i = 0; i < cPts.length; i++) {{
      const p = cPts[i];
      const sx = cx + p.e * cScale;
      const sy = cy - p.n * cScale;

      // Radial line from center
      ctx.strokeStyle = "#333";
      ctx.lineWidth = 0.5;
      ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(sx, sy); ctx.stroke();

      // Dot
      ctx.fillStyle = "#00ffff";
      ctx.beginPath(); ctx.arc(sx, sy, 5, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.arc(sx, sy, 5, 0, Math.PI * 2); ctx.stroke();

      // Number
      ctx.fillStyle = "#ccc";
      ctx.font = "9px monospace";
      ctx.fillText(String(i + 1), sx + 7, sy + 3);
    }}

    // Center cross (cyan)
    ctx.strokeStyle = "#00ffff";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(cx - 10, cy); ctx.lineTo(cx + 10, cy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx, cy - 10); ctx.lineTo(cx, cy + 10); ctx.stroke();

    // Median of cluster
    const sortedCE = cPts.map(p => p.e).sort((a, b) => a - b);
    const sortedCN = cPts.map(p => p.n).sort((a, b) => a - b);
    const medCE = sortedCE[Math.floor(sortedCE.length / 2)];
    const medCN = sortedCN[Math.floor(sortedCN.length / 2)];
    const medSx = cx + medCE * cScale, medSy = cy - medCN * cScale;
    // Magenta star for median (matches SMART star on satellite map)
    ctx.fillStyle = "#ff00ff";
    ctx.strokeStyle = "#ff00ff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let si = 0; si < 10; si++) {{
      const sr = (si % 2 === 0) ? 8 : 3;
      const sa = -Math.PI / 2 + (si * Math.PI / 5);
      const stx = medSx + sr * Math.cos(sa);
      const sty = medSy + sr * Math.sin(sa);
      if (si === 0) ctx.moveTo(stx, sty); else ctx.lineTo(stx, sty);
    }}
    ctx.closePath(); ctx.fill(); ctx.stroke();

    // Stats
    const medErr = Math.sqrt(medCE * medCE + medCN * medCN);
    ctx.fillStyle = "#aaa";
    ctx.font = "9px monospace";
    ctx.fillText("Total:" + nTotal + "  Cluster:10  Rejected:" + outlierEsts.length, 5, H - 18);
    ctx.fillText("Spread:" + clusterSpread.toFixed(2) + "m  Med err:" + medErr.toFixed(2) + "m", 5, H - 5);
  }}

  // ── Central Only (4m) bullseye chart ──
  const PX_THRESHOLD = 200;
  const CENTRAL_TARGET = 10;

  function drawCentral() {{
    const W = 250, H = 300;
    const ctx = centralCtx;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#1a1a1a";
    ctx.fillRect(0, 0, W, H);

    const margin = 30;
    const cx = W / 2, cy = H / 2 + 10;

    // Filter central detections (pixel_dist < PX_THRESHOLD)
    const centralAll = estimates.filter(e => e[2] < PX_THRESHOLD);
    const nCentral = centralAll.length;
    const nTotal = estimates.length;

    // Title
    ctx.fillStyle = "#ff00ff";
    ctx.font = "bold 12px monospace";
    ctx.fillText("CENTRAL (" + nCentral + "/" + CENTRAL_TARGET + ", <" + PX_THRESHOLD + "px)", 8, 18);

    if (nCentral === 0) {{
      ctx.fillStyle = "#555";
      ctx.font = "11px monospace";
      ctx.textAlign = "center";
      ctx.fillText("No central detections...", W / 2, H / 2);
      ctx.fillText("(need pdist < " + PX_THRESHOLD + "px)", W / 2, H / 2 + 18);
      ctx.textAlign = "start";
      ctx.fillStyle = "#888";
      ctx.font = "9px monospace";
      ctx.fillText("Total: " + nTotal + " | Central: 0", 5, H - 5);
      return;
    }}

    // Compute origin = mean of central set
    let sLat = 0, sLon = 0;
    for (const e of centralAll) {{ sLat += e[0]; sLon += e[1]; }}
    const mLat = sLat / nCentral, mLon = sLon / nCentral;

    // Convert to meters relative to central mean
    const cPts = centralAll.map(e => {{
      const [em, nm] = gpsToMeters(e[0], e[1], mLat, mLon);
      return {{ e: em, n: nm, pdist: e[2], alt: e[3], conf: e[4] }};
    }});

    // Scale: fit to 5m radius (bullseye max)
    const usable = Math.min(W, H) - 2 * margin;
    const maxRing = 5;
    const cScale = usable / (2 * maxRing);

    // Bullseye rings: 1, 2, 3, 5m
    ctx.setLineDash([3, 3]);
    ctx.strokeStyle = "#444";
    ctx.lineWidth = 0.8;
    ctx.font = "8px monospace";
    ctx.fillStyle = "#555";
    for (const r of [1, 2, 3, 5]) {{
      const rpx = r * cScale;
      if (rpx > 3 && rpx < usable) {{
        ctx.beginPath();
        ctx.arc(cx, cy, rpx, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillText(r + "m", cx + rpx + 2, cy - 2);
      }}
    }}
    ctx.setLineDash([]);

    // Center cross
    ctx.strokeStyle = "#444";
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(cx - 8, cy); ctx.lineTo(cx + 8, cy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx, cy - 8); ctx.lineTo(cx, cy + 8); ctx.stroke();

    // Color by centrality (green=most central i.e. lowest pdist, red=least)
    let minPd = Infinity, maxPd = 0;
    for (const p of cPts) {{
      if (p.pdist < minPd) minPd = p.pdist;
      if (p.pdist > maxPd) maxPd = p.pdist;
    }}
    const pdRange = Math.max(maxPd - minPd, 1);

    // Draw dots
    for (const p of cPts) {{
      const sx = cx + p.e * cScale, sy = cy - p.n * cScale;
      if (sx < -5 || sx > W + 5 || sy < -5 || sy > H + 5) continue;
      const val = (p.pdist - minPd) / pdRange;  // 0=green (most central), 1=red
      ctx.fillStyle = heatColor(val);
      ctx.beginPath(); ctx.arc(sx, sy, 3.5, 0, Math.PI * 2); ctx.fill();
    }}

    // Before 10 central: show searching message
    if (nCentral < CENTRAL_TARGET) {{
      ctx.fillStyle = "#ff00ff";
      ctx.font = "11px monospace";
      ctx.fillText(nCentral + "/" + CENTRAL_TARGET + " searching...", 8, 33);
    }} else {{
      // After 10: show median (magenta diamond) and weighted mean (cyan square)
      // Median
      const sortedE = cPts.map(p => p.e).sort((a, b) => a - b);
      const sortedN = cPts.map(p => p.n).sort((a, b) => a - b);
      const medE = sortedE[Math.floor(sortedE.length / 2)];
      const medN = sortedN[Math.floor(sortedN.length / 2)];
      const medSx = cx + medE * cScale, medSy = cy - medN * cScale;
      // Magenta star (matches SMART star style everywhere)
      ctx.fillStyle = "#ff00ff";
      ctx.strokeStyle = "#ff00ff";
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let si = 0; si < 10; si++) {{
        const sr = (si % 2 === 0) ? 7 : 3;
        const sa = -Math.PI / 2 + (si * Math.PI / 5);
        const stx = medSx + sr * Math.cos(sa);
        const sty = medSy + sr * Math.sin(sa);
        if (si === 0) ctx.moveTo(stx, sty); else ctx.lineTo(stx, sty);
      }}
      ctx.closePath(); ctx.fill(); ctx.stroke();

      // Weighted mean (1/pdist^2)
      let wE = 0, wN = 0, wTot = 0;
      for (const p of cPts) {{
        const cd = Math.max(p.pdist, 1);
        const w = 1 / (cd * cd);
        wE += p.e * w; wN += p.n * w; wTot += w;
      }}
      if (wTot > 0) {{ wE /= wTot; wN /= wTot; }}
      const wSx = cx + wE * cScale, wSy = cy - wN * cScale;
      // Cyan square
      ctx.strokeStyle = "#00ffff";
      ctx.lineWidth = 2;
      ctx.strokeRect(wSx - 5, wSy - 5, 10, 10);

      // Stats
      const medErr = Math.sqrt(medE * medE + medN * medN);
      const wErr = Math.sqrt(wE * wE + wN * wN);
      ctx.fillStyle = "#ff00ff";
      ctx.font = "9px monospace";
      ctx.fillText("Median err: " + medErr.toFixed(2) + "m", 5, H - 30);
      ctx.fillStyle = "#00ffff";
      ctx.fillText("Weighted err: " + wErr.toFixed(2) + "m", 5, H - 18);
    }}

    ctx.fillStyle = "#888";
    ctx.font = "9px monospace";
    ctx.fillText("Total:" + nTotal + " | Central:" + nCentral, 5, H - 5);
  }}

  // ── Data polling ──
  let animFrameId = null;
  let needsRedraw = false;

  function pollData() {{
    fetch("/api/estimates-full")
      .then(r => r.ok ? r.json() : null)
      .catch(() => null)
      .then(d => {{
        if (!d) return;
        estimates = d.estimates || [];
        smartData = d.smart || null;
        dronePos = d.drone || null;
        bestData = d.best || null;
        // Sync SMART cluster parameters from server
        if (d.smart_spread !== undefined) SMART_LOCK_SPREAD = d.smart_spread;
        if (d.smart_count !== undefined) SMART_LOCK_COUNT = d.smart_count;
        // Load ground truth from server if not set locally
        if (d.ground_truth && !groundTruth) {{
          groundTruth = d.ground_truth;
          document.getElementById("gt-input").value = groundTruth.lat.toFixed(7) + "," + groundTruth.lon.toFixed(7);
          document.getElementById("gt-input").style.borderColor = "#0f0";
          document.getElementById("gt-clear-btn").style.display = "inline";
        }}

        const hash = dataHash();
        if (hash !== prevDataHash) {{
          prevDataHash = hash;
          updateGlobalColorRange();
          updateFilterRanges();
          needsRedraw = true;
        }}
      }});
  }}

  function renderLoop() {{
    if (needsRedraw) {{
      needsRedraw = false;
      drawScatter();
      drawConvergence();
      drawCluster();
      drawCentral();
    }}
    animFrameId = requestAnimationFrame(renderLoop);
  }}

  // Poll every 1 second
  setInterval(pollData, 1000);
  pollData();

  // Start render loop
  renderLoop();

  // Initial draw
  drawScatter();
  drawConvergence();
  drawCluster();
  drawCentral();

}})();
</script>
'''
