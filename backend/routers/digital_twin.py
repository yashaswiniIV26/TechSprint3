from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from agents.digital_twin_agent import digital_twin_agent
from routers.student_profile import profiles_db
from services.firebase_service import firebase_service

router = APIRouter()


class CreateTwinRequest(BaseModel):
    student_id: str


class RecordEventRequest(BaseModel):
    student_id: str
    event_type: str
    data: dict


class PredictRequest(BaseModel):
    student_id: str
    target_company: Optional[str] = None


@router.post("/create")
async def create_digital_twin(request: CreateTwinRequest):
    """Create a digital twin for a student"""
    
    # Get student profile
    profile = profiles_db.get(request.student_id)
    
    if not profile:
        profile = await firebase_service.get_student(request.student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Create twin
    twin = await digital_twin_agent.create_twin(
        student_id=request.student_id,
        student_profile=profile
    )
    
    # Save to Firebase
    await firebase_service.save_digital_twin(twin["twin_id"], twin)
    
    return {
        "message": "Digital twin created successfully",
        "twin_id": twin["twin_id"],
        "student_id": request.student_id
    }


@router.post("/event")
async def record_learning_event(request: RecordEventRequest):
    """Record a learning event for the digital twin"""
    
    event = await digital_twin_agent.record_event(
        student_id=request.student_id,
        event_type=request.event_type,
        data=request.data
    )
    
    # Save event to Firebase
    await firebase_service.add_learning_event(request.student_id, event)
    
    return {
        "message": "Event recorded successfully",
        "event_id": event.get("event_id"),
        "event_type": request.event_type
    }


@router.get("/{student_id}")
async def get_digital_twin(student_id: str):
    """Get digital twin for a student"""
    
    twin = digital_twin_agent.get_twin(student_id)
    
    if not twin:
        # Try Firebase
        twin = await firebase_service.get_digital_twin(student_id)
    
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    return twin


@router.get("/{student_id}/summary")
async def get_twin_summary(student_id: str):
    """Get summary of digital twin state"""
    
    summary = await digital_twin_agent.get_twin_summary(student_id)
    
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    
    return summary


@router.post("/predict")
async def predict_weakness(request: PredictRequest):
    """Predict future weaknesses and success probability"""
    
    prediction = await digital_twin_agent.predict_weakness(
        student_id=request.student_id,
        target_company=request.target_company
    )
    
    if "error" in prediction:
        raise HTTPException(status_code=404, detail=prediction["error"])
    
    return prediction


@router.get("/{student_id}/predictions")
async def get_predictions(student_id: str):
    """Get all predictions for a student"""
    
    twin = digital_twin_agent.get_twin(student_id)
    
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    return {
        "student_id": student_id,
        "success_probabilities": twin.get("predictions", {}).get("success_probability", {}),
        "risk_factors": twin.get("predictions", {}).get("risk_factors", []),
        "opportunities": twin.get("predictions", {}).get("opportunities", [])
    }


@router.get("/{student_id}/patterns")
async def get_learning_patterns(student_id: str):
    """Get learning patterns identified by the digital twin"""
    
    twin = digital_twin_agent.get_twin(student_id)
    
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    return {
        "student_id": student_id,
        "learning_patterns": twin.get("learning_patterns", {}),
        "behavior_patterns": twin.get("behavior_patterns", {})
    }


@router.get("/{student_id}/skill-evolution")
async def get_skill_evolution(student_id: str):
    """Get skill evolution history"""
    
    twin = digital_twin_agent.get_twin(student_id)
    
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    return {
        "student_id": student_id,
        "skill_evolution": twin.get("skill_evolution", {}),
        "skills_tracked": list(twin.get("skill_evolution", {}).keys())
    }


@router.get("/{student_id}/events")
async def get_events(student_id: str, limit: int = 50):
    """Get recent events recorded for the digital twin"""
    
    twin = digital_twin_agent.get_twin(student_id)
    
    if not twin:
        # Try Firebase
        events = await firebase_service.get_learning_events(student_id, limit)
        return {
            "student_id": student_id,
            "total_events": len(events),
            "events": events
        }
    
    events = twin.get("events", [])[-limit:]
    
    return {
        "student_id": student_id,
        "total_events": len(events),
        "events": events
    }


@router.get("/{student_id}/insights")
async def get_insights(student_id: str):
    """Get AI-generated insights about the student"""
    
    twin = digital_twin_agent.get_twin(student_id)
    
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    # Generate insights based on patterns
    insights = []
    
    # Consistency insight
    consistency = twin.get("learning_patterns", {}).get("consistency_score", 0)
    if consistency < 0.3:
        insights.append({
            "type": "warning",
            "title": "Low Consistency",
            "message": "You've been inactive for several days. Try to maintain a regular study schedule.",
            "action": "Set daily reminders for study sessions"
        })
    elif consistency > 0.7:
        insights.append({
            "type": "success",
            "title": "Great Consistency!",
            "message": "You're maintaining an excellent study streak. Keep it up!",
            "action": "Continue your current routine"
        })
    
    # Interview anxiety insight
    anxiety = twin.get("behavior_patterns", {}).get("interview_anxiety", 0)
    if anxiety > 6:
        insights.append({
            "type": "tip",
            "title": "Interview Confidence",
            "message": "Your interview anxiety seems high. Practice more to build confidence.",
            "action": "Schedule 2-3 mock interviews this week"
        })
    
    # Procrastination insight
    procrastination = twin.get("behavior_patterns", {}).get("procrastination_tendency", 0)
    if procrastination > 0.5:
        insights.append({
            "type": "warning",
            "title": "Task Completion",
            "message": "You're skipping some tasks. Try breaking them into smaller chunks.",
            "action": "Use the Pomodoro technique (25 min work, 5 min break)"
        })
    
    # Strength areas
    strengths = twin.get("behavior_patterns", {}).get("strength_areas", [])
    if strengths:
        insights.append({
            "type": "success",
            "title": "Your Strengths",
            "message": f"You're performing well in: {', '.join(strengths[:3])}",
            "action": "Leverage these in your interviews"
        })
    
    # Weak areas
    weak_areas = twin.get("behavior_patterns", {}).get("topic_avoidance", [])
    if weak_areas:
        insights.append({
            "type": "info",
            "title": "Areas to Improve",
            "message": f"Focus on improving: {', '.join(weak_areas[:3])}",
            "action": "Add these to your daily practice routine"
        })
    
    return {
        "student_id": student_id,
        "total_insights": len(insights),
        "insights": insights,
        "generated_at": datetime.utcnow().isoformat()
    }


from datetime import datetime
