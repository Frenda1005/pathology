# pathology
ccrcc vs chromo
# ccRCC vs Chromophobe (Philips iSyntax) – Patch + Feature Pipeline

This repo contains a reproducible pipeline to:
1) read a Philips iSyntax slide in Docker (PixelEngine tools),
2) extract macro image,
3) detect the red ROI rectangle (scanner annotation) on macro,
4) map macro ROI -> level-0 coordinates,
5) tile patches inside ROI (level 2, 256×256 equiv),
6) QC with contact sheet,
7) filter tissue tiles,
8) extract deep features (ResNet50),
9) train slide-level classifier with Leave-One-Slide-Out CV.

---

## Prerequisites

- Docker image that contains Philips PixelEngine + `/work/PythonTools/*`
- A mounted slide like:
  `/work/tmp_slide/<SLIDE_ID>.isyntax`
- Macro image extracted (or use dump macro script below)

Python packages for ML steps:
- torch, torchvision
- pandas, numpy, pillow, tqdm
- scikit-learn

Install:
```bash
pip install -r requirements.txt


