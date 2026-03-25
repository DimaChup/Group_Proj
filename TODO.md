# TODO — Remaining Work

## 1. Clean Main Settings (3 presets)

Bake winning flag combos so `python main.py` just works:

**Setting 1 — Full Mission (50m)**
```
python main.py --search-area --no-descend --speed 5 --no-turn-realign-diag --nfz-carrot --transit flight_plans/transit.json --alt 50
```

**Setting 2 — Full Mission (35m)**
```
python main.py --search-area --no-descend --speed 5 --no-turn-realign-diag --nfz-carrot --transit flight_plans/transit.json --alt 35
```

**Setting 3 — Dry Run (no SITL)**
```
python main.py --dry-run --search-area --no-turn-realign-diag --alt 35
```

Goal: remove experimental flags, make these the defaults on a clean branch.

## 2. Vision / CV Model Optimization

- [ ] Lower confidence threshold (try 0.3, 0.25) — more detections at cost of false positives
- [ ] Test NCNN backend on Pi (`cv_models/sar_v2_1088/ncnn/`) — expected ~15 FPS
- [ ] FP16 XNNPACK on Pi — potential 2x speedup (~10 FPS)
- [ ] Threaded pipeline — overlap capture + inference (+20-30%)
- [ ] Larger model (YOLOv8s) — more accurate, benchmark on Pi
- [ ] Resolution tuning — test 416x416 or 320x320 export

## 3. Train Vision on Items of Interest

- [ ] Collect training images of items of interest (not just dummy)
- [ ] Label with `tools/label_tool.py --full`
- [ ] Add to dataset_v2 alongside existing dummy images
- [ ] Retrain with multi-class: dummy, person, cone, etc.
- [ ] Update vision.py to return class label alongside confidence

## 4. Path Planning Optimization

### Focus Area (PLB beacon)
- [ ] Tighter margins (currently 1/10th swath) — verify full coverage
- [ ] Consider spiral-in pattern for small focus areas
- [ ] Altitude: should focus area use lower altitude for better detection?

### Area of Interest
- [ ] After marking items of interest, generate a focused pattern around them
- [ ] Cluster nearby IOIs and create mini search areas
- [ ] Priority ordering: revisit highest-confidence IOIs first

### Margins → config.py
- [ ] Move `margin = step_px // 2` (normal search) to `config.SEARCH_MARGIN_FACTOR = 2`
- [ ] Move `margin = step_px // 10` (focus area) to `config.FOCUS_MARGIN_FACTOR = 10`
- [ ] Planner reads from config, new planners get same values automatically

## 5. Code Simplification

- [ ] Remove experimental flags: `--nfz-repel`, `--nfz-slow`, `--smooth-bezier`, `--smooth-extra`
- [ ] Bake `--nfz-carrot` + `--no-turn-realign-diag` + `--no-descend` as defaults
- [ ] Remove `state_machine.py` (descend variant) if not needed
- [ ] Clean up dead code paths from removed flags

## 6. Flight Day Prep

- [ ] Test on Pi with real camera + Cube (bench, no props)
- [ ] Outdoor GPS fix test
- [ ] Manual flight with passive detection
- [ ] Full autonomous bench test
- [ ] Configure Cube firmware geofence in Mission Planner (FENCE_ENABLE, SSSI polygon)
