# CV Standalone Report -- Workflow & Scoring Document

**Report**: Standalone Computer Vision Report
**Current score**: Not yet scored
**Target**: 85+ (professional technical paper quality)
**Pages**: ~15-20
**File**: `report/cv_report/main.tex`

---

## What This Report Is

A dedicated deep-dive into the computer vision pipeline for the SAR drone project. Consolidates all CV-related content from the goldmine into one self-contained professional document covering:

1. Detection model (YOLOv8n architecture, single-class design)
2. Training pipeline (3 dataset generations, augmentation, Colab)
3. Edge inference (TFLite vs NCNN vs Ultralytics, benchmarks)
4. Detection performance (altitude envelope, blur, probability model)
5. Sensor calibration (FOV, lens distortion, BGR discovery)
6. GPS target estimation (GSD, pixel-to-GPS, CEP50)
7. Real-world validation (DJI video, Pi bench testing)
8. Future work

---

## Scoring History

| Version | Date | Quality | Completeness | Clarity | Total |
|---------|------|---------|-------------|---------|-------|
| v1 | pending | -- | -- | -- | -- |

---

## Key Metrics (must appear)

- mAP50 = 0.995
- 50/50 detection, 0.966 confidence
- TFLite: 206.5ms / 4.8 FPS
- NCNN: 72ms / 9 FPS full pipeline
- CEP50 = 2.3m GPS accuracy
- 366 training images (300 syn + 16 real + 50 neg)
- FOV: 49.3 deg HFOV (Pi), 54.4 deg (DJI)
- Lens RMS: 0.399
- Model: 3.2M params, 11.7MB TFLite

## Compilation

```bash
cd "report/cv_report"
pdflatex -interaction=nonstopmode main.tex && biber main && pdflatex main.tex && pdflatex main.tex
```

## Improvement Checklist
- [ ] Compiles cleanly
- [ ] All figure references resolve
- [ ] All citations resolve
- [ ] Key metrics summary table present
- [ ] Score v1
- [ ] Iterate based on scoring
