# Simple SAR Mission Simulator

Quick, lightweight simulator to test state machine logic without running full Mission Planner.

## 🚀 Quick Start

### Step 1: Create Your Map (Do this ONCE)

```bash
python map_setup_tool.py
```

**Interactive Controls:**
- Press `1`: Draw Search Area (click points, press ENTER to close polygon)
- Press `2`: Draw No-Fly Zone (click points, press ENTER to close polygon)
- Press `3`: Place Start Point (single click)
- Press `4`: Place Transit Waypoints (click multiple, press ENTER when done)
- Press `5`: Place Search Waypoints (click multiple, press ENTER when done)
- Press `6`: Place Dummy Location (single click)
- Press `S`: **SAVE** configuration to `mission_config.json`
- Press `L`: Load existing configuration
- Press `C`: Clear all
- Press `Q`: Quit

**Tip:** Save your map with `S` and you'll never have to redraw it!

### Step 2: Run Simulation

```bash
python simple_simulator.py
```

The simulator will:
- ✅ Load your saved map
- ✅ Run the state machine automatically
- ✅ Show drone movement in real-time
- ✅ Detect PLB activation (5-15 seconds into search)
- ✅ Detect target when in range
- ✅ Calculate safe landing spot (5-10m from target)
- ✅ Return home
- ✅ Log all state transitions
- ✅ Detect no-fly zone violations

## 📊 What Gets Simulated

### Mission States
1. **INIT** → Initialize
2. **TAKEOFF** → Climb to target altitude
3. **TRANSIT_TO_SEARCH** → Fast flight to search area
4. **SEARCH_BROAD** → Follow search pattern, looking for target
5. **PLB_RECEIVED** → PLB signal activated (5-15 sec into search)
6. **SEARCH_FOCUSED** → Focus search in PLB area
7. **TARGET_DETECTED** → Visual detection of casualty
8. **APPROACH_TARGET** → Fly towards target
9. **DESCEND** → Lower altitude for verification
10. **VERIFY_TARGET** → Hover and confirm target
11. **CALCULATE_LANDING** → Find safe landing spot (5-10m away)
12. **APPROACH_LANDING** → Fly to landing spot
13. **LAND** → Land and stop
14. **DEPLOY_PAYLOAD** → Drop first aid kit
15. **RETURN_TO_HOME** → Fly back to start point
16. **LAND_AT_HOME** → Land at home
17. **MISSION_COMPLETE** → Done!

### Detection Model
- **Detection Range:** 50 units around drone
- **Detection Probability:** 30% per timestep when in range
- **PLB Timing:** Randomly activates 5-15 seconds into search

### Safety Checks
- ⚠️ No-fly zone violations detected and logged
- ⚠️ Altitude limits (can be added)
- ⚠️ Geofencing (boundary checks)

## 🎯 Benefits

1. **Fast Iteration:** Test logic in seconds, not minutes
2. **No Hardware:** Pure simulation, no drone needed
3. **Easy Debugging:** Clear state transitions, visual feedback
4. **Repeatable:** Same map, different runs
5. **Safe Testing:** Try risky scenarios without consequences

## 📝 Output Files

- `mission_config.json` - Your saved map configuration
- State transition logs printed to console
- Violation warnings in real-time

## 🔧 Next Steps

Once you're happy with the logic:
1. Refine state transitions
2. Add more complex behaviors
3. Integrate into Mission Planner simulation
4. Test on real hardware

## 💡 Tips

- **Start Simple:** Draw a small, simple map first to test
- **Iterate Fast:** Modify states, re-run quickly
- **Watch for Violations:** Check console for no-fly zone warnings
- **Multiple Runs:** Same map, different detection probabilities = different outcomes

## 🐛 Troubleshooting

**"mission_config.json not found"**
→ Run `map_setup_tool.py` first and press `S` to save

**Drone not moving**
→ Make sure you placed waypoints (steps 4 and 5)

**Target never detected**
→ Place dummy close to search waypoints, or increase detection range

**Simulation too fast/slow**
→ Adjust `plt.pause(0.01)` in `simple_simulator.py`

## 📚 Files

- `map_setup_tool.py` - Interactive map creator
- `simple_simulator.py` - State machine simulator
- `mission_config.json` - Your saved map (auto-generated)
- `SIMULATOR_README.md` - This file
