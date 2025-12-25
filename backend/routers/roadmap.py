from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

from agents.roadmap_generator_agent import roadmap_generator_agent
from agents.skill_gap_analyzer_agent import skill_gap_analyzer_agent
from agents.digital_twin_agent import digital_twin_agent
from routers.student_profile import profiles_db
from services.firebase_service import firebase_service

router = APIRouter()

# In-memory roadmap store
roadmaps_db = {}


class GenerateRoadmapRequest(BaseModel):
    student_id: str
    company_id: Optional[str] = None
    duration_weeks: int = 8
    daily_commitment: str = "moderate"  # light, moderate, intensive


class UpdateProgressRequest(BaseModel):
    task_id: str


@router.post("/generate")
async def generate_roadmap(request: GenerateRoadmapRequest):
    """Generate a personalized learning roadmap"""
    
    # Get student profile
    profile = profiles_db.get(request.student_id)
    
    if not profile:
        profile = await firebase_service.get_student(request.student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # First, perform skill gap analysis
    gap_analysis = await skill_gap_analyzer_agent.analyze_gap(
        student_id=request.student_id,
        student_profile=profile,
        company_id=request.company_id
    )
    
    # Generate roadmap
    roadmap = await roadmap_generator_agent.generate_roadmap(
        student_id=request.student_id,
        student_profile=profile,
        gap_analysis=gap_analysis,
        duration_weeks=request.duration_weeks,
        daily_hours=request.daily_commitment
    )
    
    # Store roadmap
    roadmaps_db[roadmap["roadmap_id"]] = roadmap
    
    # Save to Firebase
    await firebase_service.save_roadmap(roadmap["roadmap_id"], roadmap)
    
    return {
        "message": "Roadmap generated successfully",
        "roadmap": roadmap,
        "gap_analysis_summary": {
            "company": gap_analysis["company_name"],
            "role": gap_analysis["target_role"],
            "match_percentage": gap_analysis["skill_match_percentage"],
            "skills_to_learn": gap_analysis["missing_skills"]
        }
    }


@router.get("/{roadmap_id}")
async def get_roadmap(roadmap_id: str):
    """Get roadmap details"""
    
    roadmap = roadmaps_db.get(roadmap_id)
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    return roadmap


@router.get("/student/{student_id}/active")
async def get_active_roadmap(student_id: str):
    """Get active roadmap for a student"""
    
    # Check local store
    for rid, roadmap in roadmaps_db.items():
        if roadmap.get("student_id") == student_id and roadmap.get("status") == "active":
            return roadmap
    
    # Check Firebase
    roadmap = await firebase_service.get_student_roadmap(student_id)
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="No active roadmap found")
    
    return roadmap


@router.get("/{roadmap_id}/today")
async def get_todays_tasks(roadmap_id: str):
    """Get today's tasks from the roadmap"""
    
    roadmap = roadmaps_db.get(roadmap_id)
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    tasks = roadmap_generator_agent.get_todays_tasks(roadmap)
    
    completed_count = sum(1 for t in tasks if t.get("completed"))
    
    return {
        "roadmap_id": roadmap_id,
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "total_tasks": len(tasks),
        "completed_tasks": completed_count,
        "tasks": tasks
    }


@router.post("/{roadmap_id}/progress")
async def update_progress(roadmap_id: str, request: UpdateProgressRequest):
    """Mark a task as completed"""
    
    roadmap = roadmaps_db.get(roadmap_id)
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    # Update progress
    updated_roadmap = roadmap_generator_agent.update_progress(roadmap, request.task_id)
    
    # Save updated roadmap
    roadmaps_db[roadmap_id] = updated_roadmap
    await firebase_service.save_roadmap(roadmap_id, updated_roadmap)
    
    # Record event in digital twin
    await digital_twin_agent.record_event(
        updated_roadmap["student_id"],
        "roadmap_progress",
        {
            "roadmap_id": roadmap_id,
            "task_id": request.task_id,
            "progress_percentage": updated_roadmap["progress_percentage"]
        }
    )
    
    return {
        "message": "Progress updated",
        "roadmap_id": roadmap_id,
        "progress_percentage": updated_roadmap["progress_percentage"],
        "status": updated_roadmap["status"]
    }


@router.get("/{roadmap_id}/week/{week_number}")
async def get_week_plan(roadmap_id: str, week_number: int):
    """Get specific week's plan"""
    
    roadmap = roadmaps_db.get(roadmap_id)
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    weekly_plans = roadmap.get("weekly_plans", [])
    
    for week in weekly_plans:
        if week.get("week") == week_number:
            return week
    
    raise HTTPException(status_code=404, detail=f"Week {week_number} not found in roadmap")


@router.get("/{roadmap_id}/milestones")
async def get_milestones(roadmap_id: str):
    """Get roadmap milestones"""
    
    roadmap = roadmaps_db.get(roadmap_id)
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    milestones = roadmap.get("milestones", [])
    progress = roadmap.get("progress_percentage", 0)
    
    # Determine which milestones are completed based on progress
    weeks_completed = int((progress / 100) * roadmap.get("duration_weeks", 8))
    
    for milestone in milestones:
        milestone["completed"] = milestone.get("week", 0) <= weeks_completed
    
    return {
        "roadmap_id": roadmap_id,
        "total_milestones": len(milestones),
        "completed_milestones": sum(1 for m in milestones if m.get("completed")),
        "milestones": milestones
    }


@router.delete("/{roadmap_id}")
async def delete_roadmap(roadmap_id: str):
    """Delete a roadmap"""
    
    if roadmap_id in roadmaps_db:
        del roadmaps_db[roadmap_id]
    
    return {"message": "Roadmap deleted", "roadmap_id": roadmap_id}


# Import datetime for get_todays_tasks
from datetime import datetime
