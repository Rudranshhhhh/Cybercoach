from typing import Dict, Any, Optional

from models.session import Session
from services.llm_client import llm_client


class ReportGenerator:
    """Service for generating quiz reports."""
    
    def generate_report(self, session: Session) -> Optional[Dict[str, Any]]:
        """Generate a comprehensive report for a completed quiz."""
        if not session.is_completed and len(session.answers) == 0:
            return None
        
        score = session.get_score()
        vulnerability_patterns = session.get_vulnerability_patterns()
        
        # Build answer history for LLM
        answer_history = []
        for i, answer in enumerate(session.answers):
            question = session.questions[i] if i < len(session.questions) else None
            
            history_entry = {
                "question_id": answer.question_id,
                "scenario_summary": question.content.get("subject", "Unknown") if question else "Unknown",
                "correct_answer": question.correct_answer if question else "Unknown",
                "user_answer": answer.user_answer,
                "was_correct": answer.is_correct,
                "manipulation_type": answer.manipulation_type_missed
            }
            answer_history.append(history_entry)
        
        # Generate report with LLM
        report_data = llm_client.generate_report(
            total_questions=session.num_questions,
            correct_answers=score["correct"],
            score_percentage=score["percentage"],
            vulnerability_patterns=vulnerability_patterns,
            answer_history=answer_history
        )
        
        if not report_data:
            # Fallback to basic report
            report_data = self._generate_fallback_report(
                session, score, vulnerability_patterns, answer_history
            )
        
        # Add session info to report
        report_data["session_id"] = session.session_id
        report_data["total_questions"] = session.num_questions
        report_data["correct_answers"] = score["correct"]
        report_data["score_percentage"] = score["percentage"]
        
        return report_data
    
    def _generate_fallback_report(
        self,
        session: Session,
        score: Dict[str, Any],
        vulnerability_patterns: Dict[str, Any],
        answer_history: list
    ) -> Dict[str, Any]:
        """Generate a basic fallback report if LLM fails."""
        percentage = score["percentage"]
        
        # Determine risk level
        if percentage >= 80:
            risk_level = "Low"
            risk_score = 3
            assessment = "You have strong phishing awareness!"
        elif percentage >= 60:
            risk_level = "Moderate"
            risk_score = 5
            assessment = "You have moderate awareness but could improve."
        elif percentage >= 40:
            risk_level = "High"
            risk_score = 7
            assessment = "You are vulnerable to several phishing tactics."
        else:
            risk_level = "Critical"
            risk_score = 9
            assessment = "You are highly susceptible to phishing attacks."
        
        return {
            "overall_assessment": assessment,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "vulnerability_profile": vulnerability_patterns,
            "strengths": ["Completed the awareness training"] if score["correct"] > 0 else [],
            "recommendations": [
                "Always verify sender email addresses carefully",
                "Be suspicious of urgent requests",
                "Never click links without hovering to check the URL",
                "When in doubt, contact the company directly"
            ],
            "encouragement": "Keep practicing to improve your phishing detection skills!"
        }


# Singleton instance
report_generator = ReportGenerator()
