from typing import Dict, Optional
from models.session import Session


class SessionManager:
    """Manages quiz sessions in memory."""
    
    def __init__(self):
        """Initialize the session manager."""
        self._sessions: Dict[str, Session] = {}
    
    def create_session(self, num_questions: int = 5) -> Session:
        """Create a new quiz session."""
        session = Session(num_questions=num_questions)
        self._sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions."""
        return len(self._sessions)


# Singleton instance
session_manager = SessionManager()
