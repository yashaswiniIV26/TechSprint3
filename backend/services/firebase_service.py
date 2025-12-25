"""
Firebase Service - With In-Memory Fallback for Testing
Automatically uses in-memory storage if Firebase is not configured.
"""

from typing import Optional, Dict, List
import os
from datetime import datetime
import json

# Try to import Firebase, but don't fail if not available
FIREBASE_AVAILABLE = False
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    print("Firebase Admin SDK not available, using in-memory storage")

try:
    from config import settings
except:
    settings = None


class InMemoryStorage:
    """Simple in-memory storage for testing without Firebase"""
    
    def __init__(self):
        self.data: Dict[str, Dict[str, dict]] = {
            'students': {},
            'assessments': {},
            'roadmaps': {},
            'interview_sessions': {},
            'digital_twins': {},
            'learning_events': {},
            'skill_gaps': {},
            'users': {}
        }
    
    def set(self, collection: str, doc_id: str, data: dict):
        if collection not in self.data:
            self.data[collection] = {}
        self.data[collection][doc_id] = data
    
    def get(self, collection: str, doc_id: str) -> Optional[dict]:
        return self.data.get(collection, {}).get(doc_id)
    
    def update(self, collection: str, doc_id: str, data: dict):
        if collection in self.data and doc_id in self.data[collection]:
            self.data[collection][doc_id].update(data)
    
    def query(self, collection: str, field: str, value: str) -> List[dict]:
        results = []
        for doc_id, doc_data in self.data.get(collection, {}).items():
            if doc_data.get(field) == value:
                results.append(doc_data)
        return results
    
    def all(self, collection: str) -> List[dict]:
        return list(self.data.get(collection, {}).values())


class FirebaseService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not FirebaseService._initialized:
            self._init_firebase()
            FirebaseService._initialized = True

    def _init_firebase(self):
        """Initialize Firebase Admin SDK or fall back to in-memory storage"""
        self.db = None
        self.bucket = None
        self.memory = InMemoryStorage()
        self.using_memory = True
        
        if not FIREBASE_AVAILABLE:
            print("✅ Using in-memory storage (Firebase SDK not installed)")
            return
            
        try:
            creds_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None) if settings else None
            project_id = getattr(settings, 'FIREBASE_PROJECT_ID', None) if settings else None
            
            if creds_path and os.path.exists(creds_path):
                # Check if credentials file has actual content
                with open(creds_path, 'r') as f:
                    creds_data = json.load(f)
                    if creds_data.get('project_id') and creds_data.get('private_key'):
                        cred = credentials.Certificate(creds_path)
                        firebase_admin.initialize_app(cred, {
                            'storageBucket': f"{project_id}.appspot.com" if project_id else None
                        })
                        self.db = firestore.client()
                        self.using_memory = False
                        print("✅ Firebase initialized successfully")
                        return
            
            print("✅ Using in-memory storage (Firebase not configured)")
        except Exception as e:
            print(f"✅ Using in-memory storage (Firebase error: {e})")

    def get_db(self):
        return self.db

    def get_bucket(self):
        return self.bucket

    # Student Profile Operations
    async def create_student(self, student_id: str, data: dict) -> dict:
        """Create a new student profile"""
        data['created_at'] = datetime.utcnow().isoformat()
        if self.db and not self.using_memory:
            doc_ref = self.db.collection('students').document(student_id)
            doc_ref.set(data)
        else:
            self.memory.set('students', student_id, data)
        return data

    async def get_student(self, student_id: str) -> Optional[dict]:
        """Get student profile by ID"""
        if self.db and not self.using_memory:
            doc = self.db.collection('students').document(student_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        return self.memory.get('students', student_id)

    async def update_student(self, student_id: str, data: dict) -> dict:
        """Update student profile"""
        data['updated_at'] = datetime.utcnow().isoformat()
        if self.db and not self.using_memory:
            doc_ref = self.db.collection('students').document(student_id)
            doc_ref.update(data)
        else:
            self.memory.update('students', student_id, data)
        return data

    # Assessment Operations
    async def save_assessment_result(self, assessment_id: str, data: dict) -> dict:
        """Save assessment result"""
        if self.db and not self.using_memory:
            doc_ref = self.db.collection('assessments').document(assessment_id)
            doc_ref.set(data)
        else:
            self.memory.set('assessments', assessment_id, data)
        return data

    async def get_assessment(self, assessment_id: str) -> Optional[dict]:
        """Get assessment by ID"""
        if self.db and not self.using_memory:
            doc = self.db.collection('assessments').document(assessment_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        return self.memory.get('assessments', assessment_id)

    async def get_student_assessments(self, student_id: str) -> list:
        """Get all assessments for a student"""
        if self.db and not self.using_memory:
            docs = self.db.collection('assessments')\
                .where('student_id', '==', student_id)\
                .stream()
            return [doc.to_dict() for doc in docs]
        return self.memory.query('assessments', 'student_id', student_id)

    # Roadmap Operations
    async def save_roadmap(self, roadmap_id: str, data: dict) -> dict:
        """Save personalized roadmap"""
        if self.db and not self.using_memory:
            doc_ref = self.db.collection('roadmaps').document(roadmap_id)
            doc_ref.set(data)
        else:
            self.memory.set('roadmaps', roadmap_id, data)
        return data

    async def get_roadmap(self, roadmap_id: str) -> Optional[dict]:
        """Get roadmap by ID"""
        if self.db and not self.using_memory:
            doc = self.db.collection('roadmaps').document(roadmap_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        return self.memory.get('roadmaps', roadmap_id)

    async def get_student_roadmap(self, student_id: str) -> Optional[dict]:
        """Get active roadmap for student"""
        if self.db and not self.using_memory:
            docs = self.db.collection('roadmaps')\
                .where('student_id', '==', student_id)\
                .limit(1)\
                .stream()
            for doc in docs:
                return doc.to_dict()
            return None
        roadmaps = self.memory.query('roadmaps', 'student_id', student_id)
        return roadmaps[0] if roadmaps else None

    # Interview Session Operations
    async def save_interview_session(self, session_id: str, data: dict) -> dict:
        """Save interview session"""
        if self.db and not self.using_memory:
            doc_ref = self.db.collection('interview_sessions').document(session_id)
            doc_ref.set(data)
        else:
            self.memory.set('interview_sessions', session_id, data)
        return data

    async def get_interview_session(self, session_id: str) -> Optional[dict]:
        """Get interview session by ID"""
        if self.db and not self.using_memory:
            doc = self.db.collection('interview_sessions').document(session_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        return self.memory.get('interview_sessions', session_id)

    async def get_interview_history(self, student_id: str) -> list:
        """Get interview history for student"""
        if self.db and not self.using_memory:
            docs = self.db.collection('interview_sessions')\
                .where('student_id', '==', student_id)\
                .stream()
            return [doc.to_dict() for doc in docs]
        return self.memory.query('interview_sessions', 'student_id', student_id)

    # Digital Twin Operations
    async def save_digital_twin(self, twin_id: str, data: dict) -> dict:
        """Save digital twin profile"""
        if self.db and not self.using_memory:
            doc_ref = self.db.collection('digital_twins').document(twin_id)
            doc_ref.set(data)
        else:
            self.memory.set('digital_twins', twin_id, data)
        return data

    async def get_digital_twin(self, student_id: str) -> Optional[dict]:
        """Get digital twin for student"""
        twin_id = f"twin_{student_id}"
        if self.db and not self.using_memory:
            doc = self.db.collection('digital_twins').document(twin_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        return self.memory.get('digital_twins', twin_id)

    async def add_learning_event(self, student_id: str, event: dict) -> dict:
        """Add learning event for digital twin analysis"""
        event['student_id'] = student_id
        event['timestamp'] = datetime.utcnow().isoformat()
        event_id = f"event_{student_id}_{datetime.utcnow().timestamp()}"
        if self.db and not self.using_memory:
            doc_ref = self.db.collection('learning_events').document(event_id)
            doc_ref.set(event)
        else:
            self.memory.set('learning_events', event_id, event)
        return event

    async def get_learning_events(self, student_id: str, limit: int = 100) -> list:
        """Get learning events for student"""
        if self.db and not self.using_memory:
            docs = self.db.collection('learning_events')\
                .where('student_id', '==', student_id)\
                .limit(limit)\
                .stream()
            return [doc.to_dict() for doc in docs]
        events = self.memory.query('learning_events', 'student_id', student_id)
        return events[:limit]

    # Skill Gap Operations
    async def save_skill_gap_analysis(self, analysis_id: str, data: dict) -> dict:
        """Save skill gap analysis"""
        if self.db and not self.using_memory:
            doc_ref = self.db.collection('skill_gaps').document(analysis_id)
            doc_ref.set(data)
        else:
            self.memory.set('skill_gaps', analysis_id, data)
        return data

    async def get_skill_gap_history(self, student_id: str) -> list:
        """Get skill gap analysis history for student"""
        if self.db and not self.using_memory:
            docs = self.db.collection('skill_gaps')\
                .where('student_id', '==', student_id)\
                .stream()
            return [doc.to_dict() for doc in docs]
        return self.memory.query('skill_gaps', 'student_id', student_id)

    # User Operations (for auth)
    async def create_user(self, user_id: str, data: dict) -> dict:
        """Create a new user"""
        data['created_at'] = datetime.utcnow().isoformat()
        if self.db and not self.using_memory:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.set(data)
        else:
            self.memory.set('users', user_id, data)
        return data

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        if self.db and not self.using_memory:
            docs = self.db.collection('users')\
                .where('email', '==', email)\
                .limit(1)\
                .stream()
            for doc in docs:
                result = doc.to_dict()
                result['id'] = doc.id
                return result
            return None
        users = self.memory.query('users', 'email', email)
        return users[0] if users else None

    async def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        if self.db and not self.using_memory:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                result = doc.to_dict()
                result['id'] = doc.id
                return result
            return None
        return self.memory.get('users', user_id)


# Singleton instance
firebase_service = FirebaseService()
