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
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                print(f"DEBUG: LLM Client initialized with model {self.model_name}")
            except Exception as e:
                print(f"ERROR: Failed to initialize LLM client: {e}")
    
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
            print("ERROR: LLM client not configured")
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an ADVERSARIAL AI RED TEAM for cybersecurity training. Generate realistic, sophisticated threat simulations. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                timeout=30  # 30 second timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in chat completion: {e}")
            return None
    
    def generate_question(self, difficulty: str = "ADVANCED") -> Optional[Dict[str, Any]]:
        """
        INTENT ANALYSIS ENGINE (2026)
        """
        if not self.is_configured():
            print("ERROR: LLM client not configured, using fallback")
            return self._get_fallback_question()
        
        try:
            import random
            
            # Force variety by randomly selecting scenario type and threat vector
            threat_vectors = [
                ("AGENTIC_AI_HIJACKING", "popup"),
                ("QUISHING_2_0", "qr_poster"),
                ("VIBE_CODING_PHISH", "code_review"),
                ("OAUTH_WORM", "oauth_screen"),
                ("DEEPFAKE_VOICE", "slack")
            ]
            
            # Random selection
            selected_threat = random.choice(threat_vectors)
            forced_threat_vector = selected_threat[0]
            forced_scenario_type = selected_threat[1]
            
            # Random phishing/safe decision (50/50 for balanced training)
            is_phishing = random.random() < 0.5
            forced_answer = "Phishing" if is_phishing else "Safe"
            
            prompt = f"""You are an ELITE INTENT ANALYSIS RED TEAM ENGINE for 2026.

## CRITICAL INSTRUCTIONS - YOU MUST FOLLOW EXACTLY:
1. Scenario Type: **{forced_scenario_type}** (NOT email unless explicitly stated)
2. Threat Vector: **{forced_threat_vector}**
3. Correct Answer: **{forced_answer}**
4. Difficulty: **ELITE** - Make this EXTREMELY hard to detect

## MAKE QUESTIONS HARDER WITH MORE CONTEXT
To confuse students, you MUST include:
- **Extensive backstory**: Add realistic context about the company, project, or situation
- **Multiple details**: Include names, dates, project codes, meeting references, ticket numbers
- **Red herrings**: Add legitimate-looking details that distract from the real red flag
- **Realistic urgency**: Use time-sensitive but believable deadlines
- **Departmental jargon**: Use industry-specific terminology
- **Previous thread context**: Reference "as discussed" or "following up on our call"

## PARADIGM SHIFT
Old phishing: "Detect typos, suspicious links, grammatical errors"
2026 phishing: "Detect MALICIOUS INTENT hidden within LEGITIMATE-LOOKING workflows"

These are "post-malware" attacks—they use REAL tools to hide malicious intent.

## {forced_threat_vector} ATTACK DETAILS

### AGENTIC_AI_HIJACKING (For popup scenarios)
**The Threat**: Attackers target Model Context Protocol (MCP) or AI ecosystems. A hijacked agent "autonomously" requests permission changes that look like routine system updates.
**Why It's Hard**: Humans have "automation bias"—we trust system-generated popups from known AI tools.
**Intent Betrayal Examples**:
- "To optimize your Q1 workflow, I need access to the Financial API"
- "Copilot requires calendar AND contacts sync for meeting optimization"

### QUISHING_2_0 (For qr_poster scenarios)
**The Threat**: Multi-stage QR codes. First scan leads to neutral page; second redirect (within 12 hours) leads to credential harvesting.
**Why It's Hard**: QR codes bypass text-based email scanners entirely.
**Intent Betrayal Examples**:
- "Scan for $10 cafeteria credit" but uses bit.ly link
- "Updated WiFi credentials - scan to connect" on physical poster

### VIBE_CODING_PHISH (For code_review scenarios)
**The Threat**: Attacker mimics teammate's tone, sends "useful" AI-generated code snippet or GitHub PR with hidden backdoor.
**Why It's Hard**: Developers "vibe-code"—they guide AI rather than review every line.
**Intent Betrayal Examples**:
- Code with obfuscated eval() or unknown npm packages
- "Quick fix" PR that adds a hidden API call

### OAUTH_WORM (For oauth_screen scenarios)
**The Threat**: Instead of stealing passwords, tricks users into granting broad consent to malicious "helper apps".
**Why It's Hard**: Bypasses MFA entirely. Once granted, worm pivots between Slack, Google Workspace, Salesforce.
**Intent Betrayal Examples**:
- "MeetingNotes Pro" requesting "Full Data Deletion" permission
- Calendar app asking for "Send Emails" scope

### DEEPFAKE_VOICE (For slack scenarios)
**The Threat**: Message claims to be from colleague, uses their exact communication style, includes urgent but subtle request.
**Why It's Hard**: Mimics real colleague's writing patterns perfectly.
**Intent Betrayal Examples**:
- "Hey can you just merge this? I'm in a rush" with suspicious code
- "Boss asked me to get you to approve this invoice ASAP"

## INTENT ANALYSIS FRAMEWORK
For EACH scenario, you MUST identify the **Intent Betrayal**:
1. What is the STATED purpose? (e.g., "Optimize your workflow")
2. What is the ACTUAL request? (e.g., "Access Financial API")
3. The LOGICAL CHECK: "Does this request MATCH the stated purpose?"

## ELITE DIFFICULTY REQUIREMENTS
- NO obvious red flags (typos, suspicious domains)
- Perfect grammar and professional tone
- Realistic company names and contexts
- Intent betrayal should be SUBTLE - require careful logical analysis
- For Safe scenarios: Make them LOOK suspicious but actually legitimate
- **LONG DETAILED CONTENT**: At least 150-250 words with realistic context
- **CONFUSING DETAILS**: Add project names, ticket numbers, team names, deadlines

## RETURN VALID JSON (FOLLOW EXACTLY):
{{
    "scenario_type": "{forced_scenario_type}",
    "threat_vector": "{forced_threat_vector if is_phishing else 'LEGITIMATE'}",
    "content": {{
        "from": "realistic sender with full name and title",
        "subject": "realistic subject with project/ticket reference",
        "body": "LONG detailed scenario (150-250 words) with backstory, context, names, dates, and confusing details",
        "permissions_requested": ["specific permission 1", "specific permission 2", "specific permission 3"]
    }},
    "correct_answer": "{forced_answer}",
    "intent_analysis": {{
        "stated_purpose": "What the request claims to do",
        "actual_request": "What it actually asks for",
        "intent_betrayal": "The logical mismatch that reveals malicious intent (or why it's actually legitimate)",
        "logical_check": "The critical question to ask"
    }},
    "manipulation_type": "Automation Bias | Collaborative Trust | Urgency | Authority",
    "psychological_trigger": "AUTOMATION_BIAS | COLLABORATIVE_TRUST | FRICTIONLESS_CONVENIENCE | FEAR | AUTHORITY",
    "complexity_score": 9,
    "red_flags": ["Extremely subtle clue 1", "Extremely subtle clue 2", "Extremely subtle clue 3"],
    "why_its_hard": "Why this attack evades even experienced security professionals"
}}

## GENERATE AN ELITE-LEVEL {forced_scenario_type.upper()} SCENARIO WITH EXTENSIVE CONTEXT NOW:"""
            
            print(f"DEBUG: Calling Groq API for question generation...")
            response_text = self._chat_completion(prompt)
            
            if not response_text:
                print("DEBUG: Groq returned empty response, using fallback")
                return self._get_fallback_question()
            
            print(f"DEBUG: Groq response length: {len(response_text)} chars")
            
            try:
                result = self._parse_json_response(response_text)
                print(f"DEBUG: Parsed result keys: {result.keys()}")
                result["difficulty"] = difficulty
                return result
            except Exception as parse_error:
                print(f"DEBUG: JSON Parse Error: {parse_error}")
                print(f"DEBUG: Raw response: {response_text}")
                return self._get_fallback_question()
        except Exception as e:
            print(f"Error generating question: {e}")
            return self._get_fallback_question()

    def _get_fallback_question(self) -> Dict[str, Any]:
        """Return a hardcoded fallback question if LLM fails."""
        print("DEBUG: Using fallback question")
        return {
            "scenario_type": "email",
            "threat_vector": "LEGITIMATE",
            "content": {
                "from": "IT Support <support@company.com>",
                "subject": "Scheduled Maintenance",
                "body": "This is a reminder that we will be performing scheduled maintenance on the main server cluster tonight from 2 AM to 4 AM. No action is required from your end.",
                "permissions_requested": []
            },
            "correct_answer": "Safe",
            "difficulty": "ADVANCED",
            "intent_analysis": {
                "stated_purpose": "Notify about maintenance",
                "actual_request": "None",
                "intent_betrayal": "None - matches stated purpose",
                "logical_check": "Is there a suspicious call to action?"
            },
            "manipulation_type": None,
            "psychological_trigger": None,
            "complexity_score": 1,
            "red_flags": [],
            "why_its_hard": "Standard maintenance notification"
        }
    
    def evaluate_answer(
        self,
        scenario: Dict[str, Any],
        correct_answer: str,
        manipulation_type: Optional[str],
        red_flags: list,
        user_answer: str,
        user_reasoning: Optional[str] = None,
        psychological_trigger: Optional[str] = None,
        attack_vector: Optional[str] = None,
        intent_analysis: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        INTENT ANALYSIS EVALUATOR
        
        Paradigm: Evaluate if the user detected the INTENT BETRAYAL, not just typos.
        """
        if not self.is_configured():
            return None
        
        try:
            # Format inputs for prompt
            scenario_text = json.dumps(scenario, indent=2)
            red_flags_text = ", ".join(red_flags) if red_flags else "None"
            u_reasoning = user_reasoning or "No reasoning provided"
            m_type = manipulation_type or "None (legitimate request)"
            p_trigger = psychological_trigger or "None"
            a_vector = attack_vector or "Traditional"
            intent_text = json.dumps(intent_analysis, indent=2) if intent_analysis else "{}"
            
            # Pre-determine if user is correct
            user_is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
            
            prompt = f"""You are an INTENT ANALYSIS COACH for 2026 cybersecurity.

## CRITICAL: ANSWER COMPARISON
- Correct Answer: **{correct_answer}**
- User's Answer: **{user_answer}**
- **USER IS {"CORRECT" if user_is_correct else "INCORRECT"}** (This is pre-determined, do not change)

## The Scenario
{scenario_text}

## Attack Metadata
- Threat Vector: {a_vector}
- Manipulation Type: {m_type}
- Psychological Trigger: {p_trigger}
- Red Flags: {red_flags_text}

## Intent Analysis Context
{intent_text}

## Student's Reasoning
{u_reasoning}

## YOUR TASK
The user answered **{user_answer}** and the correct answer is **{correct_answer}**.
Therefore, the user is **{"CORRECT" if user_is_correct else "INCORRECT"}**.

{"Since the user is CORRECT, provide positive reinforcement and explain what they spotted correctly." if user_is_correct else "Since the user is INCORRECT, explain what they missed and what cognitive bias might have affected them."}

## RETURN VALID JSON:
{{
    "correct": {str(user_is_correct).lower()},
    "explanation": "Detailed analysis of why the answer was {'correct - what they spotted' if user_is_correct else 'incorrect - what they missed'}...",
    "intent_betrayal_spotted": {str(user_is_correct).lower()},
    "logical_check_applied": "{'The logical check they correctly applied' if user_is_correct else 'The logical check they should have applied'}",
    "psychological_trigger_exploited": {"'null'" if user_is_correct else f"'{p_trigger}'"},
    "bias_analysis": "Analysis of cognitive biases involved",
    "vulnerability_score": {0 if user_is_correct else 7},
    "learning_tip": "A helpful tip for future scenarios",
    "future_vulnerability": "{'None - they showed good awareness' if user_is_correct else 'Attack types they might be vulnerable to'}"
}}

Generate the evaluation JSON now:"""
            
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
        answer_history: list,
        difficulty_level: str = "BEGINNER",
        bias_heatmap: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate a comprehensive threat intelligence report."""
        if not self.is_configured():
            return None
        
        try:
            # Format inputs
            bias_text = json.dumps(bias_heatmap, indent=2) if bias_heatmap else "{}"
            vuln_text = json.dumps(vulnerability_patterns, indent=2)
            history_text = json.dumps(answer_history, indent=2)
            
            prompt = f"""You are a CISO (Chief Information Security Officer) generating a THREAT INTELLIGENCE REPORT for a user who completed a phishing simulation.

User Stats:
- Score: {{score_percentage:.1f}}% ({correct_answers}/{total_questions})
- Difficulty Level: {difficulty_level}

## Vulnerability Profile (Psychological Bias Heatmap)
{bias_text}

## Answer History
{history_text}

## Required Report Sections

1. **Executive Summary**: Professional assessment of their phishing radar.

2. **Human Bias Heatmap Analysis**:
   - Analyze their specific psychological weaknesses (Authority, Urgency, etc.) 
   - Based on the Heatmap data provided above.

3. **Zero-Day Threat Forecast**:
   - Predict FUTURE attacks they are vulnerable to based on their specific bias profile.
   - Examples: "Due to high AUTHORITY bias, you are vulnerable to Deepfake CEO Fraud."
   - Suggest specific attack vectors: Quishing, AI Vishing, Slack/Teams Phishing.

4. **Defense Protocol**:
   - 3-5 specific, actionable defensive habits tailored to their weaknesses.

## Return valid JSON:
{{
    "risk_level": "Low | Moderate | High | Critical",
    "risk_score": 1-10,
    "overall_assessment": {{
        "level": "Novice | Developing | Proficient | Expert",
        "summary": "Evaluation text..."
    }},
    "bias_heatmap": {{
        "primary_weakness": "TRIGGER_NAME",
        "analysis": "Specific analysis..."
    }},
    "zero_day_threat_forecast": {{
        "highest_risk_vector": "Vector Name",
        "probability": 85,
        "scenario": "A specific future attack scenario...",
        "secondary_risks": [
            {{"vector": "Name", "probability": 70, "reason": "Why"}}
        ]
    }},
    "defense_protocol": [
        "Specific defensive action 1",
        "Specific defensive action 2"
    ]
}}

Generate report now:"""
            
            response_text = self._chat_completion(prompt)
            
            if not response_text:
                return None
            
            return self._parse_json_response(response_text)
        except Exception as e:
            print(f"Error generating report: {e}")
            return None


# Singleton instance
llm_client = LLMClient()
