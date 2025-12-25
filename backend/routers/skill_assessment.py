from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from agents.skill_assessment_agent import skill_assessment_agent
from agents.digital_twin_agent import digital_twin_agent
from services.firebase_service import firebase_service
from models.schemas import SkillCategory

router = APIRouter()

# In-memory assessment store
assessments_db = {}


class StartAssessmentRequest(BaseModel):
    student_id: str
    category: SkillCategory
    skills: List[str]
    questions_per_skill: int = 5


class SubmitAnswerRequest(BaseModel):
    question_id: str
    answer: str
    time_taken_seconds: int


@router.post("/start")
async def start_assessment(request: StartAssessmentRequest):
    """Start a new adaptive assessment"""
    
    assessment = await skill_assessment_agent.create_assessment(
        student_id=request.student_id,
        category=request.category,
        skills=request.skills,
        questions_per_skill=request.questions_per_skill
    )
    
    # Store assessment
    assessments_db[assessment["assessment_id"]] = assessment
    
    # Return first question
    first_question = None
    if assessment["questions"]:
        first_question = {
            "question_id": assessment["questions"][0]["id"],
            "question_text": assessment["questions"][0]["question"],
            "options": assessment["questions"][0].get("options", []),
            "skill": assessment["questions"][0].get("skill", ""),
            "difficulty": assessment["questions"][0].get("difficulty", "medium"),
        }
    
    return {
        "assessment_id": assessment["assessment_id"],
        "total_questions": assessment["total_questions"],
        "category": assessment["category"],
        "current_question": first_question,
        "status": "in_progress"
    }


@router.post("/{assessment_id}/submit")
async def submit_answer(assessment_id: str, request: SubmitAnswerRequest):
    """Submit an answer for the current question"""
    
    assessment = assessments_db.get(assessment_id)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.get("status") == "completed":
        raise HTTPException(status_code=400, detail="Assessment already completed")
    
    # Submit answer and get result
    result = await skill_assessment_agent.submit_answer(
        assessment=assessment,
        question_id=request.question_id,
        answer=request.answer,
        time_taken=request.time_taken_seconds
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Get next question if available
    next_question = None
    current_index = assessment["current_index"]
    
    if current_index < len(assessment["questions"]):
        q = assessment["questions"][current_index]
        next_question = {
            "question_id": q["id"],
            "question_text": q["question"],
            "options": q.get("options", []),
            "skill": q.get("skill", ""),
            "difficulty": result["new_difficulty"],
        }
    
    return {
        "is_correct": result["is_correct"],
        "correct_answer": result["correct_answer"],
        "explanation": result["explanation"],
        "current_difficulty": result["new_difficulty"],
        "questions_remaining": result["questions_remaining"],
        "next_question": next_question
    }


@router.post("/{assessment_id}/complete")
async def complete_assessment(assessment_id: str):
    """Complete the assessment and get results"""
    
    assessment = assessments_db.get(assessment_id)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Generate results
    results = await skill_assessment_agent.complete_assessment(assessment)
    
    # Update assessment status
    assessment["status"] = "completed"
    assessment["results"] = results
    
    # Save to Firebase
    await firebase_service.save_assessment_result(assessment_id, results)
    
    # Record event in digital twin
    await digital_twin_agent.record_event(
        assessment["student_id"],
        "assessment_completed",
        results
    )
    
    return results


@router.get("/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Get assessment details"""
    
    assessment = assessments_db.get(assessment_id)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Don't return answers for in-progress assessments
    if assessment.get("status") != "completed":
        return {
            "assessment_id": assessment["assessment_id"],
            "student_id": assessment["student_id"],
            "category": assessment["category"],
            "total_questions": assessment["total_questions"],
            "current_index": assessment["current_index"],
            "status": assessment["status"],
            "started_at": assessment["started_at"]
        }
    
    return assessment


@router.get("/student/{student_id}/history")
async def get_assessment_history(student_id: str):
    """Get assessment history for a student"""
    
    # Get from Firebase
    history = await firebase_service.get_student_assessments(student_id)
    
    # Also check local store
    local_assessments = [
        a.get("results", a) for a in assessments_db.values()
        if a.get("student_id") == student_id and a.get("status") == "completed"
    ]
    
    # Combine and deduplicate
    all_ids = set()
    combined = []
    
    for a in history + local_assessments:
        aid = a.get("assessment_id")
        if aid and aid not in all_ids:
            all_ids.add(aid)
            combined.append(a)
    
    # Sort by completion date
    combined.sort(key=lambda x: x.get("completed_at", ""), reverse=True)
    
    return {
        "student_id": student_id,
        "total_assessments": len(combined),
        "assessments": combined
    }


@router.get("/questions/categories")
async def get_available_categories():
    """Get available assessment categories and skills"""
    
    return {
        "categories": [
            {
                "id": "technical",
                "name": "Technical Skills",
                "skills": ["dsa", "python", "java", "system_design", "javascript", "sql"]
            },
            {
                "id": "aptitude",
                "name": "Aptitude",
                "skills": ["logical", "quantitative", "verbal"]
            },
            {
                "id": "soft_skills",
                "name": "Soft Skills",
                "skills": ["communication", "teamwork", "leadership"]
            }
        ]
    }
