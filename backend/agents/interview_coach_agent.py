"""
AI Interview Coach Agent (Key Differentiator)
===============================================
Conducts mock interviews with real-time feedback.

Features:
- Voice-based interviews
- Speech-to-text processing
- LLM-powered interviewer
- Real-time feedback
- Regional language support
- Confidence scoring
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json

from services.gemini_service import gemini_service
from models.schemas import InterviewType


class InterviewCoachAgent:
    """Agent for conducting AI-powered mock interviews"""
    
    # Supported languages for regional support
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "mr": "Marathi",
        "bn": "Bengali",
        "gu": "Gujarati",
        "pa": "Punjabi",
    }
    
    # Interview question templates by type
    INTERVIEW_TEMPLATES = {
        "technical": {
            "intro": "Let's begin the technical interview. I'll ask you questions about data structures, algorithms, and programming concepts.",
            "categories": ["dsa", "programming", "system_concepts"],
            "duration_minutes": 45,
        },
        "hr": {
            "intro": "Welcome to the HR round. I'll be asking about your background, experiences, and how you handle various situations.",
            "categories": ["background", "behavioral", "motivation"],
            "duration_minutes": 30,
        },
        "behavioral": {
            "intro": "This is a behavioral interview. I'll ask about specific situations from your past and how you handled them.",
            "categories": ["teamwork", "leadership", "conflict", "achievement"],
            "duration_minutes": 30,
        },
        "system_design": {
            "intro": "Welcome to the system design interview. We'll discuss how to design scalable systems.",
            "categories": ["design", "scalability", "trade-offs"],
            "duration_minutes": 45,
        },
    }
    
    # Sample questions by category
    QUESTION_BANK = {
        "dsa": [
            "Explain the difference between a stack and a queue. When would you use each?",
            "What is the time complexity of binary search? How does it work?",
            "Can you explain what a hash table is and how collision resolution works?",
            "Describe different sorting algorithms and their time complexities.",
            "What is dynamic programming? Can you give an example?",
            "Explain the concept of recursion and when you would use it.",
        ],
        "programming": [
            "What are the principles of Object-Oriented Programming?",
            "Explain the difference between compiled and interpreted languages.",
            "What is a REST API? What are the HTTP methods?",
            "Explain the concept of multithreading and its challenges.",
            "What is the difference between a process and a thread?",
        ],
        "background": [
            "Tell me about yourself and your educational background.",
            "What are your greatest strengths and weaknesses?",
            "Why are you interested in this role?",
            "Where do you see yourself in 5 years?",
            "What do you know about our company?",
        ],
        "behavioral": [
            "Tell me about a time when you faced a difficult challenge. How did you overcome it?",
            "Describe a situation where you had to work with a difficult team member.",
            "Give an example of when you showed leadership.",
            "Tell me about a project you're most proud of.",
            "How do you handle tight deadlines and pressure?",
        ],
        "teamwork": [
            "Describe your experience working in a team.",
            "How do you handle disagreements with team members?",
            "Tell me about a successful team project you worked on.",
        ],
        "design": [
            "How would you design a URL shortening service like bit.ly?",
            "Design a chat application like WhatsApp.",
            "How would you design Twitter's trending topics feature?",
            "Design a rate limiter for an API.",
        ],
    }
    
    def __init__(self):
        self.gemini = gemini_service
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def start_interview(
        self,
        student_id: str,
        interview_type: InterviewType,
        language: str = "en",
        target_company: Optional[str] = None,
        target_role: Optional[str] = None,
        student_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start a new interview session"""
        
        session_id = str(uuid.uuid4())
        
        template = self.INTERVIEW_TEMPLATES.get(interview_type.value, self.INTERVIEW_TEMPLATES["technical"])
        
        session = {
            "session_id": session_id,
            "student_id": student_id,
            "interview_type": interview_type.value,
            "language": language,
            "target_company": target_company,
            "target_role": target_role or "Software Engineer",
            "student_profile": student_profile or {},
            "status": "active",
            "started_at": datetime.utcnow().isoformat(),
            "messages": [],
            "questions_asked": [],
            "current_question_index": 0,
            "evaluations": [],
            "duration_minutes": template["duration_minutes"],
        }
        
        # Generate opening message
        opening = await self._generate_opening(session)
        session["messages"].append({
            "role": "interviewer",
            "content": opening,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Store session
        self.active_sessions[session_id] = session
        
        return {
            "session_id": session_id,
            "interview_type": interview_type.value,
            "language": language,
            "opening_message": opening,
            "status": "active",
            "estimated_duration": template["duration_minutes"]
        }
    
    async def _generate_opening(self, session: Dict[str, Any]) -> str:
        """Generate personalized opening for the interview"""
        
        student_name = session.get("student_profile", {}).get("name", "candidate")
        interview_type = session["interview_type"]
        company = session.get("target_company", "the company")
        role = session.get("target_role", "Software Engineer")
        
        template = self.INTERVIEW_TEMPLATES.get(interview_type, {})
        intro = template.get("intro", "Let's begin the interview.")
        
        opening = f"""Hello {student_name}! Welcome to this mock {interview_type} interview.

{intro}

I'll be your interviewer today. We have about {template.get('duration_minutes', 30)} minutes for this session.

Please feel free to ask clarifying questions, and think out loud as you work through problems.

Let's start with a warm-up: {await self._get_next_question(session)}"""
        
        return opening
    
    async def _get_next_question(self, session: Dict[str, Any]) -> str:
        """Get the next interview question"""
        
        interview_type = session["interview_type"]
        template = self.INTERVIEW_TEMPLATES.get(interview_type, {})
        categories = template.get("categories", ["background"])
        
        # Get questions from relevant categories
        available_questions = []
        for cat in categories:
            available_questions.extend(self.QUESTION_BANK.get(cat, []))
        
        # Filter out already asked questions
        asked = session.get("questions_asked", [])
        remaining = [q for q in available_questions if q not in asked]
        
        if remaining:
            import random
            question = random.choice(remaining)
            session["questions_asked"].append(question)
            return question
        
        # If no questions left, generate with AI
        return await self._generate_ai_question(session)
    
    async def _generate_ai_question(self, session: Dict[str, Any]) -> str:
        """Generate a new question using AI"""
        
        response = await self.gemini.generate_interview_question(
            session["interview_type"],
            session.get("student_profile", {}).get("skills", []),
            "medium",
            session.get("questions_asked", []),
            session.get("student_profile", {})
        )
        
        return response.get("question", "Tell me about your experience with programming.")
    
    async def submit_response(
        self,
        session_id: str,
        response_text: str,
        audio_transcript: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit candidate's response and get feedback"""
        
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        if session["status"] != "active":
            return {"error": "Session is not active"}
        
        # Use audio transcript if provided, otherwise use text
        answer = audio_transcript or response_text
        
        # Get the last question asked
        last_question = session["questions_asked"][-1] if session["questions_asked"] else ""
        
        # Record the response
        session["messages"].append({
            "role": "candidate",
            "content": answer,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Evaluate the response
        evaluation = await self.gemini.evaluate_interview_response(
            last_question,
            answer,
            [],  # Expected points - could be enhanced
            session["interview_type"]
        )
        
        session["evaluations"].append({
            "question": last_question,
            "answer": answer,
            "evaluation": evaluation,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Generate follow-up or next question
        session["current_question_index"] += 1
        
        # Check if interview should end
        if session["current_question_index"] >= 5:  # 5 questions per session
            return await self.end_interview(session_id)
        
        # Generate interviewer response
        follow_up = await self._generate_follow_up(session, evaluation)
        next_question = await self._get_next_question(session)
        
        interviewer_response = f"{follow_up}\n\n{next_question}"
        
        session["messages"].append({
            "role": "interviewer",
            "content": interviewer_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "session_id": session_id,
            "evaluation": {
                "score": evaluation.get("score", 5),
                "brief_feedback": evaluation.get("feedback", "")[:200],
                "communication_clarity": evaluation.get("communication_clarity", 5)
            },
            "interviewer_response": interviewer_response,
            "questions_remaining": 5 - session["current_question_index"],
            "status": "active"
        }
    
    async def _generate_follow_up(
        self,
        session: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> str:
        """Generate appropriate follow-up based on evaluation"""
        
        score = evaluation.get("score", 5)
        
        if score >= 8:
            responses = [
                "Excellent answer! I can see you have a strong understanding.",
                "Very well explained. That's a comprehensive answer.",
                "Great job! You covered all the key points.",
            ]
        elif score >= 6:
            responses = [
                "Good answer. Let me ask you a follow-up question.",
                "That's a decent response. Let's explore another topic.",
                "Okay, you've covered the basics. Let's move on.",
            ]
        else:
            improvements = evaluation.get("improvements", [])
            improvement_text = improvements[0] if improvements else "consider providing more details"
            responses = [
                f"I see. For future reference, you might want to {improvement_text}. Let's continue.",
                f"That's a start. Remember to {improvement_text}. Moving on to the next question.",
            ]
        
        import random
        return random.choice(responses)
    
    async def end_interview(self, session_id: str) -> Dict[str, Any]:
        """End the interview and generate comprehensive feedback"""
        
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        session["status"] = "completed"
        session["ended_at"] = datetime.utcnow().isoformat()
        
        # Calculate overall scores
        evaluations = session.get("evaluations", [])
        
        if evaluations:
            avg_score = sum(e.get("evaluation", {}).get("score", 5) for e in evaluations) / len(evaluations)
            avg_communication = sum(e.get("evaluation", {}).get("communication_clarity", 5) for e in evaluations) / len(evaluations)
            avg_technical = sum(e.get("evaluation", {}).get("technical_accuracy", 5) for e in evaluations) / len(evaluations)
        else:
            avg_score = 5
            avg_communication = 5
            avg_technical = 5
        
        # Aggregate strengths and improvements
        all_strengths = []
        all_improvements = []
        for e in evaluations:
            eval_data = e.get("evaluation", {})
            all_strengths.extend(eval_data.get("strengths", []))
            all_improvements.extend(eval_data.get("improvements", []))
        
        # Deduplicate
        strengths = list(set(all_strengths))[:5]
        improvements = list(set(all_improvements))[:5]
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(evaluations)
        
        # Generate detailed feedback
        detailed_feedback = await self._generate_detailed_feedback(session, {
            "avg_score": avg_score,
            "confidence_score": confidence_score,
            "communication_score": avg_communication,
            "technical_score": avg_technical,
            "strengths": strengths,
            "improvements": improvements
        })
        
        feedback = {
            "session_id": session_id,
            "overall_score": round(avg_score, 1),
            "confidence_score": round(confidence_score, 1),
            "communication_score": round(avg_communication, 1),
            "technical_accuracy": round(avg_technical, 1),
            "clarity_score": round(avg_communication, 1),
            "strengths": strengths,
            "improvements": improvements,
            "detailed_feedback": detailed_feedback,
            "question_wise_feedback": [
                {
                    "question": e.get("question", ""),
                    "score": e.get("evaluation", {}).get("score", 5),
                    "feedback": e.get("evaluation", {}).get("feedback", "")
                }
                for e in evaluations
            ],
            "interview_duration_minutes": self._calculate_duration(session),
            "completed_at": session["ended_at"]
        }
        
        session["final_feedback"] = feedback
        
        # Generate closing message
        closing = self._generate_closing_message(feedback)
        session["messages"].append({
            "role": "interviewer",
            "content": closing,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "session_id": session_id,
            "status": "completed",
            "closing_message": closing,
            "feedback": feedback
        }
    
    def _calculate_confidence_score(self, evaluations: List[Dict]) -> float:
        """Calculate confidence score based on response patterns"""
        
        if not evaluations:
            return 5.0
        
        # Factors: consistency of scores, communication clarity
        scores = [e.get("evaluation", {}).get("score", 5) for e in evaluations]
        comm_scores = [e.get("evaluation", {}).get("communication_clarity", 5) for e in evaluations]
        
        avg_score = sum(scores) / len(scores)
        avg_comm = sum(comm_scores) / len(comm_scores)
        
        # Confidence is weighted average of overall performance and communication
        confidence = (avg_score * 0.6 + avg_comm * 0.4)
        
        return min(max(confidence, 1), 10)  # Clamp between 1 and 10
    
    def _calculate_duration(self, session: Dict[str, Any]) -> int:
        """Calculate interview duration in minutes"""
        
        started = datetime.fromisoformat(session["started_at"])
        ended = datetime.fromisoformat(session.get("ended_at", datetime.utcnow().isoformat()))
        
        return int((ended - started).total_seconds() / 60)
    
    async def _generate_detailed_feedback(
        self,
        session: Dict[str, Any],
        scores: Dict[str, Any]
    ) -> str:
        """Generate detailed personalized feedback"""
        
        prompt = f"""
        Generate detailed interview feedback for a candidate.
        
        Interview Type: {session['interview_type']}
        Overall Score: {scores['avg_score']}/10
        Communication: {scores['communication_score']}/10
        Technical Accuracy: {scores['technical_score']}/10
        Confidence: {scores['confidence_score']}/10
        
        Strengths identified: {scores['strengths']}
        Areas for improvement: {scores['improvements']}
        
        Generate a 150-word personalized feedback covering:
        1. Overall performance summary
        2. Key strengths to leverage
        3. Specific areas to improve
        4. Actionable tips for next interview
        
        Be encouraging but honest.
        """
        
        feedback = await self.gemini.generate_response(prompt)
        return feedback
    
    def _generate_closing_message(self, feedback: Dict[str, Any]) -> str:
        """Generate closing message based on performance"""
        
        score = feedback.get("overall_score", 5)
        
        if score >= 8:
            closing = """🎉 Excellent performance! You've demonstrated strong skills and confidence throughout this interview.

Your scores:
- Overall: {}/10
- Communication: {}/10
- Technical: {}/10
- Confidence: {}/10

You're well-prepared for real interviews. Keep practicing to maintain this level!"""
        elif score >= 6:
            closing = """👍 Good job! You've shown solid fundamentals with room for improvement.

Your scores:
- Overall: {}/10
- Communication: {}/10
- Technical: {}/10
- Confidence: {}/10

Focus on the improvement areas highlighted in your feedback, and you'll do great!"""
        else:
            closing = """📚 This was a learning experience! Don't be discouraged - everyone improves with practice.

Your scores:
- Overall: {}/10
- Communication: {}/10
- Technical: {}/10
- Confidence: {}/10

Review the feedback carefully, practice the weak areas, and try another mock interview soon!"""
        
        return closing.format(
            feedback.get("overall_score", 5),
            feedback.get("communication_score", 5),
            feedback.get("technical_accuracy", 5),
            feedback.get("confidence_score", 5)
        )
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session details"""
        return self.active_sessions.get(session_id)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES


# Singleton instance
interview_coach_agent = InterviewCoachAgent()
