#!/usr/bin/env python3
"""
pi_flight.py — SAR Ground Station with Web Dashboard

Runs on Pi (headless) or laptop (SIMULATION mode).
Serves a web dashboard at http://localhost:8090 with:
  - Live video stream from drone camera
  - 2D grid showing drone position + detection clusters
  - Command buttons: Investigate, Confirm, Interest, False Positive, Land
  - Status display: mode, altitude, GPS, detections

SIMULATION mode: connects to SITL, uses simulated camera (map.jpg)
  - Fly with WASD in terminal, or use Mission Planner
REAL mode: connects to Cube via mavproxy, uses Pi camera
  - Pilot flies RC, operator uses web dashboard

Usage:
    # Laptop simulation (needs SITL running):
    set DRONE_MODE=SIMULATION && python pi_flight.py

    # Pi real flight:
    python pi_flight.py

    Then open http://localhost:8090 in browser
"""

import threading
import queue
import time
import math
import json
import io
import argparse
import sys
import os
import signal

# Ensure Ctrl+C works even with threads
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Force headless OpenCV when no display (SSH/PuTTY)
if not os.environ.get('DISPLAY'):
    # Prevent cv2 from trying to open any GUI windows
    os.environ.pop('QT_QPA_PLATFORM', None)
    os.environ['OPENCV_VIDEOIO_PRIORITY_BACKEND'] = '0'

import cv2

# Disable GUI if no display
if not os.environ.get('DISPLAY'):
    cv2_imshow_orig = cv2.imshow
    cv2.imshow = lambda *a, **k: None
    cv2.namedWindow = lambda *a, **k: None
    cv2.setMouseCallback = lambda *a, **k: None
    cv2.waitKey = lambda *a, **k: -1
    cv2.destroyAllWindows = lambda *a, **k: None
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pymavlink import mavutil

import config
from vision import VisionSystem
from utils import GeoTransformer

if config.MODE == "SIMULATION":
    from simulation import SimulationEnvironment

# --- Constants ---
COPTER_MODES = {
    0: "STABILIZE", 2: "ALT_HOLD", 3: "AUTO", 4: "GUIDED",
    5: "LOITER", 6: "RTL", 9: "LAND", 16: "POSHOLD",
}
CLUSTER_COLORS = [
    "#00ff88", "#00ddff", "#ffaa00", "#ff00ff",
    "#00ffff", "#c864ff", "#64ffc8", "#ff9664",
]

# ========================================================================
# HTML Dashboard (inline)
# ========================================================================
HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SAR Ground Station</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#1a1a2e;color:#e0e0e0;font-family:'Courier New',monospace;overflow:hidden}
#header{background:#16213e;padding:6px 12px;display:flex;justify-content:space-between;
  align-items:center;border-bottom:2px solid #0f3460;height:40px}
#header .mode{font-size:16px;font-weight:bold;color:#00ff88}
#header .status{font-size:12px;color:#aaa}
#main{display:flex;padding:6px;gap:6px;height:calc(100vh - 96px)}
#grid-box{flex:1;background:#0a0a1a;border:1px solid #333;border-radius:4px;position:relative;min-width:300px}
#grid{width:100%;height:100%}
#cluster-info{position:absolute;bottom:4px;left:4px;font-size:11px;background:rgba(0,0,0,.8);
  padding:4px 6px;border-radius:3px;max-height:120px;overflow-y:auto}
#stream-box{flex:2;background:#000;border:1px solid #333;border-radius:4px;
  display:flex;flex-direction:column;position:relative;overflow:hidden}
#stream{width:100%;height:100%;object-fit:contain}
#det-alert{position:absolute;top:8px;right:8px;background:#ff6600;color:#000;
  padding:6px 12px;border-radius:4px;font-weight:bold;display:none;font-size:14px}
#link-lost{position:fixed;top:0;left:0;right:0;background:#ff0000;color:#fff;
  text-align:center;padding:8px;font-size:18px;font-weight:bold;display:none;z-index:999}
#controls{display:flex;gap:6px;padding:6px;background:#16213e;
  justify-content:center;flex-wrap:wrap;border-top:2px solid #0f3460;height:54px;align-items:center}
.btn{padding:8px 14px;font-size:12px;font-family:'Courier New',monospace;
  border:2px solid;border-radius:4px;cursor:pointer;background:transparent;color:#e0e0e0}
.btn:hover{opacity:.8}.btn:active{opacity:.6}
.btn.arm{border-color:#ff6600;color:#ff6600}
.btn.takeoff{border-color:#00aaff;color:#00aaff}
.btn.inv{border-color:#ffaa00;color:#ffaa00}
.btn.yes{border-color:#00ff88;color:#00ff88}
.btn.ioi{border-color:#00ddff;color:#00ddff}
.btn.fp{border-color:#ff4444;color:#ff4444}
.btn.land{border-color:#ff00ff;color:#ff00ff}
.btn.res{border-color:#888;color:#888}
.btn:disabled{opacity:.3;cursor:not-allowed}
#log{position:absolute;bottom:50px;left:8px;right:8px;font-size:11px;color:#0f0;
  background:rgba(0,0,0,.7);padding:4px;border-radius:3px;max-height:80px;overflow-y:auto;display:none}
</style></head><body>
<div id="link-lost">LINK LOST — NO HEARTBEAT</div>
<div id="header">
  <div><span class="mode" id="fmode">CONNECTING...</span>
    <span class="status" id="dmode"></span></div>
  <div class="status">
    <span id="gps">GPS: ---</span> |
    <span id="alt">ALT: --m</span> |
    <span id="det">DET: 0</span> |
    <span id="bat">BAT: --V</span>
  </div>
</div>
<div id="main">
  <div id="grid-box">
    <canvas id="grid"></canvas>
    <div id="cluster-info">No detections yet</div>
  </div>
  <div id="stream-box">
    <img id="stream" src="/stream" alt="Video Stream">
    <div id="det-alert">DETECTION</div>
  </div>
</div>
<div id="controls">
  <button class="btn arm" onclick="cmd('arm')">ARM</button>
  <button class="btn takeoff" onclick="cmd('takeoff')">TAKEOFF</button>
  <button class="btn inv" id="btn-inv" onclick="cmd('investigate')">N: INVESTIGATE</button>
  <button class="btn yes" onclick="cmd('confirm')">Y: CONFIRM</button>
  <button class="btn ioi" onclick="cmd('interest')">I: INTEREST</button>
  <button class="btn fp" onclick="cmd('false_positive')">X: FALSE POS</button>
  <button class="btn land" onclick="cmd('land')">L: LAND</button>
  <button class="btn res" onclick="cmd('resume')">M: RESUME</button>
  <button class="btn rtl" onclick="if(confirm('Return to launch?'))cmd('rtl')" style="border-color:#ff0000;color:#ff0000;font-weight:bold">RTL</button>
  <button class="btn arm" onclick="fakeDetect()" title="Create fake detection at drone position or custom GPS">FAKE DET</button>
</div>
<script>
let S={},selCluster=null,alertTimer=null;
async function cmd(a,extra){
  try{const body=Object.assign({action:a,cluster:selCluster},extra||{});
    const r=await fetch('/command',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)});
    const j=await r.json();if(j.message)showLog(j.message);
  }catch(e){console.error(e)}}
function fakeDetect(){
  const inp=prompt('Fake detection GPS (leave blank = drone position, or enter: lat,lon)','');
  if(inp===null)return;
  if(inp.trim()===''){cmd('fake_detect');}
  else{const parts=inp.split(',');if(parts.length===2){
    cmd('fake_detect',{fake_lat:parseFloat(parts[0]),fake_lon:parseFloat(parts[1])});
  }else{alert('Enter lat,lon or leave blank');}}
}
function showLog(m){console.log(m)}
function showDetAlert(){
  const el=document.getElementById('det-alert');el.style.display='block';
  clearTimeout(alertTimer);alertTimer=setTimeout(()=>{el.style.display='none'},2000)}
async function poll(){
  try{const r=await fetch('/state');S=await r.json();updateUI()}catch(e){}}
function updateUI(){
  const fm=document.getElementById('fmode');
  fm.textContent=S.flight_mode||'---';
  fm.style.color=S.flight_mode==='INVESTIGATING'?'#ffaa00':
    S.flight_mode==='LANDING'?'#ff00ff':'#00ff88';
  document.getElementById('dmode').textContent=S.drone_mode?(' ['+S.drone_mode+']'):'';
  document.getElementById('gps').textContent='GPS: '+(S.lat||0).toFixed(6)+', '+(S.lon||0).toFixed(6);
  document.getElementById('alt').textContent='ALT: '+(S.alt||0).toFixed(1)+'m';
  document.getElementById('det').textContent='DET: '+(S.total_detections||0);
  const bat=S.battery||0;const batEl=document.getElementById('bat');
  batEl.textContent='BAT: '+bat.toFixed(1)+'V';
  batEl.style.color=bat>14?'#0f0':bat>13?'#ffaa00':'#ff0000';
  document.getElementById('link-lost').style.display=(S.heartbeat_age>5)?'block':'none';
  if(S.new_detection)showDetAlert();
  drawGrid();updateClusterInfo();
  document.getElementById('btn-inv').textContent=
    selCluster?'N: INVESTIGATE #'+selCluster:'N: INVESTIGATE'}
function drawGrid(){
  const c=document.getElementById('grid'),ctx=c.getContext('2d');
  c.width=c.parentElement.clientWidth;c.height=c.parentElement.clientHeight;
  const W=c.width,H=c.height;ctx.fillStyle='#0a0a1a';ctx.fillRect(0,0,W,H);
  if(!S.lat)return;
  const R=6378137,mPerDLat=R*Math.PI/180,mPerDLon=mPerDLat*Math.cos(S.lat*Math.PI/180);
  let pts=[{la:S.lat,lo:S.lon}];
  (S.clusters||[]).forEach(c=>{if(c.lat&&c.lon)pts.push({la:c.lat,lo:c.lon})});
  (S.logged||[]).forEach(l=>{if(l.lat&&l.lon)pts.push({la:l.lat,lo:l.lon})});
  let mnLa=S.lat,mxLa=S.lat,mnLo=S.lon,mxLo=S.lon;
  pts.forEach(p=>{mnLa=Math.min(mnLa,p.la);mxLa=Math.max(mxLa,p.la);
    mnLo=Math.min(mnLo,p.lo);mxLo=Math.max(mxLo,p.lo)});
  const pad=50/mPerDLat;mnLa-=pad;mxLa+=pad;
  const padLo=50/mPerDLon;mnLo-=padLo;mxLo+=padLo;
  const sLa=(mxLa-mnLa)*mPerDLat,sLo=(mxLo-mnLo)*mPerDLon;
  if(sLa<100){const e=(100-sLa)/2/mPerDLat;mnLa-=e;mxLa+=e}
  if(sLo<100){const e=(100-sLo)/2/mPerDLon;mnLo-=e;mxLo+=e}
  function g2p(la,lo){return[(lo-mnLo)/(mxLo-mnLo)*W,(1-(la-mnLa)/(mxLa-mnLa))*H]}
  // Grid lines
  ctx.strokeStyle='#1a1a2e';ctx.lineWidth=1;
  const spanM=Math.round((mxLo-mnLo)*mPerDLon);
  const step=spanM<200?20:spanM<500?50:100;
  for(let m=0;m<=spanM;m+=step){
    const x=m/spanM*W;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}
  const spanLaM=Math.round((mxLa-mnLa)*mPerDLat);
  for(let m=0;m<=spanLaM;m+=step){
    const y=H-m/spanLaM*H;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}
  ctx.fillStyle='#333';ctx.font='10px Courier New';ctx.textAlign='left';
  ctx.fillText(spanM+'m x '+spanLaM+'m',4,H-4);
  // Search polygon
  if(S.search_poly&&S.search_poly.length>2){
    ctx.beginPath();const sp=S.search_poly;
    let[sx,sy]=g2p(sp[0][0],sp[0][1]);ctx.moveTo(sx,sy);
    for(let i=1;i<sp.length;i++){[sx,sy]=g2p(sp[i][0],sp[i][1]);ctx.lineTo(sx,sy)}
    ctx.closePath();ctx.strokeStyle='#333';ctx.lineWidth=1;ctx.stroke()}
  // Investigate target
  if(S.inv_target){
    const[ix,iy]=g2p(S.inv_target[0],S.inv_target[1]);
    ctx.beginPath();ctx.arc(ix,iy,15,0,Math.PI*2);
    ctx.strokeStyle='#ffaa0066';ctx.lineWidth=2;ctx.setLineDash([4,4]);ctx.stroke();ctx.setLineDash([])}
  // Landing target
  if(S.land_target){
    const[lx,ly]=g2p(S.land_target[0],S.land_target[1]);
    ctx.beginPath();ctx.arc(lx,ly,8,0,Math.PI*2);
    ctx.fillStyle='#ff00ff';ctx.fill();
    ctx.fillStyle='#fff';ctx.font='bold 10px Courier New';ctx.textAlign='center';
    ctx.fillText('L',lx,ly+4)}
  // Logged items
  (S.logged||[]).forEach(l=>{
    if(!l.lat||!l.lon)return;const[lx,ly]=g2p(l.lat,l.lon);
    if(l.type==='interest'){ctx.fillStyle='#00ddff';ctx.fillRect(lx-5,ly-5,10,10);
      ctx.font='9px Courier New';ctx.fillText('IOI',lx,ly+14)}
    else{ctx.strokeStyle='#ff4444';ctx.lineWidth=2;
      ctx.beginPath();ctx.moveTo(lx-5,ly-5);ctx.lineTo(lx+5,ly+5);ctx.stroke();
      ctx.beginPath();ctx.moveTo(lx+5,ly-5);ctx.lineTo(lx-5,ly+5);ctx.stroke()}});
  // Clusters
  const colors=["#00ff88","#00ddff","#ffaa00","#ff00ff","#00ffff","#c864ff","#64ffc8","#ff9664"];
  (S.clusters||[]).forEach((cl,ci)=>{
    if(!cl.lat||!cl.lon)return;const[cx,cy]=g2p(cl.lat,cl.lon);
    const col=colors[ci%colors.length];const isSel=cl.id===selCluster;
    ctx.beginPath();ctx.arc(cx,cy,isSel?14:9,0,Math.PI*2);
    if(isSel){ctx.fillStyle=col;ctx.fill()}
    ctx.strokeStyle=col;ctx.lineWidth=isSel?3:2;ctx.stroke();
    ctx.fillStyle='#fff';ctx.font='bold 11px Courier New';ctx.textAlign='center';
    ctx.fillText('#'+cl.id,cx,cy+4);
    ctx.font='9px Courier New';ctx.fillStyle=col;
    ctx.fillText(cl.count+' hits',cx,cy+18)});
  // Drone
  const[dx,dy]=g2p(S.lat,S.lon);const yaw=(S.yaw||0)*Math.PI/180;
  ctx.save();ctx.translate(dx,dy);ctx.rotate(yaw);
  ctx.beginPath();ctx.moveTo(0,-14);ctx.lineTo(9,9);ctx.lineTo(0,5);ctx.lineTo(-9,9);ctx.closePath();
  ctx.fillStyle='#ffaa00';ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=1;ctx.stroke();
  ctx.restore();
  ctx.fillStyle='#ffaa00';ctx.font='10px Courier New';ctx.textAlign='center';
  ctx.fillText('DRONE',dx,dy+22)}
function updateClusterInfo(){
  const el=document.getElementById('cluster-info');
  const cls=S.clusters||[];
  if(!cls.length){el.innerHTML='No detections yet';return}
  el.innerHTML=cls.map((c,i)=>{
    const sel=c.id===selCluster?' style="color:#ffaa00;font-weight:bold"':'';
    return '<div'+sel+' onclick="selCl('+c.id+')" style="cursor:pointer">'+
      '#'+c.id+': '+c.count+' hits | '+(c.lat||0).toFixed(6)+', '+(c.lon||0).toFixed(6)+'</div>'
  }).join('')}
function selCl(id){selCluster=selCluster===id?null:id;updateUI()}
document.addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(k==='n')cmd('investigate');else if(k==='y')cmd('confirm');
  else if(k==='i')cmd('interest');else if(k==='x')cmd('false_positive');
  else if(k==='l')cmd('land');else if(k==='m')cmd('resume');
});
setInterval(poll,400);poll();
</script></body></html>"""


# ========================================================================
# Web Server
# ========================================================================
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class WebHandler(BaseHTTPRequestHandler):
    """Handles dashboard, MJPEG stream, state API, and commands."""
    flight = None  # set by PiFlight before starting server

    def log_message(self, format, *args):
        pass  # suppress HTTP logs

    def do_GET(self):
        if self.path == '/':
            self._serve_html()
        elif self.path == '/stream':
            self._serve_stream()
        elif self.path.startswith('/state'):
            self._serve_state()
        elif self.path.startswith('/snapshot'):
            self._serve_snapshot()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/command':
            self._handle_command()
        else:
            self.send_error(404)

    def _serve_html(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_DASHBOARD.encode())

    def _serve_stream(self):
        self.send_response(200)
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        try:
            while self.flight and self.flight.running:
                jpeg = self.flight.get_stream_jpeg()
                if jpeg:
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                    self.wfile.write(jpeg)
                    self.wfile.write(b'\r\n')
                    self.wfile.flush()
                time.sleep(0.05)  # ~20fps max
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def _serve_state(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        state = self.flight.get_state() if self.flight else {}
        self.wfile.write(json.dumps(state).encode())

    def _serve_snapshot(self):
        jpeg = self.flight.snapshot_jpeg if self.flight else None
        if jpeg:
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.end_headers()
            self.wfile.write(jpeg)
        else:
            self.send_error(404)

    def _handle_command(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        result = {"ok": True, "message": ""}
        if self.flight:
            result = self.flight.handle_command(body)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())


# ========================================================================
# Main Flight Controller
# ========================================================================
class PiFlight:
    def __init__(self, args):
        # Auto-detect IP
        pi_ip = "localhost"
        try:
            import subprocess
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
            ip = result.stdout.strip().split()[0]
            if ip:
                pi_ip = ip
        except Exception:
            pass
        print(f"=== SAR GROUND STATION ({config.MODE} MODE) ===")
        if args.passive:
            print("*** PASSIVE MODE — ZERO COMMANDS WILL BE SENT ***")
        print(f"Dashboard: http://{pi_ip}:{args.port}")
        print(f"Stream:    http://{pi_ip}:{args.port}/stream")
        print()

        self.running = True
        self.args = args
        self._lock = threading.Lock()
        self._frame_lock = threading.Lock()
        self._stream_jpeg = None
        self.snapshot_jpeg = None
        self._new_detection_flag = False

        # --- Telemetry ---
        self.lat = config.REF_LAT
        self.lon = config.REF_LON
        self.alt = 0.0
        self.yaw = 0.0  # radians
        self.groundspeed = 0.0
        self.armed = False
        self.battery_v = 0.0
        self.drone_mode = "UNKNOWN"
        self.last_heartbeat = 0

        # --- Flight mode ---
        self.flight_mode = "MANUAL"  # MANUAL, INVESTIGATING, LANDING
        self.investigating = False
        self.investigate_target = None
        self.investigate_phase = None  # approaching, descending, observing
        self.investigate_cluster_idx = None
        self.investigate_alt = 15.0
        self.landing_target = None
        self.landing_phase = None  # flying_to, descending, landed
        self.landing_offset_m = 7.5

        # --- Detection / GPS estimation ---
        self.detection_clusters = []
        self.active_cluster_idx = None
        self._next_cluster_id = 0
        self.CLUSTER_THRESHOLD_M = args.cluster_dist
        self.CENTRE_THRESHOLD_PX = 30
        self.total_detections = 0
        self.logged_items = []
        self.best_gps = None

        # --- CV throttle ---
        self.cv_interval = (1.0 / args.fps) if args.fps > 0 else 0
        self.last_cv_time = 0

        # --- Setup camera/sim ---
        if config.MODE == "SIMULATION":
            self.sim = SimulationEnvironment(GeoTransformer(map_w_px=100))
            self.geo = GeoTransformer(map_w_px=self.sim.map_w)
            self.sim.geo = self.geo

            # Interactive setup (cv2 window — closes after setup)
            targets_list, self.tgt_type, self.search_poly = self.sim.setup_on_map()
            cv2.destroyAllWindows()

            self.eyes = VisionSystem(camera_index=None, model_path="best.tflite")
            self.eyes.using_ai = True

            # Store target positions (for simulation error display)
            self.all_targets_px = targets_list
            self.all_target_gps = [self.geo.pixels_to_gps(t[0], t[1]) for t in targets_list]
            self.actual_gps = self.all_target_gps[0] if self.all_target_gps else None
            if self.actual_gps:
                print(f"Real dummy GPS: {self.actual_gps[0]:.6f}, {self.actual_gps[1]:.6f}")
            print(f"Targets placed: {len(targets_list)}")
            # Convert search poly pixels to GPS
            self.search_poly_gps = []
            if self.search_poly:
                self.search_poly_gps = [self.geo.pixels_to_gps(p[0], p[1]) for p in self.search_poly]
        else:
            self.sim = None
            self.geo = GeoTransformer(map_w_px=4800)
            # Load search area: search_area.json > config.SEARCH_AREA_GPS
            sa_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "search_area.json")
            if os.path.exists(sa_file):
                import json as _json
                with open(sa_file, "r") as f:
                    sa_data = _json.load(f)
                if sa_data and len(sa_data) >= 3:
                    self.search_poly_gps = [(pt["lat"], pt["lon"]) for pt in sa_data]
                    print(f"[REAL] Search area from search_area.json: {len(self.search_poly_gps)} points")
                else:
                    self.search_poly_gps = list(config.SEARCH_AREA_GPS)
            else:
                self.search_poly_gps = list(config.SEARCH_AREA_GPS)
            self.eyes = VisionSystem(camera_index=config.REAL_CAMERA_INDEX, model_path="best.tflite")
            self.eyes.using_ai = True
            self.actual_gps = None
            self.all_target_gps = []
            print("Real mode: no ground truth")

        # --- MAVLink ---
        self.master = None
        self._connect_mavlink()

        # --- Web server ---
        WebHandler.flight = self
        self.httpd = ThreadedHTTPServer(('0.0.0.0', args.port), WebHandler)
        self._web_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self._web_thread.start()
        print(f"[WEB] Dashboard running at http://localhost:{args.port}")

    # --- MAVLink ---
    def _connect_mavlink(self):
        conn_str = config.CONNECTION_STR
        print(f"[MAV] Connecting to {conn_str}...")
        try:
            self.master = mavutil.mavlink_connection(conn_str, baud=config.BAUD_RATE)
            self.master.wait_heartbeat(timeout=10)
            print(f"[MAV] Connected! System {self.master.target_system}")
            # Request all data streams (SITL won't send GPS/attitude without this)
            self.master.mav.request_data_stream_send(
                self.master.target_system, self.master.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
            print("[MAV] Data streams requested (10Hz)")
        except Exception as e:
            print(f"[MAV] Connection failed: {e}")
            print("[MAV] Will retry in main loop...")
            self.master = None

    def drain_mavlink(self):
        if not self.master:
            return
        while True:
            msg = self.master.recv_match(blocking=False)
            if not msg:
                break
            mtype = msg.get_type()
            if mtype == 'GLOBAL_POSITION_INT':
                self.lat = msg.lat / 1e7
                self.lon = msg.lon / 1e7
                self.alt = msg.relative_alt / 1000.0
            elif mtype == 'ATTITUDE':
                self.yaw = msg.yaw
            elif mtype == 'VFR_HUD':
                self.groundspeed = msg.groundspeed
            elif mtype == 'SYS_STATUS':
                self.battery_v = msg.voltage_battery / 1000.0 if msg.voltage_battery > 0 else 0
            elif mtype == 'HEARTBEAT':
                if msg.type != mavutil.mavlink.MAV_TYPE_GCS:
                    self.last_heartbeat = time.time()
                    self.armed = self.master.motors_armed()
                    cm = msg.custom_mode
                    self.drone_mode = COPTER_MODES.get(cm, f"MODE({cm})")
                    if self.master.target_system == 0:
                        self.master.target_system = msg.get_srcSystem()
                        self.master.target_component = msg.get_srcComponent()
                        print(f"[MAV] Autopilot: system {self.master.target_system}")

    # --- Camera + CV ---
    def get_frame(self):
        if config.MODE == "SIMULATION" and self.sim:
            px, py = self.geo.gps_to_pixels(self.lat, self.lon)
            frame, _, _ = self.sim.get_drone_view(px, py, self.alt, self.yaw)
            return frame
        else:
            return self.eyes.get_frame()

    def get_stream_jpeg(self):
        with self._frame_lock:
            return self._stream_jpeg

    # --- GPS estimation ---
    def _new_cluster(self):
        self._next_cluster_id += 1
        return {
            "id": self._next_cluster_id,
            "observations": [],
            "best_gps": None,
            "total_gps": None,
            "total_wlat": 0.0, "total_wlon": 0.0, "total_w": 0.0,
            "detection_count": 0,
        }

    def _gps_distance(self, lat1, lon1, lat2, lon2):
        R = 6378137.0
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dLon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _route_to_cluster(self, est_lat, est_lon, weight):
        best_idx, best_dist = None, float('inf')
        for i, c in enumerate(self.detection_clusters):
            if c["best_gps"]:
                d = self._gps_distance(est_lat, est_lon, c["best_gps"][0], c["best_gps"][1])
                if d < best_dist:
                    best_dist = d
                    best_idx = i

        if best_idx is not None and best_dist < self.CLUSTER_THRESHOLD_M:
            cluster = self.detection_clusters[best_idx]
            idx = best_idx
        else:
            cluster = self._new_cluster()
            self.detection_clusters.append(cluster)
            idx = len(self.detection_clusters) - 1
            print(f"[CLUSTER] New item #{cluster['id']} detected!")

        self._add_observation(cluster, est_lat, est_lon, weight)
        return idx

    def _add_observation(self, cluster, est_lat, est_lon, weight):
        cluster["observations"].append((est_lat, est_lon, weight))
        if len(cluster["observations"]) > 50:
            cluster["observations"] = cluster["observations"][-50:]
        cluster["detection_count"] += 1

        # Rolling average (last 50)
        obs = cluster["observations"]
        tw = sum(w for _, _, w in obs)
        cluster["best_gps"] = (sum(la * w for la, _, w in obs) / tw,
                               sum(lo * w for _, lo, w in obs) / tw)

        # Running total average
        cluster["total_wlat"] += est_lat * weight
        cluster["total_wlon"] += est_lon * weight
        cluster["total_w"] += weight
        cluster["total_gps"] = (cluster["total_wlat"] / cluster["total_w"],
                                cluster["total_wlon"] / cluster["total_w"])

    def calculate_target_gps(self, u, v):
        """Pixel detection (u,v) -> estimated GPS position."""
        Cx, Cy = config.IMAGE_W / 2, config.IMAGE_H / 2
        dist = math.sqrt((u - Cx) ** 2 + (v - Cy) ** 2)

        if dist < self.CENTRE_THRESHOLD_PX:
            # Centre-snap: target directly below drone
            est_lat, est_lon = self.lat, self.lon
            alt_factor = (30.0 / max(self.alt, 1.0)) ** 2
            weight = 10.0 * alt_factor
        else:
            # Pixel-to-GPS projection
            gsd = (config.SENSOR_WIDTH_MM * self.alt) / (config.FOCAL_LENGTH_MM * config.IMAGE_W)
            dx_px, dy_px = u - Cx, v - Cy
            fwd_m = -dy_px * gsd
            right_m = dx_px * gsd
            offset_n = fwd_m * math.cos(self.yaw) - right_m * math.sin(self.yaw)
            offset_e = fwd_m * math.sin(self.yaw) + right_m * math.cos(self.yaw)
            R_EARTH = 6378137.0
            est_lat = self.lat + (offset_n / R_EARTH) * (180 / math.pi)
            est_lon = self.lon + (offset_e / (R_EARTH * math.cos(math.radians(self.lat)))) * (180 / math.pi)
            max_dist = math.sqrt(Cx ** 2 + Cy ** 2)
            centre_weight = 1.0 + 4.0 * (1.0 - dist / max_dist)
            alt_factor = (30.0 / max(self.alt, 1.0)) ** 2
            weight = centre_weight * alt_factor

        # Route to cluster
        if (self.investigate_phase == "observing" and self.investigate_cluster_idx is not None
                and self.investigate_cluster_idx < len(self.detection_clusters)):
            idx = self.investigate_cluster_idx
            self._add_observation(self.detection_clusters[idx], est_lat, est_lon, weight)
        else:
            idx = self._route_to_cluster(est_lat, est_lon, weight)

        self.active_cluster_idx = idx
        self.best_gps = self.detection_clusters[idx].get("total_gps") or self.detection_clusters[idx]["best_gps"]
        self.total_detections += 1
        self._new_detection_flag = True
        return est_lat, est_lon

    # --- MAVLink commands ---
    def _passive_block(self, cmd_name):
        """Block commands in passive mode"""
        if self.args.passive:
            print(f"[PASSIVE] Blocked: {cmd_name} (passive mode, zero commands)")
            return True
        return False

    def send_arm(self):
        if not self.master or self._passive_block("ARM"):
            return
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            4, 0, 0, 0, 0, 0)  # GUIDED
        time.sleep(0.5)
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            1, 0, 0, 0, 0, 0, 0)
        print("[CMD] ARM sent (GUIDED mode)")

    def send_takeoff(self, alt=20):
        if not self.master or self._passive_block("TAKEOFF"):
            return
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
            0, 0, 0, 0, 0, 0, alt)
        print(f"[CMD] TAKEOFF to {alt}m sent")

    def send_to_gps(self, target_lat, target_lon, target_alt=None):
        if not self.master or self._passive_block("GOTO"):
            return
        alt = target_alt if target_alt is not None else self.alt
        self.master.mav.set_position_target_global_int_send(
            0, self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            0b110111111000,
            int(target_lat * 1e7), int(target_lon * 1e7), alt,
            0, 0, 0, 0, 0, 0, 0, 0)

    def send_velocity(self, vx, vy, vz, yaw_rate=0):
        if not self.master or self._passive_block("VELOCITY"):
            return
        cos_yaw = math.cos(self.yaw)
        sin_yaw = math.sin(self.yaw)
        vx_ned = vx * cos_yaw - vy * sin_yaw
        vy_ned = vx * sin_yaw + vy * cos_yaw
        self.master.mav.set_position_target_local_ned_send(
            0, self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b010111000111,
            0, 0, 0, vx_ned, vy_ned, vz,
            0, 0, 0, 0, math.radians(yaw_rate))

    def send_land(self):
        if not self.master or self._passive_block("LAND"):
            return
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
            0, 0, 0, 0, 0, 0, 0)
        print("[CMD] LAND sent")

    # --- Command handler (from web dashboard) ---
    def handle_command(self, body):
        action = body.get("action", "")
        cluster_id = body.get("cluster")
        msg = ""

        if action == "arm":
            self.send_arm()
            msg = "ARM command sent"

        elif action == "takeoff":
            self.send_takeoff(self.args.takeoff_alt)
            msg = f"TAKEOFF to {self.args.takeoff_alt}m"

        elif action == "investigate":
            # Find cluster to investigate
            ci = self._find_cluster_by_id(cluster_id)
            if ci is None:
                # Use most recent cluster
                ci = self.active_cluster_idx
            if ci is not None and ci < len(self.detection_clusters):
                cl = self.detection_clusters[ci]
                target = cl.get("total_gps") or cl.get("best_gps")
                if target:
                    self.investigate_target = target
                    self.investigate_phase = "approaching"
                    self.investigate_cluster_idx = ci
                    self.flight_mode = "INVESTIGATING"
                    label = f"#{cl['id']}"
                    msg = f"Investigating {label} ({cl['detection_count']} hits)"
                    print(f"[INVESTIGATE] Flying to {label} at {target[0]:.6f}, {target[1]:.6f}")
                else:
                    msg = "Cluster has no position yet"
            else:
                msg = "No cluster to investigate"

        elif action == "confirm":
            if self.flight_mode == "INVESTIGATING" and self.investigate_cluster_idx is not None:
                ci = self.investigate_cluster_idx
                cl = self.detection_clusters[ci]
                self.flight_mode = "MANUAL"
                self.investigate_phase = None
                msg = f"Confirmed #{cl['id']} as dummy. Press L to land."
                print(f"[CONFIRM] Item #{cl['id']} confirmed as real dummy")
            else:
                msg = "Not investigating anything"

        elif action == "interest":
            if self.investigate_cluster_idx is not None and self.investigate_cluster_idx < len(self.detection_clusters):
                ci = self.investigate_cluster_idx
                cl = self.detection_clusters[ci]
                gps = cl.get("total_gps") or cl.get("best_gps")
                if gps:
                    self.logged_items.append({"type": "interest", "lat": gps[0], "lon": gps[1],
                                              "cluster_id": cl["id"], "count": cl["detection_count"]})
                    msg = f"#{cl['id']} logged as Item of Interest at {gps[0]:.6f}, {gps[1]:.6f}"
                    print(f"[IOI] {msg}")
                self._cancel_investigate()
            else:
                msg = "Not investigating anything"

        elif action == "false_positive":
            if self.investigate_cluster_idx is not None and self.investigate_cluster_idx < len(self.detection_clusters):
                ci = self.investigate_cluster_idx
                cl = self.detection_clusters[ci]
                fp_gps = cl.get("total_gps") or cl.get("best_gps")
                self.logged_items.append({"type": "false_positive",
                                          "lat": fp_gps[0] if fp_gps else 0,
                                          "lon": fp_gps[1] if fp_gps else 0,
                                          "cluster_id": cl["id"]})
                msg = f"#{cl['id']} discarded as false positive"
                print(f"[FP] {msg}")
                # Remove cluster and fix active_cluster_idx
                self.detection_clusters.pop(ci)
                if self.active_cluster_idx is not None:
                    if self.active_cluster_idx == ci:
                        self.active_cluster_idx = 0 if self.detection_clusters else None
                    elif self.active_cluster_idx > ci:
                        self.active_cluster_idx -= 1
                self._cancel_investigate()
            else:
                msg = "Not investigating anything"

        elif action == "land":
            # Find best estimate for landing
            est = None
            if self.active_cluster_idx is not None and self.active_cluster_idx < len(self.detection_clusters):
                cl = self.detection_clusters[self.active_cluster_idx]
                est = cl.get("total_gps") or cl.get("best_gps")
            if est:
                # Calculate 7.5m north of estimate
                R_EARTH = 6378137.0
                offset_lat = (self.landing_offset_m / R_EARTH) * (180 / math.pi)
                self.landing_target = (est[0] + offset_lat, est[1])
                self.landing_phase = "flying_to"
                self.flight_mode = "LANDING"
                self._cancel_investigate()
                msg = f"Landing 7.5m north of estimate"
                print(f"[LAND] Target: {self.landing_target[0]:.6f}, {self.landing_target[1]:.6f}")
            else:
                msg = "No position estimate for landing"

        elif action == "fake_detect":
            # Manual fake detection — test full sequence without CV
            fake_lat = body.get("fake_lat")
            fake_lon = body.get("fake_lon")
            if fake_lat is not None and fake_lon is not None:
                est_lat, est_lon = float(fake_lat), float(fake_lon)
            else:
                # Use drone's current position
                est_lat, est_lon = self.lat, self.lon
            # Create cluster with high-weight observation (as if confirmed detection)
            idx = self._route_to_cluster(est_lat, est_lon, weight=10.0)
            self.active_cluster_idx = idx
            cl = self.detection_clusters[idx]
            self.best_gps = cl.get("total_gps") or cl["best_gps"]
            self.total_detections += 1
            self._new_detection_flag = True
            msg = f"FAKE detection at {est_lat:.6f}, {est_lon:.6f} → cluster #{cl['id']}"
            print(f"[FAKE] {msg}")

        elif action == "resume":
            self._cancel_investigate()
            self.landing_phase = None
            self.landing_target = None
            self.flight_mode = "MANUAL"
            msg = "Resumed manual control"
            print("[RESUME] Manual mode")

        elif action == "rtl":
            if self._passive_block("RTL"):
                return {"ok": False, "message": "Blocked (passive mode)"}
            if self.master:
                self.master.mav.command_long_send(
                    self.master.target_system, self.master.target_component,
                    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 6, 0, 0, 0, 0, 0)
                self._cancel_investigate()
                self.landing_phase = None
                self.landing_target = None
                self.flight_mode = "RTL"
                msg = "RTL command sent — returning to launch"
                print("[RTL] Return to launch")
            else:
                msg = "No MAVLink connection"

        return {"ok": True, "message": msg}

    def _find_cluster_by_id(self, cluster_id):
        if cluster_id is None:
            return None
        for i, c in enumerate(self.detection_clusters):
            if c["id"] == cluster_id:
                return i
        return None

    def _cancel_investigate(self):
        self.investigating = False
        self.investigate_phase = None
        self.investigate_target = None
        self.investigate_cluster_idx = None
        if self.flight_mode == "INVESTIGATING":
            self.flight_mode = "MANUAL"

    # --- Mode execution ---
    def execute_mode(self):
        if self.flight_mode == "INVESTIGATING" and self.investigate_target:
            target = self.investigate_target
            dist = self._gps_distance(self.lat, self.lon, target[0], target[1])

            if self.investigate_phase == "approaching":
                self.send_to_gps(target[0], target[1])
                if dist < 5.0:
                    self.investigate_phase = "descending"
                    print(f"[INVESTIGATE] Near target, descending to {self.investigate_alt}m")

            elif self.investigate_phase == "descending":
                self.send_to_gps(target[0], target[1], self.investigate_alt)
                if abs(self.alt - self.investigate_alt) < 2.0:
                    self.investigate_phase = "observing"
                    self.investigating = True
                    # Capture snapshot
                    frame = self.get_frame()
                    if frame is not None:
                        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        self.snapshot_jpeg = jpeg.tobytes()
                    print("[INVESTIGATE] Observing — classify: Y=dummy, I=interest, X=false positive")

            elif self.investigate_phase == "observing":
                self.send_to_gps(target[0], target[1], self.investigate_alt)

        elif self.flight_mode == "LANDING" and self.landing_target:
            target = self.landing_target
            dist = self._gps_distance(self.lat, self.lon, target[0], target[1])

            if self.landing_phase == "flying_to":
                self.send_to_gps(target[0], target[1])
                if dist < 3.0:
                    self.landing_phase = "descending"
                    self.send_land()
                    print("[LAND] Over landing point, descending...")

            elif self.landing_phase == "descending":
                if self.alt < 0.5:
                    self.landing_phase = "landed"
                    self.flight_mode = "MANUAL"
                    print("[LAND] LANDED!")

    # --- State for web dashboard ---
    def get_state(self):
        clusters = []
        for c in self.detection_clusters:
            gps = c.get("total_gps") or c.get("best_gps")
            clusters.append({
                "id": c["id"],
                "lat": gps[0] if gps else None,
                "lon": gps[1] if gps else None,
                "count": c["detection_count"],
            })

        new_det = self._new_detection_flag
        self._new_detection_flag = False

        return {
            "lat": self.lat,
            "lon": self.lon,
            "alt": self.alt,
            "yaw": math.degrees(self.yaw),
            "speed": self.groundspeed,
            "battery": self.battery_v,
            "armed": self.armed,
            "drone_mode": self.drone_mode,
            "flight_mode": self.flight_mode,
            "total_detections": self.total_detections,
            "clusters": clusters,
            "logged": self.logged_items,
            "active_cluster": self.active_cluster_idx,
            "inv_target": list(self.investigate_target) if self.investigate_target else None,
            "land_target": list(self.landing_target) if self.landing_target else None,
            "search_poly": self.search_poly_gps,
            "has_snapshot": self.snapshot_jpeg is not None,
            "new_detection": new_det,
            "heartbeat_age": time.time() - self.last_heartbeat if self.last_heartbeat else 999,
        }

    # --- Main loop ---
    def run(self):
        print("\n[RUN] Main loop started. Open dashboard in browser.")
        print("[RUN] Terminal keys: W/S=fwd/back A/D=left/right R/F=up/down Q/E=yaw")
        print()

        # Start keyboard thread for terminal control
        kb_thread = threading.Thread(target=self._keyboard_loop, daemon=True)
        kb_thread.start()

        while self.running:
            try:
                # Retry MAVLink connection if lost
                if not self.master and time.time() - self.last_heartbeat > 5:
                    self._connect_mavlink()

                # Read telemetry
                self.drain_mavlink()

                # Get frame and run CV (throttled)
                now = time.time()
                if self.cv_interval == 0 or (now - self.last_cv_time >= self.cv_interval):
                    self.last_cv_time = now
                    if self.alt > 1.0:  # only detect when airborne
                        frame = self.get_frame()
                        if frame is not None:
                            found, u, v, conf = self.eyes.detect_in_image(frame)
                            # Draw detection overlay
                            if found:
                                cv2.rectangle(frame,
                                    (int(u - 20), int(v - 20)),
                                    (int(u + 20), int(v + 20)),
                                    (0, 255, 0), 2)
                                cv2.putText(frame, f"{conf:.2f}",
                                    (int(u - 20), int(v - 25)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                                self.calculate_target_gps(u, v)
                            # HUD overlay
                            cv2.putText(frame, f"ALT: {self.alt:.1f}m  {self.drone_mode}",
                                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                            cv2.putText(frame, f"DET: {self.total_detections}  {self.flight_mode}",
                                (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                            if self.best_gps:
                                cv2.putText(frame, f"EST: {self.best_gps[0]:.6f}, {self.best_gps[1]:.6f}",
                                    (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 255), 1)
                            # Encode for stream
                            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            with self._frame_lock:
                                self._stream_jpeg = jpeg.tobytes()
                    else:
                        # On ground — still stream camera
                        frame = self.get_frame()
                        if frame is not None:
                            cv2.putText(frame, "ON GROUND", (10, 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            with self._frame_lock:
                                self._stream_jpeg = jpeg.tobytes()

                # Execute flight mode (investigate / land)
                self.execute_mode()

                time.sleep(0.02)  # ~50Hz loop

            except KeyboardInterrupt:
                print("\n[EXIT] Shutting down...")
                self.running = False
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(1)

        self.cleanup()

    def _keyboard_loop(self):
        """Terminal keyboard control (WASD flight + commands)."""
        try:
            if sys.platform == 'win32':
                import msvcrt
                while self.running:
                    if msvcrt.kbhit():
                        ch = msvcrt.getch()
                        if ch == b'\xe0' or ch == b'\x00':
                            msvcrt.getch()  # skip extended key
                            continue
                        self._handle_key(ch.decode('ascii', errors='ignore').lower())
                    time.sleep(0.05)
            else:
                import select
                import tty
                import termios
                old = termios.tcgetattr(sys.stdin)
                try:
                    tty.setcbreak(sys.stdin.fileno())
                    while self.running:
                        if select.select([sys.stdin], [], [], 0.05)[0]:
                            ch = sys.stdin.read(1).lower()
                            self._handle_key(ch)
                finally:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
        except Exception as e:
            print(f"[KB] Keyboard thread error: {e}")

    def _handle_key(self, key):
        speed = 3.0
        climb = 2.0
        yaw_rate = 30.0

        if key == ' ':
            self.send_arm()
        elif key == 'w':
            self.send_velocity(speed, 0, 0)
        elif key == 's':
            self.send_velocity(-speed, 0, 0)
        elif key == 'a':
            self.send_velocity(0, -speed, 0)
        elif key == 'd':
            self.send_velocity(0, speed, 0)
        elif key == 'r':
            self.send_velocity(0, 0, -climb)
        elif key == 'f':
            self.send_velocity(0, 0, climb)
        elif key == 'q':
            self.send_velocity(0, 0, 0, -yaw_rate)
        elif key == 'e':
            self.send_velocity(0, 0, 0, yaw_rate)
        elif key == 't':
            self.send_takeoff(self.args.takeoff_alt)
        elif key == '\x1b':  # ESC
            self.running = False

    def cleanup(self):
        print("[CLEANUP] Shutting down...")
        self.running = False
        if self.httpd:
            self.httpd.shutdown()
        if self.eyes:
            self.eyes.release()
        if self.master:
            self.master.close()
        print("[CLEANUP] Done.")


# ========================================================================
# Entry point
# ========================================================================
def main():
    parser = argparse.ArgumentParser(description="SAR Ground Station")
    parser.add_argument('--port', type=int, default=8090, help='Web dashboard port')
    parser.add_argument('--fps', type=float, default=4, help='CV inference rate limit (0=unlimited)')
    parser.add_argument('--cluster-dist', type=float, default=30, help='Cluster grouping distance (m)')
    parser.add_argument('--takeoff-alt', type=float, default=20, help='Takeoff altitude (m)')
    parser.add_argument('--passive', action='store_true', help='Passive mode: camera+detection+stream only, ZERO commands sent to Cube')
    args = parser.parse_args()

    flight = PiFlight(args)
    flight.run()


if __name__ == "__main__":
    main()
