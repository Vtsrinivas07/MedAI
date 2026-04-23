"""
Train EfficientNet-B0 on MedMNIST 2D subsets.

Run one modality:
    cd backend && python scripts/train_medmnist_efficientnet.py --modality skin

Run all 2D modalities configured in models/medmnist_labels.py:
    cd backend && python scripts/train_medmnist_efficientnet.py --all

Requires: pip install medmnist torch torchvision timm
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import random
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import timm
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from models.medmnist_labels import (
    MEDMNIST_MODALITY_CONFIGS,
    normalize_medmnist_modality,
)


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def _write_run_manifest(run_name: str, payload: dict) -> str:
    out_dir = os.path.join(os.path.dirname(__file__), "..", "models", "weights")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{run_name}.run_manifest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return out_path


def _get_medmnist_class(name: str):
    mod = importlib.import_module("medmnist")
    return getattr(mod, name)


def _get_medmnist_info():
    mod = importlib.import_module("medmnist")
    return getattr(mod, "INFO", {})


def _display_names_for_task(task_name: str) -> list[str]:
    info = _get_medmnist_info().get(task_name, {})
    labels = info.get("label", {})
    if isinstance(labels, dict) and labels:
        try:
            return [str(labels[str(i)]) for i in range(len(labels))]
        except Exception:
            return [str(v) for _, v in sorted(labels.items(), key=lambda kv: int(kv[0]))]
    return []


class MedMNISTEfficientNetDataset(Dataset):
    """Resize MedMNIST 28x28 RGB to `image_size` for EfficientNet."""

    def __init__(
        self,
        dataset_cls,
        split: str,
        *,
        image_size: int = 224,
        multilabel: bool,
    ) -> None:
        self.ds = dataset_cls(split=split, download=True, size=28, as_rgb=True)
        self.multilabel = multilabel
        self.tfm = transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    def __len__(self) -> int:
        return len(self.ds)

    def __getitem__(self, idx: int):
        img, label = self.ds[idx]
        if not isinstance(img, Image.Image):
            img = Image.fromarray(np.asarray(img).astype(np.uint8))
        x = self.tfm(img.convert("RGB"))
        if self.multilabel:
            y = torch.as_tensor(np.asarray(label).astype(np.float32)).view(-1)
        else:
            arr = np.asarray(label).astype(np.int64).flatten()
            y = torch.tensor(int(arr[0]), dtype=torch.long)
        return x, y


def train_modality(modality: str, args) -> str:
    cfg = MEDMNIST_MODALITY_CONFIGS[modality]
    DatasetCls = _get_medmnist_class(cfg["dataset_class"])
    display_names = _display_names_for_task(cfg["task_name"])
    if not display_names:
        raise RuntimeError(f"Could not resolve class labels for task {cfg['task_name']}")

    num_classes = len(display_names)
    multilabel = bool(cfg.get("multi_label", False))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_ds = MedMNISTEfficientNetDataset(
        DatasetCls, "train", image_size=args.image_size, multilabel=multilabel
    )
    val_ds = MedMNISTEfficientNetDataset(
        DatasetCls, "val", image_size=args.image_size, multilabel=multilabel
    )

    worker_seed_gen = torch.Generator()
    worker_seed_gen.manual_seed(args.seed)
    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=False,
        generator=worker_seed_gen,
    )
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)

    model = timm.create_model("efficientnet_b0", pretrained=True, num_classes=num_classes)
    model.to(device)

    criterion = nn.BCEWithLogitsLoss() if multilabel else nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=1
    )

    print(f"\n[TRAIN] modality={modality} dataset={cfg['dataset_id']} labels={num_classes}")
    best_val_loss = float("inf")
    best_state_dict = None
    best_epoch = 0
    train_losses: list[float] = []
    val_losses: list[float] = []

    for epoch in range(args.epochs):
        model.train()
        running = 0.0
        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            if multilabel:
                yb = yb.float()
                if yb.dim() == 1:
                    yb = yb.view(xb.size(0), -1)
            else:
                yb = yb.long()
            optimizer.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()
            running += float(loss.item())
        train_loss = running / max(len(train_loader), 1)
        train_losses.append(train_loss)
        print(
            f"Epoch {epoch + 1}/{args.epochs} train loss (avg batch): "
            f"{train_loss:.4f}"
        )

        model.eval()
        vloss = 0.0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(device)
                yb = yb.to(device)
                if multilabel:
                    yb = yb.float()
                    if yb.dim() == 1:
                        yb = yb.view(xb.size(0), -1)
                else:
                    yb = yb.long()
                logits = model(xb)
                vloss += float(criterion(logits, yb).item())
        val_loss = vloss / max(len(val_loader), 1)
        val_losses.append(val_loss)
        scheduler.step(val_loss)
        print(f"Epoch {epoch + 1}/{args.epochs} val loss: {val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch + 1
            best_state_dict = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    out_dir = os.path.join(os.path.dirname(__file__), "..", "models", "weights")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, cfg["weight_file"])

    if best_state_dict is not None:
        model.load_state_dict(best_state_dict)

    checkpoint: dict = {
        "model_state_dict": model.state_dict(),
        "disease_classes": display_names,
        "class_names": display_names,
        "multi_label": multilabel,
        "backbone": "efficientnet_b0",
        "image_size": args.image_size,
        "dataset": cfg["dataset_id"],
        "medmnist_task": cfg["task_name"],
        "ui_modality": modality,
        "seed": args.seed,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "lr": args.lr,
        "weight_decay": args.weight_decay,
        "best_val_loss": best_val_loss,
        "best_epoch": best_epoch,
        "train_losses": train_losses,
        "val_losses": val_losses,
    }

    torch.save(checkpoint, out_path)
    manifest_payload = {
        "kind": "medmnist_training_run",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "script": "backend/scripts/train_medmnist_efficientnet.py",
        "modality": modality,
        "dataset": cfg["dataset_id"],
        "task_name": cfg["task_name"],
        "weight_file": cfg["weight_file"],
        "seed": args.seed,
        "hyperparameters": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "weight_decay": args.weight_decay,
            "image_size": args.image_size,
        },
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "device": str(device),
        },
        "checkpoint_path": os.path.abspath(out_path),
        "best_epoch": best_epoch,
        "best_val_loss": best_val_loss,
    }
    manifest_path = _write_run_manifest(f"train_{modality}", manifest_payload)
    print(f"[OK] Saved {modality} model to {out_path}")
    print(f"[OK] Wrote run manifest to {manifest_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--modality", type=str, default="skin")
    parser.add_argument("--all", action="store_true", dest="train_all")
    args = parser.parse_args()
    set_global_seed(args.seed)

    if args.train_all:
        failures: list[str] = []
        for modality in MEDMNIST_MODALITY_CONFIGS.keys():
            try:
                train_modality(modality, args)
            except Exception as exc:
                failures.append(f"{modality}: {exc}")
                print(f"[WARN] Failed modality={modality}: {exc}")
        if failures:
            raise SystemExit("Training failed for some modalities:\n- " + "\n- ".join(failures))
    else:
        modality = normalize_medmnist_modality(args.modality, default="skin")
        if modality not in MEDMNIST_MODALITY_CONFIGS:
            raise SystemExit(f"Unsupported modality: {args.modality}")
        train_modality(modality, args)

    print("Reload the backend to load the new weights.")


if __name__ == "__main__":
    main()
