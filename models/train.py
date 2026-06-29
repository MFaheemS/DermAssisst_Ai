"""
Training script — EfficientNet-B0 fine-tuned on skin lesion dataset.

Dataset layout expected:
  data/processed/
      train/  acne/  eczema/  melanoma/  psoriasis/
      val/    ...
      test/   ...

Usage:
    python models/train.py --epochs 20 --batch-size 32
"""
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from pathlib import Path

CLASSES = ["acne", "eczema", "melanoma", "psoriasis"]
DATA_ROOT = Path("data/processed")
SAVE_PATH = Path("models/dermassist_best.pt")


def get_loaders(batch_size):
    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.2, 0.2, 0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    train_ds = datasets.ImageFolder(DATA_ROOT / "train", transform=train_tf)
    val_ds   = datasets.ImageFolder(DATA_ROOT / "val",   transform=val_tf)
    return (
        DataLoader(train_ds, batch_size=batch_size, shuffle=True,  num_workers=4),
        DataLoader(val_ds,   batch_size=batch_size, shuffle=False, num_workers=4),
    )


def build_model(num_classes):
    model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT)
    for p in model.parameters():
        p.requires_grad = False
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model


def train(epochs, batch_size):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_loader, val_loader = get_loaders(batch_size)
    model = build_model(len(CLASSES)).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.classifier.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, epochs)

    best_acc = 0.0
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(imgs), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        scheduler.step()

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                preds = model(imgs).argmax(1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
        acc = correct / total
        print(f"Epoch {epoch}/{epochs}  loss={running_loss/len(train_loader):.4f}  val_acc={acc:.4f}")
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), SAVE_PATH)
            print(f"  → Saved best model (acc={best_acc:.4f})")

    print(f"Training complete. Best val accuracy: {best_acc:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    train(args.epochs, args.batch_size)
