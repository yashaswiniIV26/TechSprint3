import google.generativeai as genai
from typing import Optional, List, Dict, Any
from config import settings


class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a response from Gemini"""
        if not self.model:
            return "AI service not configured. Please set GOOGLE_API_KEY."
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume and extract structured information"""
        prompt = f"""
        Analyze the following resume and extract structured information.
        Return a JSON object with the following structure:
        {{
            "skills": ["skill1", "skill2", ...],
            "technical_skills": ["tech1", "tech2", ...],
            "soft_skills": ["soft1", "soft2", ...],
            "experience": [
                {{"company": "...", "role": "...", "duration": "...", "description": "..."}}
            ],
            "education": [
                {{"institution": "...", "degree": "...", "year": "...", "gpa": "..."}}
            ],
            "projects": [
                {{"name": "...", "description": "...", "technologies": ["..."]}}
            ],
            "certifications": ["cert1", "cert2", ...],
            "contact": {{"email": "...", "phone": "...", "linkedin": "..."}}
        }}
        
        Resume:
        {resume_text}
        
        Return ONLY the JSON object, no additional text.
        """
        
        response = await self.generate_response(prompt)
        try:
            import json
            # Clean up response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            return json.loads(response.strip())
        except:
            return {"skills": [], "experience": [], "education": [], "projects": [], "certifications": [], "contact": {}}

    async def generate_interview_question(
        self,
        interview_type: str,
        skill_focus: List[str],
        difficulty: str,
        previous_questions: List[str],
        student_profile: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate an interview question based on context"""
        prompt = f"""
        You are an expert interviewer. Generate ONE interview question.
        
        Interview Type: {interview_type}
        Skills to focus on: {', '.join(skill_focus)}
        Difficulty: {difficulty}
        Student's skills: {student_profile.get('skills', [])}
        Target role: {student_profile.get('job_interest', 'Software Engineer')}
        
        Previous questions asked (avoid repetition):
        {chr(10).join(previous_questions[-5:]) if previous_questions else 'None'}
        
        Return a JSON object:
        {{
            "question": "Your interview question here",
            "expected_points": ["key point 1", "key point 2"],
            "difficulty": "{difficulty}",
            "skill_tested": "primary skill being tested"
        }}
        
        Return ONLY the JSON object.
        """
        
        response = await self.generate_response(prompt)
        try:
            import json
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response.strip())
        except:
            return {
                "question": "Tell me about a challenging project you worked on.",
                "expected_points": ["Problem description", "Solution approach", "Outcome"],
                "difficulty": difficulty,
                "skill_tested": "general"
            }

    async def evaluate_interview_response(
        self,
        question: str,
        answer: str,
        expected_points: List[str],
        skill_tested: str
    ) -> Dict[str, Any]:
        """Evaluate a candidate's interview response"""
        prompt = f"""
        Evaluate this interview response:
        
        Question: {question}
        Answer: {answer}
        Expected Key Points: {', '.join(expected_points)}
        Skill Being Tested: {skill_tested}
        
        Provide evaluation as JSON:
        {{
            "score": 0-10,
            "technical_accuracy": 0-10,
            "communication_clarity": 0-10,
            "completeness": 0-10,
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"],
            "feedback": "Detailed feedback for the candidate"
        }}
        
        Return ONLY the JSON object.
        """
        
        response = await self.generate_response(prompt)
        try:
            import json
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response.strip())
        except:
            return {
                "score": 5,
                "technical_accuracy": 5,
                "communication_clarity": 5,
                "completeness": 5,
                "strengths": [],
                "improvements": ["Could not evaluate response"],
                "feedback": "Unable to process evaluation"
            }

    async def generate_roadmap(
        self,
        student_profile: Dict[str, Any],
        missing_skills: List[str],
        target_role: str,
        duration_weeks: int
    ) -> Dict[str, Any]:
        """Generate a personalized learning roadmap"""
        prompt = f"""
        Create a detailed {duration_weeks}-week learning roadmap for a student.
        
        Student Profile:
        - Current Skills: {student_profile.get('skills', [])}
        - Communication Level: {student_profile.get('communication', 'medium')}
        - Readiness Score: {student_profile.get('readiness_score', 50)}
        
        Skills to Learn: {missing_skills}
        Target Role: {target_role}
        
        Create a structured weekly plan with daily tasks.
        Return as JSON:
        {{
            "weekly_plans": [
                {{
                    "week": 1,
                    "theme": "Week theme",
                    "goals": ["goal1", "goal2"],
                    "daily_plans": [
                        {{
                            "day": 1,
                            "tasks": [
                                {{
                                    "title": "Task title",
                                    "description": "What to do",
                                    "duration_hours": 2,
                                    "skill_target": "skill name",
                                    "resources": [
                                        {{"type": "video", "title": "Resource name", "url": "example.com"}}
                                    ]
                                }}
                            ]
                        }}
                    ]
                }}
            ],
            "milestones": [
                {{"week": 2, "milestone": "Complete Java basics", "assessment": true}}
            ],
            "total_hours": 100,
            "daily_commitment_hours": 3
        }}
        
        Return ONLY the JSON object.
        """
        
        response = await self.generate_response(prompt)
        try:
            import json
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response.strip())
        except Exception as e:
            return {
                "weekly_plans": [],
                "milestones": [],
                "total_hours": duration_weeks * 20,
                "daily_commitment_hours": 3,
                "error": str(e)
            }

    async def generate_assessment_feedback(
        self,
        skill: str,
        score: float,
        answers: List[Dict[str, Any]]
    ) -> str:
        """Generate detailed feedback for assessment performance"""
        prompt = f"""
        Generate constructive feedback for a student's assessment.
        
        Skill Assessed: {skill}
        Score: {score}%
        
        Question-Answer Summary:
        {answers[:5]}  # Limit to first 5 for context
        
        Provide:
        1. What they did well
        2. Areas for improvement
        3. Specific resources or topics to study
        4. Practice recommendations
        
        Keep feedback encouraging but honest. Maximum 200 words.
        """
        
        return await self.generate_response(prompt)

    async def predict_success_probability(
        self,
        student_profile: Dict[str, Any],
        company_requirements: Dict[str, Any],
        historical_performance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict success probability for a company/role"""
        prompt = f"""
        Analyze this student's chance of success:
        
        Student Profile:
        - Skills: {student_profile.get('skills', [])}
        - Readiness Score: {student_profile.get('readiness_score', 50)}
        - Communication: {student_profile.get('communication', 'medium')}
        
        Company Requirements:
        - Required Skills: {company_requirements.get('required_skills', [])}
        - Role: {company_requirements.get('role', 'Software Engineer')}
        
        Recent Performance History:
        {historical_performance[-5:] if historical_performance else 'No history'}
        
        Return JSON:
        {{
            "success_probability": 0.0-1.0,
            "confidence_level": 0.0-1.0,
            "risk_factors": ["risk1", "risk2"],
            "strengths_for_role": ["strength1", "strength2"],
            "critical_gaps": ["gap1", "gap2"],
            "recommended_actions": [
                {{"action": "description", "priority": "high/medium/low", "expected_impact": "description"}}
            ],
            "timeline_to_readiness": "X weeks"
        }}
        
        Return ONLY the JSON object.
        """
        
        response = await self.generate_response(prompt)
        try:
            import json
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response.strip())
        except:
            return {
                "success_probability": 0.5,
                "confidence_level": 0.3,
                "risk_factors": ["Insufficient data"],
                "strengths_for_role": [],
                "critical_gaps": [],
                "recommended_actions": [],
                "timeline_to_readiness": "Unknown"
            }


# Singleton instance
gemini_service = GeminiService()
