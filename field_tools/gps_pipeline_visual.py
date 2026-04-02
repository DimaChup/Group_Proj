"""
gps_pipeline_visual.py -- Interactive GPS Estimation Pipeline Visualization

Returns a self-contained HTML/CSS/JS string showing how pixel detection
coordinates are converted to real-world GPS positions.

Usage:
    from field_tools.gps_pipeline_visual import get_gps_pipeline_html
    html = get_gps_pipeline_html()

Exposes JS function:
    updateGPSData({alt, fov_deg, ground_w, ground_h, f_px})
"""

import math
import config


def get_gps_pipeline_html():
    """Return HTML string for GPS estimation pipeline visualization."""

    # Compute defaults from config
    f_px_default = config.FOCAL_LENGTH_MM * config.IMAGE_W / config.SENSOR_WIDTH_MM
    default_alt = config.TARGET_ALT
    fov_deg = 2 * math.degrees(math.atan(config.IMAGE_W / (2 * f_px_default)))
    ground_w = default_alt * config.IMAGE_W / f_px_default
    ground_h = default_alt * config.IMAGE_H / f_px_default

    return f'''
<div id="gps-pipeline" style="font-family:'Segoe UI',system-ui,sans-serif; background:#111; color:#ccc; padding:24px; border-radius:8px; max-width:1100px; margin:0 auto;">

  <h2 style="text-align:center; color:#0ff; margin:0 0 4px 0; font-size:22px; letter-spacing:1px;">GPS Position Estimation Pipeline</h2>
  <p style="text-align:center; color:#888; margin:0 0 20px 0; font-size:13px;">Pixel Detection &rarr; Ground Coordinates &rarr; GPS Position</p>

  <!-- ── Controls ── -->
  <div style="display:flex; gap:24px; justify-content:center; flex-wrap:wrap; margin-bottom:20px;">
    <label style="display:flex; align-items:center; gap:8px; font-size:13px; color:#aaa;">
      Altitude (m)
      <input type="range" id="gps-alt-slider" min="5" max="60" value="{default_alt:.0f}" step="1"
             style="width:120px; accent-color:#0ff;">
      <span id="gps-alt-val" style="color:#0ff; font-weight:bold; min-width:32px;">{default_alt:.0f}</span>
    </label>
    <label style="display:flex; align-items:center; gap:8px; font-size:13px; color:#aaa;">
      Detection X (px)
      <input type="range" id="gps-cx-slider" min="0" max="{config.IMAGE_W}" value="900" step="1"
             style="width:120px; accent-color:#f0f;">
      <span id="gps-cx-val" style="color:#f0f; font-weight:bold; min-width:40px;">900</span>
    </label>
    <label style="display:flex; align-items:center; gap:8px; font-size:13px; color:#aaa;">
      Detection Y (px)
      <input type="range" id="gps-cy-slider" min="0" max="{config.IMAGE_H}" value="350" step="1"
             style="width:120px; accent-color:#f0f;">
      <span id="gps-cy-val" style="color:#f0f; font-weight:bold; min-width:40px;">350</span>
    </label>
    <label style="display:flex; align-items:center; gap:8px; font-size:13px; color:#aaa;">
      Yaw (&deg;)
      <input type="range" id="gps-yaw-slider" min="0" max="359" value="45" step="1"
             style="width:120px; accent-color:#ff0;">
      <span id="gps-yaw-val" style="color:#ff0; font-weight:bold; min-width:32px;">45</span>
    </label>
  </div>

  <!-- ── Main Layout: SVG diagrams + Steps ── -->
  <div style="display:flex; gap:20px; flex-wrap:wrap;">

    <!-- LEFT: Camera Geometry SVG -->
    <div style="flex:1; min-width:420px;">
      <div style="background:#0a0a0a; border:1px solid #333; border-radius:6px; padding:12px;">
        <h3 style="color:#0ff; margin:0 0 8px 0; font-size:14px; text-align:center;">Camera Projection Geometry</h3>
        <svg id="gps-geom-svg" viewBox="0 0 440 340" style="width:100%; height:auto;">
          <!-- Sky gradient -->
          <defs>
            <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#0a0a2e"/>
              <stop offset="100%" stop-color="#111"/>
            </linearGradient>
            <linearGradient id="groundGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#1a2a1a"/>
              <stop offset="100%" stop-color="#0d1a0d"/>
            </linearGradient>
            <marker id="arrowG" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <path d="M0,0 L8,3 L0,6" fill="#0f0" stroke="none"/>
            </marker>
            <marker id="arrowC" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <path d="M0,0 L8,3 L0,6" fill="#0ff" stroke="none"/>
            </marker>
            <marker id="arrowM" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <path d="M0,0 L8,3 L0,6" fill="#f0f" stroke="none"/>
            </marker>
          </defs>
          <!-- Background -->
          <rect x="0" y="0" width="440" height="200" fill="url(#skyGrad)"/>
          <rect x="0" y="200" width="440" height="140" fill="url(#groundGrad)"/>
          <line x1="0" y1="200" x2="440" y2="200" stroke="#2a4a2a" stroke-width="2"/>

          <!-- Drone body -->
          <g id="gps-drone-g">
            <rect x="205" y="42" width="30" height="12" rx="3" fill="#444" stroke="#0ff" stroke-width="1"/>
            <circle cx="220" cy="48" r="3" fill="#0ff"/>
            <!-- Propeller arms -->
            <line x1="208" y1="48" x2="195" y2="40" stroke="#555" stroke-width="1.5"/>
            <line x1="232" y1="48" x2="245" y2="40" stroke="#555" stroke-width="1.5"/>
            <circle cx="195" cy="40" r="4" fill="none" stroke="#666" stroke-width="1"/>
            <circle cx="245" cy="40" r="4" fill="none" stroke="#666" stroke-width="1"/>
          </g>

          <!-- Altitude line -->
          <line x1="220" y1="54" x2="220" y2="200" stroke="#0ff" stroke-width="1" stroke-dasharray="4,3" opacity="0.6"/>
          <text id="gps-alt-label" x="228" y="130" fill="#0ff" font-size="11" font-family="monospace">30.0 m</text>

          <!-- FOV cone -->
          <polygon id="gps-fov-cone" points="220,54 100,200 340,200" fill="rgba(0,255,255,0.04)" stroke="#0ff" stroke-width="1" stroke-dasharray="6,4" opacity="0.5"/>

          <!-- Ground coverage bar -->
          <line id="gps-ground-bar" x1="100" y1="206" x2="340" y2="206" stroke="#0f0" stroke-width="2"/>
          <line id="gps-ground-left" x1="100" y1="200" x2="100" y2="212" stroke="#0f0" stroke-width="1"/>
          <line id="gps-ground-right" x1="340" y1="200" x2="340" y2="212" stroke="#0f0" stroke-width="1"/>
          <text id="gps-ground-label" x="220" y="224" fill="#0f0" font-size="11" font-family="monospace" text-anchor="middle">26.8 x 20.0 m</text>

          <!-- Center projection line -->
          <line x1="220" y1="200" x2="220" y2="212" stroke="#555" stroke-width="1" stroke-dasharray="2,2"/>

          <!-- Detection point on ground -->
          <circle id="gps-det-ground" cx="260" cy="200" r="5" fill="#f0f" stroke="#fff" stroke-width="1"/>

          <!-- Detection projection ray -->
          <line id="gps-det-ray" x1="220" y1="54" x2="260" y2="200" stroke="#f0f" stroke-width="1" stroke-dasharray="3,3" opacity="0.7"/>

          <!-- Offset arrows -->
          <line id="gps-dx-line" x1="220" y1="195" x2="260" y2="195" stroke="#f0f" stroke-width="1.5" marker-end="url(#arrowM)"/>
          <text id="gps-dx-label" x="240" y="190" fill="#f0f" font-size="10" font-family="monospace" text-anchor="middle">dx</text>

          <!-- Frame preview inset -->
          <rect x="310" y="10" width="120" height="90" rx="3" fill="#0a0a0a" stroke="#333" stroke-width="1"/>
          <text x="370" y="24" fill="#888" font-size="9" font-family="monospace" text-anchor="middle">Camera View</text>
          <!-- Frame crosshair -->
          <line x1="370" y1="30" x2="370" y2="95" stroke="#333" stroke-width="0.5"/>
          <line x1="315" y1="60" x2="425" y2="60" stroke="#333" stroke-width="0.5"/>
          <!-- Frame center dot -->
          <circle cx="370" cy="60" r="2" fill="#0ff" opacity="0.5"/>
          <!-- Detection dot in frame -->
          <circle id="gps-det-frame" cx="384" cy="47" r="4" fill="#f0f" stroke="#fff" stroke-width="1"/>
          <!-- Offset lines in frame -->
          <line id="gps-frame-dx" x1="370" y1="60" x2="384" y2="60" stroke="#f0f" stroke-width="1" opacity="0.6"/>
          <line id="gps-frame-dy" x1="384" y1="60" x2="384" y2="47" stroke="#f0f" stroke-width="1" opacity="0.6"/>
          <text x="315" y="105" fill="#555" font-size="8" font-family="monospace">{config.IMAGE_W}x{config.IMAGE_H}</text>

          <!-- Legend -->
          <g transform="translate(10, 260)">
            <circle cx="8" cy="0" r="3" fill="#0ff"/>
            <text x="16" y="4" fill="#aaa" font-size="9" font-family="monospace">Drone nadir</text>
            <circle cx="8" cy="16" r="3" fill="#f0f"/>
            <text x="16" y="20" fill="#aaa" font-size="9" font-family="monospace">Detection</text>
            <line x1="2" y1="30" x2="14" y2="30" stroke="#0f0" stroke-width="2"/>
            <text x="16" y="34" fill="#aaa" font-size="9" font-family="monospace">Ground coverage</text>
          </g>

          <!-- Focal length annotation -->
          <text id="gps-fpx-label" x="180" y="72" fill="#888" font-size="9" font-family="monospace">f = 1584 px</text>
        </svg>
      </div>

      <!-- Yaw Rotation Compass -->
      <div style="background:#0a0a0a; border:1px solid #333; border-radius:6px; padding:12px; margin-top:12px;">
        <h3 style="color:#ff0; margin:0 0 8px 0; font-size:14px; text-align:center;">Step 4: Yaw Rotation</h3>
        <svg id="gps-compass-svg" viewBox="0 0 260 260" style="width:100%; max-width:260px; height:auto; display:block; margin:0 auto;">
          <defs>
            <marker id="arrN" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto">
              <path d="M0,0 L7,2.5 L0,5" fill="#888" stroke="none"/>
            </marker>
          </defs>
          <!-- Compass ring -->
          <circle cx="130" cy="130" r="100" fill="none" stroke="#333" stroke-width="1"/>
          <circle cx="130" cy="130" r="60" fill="none" stroke="#222" stroke-width="0.5" stroke-dasharray="3,3"/>
          <!-- Cardinal labels -->
          <text x="130" y="20" fill="#888" font-size="12" font-family="monospace" text-anchor="middle">N</text>
          <text x="240" y="134" fill="#888" font-size="12" font-family="monospace" text-anchor="middle">E</text>
          <text x="130" y="248" fill="#888" font-size="12" font-family="monospace" text-anchor="middle">S</text>
          <text x="20" y="134" fill="#888" font-size="12" font-family="monospace" text-anchor="middle">W</text>
          <!-- Tick marks -->
          <line x1="130" y1="32" x2="130" y2="40" stroke="#555" stroke-width="1"/>
          <line x1="228" y1="130" x2="220" y2="130" stroke="#555" stroke-width="1"/>
          <line x1="130" y1="228" x2="130" y2="220" stroke="#555" stroke-width="1"/>
          <line x1="32" y1="130" x2="40" y2="130" stroke="#555" stroke-width="1"/>

          <!-- Body frame axes (rotate with yaw) -->
          <g id="gps-body-axes" transform="rotate(45,130,130)">
            <!-- Forward (body) -->
            <line x1="130" y1="130" x2="130" y2="50" stroke="#0ff" stroke-width="2" marker-end="url(#arrowC)"/>
            <text x="138" y="58" fill="#0ff" font-size="10" font-family="monospace">fwd</text>
            <!-- Right (body) -->
            <line x1="130" y1="130" x2="210" y2="130" stroke="#f0f" stroke-width="2" marker-end="url(#arrowM)"/>
            <text x="198" y="124" fill="#f0f" font-size="10" font-family="monospace">right</text>
          </g>

          <!-- World frame axes (fixed) -->
          <line x1="130" y1="130" x2="130" y2="45" stroke="#888" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrN)"/>
          <line x1="130" y1="130" x2="215" y2="130" stroke="#888" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrN)"/>

          <!-- Yaw arc -->
          <path id="gps-yaw-arc" d="" fill="none" stroke="#ff0" stroke-width="2"/>
          <text id="gps-yaw-label" x="160" y="90" fill="#ff0" font-size="11" font-family="monospace">45&deg;</text>

          <!-- Detection vector (world frame) -->
          <line id="gps-world-vec" x1="130" y1="130" x2="180" y2="80" stroke="#0f0" stroke-width="2" stroke-dasharray="5,3"/>
          <circle id="gps-world-dot" cx="180" cy="80" r="4" fill="#0f0" stroke="#fff" stroke-width="1"/>
          <text id="gps-world-label" x="185" y="76" fill="#0f0" font-size="9" font-family="monospace">GPS offset</text>

          <!-- Center dot -->
          <circle cx="130" cy="130" r="3" fill="#fff"/>
        </svg>
      </div>

      <!-- Calibration Reference Card -->
      <div style="background:#0a0a0a; border:1px solid #333; border-radius:6px; padding:12px; margin-top:12px;">
        <h3 style="color:#0f0; margin:0 0 10px 0; font-size:14px; text-align:center;">Calibration Reference</h3>
        <table style="width:100%; border-collapse:collapse; font-family:monospace; font-size:12px;">
          <thead>
            <tr style="border-bottom:1px solid #444;">
              <th style="text-align:left; padding:4px 6px; color:#888;">Alt</th>
              <th style="text-align:right; padding:4px 6px; color:#888;">Coverage</th>
              <th style="text-align:right; padding:4px 6px; color:#888;">GSD</th>
              <th style="text-align:right; padding:4px 6px; color:#888;">Dummy</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom:1px solid #222;">
              <td style="padding:3px 6px; color:#0ff;">1 m</td>
              <td style="padding:3px 6px; color:#ddd; text-align:right;" id="gps-cal-cov1">0.92 x 0.69 m</td>
              <td style="padding:3px 6px; color:#ddd; text-align:right;" id="gps-cal-gsd1">0.63 mm</td>
              <td style="padding:3px 6px; color:#f0f; text-align:right;" id="gps-cal-dum1">2854 px</td>
            </tr>
            <tr style="border-bottom:1px solid #222;">
              <td style="padding:3px 6px; color:#0ff;">10 m</td>
              <td style="padding:3px 6px; color:#ddd; text-align:right;" id="gps-cal-cov10">9.2 x 6.9 m</td>
              <td style="padding:3px 6px; color:#ddd; text-align:right;" id="gps-cal-gsd10">6.3 mm</td>
              <td style="padding:3px 6px; color:#f0f; text-align:right;" id="gps-cal-dum10">285 px</td>
            </tr>
            <tr style="border-bottom:1px solid #222;">
              <td style="padding:3px 6px; color:#0ff;">30 m</td>
              <td style="padding:3px 6px; color:#ddd; text-align:right;" id="gps-cal-cov30">27.6 x 20.6 m</td>
              <td style="padding:3px 6px; color:#ddd; text-align:right;" id="gps-cal-gsd30">19.0 mm</td>
              <td style="padding:3px 6px; color:#f0f; text-align:right;" id="gps-cal-dum30">95 px</td>
            </tr>
            <tr style="background:#111; border-top:1px solid #0ff;">
              <td style="padding:4px 6px; color:#0ff; font-weight:bold;" id="gps-cal-altcur">35 m</td>
              <td style="padding:4px 6px; color:#0ff; text-align:right; font-weight:bold;" id="gps-cal-covcur">32.2 x 24.0 m</td>
              <td style="padding:4px 6px; color:#0ff; text-align:right; font-weight:bold;" id="gps-cal-gsdcur">22.1 mm</td>
              <td style="padding:4px 6px; color:#f0f; text-align:right; font-weight:bold;" id="gps-cal-dumcur">81 px</td>
            </tr>
          </tbody>
        </table>
        <div style="margin-top:8px; font-size:11px; color:#666; line-height:1.6; padding-left:4px;">
          Aspect ratio: <span style="color:#aaa;">4:3</span> ({config.IMAGE_W}x{config.IMAGE_H})<br>
          Sensor: <span style="color:#aaa;">{config.SENSOR_WIDTH_MM} mm</span> &nbsp; Focal: <span style="color:#aaa;">{config.FOCAL_LENGTH_MM} mm</span><br>
          Dummy height: <span style="color:#f0f;">1.8 m</span> &nbsp; GSD = ground_w / {config.IMAGE_W}
        </div>
      </div>
    </div>

    <!-- RIGHT: Step-by-step equations -->
    <div style="flex:1; min-width:380px; display:flex; flex-direction:column; gap:12px;">

      <!-- Step 1 -->
      <div class="gps-step" style="background:#0a0a0a; border:1px solid #333; border-radius:6px; padding:12px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
          <span style="background:#0ff; color:#000; font-weight:bold; font-size:12px; padding:2px 8px; border-radius:10px;">1</span>
          <span style="color:#0ff; font-size:14px; font-weight:600;">Pixel Offset from Centre</span>
        </div>
        <div style="font-family:monospace; font-size:13px; line-height:1.8; color:#ddd; padding-left:8px;">
          centre = ({config.IMAGE_W//2}, {config.IMAGE_H//2})<br>
          dx<sub>px</sub> = cx &minus; {config.IMAGE_W//2} = <span id="gps-s1-dx" style="color:#f0f;">172</span> px<br>
          dy<sub>px</sub> = cy &minus; {config.IMAGE_H//2} = <span id="gps-s1-dy" style="color:#f0f;">&minus;194</span> px
        </div>
        <div style="font-size:11px; color:#666; margin-top:4px; padding-left:8px;">+dx = right in image, +dy = down in image (behind drone)</div>
      </div>

      <!-- Step 2 -->
      <div class="gps-step" style="background:#0a0a0a; border:1px solid #333; border-radius:6px; padding:12px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
          <span style="background:#0ff; color:#000; font-weight:bold; font-size:12px; padding:2px 8px; border-radius:10px;">2</span>
          <span style="color:#0ff; font-size:14px; font-weight:600;">Pixels to Ground Metres</span>
        </div>
        <div style="font-family:monospace; font-size:13px; line-height:1.8; color:#ddd; padding-left:8px;">
          f<sub>px</sub> = {config.FOCAL_LENGTH_MM} &times; {config.IMAGE_W} / {config.SENSOR_WIDTH_MM} = <span id="gps-s2-fpx" style="color:#0ff;">{f_px_default:.0f}</span> px<br>
          dx<sub>m</sub> = dx<sub>px</sub> &times; alt / f<sub>px</sub> = <span id="gps-s2-dxm" style="color:#0f0;">3.26</span> m<br>
          dy<sub>m</sub> = dy<sub>px</sub> &times; alt / f<sub>px</sub> = <span id="gps-s2-dym" style="color:#0f0;">&minus;3.67</span> m
        </div>
        <div style="font-size:11px; color:#666; margin-top:4px; padding-left:8px;">
          Higher altitude &rarr; each pixel covers more ground.<br>
          At <span id="gps-s2-alt" style="color:#0ff;">30</span>m: 1 px = <span id="gps-s2-scale" style="color:#0ff;">0.019</span> m
        </div>
      </div>

      <!-- Step 3 -->
      <div class="gps-step" style="background:#0a0a0a; border:1px solid #333; border-radius:6px; padding:12px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
          <span style="background:#0ff; color:#000; font-weight:bold; font-size:12px; padding:2px 8px; border-radius:10px;">3</span>
          <span style="color:#0ff; font-size:14px; font-weight:600;">Body Frame Mapping</span>
        </div>
        <div style="font-family:monospace; font-size:13px; line-height:1.8; color:#ddd; padding-left:8px;">
          forward<sub>m</sub> = &minus;dy<sub>m</sub> = <span id="gps-s3-fwd" style="color:#0ff;">3.67</span> m<br>
          right<sub>m</sub> = dx<sub>m</sub> = <span id="gps-s3-rgt" style="color:#f0f;">3.26</span> m
        </div>
        <div style="font-size:11px; color:#666; margin-top:4px; padding-left:8px;">Image &minus;Y (up) = body forward, image +X (right) = body right</div>
      </div>

      <!-- Step 4 -->
      <div class="gps-step" style="background:#0a0a0a; border:1px solid #333; border-radius:6px; padding:12px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
          <span style="background:#ff0; color:#000; font-weight:bold; font-size:12px; padding:2px 8px; border-radius:10px;">4</span>
          <span style="color:#ff0; font-size:14px; font-weight:600;">Rotate by Drone Yaw</span>
        </div>
        <div style="font-family:monospace; font-size:13px; line-height:1.8; color:#ddd; padding-left:8px;">
          north<sub>m</sub> = fwd&middot;cos(&psi;) &minus; rgt&middot;sin(&psi;) = <span id="gps-s4-north" style="color:#0f0;">0.29</span> m<br>
          east<sub>m</sub> = fwd&middot;sin(&psi;) + rgt&middot;cos(&psi;) = <span id="gps-s4-east" style="color:#0f0;">4.90</span> m
        </div>
        <div style="font-size:11px; color:#666; margin-top:4px; padding-left:8px;">
          &psi; = <span id="gps-s4-yaw">45</span>&deg; (clockwise from North)
        </div>
      </div>

      <!-- Step 5 -->
      <div class="gps-step" style="background:#0a0a0a; border:1px solid #333; border-radius:6px; padding:12px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
          <span style="background:#0f0; color:#000; font-weight:bold; font-size:12px; padding:2px 8px; border-radius:10px;">5</span>
          <span style="color:#0f0; font-size:14px; font-weight:600;">Metres to GPS Offset</span>
        </div>
        <div style="font-family:monospace; font-size:13px; line-height:1.8; color:#ddd; padding-left:8px;">
          est_lat = drone_lat + north / 111320<br>
          est_lon = drone_lon + east / (111320 &times; cos(lat))
        </div>
        <div style="font-size:11px; color:#666; margin-top:4px; padding-left:8px;">
          1&deg; lat &asymp; 111320 m everywhere. 1&deg; lon shrinks with cos(lat).
        </div>
      </div>

      <!-- Step 6 -->
      <div class="gps-step" style="background:#0a0a0a; border:1px solid #333; border-radius:6px; padding:12px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
          <span style="background:#0f0; color:#000; font-weight:bold; font-size:12px; padding:2px 8px; border-radius:10px;">6</span>
          <span style="color:#0f0; font-size:14px; font-weight:600;">Weighted Accumulation</span>
        </div>
        <div style="font-family:monospace; font-size:13px; line-height:1.8; color:#ddd; padding-left:8px;">
          w = 1 / alt&sup2; &times; centrality<br>
          centrality = 1 + 4 &times; (1 &minus; r/r<sub>max</sub>)
        </div>
        <div style="font-size:11px; color:#666; margin-top:4px; padding-left:8px;">
          At <span id="gps-s6-alt1">10</span>m: weight = <span id="gps-s6-w1" style="color:#0f0;">0.0100</span><br>
          At <span id="gps-s6-alt2">30</span>m: weight = <span id="gps-s6-w2" style="color:#888;">0.0011</span>
          &nbsp;&mdash;&nbsp;<span id="gps-s6-ratio" style="color:#ff0;">9.0</span>&times; less valuable
        </div>
      </div>

      <!-- Summary card -->
      <div style="background:linear-gradient(135deg, #0a1a0a, #0a0a1a); border:1px solid #0f0; border-radius:6px; padding:14px; text-align:center;">
        <div style="font-size:13px; color:#888; margin-bottom:4px;">Ground Offset from Drone</div>
        <div style="font-family:monospace; font-size:20px;">
          <span style="color:#0f0;" id="gps-summary-north">+0.29</span> m N &nbsp;
          <span style="color:#0f0;" id="gps-summary-east">+4.90</span> m E
        </div>
        <div style="font-size:12px; color:#888; margin-top:4px;">
          Distance: <span id="gps-summary-dist" style="color:#ff0;">4.91</span> m &nbsp;
          Bearing: <span id="gps-summary-brg" style="color:#ff0;">86.6</span>&deg;
        </div>
        <div style="font-size:12px; color:#555; margin-top:6px;">
          Weight at current alt: <span id="gps-summary-weight" style="color:#0ff;">0.0011</span>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
(function() {{
  "use strict";

  const IMG_W = {config.IMAGE_W};
  const IMG_H = {config.IMAGE_H};
  const CX_CENTER = IMG_W / 2;
  const CY_CENTER = IMG_H / 2;
  const SENSOR_W = {config.SENSOR_WIDTH_MM};
  const FOCAL_MM = {config.FOCAL_LENGTH_MM};

  const f_px = FOCAL_MM * IMG_W / SENSOR_W;

  // DOM elements
  const altSlider = document.getElementById('gps-alt-slider');
  const cxSlider  = document.getElementById('gps-cx-slider');
  const cySlider  = document.getElementById('gps-cy-slider');
  const yawSlider = document.getElementById('gps-yaw-slider');

  function recalc() {{
    const alt = parseFloat(altSlider.value);
    const cx  = parseFloat(cxSlider.value);
    const cy  = parseFloat(cySlider.value);
    const yaw_deg = parseFloat(yawSlider.value);
    const yaw_rad = yaw_deg * Math.PI / 180;

    // Display slider values
    document.getElementById('gps-alt-val').textContent = alt.toFixed(0);
    document.getElementById('gps-cx-val').textContent = cx.toFixed(0);
    document.getElementById('gps-cy-val').textContent = cy.toFixed(0);
    document.getElementById('gps-yaw-val').textContent = yaw_deg.toFixed(0);

    // Step 1: pixel offset
    const dx_px = cx - CX_CENTER;
    const dy_px = cy - CY_CENTER;
    document.getElementById('gps-s1-dx').textContent = dx_px.toFixed(0);
    document.getElementById('gps-s1-dy').textContent = dy_px.toFixed(0);

    // Step 2: pixels to meters
    const dx_m = dx_px * alt / f_px;
    const dy_m = dy_px * alt / f_px;
    const scale = alt / f_px;
    document.getElementById('gps-s2-fpx').textContent = f_px.toFixed(0);
    document.getElementById('gps-s2-dxm').textContent = dx_m.toFixed(2);
    document.getElementById('gps-s2-dym').textContent = dy_m.toFixed(2);
    document.getElementById('gps-s2-alt').textContent = alt.toFixed(0);
    document.getElementById('gps-s2-scale').textContent = scale.toFixed(3);

    // Step 3: body frame
    const fwd_m = -dy_m;
    const rgt_m = dx_m;
    document.getElementById('gps-s3-fwd').textContent = fwd_m.toFixed(2);
    document.getElementById('gps-s3-rgt').textContent = rgt_m.toFixed(2);

    // Step 4: yaw rotation
    const north_m = fwd_m * Math.cos(yaw_rad) - rgt_m * Math.sin(yaw_rad);
    const east_m  = fwd_m * Math.sin(yaw_rad) + rgt_m * Math.cos(yaw_rad);
    document.getElementById('gps-s4-north').textContent = north_m.toFixed(2);
    document.getElementById('gps-s4-east').textContent = east_m.toFixed(2);
    document.getElementById('gps-s4-yaw').textContent = yaw_deg.toFixed(0);

    // Step 6: weighting
    const r = Math.sqrt(dx_px*dx_px + dy_px*dy_px);
    const r_max = Math.sqrt(CX_CENTER*CX_CENTER + CY_CENTER*CY_CENTER);
    const centrality = 1 + 4 * Math.max(0, 1 - r / r_max);
    const w = centrality / (alt * alt);
    const w10 = 5 / (10 * 10);  // center weight at 10m
    const w30 = 1 / (30 * 30);  // edge weight at 30m

    document.getElementById('gps-s6-alt1').textContent = '10';
    document.getElementById('gps-s6-w1').textContent = w10.toFixed(4);
    document.getElementById('gps-s6-alt2').textContent = alt.toFixed(0);
    document.getElementById('gps-s6-w2').textContent = w.toFixed(4);
    document.getElementById('gps-s6-ratio').textContent = (w10 / Math.max(w, 0.00001)).toFixed(1);

    // Summary
    const dist = Math.sqrt(north_m*north_m + east_m*east_m);
    const brg = (Math.atan2(east_m, north_m) * 180 / Math.PI + 360) % 360;
    document.getElementById('gps-summary-north').textContent = (north_m >= 0 ? '+' : '') + north_m.toFixed(2);
    document.getElementById('gps-summary-east').textContent = (east_m >= 0 ? '+' : '') + east_m.toFixed(2);
    document.getElementById('gps-summary-dist').textContent = dist.toFixed(2);
    document.getElementById('gps-summary-brg').textContent = brg.toFixed(1);
    document.getElementById('gps-summary-weight').textContent = w.toFixed(4);

    // ── Update Calibration Reference Card ──
    const DUMMY_H = 1.8;
    function calRef(a) {{
      const gw = a * SENSOR_W / FOCAL_MM;
      const gh = gw * IMG_H / IMG_W;
      const gsd = gw / IMG_W;
      const dum = DUMMY_H / gsd;
      return {{ gw, gh, gsd, dum }};
    }}
    const c1 = calRef(1), c10 = calRef(10), c30 = calRef(30), cCur = calRef(alt);
    document.getElementById('gps-cal-cov1').textContent = c1.gw.toFixed(2) + ' x ' + c1.gh.toFixed(2) + ' m';
    document.getElementById('gps-cal-gsd1').textContent = (c1.gsd * 1000).toFixed(2) + ' mm';
    document.getElementById('gps-cal-dum1').textContent = c1.dum.toFixed(0) + ' px';
    document.getElementById('gps-cal-cov10').textContent = c10.gw.toFixed(1) + ' x ' + c10.gh.toFixed(1) + ' m';
    document.getElementById('gps-cal-gsd10').textContent = (c10.gsd * 1000).toFixed(1) + ' mm';
    document.getElementById('gps-cal-dum10').textContent = c10.dum.toFixed(0) + ' px';
    document.getElementById('gps-cal-cov30').textContent = c30.gw.toFixed(1) + ' x ' + c30.gh.toFixed(1) + ' m';
    document.getElementById('gps-cal-gsd30').textContent = (c30.gsd * 1000).toFixed(1) + ' mm';
    document.getElementById('gps-cal-dum30').textContent = c30.dum.toFixed(0) + ' px';
    document.getElementById('gps-cal-altcur').textContent = alt.toFixed(0) + ' m';
    document.getElementById('gps-cal-covcur').textContent = cCur.gw.toFixed(1) + ' x ' + cCur.gh.toFixed(1) + ' m';
    document.getElementById('gps-cal-gsdcur').textContent = (cCur.gsd * 1000).toFixed(1) + ' mm';
    document.getElementById('gps-cal-dumcur').textContent = cCur.dum.toFixed(0) + ' px';

    // ── Update SVG: Camera Geometry ──
    const svgW = 440, groundY = 200, droneY = 54;
    const droneX = 220;
    const altPx = groundY - droneY;  // pixel height in SVG

    // FOV cone endpoints
    const ground_half_w = alt * IMG_W / (2 * f_px);
    const ground_total_w = ground_half_w * 2;
    const ground_h = alt * IMG_H / f_px;
    const maxGroundW = 200;  // max half-width in SVG px
    const svgScale = maxGroundW / Math.max(ground_half_w, 1);
    const svgHalfW = Math.min(ground_half_w * svgScale, maxGroundW);

    const fovL = droneX - svgHalfW;
    const fovR = droneX + svgHalfW;

    document.getElementById('gps-fov-cone').setAttribute('points',
      droneX + ',' + droneY + ' ' + fovL + ',' + groundY + ' ' + fovR + ',' + groundY);

    // Ground bar
    document.getElementById('gps-ground-bar').setAttribute('x1', fovL);
    document.getElementById('gps-ground-bar').setAttribute('x2', fovR);
    document.getElementById('gps-ground-left').setAttribute('x1', fovL);
    document.getElementById('gps-ground-left').setAttribute('x2', fovL);
    document.getElementById('gps-ground-right').setAttribute('x1', fovR);
    document.getElementById('gps-ground-right').setAttribute('x2', fovR);
    document.getElementById('gps-ground-label').textContent =
      ground_total_w.toFixed(1) + ' x ' + ground_h.toFixed(1) + ' m';
    document.getElementById('gps-alt-label').textContent = alt.toFixed(1) + ' m';
    document.getElementById('gps-fpx-label').textContent = 'f = ' + f_px.toFixed(0) + ' px';

    // Detection point on ground (SVG coords)
    const detSvgX = droneX + (dx_px / (IMG_W / 2)) * svgHalfW;
    const detGroundY = groundY;
    document.getElementById('gps-det-ground').setAttribute('cx', detSvgX);
    document.getElementById('gps-det-ray').setAttribute('x2', detSvgX);
    document.getElementById('gps-dx-line').setAttribute('x2', Math.min(Math.max(detSvgX - 8, fovL), fovR));
    document.getElementById('gps-dx-label').setAttribute('x', (droneX + detSvgX) / 2);
    document.getElementById('gps-dx-label').textContent = dx_m.toFixed(1) + ' m';

    // Frame inset detection dot
    const frameL = 315, frameR = 425, frameT = 30, frameB = 95;
    const frameCX = (frameL + frameR) / 2;
    const frameCY = (frameT + frameB) / 2;
    const frameScaleX = (frameR - frameL) / IMG_W;
    const frameScaleY = (frameB - frameT) / IMG_H;
    const detFrameX = frameCX + dx_px * frameScaleX;
    const detFrameY = frameCY + dy_px * frameScaleY;
    document.getElementById('gps-det-frame').setAttribute('cx', detFrameX);
    document.getElementById('gps-det-frame').setAttribute('cy', detFrameY);
    document.getElementById('gps-frame-dx').setAttribute('x2', detFrameX);
    document.getElementById('gps-frame-dy').setAttribute('x1', detFrameX);
    document.getElementById('gps-frame-dy').setAttribute('x2', detFrameX);
    document.getElementById('gps-frame-dy').setAttribute('y2', detFrameY);

    // ── Update SVG: Compass / Yaw ──
    const compCX = 130, compCY = 130, compR = 80;

    // Rotate body axes group
    document.getElementById('gps-body-axes').setAttribute('transform',
      'rotate(' + yaw_deg + ',' + compCX + ',' + compCY + ')');

    // Yaw arc
    const arcEnd = yaw_deg;
    if (arcEnd > 1) {{
      const arcR = 40;
      const startX = compCX;
      const startY = compCY - arcR;
      const endRad = arcEnd * Math.PI / 180;
      const endX = compCX + arcR * Math.sin(endRad);
      const endY = compCY - arcR * Math.cos(endRad);
      const large = arcEnd > 180 ? 1 : 0;
      document.getElementById('gps-yaw-arc').setAttribute('d',
        'M ' + startX + ' ' + startY + ' A ' + arcR + ' ' + arcR + ' 0 ' + large + ' 1 ' + endX + ' ' + endY);
    }} else {{
      document.getElementById('gps-yaw-arc').setAttribute('d', '');
    }}

    // Yaw label position
    const labelRad = (yaw_deg / 2) * Math.PI / 180;
    const labelR = 52;
    document.getElementById('gps-yaw-label').setAttribute('x', compCX + labelR * Math.sin(labelRad));
    document.getElementById('gps-yaw-label').setAttribute('y', compCY - labelR * Math.cos(labelRad));
    document.getElementById('gps-yaw-label').textContent = yaw_deg + '\u00B0';

    // World-frame detection vector
    const vecScale = compR / Math.max(dist, 0.01) * Math.min(dist / ground_half_w, 1);
    const worldEndX = compCX + east_m / Math.max(dist, 0.01) * vecScale * dist / Math.max(ground_half_w, 1) * compR * 0.8;
    const worldEndY = compCY - north_m / Math.max(dist, 0.01) * vecScale * dist / Math.max(ground_half_w, 1) * compR * 0.8;
    // Clamp to circle
    const wdx = worldEndX - compCX;
    const wdy = worldEndY - compCY;
    const wdr = Math.sqrt(wdx*wdx + wdy*wdy);
    const clampR = compR * 0.9;
    let finalX = worldEndX, finalY = worldEndY;
    if (wdr > clampR) {{
      finalX = compCX + wdx / wdr * clampR;
      finalY = compCY + wdy / wdr * clampR;
    }}
    document.getElementById('gps-world-vec').setAttribute('x2', finalX);
    document.getElementById('gps-world-vec').setAttribute('y2', finalY);
    document.getElementById('gps-world-dot').setAttribute('cx', finalX);
    document.getElementById('gps-world-dot').setAttribute('cy', finalY);
    document.getElementById('gps-world-label').setAttribute('x', finalX + 6);
    document.getElementById('gps-world-label').setAttribute('y', finalY - 6);
  }}

  // Bind sliders
  altSlider.addEventListener('input', recalc);
  cxSlider.addEventListener('input', recalc);
  cySlider.addEventListener('input', recalc);
  yawSlider.addEventListener('input', recalc);

  // Public API for external data updates
  window.updateGPSData = function(data) {{
    if (data.alt !== undefined) {{
      altSlider.value = data.alt;
    }}
    if (data.f_px !== undefined) {{
      // f_px is read-only display, but we can note it
    }}
    if (data.fov_deg !== undefined) {{
      // informational
    }}
    recalc();
  }};

  // Initial calculation
  recalc();
}})();
</script>
'''
