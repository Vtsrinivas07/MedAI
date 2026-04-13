"""
Utility script to create a demo EfficientNet model for testing infrastructure
Run this to generate a placeholder .pth file before you have your trained weights

Usage:
    python backend/create_demo_model.py
"""

import torch
import torch.nn as nn
import timm
import os


MODALITY_CLASSES = {
    "skin": [
        "Acne",
        "Eczema",
        "Melanoma",
        "Psoriasis",
        "Vitiligo",
        "Rosacea",
        "Normal",
    ],
    "chest": [
        "Atelectasis",
        "Cardiomegaly",
        "Effusion",
        "Infiltration",
        "Mass",
        "Nodule",
        "Pneumonia",
        "Pneumothorax",
        "Consolidation",
        "Edema",
        "Emphysema",
        "Fibrosis",
        "Pleural Thickening",
        "Hernia",
    ],
    "eye": [
        "Normal",
        "Diabetic Retinopathy",
        "Glaucoma",
        "Cataract",
        "Age-related Macular Degeneration",
        "Hypertension",
        "Myopia",
        "Other Abnormalities",
    ],
    "brain": [
        "Glioma",
        "Meningioma",
        "Pituitary",
        "No Tumor",
    ],
}


DEFAULT_OUTPUTS = {
    "skin": "backend/models/weights/efficientnet_skin_disease.pth",
    "chest": "backend/models/weights/efficientnet_chest_disease.pth",
    "eye": "backend/models/weights/efficientnet_eye_disease.pth",
    "brain": "backend/models/weights/efficientnet_brain_disease.pth",
}


def create_demo_model(
    save_path: str = "backend/models/weights/efficientnet_skin_disease.pth",
    modality: str = "skin"
):
    """
    Create a demo/untrained EfficientNet-B0 model for testing
    
    This creates a model with random weights that can be used to test
    the infrastructure. Replace this with your trained model when ready.
    """
    print("🔧 Creating demo EfficientNet-B0 model...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    modality = modality.lower().strip()
    if modality not in MODALITY_CLASSES:
        raise ValueError(f"Unsupported modality '{modality}'. Supported: {list(MODALITY_CLASSES.keys())}")

    disease_classes = MODALITY_CLASSES[modality]
    num_classes = len(disease_classes)
    
    # Create EfficientNet-B0
    print(f"   Loading EfficientNet-B0 architecture...")
    model = timm.create_model('efficientnet_b0', pretrained=False)
    
    # Modify classifier for our disease classes
    in_features = model.classifier.in_features
    model.classifier = nn.Linear(in_features, num_classes)
    
    print(f"   Modified classifier: {in_features} -> {num_classes} classes")
    
    # Save model state dict
    model_data = {
        'model_state_dict': model.state_dict(),
        'modality': modality,
        'num_classes': num_classes,
        'disease_classes': disease_classes,
        'model_name': 'efficientnet_b0',
        'note': 'DEMO MODEL - Random weights for testing only. Replace with trained weights.'
    }
    
    torch.save(model_data, save_path)
    
    file_size_mb = os.path.getsize(save_path) / (1024 * 1024)
    
    print(f"✅ Demo model saved to: {save_path}")
    print(f"   Modality: {modality}")
    print(f"   File size: {file_size_mb:.2f} MB")
    print(f"   Classes: {num_classes}")
    print(f"\n⚠️  IMPORTANT: This is a DEMO model with random weights!")
    print(f"   Predictions will be random and NOT accurate.")
    print(f"   Replace with your trained .pth file for real predictions.")
    print(f"\n📝 To replace with your trained model:")
    print(f"   1. Train your EfficientNet-B0 on your skin disease dataset")
    print(f"   2. Save the trained weights")
    print(f"   3. Copy to: {save_path}")
    print(f"   4. Restart the server")


def load_trained_model(model_path: str):
    """
    Load and verify a trained model
    
    Args:
        model_path: Path to trained .pth file
    """
    print(f"🔍 Loading model from: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"❌ Error: Model file not found at {model_path}")
        return
    
    try:
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        
        print("✅ Model loaded successfully!")
        print("\n📊 Model Information:")
        
        if isinstance(checkpoint, dict):
            for key in checkpoint.keys():
                if key != 'model_state_dict' and key != 'state_dict':
                    print(f"   {key}: {checkpoint[key]}")
            
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint
            
            # Count parameters
            total_params = sum(p.numel() for p in state_dict.values())
            print(f"   Total parameters: {total_params:,}")
        else:
            print("   Checkpoint format: Raw state_dict")
        
        print("\n✅ Model verification passed!")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "verify":
            # Verify existing model
            model_path = sys.argv[2] if len(sys.argv) > 2 else "backend/models/weights/efficientnet_skin_disease.pth"
            load_trained_model(model_path)
        elif sys.argv[1] == "create":
            # Create demo model
            modality = sys.argv[2] if len(sys.argv) > 2 else "skin"
            save_path = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_OUTPUTS.get(modality, DEFAULT_OUTPUTS["skin"])
            create_demo_model(save_path, modality=modality)
        elif sys.argv[1] == "create-all":
            for modality, output in DEFAULT_OUTPUTS.items():
                create_demo_model(output, modality=modality)
        else:
            print("Usage:")
            print("  python backend/create_demo_model.py create [modality] [path]  - Create demo model")
            print("  python backend/create_demo_model.py create-all                  - Create all modality models")
            print("  python backend/create_demo_model.py verify [path]  - Verify existing model")
    else:
        # Default: create demo model
        create_demo_model(DEFAULT_OUTPUTS["skin"], modality="skin")
