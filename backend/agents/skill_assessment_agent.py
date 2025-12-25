"""
AI Skill Assessment Agent (Diagnose Step)
==========================================
Tests students on aptitude, technical skills, and soft skills.

Features:
- Question bank tagged by skill
- Adaptive difficulty (AI increases difficulty if student does well)
- GPT for explanation feedback
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import random
import uuid

from services.gemini_service import gemini_service
from models.schemas import DifficultyLevel, SkillCategory


class SkillAssessmentAgent:
    """Agent for adaptive skill assessment"""
    
    def __init__(self):
        self.gemini = gemini_service
        self.question_bank = self._initialize_question_bank()
    
    def _initialize_question_bank(self) -> Dict[str, List[Dict]]:
        """Initialize a sample question bank"""
        return {
            "technical": {
                "dsa": {
                    "easy": [
                        {
                            "id": "dsa_e1",
                            "question": "What is the time complexity of accessing an element in an array by index?",
                            "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                            "correct": "O(1)",
                            "explanation": "Array access by index is constant time O(1) as it's a direct memory lookup."
                        },
                        {
                            "id": "dsa_e2",
                            "question": "Which data structure follows LIFO (Last In First Out) principle?",
                            "options": ["Queue", "Stack", "Linked List", "Array"],
                            "correct": "Stack",
                            "explanation": "Stack follows LIFO - the last element added is the first to be removed."
                        },
                        {
                            "id": "dsa_e3",
                            "question": "What is the time complexity of linear search?",
                            "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                            "correct": "O(n)",
                            "explanation": "Linear search checks each element one by one, so it's O(n)."
                        },
                    ],
                    "medium": [
                        {
                            "id": "dsa_m1",
                            "question": "What is the time complexity of binary search?",
                            "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                            "correct": "O(log n)",
                            "explanation": "Binary search divides the search space in half each time, giving O(log n)."
                        },
                        {
                            "id": "dsa_m2",
                            "question": "Which sorting algorithm has the best average case time complexity?",
                            "options": ["Bubble Sort - O(n²)", "Quick Sort - O(n log n)", "Selection Sort - O(n²)", "Insertion Sort - O(n²)"],
                            "correct": "Quick Sort - O(n log n)",
                            "explanation": "Quick Sort has an average case of O(n log n), making it one of the fastest general-purpose sorting algorithms."
                        },
                        {
                            "id": "dsa_m3",
                            "question": "What data structure is used for BFS traversal of a graph?",
                            "options": ["Stack", "Queue", "Heap", "Tree"],
                            "correct": "Queue",
                            "explanation": "BFS uses a queue to visit nodes level by level in FIFO order."
                        },
                    ],
                    "hard": [
                        {
                            "id": "dsa_h1",
                            "question": "What is the time complexity of Dijkstra's algorithm using a binary heap?",
                            "options": ["O(V²)", "O(E log V)", "O(V log V)", "O(E + V)"],
                            "correct": "O(E log V)",
                            "explanation": "With a binary heap, Dijkstra's algorithm runs in O(E log V) where E is edges and V is vertices."
                        },
                        {
                            "id": "dsa_h2",
                            "question": "Which algorithm is used to find strongly connected components in a directed graph?",
                            "options": ["Dijkstra's", "Kosaraju's", "Prim's", "Kruskal's"],
                            "correct": "Kosaraju's",
                            "explanation": "Kosaraju's algorithm finds all SCCs in a directed graph using two DFS passes."
                        },
                    ],
                },
                "python": {
                    "easy": [
                        {
                            "id": "py_e1",
                            "question": "What is the output of: print(type([]))?",
                            "options": ["<class 'list'>", "<class 'array'>", "<class 'tuple'>", "<class 'dict'>"],
                            "correct": "<class 'list'>",
                            "explanation": "[] creates an empty list in Python, so type([]) returns <class 'list'>."
                        },
                        {
                            "id": "py_e2",
                            "question": "Which keyword is used to define a function in Python?",
                            "options": ["function", "def", "func", "define"],
                            "correct": "def",
                            "explanation": "Python uses 'def' keyword to define functions."
                        },
                    ],
                    "medium": [
                        {
                            "id": "py_m1",
                            "question": "What is the difference between '==' and 'is' in Python?",
                            "options": [
                                "'==' compares values, 'is' compares identity",
                                "'==' compares identity, 'is' compares values",
                                "They are the same",
                                "'is' is not a valid operator"
                            ],
                            "correct": "'==' compares values, 'is' compares identity",
                            "explanation": "'==' checks if values are equal, while 'is' checks if they are the same object in memory."
                        },
                        {
                            "id": "py_m2",
                            "question": "What is a Python decorator?",
                            "options": [
                                "A function that modifies another function",
                                "A class attribute",
                                "A type of loop",
                                "A string formatter"
                            ],
                            "correct": "A function that modifies another function",
                            "explanation": "Decorators are functions that take another function and extend its behavior."
                        },
                    ],
                    "hard": [
                        {
                            "id": "py_h1",
                            "question": "What is the output of: list(map(lambda x: x**2, filter(lambda x: x%2==0, range(10))))?",
                            "options": ["[0, 4, 16, 36, 64]", "[1, 9, 25, 49, 81]", "[0, 2, 4, 6, 8]", "[4, 16, 36, 64]"],
                            "correct": "[0, 4, 16, 36, 64]",
                            "explanation": "First filters even numbers (0,2,4,6,8), then squares them to get [0,4,16,36,64]."
                        },
                    ],
                },
                "java": {
                    "easy": [
                        {
                            "id": "java_e1",
                            "question": "What is the entry point of a Java program?",
                            "options": ["main()", "start()", "run()", "init()"],
                            "correct": "main()",
                            "explanation": "Java programs start execution from the main() method."
                        },
                    ],
                    "medium": [
                        {
                            "id": "java_m1",
                            "question": "What is the difference between ArrayList and LinkedList in Java?",
                            "options": [
                                "ArrayList uses array, LinkedList uses doubly-linked list",
                                "They are the same",
                                "ArrayList is slower for all operations",
                                "LinkedList cannot store objects"
                            ],
                            "correct": "ArrayList uses array, LinkedList uses doubly-linked list",
                            "explanation": "ArrayList is better for random access, LinkedList is better for insertions/deletions."
                        },
                    ],
                    "hard": [
                        {
                            "id": "java_h1",
                            "question": "What is the purpose of the volatile keyword in Java?",
                            "options": [
                                "Ensures visibility of changes across threads",
                                "Makes variable immutable",
                                "Increases performance",
                                "Declares constants"
                            ],
                            "correct": "Ensures visibility of changes across threads",
                            "explanation": "volatile ensures that reads/writes go directly to main memory, making changes visible to all threads."
                        },
                    ],
                },
                "system_design": {
                    "medium": [
                        {
                            "id": "sd_m1",
                            "question": "What is the CAP theorem in distributed systems?",
                            "options": [
                                "Consistency, Availability, Partition tolerance - pick 2",
                                "Cache, API, Performance",
                                "Create, Alter, Process",
                                "Compute, Analyze, Predict"
                            ],
                            "correct": "Consistency, Availability, Partition tolerance - pick 2",
                            "explanation": "CAP theorem states that a distributed system can only guarantee 2 of these 3 properties."
                        },
                    ],
                    "hard": [
                        {
                            "id": "sd_h1",
                            "question": "How would you design a rate limiter for an API?",
                            "options": [
                                "Token bucket or sliding window algorithm",
                                "Simple counter",
                                "Random delay",
                                "Queue all requests"
                            ],
                            "correct": "Token bucket or sliding window algorithm",
                            "explanation": "Token bucket and sliding window are industry-standard algorithms for rate limiting."
                        },
                    ],
                },
            },
            "aptitude": {
                "logical": {
                    "easy": [
                        {
                            "id": "apt_l_e1",
                            "question": "If A > B and B > C, then which is true?",
                            "options": ["A > C", "C > A", "A = C", "Cannot determine"],
                            "correct": "A > C",
                            "explanation": "By transitivity, if A > B and B > C, then A > C."
                        },
                        {
                            "id": "apt_l_e2",
                            "question": "What comes next in the series: 2, 6, 18, 54, ?",
                            "options": ["108", "162", "72", "216"],
                            "correct": "162",
                            "explanation": "Each number is multiplied by 3. 54 × 3 = 162."
                        },
                    ],
                    "medium": [
                        {
                            "id": "apt_l_m1",
                            "question": "If FRIEND is coded as HUMJTK, how is CANDLE coded?",
                            "options": ["EDRIRL", "DCPFQG", "ESJFQG", "DCRILF"],
                            "correct": "EDRIRL",
                            "explanation": "Each letter is shifted by +2 in the alphabet."
                        },
                    ],
                },
                "quantitative": {
                    "easy": [
                        {
                            "id": "apt_q_e1",
                            "question": "What is 15% of 200?",
                            "options": ["30", "25", "35", "40"],
                            "correct": "30",
                            "explanation": "15% of 200 = (15/100) × 200 = 30."
                        },
                    ],
                    "medium": [
                        {
                            "id": "apt_q_m1",
                            "question": "A train travels 300 km in 5 hours. What is its speed in m/s?",
                            "options": ["16.67 m/s", "60 m/s", "300 m/s", "50 m/s"],
                            "correct": "16.67 m/s",
                            "explanation": "Speed = 300/5 = 60 km/h = 60 × (5/18) = 16.67 m/s."
                        },
                    ],
                },
            },
            "soft_skills": {
                "communication": {
                    "easy": [
                        {
                            "id": "ss_c_e1",
                            "question": "What is active listening?",
                            "options": [
                                "Fully concentrating on the speaker",
                                "Talking while others speak",
                                "Ignoring non-verbal cues",
                                "Preparing your response while listening"
                            ],
                            "correct": "Fully concentrating on the speaker",
                            "explanation": "Active listening means giving full attention to the speaker and understanding their message."
                        },
                    ],
                    "medium": [
                        {
                            "id": "ss_c_m1",
                            "question": "How should you handle a disagreement in a team meeting?",
                            "options": [
                                "Listen first, then express your view respectfully",
                                "Raise your voice to be heard",
                                "Walk out of the meeting",
                                "Ignore the disagreement"
                            ],
                            "correct": "Listen first, then express your view respectfully",
                            "explanation": "Professional disagreements should be handled with respect and active listening."
                        },
                    ],
                },
            },
        }
    
    def get_questions(
        self,
        category: str,
        skill: str,
        difficulty: str,
        count: int = 5
    ) -> List[Dict]:
        """Get questions from the bank based on criteria"""
        
        questions = []
        
        if category in self.question_bank:
            category_bank = self.question_bank[category]
            if skill in category_bank:
                skill_bank = category_bank[skill]
                if difficulty in skill_bank:
                    available = skill_bank[difficulty]
                    questions = random.sample(available, min(count, len(available)))
        
        return questions
    
    def calculate_adaptive_difficulty(
        self,
        current_difficulty: str,
        consecutive_correct: int,
        consecutive_wrong: int
    ) -> str:
        """Calculate next difficulty based on performance"""
        
        difficulties = ["easy", "medium", "hard"]
        current_index = difficulties.index(current_difficulty)
        
        # Increase difficulty after 2 consecutive correct
        if consecutive_correct >= 2 and current_index < 2:
            return difficulties[current_index + 1]
        
        # Decrease difficulty after 2 consecutive wrong
        if consecutive_wrong >= 2 and current_index > 0:
            return difficulties[current_index - 1]
        
        return current_difficulty
    
    async def create_assessment(
        self,
        student_id: str,
        category: SkillCategory,
        skills: List[str],
        questions_per_skill: int = 5
    ) -> Dict[str, Any]:
        """Create an adaptive assessment"""
        
        assessment_id = str(uuid.uuid4())
        questions = []
        
        category_name = category.value
        
        for skill in skills:
            # Start with medium difficulty
            skill_questions = self.get_questions(
                category_name,
                skill.lower(),
                "medium",
                questions_per_skill
            )
            
            # If not enough questions, try other difficulties
            if len(skill_questions) < questions_per_skill:
                for diff in ["easy", "hard"]:
                    more = self.get_questions(
                        category_name,
                        skill.lower(),
                        diff,
                        questions_per_skill - len(skill_questions)
                    )
                    skill_questions.extend(more)
            
            for q in skill_questions:
                q["skill"] = skill
                q["category"] = category_name
            
            questions.extend(skill_questions)
        
        # Shuffle questions
        random.shuffle(questions)
        
        return {
            "assessment_id": assessment_id,
            "student_id": student_id,
            "category": category_name,
            "questions": questions,
            "total_questions": len(questions),
            "current_index": 0,
            "answers": [],
            "adaptive_state": {
                "current_difficulty": "medium",
                "consecutive_correct": 0,
                "consecutive_wrong": 0,
                "skill_performance": {}
            },
            "started_at": datetime.utcnow().isoformat(),
            "status": "in_progress"
        }
    
    async def submit_answer(
        self,
        assessment: Dict[str, Any],
        question_id: str,
        answer: str,
        time_taken: int
    ) -> Dict[str, Any]:
        """Submit an answer and get adaptive next question"""
        
        # Find the question
        question = None
        for q in assessment["questions"]:
            if q["id"] == question_id:
                question = q
                break
        
        if not question:
            return {"error": "Question not found"}
        
        # Check answer
        is_correct = answer == question["correct"]
        
        # Update adaptive state
        state = assessment["adaptive_state"]
        skill = question["skill"]
        
        if is_correct:
            state["consecutive_correct"] += 1
            state["consecutive_wrong"] = 0
        else:
            state["consecutive_wrong"] += 1
            state["consecutive_correct"] = 0
        
        # Update skill performance
        if skill not in state["skill_performance"]:
            state["skill_performance"][skill] = {"correct": 0, "total": 0}
        state["skill_performance"][skill]["total"] += 1
        if is_correct:
            state["skill_performance"][skill]["correct"] += 1
        
        # Calculate new difficulty
        state["current_difficulty"] = self.calculate_adaptive_difficulty(
            state["current_difficulty"],
            state["consecutive_correct"],
            state["consecutive_wrong"]
        )
        
        # Record answer
        assessment["answers"].append({
            "question_id": question_id,
            "given_answer": answer,
            "correct_answer": question["correct"],
            "is_correct": is_correct,
            "time_taken": time_taken,
            "skill": skill,
            "difficulty": question.get("difficulty", "medium")
        })
        
        assessment["current_index"] += 1
        
        return {
            "is_correct": is_correct,
            "correct_answer": question["correct"],
            "explanation": question.get("explanation", ""),
            "new_difficulty": state["current_difficulty"],
            "questions_remaining": len(assessment["questions"]) - assessment["current_index"]
        }
    
    async def complete_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Complete assessment and generate results"""
        
        answers = assessment["answers"]
        total = len(answers)
        correct = sum(1 for a in answers if a["is_correct"])
        
        # Calculate skill-wise scores
        skill_scores = {}
        for skill, perf in assessment["adaptive_state"]["skill_performance"].items():
            if perf["total"] > 0:
                skill_scores[skill] = round((perf["correct"] / perf["total"]) * 100, 2)
        
        # Identify strengths and weaknesses
        strengths = [s for s, score in skill_scores.items() if score >= 70]
        weaknesses = [s for s, score in skill_scores.items() if score < 50]
        
        # Calculate overall score
        overall_score = round((correct / total) * 100, 2) if total > 0 else 0
        
        # Calculate skill gap score
        total_skills = len(skill_scores)
        weak_skills = len(weaknesses)
        skill_gap_score = round((weak_skills / total_skills) * 100, 2) if total_skills > 0 else 0
        
        # Generate AI feedback
        feedback = await self.gemini.generate_assessment_feedback(
            assessment["category"],
            overall_score,
            answers[:5]
        )
        
        result = {
            "assessment_id": assessment["assessment_id"],
            "student_id": assessment["student_id"],
            "category": assessment["category"],
            "total_questions": total,
            "correct_answers": correct,
            "score": overall_score,
            "skill_scores": skill_scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "skill_gap_score": skill_gap_score,
            "feedback": feedback,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        return result


# Singleton instance
skill_assessment_agent = SkillAssessmentAgent()
