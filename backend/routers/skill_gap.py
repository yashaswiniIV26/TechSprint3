from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from agents.skill_gap_analyzer_agent import skill_gap_analyzer_agent
from routers.student_profile import profiles_db
from services.firebase_service import firebase_service

router = APIRouter()


class AnalyzeGapRequest(BaseModel):
    student_id: str
    company_id: Optional[str] = None
    custom_requirements: Optional[dict] = None


class BatchAnalyzeRequest(BaseModel):
    student_id: str
    company_ids: Optional[List[str]] = None


@router.post("/analyze")
async def analyze_skill_gap(request: AnalyzeGapRequest):
    """Analyze skill gap for a student against a company"""
    
    # Get student profile
    profile = profiles_db.get(request.student_id)
    
    if not profile:
        profile = await firebase_service.get_student(request.student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Perform analysis
    analysis = await skill_gap_analyzer_agent.analyze_gap(
        student_id=request.student_id,
        student_profile=profile,
        company_id=request.company_id,
        custom_requirements=request.custom_requirements
    )
    
    return analysis


@router.post("/analyze-batch")
async def batch_analyze_skill_gap(request: BatchAnalyzeRequest):
    """Analyze skill gap against multiple companies"""
    
    # Get student profile
    profile = profiles_db.get(request.student_id)
    
    if not profile:
        profile = await firebase_service.get_student(request.student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Perform batch analysis
    analyses = await skill_gap_analyzer_agent.batch_analyze(
        student_id=request.student_id,
        student_profile=profile,
        company_ids=request.company_ids
    )
    
    # Find best match
    best_match = analyses[0] if analyses else None
    
    return {
        "student_id": request.student_id,
        "total_companies_analyzed": len(analyses),
        "best_match": {
            "company": best_match["company_name"] if best_match else None,
            "role": best_match["target_role"] if best_match else None,
            "match_percentage": best_match["skill_match_percentage"] if best_match else 0
        },
        "analyses": analyses
    }


@router.get("/companies")
async def get_available_companies():
    """Get list of companies available for analysis"""
    
    companies = skill_gap_analyzer_agent.get_available_companies()
    
    return {
        "total_companies": len(companies),
        "companies": companies
    }


@router.get("/company/{company_id}")
async def get_company_requirements(company_id: str):
    """Get detailed requirements for a specific company"""
    
    if company_id not in skill_gap_analyzer_agent.COMPANY_REQUIREMENTS:
        raise HTTPException(status_code=404, detail="Company not found")
    
    requirements = skill_gap_analyzer_agent.COMPANY_REQUIREMENTS[company_id]
    
    return {
        "company_id": company_id,
        **requirements
    }


@router.post("/custom-company")
async def add_custom_company(
    company_id: str,
    company_name: str,
    role: str,
    required_skills: List[str],
    preferred_skills: List[str] = [],
    minimum_cgpa: float = None
):
    """Add a custom company for analysis (temporary)"""
    
    custom_req = {
        "company_name": company_name,
        "role": role,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "minimum_cgpa": minimum_cgpa
    }
    
    # Add to agent's database temporarily
    skill_gap_analyzer_agent.COMPANY_REQUIREMENTS[company_id] = custom_req
    
    return {
        "message": "Custom company added successfully",
        "company_id": company_id,
        "requirements": custom_req
    }


@router.get("/skill-ontology/{skill}")
async def get_related_skills(skill: str):
    """Get skills related to a given skill"""
    
    related = skill_gap_analyzer_agent.get_related_skills(skill)
    
    return {
        "skill": skill,
        "related_skills": related,
        "total_related": len(related)
    }


@router.post("/compare-skills")
async def compare_two_skills(skill1: str, skill2: str):
    """Compare similarity between two skills"""
    
    similarity = skill_gap_analyzer_agent.calculate_skill_similarity(skill1, skill2)
    
    return {
        "skill1": skill1,
        "skill2": skill2,
        "similarity_score": round(similarity, 2),
        "relationship": "same" if similarity == 1.0 else
                       "strongly related" if similarity >= 0.7 else
                       "related" if similarity >= 0.3 else
                       "unrelated"
    }
