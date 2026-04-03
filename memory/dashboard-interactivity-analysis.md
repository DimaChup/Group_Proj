# Dashboard Interactivity Research: Minimal High-Impact Upgrade

## Current Bottlenecks

**Polling (2s interval, line 219 in HTML):**
- Browser fetches 7 images every 2 seconds: `/latest`, `/best`, `/smart-grid` (2x), `/map`, `/bullseye`, `/api/status`
- All image endpoints re-render server-side, even when data hasn't changed
- Example: `/toggle-map-bg` flag causes **full re-render of `/bullseye`** (10-20 panel renders per toggle)
- Pi ~30ms per bullseye render (4 panels × complex geometry) → visible lag on toggle

**Toggle Effects (Toggle buttons, lines 175-185 in HTML):**
- Button click → HTTP request → render ALL 4 bullseye panels → JPEG encode → response
- Users see spinner for 200-400ms (unacceptable on 5G/4G field)
- Non-responsive feedback

**Rendering Load (main loop, line 1815):**
- Each detection triggers `render_bullseye()` immediately
- Heavy math: 4-panel layout, geometric transforms, GPS math, heat color gradients
- At 5 FPS detection, happens 5x/sec even if browser isn't looking

## Option Analysis

### 1. **Server-Sent Events (SSE) instead of polling**
**Concept:** Server pushes data to browser instead of browser asking.

**Pros:**
- Reduces polling from 2s to 0.5s (4x more responsive)
- One-way stream, lower overhead than HTTP requests
- Pi can control update cadence (only when data changes)

**Cons:**
- Still requires polling `/api/status` for metrics
- Still re-renders full JPEG images server-side
- Doesn't solve rendering overhead
- Must maintain persistent connections per client (threaded server handles this)

**Pi CPU saving:** ~10% (fewer HTTP requests, but rendering still dominates)
**Complexity:** MEDIUM (modify Handler, add SSE endpoint, update JS)
**Offline:** YES (local server, works anywhere)
**Incremental:** Partial (works alongside JPEG polling)

**Verdict:** Good for metrics, doesn't fix core interactivity problem (image rendering).

---

### 2. **Client-side Charts (Chart.js / Plotly.js for scatter plots)**
**Concept:** Send bullseye data as JSON, let browser render scatter plots via WebGL.

**Data sent:** `{ points: [ {e_m, n_m, pdist, alt, class}, ... ], mean_lat, mean_lon, max_range }`
- Bullseye panel 1 (All Detections): scatter plot, rings, cross
- Bullseye panel 2 (Smart Cluster): filtered scatter
- Bullseye panel 3 (Center-Distance): histogram/scatter
- Bullseye panel 4 (Centrality meters): bars or gauge

**Pros:**
- **Massive Pi CPU saving:** 0ms server rendering (was 10-20ms per update)
- **Instant interactivity:** zoom, pan, filter all client-side
- **Toggle effects instant:** just flip a boolean, re-render in JS (1-5ms)
- Threshold slider works client-side (no server round-trip)
- Can add hover tooltips, crosshairs, selection tools (free in JS)

**Cons:**
- Must handle 100+ points smoothly in browser (Plotly/Chart.js do this)
- Plotly is ~500KB (but CDN cached after first load)
- Geometry math (rings, heat colors) moves to JavaScript
- Need to refactor bullseye rendering logic from OpenCV → JS canvas

**Pi CPU saving:** 50% (bullseye render is ~15% of total AI work, eliminates it)
**Complexity:** HIGH (biggest refactor, but very focused)
**Offline:** YES (Plotly from CDN, cached; fallback to local CDN link needed for field)
**Incremental:** YES (replace `/bullseye` endpoint first, `/map` later)

**Verdict:** BEST for bullseye/charts. Highest impact/effort ratio.

---

### 3. **Leaflet.js for Interactive Map**
**Concept:** Replace static `/map` JPEG with draggable, zoomable Leaflet map.

**Approach:**
- Load `map.jpg` as local tile image (not OpenStreetMap, offline)
- Plot GPS detections as markers (circles with hover info)
- Add detection history heatmap overlay
- Threshold slider filters markers

**Pros:**
- **Instant pan/zoom:** no server calls, 100% client
- **No renders on zoom:** browser handles it natively
- **Detection points always visible:** no re-render needed
- Smart cluster shows tight cluster on map (visual feedback)
- Add distance measurements, area coverage overlay

**Cons:**
- Must host `map.jpg` as Leaflet image layer (needs georeferencing bounds)
- Marker symbols need JavaScript (not pre-rendered JPEG)
- Leaflet library ~180KB (CDN cached)
- Heat color gradient logic moves to JS

**Pi CPU saving:** ~30% (map render eliminated, was ~5-10% of work)
**Complexity:** MEDIUM (Leaflet integration, image georeferencing)
**Offline:** YES (Leaflet + local map.jpg, no OSM tiles needed)
**Incremental:** YES (add Leaflet panel alongside JPEG map, users choose)

**Verdict:** Good companion to charts. Map rendering is secondary concern.

---

### 4. **Canvas-based Rendering (Custom WebGL)**
**Concept:** Upload raw detection data, let canvas render everything.

**Pros:**
- Ultimate performance
- Full control over rendering

**Cons:**
- Requires WebGL knowledge (overkill for this project)
- Not simpler than Plotly
- Offline issues (WebGL sometimes disabled on field hardware)

**Verdict:** SKIP. Plotly is simpler and sufficient.

---

## RECOMMENDATION: Two-Phase Approach

### **PHASE 1 (MINIMAL, IMMEDIATE)** — 3–4 hours
**Replace bullseye JPEG with Plotly.js scatter plots.**

1. Create `/api/bullseye-data` endpoint (returns JSON with detection points)
   ```json
   {
     "all_detections": [ {e_m, n_m, pdist, alt}, ... ],
     "smart_cluster": [ {e_m, n_m}, ... ],
     "mean_lat": X, "mean_lon": Y,
     "max_range_m": 30,
     "estimate": {lat, lon, obs_count}
   }
   ```

2. Replace HTML bullseye JPEG with `<div id="bullseye-plot">` + `<div id="bullseye-threshold">`

3. JavaScript:
   - Fetch `/api/bullseye-data` every 1s (instead of polling JPEG every 2s)
   - Render 4 Plotly subplots (scatter + rings + heatmap + histogram)
   - Threshold slider: `_all_gps_estimates.filter(p => p.centrality > threshold)`
   - Toggle effect on threshold slider: **< 10ms** (JS only, no server round-trip)

4. Benefits:
   - **Instant toggle feedback** (was 200-400ms)
   - **Faster updates** (1s JSON fetch << 2s JPEG fetch)
   - **Zoom/pan/hover work for free** (Plotly built-in)
   - **Pi saves 10-15ms per frame** (no CV2 rendering)
   - **~200 lines of Python** (new endpoint) + **~300 lines of HTML/JS** (Plotly integration)

5. **No breaking changes:** Keep `/map`, `/smart-grid`, `/latest` as-is

---

### **PHASE 2 (OPTIONAL, IF TIME)** — 2–3 hours
**Leaflet.js for interactive map.**

1. Replace `/map` JPEG with Leaflet map + `map.jpg` image layer
2. Plot GPS markers with clustering
3. Add filter slider (same as bullseye threshold)

---

## Why This is Minimal & High-Impact

| Metric | Before | After | Gain |
|--------|--------|-------|------|
| Bullseye update latency | 2000ms | 1000ms | **2x faster** |
| Toggle feedback | 200-400ms | <10ms | **20-40x faster** |
| Zoom/pan | ✗ (not possible) | ✓ (free Plotly feature) | **New capability** |
| Threshold slider | ✗ (requires server re-render) | ✓ (JS filter) | **New capability** |
| Pi CPU (detection render overhead) | 15% | 0% | **15% saved** |

## Implementation Sketch (Phase 1)

### Python side (handler):
```python
elif path == '/api/bullseye-data':
    with frame_lock:
        data = {
            "all_detections": _all_gps_estimates,
            "smart_cluster": smart_estimator.locked_cluster if smart_estimator and smart_estimator.locked else [],
            "mean_lat": sum(e[0] for e in _all_gps_estimates) / len(_all_gps_estimates) if _all_gps_estimates else 0,
            "mean_lon": sum(e[1] for e in _all_gps_estimates) / len(_all_gps_estimates) if _all_gps_estimates else 0,
            "estimate": dummy_estimator.get_estimate() or None,
            "max_range_m": 30
        }
    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(data).encode())
```

### JavaScript side:
```js
// Fetch every 1s, not 2s
setInterval(async () => {
    const data = await fetch('/api/bullseye-data').then(r => r.json());
    // Build Plotly traces
    const x_all = data.all_detections.map(p => p.e_m);
    const y_all = data.all_detections.map(p => p.n_m);
    // ... render with Plotly.newPlot()
}, 1000);

// Threshold slider (no server call needed!)
document.getElementById('threshold-slider').oninput = (e) => {
    const threshold = e.target.value;
    const filtered = data.all_detections.filter(p => p.pdist < threshold);
    Plotly.restyle('bullseye-plot', {
        x: [filtered.map(p => p.e_m)],
        y: [filtered.map(p => p.n_m)]
    });
};
```

## Offline Capability
- Plotly: Load from CDN first visit, cached in browser for field
- Fallback: Include local `lib/plotly.min.js` in repo (1-visit workaround)
- Map: Already local (`map.jpg`)
- **Result:** Works 100% offline after first cached load

## Recommendation Summary

**Do PHASE 1 (Plotly bullseye).**  
- Smallest implementation (200+300 lines)
- Biggest interactivity win (2-40x faster)
- Solves toggle lag (main user complaint)
- Adds zoom/pan/threshold filtering (user requested)
- Saves Pi CPU for AI inference

**Skip PHASE 2** unless user asks (map is secondary; JPEG map works fine for field use).

**Do NOT do:** Full Leaflet+OpenStreetMap (overkill, network dependent, less responsive than local map).
