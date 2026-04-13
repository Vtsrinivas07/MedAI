"""
EfficientNet fine-tuning for medical image classification.

Features:
- EfficientNet-B0 or EfficientNet-B3 pretrained on ImageNet
- CSV manifest-based preprocessing pipeline
- Strong but lightweight augmentation
- Transfer learning with early stopping and label smoothing
- Accuracy, weighted F1, confusion matrix, and classification report
- Checkpoint metadata compatible with the FastAPI inference service

Example:
    python backend/train_efficientnet_medical.py \
        --image-root datasets/ham10000/images \
        --train-csv datasets/ham10000/manifests/train.csv \
        --val-csv datasets/ham10000/manifests/val.csv \
        --test-csv datasets/ham10000/manifests/test.csv \
        --backbone efficientnet_b0 \
        --output-dir backend/models/weights/skin
"""

from __future__ import annotations

import argparse
import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import timm
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from torch.cuda.amp import GradScaler, autocast
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


@dataclass
class TrainingConfig:
    backbone: str = "efficientnet_b0"
    image_size: int = 224
    batch_size: int = 32
    epochs: int = 15
    learning_rate: float = 3e-4
    weight_decay: float = 1e-4
    freeze_epochs: int = 2
    patience: int = 4
    label_smoothing: float = 0.05
    num_workers: int = 4
    seed: int = 42
    dropout: float = 0.3


class MedicalImageManifestDataset(Dataset):
    def __init__(
        self,
        manifest_path: str | Path,
        image_root: str | Path,
        label_to_index: Dict[str, int],
        transform: Optional[transforms.Compose] = None,
    ) -> None:
        self.manifest = pd.read_csv(manifest_path)
        self.image_root = Path(image_root)
        self.label_to_index = label_to_index
        self.transform = transform

        if "image_path" not in self.manifest.columns or "label" not in self.manifest.columns:
            raise ValueError("Manifest must contain 'image_path' and 'label' columns")

    def __len__(self) -> int:
        return len(self.manifest)

    def __getitem__(self, index: int):
        row = self.manifest.iloc[index]
        image_path = self.image_root / row["image_path"]
        label_name = str(row["label"])
        label_index = self.label_to_index[label_name]

        image = Image.open(image_path).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)

        return image, label_index


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def build_transforms(image_size: int) -> Tuple[transforms.Compose, transforms.Compose]:
    train_transform = transforms.Compose(
        [
            transforms.Resize((image_size + 32, image_size + 32)),
            transforms.RandomResizedCrop(image_size, scale=(0.75, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.1, hue=0.02),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
            transforms.RandomErasing(p=0.15, scale=(0.02, 0.12)),
        ]
    )

    eval_transform = transforms.Compose(
        [
            transforms.Resize((image_size + 32, image_size + 32)),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )

    return train_transform, eval_transform


def load_manifest_labels(*manifest_paths: str | Path) -> List[str]:
    labels: List[str] = []
    for manifest_path in manifest_paths:
        if manifest_path is None:
            continue
        manifest = pd.read_csv(manifest_path)
        if "label" not in manifest.columns:
            raise ValueError(f"Manifest {manifest_path} is missing a 'label' column")
        labels.extend(manifest["label"].astype(str).tolist())

    unique_labels = sorted(set(labels))
    if not unique_labels:
        raise ValueError("No labels found across manifests")
    return unique_labels


def build_model(backbone: str, num_classes: int, dropout: float = 0.3, pretrained: bool = True) -> nn.Module:
    model = timm.create_model(
        backbone,
        pretrained=pretrained,
        num_classes=num_classes,
        drop_rate=dropout,
    )
    return model


def set_backbone_trainable(model: nn.Module, trainable: bool) -> None:
    for parameter in model.parameters():
        parameter.requires_grad = trainable


@torch.no_grad()
def evaluate_model(model: nn.Module, loader: DataLoader, criterion: nn.Module, device: torch.device):
    model.eval()
    total_loss = 0.0
    all_predictions: List[int] = []
    all_targets: List[int] = []

    for images, targets in loader:
        images = images.to(device)
        targets = targets.to(device)

        logits = model(images)
        loss = criterion(logits, targets)
        total_loss += loss.item() * images.size(0)

        predictions = logits.argmax(dim=1)
        all_predictions.extend(predictions.cpu().tolist())
        all_targets.extend(targets.cpu().tolist())

    average_loss = total_loss / max(len(loader.dataset), 1)
    accuracy = accuracy_score(all_targets, all_predictions)
    f1 = f1_score(all_targets, all_predictions, average="weighted")
    return average_loss, accuracy, f1, all_targets, all_predictions


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    scaler: Optional[GradScaler],
) -> float:
    model.train()
    running_loss = 0.0

    for images, targets in loader:
        images = images.to(device)
        targets = targets.to(device)

        optimizer.zero_grad(set_to_none=True)

        if scaler is not None:
            with autocast():
                logits = model(images)
                loss = criterion(logits, targets)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            logits = model(images)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()

        running_loss += loss.item() * images.size(0)

    return running_loss / max(len(loader.dataset), 1)


def save_checkpoint(
    output_path: Path,
    model: nn.Module,
    config: TrainingConfig,
    class_names: List[str],
    class_to_idx: Dict[str, int],
    best_val_accuracy: float,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "backbone": config.backbone,
        "model_name": config.backbone,
        "image_size": config.image_size,
        "num_classes": len(class_names),
        "class_names": class_names,
        "disease_classes": class_names,
        "class_to_idx": class_to_idx,
        "best_val_accuracy": best_val_accuracy,
        "training_config": {
            "batch_size": config.batch_size,
            "epochs": config.epochs,
            "learning_rate": config.learning_rate,
            "weight_decay": config.weight_decay,
            "freeze_epochs": config.freeze_epochs,
            "patience": config.patience,
            "label_smoothing": config.label_smoothing,
            "dropout": config.dropout,
        },
    }
    torch.save(checkpoint, output_path)


def save_metrics_report(
    output_dir: Path,
    class_names: List[str],
    y_true: List[int],
    y_pred: List[int],
    val_metrics: Dict[str, float],
    test_metrics: Dict[str, float],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    labels = list(range(len(class_names)))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    pd.DataFrame(cm, index=class_names, columns=class_names).to_csv(output_dir / "confusion_matrix.csv")

    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    with open(output_dir / "metrics.json", "w", encoding="utf-8") as handle:
        json.dump(
            {
                "validation": val_metrics,
                "test": test_metrics,
                "classification_report": report,
            },
            handle,
            indent=2,
        )


def build_dataloaders(
    image_root: Path,
    train_csv: Path,
    val_csv: Path,
    test_csv: Optional[Path],
    config: TrainingConfig,
):
    class_names = load_manifest_labels(train_csv, val_csv, test_csv) if test_csv else load_manifest_labels(train_csv, val_csv)
    class_to_idx = {class_name: index for index, class_name in enumerate(class_names)}

    train_transform, eval_transform = build_transforms(config.image_size)

    train_dataset = MedicalImageManifestDataset(train_csv, image_root, class_to_idx, train_transform)
    val_dataset = MedicalImageManifestDataset(val_csv, image_root, class_to_idx, eval_transform)
    test_dataset = MedicalImageManifestDataset(test_csv, image_root, class_to_idx, eval_transform) if test_csv else None

    pin_memory = torch.cuda.is_available()
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=pin_memory,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=pin_memory,
    )
    test_loader = (
        DataLoader(
            test_dataset,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=pin_memory,
        )
        if test_dataset is not None
        else None
    )

    return train_loader, val_loader, test_loader, class_names, class_to_idx


def train(
    image_root: Path,
    train_csv: Path,
    val_csv: Path,
    test_csv: Optional[Path],
    output_dir: Path,
    config: TrainingConfig,
) -> Dict[str, float]:
    seed_everything(config.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, val_loader, test_loader, class_names, class_to_idx = build_dataloaders(
        image_root=image_root,
        train_csv=train_csv,
        val_csv=val_csv,
        test_csv=test_csv,
        config=config,
    )

    model = build_model(config.backbone, num_classes=len(class_names), dropout=config.dropout, pretrained=True)
    model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=config.label_smoothing)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)
    scaler = GradScaler() if torch.cuda.is_available() else None

    best_val_accuracy = 0.0
    best_val_f1 = 0.0
    best_state_dict = None
    epochs_without_improvement = 0

    for epoch in range(1, config.epochs + 1):
        if epoch <= config.freeze_epochs:
            set_backbone_trainable(model, False)
            for parameter in model.classifier.parameters():
                parameter.requires_grad = True
        else:
            set_backbone_trainable(model, True)

        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device, scaler)
        val_loss, val_accuracy, val_f1, _, _ = evaluate_model(model, val_loader, criterion, device)
        scheduler.step(val_accuracy)

        print(
            f"Epoch {epoch:02d}/{config.epochs} | "
            f"train_loss={train_loss:.4f} | val_loss={val_loss:.4f} | "
            f"val_acc={val_accuracy:.4f} | val_f1={val_f1:.4f}"
        )

        improved = val_accuracy > best_val_accuracy
        if improved:
            best_val_accuracy = val_accuracy
            best_val_f1 = val_f1
            best_state_dict = {key: value.cpu() for key, value in model.state_dict().items()}
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= config.patience:
            print(f"Early stopping triggered after {epoch} epochs")
            break

    if best_state_dict is None:
        best_state_dict = {key: value.cpu() for key, value in model.state_dict().items()}

    model.load_state_dict(best_state_dict)
    model.to(device)

    save_checkpoint(
        output_path=output_dir / f"{config.backbone}_medical_checkpoint.pth",
        model=model,
        config=config,
        class_names=class_names,
        class_to_idx=class_to_idx,
        best_val_accuracy=best_val_accuracy,
    )

    val_loss, val_accuracy, val_f1, val_targets, val_predictions = evaluate_model(model, val_loader, criterion, device)
    val_metrics = {
        "loss": float(val_loss),
        "accuracy": float(val_accuracy),
        "f1_weighted": float(val_f1),
    }

    test_metrics = {"loss": None, "accuracy": None, "f1_weighted": None}
    test_targets: List[int] = []
    test_predictions: List[int] = []

    if test_loader is not None:
        test_loss, test_accuracy, test_f1, test_targets, test_predictions = evaluate_model(model, test_loader, criterion, device)
        test_metrics = {
            "loss": float(test_loss),
            "accuracy": float(test_accuracy),
            "f1_weighted": float(test_f1),
        }

    save_metrics_report(output_dir, class_names, val_targets, val_predictions, val_metrics, test_metrics)

    with open(output_dir / "training_summary.json", "w", encoding="utf-8") as handle:
        json.dump(
            {
                "backbone": config.backbone,
                "image_size": config.image_size,
                "num_classes": len(class_names),
                "class_names": class_names,
                "best_val_accuracy": best_val_accuracy,
                "best_val_f1": best_val_f1,
                "validation": val_metrics,
                "test": test_metrics,
            },
            handle,
            indent=2,
        )

    print("\n✅ Training complete")
    print(f"   Best validation accuracy: {best_val_accuracy:.4f}")
    print(f"   Best validation F1:       {best_val_f1:.4f}")
    print(f"   Checkpoint saved to:      {output_dir / f'{config.backbone}_medical_checkpoint.pth'}")
    print(f"   Metrics saved to:         {output_dir / 'metrics.json'}")
    print(f"   Confusion matrix saved to: {output_dir / 'confusion_matrix.csv'}")

    return {
        "best_val_accuracy": float(best_val_accuracy),
        "best_val_f1": float(best_val_f1),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fine-tune EfficientNet for medical image classification")
    parser.add_argument("--image-root", required=True, help="Root folder containing images referenced by the CSV manifests")
    parser.add_argument("--train-csv", required=True, help="Train manifest CSV with image_path,label columns")
    parser.add_argument("--val-csv", required=True, help="Validation manifest CSV with image_path,label columns")
    parser.add_argument("--test-csv", help="Optional test manifest CSV with image_path,label columns")
    parser.add_argument("--output-dir", required=True, help="Directory where checkpoints and metrics will be saved")
    parser.add_argument("--backbone", choices=["efficientnet_b0", "efficientnet_b3"], default="efficientnet_b0")
    parser.add_argument("--image-size", type=int, default=224, help="Input size used for training and inference")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--freeze-epochs", type=int, default=2)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--label-smoothing", type=float, default=0.05)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dropout", type=float, default=0.3)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = TrainingConfig(
        backbone=args.backbone,
        image_size=args.image_size,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        freeze_epochs=args.freeze_epochs,
        patience=args.patience,
        label_smoothing=args.label_smoothing,
        num_workers=args.num_workers,
        seed=args.seed,
        dropout=args.dropout,
    )

    image_root = Path(args.image_root)
    train_csv = Path(args.train_csv)
    val_csv = Path(args.val_csv)
    test_csv = Path(args.test_csv) if args.test_csv else None
    output_dir = Path(args.output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("🏥 EfficientNet Medical Image Training")
    print("=" * 78)
    print(f"Backbone:   {config.backbone}")
    print(f"Image size: {config.image_size}")
    print(f"Device:     {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print(f"Train CSV:  {train_csv}")
    print(f"Val CSV:    {val_csv}")
    print(f"Test CSV:   {test_csv if test_csv else 'not provided'}")
    print(f"Output:     {output_dir}")
    print("=" * 78)

    train(image_root, train_csv, val_csv, test_csv, output_dir, config)


if __name__ == "__main__":
    main()
