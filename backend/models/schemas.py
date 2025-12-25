from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CommunicationLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SkillCategory(str, Enum):
    TECHNICAL = "technical"
    APTITUDE = "aptitude"
    SOFT_SKILLS = "soft_skills"
    DOMAIN = "domain"


# ============ Student Profile Models ============

class StudentBase(BaseModel):
    email: str
    name: str
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None


class StudentCreate(StudentBase):
    password: str


class StudentProfile(BaseModel):
    student_id: str
    name: str
    email: str
    skills: List[str] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    communication: CommunicationLevel = CommunicationLevel.MEDIUM
    job_interest: List[str] = []
    preferred_roles: List[str] = []
    academic_marks: Optional[Dict[str, float]] = None
    coding_scores: Optional[Dict[str, float]] = None
    aptitude_scores: Optional[Dict[str, float]] = None
    readiness_score: float = 0.0
    resume_parsed: bool = False
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ResumeParseResponse(BaseModel):
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    certifications: List[str]
    contact_info: Dict[str, str]


# ============ Skill Assessment Models ============

class Question(BaseModel):
    question_id: str
    question_text: str
    question_type: str  # mcq, coding, descriptive
    skill_tags: List[str]
    difficulty: DifficultyLevel
    category: SkillCategory
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    time_limit_seconds: int = 60
    points: int = 10


class QuestionResponse(BaseModel):
    question_id: str
    student_answer: str
    time_taken_seconds: int


class AssessmentResult(BaseModel):
    assessment_id: str
    student_id: str
    category: SkillCategory
    total_questions: int
    correct_answers: int
    score: float
    skill_scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    skill_gap_score: float
    feedback: str
    completed_at: datetime


class AdaptiveTestState(BaseModel):
    current_difficulty: DifficultyLevel
    questions_answered: int
    consecutive_correct: int
    consecutive_wrong: int
    skill_performance: Dict[str, Dict[str, float]]


# ============ Skill Gap Analyzer Models ============

class CompanyRequirement(BaseModel):
    company_id: str
    company_name: str
    role: str
    required_skills: List[str]
    preferred_skills: List[str]
    minimum_cgpa: Optional[float] = None
    experience_required: Optional[str] = None


class SkillGapAnalysis(BaseModel):
    student_id: str
    company_id: str
    matching_skills: List[str]
    missing_skills: List[str]
    skill_match_percentage: float
    gap_severity: Dict[str, str]  # skill -> severity (critical, moderate, minor)
    recommendations: List[str]
    estimated_preparation_time: str
    priority_skills: List[str]


# ============ Roadmap Generator Models ============

class LearningTask(BaseModel):
    task_id: str
    title: str
    description: str
    skill_target: str
    duration_hours: float
    resources: List[Dict[str, str]]  # {type, title, url}
    priority: int
    completed: bool = False


class DayPlan(BaseModel):
    day: int
    date: str
    tasks: List[LearningTask]
    total_hours: float
    focus_skills: List[str]


class WeekPlan(BaseModel):
    week: int
    days: List[DayPlan]
    weekly_goals: List[str]
    assessment_scheduled: bool


class PersonalizedRoadmap(BaseModel):
    roadmap_id: str
    student_id: str
    target_role: str
    target_company: Optional[str] = None
    duration_weeks: int
    weekly_plans: List[WeekPlan]
    milestones: List[Dict[str, Any]]
    progress_percentage: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============ Interview Coach Models ============

class InterviewType(str, Enum):
    TECHNICAL = "technical"
    HR = "hr"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"


class InterviewSession(BaseModel):
    session_id: str
    student_id: str
    interview_type: InterviewType
    language: str = "en"  # Support regional languages
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    status: str = "active"  # active, completed, paused
    started_at: datetime
    ended_at: Optional[datetime] = None


class InterviewMessage(BaseModel):
    role: str  # interviewer, candidate
    content: str
    timestamp: datetime
    audio_url: Optional[str] = None


class InterviewFeedback(BaseModel):
    session_id: str
    overall_score: float
    confidence_score: float
    communication_score: float
    technical_accuracy: float
    clarity_score: float
    body_language_notes: Optional[str] = None
    strengths: List[str]
    improvements: List[str]
    detailed_feedback: str
    question_wise_feedback: List[Dict[str, Any]]


# ============ Digital Twin Models ============

class DigitalTwinProfile(BaseModel):
    twin_id: str
    student_id: str
    learning_patterns: Dict[str, Any]
    performance_history: List[Dict[str, Any]]
    predicted_weaknesses: List[Dict[str, Any]]
    success_probability: Dict[str, float]  # company -> probability
    recommendations: List[str]
    last_updated: datetime


class PredictionResult(BaseModel):
    target: str  # e.g., "Google Round 2"
    success_probability: float
    risk_factors: List[str]
    improvement_areas: List[str]
    corrective_actions: List[Dict[str, Any]]
    confidence_level: float


class LearningEvent(BaseModel):
    event_type: str  # assessment, interview, coding_submission, resource_completion
    timestamp: datetime
    skill_involved: List[str]
    performance_score: Optional[float] = None
    time_spent_minutes: Optional[int] = None
    metadata: Dict[str, Any] = {}


# ============ Auth Models ============

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    student_id: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str
