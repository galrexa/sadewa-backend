from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.database import get_db
from app.models import ICD10
from app.schemas import ICD10Response

router = APIRouter()

@router.get("/icd10/search", response_model=List[ICD10Response])
async def search_icd10(
    q: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Search ICD-10 codes by query string"""
    
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    # Search in both English and Indonesian names, plus code
    results = db.query(ICD10).filter(
        or_(
            ICD10.code.contains(q.upper()),
            ICD10.name_en.contains(q),
            ICD10.name_id.contains(q)
        )
    ).limit(limit).all()
    
    return results

@router.get("/icd10/{code}", response_model=ICD10Response)
async def get_icd10_by_code(code: str, db: Session = Depends(get_db)):
    """Get specific ICD-10 by code"""
    
    result = db.query(ICD10).filter(ICD10.code == code.upper()).first()
    
    if not result:
        raise HTTPException(status_code=404, detail=f"ICD-10 code {code} not found")
    
    return result

@router.get("/icd10/categories/{category}")
async def get_icd10_by_category(category: str, db: Session = Depends(get_db)):
    """Get ICD-10 codes by category (first letter)"""
    
    results = db.query(ICD10).filter(
        ICD10.code.startswith(category.upper())
    ).limit(50).all()
    
    return {
        "category": category,
        "results": results,
        "count": len(results)
    }