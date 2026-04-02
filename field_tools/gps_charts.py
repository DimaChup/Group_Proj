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
        <button id="btn-color-alt" class="active" data-mode="altitude">Altitude</button>
        <button id="btn-color-cent" data-mode="centrality">Centrality</button>
        <button id="btn-color-conf" data-mode="confidence">Confidence</button>
        <div class="sep"></div>
        <button id="btn-map-bg">Map BG: off</button>
        <div class="sep"></div>
        <button id="btn-reset-view">Reset View</button>
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

  <!-- Right column: smart cluster -->
  <div class="gps-chart-col">
    <div class="gps-chart-panel" style="width:250px;">
      <canvas id="cluster-canvas" width="250" height="300"></canvas>
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
  let prevDataHash = "";
  let colorMode = "altitude";   // altitude | centrality | confidence
  let mapBgOn = false;
  let mapImg = null;
  let mapLoading = false;

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

  // ── Color mode buttons ──
  document.querySelectorAll("#scatter-toolbar button[data-mode]").forEach(btn => {{
    btn.addEventListener("click", () => {{
      colorMode = btn.dataset.mode;
      document.querySelectorAll("#scatter-toolbar button[data-mode]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
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

  document.getElementById("btn-reset-view").addEventListener("click", () => {{
    viewCenterE = 0;
    viewCenterN = 0;
    zoomLevel = 1;
    drawScatter();
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
    return estimates.length + ":" + (smartData ? (smartData.locked ? "L" : "S") + (smartData.cluster ? smartData.cluster.length : 0) : "X");
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

    // Compute mean
    let sumLat = 0, sumLon = 0;
    for (const e of estimates) {{ sumLat += e[0]; sumLon += e[1]; }}
    const meanLat = sumLat / estimates.length;
    const meanLon = sumLon / estimates.length;

    // Convert all to meters relative to mean
    const pts = estimates.map((e, i) => {{
      const [em, nm] = gpsToMeters(e[0], e[1], meanLat, meanLon);
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
      drawMapBackground(ctx, W, H, cx, cy, meanLat, meanLon);
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

    // Color values
    let minAlt = Infinity, maxAlt = -Infinity, maxPd = 0, minConf = 1, maxConf = 0;
    for (const p of pts) {{
      if (p.alt < minAlt) minAlt = p.alt;
      if (p.alt > maxAlt) maxAlt = p.alt;
      if (p.pdist > maxPd) maxPd = p.pdist;
      if (p.conf < minConf) minConf = p.conf;
      if (p.conf > maxConf) maxConf = p.conf;
    }}
    const altRange = Math.max(maxAlt - minAlt, 0.1);
    maxPd = Math.max(maxPd, 1);
    const confRange = Math.max(maxConf - minConf, 0.01);

    // Draw dots
    for (const p of pts) {{
      const sx = cx + (p.e - viewCenterE) * viewScale;
      const sy = cy - (p.n - viewCenterN) * viewScale;
      if (sx < -10 || sx > W + 10 || sy < -10 || sy > H + 10) continue;

      let val = 0;
      if (colorMode === "altitude") val = (p.alt - minAlt) / altRange;
      else if (colorMode === "centrality") val = Math.min(1, p.pdist / maxPd);
      else if (colorMode === "confidence") val = 1 - (p.conf - minConf) / confRange;

      ctx.fillStyle = heatColor(val);
      ctx.beginPath();
      ctx.arc(sx, sy, 3.5, 0, Math.PI * 2);
      ctx.fill();
    }}

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

    // Mean marker (green cross)
    const msx = cx + (0 - viewCenterE) * viewScale;
    const msy = cy - (0 - viewCenterN) * viewScale;
    ctx.strokeStyle = "#00ff00";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(msx - 8, msy); ctx.lineTo(msx + 8, msy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(msx, msy - 8); ctx.lineTo(msx, msy + 8); ctx.stroke();

    // Weighted mean marker (cyan diamond)
    const wsx = cx + (wE - viewCenterE) * viewScale;
    const wsy = cy - (wN - viewCenterN) * viewScale;
    ctx.strokeStyle = "#00ffff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(wsx, wsy - 7); ctx.lineTo(wsx + 5, wsy);
    ctx.lineTo(wsx, wsy + 7); ctx.lineTo(wsx - 5, wsy);
    ctx.closePath(); ctx.stroke();

    // Median marker (magenta diamond)
    const medsx = cx + (medE - viewCenterE) * viewScale;
    const medsy = cy - (medN - viewCenterN) * viewScale;
    ctx.strokeStyle = "#ff00ff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(medsx, medsy - 7); ctx.lineTo(medsx + 5, medsy);
    ctx.lineTo(medsx, medsy + 7); ctx.lineTo(medsx - 5, medsy);
    ctx.closePath(); ctx.stroke();

    // Stats
    const cep50 = dists[Math.floor(dists.length / 2)] || 0;
    const maxSpread = dists[dists.length - 1] || 0;
    const meanErr = 0;  // mean is origin
    const wErr = Math.sqrt(wE * wE + wN * wN);
    const medErr = Math.sqrt(medE * medE + medN * medN);

    statsEl.innerHTML =
      `<span class="lbl">N:</span> <span class="val">${{estimates.length}}</span>` +
      ` &nbsp; <span class="lbl">CEP50:</span> <span class="val">${{cep50.toFixed(2)}}m</span>` +
      ` &nbsp; <span class="lbl">Max:</span> <span class="val">${{maxSpread.toFixed(2)}}m</span>` +
      `<br><span class="lbl">Mean err:</span> <span class="val">0.00m</span>` +
      ` &nbsp; <span class="lbl" style="color:#0ff;">Weighted:</span> <span class="val">${{wErr.toFixed(2)}}m</span>` +
      ` &nbsp; <span class="lbl" style="color:#f0f;">Median:</span> <span class="val">${{medErr.toFixed(2)}}m</span>` +
      ` &nbsp; <span class="lbl">GPS:</span> <span class="val">${{meanLat.toFixed(7)}}, ${{meanLon.toFixed(7)}}</span>`;
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
    const meanLat = sumLat / estimates.length;
    const meanLon = sumLon / estimates.length;

    let closest = null, closestDist = Infinity;
    for (let i = 0; i < estimates.length; i++) {{
      const [em, nm] = gpsToMeters(estimates[i][0], estimates[i][1], meanLat, meanLon);
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
      tooltip.textContent =
        `#${{closest + 1}}\\n` +
        `Lat: ${{est[0].toFixed(7)}}\\n` +
        `Lon: ${{est[1].toFixed(7)}}\\n` +
        `Alt: ${{est[3].toFixed(1)}}m\\n` +
        `Conf: ${{est[4].toFixed(3)}}\\n` +
        `CenterDist: ${{est[2].toFixed(0)}}px`;
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
    const meanLat = sumLat / nPts;
    const meanLon = sumLon / nPts;

    const pts = estimates.map(e => {{
      const [em, nm] = gpsToMeters(e[0], e[1], meanLat, meanLon);
      return {{ e: em, n: nm, pdist: e[2] }};
    }});

    // Final mean (reference point)
    const fmE = pts.reduce((s, p) => s + p.e, 0) / nPts;
    const fmN = pts.reduce((s, p) => s + p.n, 0) / nPts;

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

    plotLine(meanErrs, "#00ff00");
    plotLine(wErrs, "#00ffff");
    plotLine(medErrs, "#ff00ff");

    // Legend
    ctx.font = "10px monospace";
    const ly = H - 6;
    ctx.fillStyle = "#00ff00"; ctx.fillText("mean", cl, ly);
    ctx.fillStyle = "#00ffff"; ctx.fillText("weighted", cl + 50, ly);
    ctx.fillStyle = "#ff00ff"; ctx.fillText("median", cl + 120, ly);

    // X axis
    ctx.fillStyle = "#888";
    ctx.fillText("N=" + nPts, cr - 35, cb + 14);
    ctx.fillText("detection count", cl + cw / 2 - 40, cb + 14);
  }}

  // ── Smart cluster mini-chart ──
  function drawCluster() {{
    const W = 250, H = 300;
    const ctx = clusterCtx;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#1a1a1a";
    ctx.fillRect(0, 0, W, H);

    if (!smartData) {{
      ctx.fillStyle = "#555";
      ctx.font = "12px monospace";
      ctx.textAlign = "center";
      ctx.fillText("Smart Cluster", W / 2, H / 2 - 10);
      ctx.fillText("(not active)", W / 2, H / 2 + 10);
      ctx.textAlign = "start";
      return;
    }}

    const margin = 30;
    const cx = W / 2, cy = H / 2 + 10;

    if (smartData.locked && smartData.cluster && smartData.cluster.length > 0) {{
      // LOCKED header
      ctx.fillStyle = "#00ff00";
      ctx.font = "bold 13px monospace";
      ctx.fillText("LOCKED", 8, 18);
      ctx.fillStyle = "#0f0";
      ctx.font = "10px monospace";
      ctx.fillText("spread: " + (smartData.spread || 0).toFixed(2) + "m", 80, 18);

      const cluster = smartData.cluster;
      // Compute mean of cluster
      let cSumLat = 0, cSumLon = 0;
      for (const c of cluster) {{ cSumLat += c[0]; cSumLon += c[1]; }}
      const cMeanLat = cSumLat / cluster.length;
      const cMeanLon = cSumLon / cluster.length;

      const cPts = cluster.map(c => {{
        const [em, nm] = gpsToMeters(c[0], c[1], cMeanLat, cMeanLon);
        return {{ e: em, n: nm, pdist: c[2] || 0 }};
      }});

      const cDists = cPts.map(p => Math.sqrt(p.e * p.e + p.n * p.n));
      const cMax = Math.max(...cDists) * 1.5 || 0.5;
      const usable = Math.min(W, H) - 2 * margin;
      const cScale = usable / (2 * Math.max(cMax, 0.3));

      // Rings: 0.1, 0.2, 0.5, 1.0m
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

      // Center cross (cyan)
      ctx.strokeStyle = "#00ffff";
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(cx - 10, cy); ctx.lineTo(cx + 10, cy); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx, cy - 10); ctx.lineTo(cx, cy + 10); ctx.stroke();

      // Dots with numbers
      for (let i = 0; i < cPts.length; i++) {{
        const p = cPts[i];
        const sx = cx + p.e * cScale;
        const sy = cy - p.n * cScale;

        // Radial line
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

      // Median info
      if (smartData.median) {{
        ctx.fillStyle = "#ff00ff";
        ctx.font = "9px monospace";
        ctx.fillText("Med: " + smartData.median[0].toFixed(7) + ", " + smartData.median[1].toFixed(7), 5, H - 18);
      }}
      ctx.fillStyle = "#aaa";
      ctx.font = "9px monospace";
      ctx.fillText("N=" + cluster.length + "  spread=" + (smartData.spread || 0).toFixed(2) + "m", 5, H - 5);

    }} else {{
      // Searching
      ctx.fillStyle = "#ff00ff";
      ctx.font = "bold 13px monospace";
      ctx.fillText("searching...", 8, 18);
      ctx.fillStyle = "#888";
      ctx.font = "11px monospace";
      ctx.fillText("Waiting for tightest", 8, 45);
      ctx.fillText("cluster to lock", 8, 62);

      // Empty rings for visual reference
      ctx.setLineDash([3, 3]);
      ctx.strokeStyle = "#333";
      ctx.lineWidth = 0.5;
      for (const r of [0.2, 0.5, 1.0]) {{
        const rpx = r * 80;
        ctx.beginPath(); ctx.arc(cx, cy, rpx, 0, Math.PI * 2); ctx.stroke();
      }}
      ctx.setLineDash([]);

      // Center cross
      ctx.strokeStyle = "#444";
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(cx - 8, cy); ctx.lineTo(cx + 8, cy); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx, cy - 8); ctx.lineTo(cx, cy + 8); ctx.stroke();
    }}
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

        const hash = dataHash();
        if (hash !== prevDataHash) {{
          prevDataHash = hash;
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

}})();
</script>
'''
