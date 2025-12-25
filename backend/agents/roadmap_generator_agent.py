"""
Personalized Roadmap Generator Agent (Train Step)
===================================================
Creates daily learning plans for each student.

Features:
- LLM-powered plan generation
- Skill-based curriculum
- Resource recommendations
- Progress tracking
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from services.gemini_service import gemini_service


class RoadmapGeneratorAgent:
    """Agent for generating personalized learning roadmaps"""
    
    # Learning resource database
    LEARNING_RESOURCES = {
        "python": [
            {"type": "course", "title": "Python for Beginners", "url": "https://www.codecademy.com/learn/learn-python-3", "level": "beginner"},
            {"type": "video", "title": "Python Tutorial - Full Course", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc", "level": "beginner"},
            {"type": "practice", "title": "HackerRank Python", "url": "https://www.hackerrank.com/domains/python", "level": "all"},
            {"type": "docs", "title": "Official Python Docs", "url": "https://docs.python.org/3/", "level": "all"},
        ],
        "java": [
            {"type": "course", "title": "Java Programming Masterclass", "url": "https://www.udemy.com/course/java-the-complete-java-developer-course/", "level": "beginner"},
            {"type": "video", "title": "Java Full Course", "url": "https://www.youtube.com/watch?v=eIrMbAQSU34", "level": "beginner"},
            {"type": "practice", "title": "LeetCode Java", "url": "https://leetcode.com/problemset/all/", "level": "all"},
        ],
        "dsa": [
            {"type": "course", "title": "Data Structures & Algorithms", "url": "https://www.coursera.org/specializations/data-structures-algorithms", "level": "beginner"},
            {"type": "video", "title": "DSA Full Course", "url": "https://www.youtube.com/watch?v=8hly31xKli0", "level": "beginner"},
            {"type": "practice", "title": "LeetCode", "url": "https://leetcode.com/", "level": "all"},
            {"type": "practice", "title": "Codeforces", "url": "https://codeforces.com/", "level": "intermediate"},
            {"type": "book", "title": "CLRS - Introduction to Algorithms", "url": "https://mitpress.mit.edu/books/introduction-algorithms", "level": "advanced"},
        ],
        "system_design": [
            {"type": "course", "title": "Grokking System Design", "url": "https://www.educative.io/courses/grokking-the-system-design-interview", "level": "intermediate"},
            {"type": "video", "title": "System Design Primer", "url": "https://www.youtube.com/c/SystemDesignInterview", "level": "intermediate"},
            {"type": "book", "title": "Designing Data-Intensive Applications", "url": "https://dataintensive.net/", "level": "advanced"},
        ],
        "react": [
            {"type": "docs", "title": "React Official Docs", "url": "https://react.dev/", "level": "beginner"},
            {"type": "course", "title": "React - The Complete Guide", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "level": "beginner"},
            {"type": "practice", "title": "Build Projects", "url": "https://www.frontendmentor.io/", "level": "all"},
        ],
        "communication": [
            {"type": "course", "title": "Business Communication", "url": "https://www.coursera.org/learn/wharton-communication-skills", "level": "beginner"},
            {"type": "practice", "title": "Daily Speaking Practice", "url": "https://www.toastmasters.org/", "level": "all"},
            {"type": "video", "title": "TED Talks Communication", "url": "https://www.ted.com/topics/communication", "level": "all"},
        ],
        "oop": [
            {"type": "course", "title": "Object-Oriented Programming", "url": "https://www.coursera.org/learn/object-oriented-java", "level": "beginner"},
            {"type": "video", "title": "OOP Concepts Explained", "url": "https://www.youtube.com/watch?v=pTB0EiLXUC8", "level": "beginner"},
            {"type": "practice", "title": "Design Patterns Practice", "url": "https://refactoring.guru/design-patterns", "level": "intermediate"},
        ],
        "sql": [
            {"type": "course", "title": "SQL Complete Course", "url": "https://www.codecademy.com/learn/learn-sql", "level": "beginner"},
            {"type": "practice", "title": "SQLZoo", "url": "https://sqlzoo.net/", "level": "beginner"},
            {"type": "practice", "title": "HackerRank SQL", "url": "https://www.hackerrank.com/domains/sql", "level": "all"},
        ],
        "javascript": [
            {"type": "course", "title": "JavaScript Complete Guide", "url": "https://javascript.info/", "level": "beginner"},
            {"type": "video", "title": "JavaScript Crash Course", "url": "https://www.youtube.com/watch?v=hdI2bqOjy3c", "level": "beginner"},
            {"type": "practice", "title": "JavaScript30", "url": "https://javascript30.com/", "level": "intermediate"},
        ],
    }
    
    # Daily time allocation templates
    TIME_TEMPLATES = {
        "intensive": {  # 6+ hours/day
            "primary_skill": 3.0,
            "secondary_skill": 2.0,
            "practice": 1.0,
            "soft_skills": 0.5,
        },
        "moderate": {  # 3-4 hours/day
            "primary_skill": 1.5,
            "secondary_skill": 1.0,
            "practice": 0.5,
            "soft_skills": 0.5,
        },
        "light": {  # 1-2 hours/day
            "primary_skill": 1.0,
            "practice": 0.5,
            "soft_skills": 0.25,
        },
    }
    
    def __init__(self):
        self.gemini = gemini_service
    
    def get_resources_for_skill(
        self,
        skill: str,
        level: str = "all"
    ) -> List[Dict[str, str]]:
        """Get learning resources for a skill"""
        
        skill_lower = skill.lower().replace(" ", "_")
        resources = self.LEARNING_RESOURCES.get(skill_lower, [])
        
        if level != "all":
            resources = [r for r in resources if r["level"] in [level, "all"]]
        
        return resources[:5]  # Return top 5
    
    def calculate_skill_priority(
        self,
        missing_skills: List[str],
        gap_severity: Dict[str, str],
        target_role: str
    ) -> List[Dict[str, Any]]:
        """Calculate learning priority for each skill"""
        
        priority_weights = {
            "critical": 3,
            "moderate": 2,
            "minor": 1
        }
        
        # Core skills for common roles
        role_core_skills = {
            "software engineer": ["dsa", "system design", "oop"],
            "frontend developer": ["javascript", "react", "html", "css"],
            "backend developer": ["python", "java", "sql", "api"],
            "data scientist": ["python", "machine learning", "sql", "statistics"],
            "full stack": ["javascript", "react", "node.js", "sql"],
        }
        
        core_skills = role_core_skills.get(target_role.lower(), ["dsa", "oop"])
        
        priorities = []
        for skill in missing_skills:
            weight = priority_weights.get(gap_severity.get(skill, "moderate"), 2)
            
            # Boost if it's a core skill for the role
            if skill.lower() in core_skills:
                weight += 2
            
            priorities.append({
                "skill": skill,
                "priority_score": weight,
                "severity": gap_severity.get(skill, "moderate")
            })
        
        # Sort by priority (highest first)
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return priorities
    
    def create_week_plan(
        self,
        week_number: int,
        start_date: datetime,
        skills_to_focus: List[str],
        time_template: str = "moderate"
    ) -> Dict[str, Any]:
        """Create a detailed weekly plan"""
        
        template = self.TIME_TEMPLATES.get(time_template, self.TIME_TEMPLATES["moderate"])
        days = []
        
        for day_offset in range(7):
            day_date = start_date + timedelta(days=day_offset)
            
            # Weekend adjustments
            if day_date.weekday() >= 5:  # Saturday or Sunday
                if day_date.weekday() == 6:  # Sunday - rest day
                    days.append({
                        "day": day_offset + 1,
                        "date": day_date.strftime("%Y-%m-%d"),
                        "is_rest_day": True,
                        "tasks": [{
                            "task_id": str(uuid.uuid4()),
                            "title": "Rest & Review",
                            "description": "Review what you learned this week. Take notes on key concepts.",
                            "duration_hours": 1.0,
                            "skill_target": "review",
                            "resources": []
                        }],
                        "total_hours": 1.0
                    })
                    continue
            
            tasks = []
            total_hours = 0.0
            
            # Primary skill task
            if skills_to_focus:
                primary_skill = skills_to_focus[0]
                resources = self.get_resources_for_skill(primary_skill)
                
                tasks.append({
                    "task_id": str(uuid.uuid4()),
                    "title": f"Learn {primary_skill}",
                    "description": f"Focus session on {primary_skill} fundamentals and concepts",
                    "duration_hours": template.get("primary_skill", 1.5),
                    "skill_target": primary_skill,
                    "resources": resources[:2],
                    "priority": 1
                })
                total_hours += template.get("primary_skill", 1.5)
            
            # Secondary skill (alternating days)
            if len(skills_to_focus) > 1 and day_offset % 2 == 0:
                secondary_skill = skills_to_focus[1]
                resources = self.get_resources_for_skill(secondary_skill)
                
                tasks.append({
                    "task_id": str(uuid.uuid4()),
                    "title": f"Practice {secondary_skill}",
                    "description": f"Work on {secondary_skill} problems and exercises",
                    "duration_hours": template.get("secondary_skill", 1.0),
                    "skill_target": secondary_skill,
                    "resources": resources[:2],
                    "priority": 2
                })
                total_hours += template.get("secondary_skill", 1.0)
            
            # Daily DSA practice
            if "dsa" not in [s.lower() for s in skills_to_focus[:2]]:
                tasks.append({
                    "task_id": str(uuid.uuid4()),
                    "title": "DSA Practice",
                    "description": "Solve 2-3 DSA problems on LeetCode/HackerRank",
                    "duration_hours": template.get("practice", 0.5),
                    "skill_target": "dsa",
                    "resources": self.get_resources_for_skill("dsa")[:1],
                    "priority": 3
                })
                total_hours += template.get("practice", 0.5)
            
            # Soft skills (every other day)
            if day_offset % 2 == 1 and "soft_skills" in template:
                tasks.append({
                    "task_id": str(uuid.uuid4()),
                    "title": "Communication Practice",
                    "description": "Practice speaking about technical topics for 15-30 minutes",
                    "duration_hours": template.get("soft_skills", 0.25),
                    "skill_target": "communication",
                    "resources": self.get_resources_for_skill("communication")[:1],
                    "priority": 4
                })
                total_hours += template.get("soft_skills", 0.25)
            
            days.append({
                "day": day_offset + 1,
                "date": day_date.strftime("%Y-%m-%d"),
                "is_rest_day": False,
                "tasks": tasks,
                "total_hours": round(total_hours, 2),
                "focus_skills": skills_to_focus[:2]
            })
        
        return {
            "week": week_number,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": (start_date + timedelta(days=6)).strftime("%Y-%m-%d"),
            "days": days,
            "weekly_goals": [
                f"Complete core concepts of {skills_to_focus[0]}" if skills_to_focus else "Continue learning",
                f"Solve 10+ DSA problems",
                f"Build one mini-project using learned skills"
            ],
            "assessment_scheduled": week_number % 2 == 0  # Assessment every 2 weeks
        }
    
    async def generate_roadmap(
        self,
        student_id: str,
        student_profile: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        duration_weeks: int = 8,
        daily_hours: str = "moderate"
    ) -> Dict[str, Any]:
        """Generate a complete personalized roadmap"""
        
        roadmap_id = str(uuid.uuid4())
        
        # Get prioritized skills from gap analysis
        missing_skills = gap_analysis.get("missing_skills", [])
        gap_severity = gap_analysis.get("gap_severity", {})
        target_role = gap_analysis.get("target_role", "Software Engineer")
        
        priorities = self.calculate_skill_priority(missing_skills, gap_severity, target_role)
        
        # Create weekly plans
        weekly_plans = []
        start_date = datetime.utcnow()
        
        for week in range(1, duration_weeks + 1):
            # Determine focus skills for this week
            # Rotate through prioritized skills
            skill_index = (week - 1) % max(len(priorities), 1)
            focus_skills = []
            
            if priorities:
                focus_skills.append(priorities[skill_index]["skill"])
                if len(priorities) > 1:
                    next_index = (skill_index + 1) % len(priorities)
                    focus_skills.append(priorities[next_index]["skill"])
            
            week_start = start_date + timedelta(weeks=week-1)
            week_plan = self.create_week_plan(week, week_start, focus_skills, daily_hours)
            weekly_plans.append(week_plan)
        
        # Create milestones
        milestones = []
        for i, priority in enumerate(priorities[:4]):
            milestone_week = min((i + 1) * 2, duration_weeks)
            milestones.append({
                "week": milestone_week,
                "milestone": f"Complete {priority['skill']} fundamentals",
                "skill": priority["skill"],
                "assessment_required": True
            })
        
        # Add final milestone
        milestones.append({
            "week": duration_weeks,
            "milestone": "Complete full preparation - Ready for interviews!",
            "skill": "all",
            "assessment_required": True
        })
        
        # Use Gemini to enhance the roadmap with personalized advice
        enhanced_roadmap = await self.gemini.generate_roadmap(
            student_profile,
            missing_skills,
            target_role,
            duration_weeks
        )
        
        # Merge Gemini suggestions if available
        ai_suggestions = enhanced_roadmap.get("milestones", [])
        
        roadmap = {
            "roadmap_id": roadmap_id,
            "student_id": student_id,
            "target_role": target_role,
            "target_company": gap_analysis.get("company_name"),
            "duration_weeks": duration_weeks,
            "daily_commitment": daily_hours,
            "weekly_plans": weekly_plans,
            "milestones": milestones,
            "ai_suggestions": ai_suggestions,
            "skills_to_learn": [p["skill"] for p in priorities],
            "total_estimated_hours": enhanced_roadmap.get("total_hours", duration_weeks * 20),
            "progress_percentage": 0.0,
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return roadmap
    
    def update_progress(
        self,
        roadmap: Dict[str, Any],
        completed_task_id: str
    ) -> Dict[str, Any]:
        """Update roadmap progress when a task is completed"""
        
        total_tasks = 0
        completed_tasks = 0
        
        for week in roadmap.get("weekly_plans", []):
            for day in week.get("days", []):
                for task in day.get("tasks", []):
                    total_tasks += 1
                    if task.get("completed") or task["task_id"] == completed_task_id:
                        if task["task_id"] == completed_task_id:
                            task["completed"] = True
                            task["completed_at"] = datetime.utcnow().isoformat()
                        completed_tasks += 1
        
        if total_tasks > 0:
            roadmap["progress_percentage"] = round((completed_tasks / total_tasks) * 100, 2)
        
        roadmap["updated_at"] = datetime.utcnow().isoformat()
        
        return roadmap
    
    def get_todays_tasks(self, roadmap: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get tasks scheduled for today"""
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        for week in roadmap.get("weekly_plans", []):
            for day in week.get("days", []):
                if day.get("date") == today:
                    return day.get("tasks", [])
        
        # If no exact match, return first incomplete day's tasks
        for week in roadmap.get("weekly_plans", []):
            for day in week.get("days", []):
                tasks = day.get("tasks", [])
                if any(not t.get("completed") for t in tasks):
                    return tasks
        
        return []


# Singleton instance
roadmap_generator_agent = RoadmapGeneratorAgent()
