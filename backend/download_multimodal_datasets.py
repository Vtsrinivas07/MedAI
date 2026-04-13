"""
Download script for multi-modal medical datasets (Option B).

Datasets covered by default:
- Skin: SD-198 (198 classes)
- Chest: COVID-19 Radiography Database (4 classes)
- Eye: Eye Diseases Classification (4 classes)
- Brain: Brain Tumor MRI (4 classes)

Total baseline coverage: 210 classes.
You can substitute ChestX-ray14 and ODIR-5K manually if you need 224+ classes exactly.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], cwd: str | None = None) -> bool:
    try:
        subprocess.check_call(command, cwd=cwd)
        return True
    except subprocess.CalledProcessError as error:
        print(f"❌ Command failed: {' '.join(command)}")
        print(f"   {error}")
        return False


def ensure_kaggle() -> bool:
    try:
        import kaggle  # noqa: F401
        return True
    except ImportError:
        print("📦 Installing Kaggle package...")
        return run_command([sys.executable, "-m", "pip", "install", "kaggle", "--quiet"])


def kaggle_credentials_present() -> bool:
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    return os.path.exists(kaggle_json)


def clone_or_pull(repo_url: str, target_dir: Path) -> bool:
    if target_dir.exists() and (target_dir / ".git").exists():
        print(f"🔄 Updating existing repo: {target_dir}")
        return run_command(["git", "pull"], cwd=str(target_dir))

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 Cloning {repo_url} -> {target_dir}")
    return run_command(["git", "clone", repo_url, str(target_dir)])


def download_kaggle_dataset(dataset_ref: str, target_dir: Path) -> bool:
    import kaggle

    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"📥 Downloading {dataset_ref} -> {target_dir}")
    try:
        kaggle.api.dataset_download_files(
            dataset_ref,
            path=str(target_dir),
            unzip=True,
            quiet=False,
        )
        return True
    except Exception as error:
        print(f"❌ Failed to download {dataset_ref}: {error}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Download multi-modal medical datasets")
    parser.add_argument(
        "--datasets-dir",
        default="datasets",
        help="Base datasets directory (default: datasets)",
    )
    parser.add_argument(
        "--modalities",
        nargs="+",
        choices=["skin", "chest", "eye", "brain"],
        default=["skin", "chest", "eye", "brain"],
        help="Modalities to download",
    )
    args = parser.parse_args()

    base_dir = Path(args.datasets_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("🏥 Multi-Modal Dataset Downloader")
    print("=" * 72)

    success = []
    failed = []

    if "skin" in args.modalities:
        ok = clone_or_pull(
            "https://github.com/xiaoxiaoxh/SD-198.git",
            base_dir / "sd-198",
        )
        (success if ok else failed).append("skin")

    kaggle_needed = any(mod in args.modalities for mod in ["chest", "eye", "brain"])

    if kaggle_needed:
        if not ensure_kaggle():
            print("❌ Kaggle package setup failed")
            print("   Skipping Kaggle-based downloads")
            for mod in ["chest", "eye", "brain"]:
                if mod in args.modalities:
                    failed.append(mod)
        elif not kaggle_credentials_present():
            print("❌ Kaggle credentials not found at ~/.kaggle/kaggle.json")
            print("   Create token at https://www.kaggle.com/settings/account")
            for mod in ["chest", "eye", "brain"]:
                if mod in args.modalities:
                    failed.append(mod)
        else:
            kaggle_datasets = {
                "chest": "tawsifurrahman/covid19-radiography-database",
                "eye": "gunavenkatdoddi/eye-diseases-classification",
                "brain": "masoudnickparvar/brain-tumor-mri-dataset",
            }

            for modality, dataset_ref in kaggle_datasets.items():
                if modality not in args.modalities:
                    continue
                ok = download_kaggle_dataset(dataset_ref, base_dir / modality)
                (success if ok else failed).append(modality)

    print("\n" + "=" * 72)
    print("✅ Download summary")
    print("=" * 72)
    print(f"Succeeded: {', '.join(success) if success else 'None'}")
    print(f"Failed:    {', '.join(failed) if failed else 'None'}")

    print("\n📌 Next steps:")
    print("1. Inspect folders and point training to class-subfolder image roots.")
    print("2. Train one modality at a time:")
    print("   python train_multimodal_model.py --modality skin --data-dir datasets/sd-198/release_v0/images")
    print("   python train_multimodal_model.py --modality chest --data-dir datasets/chest/COVID-19_Radiography_Dataset")
    print("   python train_multimodal_model.py --modality eye --data-dir datasets/eye")
    print("   python train_multimodal_model.py --modality brain --data-dir datasets/brain/Training")


if __name__ == "__main__":
    main()
