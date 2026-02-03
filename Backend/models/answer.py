from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Answer:
    """Represents a user's answer to a question."""
    question_id: int
    user_answer: str  # "Phishing" or "Safe"
    user_reasoning: Optional[str] = None
    is_correct: bool = False
    manipulation_type_missed: Optional[str] = None
    explanation: Optional[str] = None
    learning_tip: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert answer to dictionary."""
        return {
            "question_id": self.question_id,
            "user_answer": self.user_answer,
            "user_reasoning": self.user_reasoning,
            "is_correct": self.is_correct,
            "manipulation_type_missed": self.manipulation_type_missed,
            "explanation": self.explanation,
            "learning_tip": self.learning_tip
        }


@dataclass
class AnswerEvaluation:
    """Represents the LLM's evaluation of an answer."""
    correct: bool
    explanation: str
    manipulation_that_worked: Optional[str] = None
    learning_tip: Optional[str] = None
    correct_answer: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation to dictionary for JSON response."""
        result = {
            "correct": self.correct,
            "explanation": self.explanation
        }
        
        if not self.correct:
            result["correct_answer"] = self.correct_answer
            result["manipulation_type"] = self.manipulation_that_worked
            result["learning_tip"] = self.learning_tip
        
        return result
