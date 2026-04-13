"""
One-command training entrypoint for unified medical datasets.

This script:
1. Merges multiple dataset manifests into one unified manifest
2. Groups rows by split (train/val/test)
3. Calls the existing EfficientNet training pipeline

Example:
    python backend/train_unified_medical_model.py \
        --input datasets/ham10000/manifests/train.csv skin ham10000 train \
        --input datasets/ham10000/manifests/val.csv skin ham10000 val \
        --input datasets/ham10000/manifests/test.csv skin ham10000 test \
        --image-root datasets/ham10000/images \
        --backbone efficientnet_b0 \
        --output-dir backend/models/weights/unified_skin
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from create_unified_medical_manifest import build_unified_manifest, parse_input_spec
from train_efficientnet_medical import TrainingConfig, train


InputSpec = Tuple[Path, str, str, str]


def _write_split_manifests(unified_manifest: pd.DataFrame, output_dir: Path) -> tuple[Path, Path, Path]:
    split_dir = output_dir / "manifests"
    split_dir.mkdir(parents=True, exist_ok=True)

    def _write_split(name: str) -> Path:
        split_frame = unified_manifest[unified_manifest["split"].astype(str).str.lower() == name].copy()
        if split_frame.empty:
            raise ValueError(f"No rows found for split '{name}' in unified manifest")
        split_frame = split_frame[["image_path", "label"]]
        split_path = split_dir / f"{name}.csv"
        split_frame.to_csv(split_path, index=False)
        return split_path

    train_csv = _write_split("train")
    val_csv = _write_split("val")
    test_csv = _write_split("test")
    return train_csv, val_csv, test_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train EfficientNet from a unified medical manifest")
    parser.add_argument(
        "--input",
        nargs=4,
        action="append",
        metavar=("CSV", "MODALITY", "DATASET", "SPLIT"),
        required=True,
        help="Input manifest spec: csv_path modality dataset_name split",
    )
    parser.add_argument("--image-root", required=True, help="Root folder containing all referenced images")
    parser.add_argument("--output-dir", required=True, help="Where checkpoints and metrics will be saved")
    parser.add_argument("--backbone", choices=["efficientnet_b0", "efficientnet_b3"], default="efficientnet_b0")
    parser.add_argument("--image-size", type=int, default=224)
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
    parser.add_argument("--summary-json", help="Optional summary JSON path for the unified manifest")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    inputs: List[InputSpec] = [parse_input_spec(spec) for spec in args.input]
    unified_manifest = build_unified_manifest(inputs)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    unified_manifest_path = output_dir / "unified_medical_manifest.csv"
    unified_manifest.to_csv(unified_manifest_path, index=False)

    if args.summary_json:
        summary_path = Path(args.summary_json)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_payload = {
            "rows": int(len(unified_manifest)),
            "modalities": sorted(unified_manifest["modality"].dropna().astype(str).unique().tolist()),
            "datasets": sorted(unified_manifest["dataset_name"].dropna().astype(str).unique().tolist()),
            "splits": sorted(unified_manifest["split"].dropna().astype(str).unique().tolist()),
        }
        summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    train_csv, val_csv, test_csv = _write_split_manifests(unified_manifest, output_dir)

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

    print("=" * 78)
    print("🏥 Unified Medical Model Training")
    print("=" * 78)
    print(f"Unified manifest: {unified_manifest_path}")
    print(f"Train split:      {train_csv}")
    print(f"Val split:        {val_csv}")
    print(f"Test split:       {test_csv}")
    print(f"Image root:       {args.image_root}")
    print(f"Backbone:         {config.backbone}")
    print(f"Output dir:       {output_dir}")
    print("=" * 78)

    train(
        image_root=Path(args.image_root),
        train_csv=train_csv,
        val_csv=val_csv,
        test_csv=test_csv,
        output_dir=output_dir,
        config=config,
    )


if __name__ == "__main__":
    main()
