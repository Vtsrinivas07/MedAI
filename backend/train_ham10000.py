"""
Complete Training Script for EfficientNet on HAM10000 Dataset
Skin Lesion Classification - 7 Classes

Dataset: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import timm
from torchvision import transforms
from PIL import Image
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import os
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


# ==================== CONFIGURATION ====================
class Config:
    # Paths (update these to your dataset location)
    DATA_DIR = 'datasets/ham10000'
    IMG_DIR_1 = os.path.join(DATA_DIR, 'HAM10000_images_part_1')
    IMG_DIR_2 = os.path.join(DATA_DIR, 'HAM10000_images_part_2')
    METADATA_FILE = os.path.join(DATA_DIR, 'HAM10000_metadata.csv')
    
    # Output
    OUTPUT_DIR = 'models/weights'
    MODEL_NAME = 'efficientnet_skin_disease.pth'
    
    # Training
    BATCH_SIZE = 32
    NUM_EPOCHS = 30
    LEARNING_RATE = 0.001
    NUM_WORKERS = 4
    
    # Model
    MODEL_ARCH = 'efficientnet_b0'
    IMG_SIZE = 224
    
    # Classes (mapped from HAM10000)
    CLASS_NAMES = [
        'Normal',                    # nv - Melanocytic nevi
        'Melanoma',                  # mel
        'Benign Keratosis',          # bkl
        'Basal Cell Carcinoma',      # bcc
        'Actinic Keratosis',         # akiec
        'Vascular Lesion',           # vasc
        'Dermatofibroma'             # df
    ]
    
    CLASS_MAPPING = {
        'nv': 'Normal',
        'mel': 'Melanoma',
        'bkl': 'Benign Keratosis',
        'bcc': 'Basal Cell Carcinoma',
        'akiec': 'Actinic Keratosis',
        'vasc': 'Vascular Lesion',
        'df': 'Dermatofibroma'
    }


# ==================== DATASET CLASS ====================
class HAM10000Dataset(Dataset):
    """HAM10000 Skin Lesion Dataset"""
    
    def __init__(self, df, img_dirs, transform=None):
        self.df = df.reset_index(drop=True)
        self.img_dirs = img_dirs
        self.transform = transform
        
        # Class to index mapping
        self.class_to_idx = {name: idx for idx, name in enumerate(Config.CLASS_NAMES)}
        self.idx_to_class = {idx: name for name, idx in self.class_to_idx.items()}
    
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        
        # Find image in either directory
        img_name = row['image_id'] + '.jpg'
        img_path = None
        
        for img_dir in self.img_dirs:
            potential_path = os.path.join(img_dir, img_name)
            if os.path.exists(potential_path):
                img_path = potential_path
                break
        
        if img_path is None:
            raise FileNotFoundError(f"Image not found: {img_name}")
        
        # Load image
        image = Image.open(img_path).convert('RGB')
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        # Get label
        label = self.class_to_idx[row['diagnosis']]
        
        return image, label


# ==================== DATA LOADING ====================
def load_and_prepare_data():
    """Load HAM10000 metadata and prepare train/val/test splits"""
    
    print("📂 Loading HAM10000 metadata...")
    df = pd.read_csv(Config.METADATA_FILE)
    
    # Map dx codes to class names
    df['diagnosis'] = df['dx'].map(Config.CLASS_MAPPING)
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total images: {len(df)}")
    print(f"\n   Class distribution:")
    for class_name in Config.CLASS_NAMES:
        count = len(df[df['diagnosis'] == class_name])
        percentage = count / len(df) * 100
        print(f"   - {class_name:25s}: {count:5d} ({percentage:5.2f}%)")
    
    # Split data: 70% train, 15% val, 15% test
    train_df, temp_df = train_test_split(
        df, test_size=0.3, stratify=df['diagnosis'], random_state=42
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, stratify=temp_df['diagnosis'], random_state=42
    )
    
    print(f"\n📋 Split sizes:")
    print(f"   Train: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"   Val:   {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"   Test:  {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
    
    return train_df, val_df, test_df


# ==================== TRANSFORMS ====================
def get_transforms():
    """Get training and validation transforms"""
    
    train_transform = transforms.Compose([
        transforms.Resize((Config.IMG_SIZE, Config.IMG_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((Config.IMG_SIZE, Config.IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_transform


# ==================== MODEL ====================
def create_model(num_classes=7):
    """Create EfficientNet-B0 model"""
    
    print(f"\n🤖 Creating {Config.MODEL_ARCH} model...")
    model = timm.create_model(Config.MODEL_ARCH, pretrained=True)
    
    # Modify classifier
    in_features = model.classifier.in_features
    model.classifier = nn.Linear(in_features, num_classes)
    
    print(f"   Input features: {in_features}")
    print(f"   Output classes: {num_classes}")
    print(f"   Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    return model


# ==================== TRAINING ====================
def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(dataloader, desc='Training')
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'acc': f'{100.*correct/total:.2f}%'
        })
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100. * correct / total
    
    return epoch_loss, epoch_acc


def validate(model, dataloader, criterion, device):
    """Validate model"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        pbar = tqdm(dataloader, desc='Validation')
        for images, labels in pbar:
            images, labels = images.to(device), labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100. * correct / total
    
    return epoch_loss, epoch_acc, all_preds, all_labels


# ==================== MAIN TRAINING LOOP ====================
def train():
    """Main training function"""
    
    print("=" * 70)
    print("🏥 HAM10000 Skin Lesion Classification Training")
    print("=" * 70)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n💻 Device: {device}")
    
    # Load data
    train_df, val_df, test_df = load_and_prepare_data()
    
    # Get transforms
    train_transform, val_transform = get_transforms()
    
    # Create datasets
    img_dirs = [Config.IMG_DIR_1, Config.IMG_DIR_2]
    train_dataset = HAM10000Dataset(train_df, img_dirs, train_transform)
    val_dataset = HAM10000Dataset(val_df, img_dirs, val_transform)
    test_dataset = HAM10000Dataset(test_df, img_dirs, val_transform)
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset, 
        batch_size=Config.BATCH_SIZE,
        shuffle=True,
        num_workers=Config.NUM_WORKERS,
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=Config.BATCH_SIZE,
        shuffle=False,
        num_workers=Config.NUM_WORKERS,
        pin_memory=True
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=Config.BATCH_SIZE,
        shuffle=False,
        num_workers=Config.NUM_WORKERS,
        pin_memory=True
    )
    
    # Create model
    model = create_model(num_classes=len(Config.CLASS_NAMES))
    model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=Config.LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=3, verbose=True
    )
    
    # Training loop
    print(f"\n🚀 Starting training for {Config.NUM_EPOCHS} epochs...")
    best_val_acc = 0.0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    for epoch in range(Config.NUM_EPOCHS):
        print(f"\n{'='*70}")
        print(f"Epoch {epoch+1}/{Config.NUM_EPOCHS}")
        print(f"{'='*70}")
        
        # Train
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        
        # Validate
        val_loss, val_acc, val_preds, val_labels = validate(model, val_loader, criterion, device)
        
        # Update scheduler
        scheduler.step(val_loss)
        
        # Save history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        # Print results
        print(f"\n📊 Results:")
        print(f"   Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"   Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            
            os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
            save_path = os.path.join(Config.OUTPUT_DIR, Config.MODEL_NAME)
            
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_acc': val_acc,
                'num_classes': len(Config.CLASS_NAMES),
                'disease_classes': Config.CLASS_NAMES,
                'model_name': Config.MODEL_ARCH
            }, save_path)
            
            print(f"\n✅ New best model saved! (Val Acc: {val_acc:.2f}%)")
    
    print(f"\n{'='*70}")
    print(f"✅ Training Complete!")
    print(f"   Best Validation Accuracy: {best_val_acc:.2f}%")
    print(f"   Model saved to: {os.path.join(Config.OUTPUT_DIR, Config.MODEL_NAME)}")
    print(f"{'='*70}")
    
    # Test on test set
    print("\n🧪 Evaluating on test set...")
    test_loss, test_acc, test_preds, test_labels = validate(model, test_loader, criterion, device)
    
    print(f"\n📊 Test Results:")
    print(f"   Test Loss: {test_loss:.4f}")
    print(f"   Test Acc:  {test_acc:.2f}%")
    
    # Classification report
    print("\n📋 Classification Report:")
    print(classification_report(
        test_labels, test_preds,
        target_names=Config.CLASS_NAMES,
        digits=4
    ))
    
    # Confusion matrix
    cm = confusion_matrix(test_labels, test_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=Config.CLASS_NAMES,
                yticklabels=Config.CLASS_NAMES)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
    print("\n✅ Confusion matrix saved to: confusion_matrix.png")
    
    return model, history


# ==================== MAIN ====================
if __name__ == "__main__":
    # Check if dataset exists
    if not os.path.exists(Config.METADATA_FILE):
        print("❌ Error: HAM10000 dataset not found!")
        print("\n📥 Please download the dataset from:")
        print("   https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000")
        print("\n📂 Expected structure:")
        print("   datasets/ham10000/")
        print("   ├── HAM10000_metadata.csv")
        print("   ├── HAM10000_images_part_1/")
        print("   └── HAM10000_images_part_2/")
    else:
        # Train model
        model, history = train()
        
        print("\n🎉 All done! Your model is ready to use.")
        print("\n📝 Next steps:")
        print("   1. Copy the model to your API:")
        print(f"      cp {os.path.join(Config.OUTPUT_DIR, Config.MODEL_NAME)} backend/models/weights/")
        print("   2. Restart your FastAPI server")
        print("   3. Test the /api/diagnose endpoint")
