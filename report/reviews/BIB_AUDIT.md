# Bibliography Audit

Generated: 2026-04-03

## Summary

| Metric | Count |
|--------|-------|
| Unique bib entries in `references.bib` | 128 |
| Unique bib entries in `extra_refs.bib` | 25 |
| Combined unique bib keys (both files) | 131 |
| Unique citation keys across all .tex files | 97 |
| Citations in **active** sections (included in main.tex) | 62 |
| Citations only in **inactive** sections (not in main.tex) | 35 |
| **Missing bib entries** (cited but no bib key) | **1** |
| **Dead references** (bib entry never cited) | **35** |
| **Duplicate entries** (same paper, different keys) | **17 pairs** |
| Entries duplicated across both bib files | 22 keys |
| Placeholder entries (TODO/FIXME/???) | 0 |
| Entries with incomplete required fields | 0 |

---

## 1. Missing Bib Entry (cited but not defined)

| Citation Key | Used In |
|---|---|
| `ultralytics2023yolov8` | `sections/vision_standalone.tex` |

**Note**: `vision_standalone.tex` is NOT included in `main.tex`, so this won't cause a compile error currently. However, there is a near-match: `jocher2023yolov8` in `extra_refs.bib` and `yolov8` in `references.bib` -- both reference the same Ultralytics YOLOv8 software. If `vision_standalone.tex` is ever activated, change the citation to `yolov8` or `jocher2023yolov8`.

---

## 2. Dead References (in bib files, never cited anywhere)

35 bib entries are never cited in any .tex file:

| Key | File | Notes |
|-----|------|-------|
| `agrawal2020hotl_uav` | both | Operator-in-the-loop UAV |
| `albanese2022low_power_uav` | both | Edge AI on UAVs |
| `araujo2023tvv_ras` | both | Testing/validation systematic review |
| `cabreira2019cpp_survey` | both | Coverage path planning survey |
| `chang2023gps_denied_review` | both | GPS-denied navigation review |
| `coombes2017boustrophedon` | both | Boustrophedon in wind |
| `coombes2018polygon_decomposition` | both | Polygon decomposition for CPP |
| `david2021tflite` | both | TFLite Micro (duplicate of `david2021tensorflow`) |
| `du2023multi_uav_astar` | both | Multi-UAV A* path planning |
| `fevgas2022cpp_energy` | both | Energy-efficient CPP |
| `gps_accuracy` | refs | A-GPS book |
| `gugan2023path_planning` | both | Drone path planning review |
| `hayat2020multi_objective_sar` | both | Multi-objective SAR planning |
| `hitl` | refs | Endsley human-automation (cited as `endsley1999loa` instead) |
| `jacob2018quantization` | refs | Quantization for inference |
| `jocher2023yolov8` | both | Ultralytics YOLOv8 (duplicate of `yolov8`) |
| `khan2022uav_disaster` | both | UAV disaster response |
| `kim2022geofencing` | both | UAV geofencing |
| `koopman2018av_validation` | both | AV safety validation framework |
| `lin2022gps_denied_vision` | both | Vision-based GPS-denied localization |
| `mavlink` | refs | MAVLink protocol (v1) |
| `mishra2020drone_sar` | both | Drone SAR (duplicate of `mishra2020`) |
| `missionplanner` | refs | Mission Planner (duplicate of `missionplanner2024`) |
| `mjpeg` | refs | RFC 2435 (duplicate of `rfc2435`) |
| `numpy` | refs | NumPy library |
| `redmon2016yolo` | refs | YOLOv1 (duplicate of `yolohistory`) |
| `scaramuzza2011visual` | refs | Visual odometry |
| `seraj2023hitl_drl_uav` | both | HITL deep RL for UAV |
| `shakhatreh2019uav_civil` | both | UAV civil applications survey |
| `sora` | refs | JARUS SORA (duplicate of `jarus2019sora`) |
| `terven2023yolo_review` | both | YOLO architecture review |
| `tobin2017domain` | refs | Domain randomization (duplicate of `domainrand`) |
| `toma2022edge_ml_uav` | both | Edge ML for UAV/IoT |
| `wang2023uav_yolov8` | both | UAV-YOLOv8 small object detection |
| `zhao2024yolov8n_uav` | both | YOLOv8n for UAV images |

Of these 35 dead entries, **13 are duplicates** of entries that ARE cited (marked in Section 3 below). The remaining **22 are genuinely unused** references that could be cited to strengthen the report or removed.

---

## 3. Duplicate Entries (same paper, different keys)

17 pairs of entries refer to the same paper (verified by matching DOI or title):

| Key Used (cited) | Key Unused (dead) | Paper |
|---|---|---|
| `yolov8` | `jocher2023yolov8` | Ultralytics YOLOv8 |
| `yolohistory` | `redmon2016yolo` | YOLOv1 (CVPR 2016) |
| `synthdata` | `tremblay2018training` | Training with Synthetic Data |
| `domainrand` | `tobin2017domain` | Domain Randomization (IROS 2017) |
| `covpath` | `galceran2013survey` | Coverage Path Planning Survey |
| `kalman1960` | `kalman1960new` | Kalman Filter (both cited in different sections!) |
| `murphy2014` | `murphy2014disaster` | Disaster Robotics book (both cited!) |
| `mishra2020` | `mishra2020drone_sar` | Drone SAR (Computer Communications) |
| `david2021tensorflow` | `david2021tflite` | TFLite Micro (MLSys 2021) |
| `jarus2019sora` | `sora` | JARUS SORA guidelines |
| `ardupilot_mavproxy` | `mavproxy` | MAVProxy (both cited!) |
| `missionplanner2024` | `missionplanner` | Mission Planner |
| `raspberrypi5` | `rpi5` | Raspberry Pi 5 (both cited!) |
| `ncnn2017` | `ncnn` | NCNN framework (both cited!) |
| `mjpeg` | `rfc2435` | RFC 2435 JPEG/RTP (`rfc2435` cited, `mjpeg` not) |
| `lin2014coco` | `coco_dataset` | MS COCO dataset (both cited!) |
| `hitl` | (standalone) | Endsley 2017 -- never cited, different paper from `endsley1999loa` |

**Warning**: 6 duplicate pairs have BOTH keys cited in different sections. This will produce duplicate entries in the bibliography:
- `kalman1960` (field_results) vs `kalman1960new` (target_localisation, gps_estimation_deep)
- `murphy2014` (introduction, design_rationale) vs `murphy2014disaster` (state_machine)
- `ardupilot_mavproxy` (system_architecture, field_results, design_rationale) vs `mavproxy` (hardware_platform, comms_architecture)
- `raspberrypi5` (multiple sections) vs `rpi5` (hardware_platform)
- `ncnn2017` (future_work) vs `ncnn` (cv, field_results, inference_architecture, system_description)
- `lin2014coco` (design_rationale) vs `coco_dataset` (introduction, model_training, model_comparison)

---

## 4. Cross-File Duplication

22 bib keys appear in BOTH `references.bib` and `extra_refs.bib` (exact same key, duplicate definition):

`agrawal2020hotl_uav`, `albanese2022low_power_uav`, `araujo2023tvv_ras`, `cabreira2019cpp_survey`, `chang2023gps_denied_review`, `coombes2017boustrophedon`, `coombes2018polygon_decomposition`, `du2023multi_uav_astar`, `fevgas2022cpp_energy`, `gugan2023path_planning`, `hayat2020multi_objective_sar`, `khan2022uav_disaster`, `kim2022geofencing`, `koopman2018av_validation`, `lin2022gps_denied_vision`, `lyu2023uav_sar_survey`, `seraj2023hitl_drl_uav`, `shakhatreh2019uav_civil`, `terven2023yolo_review`, `toma2022edge_ml_uav`, `wang2023uav_yolov8`, `zhao2024yolov8n_uav`

The `references.bib` comment on line 929 says "Merged from extra_refs.bib (2026-03-27) -- Duplicates excluded" but these 22 keys were NOT excluded. BibLaTeX will silently pick one definition (usually the last loaded, i.e., `extra_refs.bib`), which happens to be identical content, so no data loss -- but it is messy.

**Recommendation**: Either delete `extra_refs.bib` (since all its entries are now in `references.bib`) or remove the 22 duplicated entries from `references.bib`.

---

## 5. Entry Quality Assessment

**All entries have complete required fields.** Every entry has author, title, and year. Articles have journal fields. Conference papers have booktitle fields.

Specific quality notes:
- `@software{jocher2023yolov8}` uses the `@software` type which some BibTeX backends don't support (BibLaTeX handles it fine)
- `@manual{arm_a76}` uses `howpublished` for URL which is non-standard for `@manual` but works
- `settles2009active` is typed as `@book` but has an `institution` field (should be `@techreport`)
- `golden2006hypothermia` has `year=2002` but key says `2006` -- the book was published in 2002, so the key is misleading
- Several `@misc` entries rely on `howpublished={\url{...}}` which works but `url={...}` is cleaner with BibLaTeX
- `lin2014coco` and `yolov3` cite arXiv preprints -- these have since been published in conferences/journals

---

## 6. Placeholder Check

No placeholder entries found. No TODO, FIXME, ???, or XXX markers in either bib file.

---

## 7. Inactive Section Citations

35 citation keys appear ONLY in sections not included in `main.tex` (00_abstract, 01_introduction, 02_system_architecture, 03_hardware_platform, 04_computer_vision, 05_path_planning, 06_state_machine, 07_target_localisation, 08_ground_station, 09_simulation, 15_conclusion, introduction, steeple, vision_standalone). These sections appear to be earlier drafts replaced by newer sections.

If these sections are permanently retired, their unique citations can be considered dead weight in the bibliography.

---

## Recommended Actions (priority order)

1. **Fix 6 duplicate-key citation pairs** where both keys are actively cited -- consolidate to one key per paper to avoid duplicate bibliography entries
2. **Clean up `extra_refs.bib`** -- either delete it entirely (all 25 entries already exist in `references.bib`) or remove the 22 duplicated keys from `references.bib`
3. **Add `ultralytics2023yolov8`** to bib if `vision_standalone.tex` will be activated, or change citation to `yolov8`
4. **Fix `settles2009active`** entry type from `@book` to `@techreport`
5. **Fix `golden2006hypothermia`** key (year mismatch: key says 2006, entry says 2002)
6. **Consider citing or removing** the 22 genuinely unused references that are not duplicates
