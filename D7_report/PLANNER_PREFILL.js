// D7 Planner Prefill — generated from Apollo's running-context
// Usage: open browser console on planner.html, paste this, press Enter.
// Then reload the page — data loads from localStorage.

const prefill = {

  // ═══════════════════════════════════════════════════════════════════
  // MATRIX VIEW (m-{question}-{lens})
  // ═══════════════════════════════════════════════════════════════════

  // ── 1a: Roles and responsibilities ──────────────────────────────
  "m-1a-influence": "Formally allocated CV responsibility, but in practice took on far more: full CV pipeline (detection to GPS), simulation of entire mission, safety-critical geofencing, progressive test ladder. By building the simulation and test infrastructure, set the standard for how the team approached validation and safety — influenced the team to think in terms of progressive confidence-building rather than jumping straight to flight.",
  "m-1a-develop": "Grew from a pure technical contributor (CV specialist) into a de facto systems integrator — building simulation, safety layers, dashboards, and test infrastructure. Learned that taking on more work yourself is not the same as developing as an engineer; enabling others matters more. Also developed camera calibration, GPS estimation, and post-processing skills that weren't in the original role.",
  "m-1a-different": "Would define role boundaries more explicitly at the start and resist the urge to absorb unowned tasks. Would establish a delegation framework — when tasks aren't being driven, actively assign and follow up rather than silently taking them on. Would also separate 'technical lead' from 'individual contributor' and explicitly manage the time split.",
  "m-1a-www": "Formal CV role was clear from the start. Taking on simulation work (even though it was beyond scope) produced a thoroughly tested system that verified all R01-R12 requirements and gave the team a backup. The CV pipeline — detection to GPS coordinate estimation with attitude correction — was a genuinely novel contribution.",
  "m-1a-ebi": "Should have raised the implicit role expansion earlier with the team. The fact that simulation, safety, dashboards, and test infrastructure were all 'Apollo's side things' meant no one else understood or could maintain them. Should have been explicit: 'I'm taking on X, Y, Z — does the team agree this is the right use of my time?'",

  // ── 1b: Proudest contributions ──────────────────────────────────
  "m-1b-influence": "The simulation work demonstrated that a thorough virtual environment could substitute for limited real hardware access. It influenced the team's confidence — they could see the full mission working end-to-end before ever flying. The CV-to-GPS pipeline became the interface that Robin's state machine consumed, directly enabling integration.",
  "m-1b-develop": "Proudest of squeezing maximum learning from extremely limited data — one real flight video from Sid was used for model evaluation, retraining, FOV calibration, GPS accuracy benchmarking, and ground truth extraction. Developed the skill of making the most of constrained resources, which is a transferable engineering competency.",
  "m-1b-www": "The simulation was thoroughly tested (thousands of runs), simulated camera blur, GPS drift, and real-world failure modes. The CV pipeline achieved mAP50=0.995 on retrained model. GPS estimation pipeline included pitch/roll correction, altitude compensation, multiple averaging techniques benchmarked against ground truth. Everything came together on demo day without prior real-hardware testing of the full pipeline — which validates the simulation quality.",
  "m-1b-ebi": "(inferred) Could have documented the simulation and CV pipeline more accessibly for teammates, so they could understand and contribute to it rather than treating it as a black box. The 2508-line simple_simulator.py and 1411-line main.py were essentially single-person codebases.",
  "m-1b-different": "",

  // ── 1c: Different focus in future ───────────────────────────────
  "m-1c-influence": "",
  "m-1c-develop": "Would develop team-enablement skills: structured delegation, knowledge transfer sessions, pair programming. Instead of building alone when frustrated, would invest time in bringing others up to speed. Would also develop conflict resolution skills — when Edward and Zian weren't proactive, finding ways to engage them rather than working around them.",
  "m-1c-different": "Would focus more on team enablement and less on solo technical output. Would run the progressive test ladder step-by-step instead of accepting that 'time didn't allow.' Would front-load team process discussions: ground rules, conflict resolution protocols, communication norms. Would explicitly manage the split between technical work and coordination.",
  "m-1c-www": "",
  "m-1c-ebi": "When the team got dismayed after failed flight days, retreated into solo simulation work rather than actively pulling Edward and Zian in or finding ways to keep them engaged. Pattern of 'capability over enablement' — building alone instead of building the team up. This is the core self-criticism.",

  // ── 2a: Team structure ──────────────────────────────────────────
  "m-2a-influence": "After first team meeting, roles were explicitly allocated: Harish (hardware/comms), Zian (path planning), Robin (state machines), Apollo+Edward (CV, with Apollo delegating model training to Edward). Apollo's influence on structure was informal — he didn't change the allocation but his scope grew to encompass simulation, safety, dashboards, and test infrastructure, effectively becoming the systems integrator without that being discussed.",
  "m-2a-develop": "Learned that initial role allocation is necessary but insufficient — roles need to be revisited as the project evolves. The structure didn't adapt when some members weren't self-directed. Also learned that explicit structure (who does what, by when) matters more in a team where not everyone is equally proactive.",
  "m-2a-different": "Would establish regular role reviews — not just 'what are you working on' but 'is this allocation still right given what we've learned?' Would also create explicit interfaces between roles (not just technical APIs but human handoff protocols).",
  "m-2a-www": "Initial allocation was sensible and discussed explicitly. The CV-to-state-machine interface between Apollo and Robin worked well — defined API (detect_in_image returns found, x, y, conf) remained stable across 3 model versions.",
  "m-2a-ebi": "Structure didn't adapt when Edward and Zian were less proactive. No formal mechanism for redistributing work or escalating concerns about unequal contribution. The team was really Apollo and Robin driving things forward, with others doing assigned work but not self-directing.",

  // ── 2b: Most impactful elements of team working ─────────────────
  "m-2b-influence": "The close coordination between Apollo and Robin during integration was the most impactful positive element. Apollo provided captured images and GPS coordinates via a defined interface; Robin's state machine consumed the CV output. Ideas were discussed as colleagues. This pairing drove the project forward more than any other dynamic.",
  "m-2b-develop": "Learned that proactive members compensate for passive ones, but this creates fragility. Also learned that hardware problems outside the team's control (faulty equipment on first two flight days) can demolish morale regardless of how well-prepared the software is.",
  "m-2b-different": "",
  "m-2b-www": "Apollo-Robin collaboration: close contact during integration, defined interfaces, ideas discussed as equals. Team managed to produce a working system for demo day despite only ~1.5 functional flight days. The progressive test ladder concept (even though never fully executed) provided a safety framework.",
  "m-2b-ebi": "Communication with Edward could have been better — they trusted each other to do their jobs but didn't check in enough. When the team got demotivated after failed flight days, no one actively addressed the morale problem — people just retreated to their own work. Edward and Zian were not proactive but also weren't actively engaged or delegated to meaningfully.",

  // ── 2c: What to change in future ────────────────────────────────
  "m-2c-influence": "",
  "m-2c-develop": "Would develop explicit team management skills: structured stand-ups, written commitments, accountability check-ins. Would learn to recognise when someone isn't being proactive and intervene early rather than absorbing their work.",
  "m-2c-different": "Would front-load team-building and process discussions. Would establish written objectives, deadlines, and accountability mechanisms from week 1. When members aren't proactive, would actively delegate with clear deliverables and deadlines rather than doing things solo. Would push for more flight days or earlier hardware testing to avoid the 'everything works in simulation but we've never tested real hardware' gap.",
  "m-2c-www": "",
  "m-2c-ebi": "Should have communicated more openly about workload imbalance. Should have found ways to keep Edward and Zian engaged when morale dropped. Should have established regular progress reviews with specific deliverables rather than trusting everyone to self-manage. The complaint about hardware should have been raised earlier and more formally.",

  // ── 3a: How contributions drove team forward ────────────────────
  "m-3a-influence": "Built the simulation that verified all R01-R12 requirements end-to-end, giving the team confidence that their approach would work. Created the CV pipeline that became the core detection capability. Built safety infrastructure (geofencing, RC override guard, progressive test ladder) that made autonomous flight responsible. Provided Robin with a stable API for state machine integration. Created dashboards and monitoring tools that the whole team could use on flight days.",
  "m-3a-develop": "Grew from individual contributor to systems-level thinker. The simulation forced thinking about every failure mode — GPS drift, camera blur, wind, detection altitude limits. This systematic approach to anticipating problems was a significant personal development.",
  "m-3a-different": "",
  "m-3a-www": "Everything came together on demo day without prior real-hardware testing of the full pipeline — this validates the simulation approach. The team delivered a working MVP despite only ~1.5 functional flight days. The CV pipeline (detection, GPS estimation, multiple averaging techniques, attitude correction) was a genuine technical achievement given the data constraints.",
  "m-3a-ebi": "(inferred) Contributions were individually excellent but created a single point of failure — if Apollo was unavailable, no one else understood the simulation, CV pipeline, or safety systems. Should have paired with teammates on critical subsystems.",

  // ── 3b: What to add/re-focus in future ──────────────────────────
  "m-3b-influence": "",
  "m-3b-develop": "Would develop the discipline of knowledge transfer: writing documentation that enables others to contribute, not just documentation that records decisions. Would also develop the ability to let go of technical work and focus on coordination when that's what the team needs most.",
  "m-3b-different": "Would add structured knowledge sharing sessions — weekly 15-minute demos where each member shows what they built. Would re-focus from 'build everything myself' to 'build the team's capability.' Would run the full progressive test ladder step-by-step rather than jumping to demo day. Would invest in team process (stand-ups, retros, written commitments) from the start.",
  "m-3b-www": "",
  "m-3b-ebi": "Would invest more in enabling teammates rather than compensating for their gaps. Would prioritise real hardware testing earlier — even if it means less polished simulation. Would address team dynamics issues (unequal contribution, morale) proactively rather than retreating into solo work.",

  // ── 4a: What others did that helped ─────────────────────────────
  "m-4a-influence": "",
  "m-4a-develop": "Robin's close collaboration during integration was the most impactful support — discussing ideas as colleagues, consuming the CV API, and providing state machine context that shaped the CV output format. Robin suggesting the repulsive force concept for NFZ avoidance was a genuinely good idea that Apollo developed further. Harish's hardware setup work (when it eventually worked) was essential.",
  "m-4a-different": "(inferred) Would have benefited from more structured support — regular code reviews, pair programming, or explicit feedback on the simulation and CV pipeline.",
  "m-4a-www": "Robin and Apollo were the two proactive members and their close coordination was the project's strongest dynamic. Robin's FSM pushback (if it happened) and the repulsive force suggestion showed healthy intellectual exchange. The team's collective effort on demo day brought everything together.",
  "m-4a-ebi": "Would have valued more proactive engagement from Edward and Zian — not just doing assigned tasks but driving things forward independently. Would have benefited from the course providing working hardware from the start, like all other teams had.",

  // ── 4b: What Apollo did to help others ──────────────────────────
  "m-4b-influence": "Provided Robin with a stable API (detect_in_image -> found, x, y, conf) that remained consistent across 3 model versions, allowing Robin to build the state machine without worrying about CV internals. Built dashboards and monitoring tools (passive_watch, diagnostics) that the whole team could use. Created the progressive test ladder that provided a safety framework for everyone. Shared simulation results to build team confidence.",
  "m-4b-develop": "Learned that the most helpful thing isn't always building more — sometimes it's building less but explaining more. The interface definition between CV and state machine was a small piece of work that had outsized impact on Robin's productivity.",
  "m-4b-different": "(inferred) Could have helped more by actively mentoring Edward and Zian rather than just delegating tasks. Could have shared the CV work more openly so Edward's model training contribution could have been integrated.",
  "m-4b-www": "The stable CV API unblocked Robin's state machine work. The simulation gave the whole team a way to validate their subsystems. Building the interface was 'quite expensive' (attitude correction, altitude compensation, error handling) but it meant Robin never had to think about CV internals. Passive watch dashboard enabled safe flight-day monitoring.",
  "m-4b-ebi": "Could have communicated more with Edward about CV work to avoid the situation where Edward trained a model that wasn't used. Could have been more explicit about sharing knowledge rather than just sharing outputs. When the team got demotivated, could have actively worked to re-engage people rather than just pushing forward alone.",


  // ═══════════════════════════════════════════════════════════════════
  // CARD VIEW (c-{id}, c-{id}-www, c-{id}-ebi)
  // ═══════════════════════════════════════════════════════════════════

  "c-1a": "Formally allocated CV responsibility, shared with Edward (delegated model training). In practice, implicitly took on: full CV pipeline (detection to GPS estimation with attitude correction), entire mission simulation, safety-critical geofencing and RC override guard, progressive test ladder (41 scripts in 6 categories), dashboards and monitoring tools (passive_watch, diagnostics, pi_flight web ground station), camera calibration and post-processing tools. Roles didn't formally change but Apollo's scope grew continuously as unowned tasks accumulated. Spent 3-4x expected hours, largely on simulation.",
  "c-1a-www": "Initial role allocation was clear and sensible. Taking on simulation beyond scope produced a system that verified all R01-R12 requirements. The CV pipeline (detection to GPS with pitch/roll correction, altitude compensation, multiple averaging techniques) was a genuine novel contribution that became the integration interface with Robin's state machine.",
  "c-1a-ebi": "Should have raised the implicit role expansion with the team explicitly. Should have distinguished 'technical lead' from 'individual contributor' and managed the time split. The fact that simulation, safety, dashboards, and tests were all 'Apollo's side things' created a single point of failure.",

  "c-1b": "Most proud of: (1) The simulation — thoroughly tested, thousands of runs, simulated blur/drift/failure modes, verified all R01-R12. (2) The CV-to-GPS estimation pipeline — given only one real flight video from Sid, managed to create a realistic GPS position estimate from camera detections. Used that single video for model evaluation, retraining (mAP50=0.995), FOV calibration, GPS accuracy benchmarking, and ground truth extraction. Squeezed maximum learning from extremely limited data.",
  "c-1b-www": "Simulation quality validated when everything came together on demo day without prior real-hardware testing of full pipeline. CV pipeline achieved mAP50=0.995 on retrained model. Multiple averaging techniques (inverse variance weighting, Kalman filter, spatial clustering) benchmarked against deduced ground truth. FOV calibrated to 54.4 deg HFOV. GPS estimation included pitch/roll correction and altitude compensation.",
  "c-1b-ebi": "The 2508-line simulator and 1411-line main.py were essentially single-person codebases that no one else could maintain. Could have documented the pipeline more accessibly for teammates. Pride in technical achievement may have reinforced the solo-working pattern.",

  "c-1c": "Would focus on team enablement over solo technical output. Would run the progressive test ladder step-by-step rather than jumping to demo. Would front-load team process: ground rules, conflict resolution, communication norms, written commitments. Would manage the split between technical work and coordination explicitly. Would engage Edward and Zian actively when they weren't self-directing, rather than absorbing their work.",
  "c-1c-www": "",
  "c-1c-ebi": "Core self-criticism: pattern of retreating into solo work when things got hard — capability over enablement, building alone instead of building the team up. When Edward and Zian weren't proactive, did things himself rather than finding ways to engage them. When team got demotivated after failed flight days, retreated into simulation rather than addressing morale.",

  "c-2a": "Team of 5: Apollo, Robin, Harish, Edward, Zian. Explicitly discussed at first meeting: Harish = hardware/comms, Zian = path planning, Robin = state machines, Apollo+Edward = CV (Apollo delegated training to Edward). Structure was discussed explicitly at the start but didn't adapt as the project evolved. In practice, Robin and Apollo were the two proactive drivers; Edward and Zian did assigned work but weren't self-directed; Harish focused on hardware. Apollo's scope grew implicitly to include simulation, safety, dashboards, tests.",
  "c-2a-www": "Roles were allocated explicitly based on interests and skills. The Apollo-Robin interface (CV API consumed by state machine) was well-defined and stable. Initial structure was sensible.",
  "c-2a-ebi": "Structure should have been revisited as the project evolved. No mechanism for redistributing work when contribution was unequal. No regular role reviews or explicit discussion of who was doing what by when.",

  "c-2b": "Most impactful positive: Apollo-Robin close coordination during integration — defined API, discussed ideas as colleagues, consumed each other's outputs. Most impactful negative: faulty hardware on first two practice flight days destroyed morale and wasted prepared test scripts. Edward and Zian not being self-directed meant the two proactive members carried a disproportionate load. Communication with Edward could have been better.",
  "c-2b-www": "Apollo-Robin collaboration was strong: close contact, defined interfaces, ideas exchanged as equals. Team delivered working MVP for demo despite only ~1.5 functional flight days. Robin's repulsive force suggestion for NFZ was excellent — Apollo developed it further over several days.",
  "c-2b-ebi": "Should have addressed morale explicitly after failed flight days rather than each person retreating to their own work. Should have communicated more with Edward about CV work. Should have established accountability mechanisms for the less proactive members.",

  "c-2c": "Would front-load team-building and process discussions. Establish written objectives, deadlines, accountability from week 1. When members aren't proactive, actively delegate with clear deliverables rather than doing things solo. Push for earlier hardware access/testing. Run regular stand-ups and retrospectives. Address morale issues directly rather than compensating through individual effort.",
  "c-2c-www": "",
  "c-2c-ebi": "Should have raised workload imbalance openly. Should have found ways to keep Edward and Zian engaged. Should have established regular progress reviews with specific deliverables. Complaint about hardware should have been raised earlier and more formally. Should have invested in team process rather than assuming everyone would self-manage.",

  "c-3a": "Built simulation verifying all R01-R12 end-to-end. Created CV pipeline (detection to GPS with attitude correction) that became core detection capability. Built safety infrastructure (geofence, RC override guard, progressive test ladder). Provided Robin with stable API for state machine integration. Created dashboards and monitoring tools for flight days. Built and benchmarked multiple model variants. Everything came together on demo day — validates the simulation-first approach.",
  "c-3a-www": "Demo day success without prior full-pipeline real testing validates simulation quality. Working MVP delivered despite ~1.5 functional flight days. CV pipeline (3 model variants, attitude correction, multiple averaging techniques) was technically strong. Safety infrastructure (geofence with cv2.pointPolygonTest, RC override guard, progressive test ladder) was comprehensive.",
  "c-3a-ebi": "Contributions created a single point of failure. Should have paired with teammates on critical subsystems. Should have prioritised real hardware testing earlier even if it meant less polished simulation.",

  "c-3b": "Would add structured knowledge sharing (weekly demos). Re-focus from 'build everything' to 'build team capability.' Run full progressive test ladder step-by-step. Invest in team process from the start. Enable teammates rather than compensating for their gaps. Prioritise real hardware testing earlier.",
  "c-3b-www": "",
  "c-3b-ebi": "Would invest in enabling teammates rather than building alone. Would address team dynamics proactively. Would balance simulation polish with real-world testing. Would develop conflict resolution and delegation skills.",

  "c-4a": "Robin's close collaboration was the most impactful support — discussing ideas as colleagues, the repulsive force concept for NFZ avoidance, and consuming the CV API for state machine integration. Harish's hardware work (when it eventually functioned) was essential. The course provided flight days (though hardware was faulty initially). Sid's single flight video, despite being the only real data available, enabled model retraining and GPS estimation benchmarking.",
  "c-4a-www": "Robin-Apollo coordination was the project's strongest dynamic. Robin's repulsive force suggestion showed healthy intellectual exchange. Team collectively persevered through hardware frustrations and delivered on demo day.",
  "c-4a-ebi": "Would have valued more proactive engagement from Edward and Zian. Would have benefited from working hardware from the start (like all other teams). Would have appreciated more structured support — code reviews, pair programming.",

  "c-4b": "Provided Robin with stable CV API (detect_in_image -> found, x, y, conf) consistent across 3 model versions. Built dashboards (passive_watch, diagnostics, pi_flight) for the whole team. Created progressive test ladder as safety framework. Shared simulation results to build confidence. Built the interface layer (attitude correction, altitude compensation) that was 'quite expensive' but meant Robin never had to think about CV internals.",
  "c-4b-www": "Stable API unblocked Robin's state machine work. Simulation gave the team a validation tool. Interface definition had outsized impact relative to its size. Passive watch dashboard enabled safe flight-day monitoring.",
  "c-4b-ebi": "Could have communicated more with Edward to avoid the unused model situation. Could have shared knowledge, not just outputs. Could have actively re-engaged the team when morale dropped rather than pushing forward alone. Could have mentored Edward and Zian rather than just delegating tasks."
};

// ─── LOAD INTO LOCALSTORAGE ──────────────────────────────────────
localStorage.setItem('d7-planner-v2', JSON.stringify(prefill));
console.log(`Loaded ${Object.keys(prefill).length} prefill entries into localStorage.`);
console.log('Reload the page to see the data in the planner.');
