import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # LLM Configuration (Groq)
    GROK_API_KEY = os.getenv("GROK_API_KEY", "")
    GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.groq.com/openai/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    
    # Quiz Configuration
    DEFAULT_NUM_QUESTIONS = 5
    MAX_QUESTIONS = 10
    
    # Flask Configuration
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("FLASK_PORT", 5000))
