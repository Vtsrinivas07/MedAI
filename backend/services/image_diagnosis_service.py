"""Medical image diagnosis service for MedMNIST 2D subsets using EfficientNet-B0."""

import os
import io
import logging
from typing import Dict, Optional

import timm
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

from models.medmnist_labels import MEDMNIST_MODALITY_CONFIGS, normalize_medmnist_modality

logger = logging.getLogger(__name__)


class ImageDiagnosisService:
    """Service for medical image classification across configured MedMNIST modalities."""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    WEIGHTS_DIR = os.path.join(BASE_DIR, "models", "weights")
    MODEL_PATH = os.path.join(WEIGHTS_DIR, "efficientnet_skin_disease.pth")
    BACKBONE = "efficientnet_b0"
    IMAGE_SIZE = 224
    
    def __init__(
        self,
        model_path: str = MODEL_PATH,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize the image diagnosis service
        
        Args:
            model_path: Backward-compatible explicit model path for skin
            confidence_threshold: Minimum confidence for predictions (0-1)
        """
        self.confidence_threshold = confidence_threshold
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        self.models = {}
        self.model_metadata = {}
        self.class_names_by_modality: dict[str, list[str]] = {}
        self.backbone_by_modality: dict[str, str] = {}
        self.image_size_by_modality: dict[str, int] = {}
        self.transform_by_size: dict[int, transforms.Compose] = {}

        logger.info(f"🩺 Initializing Image Diagnosis Service")
        logger.info(f"   Device: {self.device}")
        logger.info(f"   Confidence threshold: {confidence_threshold}")

        # Prefer explicit path for backward compatibility (skin), then scan known modality files.
        if os.path.exists(self.model_path):
            try:
                self._load_model_for_modality("skin", self.model_path)
            except Exception as exc:
                logger.warning(f"⚠️ Failed to load explicit model from {self.model_path}: {exc}")

        for modality, cfg in MEDMNIST_MODALITY_CONFIGS.items():
            path = self._weight_path_for_modality(modality)
            if modality == "skin" and os.path.exists(self.model_path):
                continue
            if not os.path.exists(path):
                continue
            try:
                self._load_model_for_modality(modality, path)
            except Exception as exc:
                logger.warning(f"⚠️ Failed to load {modality} model from {path}: {exc}")

        if not self.models:
            logger.warning("⚠️ No MedMNIST EfficientNet weights loaded")
    
    def _get_transform(self, image_size: int = 224) -> transforms.Compose:
        """
        Get image preprocessing transformations
        Uses ImageNet normalization (standard for EfficientNet)
        
        Returns:
            torchvision transforms composition
        """
        return transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],  # ImageNet mean
                std=[0.229, 0.224, 0.225]     # ImageNet std
            )
        ])
    
    def _create_model(self, backbone: str, num_classes: int) -> nn.Module:
        """
        Create EfficientNet model architecture
        
        Returns:
            PyTorch model
        """
        model = timm.create_model(backbone, pretrained=False)
        
        # Modify classifier for our number of disease classes
        if hasattr(model, 'classifier') and isinstance(model.classifier, nn.Linear):
            in_features = model.classifier.in_features
            model.classifier = nn.Linear(in_features, num_classes)
        elif hasattr(model, 'get_classifier'):
            classifier = model.get_classifier()
            in_features = classifier.in_features
            model.classifier = nn.Linear(in_features, num_classes)
        else:
            raise RuntimeError(f"Unsupported backbone head for {backbone}")

        return model

    @staticmethod
    def _extract_state_dict(checkpoint):
        if isinstance(checkpoint, dict):
            if 'model_state_dict' in checkpoint:
                return checkpoint['model_state_dict'], checkpoint
            if 'state_dict' in checkpoint:
                return checkpoint['state_dict'], checkpoint
        return checkpoint, checkpoint if isinstance(checkpoint, dict) else {}

    @staticmethod
    def _clean_state_dict(state_dict):
        if not isinstance(state_dict, dict):
            return state_dict

        cleaned_state_dict = {}
        for key, value in state_dict.items():
            if key.startswith('module.'):
                cleaned_state_dict[key[len('module.'):]] = value
            else:
                cleaned_state_dict[key] = value
        return cleaned_state_dict

    def _resolve_class_names(self, metadata: dict, modality: str) -> list[str]:
        class_names = metadata.get('disease_classes') or metadata.get('class_names')
        if class_names:
            return list(class_names)

        cfg = MEDMNIST_MODALITY_CONFIGS.get(modality, {})
        fallback = cfg.get("task_name") or modality
        return [f"{fallback}_class_{i}" for i in range(32)]

    def _load_model_for_modality(self, modality: str, model_path: str):
        """Load modality model weights from .pth file."""
        try:
            logger.info(f"📥 Loading {modality} model weights from {model_path}")

            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            state_dict, metadata = self._extract_state_dict(checkpoint)
            state_dict = self._clean_state_dict(state_dict)

            meta_dict = dict(metadata) if isinstance(metadata, dict) else {}
            class_names = self._resolve_class_names(meta_dict, modality)
            if isinstance(state_dict, dict):
                for key in ("classifier.weight", "head.fc.weight", "fc.weight"):
                    if key in state_dict and hasattr(state_dict[key], "shape"):
                        n = int(state_dict[key].shape[0])
                        if n > 0 and len(class_names) != n:
                            class_names = class_names[:n] if len(class_names) > n else class_names + [f"class_{i}" for i in range(len(class_names), n)]
                        break

            backbone = meta_dict.get('backbone') or meta_dict.get('model_name') or self.BACKBONE
            image_size = int(meta_dict.get('image_size') or self.IMAGE_SIZE)
            transform = self.transform_by_size.get(image_size)
            if not transform:
                transform = self._get_transform(image_size)
                self.transform_by_size[image_size] = transform

            cfg = MEDMNIST_MODALITY_CONFIGS.get(modality, {})
            if "multi_label" not in meta_dict:
                meta_dict["multi_label"] = bool(cfg.get("multi_label", False))
            meta_dict["ui_modality"] = modality
            meta_dict["weight_path"] = model_path
            self.model_metadata[modality] = meta_dict
            self.class_names_by_modality[modality] = class_names
            self.backbone_by_modality[modality] = backbone
            self.image_size_by_modality[modality] = image_size

            model = self._create_model(backbone, num_classes=len(class_names))
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()

            self.models[modality] = model

            logger.info(f"✅ {modality} model loaded successfully")
            logger.info(f"   Backbone: {backbone}")
            logger.info(f"   Image size: {image_size}")
            logger.info(f"   Classes: {len(class_names)}")
            logger.info(f"   Parameters: {sum(p.numel() for p in model.parameters()):,}")

        except Exception as e:
            logger.error(f"❌ Failed to load {modality} model: {e}")
            raise

    def refresh_models(self) -> Dict[str, bool]:
        """Scan known weight files and load any newly available modality models."""
        refreshed: Dict[str, bool] = {}
        for modality, cfg in MEDMNIST_MODALITY_CONFIGS.items():
            if modality in self.models:
                refreshed[modality] = False
                continue

            path = self._weight_path_for_modality(modality)
            if not os.path.exists(path):
                refreshed[modality] = False
                continue

            try:
                self._load_model_for_modality(modality, path)
                refreshed[modality] = True
            except Exception as exc:
                logger.warning(f"⚠️ Refresh failed for {modality} from {path}: {exc}")
                refreshed[modality] = False
        return refreshed
    
    def preprocess_image(self, image_data: bytes, image_size: int) -> torch.Tensor:
        """
        Preprocess image for model input
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Preprocessed tensor (1, 3, 224, 224)
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB (handle RGBA, grayscale, etc.)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply transformations
            transform = self.transform_by_size.get(image_size)
            if not transform:
                transform = self._get_transform(image_size)
                self.transform_by_size[image_size] = transform
            tensor = transform(image)
            
            # Add batch dimension
            tensor = tensor.unsqueeze(0)
            
            return tensor
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise ValueError(f"Invalid image data: {e}")
    
    def _select_modality(self, requested_modality: Optional[str]) -> str:
        if requested_modality in (None, "", "auto"):
            if "skin" in self.models:
                return "skin"
            if self.models:
                return next(iter(self.models.keys()))
            raise RuntimeError(
                "No MedMNIST model weights are loaded. Add trained .pth files to "
                "backend/models/weights or run: cd backend && python "
                "scripts/train_medmnist_efficientnet.py --all"
            )

        modality = normalize_medmnist_modality(requested_modality, default="skin")
        if modality not in self.models:
            available = ", ".join(sorted(self.models.keys())) or "none"
            expected_path = self._expected_weight_path(modality)
            raise RuntimeError(
                f"Requested modality '{requested_modality}' is not loaded. Available: {available}. "
                f"Expected weight file: {expected_path}. Train it with: "
                f"{self._training_command_for(modality)}"
            )
        return modality

    def predict(self, image_data: bytes, modality: str = "auto") -> Dict:
        """
        Predict disease from image
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with prediction results:
            {
                'disease': str,
                'confidence': float,
                'all_predictions': List[Dict],
                'meets_threshold': bool
            }
        """
        selected_modality = self._select_modality(modality)
        model = self.models[selected_modality]
        class_names = self.class_names_by_modality[selected_modality]
        model_meta = self.model_metadata.get(selected_modality, {})
        image_size = int(self.image_size_by_modality.get(selected_modality, self.IMAGE_SIZE))
        
        try:
            # Preprocess image
            tensor = self.preprocess_image(image_data, image_size=image_size)
            tensor = tensor.to(self.device)

            multi_label = bool(model_meta.get("multi_label", False))

            # Run inference
            with torch.no_grad():
                logits = model(tensor)
                if multi_label:
                    probabilities = torch.sigmoid(logits)
                    probs = probabilities[0].cpu().numpy()
                else:
                    probabilities = torch.nn.functional.softmax(logits, dim=1)
                    probs = probabilities[0].cpu().numpy()

            # Get top prediction (highest probability mass)
            top_idx = int(probs.argmax())
            top_disease = class_names[top_idx]
            top_confidence = float(probs[top_idx])

            # Get all predictions sorted by confidence
            all_predictions = [
                {
                    'disease': class_names[i],
                    'confidence': float(probs[i])
                }
                for i in range(len(class_names))
            ]
            all_predictions.sort(key=lambda x: x['confidence'], reverse=True)

            if multi_label:
                meets_threshold = top_confidence >= max(0.35, self.confidence_threshold * 0.5)
            else:
                meets_threshold = top_confidence >= self.confidence_threshold

            result = {
                'modality': selected_modality,
                'disease': top_disease,
                'confidence': top_confidence,
                'all_predictions': all_predictions,
                'meets_threshold': meets_threshold,
                'multi_label': multi_label,
            }

            logger.info(
                f"🔍 Prediction ({selected_modality}): {top_disease} ({top_confidence:.2%})"
            )

            return result

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise

    def predict_from_file(self, file_path: str) -> Dict:
        """
        Predict disease from image file path
        
        Args:
            file_path: Path to image file
            
        Returns:
            Prediction dictionary (same as predict())
        """
        with open(file_path, 'rb') as f:
            image_data = f.read()
        return self.predict(image_data, modality="auto")

    def _expected_weight_path(self, modality: str) -> str:
        cfg = MEDMNIST_MODALITY_CONFIGS.get(modality, {})
        weight_file = cfg.get("weight_file")
        if not weight_file:
            return ""
        return self._weight_path_for_modality(modality)

    def _weight_path_for_modality(self, modality: str) -> str:
        cfg = MEDMNIST_MODALITY_CONFIGS.get(modality, {})
        weight_file = cfg.get("weight_file")
        if not weight_file:
            return ""
        return os.path.join(self.WEIGHTS_DIR, weight_file)

    def _training_command_for(self, modality: str) -> str:
        return f"cd backend && python scripts/train_medmnist_efficientnet.py --modality {modality}"

    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model metadata
        """
        self.refresh_models()
        supported_modalities = sorted(list(MEDMNIST_MODALITY_CONFIGS.keys()))
        loaded_modalities = sorted(list(self.models.keys()))
        missing_modalities = [m for m in supported_modalities if m not in self.models]

        return {
            'ready': bool(loaded_modalities),
            'status_message': (
                f"Loaded modalities: {', '.join(loaded_modalities)}"
                if loaded_modalities
                else "No MedMNIST weights loaded. Diagnosis requests will return 503 until weights are added."
            ),
            'model_name': 'EfficientNet-B0',
            'supported_modalities': supported_modalities,
            'loaded_modalities': loaded_modalities,
            'missing_modalities': missing_modalities,
            'confidence_threshold': self.confidence_threshold,
            'device': str(self.device),
            'training': {
                'train_all_command': 'cd backend && python scripts/train_medmnist_efficientnet.py --all',
                'missing_modality_commands': {
                    modality: self._training_command_for(modality)
                    for modality in missing_modalities
                },
            },
            'modalities': {
                modality: {
                    'model_name': self.backbone_by_modality.get(modality, self.BACKBONE).replace('_', '-').upper(),
                    'backbone': self.backbone_by_modality.get(modality, self.BACKBONE),
                    'modality': modality,
                    'num_classes': len(self.class_names_by_modality.get(modality, [])),
                    'disease_classes': self.class_names_by_modality.get(modality, []),
                    'input_size': (
                        self.image_size_by_modality.get(modality, self.IMAGE_SIZE),
                        self.image_size_by_modality.get(modality, self.IMAGE_SIZE),
                    ),
                    'confidence_threshold': self.confidence_threshold,
                    'device': str(self.device),
                    'model_loaded': modality in self.models,
                    'model_path': self.model_metadata.get(modality, {}).get('weight_path') or self._expected_weight_path(modality),
                    'expected_weight_path': self._expected_weight_path(modality),
                    'dataset': self.model_metadata.get(modality, {}).get('dataset'),
                    'task': self.model_metadata.get(modality, {}).get('medmnist_task'),
                    'multi_label': bool(self.model_metadata.get(modality, {}).get('multi_label', False)),
                    'train_command': self._training_command_for(modality),
                }
                for modality in supported_modalities
            },
        }


# Singleton instance
_diagnosis_service_instance = None

def get_diagnosis_service() -> ImageDiagnosisService:
    """Get or create singleton diagnosis service instance"""
    global _diagnosis_service_instance
    if _diagnosis_service_instance is None:
        _diagnosis_service_instance = ImageDiagnosisService()
    return _diagnosis_service_instance
