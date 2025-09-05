from fastapi import APIRouter, HTTPException
from typing import List
import json
import os
from app.schemas import InteractionRequest, InteractionResponse
from services.groq_service import groq_service

router = APIRouter()

def load_drug_interactions():
    """Load drug interactions database"""
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "drug_interactions.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_patients():
    """Load patients database"""
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "patients.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@router.post("/analyze-interactions", response_model=InteractionResponse)
async def analyze_interactions(request: InteractionRequest):
    """Analyze drug interactions using Groq AI"""
    
    # Find patient data
    patients = load_patients()
    patient_data = None
    
    for patient in patients:
        if patient["id"] == request.patient_id:
            patient_data = patient
            break
    
    if not patient_data:
        raise HTTPException(status_code=404, detail=f"Patient {request.patient_id} not found")
    
    # Load drug interactions database
    drug_interactions_db = load_drug_interactions()
    
    # Call Groq service for analysis
    try:
        analysis_result = await groq_service.analyze_drug_interactions(
            patient_data=patient_data,
            new_medications=request.new_medications,
            drug_interactions_db=drug_interactions_db,
            notes=request.notes
        )
        
        # Transform to response format
        response = InteractionResponse(
            patient_id=request.patient_id,
            warnings=analysis_result.get("warnings", []),
            safe_to_prescribe=analysis_result.get("safe_to_prescribe", False),
            llm_reasoning=analysis_result.get("reasoning", "")
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/test-groq")
async def test_groq_connection():
    """Test Groq API connection"""
    result = await groq_service.test_connection()
    return {"status": "success", "response": result}