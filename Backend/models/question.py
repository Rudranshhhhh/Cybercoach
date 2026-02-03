from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class ManipulationType(Enum):
    """Types of manipulation tactics used in phishing."""
    URGENCY = "Urgency"
    AUTHORITY = "Authority"
    FEAR = "Fear"
    REWARD = "Reward"


class ScenarioType(Enum):
    """Types of phishing scenarios."""
    EMAIL = "email"
    SMS = "sms"
    WEBSITE = "website"


class Difficulty(Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Question:
    """Represents a phishing/safe scenario question."""
    id: int
    scenario_type: ScenarioType
    content: Dict[str, Any]
    correct_answer: str  # "Phishing" or "Safe"
    manipulation_type: Optional[ManipulationType] = None
    difficulty: Difficulty = Difficulty.MEDIUM
    red_flags: list = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary for JSON response."""
        return {
            "id": self.id,
            "scenario_type": self.scenario_type.value,
            "content": self.content,
            "correct_answer": self.correct_answer,
            "manipulation_type": self.manipulation_type.value if self.manipulation_type else None,
            "difficulty": self.difficulty.value,
            "red_flags": self.red_flags
        }
    
    def to_user_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary for user (without answers)."""
        result = {
            "id": self.id,
            "scenario_type": getattr(self, 'scenario_type_str', self.scenario_type.value),
            "content": self.content,
            "question": "Is this Phishing or Safe?"
        }
        
        # Add optional fields if they exist
        if hasattr(self, 'threat_vector'):
            result["threat_vector"] = self.threat_vector
        if hasattr(self, 'intent_analysis'):
            result["intent_analysis"] = self.intent_analysis
            
        return result
