# MedMNIST model weights

This directory intentionally does not include trained `.pth` files.

The diagnosis API loads one EfficientNet-B0 weight file per MedMNIST modality. The
expected filenames are configured in `backend/models/medmnist_labels.py`, for
example:

- `efficientnet_skin_disease.pth`
- `efficientnet_chest_disease.pth`
- `efficientnet_retina_disease.pth`

Train weights from the backend directory:

```bash
python scripts/train_medmnist_efficientnet.py --all
```

Or train a single modality:

```bash
python scripts/train_medmnist_efficientnet.py --modality skin
```

Without these `.pth` files, `/api/diagnose` returns `503 Service Unavailable`
with a setup message instead of producing a misleading fake diagnosis.
