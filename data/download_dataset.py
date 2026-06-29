"""
Dataset download and organisation script for DermAssist-AI.

Supported sources
-----------------
1. ISIC 2019 (melanoma + nevus + other)       — requires free ISIC account
2. Kaggle Skin Disease Dataset                 — requires kaggle API key
3. DermNet NZ (scraping)                      — educational use only

Usage
-----
    # Option A: Kaggle (recommended)
    pip install kaggle
    # Place kaggle.json in ~/.kaggle/
    python data/download_dataset.py --source kaggle

    # Option B: Manual ISIC download
    python data/download_dataset.py --source isic --isic-dir /path/to/isic

    # Option C: Create a minimal dummy dataset for dev/testing
    python data/download_dataset.py --source dummy --n 50
"""
import argparse
import random
import shutil
from pathlib import Path

import numpy as np

RAW_DIR = Path("data/raw")
CLASSES = ["acne", "eczema", "melanoma", "psoriasis", "normal"]


def create_dummy_dataset(n_per_class: int = 50):
    """Create tiny synthetic images so the pipeline can be exercised without real data."""
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("Pillow required: pip install Pillow")

    print(f"Creating dummy dataset ({n_per_class} images per class)...")
    palette = {
        "acne":      (220, 150, 130),
        "eczema":    (210, 180, 140),
        "melanoma":  (80,  50,  40),
        "psoriasis": (200, 160, 160),
        "normal":    (230, 200, 180),
    }
    for cls in CLASSES:
        cls_dir = RAW_DIR / cls
        cls_dir.mkdir(parents=True, exist_ok=True)
        r, g, b = palette[cls]
        for i in range(n_per_class):
            noise = np.random.randint(-20, 20, (224, 224, 3), dtype=np.int16)
            arr = np.clip(np.array([r, g, b], dtype=np.int16) + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr, "RGB")
            img.save(cls_dir / f"{cls}_{i:04d}.jpg")
        print(f"  {cls}: {n_per_class} dummy images")
    print("Done. Run utils/preprocess.py to split into train/val/test.")


def download_kaggle():
    """Download via Kaggle API (requires ~/.kaggle/kaggle.json)."""
    try:
        import kaggle  # noqa: F401
    except ImportError:
        raise SystemExit("Install kaggle: pip install kaggle")
    import subprocess, sys
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    # Skin disease image dataset (4 classes, ~2 000 images)
    cmd = [
        sys.executable, "-m", "kaggle", "datasets", "download",
        "-d", "shubhamgoel27/dermnet",
        "--unzip", "-p", str(RAW_DIR),
    ]
    print("Downloading from Kaggle (DermNet)...")
    subprocess.run(cmd, check=True)
    print("Done.")


def download_isic(isic_dir: str):
    """Organise a manually downloaded ISIC 2019 archive."""
    src = Path(isic_dir)
    if not src.exists():
        raise SystemExit(f"ISIC directory not found: {src}")
    mapping = {
        "MEL": "melanoma",
        "NV":  "normal",
        "BCC": "melanoma",
        "AK":  "melanoma",
        "BKL": "normal",
        "DF":  "normal",
        "VASC": "normal",
        "SCC": "melanoma",
        "UNK": "normal",
    }
    moved = {c: 0 for c in CLASSES}
    for img in src.rglob("*.jpg"):
        prefix = img.stem.split("_")[0].upper() if "_" in img.stem else "UNK"
        dest_class = mapping.get(prefix, "normal")
        dest = RAW_DIR / dest_class
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(img, dest / img.name)
        moved[dest_class] += 1
    for c, n in moved.items():
        print(f"  {c}: {n} images")
    print("Done.")


def main():
    parser = argparse.ArgumentParser(description="DermAssist-AI dataset downloader")
    parser.add_argument("--source", choices=["dummy", "kaggle", "isic"], default="dummy")
    parser.add_argument("--n", type=int, default=50, help="Images per class (dummy mode)")
    parser.add_argument("--isic-dir", type=str, default="", help="Path to ISIC archive folder")
    args = parser.parse_args()

    if args.source == "dummy":
        create_dummy_dataset(args.n)
    elif args.source == "kaggle":
        download_kaggle()
    elif args.source == "isic":
        download_isic(args.isic_dir)


if __name__ == "__main__":
    main()
