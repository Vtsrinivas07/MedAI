from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import os
import re
import json

from models.chat import ChatRequest, ChatResponse, ChatSession, Message
from middleware.auth import get_current_user
from config.database import get_database
from services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

DEFAULT_MODULE_ROUTES = {
    "doctor_appointment": "/consultations",
    "doctor_portal": "/doctor/dashboard",
    "lab_tests": "/lab-tests",
    "pharmacy": "/pharmacy",
    "medicine_reminders": "/medicines",
    "health_tracking": "/health-tracking",
}

EMERGENCY_PATTERNS = re.compile(
    r"\b(chest pain|pressure in chest|shortness of breath|difficulty breathing|severe headache|"
    r"weakness|numbness|speech difficulty|loss of consciousness|seizure|overdose|poisoning|anaphylaxis|"
    r"severe bleeding|stroke|heart attack)\b",
    re.I,
)

DOCTOR_ROLE_RULES = [
    (re.compile(r"\b(skin|rash|acne|eczema|psoriasis|lesion|mole|itching)\b", re.I), "Dermatologist", "High"),
    (re.compile(r"\b(chest|cough|breath|lungs|xray|pneumonia|asthma|wheezing)\b", re.I), "Pulmonologist", "High"),
    (re.compile(r"\b(heart|bp|blood pressure|palpitation|cardiac|hypertension)\b", re.I), "Cardiologist", "High"),
    (re.compile(r"\b(eye|vision|retina|blurred|vision loss|red eye)\b", re.I), "Ophthalmologist", "Medium"),
    (re.compile(r"\b(brain|headache|stroke|seizure|neuro|migraine|dizziness)\b", re.I), "Neurologist", "High"),
    (re.compile(r"\b(blood|anemia|hemoglobin|hematology|platelet|bruise)\b", re.I), "Hematologist", "Medium"),
    (re.compile(r"\b(pathology|biopsy|tumor|cancer|oncology|mass|growth)\b", re.I), "Oncologist", "High"),
    (re.compile(r"\b(kidney|renal|creatinine|urine|uti|bladder)\b", re.I), "Nephrologist", "Medium"),
    (re.compile(r"\b(diabetes|sugar|glucose|thyroid|hormone|weight loss|weight gain)\b", re.I), "Endocrinologist", "Medium"),
    (re.compile(r"\b(stomach|abdomen|nausea|vomit|diarrhea|constipation|acidity|reflux|gastritis)\b", re.I), "Gastroenterologist", "Medium"),
    (re.compile(r"\b(joint|bone|fracture|sprain|back pain|knee|shoulder|arthritis|spine)\b", re.I), "Orthopedic Surgeon", "Medium"),
    (re.compile(r"\b(ear|nose|throat|sinus|hearing|sore throat|tonsil)\b", re.I), "ENT Specialist", "Medium"),
    (re.compile(r"\b(mood|anxiety|depression|panic|stress|sleep|insomnia)\b", re.I), "Psychiatrist / Clinical Psychologist", "Medium"),
    (re.compile(r"\b(pregnancy|pregnant|period|menstrual|vaginal|pcos|fertility)\b", re.I), "Gynecologist / Obstetrician", "Medium"),
    (re.compile(r"\b(prostate|urinary|bladder|erection|erectile|penis|testicle)\b", re.I), "Urologist", "Medium"),
    (re.compile(r"\b(allergy|sneezing|hives|asthma|immuno|seasonal)\b", re.I), "Allergist / Immunologist", "Medium"),
    (re.compile(r"\b(fever|infection|antibiotic|contagious|sepsis|flu|covid)\b", re.I), "Infectious Disease Specialist", "Medium"),
]


def _suggest_doctors_from_text(text: str) -> list[dict]:
    text = text or ""
    lowered = text.lower()
    suggestions = []
    seen = set()

    if EMERGENCY_PATTERNS.search(lowered):
        suggestions.append(
            {
                "role": "Emergency Medicine / ER",
                "urgency": "High",
                "reason": "Urgent symptoms were detected. Seek immediate in-person evaluation.",
            }
        )
        seen.add("Emergency Medicine / ER")

    for pattern, role, urgency in DOCTOR_ROLE_RULES:
        if pattern.search(lowered) and role not in seen:
            matched_terms = sorted({match.group(0) for match in pattern.finditer(lowered)})
            reason = f"Matched terms: {', '.join(matched_terms[:3])}." if matched_terms else f"Matched context for {role.lower()} evaluation."
            suggestions.append(
                {
                    "role": role,
                    "urgency": urgency,
                    "reason": reason,
                }
            )
            seen.add(role)

    if not suggestions:
        suggestions.append(
            {
                "role": "General Physician",
                "urgency": "Medium",
                "reason": "Start with general triage and referral as needed.",
            }
        )
    return suggestions[:3]


def _build_care_bundle(user_text: str, ai_text: str, sources: Optional[list[dict]] = None) -> dict:
    combined = f"{user_text or ''}\n{ai_text or ''}"
    doctor_suggestions = _suggest_doctors_from_text(combined)
    return {
        "model_stack": {
            "image_model": "EfficientNet-B0 (MedMNIST) for medical image diagnosis when image is used",
            "llm": "Gemini (configured provider)",
            "rag": "ChromaDB/FAISS retrieval when enabled",
        },
        "doctor_suggestions": doctor_suggestions,
        "module_routes": DEFAULT_MODULE_ROUTES,
        "module_actions": [
            {
                "key": "doctor_appointment",
                "label": "Doctor Appointment",
                "description": "Book a specialist visit from the chatbot recommendation.",
            },
            {
                "key": "lab_tests",
                "label": "Lab Tests",
                "description": "Open suggested lab work or imaging checks.",
            },
            {
                "key": "pharmacy",
                "label": "Pharmacy Medicines",
                "description": "Review medicines with clinician approval.",
            },
            {
                "key": "medicine_reminders",
                "label": "Medicine Reminders",
                "description": "Set treatment reminders and adherence tracking.",
            },
            {
                "key": "health_tracking",
                "label": "Health Tracking",
                "description": "Send the care plan into health tracking for follow-up.",
            },
        ],
        "next_actions": [
            "Book doctor appointment from chatbot recommendations",
            "Order suggested lab tests and upload reports",
            "Review pharmacy medicine options with clinician advice",
            "Set medicine reminders for treatment adherence",
            "Log symptoms/vitals in health tracking for longitudinal follow-up",
        ],
        "summary": "Chatbot-generated care plan with specialist suggestions, follow-up modules, and tracking handoff.",
        "sources_count": len(sources or []),
    }


async def _build_care_bundle_async(user_text: str, ai_text: str, sources: Optional[list[dict]] = None) -> dict:
    bundle = _build_care_bundle(user_text, ai_text, sources)
    combined = f"{user_text or ''}\n{ai_text or ''}".strip()
    if not combined:
        return bundle

    prompt = (
        "Extract best-fit medical specialist roles from the following patient context. "
        "Return strict JSON only in this format: "
        "{\"doctor_suggestions\":[{\"role\":\"...\",\"urgency\":\"Low|Medium|High\",\"reason\":\"...\"}]}.\n"
        "Rules: max 3 roles, concise reason, no markdown, no extra keys.\n\n"
        f"Patient context:\n{combined[:1800]}"
    )
    try:
        raw = await ai_service.get_simple_response(
            message=prompt,
            conversation_history=[],
            max_tokens=220,
            system_prompt=(
                "You are a medical triage assistant. Return valid compact JSON only. "
                "Do not include explanatory prose outside JSON."
            ),
        )
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            parsed = json.loads(raw[start : end + 1])
            suggestions = parsed.get("doctor_suggestions")
            if isinstance(suggestions, list) and suggestions:
                normalized = []
                for item in suggestions[:3]:
                    if not isinstance(item, dict):
                        continue
                    role = str(item.get("role") or "").strip()
                    urgency = str(item.get("urgency") or "Medium").strip().title()
                    reason = str(item.get("reason") or "").strip() or "Context-based specialist recommendation."
                    if role:
                        if urgency not in ("Low", "Medium", "High"):
                            urgency = "Medium"
                        normalized.append({"role": role, "urgency": urgency, "reason": reason})
                if normalized:
                    bundle["doctor_suggestions"] = normalized
    except Exception:
        pass
    return bundle

@router.post("/", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a message and get AI response"""
    db = get_database()
    user_id = str(current_user["_id"])
    
    if chat_request.session_id:
        session = await db.chat_sessions.find_one({
            "_id": ObjectId(chat_request.session_id),
            "user_id": user_id
        })
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
    else:
        session = {
            "user_id": user_id,
            "title": chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.chat_sessions.insert_one(session)
        session["_id"] = result.inserted_id
    
    user_message = {
        "role": "user",
        "content": chat_request.message,
        "timestamp": datetime.utcnow()
    }
    
    sources = None
    try:
        if chat_request.use_rag:
            ai_response, sources = await ai_service.get_rag_response(
                chat_request.message,
                session.get("messages", [])
            )
        else:
            ai_response = await ai_service.get_simple_response(
                chat_request.message,
                session.get("messages", [])
            )
            sources = None
    except Exception as e:
        error_msg = str(e).lower()
        
        if "rate limit" in error_msg or "429" in error_msg or "quota" in error_msg:
            ai_response = """⚠️ **Rate Limit Exceeded**

The AI service is currently experiencing high demand. Here are your options:

• **Wait a Few Minutes** - Try again in 3-5 minutes when the rate limit resets
• **Basic Medical Info** - I can still provide general health information and suggestions
• **Contact Support** - If you need urgent assistance, please contact our support team

**What you asked:** """ + chat_request.message[:100]
        
        elif "api" in error_msg and "key" in error_msg:
            ai_response = """⚠️ **API Configuration Error**

The health assistant is temporarily unavailable due to a configuration issue. Our team has been notified and is working on a fix.

Please try again in a few moments."""
        
        elif "connection" in error_msg or "timeout" in error_msg:
            ai_response = """⚠️ **Connection Error**

Unable to connect to the health assistant service. This is usually temporary.

**Try:**
• Refresh the page and try again
• Wait a few seconds and submit your question again
• Contact support if the issue persists"""
        
        else:
            ai_response = f"""⚠️ **Service Temporarily Unavailable**

We encountered an issue: {str(e)[:100]}

Please try again in a moment, or contact our support team for assistance."""
    
    assistant_message = {
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.utcnow()
    }
    
    await db.chat_sessions.update_one(
        {"_id": session["_id"]},
        {
            "$push": {
                "messages": {
                    "$each": [user_message, assistant_message]
                }
            },
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return ChatResponse(
        message=ai_response,
        session_id=str(session["_id"]),
        sources=sources,
        care_bundle=await _build_care_bundle_async(chat_request.message, ai_response, sources),
    )

@router.get("/sessions", response_model=List[ChatSession])
async def get_sessions(current_user: dict = Depends(get_current_user)):
    """Get all chat sessions for current user"""
    db = get_database()
    user_id = str(current_user["_id"])
    
    sessions = await db.chat_sessions.find(
        {"user_id": user_id}
    ).sort("updated_at", -1).to_list(100)
    
    for session in sessions:
        session["_id"] = str(session["_id"])
    
    return sessions

@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific chat session"""
    db = get_database()
    user_id = str(current_user["_id"])
    
    session = await db.chat_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    session["_id"] = str(session["_id"])
    return session

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a chat session"""
    db = get_database()
    user_id = str(current_user["_id"])
    
    result = await db.chat_sessions.delete_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return {"message": "Session deleted successfully"}

@router.post("/upload", response_model=ChatResponse)
async def upload_file(
    file: UploadFile = File(...),
    message: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    use_rag: bool = Form(True),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document or image; extract text (PDF/DOCX/TXT or Gemini vision) and answer with AI."""
    db = get_database()
    user_id = str(current_user["_id"])

    file_content = await file.read()
    file_size = len(file_content)

    if file_size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit"
        )

    if session_id:
        session = await db.chat_sessions.find_one({
            "_id": ObjectId(session_id),
            "user_id": user_id
        })
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
    else:
        session = {
            "user_id": user_id,
            "title": f"File: {file.filename}",
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.chat_sessions.insert_one(session)
        session["_id"] = result.inserted_id

    ctype = (file.content_type or "").lower()
    extracted = ""
    extract_note = ""

    if ctype.startswith("image/"):
        extracted = await ai_service.extract_text_from_image(file_content, ctype or "image/jpeg")
        if extracted.startswith("[Image text extraction failed"):
            extract_note = extracted
            extracted = ""
        elif not (extracted or "").strip():
            extract_note = (
                "Photo OCR needs Google Gemini. Set **AI_PROVIDER=gemini** and **GEMINI_API_KEY** in `backend/.env`, "
                "or upload a **PDF / DOCX** export of the document instead."
            )
    else:
        from services.document_extract import extract_document_text
        extracted, extract_note = extract_document_text(file.filename, file.content_type, file_content)

    preview = (extracted or "")[:1200]
    user_content = message or f"I've uploaded **{file.filename}** ({file_size / 1024:.1f} KB)."
    user_message = {
        "role": "user",
        "content": user_content,
        "file": {
            "name": file.filename,
            "type": file.content_type,
            "size": file_size
        },
        "extracted_preview": preview or None,
        "timestamp": datetime.utcnow()
    }

    sources = None
    if not (extracted or "").strip():
        if extract_note:
            ai_response = (
                f"I received **{file.filename}**, but could not read usable text from it.\n\n"
                f"{extract_note}\n\n"
                "Try PDF or DOCX (not scanned-only PDF without OCR), or configure Gemini for photo uploads."
            )
        else:
            ai_response = (
                f"I received **{file.filename}**, but no text could be extracted. "
                "Try a text-based PDF, DOCX, TXT, or a clearer photo with **GEMINI_API_KEY** set for OCR."
            )
    else:
        combined = (
            f"The user uploaded a file named `{file.filename}`.\n\n"
            f"--- Extracted content ---\n{extracted.strip()}\n--- End extract ---\n\n"
            f"User note / question: {message or 'Please summarize this document, highlight abnormal values if any, and suggest sensible next steps (not a formal diagnosis).'}"
        )
        doc_system = (
            "You are MedAI, a medical assistant. The user shared extracted text from a file (PDF, Word, or image OCR). "
            "Summarize clearly with short headings and bullets when helpful. Note noteworthy values or concerns in neutral language. "
            "Complete every sentence—do not stop mid-phrase. Mention red-flag symptoms or when to seek urgent care. "
            "Do not give a definitive diagnosis or prescribe medications."
        )
        try:
            if use_rag:
                ai_response, sources = await ai_service.get_rag_response(
                    combined,
                    session.get("messages", []),
                    max_output_tokens=2048,
                )
            else:
                ai_response = await ai_service.get_simple_response(
                    combined,
                    session.get("messages", []),
                    max_tokens=2048,
                    system_prompt=doc_system,
                )
        except Exception as e:
            sources = None
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg or "quota" in error_msg:
                ai_response = (
                    "⚠️ **Rate limit** while analyzing your file. Please wait a few minutes and try again.\n\n"
                    f"**Extract preview (first ~400 chars):** {extracted[:400]}…"
                )
            else:
                ai_response = (
                    f"⚠️ I extracted text from your file but the AI step failed: {str(e)[:200]}\n\n"
                    f"**Preview:** {extracted[:600]}…"
                )

    assistant_message = {
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.utcnow()
    }

    await db.chat_sessions.update_one(
        {"_id": session["_id"]},
        {
            "$push": {
                "messages": {
                    "$each": [user_message, assistant_message]
                }
            },
            "$set": {"updated_at": datetime.utcnow()}
        }
    )

    return ChatResponse(
        message=ai_response,
        session_id=str(session["_id"]),
        sources=sources,
        success=True,
        extracted_preview=preview[:500] if preview else None,
        care_bundle=await _build_care_bundle_async((message or extracted or file.filename), ai_response, sources),
    )
    
@router.post("/generate-recommendations")
async def generate_recommendations(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate structured health recommendations from user's message"""
    db = get_database()
    user_id = str(current_user["_id"])
    
    user_profile = await db.users.find_one({"_id": current_user["_id"]})
    health_profile = user_profile.get("health_profile", {}) if user_profile else {}
    
    recommendations = await ai_service.generate_health_recommendations(
        chat_request.message,
        health_profile
    )
    
    recommendation_doc = {
        "user_id": user_id,
        "trigger_message": chat_request.message,
        "recommendations": recommendations,
        "created_at": datetime.utcnow(),
        "applied": False  # Track if user has applied these recommendations
    }
    
    result = await db.recommendations.insert_one(recommendation_doc)
    recommendation_doc["_id"] = str(result.inserted_id)
    
    return {
        "recommendation_id": str(result.inserted_id),
        "recommendations": recommendations,
        "message": "Recommendations generated successfully"
    }

@router.get("/recommendations/latest")
async def get_latest_recommendations(current_user: dict = Depends(get_current_user)):
    """Get user's latest recommendations"""
    db = get_database()
    user_id = str(current_user["_id"])
    
    recommendation = await db.recommendations.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )
    
    if not recommendation:
        return {"recommendations": None, "message": "No recommendations found"}
    
    recommendation["_id"] = str(recommendation["_id"])
    return {"recommendations": recommendation}

@router.post("/recommendations/{recommendation_id}/apply")
async def apply_recommendations(
    recommendation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Apply recommendations to user's medicine reminders and meal plan"""
    db = get_database()
    user_id = str(current_user["_id"])
    
    recommendation = await db.recommendations.find_one({
        "_id": ObjectId(recommendation_id),
        "user_id": user_id
    })
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    recommendations_data = recommendation["recommendations"]
    
    for med in recommendations_data.get("medications", []):
        reminder_dict = {
            "user_id": user_id,
            "medicine_name": med["name"],
            "dosage": med["dosage"],
            "frequency": med["frequency"],
            "times": ["08:00", "14:00", "20:00"],  # Default times
            "start_date": datetime.utcnow(),
            "end_date": None,
            "notes": med.get("notes", ""),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "from_ai": True
        }
        await db.medicine_reminders.insert_one(reminder_dict)
    
    meal_plan_dict = {
        "user_id": user_id,
        "date": datetime.utcnow().date().isoformat(),
        "meals": recommendations_data.get("meal_plan", {}),
        "created_at": datetime.utcnow(),
        "from_ai": True
    }
    await db.meal_plans.insert_one(meal_plan_dict)
    
    await db.recommendations.update_one(
        {"_id": ObjectId(recommendation_id)},
        {"$set": {"applied": True, "applied_at": datetime.utcnow()}}
    )
    
    return {
        "message": "Recommendations applied successfully",
        "medications_added": len(recommendations_data.get("medications", [])),
        "meal_plan_saved": True
    }

