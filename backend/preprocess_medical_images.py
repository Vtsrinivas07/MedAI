"""
Medical image preprocessing utilities.

This script prepares stratified train/val/test CSV manifests that can be used by
EfficientNet training code. It supports:
- Generic ImageFolder-style datasets
- HAM10000 metadata + image folders

Example:
    python backend/preprocess_medical_images.py \
        --mode ham10000 \
        --metadata-csv datasets/ham10000/HAM10000_metadata.csv \
        --image-root datasets/ham10000/HAM10000_images \
        --output-dir datasets/ham10000/manifests

    python backend/preprocess_medical_images.py \
        --mode imagefolder \
        --image-root datasets/sd-198/release_v0/images \
        --output-dir datasets/sd-198/manifests
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _scan_imagefolder(image_root: Path) -> pd.DataFrame:
    records: List[Dict[str, str]] = []

    for class_dir in sorted(path for path in image_root.iterdir() if path.is_dir()):
        label = class_dir.name
        for image_path in class_dir.rglob("*"):
            if image_path.suffix.lower() in IMAGE_EXTENSIONS:
                records.append(
                    {
                        "image_path": str(image_path.relative_to(image_root)).replace("\\", "/"),
                        "label": label,
                    }
                )

    if not records:
        raise ValueError(f"No image files found under {image_root}")

    return pd.DataFrame(records)


def _index_images(image_root: Path) -> Dict[str, Path]:
    image_index: Dict[str, Path] = {}
    for image_path in image_root.rglob("*"):
        if image_path.suffix.lower() in IMAGE_EXTENSIONS:
            image_index[image_path.stem] = image_path
    return image_index


def _prepare_ham10000(metadata_csv: Path, image_root: Path) -> pd.DataFrame:
    metadata = pd.read_csv(metadata_csv)
    if "dx" not in metadata.columns:
        raise ValueError("HAM10000 metadata must include a 'dx' label column")

    image_index = _index_images(image_root)
    records: List[Dict[str, str]] = []

    image_id_column = "image_id" if "image_id" in metadata.columns else "image" if "image" in metadata.columns else None
    if not image_id_column:
        raise ValueError("HAM10000 metadata must include an 'image_id' or 'image' column")

    for _, row in metadata.iterrows():
        image_id = str(row[image_id_column])
        label = str(row["dx"])
        image_path = image_index.get(image_id)
        if image_path is None:
            continue

        records.append(
            {
                "image_path": str(image_path.relative_to(image_root)).replace("\\", "/"),
                "label": label,
            }
        )

    if not records:
        raise ValueError(
            f"No HAM10000 image files were matched under {image_root}. "
            "Check the image root and metadata CSV."
        )

    return pd.DataFrame(records)


def _split_manifest(
    manifest: pd.DataFrame,
    output_dir: Path,
    val_size: float = 0.15,
    test_size: float = 0.15,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_df, temp_df = train_test_split(
        manifest,
        test_size=val_size + test_size,
        random_state=seed,
        stratify=manifest["label"],
    )

    relative_val_size = val_size / (val_size + test_size)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=1 - relative_val_size,
        random_state=seed,
        stratify=temp_df["label"],
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(output_dir / "train.csv", index=False)
    val_df.to_csv(output_dir / "val.csv", index=False)
    test_df.to_csv(output_dir / "test.csv", index=False)

    return train_df, val_df, test_df


def prepare_manifests(
    mode: str,
    image_root: Path,
    output_dir: Path,
    metadata_csv: Optional[Path] = None,
    val_size: float = 0.15,
    test_size: float = 0.15,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if mode == "imagefolder":
        manifest = _scan_imagefolder(image_root)
    elif mode == "ham10000":
        if metadata_csv is None:
            raise ValueError("metadata_csv is required for ham10000 mode")
        manifest = _prepare_ham10000(metadata_csv, image_root)
    else:
        raise ValueError("mode must be either 'imagefolder' or 'ham10000'")

    return _split_manifest(manifest, output_dir, val_size=val_size, test_size=test_size, seed=seed)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare manifests for medical image training")
    parser.add_argument("--mode", choices=["imagefolder", "ham10000"], required=True)
    parser.add_argument("--image-root", required=True, help="Root directory that contains class folders or HAM10000 images")
    parser.add_argument("--metadata-csv", help="HAM10000 metadata CSV path")
    parser.add_argument("--output-dir", required=True, help="Where train.csv/val.csv/test.csv will be written")
    parser.add_argument("--val-size", type=float, default=0.15)
    parser.add_argument("--test-size", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    image_root = Path(args.image_root)
    output_dir = Path(args.output_dir)
    metadata_csv = Path(args.metadata_csv) if args.metadata_csv else None

    train_df, val_df, test_df = prepare_manifests(
        mode=args.mode,
        image_root=image_root,
        output_dir=output_dir,
        metadata_csv=metadata_csv,
        val_size=args.val_size,
        test_size=args.test_size,
        seed=args.seed,
    )

    print("✅ Manifests created")
    print(f"   Train: {len(train_df)}")
    print(f"   Val:   {len(val_df)}")
    print(f"   Test:  {len(test_df)}")
    print(f"   Output: {output_dir}")


if __name__ == "__main__":
    main()
