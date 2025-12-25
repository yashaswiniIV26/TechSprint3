from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

from agents.interview_coach_agent import interview_coach_agent
from agents.digital_twin_agent import digital_twin_agent
from routers.student_profile import profiles_db
from services.firebase_service import firebase_service
from models.schemas import InterviewType

router = APIRouter()


class StartInterviewRequest(BaseModel):
    student_id: str
    interview_type: InterviewType
    language: str = "en"
    target_company: Optional[str] = None
    target_role: Optional[str] = None


class SubmitResponseRequest(BaseModel):
    response_text: str
    audio_transcript: Optional[str] = None


@router.post("/start")
async def start_interview(request: StartInterviewRequest):
    """Start a new mock interview session"""
    
    # Get student profile
    profile = profiles_db.get(request.student_id)
    
    if not profile:
        profile = await firebase_service.get_student(request.student_id)
    
    # Start interview session
    session = await interview_coach_agent.start_interview(
        student_id=request.student_id,
        interview_type=request.interview_type,
        language=request.language,
        target_company=request.target_company,
        target_role=request.target_role,
        student_profile=profile
    )
    
    return session


@router.post("/{session_id}/respond")
async def submit_response(session_id: str, request: SubmitResponseRequest):
    """Submit a response during the interview"""
    
    result = await interview_coach_agent.submit_response(
        session_id=session_id,
        response_text=request.response_text,
        audio_transcript=request.audio_transcript
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/{session_id}/end")
async def end_interview(session_id: str):
    """End the interview and get comprehensive feedback"""
    
    result = await interview_coach_agent.end_interview(session_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Get session to record event
    session = interview_coach_agent.get_session(session_id)
    
    if session:
        # Save to Firebase
        await firebase_service.save_interview_session(session_id, session)
        
        # Record event in digital twin
        await digital_twin_agent.record_event(
            session["student_id"],
            "interview_completed",
            {
                "session_id": session_id,
                "interview_type": session["interview_type"],
                "feedback": result.get("feedback", {})
            }
        )
    
    return result


@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get interview session details"""
    
    session = interview_coach_agent.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Return sanitized session data
    return {
        "session_id": session["session_id"],
        "student_id": session["student_id"],
        "interview_type": session["interview_type"],
        "language": session["language"],
        "status": session["status"],
        "started_at": session["started_at"],
        "ended_at": session.get("ended_at"),
        "questions_asked": len(session.get("questions_asked", [])),
        "messages": session.get("messages", []),
        "final_feedback": session.get("final_feedback")
    }


@router.get("/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get all messages from an interview session"""
    
    session = interview_coach_agent.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": session.get("messages", [])
    }


@router.get("/{session_id}/feedback")
async def get_session_feedback(session_id: str):
    """Get feedback for a completed interview"""
    
    session = interview_coach_agent.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Interview not yet completed")
    
    return session.get("final_feedback", {})


@router.get("/student/{student_id}/history")
async def get_interview_history(student_id: str):
    """Get interview history for a student"""
    
    # Get from Firebase
    history = await firebase_service.get_interview_history(student_id)
    
    # Format for response
    formatted = []
    for session in history:
        formatted.append({
            "session_id": session.get("session_id"),
            "interview_type": session.get("interview_type"),
            "status": session.get("status"),
            "started_at": session.get("started_at"),
            "ended_at": session.get("ended_at"),
            "overall_score": session.get("final_feedback", {}).get("overall_score"),
            "confidence_score": session.get("final_feedback", {}).get("confidence_score"),
        })
    
    return {
        "student_id": student_id,
        "total_interviews": len(formatted),
        "interviews": formatted
    }


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for interviews"""
    
    languages = interview_coach_agent.get_supported_languages()
    
    return {
        "supported_languages": [
            {"code": code, "name": name}
            for code, name in languages.items()
        ]
    }


@router.get("/types")
async def get_interview_types():
    """Get available interview types"""
    
    return {
        "types": [
            {
                "id": "technical",
                "name": "Technical Interview",
                "description": "Data structures, algorithms, and programming concepts",
                "duration_minutes": 45
            },
            {
                "id": "hr",
                "name": "HR Interview",
                "description": "Background, motivation, and cultural fit questions",
                "duration_minutes": 30
            },
            {
                "id": "behavioral",
                "name": "Behavioral Interview",
                "description": "Situation-based questions about past experiences",
                "duration_minutes": 30
            },
            {
                "id": "system_design",
                "name": "System Design Interview",
                "description": "Design scalable systems and architecture",
                "duration_minutes": 45
            }
        ]
    }
