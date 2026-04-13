# MedAI - AI-Powered Healthcare Platform

A full-stack healthcare platform combining AI-powered chat, digital prescriptions, medicine reminders, health tracking, lab test management, and pharmacy ordering.

![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react) ![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?logo=fastapi) ![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb)

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, React Router, Axios, Recharts, Lucide React |
| **Backend** | FastAPI, Python 3.11+, Pydantic, Motor (async MongoDB driver) |
| **Database** | MongoDB Atlas (or local MongoDB), Redis (rate limiting & caching) |
| **AI / LLM** | Gemini, OpenAI, HuggingFace, Ollama (configurable via `AI_PROVIDER`) |
| **RAG** | LangChain + FAISS + ChromaDB + Sentence Transformers (local embeddings) |
| **Auth** | JWT (python-jose), Google OAuth 2.0, OTP via SMS |
| **Notifications** | Twilio (SMS), SendGrid (email) |
| **Storage** | AWS S3 (optional — for file uploads) |

---

## Implemented Features

### Authentication
- Email/password login and registration
- Google OAuth 2.0 login
- Mobile OTP authentication (SMS via Twilio)
- JWT access + refresh token flow
- Role-based access control: `patient`, `doctor`, `admin`

### AI Chatbot
- Natural language symptom input
- File/image/PDF upload for medical document analysis
- Multi-provider LLM support (switch via `AI_PROVIDER` in `.env`)
- RAG-enhanced responses using local medical document corpus (FAISS + ChromaDB)
- Chat session history with resume support

### AI Analysis
- Symptom analysis via AI
- Medical image / description analysis
- Health trend analysis using logged vitals
- Treatment path suggestions (self-care / consultation / emergency)

### Health Tracking
- Daily vitals logging: blood pressure, blood sugar, heart rate, weight, temperature, oxygen, sleep, exercise, mood
- Historical trend charts
- Health analytics and risk scoring

### Medicine Reminders
- Create, update, delete reminders
- Bulk reminder creation from prescription (auto-maps frequency to morning/afternoon/evening/night)
- Scheduled notification delivery (email + SMS)
- Intake logging (taken / missed / skipped)
- Medicine scan endpoint (barcode / prescription image)

### Prescriptions
- Upload and AI-parse prescriptions (PDF, image, or text)
- Extract medicines, dosage, frequency, instructions
- Prescription history per patient
- One-click add all medicines as reminders

### Lab Tests
- Browse available tests with pricing
- Book tests
- Upload test reports
- View booking history

### Pharmacy & Orders
- Browse and search products
- Cart and checkout flow
- Order management with status tracking

### Doctor Portal
- Doctor dashboard with patient stats
- Patient list with consultation history
- Write and manage prescriptions
- Profile management (specialty, availability, fee, languages)

### Admin Portal
- Platform statistics dashboard
- User management (view, update roles)
- Create doctor accounts
- Analytics

### Consultations
- View past and upcoming consultations
- Create consultation records
- Update consultation status

### Nearby Doctors
- Search doctors by specialty, name, and city
- Filter by consultation type (message / voice / video / appointment)
- Book appointment or send message via modal

---

## Project Structure

```
MedAi/
├── backend/
│   ├── main.py                    # FastAPI app, middleware, router registration
│   ├── requirements.txt
│   ├── config/
│   │   ├── database.py            # MongoDB connection
│   │   ├── redis.py               # Redis client
│   │   └── settings.py            # Environment settings
│   ├── middleware/
│   │   ├── auth.py                # JWT verification
│   │   ├── error_handler.py       # Global error handler
│   │   └── rate_limiter.py        # Per-IP rate limiting
│   ├── models/                    # Pydantic request/response models
│   │   ├── user.py
│   │   ├── chat.py
│   │   ├── health.py
│   │   ├── medicine.py
│   │   ├── order.py
│   │   ├── prescription.py
│   │   ├── product.py
│   │   └── lab_test.py
│   ├── routes/
│   │   ├── auth.py                # /api/auth
│   │   ├── chat.py                # /api/chat
│   │   ├── health.py              # /api/health
│   │   ├── medicine.py            # /api/medicine
│   │   ├── prescription.py        # /api/prescriptions
│   │   ├── lab_test.py            # /api/lab-tests
│   │   ├── product.py             # /api/products
│   │   ├── order.py               # /api/orders
│   │   ├── doctor.py              # /api/doctor
│   │   ├── admin.py               # /api/admin
│   │   ├── analysis.py            # /api/analysis
│   │   └── consultations.py       # /api/consultations
│   ├── services/
│   │   ├── ai_service.py          # Multi-provider LLM client
│   │   ├── rag_service.py         # LangChain + FAISS + ChromaDB RAG
│   │   ├── health_analytics.py    # Trend analysis, risk scoring
│   │   ├── notification_service.py # Twilio SMS + SendGrid email
│   │   ├── reminder_scheduler.py  # Background medicine reminder scheduler
│   │   ├── cache_service.py       # Redis cache helpers
│   │   └── s3_service.py          # AWS S3 uploads
│   └── medical_docs/              # RAG knowledge base text files
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── services/api.js         # Axios client + all API helpers
        ├── context/
        │   ├── AuthContext.jsx
        │   └── ThemeContext.jsx
        ├── components/
        │   ├── ChatLayout.jsx
        │   ├── DashboardLayout.jsx
        │   ├── MainLayout.jsx
        │   ├── Navigation.jsx
        │   ├── Sidebar.jsx
        │   └── RecommendationsPanel.jsx
        └── pages/
            ├── Login.jsx / Register.jsx
            ├── Chatbot.jsx
            ├── HealthTracking.jsx
            ├── MedicineReminder.jsx / ScanMedicines.jsx
            ├── PatientPrescriptions.jsx
            ├── LabTests.jsx / MyLabTests.jsx
            ├── Pharmacy.jsx / Orders.jsx
            ├── Consultations.jsx / NearbyDoctors.jsx
            ├── Profile.jsx
            ├── DoctorDashboard.jsx / DoctorProfile.jsx
            ├── DoctorAppointments.jsx / DoctorConsultations.jsx
            ├── DoctorPrescriptions.jsx / PatientList.jsx
            ├── AdminDashboard.jsx / AdminAnalytics.jsx
            ├── UserManagement.jsx / CreateDoctor.jsx
            └── About.jsx / Help.jsx
```

---

## API Endpoints

### Auth — `/api/auth`
| Method | Path | Description |
|---|---|---|
| POST | `/register` | Register with email/password |
| POST | `/login` | Login with email/password |
| POST | `/google` | Login with Google OAuth |
| POST | `/request-otp` | Send OTP to mobile number |
| POST | `/verify-otp` | Verify OTP, return tokens |
| GET | `/me` | Get current user |
| POST | `/logout` | Logout |
| PUT | `/profile` | Update profile |

### Chat — `/api/chat`
| Method | Path | Description |
|---|---|---|
| POST | `/` | Send message to AI chatbot |
| GET | `/sessions` | Get all chat sessions |
| GET | `/sessions/{id}` | Get specific session |
| DELETE | `/sessions/{id}` | Delete session |

### AI Analysis — `/api/analysis`
| Method | Path | Description |
|---|---|---|
| POST | `/symptoms` | Analyze symptoms |
| POST | `/image` | Analyze medical image or description |
| GET | `/health-trends` | Health trend analysis from logs |

### Health — `/api/health`
| Method | Path | Description |
|---|---|---|
| POST | `/logs` | Create health log |
| GET | `/logs` | Get health logs |
| PUT | `/logs/{id}` | Update health log |
| DELETE | `/logs/{id}` | Delete health log |
| GET | `/analytics` | Get health analytics |

### Medicine — `/api/medicine`
| Method | Path | Description |
|---|---|---|
| POST | `/reminders` | Create reminder |
| GET | `/reminders` | Get all reminders |
| PUT | `/reminders/{id}` | Update reminder |
| DELETE | `/reminders/{id}` | Delete reminder |
| POST | `/bulk-reminders` | Create reminders from prescription |
| POST | `/log` | Log medicine intake |
| POST | `/scan` | Scan medicine barcode or prescription image |

### Prescriptions — `/api/prescriptions`
| Method | Path | Description |
|---|---|---|
| POST | `/` | Create prescription |
| GET | `/` | Get prescriptions |
| GET | `/{id}` | Get specific prescription |
| DELETE | `/{id}` | Delete prescription |
| POST | `/parse` | AI-parse prescription (PDF/image/text) |

### Lab Tests — `/api/lab-tests`
| Method | Path | Description |
|---|---|---|
| GET | `/` | Get available tests |
| POST | `/book` | Book a test |
| GET | `/bookings` | Get user bookings |
| POST | `/bookings/{id}/upload-report` | Upload test report |

### Products — `/api/products`
| Method | Path | Description |
|---|---|---|
| GET | `/` | List products |
| GET | `/search` | Search products |

### Orders — `/api/orders`
| Method | Path | Description |
|---|---|---|
| POST | `/` | Create order |
| GET | `/` | Get orders |
| PUT | `/{id}/status` | Update order status |

### Doctor — `/api/doctor`
| Method | Path | Description |
|---|---|---|
| GET | `/dashboard` | Doctor dashboard stats |
| GET | `/patients` | Patient list |
| GET | `/patients/{id}` | Patient details |
| GET | `/search` | Search doctors by specialty/name/city |
| PUT | `/profile` | Update doctor profile |

### Admin — `/api/admin`
| Method | Path | Description |
|---|---|---|
| GET | `/stats` | Platform statistics |
| GET | `/users` | List all users |
| PUT | `/users/{id}/role` | Update user role |
| POST | `/create-doctor` | Create doctor account |

### Consultations — `/api/consultations`
| Method | Path | Description |
|---|---|---|
| GET | `/` | Get user consultations |
| POST | `/` | Create consultation |
| GET | `/{id}` | Get specific consultation |
| PUT | `/{id}` | Update consultation |

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas (or local MongoDB)
- Redis (local or cloud)

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

Create `backend/.env`:
```env
# Required
MONGODB_URI=mongodb+srv://...
JWT_SECRET_KEY=your-secret-key-min-32-chars
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# AI Provider (choose one)
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
# HUGGINGFACE_API_KEY=
# OPENAI_API_KEY=

# Optional services
REDIS_URL=redis://localhost:6379/0
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=

DEBUG=True
```

```bash
python main.py
```

API runs at `http://localhost:8000` — Swagger docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

```bash
npm run dev
```

App runs at `http://localhost:5173`

---

## AI Provider Options

Set `AI_PROVIDER` in `backend/.env`:

| Value | Env Key | Notes |
|---|---|---|
| `gemini` | `GEMINI_API_KEY` | Google Gemini — free tier, recommended |
| `huggingface` | `HUGGINGFACE_API_KEY` | HuggingFace Inference API — free |
| `openai` | `OPENAI_API_KEY` | OpenAI GPT — paid |
| `ollama` | _(none)_ | Local — install Ollama separately |

---

## Deployment

### Vercel + Render (Recommended)

**Frontend → Vercel:**
1. Push to GitHub and connect the repo to Vercel
2. Set environment variables: `VITE_API_URL`, `VITE_GOOGLE_CLIENT_ID`

**Backend → Render:**
1. Connect GitHub repository
2. Runtime: Python
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add all `.env` variables in the Render dashboard

### Other Options
- **AWS**: Elastic Beanstalk or App Runner
- **Google Cloud**: Cloud Run
- **Azure**: App Service
