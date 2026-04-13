"""
Quick Dataset Download Script
Downloads HAM10000 dataset using Kaggle API
"""

import os
import zipfile
import subprocess
import sys


def check_kaggle_api():
    """Check if Kaggle API is installed and configured"""
    try:
        import kaggle
        print("✅ Kaggle API installed")
        return True
    except ImportError:
        print("❌ Kaggle API not installed")
        print("\n📦 Installing Kaggle API...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "--quiet"])
        print("✅ Kaggle API installed")
        return True


def check_kaggle_credentials():
    """Check if Kaggle credentials are configured"""
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    
    if os.path.exists(kaggle_json):
        print("✅ Kaggle credentials found")
        return True
    else:
        print("❌ Kaggle credentials not found")
        print("\n🔑 To set up Kaggle API:")
        print("   1. Go to: https://www.kaggle.com/settings/account")
        print("   2. Scroll to 'API' section")
        print("   3. Click 'Create New API Token'")
        print("   4. This downloads kaggle.json")
        print("   5. Move it to: ~/.kaggle/kaggle.json")
        print("   6. On Linux/Mac: chmod 600 ~/.kaggle/kaggle.json")
        return False


def download_ham10000(output_dir="datasets/ham10000"):
    """Download HAM10000 dataset from Kaggle"""
    
    print("\n" + "="*70)
    print("📥 Downloading HAM10000 Dataset")
    print("="*70)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Download dataset
    print("\n📦 Downloading from Kaggle...")
    print("   Dataset: kmader/skin-cancer-mnist-ham10000")
    print("   Size: ~1.9 GB")
    print("   This may take a few minutes...\n")
    
    try:
        import kaggle
        kaggle.api.dataset_download_files(
            'kmader/skin-cancer-mnist-ham10000',
            path=output_dir,
            unzip=True,
            quiet=False
        )
        print("\n✅ Download complete!")
        return True
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False


def verify_dataset(dataset_dir="datasets/ham10000"):
    """Verify dataset structure"""
    
    print("\n" + "="*70)
    print("🔍 Verifying Dataset")
    print("="*70)
    
    required_files = [
        'HAM10000_metadata.csv',
        'HAM10000_images_part_1',
        'HAM10000_images_part_2'
    ]
    
    all_present = True
    for item in required_files:
        path = os.path.join(dataset_dir, item)
        if os.path.exists(path):
            if item.endswith('.csv'):
                print(f"   ✅ {item}")
            else:
                num_images = len([f for f in os.listdir(path) if f.endswith('.jpg')])
                print(f"   ✅ {item} ({num_images} images)")
        else:
            print(f"   ❌ {item} - NOT FOUND")
            all_present = False
    
    if all_present:
        print("\n✅ Dataset verification successful!")
        return True
    else:
        print("\n❌ Dataset incomplete")
        return False


def main():
    """Main function"""
    
    print("="*70)
    print("🏥 HAM10000 Dataset Downloader")
    print("="*70)
    
    # Check Kaggle API
    if not check_kaggle_api():
        print("\n❌ Failed to install Kaggle API")
        return
    
    # Check credentials
    if not check_kaggle_credentials():
        print("\n❌ Please configure Kaggle credentials first")
        return
    
    # Download dataset
    output_dir = "datasets/ham10000"
    
    if os.path.exists(os.path.join(output_dir, 'HAM10000_metadata.csv')):
        print(f"\n⚠️  Dataset already exists in: {output_dir}")
        response = input("   Download again? (y/n): ")
        if response.lower() != 'y':
            print("   Skipping download")
            verify_dataset(output_dir)
            return
    
    success = download_ham10000(output_dir)
    
    if success:
        # Verify
        verify_dataset(output_dir)
        
        print("\n" + "="*70)
        print("✅ Setup Complete!")
        print("="*70)
        print("\n📂 Dataset location:", os.path.abspath(output_dir))
        print("\n🚀 Next steps:")
        print("   1. Train the model:")
        print("      python train_ham10000.py")
        print("   2. Wait for training to complete (~2-4 hours on GPU)")
        print("   3. Model will be saved to: models/weights/efficientnet_skin_disease.pth")
        print("   4. Restart your API server to use the trained model")


if __name__ == "__main__":
    main()
