"""
Generic training pipeline for multi-modal medical image classification.

Usage examples:
python train_multimodal_model.py --modality skin --data-dir datasets/sd-198/release_v0/images
python train_multimodal_model.py --modality chest --data-dir datasets/chest/COVID-19_Radiography_Dataset
python train_multimodal_model.py --modality eye --data-dir datasets/eye
python train_multimodal_model.py --modality brain --data-dir datasets/brain/Training
"""

import argparse
import os
from pathlib import Path

import timm
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
from tqdm import tqdm


class TrainConfig:
    model_arch = "efficientnet_b0"
    image_size = 224
    batch_size = 32
    epochs = 20
    lr = 0.001
    num_workers = 4


def build_transforms(image_size: int):
    train_tf = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15, hue=0.05),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    eval_tf = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    return train_tf, eval_tf


def discover_dataset_root(data_dir: Path) -> Path:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    if (data_dir / "train").exists() and any((data_dir / "train").iterdir()):
        return data_dir / "train"

    return data_dir


def create_dataloaders(data_dir: Path, image_size: int, batch_size: int, num_workers: int):
    train_tf, eval_tf = build_transforms(image_size)

    root = discover_dataset_root(data_dir)
    full_dataset = datasets.ImageFolder(root=str(root), transform=train_tf)

    if len(full_dataset.classes) < 2:
        raise ValueError("Dataset must contain at least two class subfolders")

    targets = full_dataset.targets
    indices = list(range(len(full_dataset)))

    train_idx, val_test_idx = train_test_split(
        indices,
        test_size=0.3,
        random_state=42,
        stratify=targets,
    )

    val_test_targets = [targets[i] for i in val_test_idx]
    val_idx, test_idx = train_test_split(
        val_test_idx,
        test_size=0.5,
        random_state=42,
        stratify=val_test_targets,
    )

    train_dataset = Subset(full_dataset, train_idx)

    eval_dataset = datasets.ImageFolder(root=str(root), transform=eval_tf)
    val_dataset = Subset(eval_dataset, val_idx)
    test_dataset = Subset(eval_dataset, test_idx)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    return train_loader, val_loader, test_loader, full_dataset.classes


def create_model(num_classes: int):
    model = timm.create_model(TrainConfig.model_arch, pretrained=True)
    in_features = model.classifier.in_features
    model.classifier = nn.Linear(in_features, num_classes)
    return model


def run_epoch(model, loader, criterion, device, optimizer=None):
    is_train = optimizer is not None
    model.train() if is_train else model.eval()

    running_loss = 0.0
    running_correct = 0
    total = 0

    pbar = tqdm(loader, desc="Train" if is_train else "Eval")

    with torch.set_grad_enabled(is_train):
        for images, labels in pbar:
            images = images.to(device)
            labels = labels.to(device)

            if is_train:
                optimizer.zero_grad()

            outputs = model(images)
            loss = criterion(outputs, labels)

            if is_train:
                loss.backward()
                optimizer.step()

            running_loss += loss.item()
            preds = outputs.argmax(dim=1)
            running_correct += (preds == labels).sum().item()
            total += labels.size(0)

            pbar.set_postfix(
                loss=f"{running_loss / max(1, len(loader)):.4f}",
                acc=f"{100.0 * running_correct / max(1, total):.2f}%",
            )

    epoch_loss = running_loss / max(1, len(loader))
    epoch_acc = 100.0 * running_correct / max(1, total)
    return epoch_loss, epoch_acc


def train(modality: str, data_dir: Path, output_path: Path):
    print("=" * 72)
    print(f"🏥 Training modality: {modality}")
    print("=" * 72)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_loader, val_loader, test_loader, class_names = create_dataloaders(
        data_dir,
        TrainConfig.image_size,
        TrainConfig.batch_size,
        TrainConfig.num_workers,
    )

    print(f"Detected classes: {len(class_names)}")

    model = create_model(len(class_names)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=TrainConfig.lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)

    best_val_acc = 0.0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(TrainConfig.epochs):
        print(f"\nEpoch {epoch + 1}/{TrainConfig.epochs}")
        train_loss, train_acc = run_epoch(model, train_loader, criterion, device, optimizer=optimizer)
        val_loss, val_acc = run_epoch(model, val_loader, criterion, device)

        scheduler.step(val_loss)

        print(f"Train: loss={train_loss:.4f} acc={train_acc:.2f}%")
        print(f"Val:   loss={val_loss:.4f} acc={val_acc:.2f}%")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "modality": modality,
                    "num_classes": len(class_names),
                    "disease_classes": class_names,
                    "model_name": TrainConfig.model_arch,
                    "image_size": TrainConfig.image_size,
                    "val_acc": val_acc,
                },
                output_path,
            )
            print(f"✅ Saved new best checkpoint: {output_path}")

    print("\nEvaluating best-in-memory model on test split...")
    test_loss, test_acc = run_epoch(model, test_loader, criterion, device)
    print(f"Test:  loss={test_loss:.4f} acc={test_acc:.2f}%")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")


def parse_args():
    parser = argparse.ArgumentParser(description="Train a modality-specific medical image model")
    parser.add_argument("--modality", required=True, choices=["skin", "chest", "eye", "brain"])
    parser.add_argument("--data-dir", required=True, help="Directory with class subfolders or train/ class folders")
    parser.add_argument(
        "--output",
        default=None,
        help="Output checkpoint path. Defaults to models/weights/efficientnet_<modality>_disease.pth",
    )
    parser.add_argument("--epochs", type=int, default=TrainConfig.epochs)
    parser.add_argument("--batch-size", type=int, default=TrainConfig.batch_size)
    parser.add_argument("--lr", type=float, default=TrainConfig.lr)
    return parser.parse_args()


def main():
    args = parse_args()

    TrainConfig.epochs = args.epochs
    TrainConfig.batch_size = args.batch_size
    TrainConfig.lr = args.lr

    default_output = Path("models/weights") / f"efficientnet_{args.modality}_disease.pth"
    output_path = Path(args.output) if args.output else default_output

    train(args.modality, Path(args.data_dir), output_path)


if __name__ == "__main__":
    main()
