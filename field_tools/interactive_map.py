"""
interactive_map.py — Interactive Canvas Map Component for Browser Dashboard

Provides get_interactive_map_html() which returns a complete HTML/CSS/JS string
for an interactive satellite map with:
  - Canvas overlay on static map image (loaded once)
  - Scroll-wheel zoom (centered on mouse)
  - Click+drag pan
  - Near-realtime drone position dot + heading arrow (500ms poll)
  - Camera FOV footprint rectangle rotated by yaw
  - GPS detection estimate dots (green)
  - Smart cluster median star marker (magenta)
  - Search area polygon overlay
  - Scale bar

Usage in passive_watch.py or pi_flight.py:
    from field_tools.interactive_map import get_interactive_map_html

    # In your HTML_PAGE string, replace the static <img id="map" src="/map">
    # with the div returned by get_interactive_map_html()

    # Add two API endpoints to your HTTP handler:
    #   /api/drone   → JSON with {lat, lon, alt, yaw, sats, mode}
    #   /api/estimates → JSON with {estimates: [[lat, lon], ...], smart: [lat, lon] or null}

Coordinate system:
    Map pixel (0,0) = top-left corner = (REF_LAT, REF_LON)
    px = (lon - REF_LON) * 111320 * cos(REF_LAT) / MAP_WIDTH_METERS * map_width_px
    py = (REF_LAT - lat) * 111320 / MAP_WIDTH_METERS * map_width_px
"""

import math
import json
import config


def get_map_constants():
    """Return map calibration constants for the JS client."""
    return {
        "REF_LAT": config.REF_LAT,
        "REF_LON": config.REF_LON,
        "MAP_WIDTH_METERS": config.MAP_WIDTH_METERS,
        "SENSOR_WIDTH_MM": config.SENSOR_WIDTH_MM,
        "FOCAL_LENGTH_MM": config.FOCAL_LENGTH_MM,
        "IMAGE_W": config.IMAGE_W,
        "IMAGE_H": config.IMAGE_H,
        "SEARCH_AREA_GPS": list(config.SEARCH_AREA_GPS),
        "FLIGHT_AREA_GPS": list(config.FLIGHT_AREA_GPS),
        "SSSI_GPS": list(config.SSSI_GPS),
        "TAKEOFF_GPS": list(config.TAKEOFF_GPS),
    }


def get_interactive_map_html(container_id="map-container", width="100%", height="400px"):
    """Return complete HTML + JS for the interactive map component.

    The returned string is a self-contained <div> with inline <style> and <script>.
    Drop it into any HTML page. Requires:
      - /map endpoint serving the static JPEG map image
      - /api/drone endpoint returning drone telemetry JSON
      - /api/estimates endpoint returning GPS estimates JSON
    """
    constants = get_map_constants()
    constants_json = json.dumps(constants)

    return f'''
<div id="{container_id}" style="width:{width}; height:{height}; position:relative; overflow:hidden; background:#111; border:1px solid #333; border-radius:4px;">
  <canvas id="imap-canvas" style="position:absolute; top:0; left:0; width:100%; height:100%; cursor:grab;"></canvas>
  <div id="imap-info" style="position:absolute; top:6px; left:6px; background:rgba(0,0,0,0.7); color:#0f0; font:11px monospace; padding:4px 8px; border-radius:3px; pointer-events:none; z-index:10;"></div>
  <div id="imap-zoom-info" style="position:absolute; bottom:6px; right:6px; background:rgba(0,0,0,0.7); color:#aaa; font:10px monospace; padding:3px 6px; border-radius:3px; pointer-events:none; z-index:10;"></div>
  <div style="position:absolute; top:6px; right:6px; display:flex; gap:4px; z-index:10;">
    <button id="imap-btn-coverage" style="background:rgba(0,180,0,0.8); color:#fff; border:none; font:10px monospace; padding:3px 7px; border-radius:3px; cursor:pointer;">Coverage: ON</button>
    <button id="imap-btn-clear-cov" style="background:rgba(120,120,120,0.8); color:#fff; border:none; font:10px monospace; padding:3px 7px; border-radius:3px; cursor:pointer;">Clear Coverage</button>
  </div>
</div>

<script>
(function() {{
  "use strict";

  // ── Config from Python ──
  const CFG = {constants_json};
  const REF_LAT = CFG.REF_LAT;
  const REF_LON = CFG.REF_LON;
  const MAP_W_M = CFG.MAP_WIDTH_METERS;
  const COS_REF = Math.cos(REF_LAT * Math.PI / 180);

  // ── Canvas setup ──
  const container = document.getElementById("{container_id}");
  const canvas = document.getElementById("imap-canvas");
  const ctx = canvas.getContext("2d");
  const infoEl = document.getElementById("imap-info");
  const zoomInfoEl = document.getElementById("imap-zoom-info");

  // High-DPI support
  function resizeCanvas() {{
    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = rect.width + "px";
    canvas.style.height = rect.height + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return {{ w: rect.width, h: rect.height }};
  }}
  let canvasSize = resizeCanvas();
  window.addEventListener("resize", function() {{
    canvasSize = resizeCanvas();
    requestRedraw();
  }});

  // ── Map image ──
  const mapImg = new Image();
  let mapLoaded = false;
  let mapW = 1, mapH = 1;  // natural pixel dimensions of map.jpg
  mapImg.onload = function() {{
    mapLoaded = true;
    mapW = mapImg.naturalWidth;
    mapH = mapImg.naturalHeight;
    // Initial fit: scale map to fill container
    fitMapToView();
    requestRedraw();
  }};
  mapImg.src = "/map?" + Date.now();

  // ── View transform: pan + zoom ──
  // viewX, viewY = top-left of viewport in map-pixel space
  // viewScale = how many screen pixels per map pixel
  let viewX = 0, viewY = 0, viewScale = 1;

  function fitMapToView() {{
    const scaleX = canvasSize.w / mapW;
    const scaleY = canvasSize.h / mapH;
    viewScale = Math.min(scaleX, scaleY);
    // Center the map
    viewX = -(canvasSize.w / viewScale - mapW) / 2;
    viewY = -(canvasSize.h / viewScale - mapH) / 2;
  }}

  // Screen coords <-> map pixel coords
  function screenToMap(sx, sy) {{
    return {{
      x: sx / viewScale + viewX,
      y: sy / viewScale + viewY
    }};
  }}
  function mapToScreen(mx, my) {{
    return {{
      x: (mx - viewX) * viewScale,
      y: (my - viewY) * viewScale
    }};
  }}

  // GPS <-> map pixel coords
  function gpsToMapPx(lat, lon) {{
    const dn = (REF_LAT - lat) * 111320;
    const de = (lon - REF_LON) * 111320 * COS_REF;
    const px = de / MAP_W_M * mapW;
    const py = dn / MAP_W_M * mapW;  // square pixels: use mapW for both
    return {{ x: px, y: py }};
  }}

  function gpsToScreen(lat, lon) {{
    const mp = gpsToMapPx(lat, lon);
    return mapToScreen(mp.x, mp.y);
  }}

  // ── State ──
  let drone = {{ lat: 0, lon: 0, alt: 0, yaw: 0, sats: 0, mode: "---" }};
  let estimates = [];       // [[lat, lon], ...]
  let smartMedian = null;   // [lat, lon] or null
  let needsRedraw = true;

  // ── Coverage trace ──
  let coverageHistory = [];   // array of [[lat,lon], [lat,lon], [lat,lon], [lat,lon]]
  let coverageEnabled = true;
  const COVERAGE_MAX = 2000;

  function computeFootprintCorners(lat, lon, alt, yaw) {{
    // Returns 4 GPS corners of the camera footprint, or null if invalid
    if (lat === 0 && lon === 0) return null;
    if (alt < 0.5) return null;

    const gndW = alt * CFG.SENSOR_WIDTH_MM / CFG.FOCAL_LENGTH_MM;
    const gndH = gndW * CFG.IMAGE_H / CFG.IMAGE_W;
    const hw = gndW / 2;
    const hh = gndH / 2;

    const yawRad = yaw * Math.PI / 180;
    const cosY = Math.cos(yawRad);
    const sinY = Math.sin(yawRad);

    const offsets = [
      [ hh, -hw],  // front-left
      [ hh,  hw],  // front-right
      [-hh,  hw],  // back-right
      [-hh, -hw],  // back-left
    ];

    const corners = [];
    for (let i = 0; i < 4; i++) {{
      const n = offsets[i][0];
      const e = offsets[i][1];
      const north_m = n * cosY - e * sinY;
      const east_m  = n * sinY + e * cosY;
      const dlat = north_m / 111320;
      const dlon = east_m / (111320 * COS_REF);
      corners.push([lat + dlat, lon + dlon]);
    }}
    return corners;
  }}

  function pushCoverage() {{
    if (!coverageEnabled) return;
    const corners = computeFootprintCorners(drone.lat, drone.lon, drone.alt, drone.yaw);
    if (!corners) return;
    coverageHistory.push(corners);
    if (coverageHistory.length > COVERAGE_MAX) {{
      coverageHistory = coverageHistory.slice(coverageHistory.length - COVERAGE_MAX);
    }}
  }}

  function requestRedraw() {{ needsRedraw = true; }}

  // ── Mouse interaction ──
  let isPanning = false;
  let panStartX = 0, panStartY = 0;
  let panStartViewX = 0, panStartViewY = 0;

  canvas.addEventListener("mousedown", function(e) {{
    if (e.button === 0) {{
      isPanning = true;
      panStartX = e.clientX;
      panStartY = e.clientY;
      panStartViewX = viewX;
      panStartViewY = viewY;
      canvas.style.cursor = "grabbing";
      e.preventDefault();
    }}
  }});

  window.addEventListener("mousemove", function(e) {{
    if (isPanning) {{
      const dx = e.clientX - panStartX;
      const dy = e.clientY - panStartY;
      viewX = panStartViewX - dx / viewScale;
      viewY = panStartViewY - dy / viewScale;
      requestRedraw();
    }}
  }});

  window.addEventListener("mouseup", function(e) {{
    if (e.button === 0 && isPanning) {{
      isPanning = false;
      canvas.style.cursor = "grab";
    }}
  }});

  // Zoom centered on mouse
  canvas.addEventListener("wheel", function(e) {{
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    // Map point under mouse before zoom
    const before = screenToMap(mx, my);

    const zoomFactor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    const newScale = viewScale * zoomFactor;

    // Clamp zoom: min = fit-to-view, max = 20x native
    const minScale = Math.min(canvasSize.w / mapW, canvasSize.h / mapH) * 0.5;
    const maxScale = 20;
    viewScale = Math.max(minScale, Math.min(maxScale, newScale));

    // Adjust pan so the point under mouse stays fixed
    viewX = before.x - mx / viewScale;
    viewY = before.y - my / viewScale;

    requestRedraw();
  }}, {{ passive: false }});

  // Double-click to reset view
  canvas.addEventListener("dblclick", function(e) {{
    e.preventDefault();
    fitMapToView();
    requestRedraw();
  }});

  // ── Drawing functions ──

  function drawMapImage() {{
    if (!mapLoaded) return;
    const tl = mapToScreen(0, 0);
    const br = mapToScreen(mapW, mapH);
    ctx.drawImage(mapImg, tl.x, tl.y, br.x - tl.x, br.y - tl.y);
  }}

  function drawPolygon(gpsPoints, strokeColor, fillColor, lineWidth) {{
    if (!gpsPoints || gpsPoints.length < 2) return;
    ctx.beginPath();
    for (let i = 0; i < gpsPoints.length; i++) {{
      const p = gpsToScreen(gpsPoints[i][0], gpsPoints[i][1]);
      if (i === 0) ctx.moveTo(p.x, p.y);
      else ctx.lineTo(p.x, p.y);
    }}
    ctx.closePath();
    if (fillColor) {{
      ctx.fillStyle = fillColor;
      ctx.fill();
    }}
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = lineWidth || 1.5;
    ctx.stroke();
  }}

  function drawZones() {{
    // Flight area (blue, thin)
    drawPolygon(CFG.FLIGHT_AREA_GPS, "rgba(0,150,255,0.6)", "rgba(0,150,255,0.05)", 1);
    // SSSI no-fly zone (red)
    drawPolygon(CFG.SSSI_GPS, "rgba(255,50,50,0.8)", "rgba(255,0,0,0.08)", 1.5);
    // Search area (yellow)
    drawPolygon(CFG.SEARCH_AREA_GPS, "rgba(255,255,0,0.8)", "rgba(255,255,0,0.06)", 2);

    // Takeoff marker
    const tp = gpsToScreen(CFG.TAKEOFF_GPS[0], CFG.TAKEOFF_GPS[1]);
    ctx.beginPath();
    ctx.arc(tp.x, tp.y, 4, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(255,255,255,0.8)";
    ctx.fill();
    ctx.strokeStyle = "#00f";
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = "#fff";
    ctx.font = "9px monospace";
    ctx.fillText("H", tp.x - 3, tp.y + 3);
  }}

  function drawCoverage() {{
    if (!coverageEnabled || coverageHistory.length === 0) return;
    ctx.fillStyle = "rgba(80,160,255,0.06)";
    for (let c = 0; c < coverageHistory.length; c++) {{
      const corners = coverageHistory[c];
      ctx.beginPath();
      for (let i = 0; i < 4; i++) {{
        const sp = gpsToScreen(corners[i][0], corners[i][1]);
        if (i === 0) ctx.moveTo(sp.x, sp.y);
        else ctx.lineTo(sp.x, sp.y);
      }}
      ctx.closePath();
      ctx.fill();
    }}
  }}

  function drawDrone() {{
    if (drone.lat === 0 && drone.lon === 0) return;

    const p = gpsToScreen(drone.lat, drone.lon);
    const r = Math.max(5, 8 * viewScale);

    // Drone dot (blue filled)
    ctx.beginPath();
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(0,120,255,0.85)";
    ctx.fill();
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Heading arrow — yaw=0 is North, positive clockwise
    const yawRad = drone.yaw * Math.PI / 180;
    const arrowLen = r * 2.5;
    const ax = p.x + Math.sin(yawRad) * arrowLen;
    const ay = p.y - Math.cos(yawRad) * arrowLen;

    ctx.beginPath();
    ctx.moveTo(p.x, p.y);
    ctx.lineTo(ax, ay);
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Arrowhead
    const headLen = r * 1.2;
    const headAngle = 0.4;
    ctx.beginPath();
    ctx.moveTo(ax, ay);
    ctx.lineTo(
      ax - headLen * Math.sin(yawRad - headAngle),
      ay + headLen * Math.cos(yawRad - headAngle)
    );
    ctx.moveTo(ax, ay);
    ctx.lineTo(
      ax - headLen * Math.sin(yawRad + headAngle),
      ay + headLen * Math.cos(yawRad + headAngle)
    );
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 2;
    ctx.stroke();
  }}

  function drawFootprint() {{
    // Camera FOV rectangle on the ground, rotated by yaw
    if (drone.lat === 0 && drone.lon === 0) return;
    if (drone.alt < 0.5) return;

    const alt = drone.alt;
    // Ground coverage in meters
    const gndW = alt * CFG.SENSOR_WIDTH_MM / CFG.FOCAL_LENGTH_MM;
    const gndH = gndW * CFG.IMAGE_H / CFG.IMAGE_W;

    // Half-sizes in meters
    const hw = gndW / 2;
    const hh = gndH / 2;

    // Four corners relative to drone, rotated by yaw (clockwise from North)
    // Camera looks straight down: rectangle hw x hh on ground
    // At yaw=0 (North): front=+North, right=+East
    const yawRad = drone.yaw * Math.PI / 180;
    const cosY = Math.cos(yawRad);
    const sinY = Math.sin(yawRad);

    // Corner offsets in meters (north, east) before rotation
    // north = +lat (when yaw=0), east = +lon (when yaw=0)
    const corners = [
      [ hh, -hw],  // front-left  (forward, left)
      [ hh,  hw],  // front-right (forward, right)
      [-hh,  hw],  // back-right  (behind, right)
      [-hh, -hw],  // back-left   (behind, left)
    ];

    ctx.beginPath();
    for (let i = 0; i < 4; i++) {{
      const n = corners[i][0];  // north component
      const e = corners[i][1];  // east component
      // Clockwise rotation by yaw (compass convention: 0=N, 90=E)
      const north_m = n * cosY - e * sinY;
      const east_m  = n * sinY + e * cosY;

      // Convert meter offset to GPS offset
      const dlat = north_m / 111320;
      const dlon = east_m / (111320 * COS_REF);
      const sp = gpsToScreen(drone.lat + dlat, drone.lon + dlon);

      if (i === 0) ctx.moveTo(sp.x, sp.y);
      else ctx.lineTo(sp.x, sp.y);
    }}
    ctx.closePath();
    ctx.fillStyle = "rgba(0,255,200,0.1)";
    ctx.fill();
    ctx.strokeStyle = "rgba(0,255,200,0.6)";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 3]);
    ctx.stroke();
    ctx.setLineDash([]);
  }}

  function drawEstimates() {{
    if (estimates.length === 0) return;

    const dotR = Math.max(2, 3 * viewScale);

    for (let i = 0; i < estimates.length; i++) {{
      const p = gpsToScreen(estimates[i][0], estimates[i][1]);
      // Skip if off-screen
      if (p.x < -10 || p.x > canvasSize.w + 10 || p.y < -10 || p.y > canvasSize.h + 10) continue;

      ctx.beginPath();
      ctx.arc(p.x, p.y, dotR, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(0,255,80,0.7)";
      ctx.fill();
      ctx.strokeStyle = "rgba(0,255,80,0.3)";
      ctx.lineWidth = 0.5;
      ctx.stroke();
    }}

    // Smart cluster median star
    if (smartMedian) {{
      const sp = gpsToScreen(smartMedian[0], smartMedian[1]);
      drawStar(sp.x, sp.y, 5, 10, 5, "rgba(255,0,255,0.9)", "rgba(255,0,255,0.4)");
      // Label
      ctx.fillStyle = "#f0f";
      ctx.font = "bold 10px monospace";
      ctx.fillText("SMART", sp.x + 12, sp.y + 4);
    }}
  }}

  function drawStar(cx, cy, spikes, outerR, innerR, stroke, fill) {{
    let rot = -Math.PI / 2;
    const step = Math.PI / spikes;
    ctx.beginPath();
    for (let i = 0; i < spikes * 2; i++) {{
      const r = i % 2 === 0 ? outerR : innerR;
      const x = cx + Math.cos(rot + step * i) * r;
      const y = cy + Math.sin(rot + step * i) * r;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }}
    ctx.closePath();
    if (fill) {{ ctx.fillStyle = fill; ctx.fill(); }}
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 2;
    ctx.stroke();
  }}

  function drawScaleBar() {{
    // Bottom-left scale bar
    const margin = 15;
    const barY = canvasSize.h - margin;

    // Determine a nice round distance for the bar
    // How many meters does 100 screen pixels represent?
    const metersPerPx = MAP_W_M / (mapW * viewScale);
    const rawMeters = metersPerPx * 120;

    // Pick the nearest "nice" distance
    const niceDistances = [1, 2, 5, 10, 20, 50, 100, 200, 500];
    let dist = niceDistances[0];
    for (let i = niceDistances.length - 1; i >= 0; i--) {{
      if (niceDistances[i] <= rawMeters * 1.2) {{ dist = niceDistances[i]; break; }}
    }}

    const barPx = dist / metersPerPx;
    const x0 = margin;
    const x1 = margin + barPx;

    // Draw bar
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x0, barY);
    ctx.lineTo(x1, barY);
    // End ticks
    ctx.moveTo(x0, barY - 5);
    ctx.lineTo(x0, barY + 2);
    ctx.moveTo(x1, barY - 5);
    ctx.lineTo(x1, barY + 2);
    ctx.stroke();

    // Background for text
    const label = dist >= 1000 ? (dist / 1000) + " km" : dist + " m";
    ctx.font = "bold 10px monospace";
    const tw = ctx.measureText(label).width;
    const tx = x0 + (barPx - tw) / 2;
    ctx.fillStyle = "rgba(0,0,0,0.6)";
    ctx.fillRect(tx - 2, barY - 16, tw + 4, 13);
    ctx.fillStyle = "#fff";
    ctx.fillText(label, tx, barY - 6);
  }}

  // ── Main render loop ──
  function render() {{
    if (!needsRedraw) {{
      requestAnimationFrame(render);
      return;
    }}
    needsRedraw = false;

    // Clear
    ctx.clearRect(0, 0, canvasSize.w, canvasSize.h);

    // Background
    ctx.fillStyle = "#111";
    ctx.fillRect(0, 0, canvasSize.w, canvasSize.h);

    // Map image
    drawMapImage();

    // Zone overlays
    drawZones();

    // Coverage trace (below everything else)
    drawCoverage();

    // GPS estimate dots
    drawEstimates();

    // Camera footprint
    drawFootprint();

    // Drone marker (on top)
    drawDrone();

    // Scale bar (screen space, always visible)
    drawScaleBar();

    // Info overlay
    updateInfo();

    requestAnimationFrame(render);
  }}

  function updateInfo() {{
    const parts = [];
    if (drone.lat !== 0 || drone.lon !== 0) {{
      parts.push(`${{drone.lat.toFixed(6)}}, ${{drone.lon.toFixed(6)}}`);
      parts.push(`Alt:${{drone.alt.toFixed(1)}}m  Sats:${{drone.sats}}  ${{drone.mode}}`);
    }} else {{
      parts.push("No GPS");
    }}
    if (estimates.length > 0) {{
      parts.push(`${{estimates.length}} detections`);
    }}
    if (coverageEnabled && coverageHistory.length > 0) {{
      parts.push(`Cov:${{coverageHistory.length}}`);
    }}
    infoEl.textContent = parts.join(" | ");

    const zoom = (viewScale * mapW / canvasSize.w * 100).toFixed(0);
    zoomInfoEl.textContent = `${{zoom}}% | dblclick=reset`;
  }}

  // ── Coverage buttons ──
  const btnCoverage = document.getElementById("imap-btn-coverage");
  const btnClearCov = document.getElementById("imap-btn-clear-cov");

  btnCoverage.addEventListener("click", function() {{
    coverageEnabled = !coverageEnabled;
    btnCoverage.textContent = "Coverage: " + (coverageEnabled ? "ON" : "OFF");
    btnCoverage.style.background = coverageEnabled ? "rgba(0,180,0,0.8)" : "rgba(120,120,120,0.8)";
    requestRedraw();
  }});

  btnClearCov.addEventListener("click", function() {{
    coverageHistory = [];
    requestRedraw();
  }});

  // ── Data polling ──
  let pollDroneTimer = null;
  let pollEstTimer = null;

  function pollDrone() {{
    fetch("/api/drone").then(r => r.json()).then(d => {{
      let changed = false;
      if (d.lat !== drone.lat || d.lon !== drone.lon || d.yaw !== drone.yaw || d.alt !== drone.alt) {{
        changed = true;
      }}
      drone.lat = d.lat || 0;
      drone.lon = d.lon || 0;
      drone.alt = d.alt || 0;
      drone.yaw = d.yaw || 0;
      drone.sats = d.sats || 0;
      drone.mode = d.mode || "---";
      if (changed) {{
        pushCoverage();
        requestRedraw();
      }}
    }}).catch(function() {{}});
  }}

  function pollEstimates() {{
    fetch("/api/estimates").then(r => r.json()).then(d => {{
      const newEst = d.estimates || [];
      const newSmart = d.smart || null;
      // Only redraw if data changed
      if (newEst.length !== estimates.length || newSmart !== smartMedian) {{
        estimates = newEst;
        smartMedian = newSmart;
        requestRedraw();
      }}
    }}).catch(function() {{}});
  }}

  // Start polling
  pollDroneTimer = setInterval(pollDrone, 500);
  pollEstTimer = setInterval(pollEstimates, 2000);

  // Initial polls
  pollDrone();
  pollEstimates();

  // Start render loop
  requestAnimationFrame(render);

}})();
</script>
'''


def get_api_drone_handler(gps_data, gps_lock):
    """Return a function that produces drone telemetry JSON.

    Args:
        gps_data: dict with lat, lon, alt, yaw, sats, mode keys
        gps_lock: threading.Lock protecting gps_data

    Returns:
        bytes: JSON-encoded drone state
    """
    import json
    with gps_lock:
        d = {
            "lat": gps_data.get("lat", 0),
            "lon": gps_data.get("lon", 0),
            "alt": gps_data.get("alt", 0),
            "yaw": gps_data.get("yaw", 0),
            "sats": gps_data.get("sats", 0),
            "mode": gps_data.get("mode", "---"),
        }
    return json.dumps(d).encode()


def get_api_estimates_handler(all_estimates, smart_estimator=None):
    """Return JSON bytes for /api/estimates endpoint.

    Args:
        all_estimates: list of (lat, lon, pixel_dist) tuples
        smart_estimator: SmartEstimator instance or None

    Returns:
        bytes: JSON-encoded estimates
    """
    import json
    est_list = [[e[0], e[1]] for e in all_estimates]
    smart = None
    if smart_estimator and smart_estimator.locked:
        med = smart_estimator.get_median()
        if med:
            smart = [med[0], med[1]]
    return json.dumps({"estimates": est_list, "smart": smart}).encode()
