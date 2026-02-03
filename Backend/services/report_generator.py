from typing import Dict, Any, Optional

from models.session import Session
from services.llm_client import llm_client


class ReportGenerator:
    """Service for generating threat intelligence reports with Zero-Day Forecasting."""
    
    def generate_report(self, session: Session) -> Optional[Dict[str, Any]]:
        """Generate a comprehensive threat intelligence report."""
        if not session.is_completed and len(session.answers) == 0:
            return None
        
        score = session.get_score()
        vulnerability_patterns = session.get_vulnerability_patterns()
        bias_heatmap = session.get_bias_heatmap()
        
        # Build enhanced answer history for LLM
        answer_history = []
        for i, answer in enumerate(session.answers):
            question = session.questions[i] if i < len(session.questions) else None
            
            history_entry = {
                "question_id": answer.question_id,
                "scenario_summary": question.content.get("subject", "Unknown") if question else "Unknown",
                "correct_answer": question.correct_answer if question else "Unknown",
                "user_answer": answer.user_answer,
                "was_correct": answer.is_correct,
                "manipulation_type": answer.manipulation_type_missed,
                "psychological_trigger": getattr(question, 'psychological_trigger', None) if question else None,
                "attack_vector": getattr(question, 'attack_vector', None) if question else None
            }
            answer_history.append(history_entry)
        
        # Generate report with LLM including bias data
        report_data = llm_client.generate_report(
            total_questions=session.num_questions,
            correct_answers=score["correct"],
            score_percentage=score["percentage"],
            vulnerability_patterns=vulnerability_patterns,
            answer_history=answer_history,
            difficulty_level=session.difficulty_level,
            bias_heatmap=bias_heatmap
        )
        
        if not report_data:
            # Fallback to basic report
            report_data = self._generate_fallback_report(
                session, score, vulnerability_patterns, answer_history, bias_heatmap
            )
        
        # Add session info to report
        report_data["session_id"] = session.session_id
        report_data["total_questions"] = session.num_questions
        report_data["correct_answers"] = score["correct"]
        report_data["score_percentage"] = score["percentage"]
        report_data["final_difficulty"] = session.difficulty_level
        
        return report_data
    
    def _generate_fallback_report(
        self,
        session: Session,
        score: Dict[str, Any],
        vulnerability_patterns: Dict[str, Any],
        answer_history: list,
        bias_heatmap: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a fallback report with Zero-Day Forecasting if LLM fails."""
        percentage = score["percentage"]
        
        # Determine risk level
        if percentage >= 80:
            risk_level = "Low"
            risk_score = 3
            level = "Expert"
            assessment = "You have strong phishing awareness and can detect sophisticated attacks."
        elif percentage >= 60:
            risk_level = "Moderate"
            risk_score = 5
            level = "Proficient"
            assessment = "You have good awareness but could improve on advanced attack detection."
        elif percentage >= 40:
            risk_level = "High"
            risk_score = 7
            level = "Developing"
            assessment = "You are vulnerable to several phishing tactics and need more training."
        else:
            risk_level = "Critical"
            risk_score = 9
            level = "Novice"
            assessment = "You are highly susceptible to phishing attacks. Immediate training recommended."
        
        # Generate Zero-Day Threat Forecast based on primary weakness
        primary_weakness = bias_heatmap.get("primary_weakness")
        threat_forecast = self._generate_threat_forecast(primary_weakness, percentage)
        
        return {
            "overall_assessment": {
                "level": level,
                "summary": assessment
            },
            "risk_score": risk_score,
            "risk_level": risk_level,
            "bias_heatmap": bias_heatmap.get("heatmap", {}),
            "primary_weakness": {
                "trigger": primary_weakness,
                "vulnerability_percentage": bias_heatmap.get("primary_vulnerability_percentage", 0),
                "psychology": f"You showed susceptibility to {primary_weakness} manipulation tactics."
            },
            "zero_day_threat_forecast": threat_forecast,
            "vulnerability_profile": vulnerability_patterns,
            "strengths": ["Completed the awareness training"] if score["correct"] > 0 else [],
            "defense_protocol": [
                "Always verify sender email addresses carefully",
                "Be suspicious of urgent requests - take a pause before acting",
                "Never click links without hovering to check the URL",
                "When in doubt, contact the company through official channels",
                "Enable multi-factor authentication on all accounts"
            ],
            "next_level_challenge": f"Focus on resisting {primary_weakness} tactics to reach the next level."
        }
    
    def _generate_threat_forecast(self, primary_weakness: Optional[str], score: float) -> Dict[str, Any]:
        """Generate Zero-Day Threat Forecast based on user's weaknesses."""
        threat_map = {
            "AUTHORITY": {
                "highest_risk_vector": "Deepfake Vishing",
                "probability": 85,
                "scenario": "You are vulnerable to AI-synthesized voice calls from 'your CEO' requesting urgent wire transfers.",
                "secondary_risks": [
                    {"vector": "Business Email Compromise 2.0", "probability": 75, "reason": "Your AUTHORITY bias makes you likely to follow fake executive orders"}
                ]
            },
            "URGENCY": {
                "highest_risk_vector": "AI-Synthesized Spear Phishing",
                "probability": 80,
                "scenario": "Time-pressured phishing attacks that exploit your tendency to react without verification.",
                "secondary_risks": [
                    {"vector": "Deepfake Vishing", "probability": 70, "reason": "Urgent voice calls bypass your defenses"}
                ]
            },
            "CURIOSITY": {
                "highest_risk_vector": "Quishing (QR Code Phishing)",
                "probability": 75,
                "scenario": "Your curiosity makes you likely to scan unknown QR codes leading to malicious sites.",
                "secondary_risks": [
                    {"vector": "Collaboration Tool Attacks", "probability": 65, "reason": "Mysterious Slack/Teams messages trigger your curiosity"}
                ]
            },
            "FEAR": {
                "highest_risk_vector": "Ransomware Social Engineering",
                "probability": 80,
                "scenario": "Fear-based attacks claiming your device is compromised will trigger panic responses.",
                "secondary_risks": [
                    {"vector": "Tech Support Scams", "probability": 75, "reason": "Fear of data loss makes you vulnerable to fake support"}
                ]
            },
            "SCARCITY": {
                "highest_risk_vector": "Fake Investment Schemes",
                "probability": 70,
                "scenario": "Limited-time offers and exclusive deals will bypass your critical thinking.",
                "secondary_risks": [
                    {"vector": "Cryptocurrency Phishing", "probability": 60, "reason": "Fear of missing out on crypto gains"}
                ]
            }
        }
        
        if primary_weakness and primary_weakness in threat_map:
            return threat_map[primary_weakness]
        
        # Default forecast
        return {
            "highest_risk_vector": "General Phishing",
            "probability": 50,
            "scenario": "Continue training to identify your specific vulnerabilities.",
            "secondary_risks": []
        }


# Singleton instance
report_generator = ReportGenerator()
