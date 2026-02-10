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

📦 Step-by-Step Pipeline
0️⃣ Dump Macro Image
Generate a macro preview image if you don’t already have one:
bash scripts/00_dump_macro.sh \
  /work/tmp_slide/<SLIDE_ID>.isyntax \
  /work/tmp_slide/<SLIDE_ID>_MACROIMAGE.jpg
1️⃣ Detect Tissue ROI on Macro
Detect tissue region on macro image and map coordinates to Level-0 resolution.
python3 scripts/01_detect_roi_bbox.py \
  --macro /work/tmp_slide/<SLIDE_ID>_MACROIMAGE.jpg \
  --w0 153606 \
  --h0 91142 \
  --out_overlay /work/tmp_slide/<SLIDE_ID>_macro_detected_roi.png
Output
Printed to terminal:
MACRO roi bbox (mx0,my0,mx1,my1)
LEVEL0 bbox (X0,Y0,X1,Y1)
👉 Use the LEVEL0 coordinates in Step 2
2️⃣ Extract Patches Inside ROI
Insert bbox numbers from Step 1.
bash scripts/02_patch_extract_roi.sh \
  /work/tmp_slide/<SLIDE_ID>.isyntax \
  28424 0 109898 83220 \
  2 1024
Parameters
Argument	Meaning
2	Pyramid level
1024	Tile size in Level-0 units
Output
256×256 tiles at Level-2 resolution
3️⃣ QC — Visualize Patch Grid
Verify patch coverage:
python3 scripts/03_make_patch_grid.py \
  --tile_dir /work/<SLIDE_ID>_<RUNID> \
  --out /work/tmp_slide/<SLIDE_ID>_grid.png
This helps confirm extraction coverage is correct.
4️⃣ Filter Tissue-Only Patches
Remove background or blank tiles:
python3 scripts/04_filter_tissue_tiles.py \
  --tile_dir /work/<SLIDE_ID>_<RUNID> \
  --out_dir /work/tmp_slide/<SLIDE_ID>_tissue_only
5️⃣ Organize Dataset
Example for ccRCC slides:
mkdir -p /work/dataset/slides/ccrcc/<SLIDE_ID>

cp /work/tmp_slide/<SLIDE_ID>_tissue_only/*.png \
   /work/dataset/slides/ccrcc/<SLIDE_ID>/
Expected Directory Structure
dataset/
  slides/
    ccrcc/
      slide1/
      slide2/
    chromophobe/
      slideA/
6️⃣ Extract Deep Features (ResNet50)
python3 scripts/06_extract_features_resnet50.py \
  --root /work/dataset/slides \
  --out_csv /work/dataset/features/features_resnet50.csv \
  --out_dir /work/dataset/features
Produces
Patch embeddings
Slide-aggregated feature CSV
7️⃣ Train Slide Classifier (Leave-One-Out CV)
python3 scripts/07_train_slide_loo.py \
  --csv /work/dataset/features/features_resnet50.csv \
  --pos_label ccrcc
Outputs
AUC
Accuracy
Predictions
/work/dataset/features/slide_predictions_loo.csv

