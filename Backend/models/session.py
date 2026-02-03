from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from models.question import Question
from models.answer import Answer


@dataclass
class Session:
    """Represents a quiz session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    num_questions: int = 5
    current_question_index: int = 0
    questions: List[Question] = field(default_factory=list)
    answers: List[Answer] = field(default_factory=list)
    is_completed: bool = False
    
    def get_current_question(self) -> Optional[Question]:
        """Get the current question to answer."""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def add_question(self, question: Question) -> None:
        """Add a question to the session."""
        self.questions.append(question)
    
    def add_answer(self, answer: Answer) -> None:
        """Add an answer and move to next question."""
        self.answers.append(answer)
        self.current_question_index += 1
        
        if self.current_question_index >= self.num_questions:
            self.is_completed = True
    
    def get_score(self) -> Dict[str, Any]:
        """Calculate the current score."""
        correct = sum(1 for a in self.answers if a.is_correct)
        total = len(self.answers)
        
        return {
            "correct": correct,
            "total": total,
            "percentage": round((correct / total * 100) if total > 0 else 0, 1)
        }
    
    def get_vulnerability_patterns(self) -> Dict[str, Any]:
        """Analyze which manipulation types the user is susceptible to."""
        patterns = {}
        
        for answer in self.answers:
            if not answer.is_correct and answer.manipulation_type_missed:
                manipulation = answer.manipulation_type_missed
                if manipulation not in patterns:
                    patterns[manipulation] = {"count": 0, "questions": []}
                patterns[manipulation]["count"] += 1
                patterns[manipulation]["questions"].append(answer.question_id)
        
        # Find most susceptible manipulation type
        most_susceptible = None
        max_count = 0
        for manipulation, data in patterns.items():
            if data["count"] > max_count:
                max_count = data["count"]
                most_susceptible = manipulation
        
        return {
            "most_susceptible_to": most_susceptible,
            "patterns": [
                {
                    "manipulation_type": m,
                    "times_missed": d["count"],
                    "question_ids": d["questions"]
                }
                for m, d in patterns.items()
            ]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "num_questions": self.num_questions,
            "current_question": self.current_question_index + 1,
            "total_questions": self.num_questions,
            "is_completed": self.is_completed,
            "score": self.get_score()
        }
