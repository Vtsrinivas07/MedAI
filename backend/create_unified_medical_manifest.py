"""
Merge multiple medical dataset manifests into one unified manifest.

This helps build a single training index across modalities while keeping
per-dataset provenance and modality information.

Expected input CSV columns:
- image_path
- label

Optional input columns preserved when available:
- modality
- dataset_name
- split
- metadata

Example:
    python backend/create_unified_medical_manifest.py \
        --output datasets/unified/medical_manifest.csv \
        --input datasets/ham10000/manifests/train.csv skin ham10000 train \
        --input datasets/chest/manifests/train.csv chest chestxray14 train
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Sequence, Tuple

import pandas as pd


InputSpec = Tuple[Path, str, str, str]


def parse_input_spec(raw_value: Sequence[str]) -> InputSpec:
    if len(raw_value) != 4:
        raise ValueError(
            "Each --input must provide exactly 4 values: csv_path modality dataset_name split"
        )

    csv_path = Path(raw_value[0])
    modality = raw_value[1].strip().lower()
    dataset_name = raw_value[2].strip()
    split = raw_value[3].strip().lower()
    return csv_path, modality, dataset_name, split


def normalize_manifest_frame(frame: pd.DataFrame, modality: str, dataset_name: str, split: str) -> pd.DataFrame:
    if "image_path" not in frame.columns or "label" not in frame.columns:
        raise ValueError("Manifest must include image_path and label columns")

    output = frame.copy()
    output["modality"] = output.get("modality", modality)
    output["dataset_name"] = output.get("dataset_name", dataset_name)
    output["split"] = output.get("split", split)

    if "metadata" not in output.columns:
        output["metadata"] = "{}"
    else:
        output["metadata"] = output["metadata"].fillna("{}")

    for column in ["image_path", "label", "modality", "dataset_name", "split", "metadata"]:
        if column not in output.columns:
            output[column] = ""

    return output[["image_path", "label", "modality", "dataset_name", "split", "metadata"]]


def build_unified_manifest(inputs: List[InputSpec]) -> pd.DataFrame:
    frames = []
    for csv_path, modality, dataset_name, split in inputs:
        if not csv_path.exists():
            raise FileNotFoundError(f"Manifest not found: {csv_path}")

        frame = pd.read_csv(csv_path)
        frames.append(normalize_manifest_frame(frame, modality, dataset_name, split))

    if not frames:
        raise ValueError("No input manifests were provided")

    unified = pd.concat(frames, ignore_index=True)
    unified = unified.drop_duplicates(subset=["image_path", "label", "modality", "dataset_name", "split"])
    return unified


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create one unified medical manifest")
    parser.add_argument(
        "--input",
        nargs=4,
        action="append",
        metavar=("CSV", "MODALITY", "DATASET", "SPLIT"),
        required=True,
        help="Input manifest spec: csv_path modality dataset_name split",
    )
    parser.add_argument("--output", required=True, help="Output unified manifest CSV")
    parser.add_argument("--summary-json", help="Optional summary JSON path")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    inputs = [parse_input_spec(spec) for spec in args.input]
    unified = build_unified_manifest(inputs)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    unified.to_csv(output_path, index=False)

    if args.summary_json:
        summary = {
            "rows": int(len(unified)),
            "modalities": sorted(unified["modality"].dropna().astype(str).unique().tolist()),
            "datasets": sorted(unified["dataset_name"].dropna().astype(str).unique().tolist()),
            "splits": sorted(unified["split"].dropna().astype(str).unique().tolist()),
        }
        summary_path = Path(args.summary_json)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("✅ Unified manifest created")
    print(f"   Rows: {len(unified)}")
    print(f"   Output: {output_path}")


if __name__ == "__main__":
    main()
