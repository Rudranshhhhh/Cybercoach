from typing import Dict, Any, Optional, Tuple

from models.question import Question, ScenarioType, ManipulationType, Difficulty
from models.answer import Answer, AnswerEvaluation
from models.session import Session
from services.llm_client import llm_client
from services.session_manager import session_manager


class QuizService:
    """Service for managing quiz flow with Adversarial AI features."""
    
    def start_quiz(self, num_questions: int = 5) -> Session:
        """Start a new quiz session."""
        return session_manager.create_session(num_questions)
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return session_manager.get_session(session_id)
    
    def generate_question(self, session: Session) -> Optional[Question]:
        """Generate a new question at the session's current difficulty level."""
        if session.is_completed:
            print("DEBUG: Session completed, no more questions")
            return None
        
        # Check if we already have this question generated
        if session.current_question_index < len(session.questions):
            print(f"DEBUG: Returning existing question {session.current_question_index}")
            return session.questions[session.current_question_index]
        
        # Generate new question from LLM with current difficulty
        print(f"DEBUG: Generating new question at index {session.current_question_index}")
        question_data = llm_client.generate_question(
            difficulty=session.difficulty_level
        )
        
        if not question_data:
            print("DEBUG: LLM returned None for question_data")
            return None
        
        print(f"DEBUG: Got question_data with keys: {question_data.keys()}")
        
        # Parse manipulation type
        manipulation_type = None
        if question_data.get("manipulation_type"):
            try:
                manipulation_type = ManipulationType(question_data["manipulation_type"])
            except ValueError:
                pass
        
        # Map difficulty string to enum
        difficulty_map = {
            "BEGINNER": Difficulty.EASY,
            "INTERMEDIATE": Difficulty.MEDIUM,
            "ADVANCED": Difficulty.HARD,
            "EXPERT": Difficulty.HARD
        }
        
        # Map scenario type from LLM response
        scenario_type_map = {
            "email": ScenarioType.EMAIL,
            "popup": ScenarioType.EMAIL,  # Fallback to EMAIL for display
            "slack": ScenarioType.EMAIL,
            "oauth_screen": ScenarioType.EMAIL,
            "qr_poster": ScenarioType.EMAIL,
            "code_review": ScenarioType.EMAIL
        }
        scenario_type_str = question_data.get("scenario_type", "email")
        scenario_type = scenario_type_map.get(scenario_type_str, ScenarioType.EMAIL)
        
        # Create question object with enhanced metadata
        question = Question(
            id=session.current_question_index + 1,
            scenario_type=scenario_type,
            content=question_data.get("content", {}),
            correct_answer=question_data.get("correct_answer", "Safe"),
            manipulation_type=manipulation_type,
            difficulty=difficulty_map.get(session.difficulty_level, Difficulty.MEDIUM),
            red_flags=question_data.get("red_flags", [])
        )
        
        # Store scenario_type string for frontend
        question.scenario_type_str = scenario_type_str
        print(f"DEBUG: Created question with scenario_type: {scenario_type_str}")
        
        # Store additional metadata for evaluation
        question.psychological_trigger = question_data.get("psychological_trigger")
        question.attack_vector = question_data.get("attack_vector")
        question.sophistication_notes = question_data.get("sophistication_notes")
        
        # Store 2026 Threat Intelligence metadata
        question.threat_vector = question_data.get("threat_vector")
        question.complexity_score = question_data.get("complexity_score")
        question.why_its_hard = question_data.get("why_its_hard")
        question.psychological_exploit = question_data.get("psychological_exploit")
        question.trend_2026 = question_data.get("trend_2026")
        question.trend_shift = question_data.get("trend_shift")
        
        # Store Intent Analysis for 2026 evaluation
        question.intent_analysis = question_data.get("intent_analysis")
        
        session.add_question(question)
        return question
    
    def evaluate_answer(
        self,
        session: Session,
        question_id: int,
        user_answer: str,
        user_reasoning: Optional[str] = None
    ) -> Tuple[Optional[AnswerEvaluation], Optional[str]]:
        """Evaluate a user's answer with psychological bias tracking."""
        # Find the question
        question = None
        for q in session.questions:
            if q.id == question_id:
                question = q
                break
        
        if not question:
            return None, "Question not found"
        
        # Check if already answered
        for a in session.answers:
            if a.question_id == question_id:
                return None, "Question already answered"
        
        # Get psychological trigger for tracking
        psychological_trigger = getattr(question, 'psychological_trigger', None)
        attack_vector = getattr(question, 'attack_vector', None)
        
        print(f"DEBUG: Evaluating Q{question_id}")
        print(f"DEBUG: User Answer: '{user_answer}'")
        print(f"DEBUG: Correct Answer: '{question.correct_answer}'")
        
        # Evaluate with LLM
        evaluation_data = llm_client.evaluate_answer(
            scenario=question.content,
            correct_answer=question.correct_answer,
            manipulation_type=question.manipulation_type.value if question.manipulation_type else None,
            red_flags=question.red_flags,
            user_answer=user_answer,
            user_reasoning=user_reasoning,
            psychological_trigger=psychological_trigger,
            attack_vector=attack_vector,
            intent_analysis=getattr(question, 'intent_analysis', None)
        )
        
        if evaluation_data:
            print("DEBUG: LLM Evaluation Successful")
        else:
            print("DEBUG: LLM Evaluation Failed - Using Fallback")
        
        if not evaluation_data:
            # Fallback to simple comparison
            is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()
            print(f"DEBUG: Fallback comparison: {user_answer.strip().lower()} == {question.correct_answer.strip().lower()} -> {is_correct}")
            
            evaluation_data = {
                "correct": is_correct,
                "explanation": "Correct!" if is_correct else f"The correct answer was {question.correct_answer}.",
                "psychological_trigger_exploited": psychological_trigger if not is_correct else None,
                "learning_tip": "Always verify sender domains and look for urgency tactics." if not is_correct else None
            }
        
        # Get threat intelligence metadata from question
        threat_vector = getattr(question, 'threat_vector', None) or getattr(question, 'attack_vector', None)
        complexity_score = getattr(question, 'complexity_score', None)
        why_its_hard = getattr(question, 'why_its_hard', None)
        psychological_exploit = getattr(question, 'psychological_exploit', None)
        
        # Create evaluation object with enhanced data
        evaluation = AnswerEvaluation(
            correct=evaluation_data.get("correct", False),
            explanation=evaluation_data.get("explanation", ""),
            manipulation_that_worked=evaluation_data.get("psychological_trigger_exploited"),
            learning_tip=evaluation_data.get("learning_tip"),
            correct_answer=question.correct_answer if not evaluation_data.get("correct") else None,
            threat_vector=threat_vector,
            complexity_score=complexity_score,
            why_its_hard=why_its_hard,
            psychological_exploit=psychological_exploit
        )
        
        # Add bias analysis to evaluation
        evaluation.bias_analysis = evaluation_data.get("bias_analysis")
        evaluation.vulnerability_score = evaluation_data.get("vulnerability_score", 0)
        evaluation.future_vulnerability = evaluation_data.get("future_vulnerability")
        
        # Create and store answer
        answer = Answer(
            question_id=question_id,
            user_answer=user_answer,
            user_reasoning=user_reasoning,
            is_correct=evaluation.correct,
            manipulation_type_missed=evaluation.manipulation_that_worked,
            explanation=evaluation.explanation,
            learning_tip=evaluation.learning_tip
        )
        
        # Add answer with psychological trigger for bias tracking
        session.add_answer(answer, psychological_trigger=psychological_trigger)
        
        return evaluation, None
    
    def is_quiz_complete(self, session: Session) -> bool:
        """Check if the quiz is complete."""
        return session.is_completed
    
    def get_progress(self, session: Session) -> Dict[str, Any]:
        """Get the current quiz progress with difficulty info."""
        score = session.get_score()
        return {
            "current_question": session.current_question_index + 1,
            "total_questions": session.num_questions,
            "answered": len(session.answers),
            "correct": score["correct"],
            "is_completed": session.is_completed,
            "difficulty_level": session.difficulty_level,
            "bias_heatmap": session.get_bias_heatmap()
        }


# Singleton instance
quiz_service = QuizService()
