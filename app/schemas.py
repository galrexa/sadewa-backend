from pydantic import BaseModel
from typing import List, Optional

# ICD-10 Schemas
class ICD10Base(BaseModel):
    code: str
    name_en: str
    name_id: str

class ICD10Response(ICD10Base):
    class Config:
        from_attributes = True

# Patient Schemas
class PatientBase(BaseModel):
    id: str
    name: str
    age: int
    gender: str

class PatientResponse(PatientBase):
    diagnoses: List[str]
    current_medications: List[str]
    allergies: List[str]

# Interaction Analysis Schemas
class InteractionRequest(BaseModel):
    patient_id: str
    new_medications: List[str]
    notes: Optional[str] = ""

class InteractionWarning(BaseModel):
    type: str  # "drug-drug", "drug-disease"
    severity: str  # "Major", "Moderate", "Minor"
    description: str
    medications_involved: List[str]

class InteractionResponse(BaseModel):
    patient_id: str
    warnings: List[InteractionWarning]
    safe_to_prescribe: bool
    llm_reasoning: str