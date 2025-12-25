"""
Digital Twin AI Agent
======================
Creates an evolving AI clone of each student that learns from all interactions
and predicts future performance.

Features:
- Continuous learning from assessments, interviews, and activities
- Pattern recognition in learning behavior
- Predictive analytics for success probability
- Proactive weakness identification
- GitHub integration for code analysis
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import math

from services.gemini_service import gemini_service


class DigitalTwinAgent:
    """Agent for maintaining and evolving student digital twins"""
    
    def __init__(self):
        self.gemini = gemini_service
        self.twins: Dict[str, Dict[str, Any]] = {}
    
    async def create_twin(
        self,
        student_id: str,
        student_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new digital twin for a student"""
        
        twin_id = f"twin_{student_id}"
        
        twin = {
            "twin_id": twin_id,
            "student_id": student_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            
            # Learning patterns
            "learning_patterns": {
                "preferred_time": None,  # Morning/afternoon/evening
                "session_duration": [],  # Average study duration
                "consistency_score": 0.0,  # How consistently they study
                "topics_by_strength": {},  # topic -> strength level
                "learning_velocity": {},  # topic -> learning speed
            },
            
            # Performance history
            "performance_history": [],
            
            # Skill evolution
            "skill_evolution": {},  # skill -> [timestamps, levels]
            
            # Behavior patterns
            "behavior_patterns": {
                "procrastination_tendency": 0.0,
                "interview_anxiety": 0.0,
                "topic_avoidance": [],
                "strength_areas": [],
            },
            
            # Predictions
            "predictions": {
                "success_probability": {},  # company -> probability
                "risk_factors": [],
                "opportunities": [],
            },
            
            # Events log
            "events": [],
            
            # Profile snapshot
            "profile_snapshot": student_profile,
        }
        
        self.twins[twin_id] = twin
        
        return twin
    
    async def record_event(
        self,
        student_id: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record a learning event and update the twin"""
        
        twin_id = f"twin_{student_id}"
        
        if twin_id not in self.twins:
            # Create twin if doesn't exist
            await self.create_twin(student_id, data.get("profile", {}))
        
        twin = self.twins[twin_id]
        
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        
        twin["events"].append(event)
        
        # Process event based on type
        if event_type == "assessment_completed":
            await self._process_assessment_event(twin, data)
        elif event_type == "interview_completed":
            await self._process_interview_event(twin, data)
        elif event_type == "coding_submission":
            await self._process_coding_event(twin, data)
        elif event_type == "resource_completed":
            await self._process_learning_event(twin, data)
        elif event_type == "roadmap_progress":
            await self._process_roadmap_event(twin, data)
        elif event_type == "github_activity":
            await self._process_github_event(twin, data)
        
        # Update patterns
        await self._update_learning_patterns(twin)
        
        # Update predictions
        await self._update_predictions(twin)
        
        twin["last_updated"] = datetime.utcnow().isoformat()
        
        return event
    
    async def _process_assessment_event(
        self,
        twin: Dict[str, Any],
        data: Dict[str, Any]
    ):
        """Process assessment completion event"""
        
        skill_scores = data.get("skill_scores", {})
        
        # Update skill evolution
        for skill, score in skill_scores.items():
            if skill not in twin["skill_evolution"]:
                twin["skill_evolution"][skill] = []
            
            twin["skill_evolution"][skill].append({
                "timestamp": datetime.utcnow().isoformat(),
                "score": score
            })
        
        # Add to performance history
        twin["performance_history"].append({
            "type": "assessment",
            "category": data.get("category", "unknown"),
            "score": data.get("score", 0),
            "timestamp": datetime.utcnow().isoformat(),
            "strengths": data.get("strengths", []),
            "weaknesses": data.get("weaknesses", []),
        })
        
        # Update behavior patterns
        weaknesses = data.get("weaknesses", [])
        if weaknesses:
            twin["behavior_patterns"]["topic_avoidance"].extend(weaknesses)
            # Deduplicate
            twin["behavior_patterns"]["topic_avoidance"] = list(set(
                twin["behavior_patterns"]["topic_avoidance"]
            ))[:10]
        
        strengths = data.get("strengths", [])
        if strengths:
            twin["behavior_patterns"]["strength_areas"].extend(strengths)
            twin["behavior_patterns"]["strength_areas"] = list(set(
                twin["behavior_patterns"]["strength_areas"]
            ))[:10]
    
    async def _process_interview_event(
        self,
        twin: Dict[str, Any],
        data: Dict[str, Any]
    ):
        """Process interview completion event"""
        
        feedback = data.get("feedback", {})
        
        # Track interview anxiety
        confidence_score = feedback.get("confidence_score", 5)
        current_anxiety = twin["behavior_patterns"]["interview_anxiety"]
        
        # Low confidence = high anxiety
        anxiety_indicator = 10 - confidence_score
        
        # Rolling average
        twin["behavior_patterns"]["interview_anxiety"] = (
            current_anxiety * 0.7 + anxiety_indicator * 0.3
        )
        
        # Add to performance history
        twin["performance_history"].append({
            "type": "interview",
            "interview_type": data.get("interview_type", "technical"),
            "score": feedback.get("overall_score", 5),
            "confidence": confidence_score,
            "communication": feedback.get("communication_score", 5),
            "timestamp": datetime.utcnow().isoformat(),
            "improvements": feedback.get("improvements", []),
        })
    
    async def _process_coding_event(
        self,
        twin: Dict[str, Any],
        data: Dict[str, Any]
    ):
        """Process coding submission event"""
        
        # Track DSA progress
        problem_type = data.get("problem_type", "unknown")
        difficulty = data.get("difficulty", "medium")
        solved = data.get("solved", False)
        time_taken = data.get("time_minutes", 0)
        
        # Update learning velocity for DSA
        if "dsa" not in twin["learning_patterns"]["learning_velocity"]:
            twin["learning_patterns"]["learning_velocity"]["dsa"] = {
                "problems_attempted": 0,
                "problems_solved": 0,
                "avg_time": 0,
            }
        
        dsa_stats = twin["learning_patterns"]["learning_velocity"]["dsa"]
        dsa_stats["problems_attempted"] += 1
        if solved:
            dsa_stats["problems_solved"] += 1
        
        # Update average time
        if time_taken > 0:
            total_time = dsa_stats["avg_time"] * (dsa_stats["problems_attempted"] - 1)
            dsa_stats["avg_time"] = (total_time + time_taken) / dsa_stats["problems_attempted"]
    
    async def _process_learning_event(
        self,
        twin: Dict[str, Any],
        data: Dict[str, Any]
    ):
        """Process learning resource completion event"""
        
        skill = data.get("skill", "unknown")
        duration_minutes = data.get("duration_minutes", 0)
        completion_status = data.get("completion_status", "partial")
        
        # Track session duration
        twin["learning_patterns"]["session_duration"].append(duration_minutes)
        
        # Keep only last 30 sessions
        if len(twin["learning_patterns"]["session_duration"]) > 30:
            twin["learning_patterns"]["session_duration"] = \
                twin["learning_patterns"]["session_duration"][-30:]
        
        # Update learning velocity for this skill
        if skill not in twin["learning_patterns"]["learning_velocity"]:
            twin["learning_patterns"]["learning_velocity"][skill] = {
                "sessions": 0,
                "total_time": 0,
                "completions": 0,
            }
        
        stats = twin["learning_patterns"]["learning_velocity"][skill]
        stats["sessions"] += 1
        stats["total_time"] += duration_minutes
        if completion_status == "completed":
            stats["completions"] += 1
    
    async def _process_roadmap_event(
        self,
        twin: Dict[str, Any],
        data: Dict[str, Any]
    ):
        """Process roadmap progress event"""
        
        progress = data.get("progress_percentage", 0)
        tasks_completed = data.get("tasks_completed", 0)
        tasks_skipped = data.get("tasks_skipped", 0)
        
        # Track procrastination
        if tasks_skipped > tasks_completed:
            twin["behavior_patterns"]["procrastination_tendency"] = min(
                twin["behavior_patterns"]["procrastination_tendency"] + 0.1,
                1.0
            )
        else:
            twin["behavior_patterns"]["procrastination_tendency"] = max(
                twin["behavior_patterns"]["procrastination_tendency"] - 0.05,
                0.0
            )
    
    async def _process_github_event(
        self,
        twin: Dict[str, Any],
        data: Dict[str, Any]
    ):
        """Process GitHub activity event"""
        
        commits = data.get("commits", 0)
        languages = data.get("languages", [])
        
        # Update profile with GitHub insights
        if "github_activity" not in twin:
            twin["github_activity"] = {
                "total_commits": 0,
                "languages": {},
                "activity_streak": 0,
            }
        
        twin["github_activity"]["total_commits"] += commits
        
        for lang in languages:
            if lang not in twin["github_activity"]["languages"]:
                twin["github_activity"]["languages"][lang] = 0
            twin["github_activity"]["languages"][lang] += 1
    
    async def _update_learning_patterns(self, twin: Dict[str, Any]):
        """Update learning patterns based on recent events"""
        
        events = twin.get("events", [])
        
        if not events:
            return
        
        # Calculate consistency score
        recent_events = [
            e for e in events
            if datetime.fromisoformat(e["timestamp"]) > datetime.utcnow() - timedelta(days=14)
        ]
        
        # Count events per day in last 14 days
        days_with_activity = set()
        for e in recent_events:
            event_date = datetime.fromisoformat(e["timestamp"]).date()
            days_with_activity.add(event_date)
        
        # Consistency = days active / 14
        twin["learning_patterns"]["consistency_score"] = len(days_with_activity) / 14.0
        
        # Determine preferred time
        hour_counts = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}
        for e in recent_events:
            hour = datetime.fromisoformat(e["timestamp"]).hour
            if 5 <= hour < 12:
                hour_counts["morning"] += 1
            elif 12 <= hour < 17:
                hour_counts["afternoon"] += 1
            elif 17 <= hour < 21:
                hour_counts["evening"] += 1
            else:
                hour_counts["night"] += 1
        
        if max(hour_counts.values()) > 0:
            twin["learning_patterns"]["preferred_time"] = max(hour_counts, key=hour_counts.get)
    
    async def _update_predictions(self, twin: Dict[str, Any]):
        """Update success predictions based on current state"""
        
        # Calculate base success probability factors
        consistency = twin["learning_patterns"]["consistency_score"]
        anxiety = twin["behavior_patterns"]["interview_anxiety"]
        procrastination = twin["behavior_patterns"]["procrastination_tendency"]
        
        # Get recent assessment performance
        recent_assessments = [
            p for p in twin["performance_history"]
            if p.get("type") == "assessment"
        ][-5:]
        
        avg_assessment_score = 0
        if recent_assessments:
            avg_assessment_score = sum(a.get("score", 0) for a in recent_assessments) / len(recent_assessments)
        
        # Calculate base probability
        base_probability = (
            consistency * 0.2 +
            (1 - anxiety / 10) * 0.15 +
            (1 - procrastination) * 0.15 +
            (avg_assessment_score / 100) * 0.5
        )
        
        # Identify risk factors
        risk_factors = []
        
        if consistency < 0.5:
            risk_factors.append({
                "factor": "Low consistency in learning",
                "impact": "high",
                "recommendation": "Try to study at least 5 days a week"
            })
        
        if anxiety > 7:
            risk_factors.append({
                "factor": "High interview anxiety",
                "impact": "high",
                "recommendation": "Practice more mock interviews to build confidence"
            })
        
        if procrastination > 0.6:
            risk_factors.append({
                "factor": "Tendency to skip tasks",
                "impact": "medium",
                "recommendation": "Break tasks into smaller chunks and use the Pomodoro technique"
            })
        
        weak_skills = twin["behavior_patterns"].get("topic_avoidance", [])
        if len(weak_skills) > 3:
            risk_factors.append({
                "factor": f"Multiple weak areas: {', '.join(weak_skills[:3])}",
                "impact": "high",
                "recommendation": f"Focus on improving: {weak_skills[0]}"
            })
        
        # Update predictions
        twin["predictions"]["risk_factors"] = risk_factors
        
        # Calculate company-specific probabilities
        company_adjustments = {
            "Google": {"dsa_weight": 0.4, "system_design_weight": 0.3},
            "Amazon": {"dsa_weight": 0.35, "leadership_weight": 0.25},
            "Microsoft": {"dsa_weight": 0.35, "system_design_weight": 0.25},
            "Meta": {"dsa_weight": 0.4, "system_design_weight": 0.3},
            "Startups": {"versatility_weight": 0.4, "communication_weight": 0.3},
        }
        
        for company, weights in company_adjustments.items():
            # Adjust base probability based on company-specific factors
            adjustment = 0
            
            skill_strengths = twin["behavior_patterns"].get("strength_areas", [])
            
            if "dsa" in skill_strengths or "algorithms" in skill_strengths:
                adjustment += weights.get("dsa_weight", 0.2)
            
            if "system design" in skill_strengths:
                adjustment += weights.get("system_design_weight", 0.2)
            
            company_probability = min(base_probability + adjustment - (len(risk_factors) * 0.05), 0.95)
            company_probability = max(company_probability, 0.1)
            
            twin["predictions"]["success_probability"][company] = round(company_probability, 2)
    
    async def predict_weakness(
        self,
        student_id: str,
        target_company: str = None
    ) -> Dict[str, Any]:
        """Predict future weaknesses based on learning patterns"""
        
        twin_id = f"twin_{student_id}"
        
        if twin_id not in self.twins:
            return {"error": "Digital twin not found. Complete some activities first."}
        
        twin = self.twins[twin_id]
        
        # Analyze skill evolution trends
        declining_skills = []
        stagnant_skills = []
        
        for skill, history in twin["skill_evolution"].items():
            if len(history) >= 3:
                recent = history[-3:]
                scores = [h["score"] for h in recent]
                
                # Check for decline
                if scores[-1] < scores[0]:
                    declining_skills.append({
                        "skill": skill,
                        "trend": "declining",
                        "recent_scores": scores,
                    })
                # Check for stagnation
                elif abs(scores[-1] - scores[0]) < 5:
                    stagnant_skills.append({
                        "skill": skill,
                        "trend": "stagnant",
                        "recent_scores": scores,
                    })
        
        # Generate predictions using AI
        prediction_context = {
            "declining_skills": declining_skills,
            "stagnant_skills": stagnant_skills,
            "topic_avoidance": twin["behavior_patterns"]["topic_avoidance"],
            "consistency": twin["learning_patterns"]["consistency_score"],
            "interview_anxiety": twin["behavior_patterns"]["interview_anxiety"],
            "success_probabilities": twin["predictions"]["success_probability"],
        }
        
        ai_prediction = await self.gemini.predict_success_probability(
            twin["profile_snapshot"],
            {"company_name": target_company, "required_skills": ["dsa", "system design"]},
            twin["performance_history"][-10:]
        )
        
        return {
            "student_id": student_id,
            "target_company": target_company,
            "predicted_weaknesses": declining_skills + stagnant_skills,
            "success_probability": ai_prediction.get("success_probability", 0.5),
            "confidence_level": ai_prediction.get("confidence_level", 0.5),
            "risk_factors": twin["predictions"]["risk_factors"],
            "recommended_actions": ai_prediction.get("recommended_actions", []),
            "timeline_to_readiness": ai_prediction.get("timeline_to_readiness", "Unknown"),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_twin_summary(self, student_id: str) -> Dict[str, Any]:
        """Get a summary of the digital twin state"""
        
        twin_id = f"twin_{student_id}"
        
        if twin_id not in self.twins:
            return {"error": "Digital twin not found"}
        
        twin = self.twins[twin_id]
        
        return {
            "student_id": student_id,
            "twin_id": twin_id,
            "events_recorded": len(twin.get("events", [])),
            "learning_patterns": twin["learning_patterns"],
            "behavior_patterns": twin["behavior_patterns"],
            "success_predictions": twin["predictions"]["success_probability"],
            "risk_factors_count": len(twin["predictions"]["risk_factors"]),
            "skills_tracked": list(twin["skill_evolution"].keys()),
            "last_updated": twin["last_updated"],
        }
    
    def get_twin(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get the full digital twin data"""
        return self.twins.get(f"twin_{student_id}")


# Singleton instance
digital_twin_agent = DigitalTwinAgent()
