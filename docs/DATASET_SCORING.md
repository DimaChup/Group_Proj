# Dataset v3 — Objective Scoring

> Generated 2026-04-03. Brutally honest assessment against project detection needs.
>
> Reference docs: `docs/NEEDS_VS_CAPABILITIES.md` (R03, R07), `docs/CV_BEST_PRACTICES.md`,
> `config.py` (TARGET_ALT=35m, VERIFY_ALT=15m, SEARCH_SPEED_MPS=10m/s).

---

## Dataset Facts

| Metric | Value |
|--------|-------|
| Total images | 700 |
| Synthetic (close 15-20m) | 96 |
| Synthetic (mid 20-35m) | 188 |
| Synthetic (far 35-50m) | 142 |
| Synthetic (multi-target) | 74 |
| Real labelled frames | 100 |
| Negatives (empty labels) | 100 |
| Image size | 640x640 |
| Train / val split | 560 / 140 (80/20) |
| Val includes real images | Yes (17 real in val) |
| Classes | 1 (dummy) |

---

## Scoring Matrix

| Criterion | Score | Evidence | Gap |
|---|---|---|---|
| **Dataset size (500-1000 target)** | **8** | 700 images. Within the recommended 500-1000 range from CV_BEST_PRACTICES.md. v2 had only 366. | Solid. Could push to 800-900 with more real frames but diminishing returns. |
| **Altitude coverage (15-50m)** | **7** | Three tiers: close (96, 15-20m), mid (188, 20-35m), far (142, 35-50m). Avg bbox heights: close=0.199, mid=0.123, far=0.079. Covers TARGET_ALT=35m and VERIFY_ALT=15m. | Mid-range is over-represented (38% of synthetic). Close (15-20m) is the thinnest band at 19% despite being critical for VERIFY/DESCENDING states. Real frames only cover one altitude band (avg bbox_h=0.157, ~mid range). No real frames from high altitude. |
| **Real:synthetic ratio (25-50% real target)** | **6** | 100/700 = 14.3%. v2 had 16/366 = 4.4%, so a 3x improvement. CV_BEST_PRACTICES.md says 25-50% is target for robust outdoor detection. | Still below the 25% minimum. 100 real frames is a strong absolute number, but they all come from a single DJI flight (one dummy, one field, one lighting condition, one altitude). Need real frames from multiple flights/conditions to hit 25%+ meaningfully. |
| **Negative ratio (15-25% target)** | **7** | 100/700 = 14.3%. CV_BEST_PRACTICES.md target is 15-25%. | Just below the 15% floor. More importantly: zero hard negatives. No frames where the model previously made false positive detections are included. Hard negatives are the highest-impact subset. |
| **Train/val split (80/20)** | **9** | 560/140 split. train.txt and val.txt are separate files. Val includes all categories (23 close, 31 mid, 23 far, 24 multi, 17 real, 22 neg). Real images present in both sets. | Near perfect. Minor issue: dataset.yaml originally pointed train/val to the same `images/` directory (the generator's default). Actual YAML now uses train.txt/val.txt which is correct. |
| **Augmentation diversity (10+ types)** | **8** | 10 augmentation types implemented: (1) HSV color jitter, (2) gamma correction, (3) brightness/contrast, (4) Gaussian noise, (5) motion blur, (6) Gaussian blur, (7) random shadows, (8) haze/fog, (9) barrel distortion, (10) perspective warp. | Meets the 10-type target exactly. Probabilities are reasonable (motion blur at 20% is low given it's the "#1 failure mode" per CV_BEST_PRACTICES.md -- should be 40-50%). Missing: random erasing/cutout (listed in best practices as rank 6). |
| **Background diversity** | **5** | 100 map.jpg crops + 50 DJI video frame crops = 150 backgrounds. Two sources only: one satellite image and one flight video. | CV_BEST_PRACTICES.md says "minimum 20+ distinct background images". 150 crops sounds high but they come from only 2 source images. Map.jpg is a single field. DJI video is one flight over the same field. Model will overfit to this specific grass/path texture. No Google Earth screenshots, no other fields, no urban areas, no varied terrain. This is the weakest criterion. |
| **Target appearance variety** | **6** | 1 dummy.png (single pose, single outfit). 4 accessories (pants, tshirt, backpack, cone) placed near dummy at 40% probability. Multi-target images at 15% (74 images with 2-3 dummies). | All synthetic targets are the same dummy.png rotated and scaled. No pose variation (lying vs sitting vs standing). No clothing variety on the dummy itself. Accessories add visual clutter but don't change the target's appearance. Real frames are all the same physical dummy from the same angle (overhead). One-dummy problem: model may learn "this specific orange shape" rather than "person-shaped object on ground". |
| **Motion blur simulation** | **7** | Directional kernel with random angle 0-360 degrees, kernel size 3-15px odd. Applied to 20% of images post-composite. | Implementation is correct (directional, not just Gaussian). But 20% probability is too low. CV_BEST_PRACTICES.md ranks motion blur as #1 failure mode. At SEARCH_SPEED_MPS=10m/s and TARGET_ALT=35m, motion blur is present in most real frames. Should be 40-60%. Also: blur is applied to the entire composite, not just the image (correct -- blur affects everything during real flight). Kernel size range 3-15px is reasonable but untested against real blur at 10m/s. |
| **Domain gap mitigation** | **4** | Alpha blending uses dummy.png's native alpha channel (256 unique alpha values, but only 0.7% of pixels are soft-edge -- mostly hard cutout). No background-aware color/brightness matching. No Gaussian blur on composite edges. Post-composite augmentations (noise, blur, jitter) partially mask the pasting artifacts. | This is the second weakest criterion. CV_BEST_PRACTICES.md specifically calls out three techniques: (1) Gaussian blur on alpha mask edges -- NOT implemented (dummy.png has hard edges, generator does not add soft blending), (2) background-aware color matching -- NOT implemented (no brightness normalization of dummy to local background), (3) multiple background sources -- partially done (2 sources, needs 5+). The model is at high risk of learning "rectangular brightness discontinuity = dummy" rather than actual target features. |

---

## Summary

| Category | Score | Weight | Notes |
|----------|:-----:|:------:|-------|
| Dataset size | 8 | Medium | Good |
| Altitude coverage | 7 | High | Adequate but close-range under-represented |
| Real:synthetic ratio | 6 | Critical | 14% vs 25% target |
| Negative ratio | 7 | High | Just below 15% floor, no hard negatives |
| Train/val split | 9 | Medium | Correct |
| Augmentation diversity | 8 | High | Meets target, motion blur probability too low |
| Background diversity | 5 | Critical | Only 2 source images |
| Target appearance variety | 6 | High | Single dummy, no pose variation |
| Motion blur simulation | 7 | Critical | Right technique, too infrequent |
| Domain gap mitigation | 4 | Critical | Missing edge blending and color matching |

**Overall: 6.7 / 10**

---

## Critical Gaps (ordered by impact on real-world detection)

### 1. Domain gap (score 4) -- highest risk of field failure

The generator pastes dummy.png onto backgrounds with hard edges and no brightness
matching. The model will learn the pasting artifact, not the target. This is the #1
reason synthetic-trained models fail outdoors.

**Fix (30 min code change):**
- Add Gaussian blur on alpha mask edges (5-7px kernel) in `paste_target()`
- Add local brightness matching (normalize dummy mean brightness to background patch)
- Both techniques are documented in CV_BEST_PRACTICES.md Section 5 with code snippets

### 2. Background diversity (score 5) -- overfitting to one field

150 background crops from 2 source images. The model will memorize this field's grass
texture. Any other field (or even this field under different lighting) will degrade
performance.

**Fix (1 hour):**
- Add 10+ Google Earth screenshots of UK fields at similar scale
- Add frames from other drone videos (YouTube SAR footage, DJI stock footage)
- Target: 5+ visually distinct background sources

### 3. Real:synthetic ratio (score 6) -- 14% vs 25% target

100 real frames is a good absolute number but they're all from one flight. The model
sees the same dummy, same field, same lighting, same altitude range in every real frame.

**Fix (requires next flight):**
- Label frames from passive_watch.py during manual flights (different altitudes, angles)
- Each flight adds a new lighting/altitude/background condition
- Target: 175+ real frames (25% of 700) from 2+ flights

### 4. Motion blur probability (score 7) -- under-applied

20% application rate for the #1 failure mode. At 10 m/s search speed and 35m altitude,
most real frames have some motion blur.

**Fix (5 min config change):**
- Increase motion blur probability from 20% to 45%
- Consider altitude-dependent blur: more blur at lower altitudes (larger pixel displacement)

---

## What v3 Does Well

1. **Size**: 700 images is within the sweet spot. v2 had 366.
2. **Altitude tiers**: Close/mid/far split with physically-correct pixel scaling.
3. **Train/val split**: Proper 80/20 with all categories represented in val.
4. **Augmentation count**: 10 types covering the most important failure modes.
5. **Multi-target**: 74 images with 2-3 dummies (realistic for multi-casualty scenarios).
6. **Accessories**: Pants, tshirt, backpack, cone add visual clutter around the target.
7. **Real frames**: 6x more than v2 (100 vs 16). Properly tiled from detection CSV.
8. **Image size**: 640x640 matches TFLite inference resolution (correcting the v2 mismatch).

---

## Verdict

Dataset v3 is a solid improvement over v2 (366 images, 4.4% real, no altitude tiers,
no multi-target). It will likely achieve high mAP on validation. **The risk is field
performance**: the domain gap and background diversity issues mean the model may
struggle with real outdoor images it hasn't seen before.

The two highest-priority fixes (edge blending + color matching) are code changes in
`generate_dataset_v3.py` that take under an hour and require no new data collection.
They should be applied before the next training run.
