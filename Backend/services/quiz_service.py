from typing import Dict, Any, Optional, Tuple

from models.question import Question, ScenarioType, ManipulationType, Difficulty
from models.answer import Answer, AnswerEvaluation
from models.session import Session
from services.llm_client import llm_client
from services.session_manager import session_manager


class QuizService:
    """Service for managing quiz flow and logic."""
    
    def start_quiz(self, num_questions: int = 5) -> Session:
        """Start a new quiz session."""
        return session_manager.create_session(num_questions)
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return session_manager.get_session(session_id)
    
    def generate_question(self, session: Session) -> Optional[Question]:
        """Generate a new question for the session."""
        if session.is_completed:
            return None
        
        # Check if we already have this question generated
        if session.current_question_index < len(session.questions):
            return session.questions[session.current_question_index]
        
        # Generate new question from LLM
        question_data = llm_client.generate_question()
        
        if not question_data:
            return None
        
        # Parse manipulation type
        manipulation_type = None
        if question_data.get("manipulation_type"):
            try:
                manipulation_type = ManipulationType(question_data["manipulation_type"])
            except ValueError:
                pass
        
        # Create question object
        question = Question(
            id=session.current_question_index + 1,
            scenario_type=ScenarioType.EMAIL,
            content=question_data.get("content", {}),
            correct_answer=question_data.get("correct_answer", "Safe"),
            manipulation_type=manipulation_type,
            difficulty=Difficulty.MEDIUM,
            red_flags=question_data.get("red_flags", [])
        )
        
        session.add_question(question)
        return question
    
    def evaluate_answer(
        self,
        session: Session,
        question_id: int,
        user_answer: str,
        user_reasoning: Optional[str] = None
    ) -> Tuple[Optional[AnswerEvaluation], Optional[str]]:
        """Evaluate a user's answer and return the evaluation."""
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
        
        # Evaluate with LLM
        evaluation_data = llm_client.evaluate_answer(
            scenario=question.content,
            correct_answer=question.correct_answer,
            manipulation_type=question.manipulation_type.value if question.manipulation_type else None,
            red_flags=question.red_flags,
            user_answer=user_answer,
            user_reasoning=user_reasoning
        )
        
        if not evaluation_data:
            # Fallback to simple comparison
            is_correct = user_answer.lower() == question.correct_answer.lower()
            evaluation_data = {
                "correct": is_correct,
                "explanation": "Correct!" if is_correct else f"The correct answer was {question.correct_answer}.",
                "manipulation_that_worked": question.manipulation_type.value if question.manipulation_type and not is_correct else None,
                "learning_tip": "Always verify sender domains and look for urgency tactics." if not is_correct else None
            }
        
        # Create evaluation object
        evaluation = AnswerEvaluation(
            correct=evaluation_data.get("correct", False),
            explanation=evaluation_data.get("explanation", ""),
            manipulation_that_worked=evaluation_data.get("manipulation_that_worked"),
            learning_tip=evaluation_data.get("learning_tip"),
            correct_answer=question.correct_answer if not evaluation_data.get("correct") else None
        )
        
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
        
        session.add_answer(answer)
        
        return evaluation, None
    
    def is_quiz_complete(self, session: Session) -> bool:
        """Check if the quiz is complete."""
        return session.is_completed
    
    def get_progress(self, session: Session) -> Dict[str, Any]:
        """Get the current quiz progress."""
        score = session.get_score()
        return {
            "current_question": session.current_question_index + 1,
            "total_questions": session.num_questions,
            "answered": len(session.answers),
            "correct": score["correct"],
            "is_completed": session.is_completed
        }


# Singleton instance
quiz_service = QuizService()
