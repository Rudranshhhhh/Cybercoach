import json
import os
from typing import Dict, Any, Optional

from openai import OpenAI

from config import Config


class LLMClient:
    """Client for interacting with Grok AI via OpenAI-compatible API."""
    
    def __init__(self):
        """Initialize the Grok client."""
        self.api_key = Config.GROK_API_KEY
        self.base_url = Config.GROK_BASE_URL
        self.model_name = Config.LLM_MODEL
        self.client = None
        self._prompts_cache = {}
        
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
    
    def is_configured(self) -> bool:
        """Check if the LLM client is properly configured."""
        return bool(self.api_key and self.client)
    
    def _load_prompt(self, prompt_name: str) -> str:
        """Load a prompt template from the prompts directory."""
        if prompt_name in self._prompts_cache:
            return self._prompts_cache[prompt_name]
        
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            f"{prompt_name}.txt"
        )
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        
        self._prompts_cache[prompt_name] = prompt
        return prompt
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        text = response_text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text.strip())
    
    def _chat_completion(self, prompt: str) -> Optional[str]:
        """Make a chat completion request to Grok."""
        if not self.is_configured():
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful cybersecurity expert. Always respond with valid JSON when requested."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in chat completion: {e}")
            return None
    
    def generate_question(self) -> Optional[Dict[str, Any]]:
        """Generate a phishing/safe scenario question."""
        if not self.is_configured():
            return None
        
        try:
            prompt = self._load_prompt("generate_question")
            response_text = self._chat_completion(prompt)
            
            if not response_text:
                return None
            
            return self._parse_json_response(response_text)
        except Exception as e:
            print(f"Error generating question: {e}")
            return None
    
    def evaluate_answer(
        self,
        scenario: Dict[str, Any],
        correct_answer: str,
        manipulation_type: Optional[str],
        red_flags: list,
        user_answer: str,
        user_reasoning: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a user's answer to a phishing scenario."""
        if not self.is_configured():
            return None
        
        try:
            prompt_template = self._load_prompt("evaluate_answer")
            
            # Format the scenario for the prompt
            scenario_text = json.dumps(scenario, indent=2)
            red_flags_text = ", ".join(red_flags) if red_flags else "None"
            
            prompt = prompt_template.format(
                scenario=scenario_text,
                correct_answer=correct_answer,
                manipulation_type=manipulation_type or "None (legitimate email)",
                red_flags=red_flags_text,
                user_answer=user_answer,
                user_reasoning=user_reasoning or "No reasoning provided"
            )
            
            response_text = self._chat_completion(prompt)
            
            if not response_text:
                return None
            
            return self._parse_json_response(response_text)
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return None
    
    def generate_report(
        self,
        total_questions: int,
        correct_answers: int,
        score_percentage: float,
        vulnerability_patterns: Dict[str, Any],
        answer_history: list
    ) -> Optional[Dict[str, Any]]:
        """Generate a comprehensive quiz report."""
        if not self.is_configured():
            return None
        
        try:
            prompt_template = self._load_prompt("generate_report")
            
            prompt = prompt_template.format(
                total_questions=total_questions,
                correct_answers=correct_answers,
                score_percentage=score_percentage,
                vulnerability_patterns=json.dumps(vulnerability_patterns, indent=2),
                answer_history=json.dumps(answer_history, indent=2)
            )
            
            response_text = self._chat_completion(prompt)
            
            if not response_text:
                return None
            
            return self._parse_json_response(response_text)
        except Exception as e:
            print(f"Error generating report: {e}")
            return None


# Singleton instance
llm_client = LLMClient()
