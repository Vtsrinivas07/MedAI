"""Evaluate MedMNIST EfficientNet-B0 checkpoints on held-out test splits.

Example:
    cd backend && python scripts/evaluate_medmnist_efficientnet.py --modalities skin pneumonia retina breast
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
from typing import Any

import numpy as np
import timm
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    roc_auc_score,
)
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.medmnist_labels import MEDMNIST_MODALITY_CONFIGS, normalize_medmnist_modality


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def _get_medmnist_class(name: str):
    mod = importlib.import_module("medmnist")
    return getattr(mod, name)


class MedMNISTEvalDataset(Dataset):
    def __init__(self, dataset_cls, split: str, image_size: int, multilabel: bool):
        self.ds = dataset_cls(split=split, download=True, size=28, as_rgb=True)
        self.multilabel = multilabel
        self.tfm = transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    def __len__(self):
        return len(self.ds)

    def __getitem__(self, idx):
        img, label = self.ds[idx]
        if not isinstance(img, Image.Image):
            img = Image.fromarray(np.asarray(img).astype(np.uint8))
        x = self.tfm(img.convert("RGB"))
        arr = np.asarray(label)
        if self.multilabel:
            y = arr.astype(np.float32).reshape(-1)
        else:
            y = int(arr.astype(np.int64).flatten()[0])
        return x, y


def _create_model(backbone: str, num_classes: int) -> nn.Module:
    model = timm.create_model(backbone, pretrained=False)
    if hasattr(model, "classifier") and isinstance(model.classifier, nn.Linear):
        in_features = model.classifier.in_features
        model.classifier = nn.Linear(in_features, num_classes)
    elif hasattr(model, "get_classifier"):
        classifier = model.get_classifier()
        in_features = classifier.in_features
        model.classifier = nn.Linear(in_features, num_classes)
    else:
        raise RuntimeError(f"Unsupported classifier head for backbone={backbone}")
    return model


def _extract_state_dict(ckpt: Any):
    if isinstance(ckpt, dict):
        if "model_state_dict" in ckpt:
            return ckpt["model_state_dict"], ckpt
        if "state_dict" in ckpt:
            return ckpt["state_dict"], ckpt
    return ckpt, ckpt if isinstance(ckpt, dict) else {}


def _clean_state_dict(state_dict: dict) -> dict:
    cleaned = {}
    for k, v in state_dict.items():
        if k.startswith("module."):
            cleaned[k[len("module.") :]] = v
        else:
            cleaned[k] = v
    return cleaned


def evaluate_modality(modality: str, batch_size: int = 64) -> dict:
    cfg = MEDMNIST_MODALITY_CONFIGS[modality]
    weight_path = os.path.join(
        os.path.dirname(__file__), "..", "models", "weights", cfg["weight_file"]
    )
    weight_path = os.path.abspath(weight_path)

    if not os.path.exists(weight_path):
        raise FileNotFoundError(f"Missing weight file: {weight_path}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    ckpt = torch.load(weight_path, map_location=device, weights_only=False)
    state_dict, meta = _extract_state_dict(ckpt)
    state_dict = _clean_state_dict(state_dict)

    class_names = list(meta.get("class_names") or meta.get("disease_classes") or [])
    if not class_names:
        raise RuntimeError(f"Checkpoint missing class names: {weight_path}")

    num_classes = len(class_names)
    backbone = str(meta.get("backbone") or "efficientnet_b0")
    image_size = int(meta.get("image_size") or 224)
    multi_label = bool(meta.get("multi_label", cfg.get("multi_label", False)))

    model = _create_model(backbone, num_classes=num_classes)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    dataset_cls = _get_medmnist_class(cfg["dataset_class"])
    test_ds = MedMNISTEvalDataset(dataset_cls, "test", image_size=image_size, multilabel=multi_label)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    y_true_chunks = []
    y_prob_chunks = []
    y_pred_chunks = []

    with torch.no_grad():
        for xb, yb in test_loader:
            xb = xb.to(device)
            logits = model(xb)

            if multi_label:
                probs = torch.sigmoid(logits).cpu().numpy()
                preds = (probs >= 0.5).astype(np.int64)
                y_true = np.asarray(yb, dtype=np.float32)
            else:
                probs = torch.softmax(logits, dim=1).cpu().numpy()
                preds = probs.argmax(axis=1).astype(np.int64)
                y_true = np.asarray(yb, dtype=np.int64)

            y_true_chunks.append(y_true)
            y_prob_chunks.append(probs)
            y_pred_chunks.append(preds)

    y_true_all = np.concatenate(y_true_chunks, axis=0)
    y_prob_all = np.concatenate(y_prob_chunks, axis=0)
    y_pred_all = np.concatenate(y_pred_chunks, axis=0)

    results = {
        "modality": modality,
        "dataset": cfg["dataset_id"],
        "task": cfg["task_name"],
        "multi_label": multi_label,
        "num_test_samples": int(y_true_all.shape[0]),
    }

    if multi_label:
        try:
            auc_macro = float(roc_auc_score(y_true_all, y_prob_all, average="macro"))
        except Exception:
            auc_macro = None

        try:
            map_macro = float(average_precision_score(y_true_all, y_prob_all, average="macro"))
        except Exception:
            map_macro = None

        f1_macro = float(f1_score(y_true_all, y_pred_all, average="macro", zero_division=0))

        results.update(
            {
                "accuracy": None,
                "f1_macro": f1_macro,
                "auc_macro": auc_macro,
                "map_macro": map_macro,
            }
        )
    else:
        acc = float(accuracy_score(y_true_all, y_pred_all))
        f1m = float(f1_score(y_true_all, y_pred_all, average="macro", zero_division=0))

        auc = None
        try:
            if num_classes == 2:
                auc = float(roc_auc_score(y_true_all, y_prob_all[:, 1]))
            elif num_classes > 2:
                auc = float(roc_auc_score(y_true_all, y_prob_all, multi_class="ovr", average="macro"))
        except Exception:
            auc = None

        results.update(
            {
                "accuracy": acc,
                "f1_macro": f1m,
                "auc_macro": auc,
                "map_macro": None,
            }
        )

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modalities", nargs="+", default=["skin", "pneumonia", "retina", "breast"])
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output-file", type=str, default="models/weights/medmnist_eval_results.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    set_global_seed(args.seed)

    modalities = [normalize_medmnist_modality(m) for m in args.modalities]
    results = []

    for m in modalities:
        if m not in MEDMNIST_MODALITY_CONFIGS:
            print(f"[WARN] Skipping unsupported modality: {m}")
            continue
        print(f"[EVAL] {m} ...")
        try:
            res = evaluate_modality(m, batch_size=args.batch_size)
            results.append(res)
            print(
                f"  accuracy={res['accuracy']} f1_macro={res['f1_macro']} "
                f"auc_macro={res['auc_macro']} map_macro={res['map_macro']}"
            )
        except Exception as exc:
            print(f"[ERR] {m}: {exc}")

    out_path = os.path.abspath(args.output_file)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = {
        "kind": "medmnist_evaluation_run",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "script": "backend/scripts/evaluate_medmnist_efficientnet.py",
        "seed": args.seed,
        "batch_size": args.batch_size,
        "modalities_requested": args.modalities,
        "modalities_evaluated": [r["modality"] for r in results],
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
        },
        "results": results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    manifest_path = os.path.splitext(out_path)[0] + ".run_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[OK] Wrote evaluation results to {out_path}")
    print(f"[OK] Wrote evaluation manifest to {manifest_path}")


if __name__ == "__main__":
    main()
