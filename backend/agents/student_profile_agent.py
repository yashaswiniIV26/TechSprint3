"""
Student Profile & Data Agent (Base Layer)
==========================================
Collects and maintains student intelligence profiles.

Features:
- Resume parsing with spaCy
- Skill extraction and categorization
- Readiness score calculation
- Profile aggregation from multiple sources
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Try importing spaCy - will work after installation
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

from services.gemini_service import gemini_service


class StudentProfileAgent:
    """Agent for managing student profiles and data extraction"""
    
    # Skill categories for classification
    TECHNICAL_SKILLS = {
        "programming": ["python", "java", "javascript", "c++", "c", "go", "rust", "typescript", "ruby", "php", "swift", "kotlin"],
        "web": ["html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi", "next.js"],
        "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "firebase", "oracle", "cassandra"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins"],
        "data_science": ["machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"],
        "dsa": ["data structures", "algorithms", "dsa", "dynamic programming", "graphs", "trees", "sorting", "searching"],
        "system_design": ["system design", "microservices", "api design", "scalability", "distributed systems"],
        "mobile": ["android", "ios", "react native", "flutter", "swift", "kotlin"],
    }
    
    SOFT_SKILLS = [
        "communication", "leadership", "teamwork", "problem solving", "critical thinking",
        "time management", "adaptability", "creativity", "collaboration", "presentation"
    ]
    
    def __init__(self):
        self.gemini = gemini_service
    
    async def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text and extract structured information"""
        
        # Use Gemini for comprehensive parsing
        parsed_data = await self.gemini.analyze_resume(resume_text)
        
        # Enhance with local NLP if available
        if nlp:
            doc = nlp(resume_text.lower())
            
            # Extract additional skills using pattern matching
            local_skills = self._extract_skills_from_text(resume_text.lower())
            
            # Merge skills
            all_skills = set(parsed_data.get("skills", []))
            all_skills.update(local_skills)
            parsed_data["skills"] = list(all_skills)
            
            # Extract entities
            entities = self._extract_entities(doc)
            parsed_data["entities"] = entities
        
        return parsed_data
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills using pattern matching"""
        found_skills = []
        
        # Check for technical skills
        for category, skills in self.TECHNICAL_SKILLS.items():
            for skill in skills:
                if skill.lower() in text:
                    found_skills.append(skill)
        
        # Check for soft skills
        for skill in self.SOFT_SKILLS:
            if skill.lower() in text:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """Extract named entities from spaCy doc"""
        entities = {
            "organizations": [],
            "dates": [],
            "locations": [],
            "education": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:
                entities["locations"].append(ent.text)
        
        return entities
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into technical and soft skills"""
        technical = []
        soft = []
        other = []
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Check if technical
            is_technical = False
            for category, tech_skills in self.TECHNICAL_SKILLS.items():
                if any(ts in skill_lower for ts in tech_skills):
                    technical.append(skill)
                    is_technical = True
                    break
            
            if not is_technical:
                # Check if soft skill
                if any(ss in skill_lower for ss in self.SOFT_SKILLS):
                    soft.append(skill)
                else:
                    other.append(skill)
        
        return {
            "technical": technical,
            "soft": soft,
            "other": other
        }
    
    def calculate_readiness_score(self, profile: Dict[str, Any]) -> float:
        """
        Calculate overall placement readiness score (0-100)
        
        Factors:
        - Technical skills coverage (30%)
        - Soft skills (15%)
        - Coding test scores (20%)
        - Aptitude scores (15%)
        - Communication level (10%)
        - Academic marks (10%)
        """
        score = 0.0
        
        # Technical skills (30%)
        tech_skills = profile.get("technical_skills", [])
        tech_score = min(len(tech_skills) * 5, 30)  # 5 points per skill, max 30
        score += tech_score
        
        # Soft skills (15%)
        soft_skills = profile.get("soft_skills", [])
        soft_score = min(len(soft_skills) * 3, 15)  # 3 points per skill, max 15
        score += soft_score
        
        # Coding scores (20%)
        coding_scores = profile.get("coding_scores", {})
        if coding_scores:
            avg_coding = sum(coding_scores.values()) / len(coding_scores)
            score += (avg_coding / 100) * 20
        
        # Aptitude scores (15%)
        aptitude_scores = profile.get("aptitude_scores", {})
        if aptitude_scores:
            avg_aptitude = sum(aptitude_scores.values()) / len(aptitude_scores)
            score += (avg_aptitude / 100) * 15
        
        # Communication level (10%)
        comm_levels = {"low": 3, "medium": 7, "high": 10}
        comm_level = profile.get("communication", "medium")
        score += comm_levels.get(comm_level, 5)
        
        # Academic marks (10%)
        academic = profile.get("academic_marks", {})
        if academic:
            cgpa = academic.get("cgpa", 0)
            if cgpa > 0:
                # Assuming CGPA out of 10
                score += (cgpa / 10) * 10
        
        return min(round(score, 2), 100)
    
    async def create_student_profile(
        self,
        student_id: str,
        name: str,
        email: str,
        resume_text: Optional[str] = None,
        selected_skills: List[str] = None,
        coding_scores: Dict[str, float] = None,
        aptitude_scores: Dict[str, float] = None,
        communication_level: str = "medium",
        academic_marks: Dict[str, float] = None,
        preferred_roles: List[str] = None
    ) -> Dict[str, Any]:
        """Create a comprehensive student profile"""
        
        profile = {
            "student_id": student_id,
            "name": name,
            "email": email,
            "skills": selected_skills or [],
            "technical_skills": [],
            "soft_skills": [],
            "communication": communication_level,
            "job_interest": preferred_roles or [],
            "preferred_roles": preferred_roles or [],
            "coding_scores": coding_scores or {},
            "aptitude_scores": aptitude_scores or {},
            "academic_marks": academic_marks or {},
            "resume_parsed": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Parse resume if provided
        if resume_text:
            parsed = await self.parse_resume(resume_text)
            profile["resume_parsed"] = True
            
            # Merge skills
            all_skills = set(profile["skills"])
            all_skills.update(parsed.get("skills", []))
            profile["skills"] = list(all_skills)
            
            # Add parsed data
            profile["experience"] = parsed.get("experience", [])
            profile["education"] = parsed.get("education", [])
            profile["projects"] = parsed.get("projects", [])
            profile["certifications"] = parsed.get("certifications", [])
        
        # Categorize skills
        categorized = self.categorize_skills(profile["skills"])
        profile["technical_skills"] = categorized["technical"]
        profile["soft_skills"] = categorized["soft"]
        
        # Calculate readiness score
        profile["readiness_score"] = self.calculate_readiness_score(profile)
        
        return profile
    
    async def update_profile_from_assessment(
        self,
        profile: Dict[str, Any],
        assessment_type: str,
        scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Update profile based on assessment results"""
        
        if assessment_type == "coding":
            profile["coding_scores"] = {
                **profile.get("coding_scores", {}),
                **scores
            }
        elif assessment_type == "aptitude":
            profile["aptitude_scores"] = {
                **profile.get("aptitude_scores", {}),
                **scores
            }
        elif assessment_type == "communication":
            # Calculate communication level from score
            avg_score = sum(scores.values()) / len(scores) if scores else 50
            if avg_score >= 70:
                profile["communication"] = "high"
            elif avg_score >= 40:
                profile["communication"] = "medium"
            else:
                profile["communication"] = "low"
        
        # Recalculate readiness score
        profile["readiness_score"] = self.calculate_readiness_score(profile)
        profile["updated_at"] = datetime.utcnow().isoformat()
        
        return profile
    
    def get_profile_summary(self, profile: Dict[str, Any]) -> str:
        """Generate a human-readable profile summary"""
        summary = f"""
Student Profile Summary
=======================
Name: {profile.get('name', 'N/A')}
Readiness Score: {profile.get('readiness_score', 0)}/100

Technical Skills: {', '.join(profile.get('technical_skills', [])[:10]) or 'None listed'}
Soft Skills: {', '.join(profile.get('soft_skills', [])[:5]) or 'None listed'}
Communication Level: {profile.get('communication', 'Not assessed')}

Target Roles: {', '.join(profile.get('preferred_roles', [])[:3]) or 'Not specified'}

Assessment Status:
- Coding Tests: {'Completed' if profile.get('coding_scores') else 'Pending'}
- Aptitude Tests: {'Completed' if profile.get('aptitude_scores') else 'Pending'}
- Resume: {'Parsed' if profile.get('resume_parsed') else 'Not uploaded'}
"""
        return summary.strip()


# Singleton instance
student_profile_agent = StudentProfileAgent()
