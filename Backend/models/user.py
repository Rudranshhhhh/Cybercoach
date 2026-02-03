from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User model for authentication."""
    email: str
    password_hash: str
    name: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    _id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for MongoDB."""
        data = {
            "email": self.email,
            "password_hash": self.password_hash,
            "name": self.name,
            "created_at": self.created_at
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from MongoDB document."""
        return cls(
            email=data.get("email", ""),
            password_hash=data.get("password_hash", ""),
            name=data.get("name", ""),
            created_at=data.get("created_at", datetime.utcnow()),
            _id=str(data.get("_id", ""))
        )
