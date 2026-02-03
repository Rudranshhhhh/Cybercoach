from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from models.question import Question
from models.answer import Answer


# Difficulty levels for Adversarial Evolver (Start HARD, scale up)
DIFFICULTY_LEVELS = ["ADVANCED", "EXPERT", "ELITE"]

# Psychological triggers for Bias Heatmap
PSYCHOLOGICAL_TRIGGERS = ["AUTHORITY", "URGENCY", "SCARCITY", "CURIOSITY", "FEAR"]


@dataclass
class Session:
    """Represents a quiz session with advanced AI tracking."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    num_questions: int = 5
    current_question_index: int = 0
    questions: List[Question] = field(default_factory=list)
    answers: List[Answer] = field(default_factory=list)
    is_completed: bool = False
    
    # Adversarial Evolver - Difficulty Scaling (Start from ADVANCED)
    difficulty_level: str = "ADVANCED"
    consecutive_correct: int = 0
    
    # Human Bias Heatmap - Psychological Vulnerability Tracking
    bias_counts: Dict[str, int] = field(default_factory=lambda: {
        "AUTHORITY": 0,
        "URGENCY": 0,
        "SCARCITY": 0,
        "CURIOSITY": 0,
        "FEAR": 0
    })
    bias_exposures: Dict[str, int] = field(default_factory=lambda: {
        "AUTHORITY": 0,
        "URGENCY": 0,
        "SCARCITY": 0,
        "CURIOSITY": 0,
        "FEAR": 0
    })
    
    def get_current_question(self) -> Optional[Question]:
        """Get the current question to answer."""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def add_question(self, question: Question) -> None:
        """Add a question to the session."""
        self.questions.append(question)
    
    def add_answer(self, answer: Answer, psychological_trigger: Optional[str] = None) -> None:
        """Add an answer and update difficulty/bias tracking."""
        self.answers.append(answer)
        
        # Track bias exposure
        if psychological_trigger and psychological_trigger in self.bias_exposures:
            self.bias_exposures[psychological_trigger] += 1
        
        # Adversarial Evolver: Adjust difficulty based on performance
        if answer.is_correct:
            self.consecutive_correct += 1
            # Level up after 2 consecutive correct answers
            if self.consecutive_correct >= 2:
                self._increase_difficulty()
                self.consecutive_correct = 0
        else:
            self.consecutive_correct = 0
            # Track which bias got them
            if psychological_trigger and psychological_trigger in self.bias_counts:
                self.bias_counts[psychological_trigger] += 1
        
        self.current_question_index += 1
        
        if self.current_question_index >= self.num_questions:
            self.is_completed = True
    
    def _increase_difficulty(self) -> None:
        """Increase difficulty level (Adversarial Evolver)."""
        current_idx = DIFFICULTY_LEVELS.index(self.difficulty_level)
        if current_idx < len(DIFFICULTY_LEVELS) - 1:
            self.difficulty_level = DIFFICULTY_LEVELS[current_idx + 1]
    
    def get_score(self) -> Dict[str, Any]:
        """Calculate the current score."""
        correct = sum(1 for a in self.answers if a.is_correct)
        total = len(self.answers)
        
        return {
            "correct": correct,
            "total": total,
            "percentage": round((correct / total * 100) if total > 0 else 0, 1)
        }
    
    def get_bias_heatmap(self) -> Dict[str, Any]:
        """Generate the Human Bias Heatmap with vulnerability percentages."""
        heatmap = {}
        
        for trigger in PSYCHOLOGICAL_TRIGGERS:
            exposures = self.bias_exposures[trigger]
            failures = self.bias_counts[trigger]
            
            if exposures > 0:
                vulnerability = round((failures / exposures) * 100)
            else:
                vulnerability = 0
            
            heatmap[trigger] = {
                "vulnerability_percentage": vulnerability,
                "times_exposed": exposures,
                "times_failed": failures
            }
        
        # Find primary weakness
        max_vulnerability = 0
        primary_weakness = None
        for trigger, data in heatmap.items():
            if data["times_failed"] > 0 and data["vulnerability_percentage"] > max_vulnerability:
                max_vulnerability = data["vulnerability_percentage"]
                primary_weakness = trigger
        
        return {
            "heatmap": heatmap,
            "primary_weakness": primary_weakness,
            "primary_vulnerability_percentage": max_vulnerability
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
            "difficulty_level": self.difficulty_level,
            "score": self.get_score(),
            "bias_heatmap": self.get_bias_heatmap()
        }
