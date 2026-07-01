"""
HAM10000 Dataset Statistics
Analyzes metadata, image properties, class distribution, and data quality.
"""

import os
import sys
import random
import warnings
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
METADATA    = os.path.join(BASE_DIR, "dataset", "HAM10000_metadata.csv")
IMAGE_DIR   = os.path.join(BASE_DIR, "data", "raw")          # images live here
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

CLASS_NAMES = {
    "nv":    "Melanocytic nevi",
    "mel":   "Melanoma",
    "bkl":   "Benign keratosis",
    "bcc":   "Basal cell carcinoma",
    "akiec": "Actinic keratosis / Bowen's disease",
    "vasc":  "Vascular lesions",
    "df":    "Dermatofibroma",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _wrap(items, width=80):
    """Wrap a list of strings into a fixed-width console block."""
    line, lines = "", []
    for item in items:
        if len(line) + len(item) + 2 > width:
            lines.append(line)
            line = item
        else:
            line = (line + ", " + item).lstrip(", ")
    if line:
        lines.append(line)
    return "\n".join(lines)


def _iter(iterable, desc=""):
    return tqdm(iterable, desc=desc, ncols=90) if HAS_TQDM else iterable


def _save_fig(name):
    path = os.path.join(REPORTS_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


# ── 1. Load ────────────────────────────────────────────────────────────────────

def load_dataset():
    df = pd.read_csv(METADATA)

    # Collect image files
    img_map = {}
    if os.path.isdir(IMAGE_DIR):
        for root, _, files in os.walk(IMAGE_DIR):
            for f in files:
                if f.lower().endswith((".jpg", ".jpeg", ".png")):
                    stem = os.path.splitext(f)[0]
                    img_map[stem] = os.path.join(root, f)

    df["image_path"] = df["image_id"].map(img_map)
    missing = df[df["image_path"].isna()]["image_id"].tolist()

    print(f"Total metadata records : {len(df)}")
    print(f"Total images found     : {len(img_map)}")
    if missing:
        print(f"Missing image files    : {len(missing)}")
        if len(missing) <= 20:
            for m in missing:
                print(f"  - {m}")
    else:
        print("Missing image files    : 0")

    return df, img_map


# ── 2. Dataset size ────────────────────────────────────────────────────────────

def dataset_size(df):
    n_classes = df["dx"].nunique()
    print(f"\nDataset Name : HAM10000")
    print(f"Total Images : {len(df)}")
    print(f"Classes      : {n_classes}")
    print(f"Image Format : JPG")
    print(f"Color Mode   : RGB")
    return n_classes


# ── 3. Class distribution ──────────────────────────────────────────────────────

def class_distribution(df):
    counts  = df["dx"].value_counts()
    total   = counts.sum()
    largest = counts.idxmax()
    smallest = counts.idxmin()
    ratio   = counts.max() / counts.min()

    print("\nClass Distribution")
    print("-" * 40)
    for cls, cnt in counts.items():
        print(f"  {cls:<8}: {cnt:>5}  ({cnt/total*100:.2f}%)")
    print(f"\n  Largest class  : {largest} ({counts[largest]})")
    print(f"  Smallest class : {smallest} ({counts[smallest]})")
    print(f"  Imbalance ratio: {ratio:.1f}x")

    # Bar chart
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(counts.index, counts.values,
                  color=plt.cm.tab10.colors[:len(counts)])
    ax.set_title("HAM10000 – Class Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Lesion Type")
    ax.set_ylabel("Number of Images")
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                str(val), ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    p = _save_fig("class_distribution.png")
    print(f"\n  Saved → {p}")

    # Pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=plt.cm.tab10.colors[:len(counts)],
        startangle=140,
    )
    ax.set_title("HAM10000 – Class Distribution (Pie)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    _save_fig("class_distribution_pie.png")

    return counts


# ── 4 & 5. Resolution + channels ──────────────────────────────────────────────

def image_properties(df):
    paths = df["image_path"].dropna().tolist()
    if not paths:
        print("\n[Image Properties] No images found – skipping.")
        return {}

    widths, heights, channels = [], [], Counter()
    corrupted = []

    for path in _iter(paths, desc="Scanning images"):
        try:
            with Image.open(path) as img:
                w, h = img.size
                widths.append(w)
                heights.append(h)
                mode = img.mode
                if mode == "RGB":
                    channels["RGB"] += 1
                elif mode in ("L", "LA"):
                    channels["Grayscale"] += 1
                elif mode == "RGBA":
                    channels["RGBA"] += 1
                else:
                    channels[mode] += 1
        except Exception:
            corrupted.append(os.path.basename(path))

    # Resolution
    resolutions = set(zip(widths, heights))
    print("\nImage Resolution")
    print("-" * 40)
    print(f"  Minimum : {min(widths)}×{min(heights)}")
    print(f"  Maximum : {max(widths)}×{max(heights)}")
    print(f"  Average : {int(np.mean(widths))}×{int(np.mean(heights))}")
    print(f"  Unique  : {len(resolutions)}")

    # Resolution distribution (if varied)
    if len(resolutions) > 1:
        res_labels = [f"{w}×{h}" for w, h in sorted(resolutions)]
        res_counts = [
            sum(1 for ww, hh in zip(widths, heights) if ww == w and hh == h)
            for w, h in sorted(resolutions)
        ]
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(res_labels, res_counts)
        ax.set_title("Resolution Distribution")
        ax.set_xlabel("Resolution")
        ax.set_ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        _save_fig("resolution_distribution.png")

    # Channels
    print("\nImage Channels")
    print("-" * 40)
    for mode, cnt in channels.items():
        print(f"  {mode:<12}: {cnt}")

    # Corrupted
    print(f"\nCorrupted Images : {len(corrupted)}")
    if corrupted:
        for f in corrupted[:20]:
            print(f"  - {f}")

    return {
        "widths": widths, "heights": heights,
        "channels": channels, "corrupted": corrupted,
    }


# ── 6. Pixel statistics ────────────────────────────────────────────────────────

def pixel_statistics(df, sample_size=500):
    paths = df["image_path"].dropna().tolist()
    if not paths:
        print("\n[Pixel Statistics] No images found – skipping.")
        return {}

    sample = random.sample(paths, min(sample_size, len(paths)))
    r_vals, g_vals, b_vals = [], [], []

    for path in _iter(sample, desc="Pixel stats (sample)"):
        try:
            with Image.open(path) as img:
                arr = np.array(img.convert("RGB"), dtype=np.float32) / 255.0
                r_vals.append(arr[:, :, 0].mean())
                g_vals.append(arr[:, :, 1].mean())
                b_vals.append(arr[:, :, 2].mean())
        except Exception:
            pass

    stats = {
        "mean":  (np.mean(r_vals), np.mean(g_vals), np.mean(b_vals)),
        "std":   (np.std(r_vals),  np.std(g_vals),  np.std(b_vals)),
        "min":   (np.min(r_vals),  np.min(g_vals),  np.min(b_vals)),
        "max":   (np.max(r_vals),  np.max(g_vals),  np.max(b_vals)),
    }

    print(f"\nPixel Statistics (sample of {len(sample)} images)")
    print("-" * 40)
    for stat, vals in stats.items():
        print(f"  {stat.capitalize():<6}  R: {vals[0]:.3f}  G: {vals[1]:.3f}  B: {vals[2]:.3f}")

    return stats


# ── 7. Metadata statistics ─────────────────────────────────────────────────────

def metadata_statistics(df):
    print("\nMetadata Statistics")
    print("-" * 40)

    # Age
    age = df["age"].dropna()
    print(f"  Age – min: {int(age.min())}  max: {int(age.max())}  "
          f"mean: {age.mean():.1f}  median: {age.median():.1f}")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(age, bins=20, color="steelblue", edgecolor="white")
    ax.set_title("Age Distribution")
    ax.set_xlabel("Age")
    ax.set_ylabel("Count")
    plt.tight_layout()
    _save_fig("age_distribution.png")

    # Sex
    sex_counts = df["sex"].fillna("unknown").str.lower().value_counts()
    print("\n  Gender Distribution")
    for gender, cnt in sex_counts.items():
        print(f"    {gender.capitalize():<10}: {cnt}")

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(sex_counts.values, labels=[g.capitalize() for g in sex_counts.index],
           autopct="%1.1f%%", colors=["steelblue", "salmon", "gray"])
    ax.set_title("Gender Distribution")
    plt.tight_layout()
    _save_fig("gender_distribution.png")

    # Localization
    if "localization" in df.columns:
        loc_counts = df["localization"].fillna("unknown").value_counts()
        print("\n  Lesion Location (top 10)")
        for loc, cnt in loc_counts.head(10).items():
            print(f"    {loc:<25}: {cnt}")

    return sex_counts


# ── 8. Missing data ────────────────────────────────────────────────────────────

def missing_data(df):
    print("\nMissing Values")
    print("-" * 40)
    for col in df.columns:
        n = df[col].isna().sum()
        print(f"  {col:<20}: {n}")


# ── 9. Duplicate detection ─────────────────────────────────────────────────────

def duplicate_detection(df):
    dup_ids  = df["image_id"].duplicated().sum()
    dup_rows = df.duplicated().sum()
    print(f"\nDuplicate image IDs      : {dup_ids}")
    print(f"Duplicate metadata rows  : {dup_rows}")


# ── 10. Sample visualization ───────────────────────────────────────────────────

def sample_visualization(df):
    paths_available = df["image_path"].notna()
    if not paths_available.any():
        print("\n[Sample Visualization] No images found – skipping.")
        return

    classes = df["dx"].unique()
    n = len(classes)
    fig, axes = plt.subplots(1, n, figsize=(3 * n, 3))
    fig.suptitle("Sample Image per Class", fontsize=13, fontweight="bold")

    for ax, cls in zip(axes, sorted(classes)):
        subset = df[(df["dx"] == cls) & paths_available]
        if subset.empty:
            ax.axis("off")
            ax.set_title(cls)
            continue
        row = subset.sample(1).iloc[0]
        try:
            img = Image.open(row["image_path"]).convert("RGB")
            ax.imshow(img)
        except Exception:
            ax.text(0.5, 0.5, "Error", ha="center", va="center")
        ax.set_title(f"{cls}\n({CLASS_NAMES.get(cls, '')})", fontsize=7)
        ax.axis("off")

    plt.tight_layout()
    p = _save_fig("sample_images_per_class.png")
    print(f"\nSample visualization saved → {p}")


# ── 11. Report ─────────────────────────────────────────────────────────────────

def save_report(df, counts, img_props, pix_stats, sex_counts):
    path = os.path.join(REPORTS_DIR, "dataset_report.txt")
    corrupted = img_props.get("corrupted", [])
    widths    = img_props.get("widths", [])
    heights   = img_props.get("heights", [])
    mean_rgb  = pix_stats.get("mean", ("N/A", "N/A", "N/A"))
    std_rgb   = pix_stats.get("std",  ("N/A", "N/A", "N/A"))

    lines = [
        "HAM10000 Dataset Report",
        "=" * 40,
        "",
        "Dataset Size",
        f"  Total Images : {len(df)}",
        f"  Classes      : {df['dx'].nunique()}",
        "",
        "Image Resolution",
    ]

    if widths:
        lines += [
            f"  Minimum : {min(widths)}×{min(heights)}",
            f"  Maximum : {max(widths)}×{max(heights)}",
            f"  Average : {int(np.mean(widths))}×{int(np.mean(heights))}",
        ]
    else:
        lines.append("  No images scanned.")

    lines += [
        "",
        "Image Format",
        "  RGB JPEG",
        "",
        "Class Distribution",
    ]
    for cls, cnt in counts.items():
        lines.append(f"  {cls:<8}: {cnt}  ({cnt/len(df)*100:.2f}%)")

    lines += [
        "",
        f"Largest Class  : {counts.idxmax()} ({counts.max()})",
        f"Smallest Class : {counts.idxmin()} ({counts.min()})",
        f"Imbalance Ratio: {counts.max()/counts.min():.1f}x",
        "",
        "Missing Metadata",
    ]
    for col in df.columns:
        n = df[col].isna().sum()
        if n > 0:
            lines.append(f"  {col}: {n}")

    lines += [
        "",
        f"Corrupted Images : {len(corrupted)}",
    ]
    if corrupted:
        for f in corrupted:
            lines.append(f"  - {f}")

    lines += [
        "",
        "Gender Distribution",
    ]
    for g, cnt in sex_counts.items():
        lines.append(f"  {g.capitalize():<10}: {cnt}")

    if isinstance(mean_rgb[0], float):
        lines += [
            "",
            "Pixel Statistics (normalised, sample)",
            f"  Mean  R: {mean_rgb[0]:.3f}  G: {mean_rgb[1]:.3f}  B: {mean_rgb[2]:.3f}",
            f"  Std   R: {std_rgb[0]:.3f}   G: {std_rgb[1]:.3f}  B: {std_rgb[2]:.3f}",
        ]

    lines += ["", f"Report generated on : {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nReport saved to {path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("     HAM10000 Dataset Statistics")
    print("=" * 50)

    df, img_map = load_dataset()

    print()
    dataset_size(df)

    counts    = class_distribution(df)
    img_props = image_properties(df)
    pix_stats = pixel_statistics(df)
    sex_counts = metadata_statistics(df)
    missing_data(df)
    duplicate_detection(df)
    sample_visualization(df)
    save_report(df, counts, img_props, pix_stats, sex_counts)

    print("\n" + "=" * 50)
    print("Done.")
    print("=" * 50)


if __name__ == "__main__":
    main()
