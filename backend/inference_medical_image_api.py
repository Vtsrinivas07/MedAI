"""
Standalone FastAPI inference API for the medical image EfficientNet pipeline.

This is useful when you want model prediction + RAG + LLM explanation
without mounting the endpoint inside the main application.

Run:
    uvicorn backend.inference_medical_image_api:app --reload --port 8001
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from services.medical_image_pipeline import get_medical_image_pipeline

app = FastAPI(title="MedAI Medical Image Inference API", version="1.0.0")
pipeline = get_medical_image_pipeline()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "medical-image-inference"}


@app.post("/predict")
async def predict_medical_condition(
    image: UploadFile = File(..., description="Medical image file"),
    modality: str = Form("skin", description="skin, chest, eye, brain"),
    symptoms: Optional[str] = Form(None, description="Optional symptoms text"),
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file")

    image_data = await image.read()
    if not image_data:
        raise HTTPException(status_code=400, detail="Empty image file")

    result = await pipeline.analyze(image_data=image_data, modality=modality, symptoms=symptoms)
    return {"success": True, "data": result}
