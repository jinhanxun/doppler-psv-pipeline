# Automated Pipeline for Doppler PSV Quantification
**Minimal‑input, bias‑reduced spectral envelope tracking for Doppler ultrasound.**

This repository contains a lightweight Python pipeline to quantify **peak systolic velocity (PSV)** from spectral Doppler images.  
It standardizes image scale, isolates the trace via user‑guided cropping, converts to grayscale, performs **vertical intensity averaging**, and detects cycle‑wise PSV using `scipy.signal.find_peaks`.  
Outputs include **annotated images** with detected PSV points and **CSV tables** with pixel coordinates, calibrated velocities, and per‑cycle summary statistics.

---

## ✨ Features
- Minimal user input (scale markers + cropping); no manual PSV picking
- Vertical intensity averaging for robust spectral envelope extraction
- Adaptive peak detection per cardiac cycle via `find_peaks`
- Batch processing of folders of images
- Reproducible **CSV outputs** and **annotated PNGs/JPGs**
- Tunable detection parameters (band width, prominence, distance, etc.)

---

## 🗂 Repository structure
```
doppler-psv-pipeline/
├─ pig_dataprocess_auto.py        # main script (your provided file)
├─ README.md
├─ requirements.txt
├─ LICENSE
├─ .gitignore
└─ examples/
   └─ images/                     # put a few example JPG/PNG images here (optional)
```
> Feel free to rename the script to `psv_pipeline.py` later; keeping your original filename for now.

---

## 🚀 Quick start
1. **Install dependencies**
   ```bash
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Organize images**  
   Put input images (e.g., `.jpg`, `.png`) into a folder, e.g., `data/input/`.

3. **Run the script**
   ```bash
   python pig_dataprocess_auto.py
   ```
   By default the script reads images from a configured input folder and writes **annotated images** and **CSV files** to an output folder.  
   (If your current version uses constants at the top of the file—e.g., `INPUT_FOLDER`, `OUTPUT_FOLDER`, `TARGET_WIDTH`, `BAND_WIDTH`, `DIST_MIN`, `PROMINENCE_FACTOR`, `HEIGHT_FACTOR`, `BRIGHTNESS_THRESHOLD`, etc.—adjust them there.)

> **Tip:** If you'd like a CLI with flags (e.g., `--input`, `--output`), I can refactor the script into a module and add an argparse interface.

---

## ⚙️ Configuration knobs
Common parameters (found near the top of the script):
- `TARGET_WIDTH` – standardize all images to this width before processing
- `BAND_WIDTH` – number of vertical pixels for local intensity band averaging
- `DIST_MIN` – minimum horizontal distance (pixels) between detected PSV peaks
- `PROMINENCE_FACTOR`, `HEIGHT_FACTOR` – adaptive thresholds for `find_peaks`
- `BRIGHTNESS_THRESHOLD` – ignore very dark pixels/noise in the spectral region
- (plus any of your `INPUT_FOLDER`, `OUTPUT_FOLDER`, cropping and scale settings)

---

## 📦 Outputs
For each input image, the pipeline produces:
- **`<name>_labeled.<ext>`** – image annotated with PSV detections/markers
- **`<name>_psv.csv`** – per‑cycle table of:
  - `X Position (pixels)`
  - `Y Position (pixels)`
  - `Converted Y Position (velocity units)` *(after calibration)*
- **`<name>_psv_summary.csv`** (if applicable) – means/SD across cycles

The script prints a progress log in the terminal and summarizes what was saved.

---

## ✅ Validation
The method has been validated on multiple independent batches of ultrasound images to confirm **consistency** and **robustness**. For manuscript use, add a short “Validation” subsection describing datasets, inter/intra‑batch results, and any inter‑operator checks if applicable.

---

## 🧪 Reproducibility notes
- Fix `TARGET_WIDTH` and all thresholds/scale markers for a given dataset.
- Keep a small `examples/images/` set to sanity‑check future changes.
- Use `DEBUG = True` in the script to visualize intermediate steps (if provided).


