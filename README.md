# MedAI

MedAI is a full-stack healthcare platform built with a React + Vite frontend and a FastAPI backend. It combines AI chat, user dashboards, health tracking, prescriptions, pharmacy ordering, lab test workflows, doctor/admin tools, and medical image diagnosis in one app.

This branch includes the MedMNIST diagnosis integration. The diagnosis pipeline now focuses on image-based inference with EfficientNet-B0 models trained on supported MedMNIST 2D subsets. Text-only chatbot input is handled by general chat, not diagnosis.

## What The App Does

MedAI is organized around three main ideas:

1. Help patients get quick health guidance through AI chat and image analysis.
2. Connect that guidance to practical next steps such as doctors, prescriptions, tests, reminders, and pharmacy ordering.
3. Give admins and doctors dedicated dashboards for operational workflows.

## Core Features

- AI-powered medical chat with optional RAG knowledge retrieval
- Medical image diagnosis using MedMNIST + EfficientNet-B0
- User registration, login, Google OAuth, and role-based access control
- Patient dashboard features for health tracking, consultations, reminders, prescriptions, and orders
- Doctor dashboard for patient management, consultations, appointments, and prescriptions
- Admin dashboard for platform management, analytics, roles, settings, and doctor onboarding
- Lab test browsing and tracking
- Pharmacy product browsing and order flow
- Document/image upload support for medical chat and extraction

## Diagnosis Flow

The diagnosis pipeline is image-first:

1. A medical image is uploaded.
2. The backend selects a MedMNIST modality, or auto-detects a suitable one when possible.
3. EfficientNet-B0 runs inference using the loaded modality-specific weight file.
4. The predicted disease is mapped to doctor guidance, treatment hints, suggested tests, and disease details.
5. The AI layer generates a concise explanation, optionally enriched with RAG medical references.

Supported MedMNIST modalities are configured in `backend/models/medmnist_labels.py`:

- `skin` for DermaMNIST
- `pathology` for PathMNIST
- `chest` for ChestMNIST
- `oct` for OCTMNIST
- `pneumonia` for PneumoniaMNIST
- `retina` for RetinaMNIST
- `blood` for BloodMNIST
- `tissue` for TissueMNIST
- `breast` for BreastMNIST
- `organa` for OrganAMNIST
- `organc` for OrganCMNIST
- `organs` for OrganSMNIST

Common aliases such as `xray`, `lung`, `lungs`, `eye`, `organ-a`, `organ-c`, and `organ-s` are normalized to a supported modality.

## Backend Architecture

The backend is a FastAPI application with these responsibilities:

- API routing for auth, chat, health, medicine, doctor, admin, lab tests, products, orders, prescriptions, consultations, and diagnosis
- MongoDB integration for persistent application data
- Redis integration for cache or runtime support
- JWT-based authentication and authorization middleware
- rate limiting and centralized error handling
- background reminder scheduling
- AI services for chat, OCR, image description, RAG, and diagnosis explanations

Key backend files:

- `backend/main.py` starts the app, registers middleware, mounts routers, and launches the reminder scheduler.
- `backend/services/medical_image_pipeline.py` turns image predictions into structured diagnosis output.
- `backend/services/image_diagnosis_service.py` loads the EfficientNet-B0 weights and performs image inference.
- `backend/services/ai_service.py` connects to Gemini, Hugging Face, OpenAI, or Ollama.
- `backend/routes/diagnose.py` exposes the medical image diagnosis API.

## Frontend Architecture

The frontend is a React application using Vite, React Router, Tailwind CSS, Framer Motion, and role-aware routing.

It includes:

- auth pages for login, registration, and OAuth success
- patient pages for chatbot, health tracking, reminders, pharmacy, lab tests, prescriptions, consultations, profile, help, and about
- admin pages for dashboard, users, roles, analytics, settings, and doctor creation
- doctor pages for dashboard, patients, consultations, appointments, prescriptions, profile, and settings

## Project Structure

```text
MedAI/
├── backend/
│   ├── config/
│   ├── middleware/
│   ├── medical_docs/
│   ├── models/
│   ├── routes/
│   ├── scripts/
│   └── services/
└── frontend/
	├── src/
	│   ├── components/
	│   ├── context/
	│   ├── pages/
	│   ├── services/
	│   └── styles/
	└── public/
```

## Tech Stack

Backend:

- FastAPI
- Uvicorn
- MongoDB with Motor / PyMongo
- Redis
- JWT auth
- Google OAuth
- OpenAI / Gemini / Hugging Face / Ollama integration
- FAISS / Chroma RAG support
- PyTorch, torchvision, timm, and MedMNIST

Frontend:

- React 18
- Vite
- React Router
- Tailwind CSS
- Framer Motion
- Lucide icons
- Recharts
- Google OAuth client

## Environment Variables

The backend reads settings from `backend/.env`. Common variables include:

```env
MONGODB_URI=
DB_NAME=medai
REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback

AI_PROVIDER=gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

HUGGINGFACE_API_KEY=
HUGGINGFACE_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1

OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

CHROMA_PERSIST_DIR=./chroma_db
FAISS_INDEX_PATH=./faiss_index
```

The frontend reads `frontend/.env` for values such as `VITE_GOOGLE_CLIENT_ID` and any API base URL you use in the browser app.

## Local Setup

### Backend

From the `backend` folder:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

On Windows, you can also use `py -m pip install -r requirements.txt` and `py main.py`.

### Frontend

From the `frontend` folder:

```bash
cd frontend
npm install
npm run dev
```

## Reproducible MedMNIST Pipeline

Use scripts as canonical training/evaluation entrypoints. The notebook is for visualization and iterative analysis.

### Train one modality

```bash
cd backend
python scripts/train_medmnist_efficientnet.py --modality skin --epochs 10 --batch-size 64 --seed 42
```

### Train all modalities

```bash
cd backend
python scripts/train_medmnist_efficientnet.py --all --epochs 10 --batch-size 64 --seed 42
```

### Evaluate checkpoints

```bash
cd backend
python scripts/evaluate_medmnist_efficientnet.py --modalities skin pathology oct pneumonia retina breast --seed 42
```

Outputs:
- `backend/models/weights/*.pth` (checkpoints)
- `backend/models/weights/train_<modality>.run_manifest.json`
- `backend/models/weights/medmnist_eval_results.json`
- `backend/models/weights/medmnist_eval_results.run_manifest.json`

## Important API Areas

- `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/google`
- `POST /api/chat` for general AI chat and document-assisted chat
- `POST /api/analysis/*` for general AI-based health analysis
- `POST /api/diagnose` for MedMNIST image diagnosis
- `GET /api/diagnose/model-info` for loaded model details
- `GET /api/health-check` for a simple service health response

## Operational Notes

- The backend starts a medicine reminder scheduler on startup.
- CORS is configured for local frontend ports such as `5173`, `3000`, and `3001`.
- The image diagnosis service loads modality-specific weight files from `backend/models/weights/`.
- If no model weights are available, diagnosis requests will not work until the appropriate `.pth` files are present.
- AI responses depend on the selected provider and its configured API key.
- `/api/health-check` reports dependency state for MongoDB and Redis.

## Quality Gates

Backend:

```bash
cd backend
pytest -q
```

Frontend:

```bash
cd frontend
npm run test
npm run build
```

CI:
- GitHub Actions workflow: `.github/workflows/ci.yml`
- Includes backend tests, frontend tests/build, and a basic secret-pattern guard.

## Containerized Run

```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Redis: `localhost:6379`

## Known Release Blockers

- Local credentials currently remain in `backend/.env` by explicit user instruction in this workspace.
- Before public release, rotate and remove all secrets from tracked history and switch to managed secret injection.

## Safety Note

MedAI provides AI-assisted guidance and preliminary assessment only. It does not replace a licensed healthcare professional, a formal diagnosis, or emergency care.

## License

This project is intended for educational and development use.
