"""MedMNIST modality metadata for 2D EfficientNet pipelines."""

from __future__ import annotations

MEDMNIST_MODALITY_CONFIGS: dict[str, dict] = {
    "skin": {
        "dataset_class": "DermaMNIST",
        "task_name": "dermamnist",
        "dataset_id": "MedMNIST-DermaMNIST",
        "weight_file": "efficientnet_skin_disease.pth",
        "multi_label": False,
    },
    "pathology": {
        "dataset_class": "PathMNIST",
        "task_name": "pathmnist",
        "dataset_id": "MedMNIST-PathMNIST",
        "weight_file": "efficientnet_pathology_disease.pth",
        "multi_label": False,
    },
    "chest": {
        "dataset_class": "ChestMNIST",
        "task_name": "chestmnist",
        "dataset_id": "MedMNIST-ChestMNIST",
        "weight_file": "efficientnet_chest_disease.pth",
        "multi_label": True,
    },
    "oct": {
        "dataset_class": "OCTMNIST",
        "task_name": "octmnist",
        "dataset_id": "MedMNIST-OCTMNIST",
        "weight_file": "efficientnet_oct_disease.pth",
        "multi_label": False,
    },
    "pneumonia": {
        "dataset_class": "PneumoniaMNIST",
        "task_name": "pneumoniamnist",
        "dataset_id": "MedMNIST-PneumoniaMNIST",
        "weight_file": "efficientnet_pneumonia_disease.pth",
        "multi_label": False,
    },
    "retina": {
        "dataset_class": "RetinaMNIST",
        "task_name": "retinamnist",
        "dataset_id": "MedMNIST-RetinaMNIST",
        "weight_file": "efficientnet_retina_disease.pth",
        "multi_label": False,
    },
    "blood": {
        "dataset_class": "BloodMNIST",
        "task_name": "bloodmnist",
        "dataset_id": "MedMNIST-BloodMNIST",
        "weight_file": "efficientnet_blood_disease.pth",
        "multi_label": False,
    },
    "tissue": {
        "dataset_class": "TissueMNIST",
        "task_name": "tissuemnist",
        "dataset_id": "MedMNIST-TissueMNIST",
        "weight_file": "efficientnet_tissue_disease.pth",
        "multi_label": False,
    },
    "breast": {
        "dataset_class": "BreastMNIST",
        "task_name": "breastmnist",
        "dataset_id": "MedMNIST-BreastMNIST",
        "weight_file": "efficientnet_breast_disease.pth",
        "multi_label": False,
    },
    "organa": {
        "dataset_class": "OrganAMNIST",
        "task_name": "organamnist",
        "dataset_id": "MedMNIST-OrganAMNIST",
        "weight_file": "efficientnet_organa_disease.pth",
        "multi_label": False,
    },
    "organc": {
        "dataset_class": "OrganCMNIST",
        "task_name": "organcmnist",
        "dataset_id": "MedMNIST-OrganCMNIST",
        "weight_file": "efficientnet_organc_disease.pth",
        "multi_label": False,
    },
    "organs": {
        "dataset_class": "OrganSMNIST",
        "task_name": "organsmnist",
        "dataset_id": "MedMNIST-OrganSMNIST",
        "weight_file": "efficientnet_organs_disease.pth",
        "multi_label": False,
    },
}

MODALITY_ALIASES: dict[str, str] = {
    "eye": "retina",
    "xray": "chest",
    "lungs": "pneumonia",
    "lung": "pneumonia",
    "organ-a": "organa",
    "organ-c": "organc",
    "organ-s": "organs",
}


def normalize_medmnist_modality(modality: str, default: str = "skin") -> str:
    m = (modality or "").strip().lower()
    if not m:
        return default
    m = MODALITY_ALIASES.get(m, m)
    if m in MEDMNIST_MODALITY_CONFIGS:
        return m
    return default
