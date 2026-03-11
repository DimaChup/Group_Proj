# NICE_TO_HAVE — Improvement Backlog

> Ideas never deleted, only reordered. Score = Impact / Effort.

| # | Feature | Status | Impact (1-5) | Effort (1-5) | Score | Module |
|---|---------|--------|:---:|:---:|:---:|--------|
| 1 | Split main.py run() into state handler methods | NOT STARTED | 4 | 2 | 2.0 | main.py |
| 2 | Split simple_simulator.py into UI + estimation + flight modules | NOT STARTED | 5 | 4 | 1.3 | simple_simulator |
| 3 | Replace hardcoded 0.62 lat scale with cos(lat) | NOT STARTED | 3 | 1 | 3.0 | main.py |
| 4 | Add state transition logging | NOT STARTED | 4 | 1 | 4.0 | main.py |
| 5 | Fix self.investigating init bug in pi_flight.py | NOT STARTED | 5 | 1 | 5.0 | pi_flight.py |
| 6 | HTML-escape CLI args in stream page (XSS fix) | NOT STARTED | 3 | 1 | 3.0 | main.py |
| 7 | Use json.dumps for /cmd response (injection fix) | NOT STARTED | 3 | 1 | 3.0 | main.py |
| 8 | Z mode: offset centering for safety (don't hover over casualty) | NOT STARTED | 5 | 3 | 1.7 | simple_simulator |
| 9 | Retrain model with real flight photos | NOT STARTED | 5 | 3 | 1.7 | vision.py |
| 10 | INT8 quantized TFLite export | NOT STARTED | 3 | 2 | 1.5 | models/ |
| 11 | Extract duplicate Kalman code to shared method | NOT STARTED | 2 | 1 | 2.0 | simple_simulator |
| 12 | Add investigate timeout (120s → auto-cancel) | NOT STARTED | 3 | 1 | 3.0 | simple_simulator |
| 13 | Auto-dump recording CSV on exit | NOT STARTED | 3 | 1 | 3.0 | simple_simulator |
| 14 | pi_9 resolution test script | NOT STARTED | 3 | 2 | 1.5 | tests/ |
| 15 | Handle graceful shutdown on network disconnect | NOT STARTED | 3 | 2 | 1.5 | main.py |
| 16 | Split handle_command() into per-command methods | NOT STARTED | 2 | 1 | 2.0 | pi_flight.py |
