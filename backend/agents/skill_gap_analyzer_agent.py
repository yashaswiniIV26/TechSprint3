"""
Skill Gap Analyzer Agent (Brain of Velionx)
============================================
Compares student skills vs company-required skills.

Features:
- Skill ontology mapping
- Cosine similarity algorithm
- Gap severity classification
- Priority recommendations
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime
import uuid

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_ML = True
except ImportError:
    HAS_ML = False

from services.gemini_service import gemini_service


class SkillGapAnalyzerAgent:
    """Agent for analyzing skill gaps between students and job requirements"""
    
    # Skill ontology - maps related skills
    SKILL_ONTOLOGY = {
        # Programming languages (related skills)
        "python": ["data science", "machine learning", "django", "flask", "fastapi"],
        "java": ["spring", "android", "enterprise", "oop"],
        "javascript": ["react", "node.js", "angular", "vue", "typescript", "frontend"],
        "c++": ["systems programming", "competitive programming", "dsa", "game development"],
        "c": ["embedded", "systems", "operating systems"],
        
        # Web technologies
        "react": ["javascript", "frontend", "typescript", "redux", "next.js"],
        "node.js": ["javascript", "backend", "express", "api"],
        "html": ["css", "web", "frontend"],
        "css": ["html", "web", "frontend", "tailwind", "bootstrap"],
        
        # Data & ML
        "machine learning": ["python", "data science", "tensorflow", "pytorch", "numpy", "pandas"],
        "data science": ["python", "machine learning", "statistics", "sql", "visualization"],
        "sql": ["database", "postgresql", "mysql", "data analysis"],
        
        # Core CS
        "dsa": ["algorithms", "data structures", "problem solving", "competitive programming"],
        "oop": ["object oriented", "design patterns", "java", "c++", "python"],
        "system design": ["architecture", "scalability", "distributed systems", "microservices"],
        
        # Cloud & DevOps
        "aws": ["cloud", "devops", "infrastructure"],
        "docker": ["containers", "kubernetes", "devops", "microservices"],
        "kubernetes": ["containers", "docker", "devops", "orchestration"],
        
        # Soft skills
        "communication": ["presentation", "teamwork", "leadership"],
        "leadership": ["management", "teamwork", "communication"],
        "problem solving": ["analytical", "critical thinking", "dsa"],
    }
    
    # Company requirements database (sample)
    COMPANY_REQUIREMENTS = {
        "google_sde1": {
            "company_name": "Google",
            "role": "Software Development Engineer I",
            "required_skills": ["dsa", "system design", "python", "problem solving"],
            "preferred_skills": ["distributed systems", "machine learning", "go"],
            "minimum_cgpa": 7.0,
        },
        "amazon_sde1": {
            "company_name": "Amazon",
            "role": "Software Development Engineer I",
            "required_skills": ["dsa", "java", "oop", "system design"],
            "preferred_skills": ["aws", "microservices", "leadership"],
            "minimum_cgpa": 6.5,
        },
        "microsoft_sde": {
            "company_name": "Microsoft",
            "role": "Software Engineer",
            "required_skills": ["dsa", "c++", "system design", "problem solving"],
            "preferred_skills": ["azure", "distributed systems", "c#"],
            "minimum_cgpa": 7.0,
        },
        "meta_sde": {
            "company_name": "Meta",
            "role": "Software Engineer",
            "required_skills": ["dsa", "system design", "python", "react"],
            "preferred_skills": ["machine learning", "mobile development"],
            "minimum_cgpa": 7.5,
        },
        "startup_fullstack": {
            "company_name": "Tech Startup",
            "role": "Full Stack Developer",
            "required_skills": ["javascript", "react", "node.js", "sql"],
            "preferred_skills": ["typescript", "docker", "aws"],
            "minimum_cgpa": 6.0,
        },
        "tcs_developer": {
            "company_name": "TCS",
            "role": "Developer",
            "required_skills": ["java", "sql", "oop", "communication"],
            "preferred_skills": ["spring", "html", "css"],
            "minimum_cgpa": 6.0,
        },
        "infosys_se": {
            "company_name": "Infosys",
            "role": "Systems Engineer",
            "required_skills": ["java", "python", "sql", "communication"],
            "preferred_skills": ["cloud", "agile"],
            "minimum_cgpa": 6.0,
        },
        "data_scientist": {
            "company_name": "Data Company",
            "role": "Data Scientist",
            "required_skills": ["python", "machine learning", "sql", "statistics"],
            "preferred_skills": ["deep learning", "nlp", "tableau"],
            "minimum_cgpa": 7.0,
        },
    }
    
    def __init__(self):
        self.gemini = gemini_service
        if HAS_ML:
            self.vectorizer = TfidfVectorizer()
    
    def get_related_skills(self, skill: str) -> List[str]:
        """Get skills related to a given skill from ontology"""
        skill_lower = skill.lower()
        related = set()
        
        # Direct mapping
        if skill_lower in self.SKILL_ONTOLOGY:
            related.update(self.SKILL_ONTOLOGY[skill_lower])
        
        # Reverse mapping - find skills that list this skill
        for key, values in self.SKILL_ONTOLOGY.items():
            if skill_lower in [v.lower() for v in values]:
                related.add(key)
        
        return list(related)
    
    def calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills using ontology"""
        
        if skill1.lower() == skill2.lower():
            return 1.0
        
        # Check direct relationships
        related_to_1 = set(self.get_related_skills(skill1))
        related_to_2 = set(self.get_related_skills(skill2))
        
        # If either is related to the other
        if skill2.lower() in [r.lower() for r in related_to_1]:
            return 0.7
        if skill1.lower() in [r.lower() for r in related_to_2]:
            return 0.7
        
        # Check overlap in related skills
        overlap = related_to_1.intersection(related_to_2)
        if overlap:
            return 0.3 + (0.4 * len(overlap) / max(len(related_to_1), len(related_to_2), 1))
        
        return 0.0
    
    def calculate_skill_match(
        self,
        student_skills: List[str],
        required_skills: List[str]
    ) -> Tuple[List[str], List[str], float]:
        """Calculate skill match using cosine similarity and ontology"""
        
        student_skills_lower = [s.lower() for s in student_skills]
        required_skills_lower = [s.lower() for s in required_skills]
        
        matching = []
        missing = []
        
        total_match_score = 0.0
        
        for req_skill in required_skills_lower:
            best_match_score = 0.0
            best_match = None
            
            for student_skill in student_skills_lower:
                similarity = self.calculate_skill_similarity(req_skill, student_skill)
                if similarity > best_match_score:
                    best_match_score = similarity
                    best_match = student_skill
            
            if best_match_score >= 0.6:  # Threshold for considering a match
                matching.append(req_skill)
                total_match_score += best_match_score
            else:
                missing.append(req_skill)
        
        # Calculate percentage
        if required_skills:
            match_percentage = (total_match_score / len(required_skills)) * 100
        else:
            match_percentage = 100.0
        
        return matching, missing, round(match_percentage, 2)
    
    def classify_gap_severity(
        self,
        missing_skill: str,
        student_skills: List[str]
    ) -> str:
        """Classify how severe a skill gap is based on related skills"""
        
        related = self.get_related_skills(missing_skill)
        student_skills_lower = [s.lower() for s in student_skills]
        
        # Check if student has related skills
        related_coverage = sum(1 for r in related if r.lower() in student_skills_lower)
        
        if related_coverage >= 2:
            return "minor"  # Student has foundation
        elif related_coverage >= 1:
            return "moderate"  # Some related knowledge
        else:
            return "critical"  # No related skills
    
    def estimate_learning_time(self, skill: str, severity: str) -> str:
        """Estimate time needed to learn a skill"""
        
        base_times = {
            "programming_language": {"critical": "8-12 weeks", "moderate": "4-6 weeks", "minor": "2-3 weeks"},
            "framework": {"critical": "4-6 weeks", "moderate": "2-3 weeks", "minor": "1-2 weeks"},
            "concept": {"critical": "6-8 weeks", "moderate": "3-4 weeks", "minor": "1-2 weeks"},
            "soft_skill": {"critical": "8-12 weeks", "moderate": "4-6 weeks", "minor": "2-4 weeks"},
        }
        
        # Categorize skill
        programming_langs = ["python", "java", "javascript", "c++", "c", "go", "rust"]
        frameworks = ["react", "angular", "vue", "django", "spring", "node.js"]
        soft_skills = ["communication", "leadership", "teamwork", "presentation"]
        
        skill_lower = skill.lower()
        
        if skill_lower in programming_langs:
            return base_times["programming_language"][severity]
        elif skill_lower in frameworks:
            return base_times["framework"][severity]
        elif skill_lower in soft_skills:
            return base_times["soft_skill"][severity]
        else:
            return base_times["concept"][severity]
    
    async def analyze_gap(
        self,
        student_id: str,
        student_profile: Dict[str, Any],
        company_id: str = None,
        custom_requirements: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive skill gap analysis"""
        
        # Get requirements
        if custom_requirements:
            requirements = custom_requirements
        elif company_id and company_id in self.COMPANY_REQUIREMENTS:
            requirements = self.COMPANY_REQUIREMENTS[company_id]
        else:
            # Default to general SDE requirements
            requirements = self.COMPANY_REQUIREMENTS["google_sde1"]
        
        student_skills = student_profile.get("skills", []) + \
                        student_profile.get("technical_skills", []) + \
                        student_profile.get("soft_skills", [])
        
        required_skills = requirements.get("required_skills", [])
        preferred_skills = requirements.get("preferred_skills", [])
        
        # Analyze required skills
        matching, missing, match_percentage = self.calculate_skill_match(
            student_skills, required_skills
        )
        
        # Analyze preferred skills
        pref_matching, pref_missing, pref_match = self.calculate_skill_match(
            student_skills, preferred_skills
        )
        
        # Classify gaps by severity
        gap_severity = {}
        for skill in missing:
            severity = self.classify_gap_severity(skill, student_skills)
            gap_severity[skill] = severity
        
        # Prioritize skills (critical > moderate > minor)
        priority_order = {"critical": 1, "moderate": 2, "minor": 3}
        priority_skills = sorted(
            missing,
            key=lambda s: priority_order.get(gap_severity.get(s, "moderate"), 2)
        )
        
        # Estimate total preparation time
        total_weeks = 0
        for skill in missing:
            time_str = self.estimate_learning_time(skill, gap_severity[skill])
            # Extract average weeks from time string
            weeks = int(time_str.split("-")[1].split()[0])
            total_weeks += weeks
        
        # Generate recommendations
        recommendations = []
        for skill in priority_skills[:5]:
            severity = gap_severity[skill]
            time_needed = self.estimate_learning_time(skill, severity)
            related = self.get_related_skills(skill)[:3]
            
            rec = f"Learn {skill.upper()} ({severity} priority) - Est. {time_needed}"
            if related:
                rec += f". Build on your knowledge of: {', '.join(related)}"
            recommendations.append(rec)
        
        analysis_id = str(uuid.uuid4())
        
        return {
            "analysis_id": analysis_id,
            "student_id": student_id,
            "company_id": company_id,
            "company_name": requirements.get("company_name", "Unknown"),
            "target_role": requirements.get("role", "Software Engineer"),
            "matching_skills": matching,
            "missing_skills": missing,
            "skill_match_percentage": match_percentage,
            "preferred_matching": pref_matching,
            "preferred_missing": pref_missing,
            "preferred_match_percentage": pref_match,
            "gap_severity": gap_severity,
            "priority_skills": priority_skills,
            "recommendations": recommendations,
            "estimated_preparation_time": f"{total_weeks} weeks" if total_weeks > 0 else "Ready!",
            "cgpa_requirement": requirements.get("minimum_cgpa"),
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    def get_available_companies(self) -> List[Dict[str, str]]:
        """Get list of available companies for analysis"""
        return [
            {
                "id": cid,
                "company_name": data["company_name"],
                "role": data["role"]
            }
            for cid, data in self.COMPANY_REQUIREMENTS.items()
        ]
    
    async def batch_analyze(
        self,
        student_id: str,
        student_profile: Dict[str, Any],
        company_ids: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Analyze gaps for multiple companies"""
        
        if company_ids is None:
            company_ids = list(self.COMPANY_REQUIREMENTS.keys())
        
        analyses = []
        for cid in company_ids:
            if cid in self.COMPANY_REQUIREMENTS:
                analysis = await self.analyze_gap(student_id, student_profile, cid)
                analyses.append(analysis)
        
        # Sort by match percentage (best matches first)
        analyses.sort(key=lambda x: x["skill_match_percentage"], reverse=True)
        
        return analyses


# Singleton instance
skill_gap_analyzer_agent = SkillGapAnalyzerAgent()
