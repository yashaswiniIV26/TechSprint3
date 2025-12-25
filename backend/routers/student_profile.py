from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional
import uuid
import io

try:
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

from agents.student_profile_agent import student_profile_agent
from services.firebase_service import firebase_service
from routers.auth import get_current_user

router = APIRouter()

# In-memory profile store (use database in production)
profiles_db = {}


@router.post("/create")
async def create_profile(
    name: str = Form(...),
    email: str = Form(...),
    skills: str = Form(""),  # Comma-separated
    communication_level: str = Form("medium"),
    preferred_roles: str = Form(""),
    coding_scores: str = Form("{}"),  # JSON string
    aptitude_scores: str = Form("{}"),
    academic_marks: str = Form("{}"),
    resume: Optional[UploadFile] = File(None)
):
    """Create a new student profile"""
    
    import json
    
    student_id = str(uuid.uuid4())
    
    # Parse skills
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    role_list = [r.strip() for r in preferred_roles.split(",") if r.strip()]
    
    # Parse JSON fields
    try:
        coding = json.loads(coding_scores) if coding_scores else {}
        aptitude = json.loads(aptitude_scores) if aptitude_scores else {}
        academic = json.loads(academic_marks) if academic_marks else {}
    except json.JSONDecodeError:
        coding, aptitude, academic = {}, {}, {}
    
    # Parse resume if provided
    resume_text = None
    if resume and HAS_PDF:
        try:
            content = await resume.read()
            pdf = pdfplumber.open(io.BytesIO(content))
            resume_text = ""
            for page in pdf.pages:
                resume_text += page.extract_text() or ""
            pdf.close()
        except Exception as e:
            print(f"Error parsing PDF: {e}")
    
    # Create profile using agent
    profile = await student_profile_agent.create_student_profile(
        student_id=student_id,
        name=name,
        email=email,
        resume_text=resume_text,
        selected_skills=skill_list,
        coding_scores=coding,
        aptitude_scores=aptitude,
        communication_level=communication_level,
        academic_marks=academic,
        preferred_roles=role_list
    )
    
    # Store profile
    profiles_db[student_id] = profile
    
    # Save to Firebase
    await firebase_service.create_student(student_id, profile)
    
    return {
        "message": "Profile created successfully",
        "student_id": student_id,
        "profile": profile
    }


@router.get("/{student_id}")
async def get_profile(student_id: str):
    """Get student profile by ID"""
    
    # Check local cache first
    profile = profiles_db.get(student_id)
    
    if not profile:
        # Try Firebase
        profile = await firebase_service.get_student(student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.put("/{student_id}")
async def update_profile(
    student_id: str,
    skills: Optional[str] = Form(None),
    communication_level: Optional[str] = Form(None),
    preferred_roles: Optional[str] = Form(None),
    coding_scores: Optional[str] = Form(None),
    aptitude_scores: Optional[str] = Form(None),
    academic_marks: Optional[str] = Form(None),
    github_username: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None)
):
    """Update student profile"""
    
    import json
    from datetime import datetime
    
    profile = profiles_db.get(student_id)
    
    if not profile:
        profile = await firebase_service.get_student(student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields
    if skills:
        new_skills = [s.strip() for s in skills.split(",") if s.strip()]
        profile["skills"] = list(set(profile.get("skills", []) + new_skills))
        categorized = student_profile_agent.categorize_skills(profile["skills"])
        profile["technical_skills"] = categorized["technical"]
        profile["soft_skills"] = categorized["soft"]
    
    if communication_level:
        profile["communication"] = communication_level
    
    if preferred_roles:
        profile["preferred_roles"] = [r.strip() for r in preferred_roles.split(",") if r.strip()]
    
    if coding_scores:
        try:
            profile["coding_scores"] = json.loads(coding_scores)
        except:
            pass
    
    if aptitude_scores:
        try:
            profile["aptitude_scores"] = json.loads(aptitude_scores)
        except:
            pass
    
    if academic_marks:
        try:
            profile["academic_marks"] = json.loads(academic_marks)
        except:
            pass
    
    if github_username:
        profile["github_username"] = github_username
    
    if linkedin_url:
        profile["linkedin_url"] = linkedin_url
    
    # Recalculate readiness score
    profile["readiness_score"] = student_profile_agent.calculate_readiness_score(profile)
    profile["updated_at"] = datetime.utcnow().isoformat()
    
    # Update stores
    profiles_db[student_id] = profile
    await firebase_service.update_student(student_id, profile)
    
    return {
        "message": "Profile updated successfully",
        "profile": profile
    }


@router.post("/{student_id}/upload-resume")
async def upload_resume(
    student_id: str,
    resume: UploadFile = File(...)
):
    """Upload and parse resume for existing profile"""
    
    if not HAS_PDF:
        raise HTTPException(
            status_code=500,
            detail="PDF parsing not available. Install pdfplumber."
        )
    
    profile = profiles_db.get(student_id)
    
    if not profile:
        profile = await firebase_service.get_student(student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Parse resume
    try:
        content = await resume.read()
        pdf = pdfplumber.open(io.BytesIO(content))
        resume_text = ""
        for page in pdf.pages:
            resume_text += page.extract_text() or ""
        pdf.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing PDF: {str(e)}")
    
    # Parse using agent
    parsed = await student_profile_agent.parse_resume(resume_text)
    
    # Merge with existing profile
    all_skills = set(profile.get("skills", []))
    all_skills.update(parsed.get("skills", []))
    profile["skills"] = list(all_skills)
    
    categorized = student_profile_agent.categorize_skills(profile["skills"])
    profile["technical_skills"] = categorized["technical"]
    profile["soft_skills"] = categorized["soft"]
    
    profile["experience"] = parsed.get("experience", [])
    profile["education"] = parsed.get("education", [])
    profile["projects"] = parsed.get("projects", [])
    profile["certifications"] = parsed.get("certifications", [])
    profile["resume_parsed"] = True
    
    # Recalculate score
    profile["readiness_score"] = student_profile_agent.calculate_readiness_score(profile)
    
    # Update stores
    profiles_db[student_id] = profile
    await firebase_service.update_student(student_id, profile)
    
    return {
        "message": "Resume parsed successfully",
        "parsed_data": parsed,
        "updated_profile": profile
    }


@router.get("/{student_id}/summary")
async def get_profile_summary(student_id: str):
    """Get human-readable profile summary"""
    
    profile = profiles_db.get(student_id)
    
    if not profile:
        profile = await firebase_service.get_student(student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    summary = student_profile_agent.get_profile_summary(profile)
    
    return {
        "student_id": student_id,
        "summary": summary,
        "readiness_score": profile.get("readiness_score", 0)
    }


@router.get("/{student_id}/readiness")
async def get_readiness_score(student_id: str):
    """Get detailed readiness score breakdown"""
    
    profile = profiles_db.get(student_id)
    
    if not profile:
        profile = await firebase_service.get_student(student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Calculate breakdown
    tech_skills = profile.get("technical_skills", [])
    soft_skills = profile.get("soft_skills", [])
    coding_scores = profile.get("coding_scores", {})
    aptitude_scores = profile.get("aptitude_scores", {})
    academic = profile.get("academic_marks", {})
    
    breakdown = {
        "technical_skills": {
            "score": min(len(tech_skills) * 5, 30),
            "max": 30,
            "count": len(tech_skills)
        },
        "soft_skills": {
            "score": min(len(soft_skills) * 3, 15),
            "max": 15,
            "count": len(soft_skills)
        },
        "coding": {
            "score": (sum(coding_scores.values()) / len(coding_scores) / 100 * 20) if coding_scores else 0,
            "max": 20,
            "tests_completed": len(coding_scores)
        },
        "aptitude": {
            "score": (sum(aptitude_scores.values()) / len(aptitude_scores) / 100 * 15) if aptitude_scores else 0,
            "max": 15,
            "tests_completed": len(aptitude_scores)
        },
        "communication": {
            "score": {"low": 3, "medium": 7, "high": 10}.get(profile.get("communication", "medium"), 5),
            "max": 10,
            "level": profile.get("communication", "medium")
        },
        "academics": {
            "score": (academic.get("cgpa", 0) / 10 * 10) if academic.get("cgpa") else 0,
            "max": 10,
            "cgpa": academic.get("cgpa", 0)
        }
    }
    
    total_score = sum(b["score"] for b in breakdown.values())
    
    return {
        "student_id": student_id,
        "readiness_score": round(total_score, 2),
        "max_score": 100,
        "breakdown": breakdown,
        "recommendations": _get_readiness_recommendations(breakdown)
    }


def _get_readiness_recommendations(breakdown: dict) -> List[str]:
    """Generate recommendations based on score breakdown"""
    
    recommendations = []
    
    if breakdown["technical_skills"]["score"] < 15:
        recommendations.append("Add more technical skills to your profile and get them validated through assessments")
    
    if breakdown["coding"]["tests_completed"] < 2:
        recommendations.append("Complete coding assessments to improve your readiness score")
    
    if breakdown["aptitude"]["tests_completed"] < 2:
        recommendations.append("Take aptitude tests to demonstrate your problem-solving abilities")
    
    if breakdown["communication"]["level"] == "low":
        recommendations.append("Practice communication skills through mock interviews")
    
    if not breakdown["academics"]["cgpa"]:
        recommendations.append("Add your academic marks to complete your profile")
    
    return recommendations
