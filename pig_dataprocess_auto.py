import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os
from glob import glob

# === CONFIG ===
DEBUG = False
BAND_WIDTH = 6
DIST_MIN = 60
PROMINENCE_FACTOR = 1.0
HEIGHT_FACTOR = 0.3
TARGET_WIDTH = 1024
BRIGHTNESS_THRESHOLD = 5
INPUT_FOLDER = "./example_images"
OUTPUT_FOLDER = "./output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Gather all .jpg images ===
image_files = sorted(glob(os.path.join(INPUT_FOLDER, "*.jpg")))

# === Process each image ===
for image_path in image_files:
    print(f"\n📷 Processing: {os.path.basename(image_path)}")
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Could not load image: {image_path}")
        continue

    # Resize image
    original_height, original_width = image.shape[:2]
    resize_scale = TARGET_WIDTH / original_width
    target_height = int(original_height * resize_scale)
    image = cv2.resize(image, (TARGET_WIDTH, target_height), interpolation=cv2.INTER_AREA)

    # Manual cropping
    print("🖼️ Select the Region of Interest (ROI), then press ENTER or SPACE.")
    roi = cv2.selectROI("Select ROI", image, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    x_start, y_start, w, h = roi
    cropped = image[y_start:y_start + h, x_start:x_start + w]

    # Save cropped image
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    cropped_path = os.path.join(OUTPUT_FOLDER, base_name + "_cropped.jpg")
    cv2.imwrite(cropped_path, cropped)
    print(f"💾 Cropped image saved to: {cropped_path}")

    # Upscale and grayscale
    scale_factor = 2
    upscaled = cv2.resize(cropped, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)
    gray[gray < BRIGHTNESS_THRESHOLD] = 0
    img_height, img_width = gray.shape

    # Signal extraction across entire height
    signal_profile = gray.mean(axis=0)
    signal_std = np.std(signal_profile)
    signal_mean = np.mean(signal_profile)
    adaptive_prominence = PROMINENCE_FACTOR * signal_std
    adaptive_height = signal_mean + HEIGHT_FACTOR * signal_std

    peaks, _ = find_peaks(signal_profile,
                          distance=DIST_MIN,
                          prominence=adaptive_prominence,
                          height=adaptive_height)

    if len(peaks) < 2:
        print("⚠️ Too few peaks detected. Skipping this image.")
        continue

    # Segment signal by midpoints
    region_boundaries = []
    left_bound = max(0, peaks[0] - (peaks[1] - peaks[0]) // 2)
    region_boundaries.append(left_bound)
    for i in range(len(peaks) - 1):
        midpoint = (peaks[i] + peaks[i + 1]) // 2
        region_boundaries.append(midpoint)
    right_bound = min(img_width, peaks[-1] + (peaks[-1] - peaks[-2]) // 2)
    region_boundaries.append(right_bound)

    # Top-most bright pixel in each segment
    highest_peaks = []
    intensity_threshold = 0
    for i in range(len(region_boundaries) - 1):
        x0 = region_boundaries[i]
        x1 = region_boundaries[i + 1]
        subregion = gray[:, x0:x1]
        min_y = img_height
        min_x_local = -1
        for x_local in range(subregion.shape[1]):
            col = subregion[:, x_local]
            valid_y = np.where(col > intensity_threshold)[0]
            if len(valid_y) > 0:
                y = np.min(valid_y)
                if y < min_y:
                    min_y = y
                    min_x_local = x_local
        if min_x_local >= 0 and min_y < img_height:
            x_global = x0 + min_x_local
            highest_peaks.append((x_global, min_y))

    # Manual y-scale
    y_bottom = float(input(f"Enter the Y-axis value at the bottom of the image [{base_name}]: "))
    y_top = float(input(f"Enter the Y-axis value at the top of the image [{base_name}]: "))
    raw_y_coords = [pt[1] for pt in highest_peaks]
    converted_y = (1 - np.array(raw_y_coords) / img_height) * (y_top - y_bottom) + y_bottom

    # Annotate image
    labeled_img = upscaled.copy()
    for i, (x, y) in enumerate(highest_peaks):
        cv2.circle(labeled_img, (x, y), 5, (255, 0, 0), -1)
        cv2.putText(labeled_img, f"{i+1}", (x - 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    for i in range(len(region_boundaries)):
        cv2.line(labeled_img, (region_boundaries[i], 0), (region_boundaries[i], img_height), (0, 255, 0), 1)
    for i in range(len(region_boundaries) - 1):
        label_x = (region_boundaries[i] + region_boundaries[i + 1]) // 2
        cv2.putText(labeled_img, f"{i+1}", (label_x - 5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2, cv2.LINE_AA)

    # Save labeled image and CSV
    final_img_path = os.path.join(OUTPUT_FOLDER, base_name + "_labeled.jpg")
    final_csv_path = os.path.join(OUTPUT_FOLDER, base_name + ".csv")
    cv2.imwrite(final_img_path, labeled_img)

    mean_converted_y = converted_y.mean()
    std_converted_y = converted_y.std()
    df_final = pd.DataFrame({
        'Heartbeat #': list(range(1, len(highest_peaks) + 1)),
        'Y Position (pixels)': raw_y_coords,
        f'Converted Y Position ({y_bottom}–{y_top} scale)': converted_y
    })
    df_stats = pd.DataFrame({
        'Heartbeat #': ['Mean', 'Std'],
        'Y Position (pixels)': [None, None],
        f'Converted Y Position ({y_bottom}–{y_top} scale)': [mean_converted_y, std_converted_y]
    })
    df_final_with_stats = pd.concat([df_final, df_stats], ignore_index=True)
    df_final_with_stats.to_csv(final_csv_path, index=False)

    print(f"✅ Done: Saved labeled image and CSV for {base_name}")

print("\n🎉 All images processed.")
