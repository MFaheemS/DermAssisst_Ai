"""
Dataset preprocessing helpers.
- Splits raw images into train/val/test (70/15/15)
- Applies basic quality checks (min resolution, RGB only)
"""
import shutil
import random
from pathlib import Path
from PIL import Image

RAW_DIR  = Path("data/raw")
PROC_DIR = Path("data/processed")
SPLITS   = {"train": 0.70, "val": 0.15, "test": 0.15}
MIN_SIZE = (64, 64)
SEED     = 42


def preprocess():
    random.seed(SEED)
    for cls_dir in RAW_DIR.iterdir():
        if not cls_dir.is_dir():
            continue
        images = [p for p in cls_dir.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        images = [p for p in images if _valid(p)]
        random.shuffle(images)

        n = len(images)
        n_train = int(n * SPLITS["train"])
        n_val   = int(n * SPLITS["val"])

        buckets = {
            "train": images[:n_train],
            "val":   images[n_train:n_train + n_val],
            "test":  images[n_train + n_val:],
        }
        for split, files in buckets.items():
            dest = PROC_DIR / split / cls_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in files:
                shutil.copy2(f, dest / f.name)
        print(f"{cls_dir.name}: {n} images → train={len(buckets['train'])} val={len(buckets['val'])} test={len(buckets['test'])}")


def _valid(path):
    try:
        img = Image.open(path)
        return img.mode == "RGB" and img.size[0] >= MIN_SIZE[0] and img.size[1] >= MIN_SIZE[1]
    except Exception:
        return False


if __name__ == "__main__":
    preprocess()
